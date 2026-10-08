//! Generates `crates/gatana-api/src/<spec>.rs` from the OpenAPI documents the Gatana backend serves.
//!
//! Only the operations listed in `crates/gatana-api/operations.json` are generated, with the schemas
//! they reach. Each operation becomes a method that takes its path parameters, query parameters and
//! request body as typed arguments and returns a `Call` typed with its response. The JSON Schemas are
//! simplified before typify turns them into Rust types (see `normalize`), so that a typed read keeps
//! working when the server adds fields or tightens a constraint.
//!
//! Usage:
//!   cargo run -p gatana-codegen                                # fetch from the base URL in operations.json
//!   cargo run -p gatana-codegen -- --base-url https://acme.local.gatana.ai
//!   cargo run -p gatana-codegen -- --spec v1=path/to/v1.json --spec v2=path/to/v2.json

use anyhow::{Context, Result, anyhow, bail};
use proc_macro2::TokenStream;
use quote::{format_ident, quote};
use serde::Deserialize;
use serde_json::{Map, Value, json};
use std::collections::{BTreeMap, HashMap};
use std::path::{Path, PathBuf};
use std::process::Command;

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct Config {
    /// Where the documents are fetched from when no local file is given.
    default_base_url: String,
    specs: Vec<SpecConfig>,
}

#[derive(Deserialize)]
struct SpecConfig {
    /// Module name, and the name of the generated file.
    name: String,
    /// Path of the document on the base URL.
    path: String,
    /// operationIds to generate, in the order they are emitted.
    operations: Vec<String>,
    /// Named schemas no operation returns but the CLI reads, such as event stream payloads.
    #[serde(default)]
    schemas: Vec<String>,
}

fn main() -> Result<()> {
    let api_dir = Path::new(env!("CARGO_MANIFEST_DIR")).join("../gatana-api");
    let config_path = api_dir.join("operations.json");
    let config: Config = serde_json::from_str(
        &std::fs::read_to_string(&config_path).with_context(|| format!("reading {}", config_path.display()))?,
    )
    .with_context(|| format!("parsing {}", config_path.display()))?;

    let mut local: HashMap<String, PathBuf> = HashMap::new();
    let mut base_url = config.default_base_url.clone();
    let mut args = std::env::args().skip(1);
    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--spec" => {
                let value = args.next().ok_or_else(|| anyhow!("--spec needs NAME=PATH"))?;
                let (name, path) = value.split_once('=').ok_or_else(|| anyhow!("--spec needs NAME=PATH"))?;
                local.insert(name.to_string(), PathBuf::from(path));
            }
            "--base-url" => base_url = args.next().ok_or_else(|| anyhow!("--base-url needs a URL"))?,
            other => bail!("unknown argument {other}"),
        }
    }

    for spec in &config.specs {
        let text = match local.get(&spec.name) {
            Some(path) => std::fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?,
            None => fetch(&format!("{}{}", base_url.trim_end_matches('/'), spec.path))?,
        };
        let doc: Value = serde_json::from_str(&text).with_context(|| format!("parsing the {} document", spec.name))?;
        let code = generate(spec, &doc).with_context(|| format!("generating {}", spec.name))?;
        let out = api_dir.join("src").join(format!("{}.rs", spec.name));
        std::fs::write(&out, code).with_context(|| format!("writing {}", out.display()))?;
        eprintln!("wrote {} ({} operations)", out.display(), spec.operations.len());
    }
    Ok(())
}

fn fetch(url: &str) -> Result<String> {
    eprintln!("fetching {url}");
    let output = Command::new("curl").args(["-fsSL", url]).output().context("running curl")?;
    if !output.status.success() {
        bail!("curl {url} failed: {}", String::from_utf8_lossy(&output.stderr).trim());
    }
    Ok(String::from_utf8(output.stdout)?)
}

struct Operation {
    id: String,
    method: String,
    path: String,
    summary: Option<String>,
    path_params: Vec<Param>,
    query_params: Vec<Param>,
    body: Option<Value>,
    response: Option<Value>,
}

struct Param {
    name: String,
    required: bool,
    description: Option<String>,
    /// True when the parameter takes several values (`?name=a&name=b`).
    repeated: bool,
    /// Allowed values, for the doc comment.
    values: Vec<String>,
}

const SCHEMA_PREFIX: &str = "#/components/schemas/";

/// zod-openapi names schemas that are reused but never registered `__schemaN`. They are inlined so
/// typify names their types after where they are used instead of `Schema462`.
fn is_anonymous(name: &str) -> bool {
    name.starts_with("__schema")
}

fn ref_name(schema: &Value) -> Option<&str> {
    schema.get("$ref")?.as_str()?.strip_prefix(SCHEMA_PREFIX)
}

struct Components<'a> {
    schemas: &'a Map<String, Value>,
}

impl Components<'_> {
    fn get(&self, name: &str) -> Result<&Value> {
        self.schemas.get(name).ok_or_else(|| anyhow!("schema {name} is referenced but not defined"))
    }

    /// Replaces every reference to an anonymous schema with a copy of it. Keywords next to the
    /// reference (a description, usually) win over the copied ones.
    fn inline(&self, value: &Value, stack: &mut Vec<String>) -> Result<Value> {
        match value {
            Value::Object(map) => {
                if let Some(name) = ref_name(value).filter(|name| is_anonymous(name)) {
                    if stack.iter().any(|entry| entry == name) {
                        bail!("anonymous schema {name} refers to itself; give it a name in the backend");
                    }
                    stack.push(name.to_string());
                    let mut inlined = self.inline(self.get(name)?, stack)?;
                    stack.pop();
                    if let Value::Object(target) = &mut inlined {
                        for (key, sibling) in map.iter().filter(|(key, _)| key.as_str() != "$ref") {
                            target.insert(key.clone(), self.inline(sibling, stack)?);
                        }
                    }
                    return Ok(inlined);
                }
                let mut out = Map::new();
                for (key, child) in map {
                    out.insert(key.clone(), self.inline(child, stack)?);
                }
                Ok(Value::Object(out))
            }
            Value::Array(items) => {
                Ok(Value::Array(items.iter().map(|item| self.inline(item, stack)).collect::<Result<_>>()?))
            }
            other => Ok(other.clone()),
        }
    }

    /// The schema a reference points at, normalized; anything else as it is.
    fn resolved(&self, schema: &Value) -> Value {
        match ref_name(schema) {
            Some(name) => match self.get(name).and_then(|target| self.inline(target, &mut Vec::new())) {
                Ok(target) => normalize(target, self),
                Err(_) => schema.clone(),
            },
            None => schema.clone(),
        }
    }

    /// An object, or a reference to one: a member typify can tag in a `oneOf`.
    fn is_objectish(&self, schema: &Value) -> bool {
        if let Some(name) = ref_name(schema) {
            return self.get(name).map(|target| self.is_objectish(target)).unwrap_or(false);
        }
        schema.get("type").and_then(Value::as_str) == Some("object") || schema.get("properties").is_some()
    }
}

/// Validation keywords and annotations the CLI has no use for. Dropping the validation keywords
/// keeps a typed read working when the server returns data its schema is stricter than (an old row
/// with a long description), and keeps plain `String`s instead of constrained newtypes. `format` is
/// dropped for the same reason: dates stay strings.
const DROPPED_KEYWORDS: &[&str] = &[
    "pattern",
    "minLength",
    "maxLength",
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "multipleOf",
    "minItems",
    "maxItems",
    "uniqueItems",
    "minProperties",
    "maxProperties",
    "propertyNames",
    "format",
    "default",
    "examples",
    "example",
    "readOnly",
    "writeOnly",
    "deprecated",
    "discriminator",
    "xml",
    "externalDocs",
    "title",
    "$schema",
    "$id",
    "$comment",
    "contentEncoding",
    "contentMediaType",
];

/// Rewrites one schema into the subset typify handles well. Schema-aware: property maps are walked
/// as maps of schemas, so a property that happens to be called `format` survives.
fn normalize(schema: Value, components: &Components) -> Value {
    let Value::Object(mut map) = schema else {
        return schema;
    };
    if let Some(reference) = map.get("$ref") {
        // A sibling keyword next to a named reference would make typify wrap the type.
        return json!({ "$ref": reference });
    }
    let tuple = map.get("items").is_some_and(Value::is_array);
    for keyword in DROPPED_KEYWORDS {
        // A tuple keeps its length: normalize runs again after nullable schemas are hoisted.
        if tuple && (*keyword == "minItems" || *keyword == "maxItems") {
            continue;
        }
        map.remove(*keyword);
    }
    // Closed objects would reject fields the server adds later; open is what the TypeScript SDK did.
    if map.get("additionalProperties") == Some(&Value::Bool(false)) {
        map.remove("additionalProperties");
    }
    if let Some(value) = map.remove("const")
        && !map.contains_key("enum")
    {
        map.insert("enum".into(), Value::Array(vec![value]));
    }
    // JSON Schema 2020-12 tuples become draft-07 tuples, the dialect typify reads.
    if let Some(Value::Array(prefix)) = map.remove("prefixItems") {
        let len = prefix.len();
        map.insert("items".into(), Value::Array(prefix));
        map.insert("additionalItems".into(), Value::Bool(false));
        map.insert("minItems".into(), json!(len));
        map.insert("maxItems".into(), json!(len));
    }

    for key in ["properties", "patternProperties"] {
        if let Some(Value::Object(properties)) = map.remove(key) {
            let normalized = properties.into_iter().map(|(name, child)| (name, normalize(child, components)));
            map.insert(key.into(), Value::Object(normalized.collect()));
        }
    }
    for key in ["additionalProperties", "not", "additionalItems"] {
        if let Some(child @ Value::Object(_)) = map.remove(key) {
            map.insert(key.into(), normalize(child, components));
        } else if key == "additionalItems" && map.get("items").is_some_and(Value::is_array) {
            map.insert(key.into(), Value::Bool(false));
        }
    }
    match map.remove("items") {
        Some(Value::Array(items)) => {
            let items = items.into_iter().map(|item| normalize(item, components)).collect();
            map.insert("items".into(), Value::Array(items));
        }
        Some(item @ Value::Object(_)) => {
            map.insert("items".into(), normalize(item, components));
        }
        Some(Value::Bool(false)) | None => {}
        Some(other) => {
            map.insert("items".into(), other);
        }
    }
    if let Some(Value::Array(members)) = map.remove("allOf") {
        let members = members.into_iter().map(|member| normalize(member, components)).collect();
        map.insert("allOf".into(), Value::Array(members));
    }

    // Unions. Objects are made a oneOf so typify can tell them apart by their `type` tag instead of
    // flattening every variant into one struct; a null member becomes an Option around the rest.
    let mut union: Option<Value> = None;
    for key in ["anyOf", "oneOf"] {
        let Some(Value::Array(members)) = map.remove(key) else {
            continue;
        };
        let mut flat = Vec::new();
        for member in members.into_iter().map(|member| normalize(member, components)) {
            // A union inside a union (a reference to a nullable schema, once hoisted) is one union.
            let nested = member.as_object().is_some_and(|inner| {
                inner.keys().all(|key| key == "anyOf" || key == "description")
                    && inner.get("anyOf").is_some_and(Value::is_array)
            });
            match member {
                Value::Object(mut inner) if nested => {
                    if let Some(Value::Array(members)) = inner.remove("anyOf") {
                        flat.extend(members);
                    }
                }
                other => flat.push(other),
            }
        }
        let (mut nulls, rest): (Vec<Value>, Vec<Value>) =
            flat.into_iter().partition(|member| member.get("type").and_then(Value::as_str) == Some("null"));
        nulls.truncate(1);
        let string_enum = |member: &Value| {
            member.get("enum").and_then(Value::as_array).is_some_and(|values| values.iter().all(Value::is_string))
                && member.get("type").and_then(Value::as_str).is_none_or(|kind| kind == "string")
        };
        let plain_string = |member: &Value| {
            member.get("type").and_then(Value::as_str) == Some("string")
                && member.as_object().is_some_and(|map| map.keys().all(|key| key == "type" || key == "description"))
        };
        let inner = if rest.len() > 1
            && rest.iter().all(|member| string_enum(member) || plain_string(member))
            && rest.iter().any(plain_string)
        {
            // Known values or any other string: a string.
            json!({ "type": "string" })
        } else if rest.len() > 1 && rest.iter().all(string_enum) {
            // `"server"` or `"user"`, written as a union of one-value enums: one enum.
            let mut values: Vec<Value> = Vec::new();
            for value in rest.iter().flat_map(|member| member["enum"].as_array().into_iter().flatten()) {
                if !values.contains(value) {
                    values.push(value.clone());
                }
            }
            json!({ "type": "string", "enum": values })
        } else if rest.len() == 1 {
            rest.into_iter().next().unwrap_or(Value::Null)
        } else if rest.len() > 1 && rest.iter().all(|member| components.is_objectish(member)) {
            // When every member names itself in a `type` property, the members are inlined: typify
            // then emits a `#[serde(tag = "type")]` enum with variants named after the tags.
            // A member that allows several tags is one member per tag.
            let inlined: Vec<Value> =
                rest.iter().map(|member| components.resolved(member)).flat_map(split_by_tag).collect();
            let tags: Vec<Option<String>> = inlined.iter().map(type_tag).collect();
            let distinct = tags.iter().flatten().collect::<std::collections::HashSet<_>>().len() == tags.len();
            if tags.iter().all(Option::is_some) && distinct {
                json!({ "oneOf": inlined })
            } else {
                json!({ "oneOf": rest })
            }
        } else {
            json!({ key: rest })
        };
        union = Some(if nulls.is_empty() { inner } else { json!({ "anyOf": [inner, { "type": "null" }] }) });
    }
    // OpenAPI 3.0 spelling of a nullable type.
    if map.remove("nullable") == Some(Value::Bool(true)) {
        let base = match union.take() {
            Some(union) => union,
            None => Value::Object(std::mem::take(&mut map)),
        };
        union = Some(json!({ "anyOf": [base, { "type": "null" }] }));
    }
    if let Some(Value::Object(union)) = union {
        if map.keys().all(|key| key == "description") {
            map.extend(union);
        } else {
            // The union sits next to other keywords (an object with properties and an anyOf):
            // typify reads that as an intersection.
            map = Map::from_iter([("allOf".to_string(), json!([Value::Object(map), Value::Object(union)]))]);
        }
    }
    Value::Object(map)
}

fn split_by_tag(schema: Value) -> Vec<Value> {
    let values = match schema.pointer("/properties/type/enum").and_then(Value::as_array) {
        Some(values) if values.len() > 1 && values.iter().all(Value::is_string) => values.clone(),
        _ => return vec![schema],
    };
    values
        .into_iter()
        .map(|value| {
            let mut member = schema.clone();
            if let Some(tag) = member.pointer_mut("/properties/type") {
                *tag = json!({ "type": "string", "enum": [value] });
            }
            member
        })
        .collect()
}

/// The value of a required `type` property that has exactly one allowed value.
fn type_tag(schema: &Value) -> Option<String> {
    let required = schema.get("required")?.as_array()?;
    if !required.iter().any(|name| name.as_str() == Some("type")) {
        return None;
    }
    let values = schema.pointer("/properties/type/enum")?.as_array()?;
    match values.as_slice() {
        [Value::String(tag)] => Some(tag.clone()),
        _ => None,
    }
}

/// The non-null part of a schema that is `X or null` at its top level.
fn without_null(schema: &Value) -> Option<Value> {
    let map = schema.as_object()?;
    if let Some(types) = map.get("type").and_then(Value::as_array) {
        let rest: Vec<&Value> = types.iter().filter(|kind| kind.as_str() != Some("null")).collect();
        if rest.len() == types.len() || rest.len() != 1 {
            return None;
        }
        let mut inner = map.clone();
        inner.insert("type".into(), rest[0].clone());
        return Some(Value::Object(inner));
    }
    if !map.keys().all(|key| key == "anyOf" || key == "description") {
        return None;
    }
    let members = map.get("anyOf")?.as_array()?;
    let rest: Vec<&Value> =
        members.iter().filter(|member| member.get("type").and_then(Value::as_str) != Some("null")).collect();
    if rest.len() != 1 || members.len() == 1 {
        return None;
    }
    let mut inner = rest[0].clone();
    if let (Some(description), Value::Object(target)) = (map.get("description"), &mut inner) {
        target.entry("description").or_insert_with(|| description.clone());
    }
    Some(inner)
}

fn wrap_nullable_refs(value: &mut Value, names: &[String]) {
    if ref_name(value).is_some_and(|name| names.iter().any(|entry| entry == name)) {
        *value = json!({ "anyOf": [value.clone(), { "type": "null" }] });
        return;
    }
    match value {
        Value::Object(map) => map.values_mut().for_each(|child| wrap_nullable_refs(child, names)),
        Value::Array(items) => items.iter_mut().for_each(|item| wrap_nullable_refs(item, names)),
        _ => {}
    }
}

fn named_refs(value: &Value, out: &mut Vec<String>) {
    match value {
        Value::Object(map) => {
            if let Some(name) = ref_name(value) {
                out.push(name.to_string());
            }
            map.values().for_each(|child| named_refs(child, out));
        }
        Value::Array(items) => items.iter().for_each(|item| named_refs(item, out)),
        _ => {}
    }
}

fn json_schema_of(content: Option<&Value>) -> Option<Value> {
    let content = content?.as_object()?;
    content
        .iter()
        .find(|(media, _)| media.starts_with("application/json"))
        .and_then(|(_, entry)| entry.get("schema").cloned())
}

fn collect_operations(spec: &SpecConfig, doc: &Value, components: &Components) -> Result<Vec<Operation>> {
    let paths = doc.get("paths").and_then(Value::as_object).ok_or_else(|| anyhow!("no paths"))?;
    let mut by_id: HashMap<&str, (&str, &str, &Value, Option<&Value>)> = HashMap::new();
    for (path, item) in paths {
        let shared = item.get("parameters");
        for (method, op) in item.as_object().into_iter().flatten() {
            if let Some(id) = op.get("operationId").and_then(Value::as_str) {
                by_id.insert(id, (method.as_str(), path.as_str(), op, shared));
            }
        }
    }

    let mut operations = Vec::new();
    for id in &spec.operations {
        let (method, path, op, shared) =
            *by_id.get(id.as_str()).ok_or_else(|| anyhow!("operation {id} is not in the {} document", spec.name))?;
        let mut path_params = Vec::new();
        let mut query_params = Vec::new();
        let params = shared.and_then(Value::as_array).into_iter().flatten();
        for param in params.chain(op.get("parameters").and_then(Value::as_array).into_iter().flatten()) {
            if param.get("$ref").is_some() {
                bail!("{id}: parameter references are not supported");
            }
            let name = param["name"].as_str().ok_or_else(|| anyhow!("{id}: parameter without a name"))?;
            let schema = components.inline(param.get("schema").unwrap_or(&Value::Null), &mut Vec::new())?;
            let description = param
                .get("description")
                .or_else(|| schema.get("description"))
                .and_then(Value::as_str)
                .map(str::to_string);
            let parsed = Param {
                name: name.to_string(),
                required: param.get("required").and_then(Value::as_bool).unwrap_or(false),
                description,
                repeated: is_repeated(&schema),
                values: enum_values(&schema),
            };
            match param.get("in").and_then(Value::as_str) {
                Some("path") => path_params.push(parsed),
                Some("query") => query_params.push(parsed),
                Some("header") | Some("cookie") => {}
                other => bail!("{id}: parameter {name} is in {other:?}"),
            }
        }
        // Path parameters in the order the path names them.
        let order: Vec<&str> =
            path.split('{').skip(1).filter_map(|part| part.split_once('}').map(|(n, _)| n)).collect();
        path_params.sort_by_key(|param| order.iter().position(|name| *name == param.name).unwrap_or(usize::MAX));
        if path_params.len() != order.len() {
            bail!("{id}: path {path} and its parameters do not match");
        }

        let body = json_schema_of(op.get("requestBody").and_then(|body| body.get("content")));
        let responses = op.get("responses").and_then(Value::as_object);
        let response = responses
            .into_iter()
            .flatten()
            .filter(|(code, _)| code.starts_with('2'))
            .find_map(|(_, response)| json_schema_of(response.get("content")));
        operations.push(Operation {
            id: id.clone(),
            method: method.to_uppercase(),
            path: path.to_string(),
            summary: op.get("description").or_else(|| op.get("summary")).and_then(Value::as_str).map(str::to_string),
            path_params,
            query_params,
            body,
            response,
        });
    }
    Ok(operations)
}

fn is_repeated(schema: &Value) -> bool {
    if schema.get("type").and_then(Value::as_str) == Some("array") {
        return true;
    }
    ["anyOf", "oneOf"]
        .iter()
        .any(|key| schema.get(*key).and_then(Value::as_array).is_some_and(|members| members.iter().any(is_repeated)))
}

fn enum_values(schema: &Value) -> Vec<String> {
    schema
        .get("enum")
        .and_then(Value::as_array)
        .map(|values| values.iter().filter_map(Value::as_str).map(str::to_string).collect())
        .unwrap_or_default()
}

fn generate(spec: &SpecConfig, doc: &Value) -> Result<String> {
    let empty = Map::new();
    let schemas = doc.pointer("/components/schemas").and_then(Value::as_object).unwrap_or(&empty);
    let components = Components { schemas };
    let operations = collect_operations(spec, doc, &components)?;
    let base_path = doc
        .pointer("/servers/0/url")
        .and_then(Value::as_str)
        .and_then(|url| url.split_once("://").map(|(_, rest)| rest))
        .and_then(|rest| rest.find('/').map(|index| rest[index..].to_string()))
        .ok_or_else(|| anyhow!("the document has no server URL to take the base path from"))?;

    // The schemas the operations reach, anonymous ones inlined, everything normalized.
    let prepare =
        |schema: &Value| -> Result<Value> { Ok(normalize(components.inline(schema, &mut Vec::new())?, &components)) };
    let mut bodies = Vec::new();
    let mut responses = Vec::new();
    let mut pending = Vec::new();
    for op in &operations {
        let body = op.body.as_ref().map(prepare).transpose()?;
        let response = op.response.as_ref().map(prepare).transpose()?;
        body.iter().chain(response.iter()).for_each(|schema| named_refs(schema, &mut pending));
        bodies.push(body);
        responses.push(response);
    }
    pending.extend(spec.schemas.iter().cloned());
    let mut named: BTreeMap<String, Value> = BTreeMap::new();
    while let Some(name) = pending.pop() {
        if named.contains_key(&name) {
            continue;
        }
        let schema = prepare(components.get(&name)?)?;
        named_refs(&schema, &mut pending);
        named.insert(name, schema);
    }

    // typify names a nullable named schema and the object inside it alike and emits both. The
    // definition becomes the object, and every reference to it a nullable reference.
    let mut hoisted: std::collections::HashSet<String> = std::collections::HashSet::new();
    loop {
        let mut round = Vec::new();
        for (name, schema) in named.iter_mut() {
            if hoisted.contains(name) {
                continue;
            }
            if let Some(inner) = without_null(schema) {
                *schema = inner;
                hoisted.insert(name.clone());
                round.push(name.clone());
            }
        }
        if round.is_empty() {
            break;
        }
        let rewrite = |schema: &mut Value| {
            wrap_nullable_refs(schema, &round);
            *schema = normalize(std::mem::take(schema), &components);
        };
        named.values_mut().for_each(rewrite);
        bodies.iter_mut().chain(responses.iter_mut()).flatten().for_each(rewrite);
    }

    let mut settings = typify::TypeSpaceSettings::default();
    settings.with_struct_builder(false);
    let mut type_space = typify::TypeSpace::new(&settings);
    let definitions = named
        .iter()
        .map(|(name, schema)| {
            let schema: schemars::schema::Schema =
                serde_json::from_value(schema.clone()).with_context(|| format!("schema {name}"))?;
            Ok((name.clone(), schema))
        })
        .collect::<Result<Vec<_>>>()?;
    type_space.add_ref_types(definitions)?;

    let mut type_of = |schema: &Option<Value>, name: String| -> Result<TokenStream> {
        let Some(schema) = schema else {
            return Ok(quote! { ::serde_json::Value });
        };
        if schema.as_object().is_some_and(Map::is_empty) {
            return Ok(quote! { ::serde_json::Value });
        }
        let parsed: schemars::schema::Schema = serde_json::from_value(schema.clone())?;
        let id = type_space.add_type_with_name(&parsed, Some(name.clone())).with_context(|| format!("type {name}"))?;
        Ok(type_space.get_type(&id)?.ident())
    };

    let mut methods = Vec::new();
    let mut query_structs = Vec::new();
    for ((op, body), response) in operations.iter().zip(&bodies).zip(&responses) {
        let pascal = pascal_case(&op.id);
        let response_type = type_of(response, format!("{pascal}Response"))?;
        let body_type = match body {
            Some(_) => Some(type_of(body, format!("{pascal}Body"))?),
            None => None,
        };
        let (method, query_struct) = emit_operation(op, &pascal, &response_type, body_type.as_ref())?;
        methods.push(method);
        query_structs.extend(query_struct);
    }
    let types = type_space.to_stream();

    let header = format!(
        " Client for the Gatana `{}` API: {}.\n\n Generated by gatana-codegen from the backend's OpenAPI document. Do not edit; change\n `operations.json` and run `just generate-rs` instead.",
        spec.name,
        doc.pointer("/info/title").and_then(Value::as_str).unwrap_or("Gatana API")
    );
    let tokens = quote! {
        #![doc = #header]
        #![allow(clippy::all, unused_imports, irrefutable_let_patterns, dead_code)]

        /// Path every operation of this API starts with.
        pub const BASE_PATH: &str = #base_path;

        /// Request and response types.
        pub mod types {
            #types
        }

        /// Optional query parameters, one struct per operation that takes any.
        pub mod query {
            #(#query_structs)*
        }

        use types::*;

        /// The operations of this API.
        #[derive(Clone, Copy)]
        pub struct Api<'a> {
            client: &'a crate::Client,
        }

        impl<'a> Api<'a> {
            pub fn new(client: &'a crate::Client) -> Self {
                Self { client }
            }

            #(#methods)*
        }
    };
    let file: syn::File = syn::parse2(tokens).context("the generated code does not parse")?;
    Ok(strip_schema_docs(&prettyplease::unparse(&file)))
}

fn emit_operation(
    op: &Operation,
    pascal: &str,
    response_type: &TokenStream,
    body_type: Option<&TokenStream>,
) -> Result<(TokenStream, Option<TokenStream>)> {
    let fn_name = format_ident!("{}", snake_case(&op.id));
    let raw_fn_name = format_ident!("{}_raw", snake_case(&op.id));
    let method = format_ident!("{}", op.method);
    let mut doc = format!(" `{} {}`", op.method, op.path);
    if let Some(summary) = &op.summary {
        doc.push_str(&format!("\n\n {}", summary.replace('\n', "\n ")));
    }

    let mut format_string = String::from("{}");
    let mut rest = op.path.as_str();
    while let Some(start) = rest.find('{') {
        format_string.push_str(&rest[..start]);
        format_string.push_str("{}");
        let end = rest[start..].find('}').ok_or_else(|| anyhow!("{}: unclosed parameter", op.id))?;
        rest = &rest[start + end + 1..];
    }
    format_string.push_str(rest);

    let path_args: Vec<_> = op.path_params.iter().map(|param| format_ident!("{}", snake_case(&param.name))).collect();
    let required_query: Vec<&Param> = op.query_params.iter().filter(|param| param.required).collect();
    let optional_query: Vec<&Param> = op.query_params.iter().filter(|param| !param.required).collect();
    let required_args: Vec<_> =
        required_query.iter().map(|param| format_ident!("{}", snake_case(&param.name))).collect();
    let required_names: Vec<&str> = required_query.iter().map(|param| param.name.as_str()).collect();

    let (query_arg, query_apply, query_struct) = if optional_query.is_empty() {
        (quote! {}, quote! {}, None)
    } else {
        let struct_name = format_ident!("{}", pascal);
        let fields = optional_query.iter().map(|param| {
            let field = format_ident!("{}", snake_case(&param.name));
            let mut doc = param.description.clone().unwrap_or_default();
            if !param.values.is_empty() {
                doc.push_str(&format!(" One of: {}.", param.values.join(", ")));
            }
            let doc = format!(" `{}`. {}", param.name, doc.trim());
            let ty = if param.repeated {
                quote! { Vec<String> }
            } else {
                quote! { Option<String> }
            };
            quote! { #[doc = #doc] pub #field: #ty, }
        });
        let applies = optional_query.iter().map(|param| {
            let field = format_ident!("{}", snake_case(&param.name));
            let name = &param.name;
            if param.repeated {
                quote! { for value in &self.#field { call = call.query(#name, value); } }
            } else {
                quote! { if let Some(value) = &self.#field { call = call.query(#name, value); } }
            }
        });
        let doc = format!(" Optional query parameters of `{}`.", op.id);
        let query_struct = quote! {
            #[doc = #doc]
            #[derive(Debug, Clone, Default)]
            pub struct #struct_name {
                #(#fields)*
            }

            impl #struct_name {
                pub fn apply<'c, T>(&self, mut call: crate::Call<'c, T>) -> crate::Call<'c, T> {
                    #(#applies)*
                    call
                }
            }
        };
        (quote! { query: &query::#struct_name, }, quote! { let call = query.apply(call); }, Some(query_struct))
    };

    let build = quote! {
        #(let #path_args = crate::encode_path_segment(#path_args);)*
        let path = format!(#format_string, BASE_PATH #(, #path_args)*);
        let call = crate::Call::new(self.client, ::reqwest::Method::#method, path);
        #(let call = call.query(#required_names, #required_args);)*
        #query_apply
    };

    let tokens = match body_type {
        None => quote! {
            #[doc = #doc]
            pub fn #fn_name(&self, #(#path_args: &str,)* #(#required_args: &str,)* #query_arg) -> crate::Call<'a, #response_type> {
                #build
                call
            }
        },
        Some(body_type) => {
            let raw_doc = format!(" `{} {}` with a body that is sent as given, unchecked.", op.method, op.path);
            quote! {
                #[doc = #doc]
                pub fn #fn_name(&self, #(#path_args: &str,)* #(#required_args: &str,)* #query_arg body: &#body_type) -> crate::Call<'a, #response_type> {
                    #build
                    call.json(body)
                }

                #[doc = #raw_doc]
                pub fn #raw_fn_name(&self, #(#path_args: &str,)* #(#required_args: &str,)* #query_arg body: ::serde_json::Value) -> crate::Call<'a, #response_type> {
                    #build
                    call.json_value(body)
                }
            }
        }
    };
    Ok((tokens, query_struct))
}

/// typify documents every type with its JSON Schema; in generated code that nobody reads as
/// documentation it only triples the size of the file.
fn strip_schema_docs(code: &str) -> String {
    let mut out: Vec<&str> = Vec::new();
    let mut skipping = false;
    for line in code.lines() {
        let trimmed = line.trim();
        if trimmed == "/// <details><summary>JSON schema</summary>" {
            skipping = true;
            while out.last().is_some_and(|previous| previous.trim() == "///") {
                out.pop();
            }
            continue;
        }
        if skipping {
            if trimmed == "/// </details>" {
                skipping = false;
            }
            continue;
        }
        out.push(line);
    }
    let mut text = out.join("\n");
    text.push('\n');
    text
}

fn snake_case(name: &str) -> String {
    let mut out = String::new();
    for (index, ch) in name.chars().enumerate() {
        if ch.is_ascii_uppercase() {
            if index > 0 && !out.ends_with('_') {
                out.push('_');
            }
            out.push(ch.to_ascii_lowercase());
        } else if ch.is_ascii_alphanumeric() {
            out.push(ch);
        } else if !out.ends_with('_') {
            out.push('_');
        }
    }
    match out.as_str() {
        "type" | "ref" | "self" | "match" | "mod" | "fn" | "use" | "where" | "async" | "await" => format!("{out}_"),
        _ => out,
    }
}

fn pascal_case(name: &str) -> String {
    let mut chars = name.chars();
    chars.next().map(|first| first.to_ascii_uppercase().to_string() + chars.as_str()).unwrap_or_default()
}
