//! `gatana tools`: `ls` lists the enabled tools, shows the arguments of one tool with an example call,
//! and calls a tool.
//!
//! Tools are read raw: their schemas are free-form JSON Schema, and the server objects that say
//! whether a server is enabled are a union the backend grows.

use super::resources::split_tool_name;
use super::{Silent, array_at, text_at};
use crate::cli::{ToolArgs, ToolPart, ToolsArgs, ToolsCommand};
use crate::context::Context;
use crate::output::{self, Column, Options};
use crate::util::{coerce_scalar, js_string, parse_inline_object, read_piped_stdin};
use anyhow::{Context as _, Result, bail};
use gatana_api::v1;
use serde_json::{Map, Value, json};
use std::collections::HashSet;

/// How many arguments the example call of `gatana tools <tool>` fills in.
const EXAMPLE_ARGUMENTS: usize = 3;
/// Longer descriptions are cut in tables, so that a row fits on one line.
const DESCRIPTION_WIDTH: usize = 80;

const TOOL_COLUMNS: [Column; 2] = [Column::path("Name", "name"), Column::path("Description", "description")];
const ALL_TOOL_COLUMNS: [Column; 3] =
    [Column::path("Name", "name"), Column::path("Enabled", "enabled"), Column::path("Description", "description")];
const ARGUMENT_COLUMNS: [Column; 4] = [
    Column::path("Name", "name"),
    Column::path("Type", "type"),
    Column::path("Required", "required"),
    Column::path("Description", "description"),
];

pub async fn run(context: &Context, args: ToolsArgs) -> Result<()> {
    match (args.command, args.tool) {
        (Some(ToolsCommand::Ls { server, all }), _) => list(context, server.as_deref(), all).await,
        (Some(ToolsCommand::Call(call)), _) => call_tool(context, call).await,
        (None, Some(name)) => show(context, &name).await,
        // Only a global flag such as "-o json" was given; without any, clap prints the help.
        (None, None) => bail!("Give a tool name, or list the tools with \"gatana tools ls\""),
    }
}

/// `gatana tools ls [--server <slug>] [--all]`: the tools a call can reach, unless `--all`.
async fn list(context: &Context, server: Option<&str>, all: bool) -> Result<()> {
    let api = context.api().await?;
    // The table shows no schemas, so it does not download them. JSON and YAML output keep them.
    let schemas = (!output::machine_readable()).then(|| "false".to_string());
    let (tools, servers) = match server {
        Some(slug) => {
            let query = v1::query::ListMcpServerTools { schemas };
            let (tools, server) = tokio::try_join!(
                api.v1().list_mcp_server_tools(slug, &query).value(),
                api.v2().get_server_v2(slug).value(),
            )?;
            (array_at(&tools, "tools"), vec![server])
        }
        None => {
            let query = v1::query::ListTools { schemas, ..Default::default() };
            let (tools, servers) =
                tokio::try_join!(api.v1().list_tools(&query).value(), api.v2().list_servers_v2().value())?;
            (array_at(&tools, "tools"), array_at(&servers, "servers"))
        }
    };
    let disabled_servers: HashSet<&str> = servers
        .iter()
        .filter(|server| server.get("isEnabled") == Some(&Value::Bool(false)))
        .filter_map(|server| text_at(server, "/slug"))
        .collect();
    let enabled = |tool: &Value| {
        tool.get("isEnabled") == Some(&Value::Bool(true))
            && !text_at(tool, "/serverSlug").is_some_and(|slug| disabled_servers.contains(slug))
    };
    let mut tools: Vec<Value> = tools.into_iter().filter(|tool| all || enabled(tool)).collect();
    tools.sort_by(|a, b| text_at(a, "/universalName").cmp(&text_at(b, "/universalName")));

    if output::machine_readable() {
        output::print(&Value::Array(tools));
        return Ok(());
    }
    if tools.is_empty() {
        let scope = server.map(|slug| format!(" on server '{slug}'")).unwrap_or_default();
        if all {
            output::println(&format!("No tools found{scope}."));
        } else {
            output::println(&format!("No enabled tools found{scope}. Add --all to see the disabled tools too."));
        }
        return Ok(());
    }
    let rows: Vec<Value> = tools
        .iter()
        .map(|tool| {
            json!({
                "name": text_at(tool, "/universalName").unwrap_or_default(),
                "enabled": enabled(tool),
                "description": first_line(description(tool), DESCRIPTION_WIDTH),
            })
        })
        .collect();
    let columns: &[Column] = if all { &ALL_TOOL_COLUMNS } else { &TOOL_COLUMNS };
    output::output(&Value::Array(rows), Options::columns(columns));
    Ok(())
}

/// `gatana tools <tool>`: the description, the arguments and an example call.
async fn show(context: &Context, name: &str) -> Result<()> {
    if !name.contains('_') {
        bail!(
            "\"{name}\" is not a tool name. A tool name is <server>_<tool>. To list the tools of a server, run \"gatana tools ls --server {name}\""
        );
    }
    let (server, tool) = split_tool_name(name)?;
    let found = context.api().await?.v1().get_mcp_server_tool(server, tool).value().await?;
    if output::machine_readable() {
        output::print(&found);
        return Ok(());
    }

    let schema = input_schema(&found);
    let mut lines = vec![output::bold(text_at(&found, "/universalName").unwrap_or(name))];
    lines.push(format!("Server: {server}"));
    if found.get("isEnabled") == Some(&Value::Bool(false)) {
        lines.push(output::yellow("The tool is disabled. A call fails until a maintainer of the server enables it."));
    }
    let description = description(&found).trim();
    if !description.is_empty() {
        lines.push(String::new());
        lines.push(description.to_string());
    }

    lines.push(String::new());
    let arguments = argument_rows(schema);
    if arguments.is_empty() {
        lines.push(format!("{} none", output::bold("Arguments:")));
    } else {
        lines.push(output::bold("Arguments:"));
        let table = output::render_table(&arguments, Some(&ARGUMENT_COLUMNS), false);
        lines.extend(table.into_iter().map(|line| format!("  {line}")));
    }

    lines.push(String::new());
    lines.push(output::bold("Example:"));
    lines.push(format!("  {}", example_call(name, schema)));
    if arguments.len() > EXAMPLE_ARGUMENTS {
        lines.push(output::dim(&format!("  The example shows {EXAMPLE_ARGUMENTS} of {} arguments.", arguments.len())));
    }
    for line in lines {
        output::println(&line);
    }
    Ok(())
}

/// The description that MCP clients see: the override, if one is on.
fn description(tool: &Value) -> &str {
    if tool.get("overrideDescription") == Some(&Value::Bool(true)) {
        text_at(tool, "/descriptionOverride").unwrap_or_default()
    } else {
        text_at(tool, "/description").unwrap_or_default()
    }
}

/// The input schema that Gatana checks a call against: the override, if one is on.
fn input_schema(tool: &Value) -> &Value {
    let key =
        if tool.get("overrideInputSchema") == Some(&Value::Bool(true)) { "inputSchemaOverride" } else { "schema" };
    tool.get(key).unwrap_or(&Value::Null)
}

/// The first line of a text, cut to `width` characters.
fn first_line(text: &str, width: usize) -> String {
    let line = text.trim().lines().next().unwrap_or_default().trim();
    if line.chars().count() <= width {
        return line.to_string();
    }
    let cut: String = line.chars().take(width - 1).collect();
    format!("{}…", cut.trim_end())
}

fn properties(schema: &Value) -> Vec<(&String, &Value)> {
    schema.get("properties").and_then(Value::as_object).map(|map| map.iter().collect()).unwrap_or_default()
}

fn required(schema: &Value) -> HashSet<&str> {
    schema.get("required").and_then(Value::as_array).into_iter().flatten().filter_map(Value::as_str).collect()
}

/// One row per top-level argument, required ones first, otherwise in the order of the schema.
fn argument_rows(schema: &Value) -> Vec<Value> {
    let required = required(schema);
    let mut rows: Vec<(bool, Value)> = properties(schema)
        .into_iter()
        .map(|(name, property)| {
            let is_required = required.contains(name.as_str());
            let row = json!({
                "name": name,
                "type": type_label(property),
                "required": if is_required { "yes" } else { "no" },
                "description": first_line(text_at(property, "/description").unwrap_or_default(), DESCRIPTION_WIDTH),
            });
            (is_required, row)
        })
        .collect();
    rows.sort_by_key(|(is_required, _)| !is_required);
    rows.into_iter().map(|(_, row)| row).collect()
}

/// A short type: `string`, `integer[]`, `a|b|c` for a small enum, `string|number` for a union.
fn type_label(schema: &Value) -> String {
    if let Some(constant) = schema.get("const") {
        return js_string(constant);
    }
    if let Some(values) = schema.get("enum").and_then(Value::as_array)
        && !values.is_empty()
        && values.len() <= 5
    {
        return values.iter().map(js_string).collect::<Vec<_>>().join("|");
    }
    for key in ["anyOf", "oneOf"] {
        if let Some(branches) = schema.get(key).and_then(Value::as_array) {
            let labels: Vec<String> =
                branches.iter().map(type_label).filter(|label| label != "null").collect::<Vec<_>>();
            if !labels.is_empty() {
                return labels.join("|");
            }
        }
    }
    match base_type(schema) {
        Some("array") => match schema.get("items") {
            Some(items) => format!("{}[]", type_label(items)),
            None => "array".to_string(),
        },
        Some(kind) => kind.to_string(),
        None if schema.get("properties").is_some() || schema.get("$ref").is_some() => "object".to_string(),
        None => "any".to_string(),
    }
}

/// The type of a schema; for `["string", "null"]`, the first type that is not null.
fn base_type(schema: &Value) -> Option<&str> {
    match schema.get("type") {
        Some(Value::String(kind)) => Some(kind),
        Some(Value::Array(kinds)) => kinds.iter().filter_map(Value::as_str).find(|kind| *kind != "null"),
        _ => None,
    }
}

/// A value for the example call: the schema's own const, enum, default or example when it has
/// one, else a placeholder of the right type.
fn example_value(schema: &Value) -> Value {
    if let Some(constant) = schema.get("const") {
        return constant.clone();
    }
    if let Some(first) = schema.get("enum").and_then(Value::as_array).and_then(|values| values.first()) {
        return first.clone();
    }
    if let Some(default) = schema.get("default").filter(|value| !value.is_null()) {
        return default.clone();
    }
    if let Some(example) = schema.get("examples").and_then(Value::as_array).and_then(|values| values.first()) {
        return example.clone();
    }
    for key in ["anyOf", "oneOf"] {
        if let Some(branch) = schema
            .get(key)
            .and_then(Value::as_array)
            .and_then(|branches| branches.iter().find(|branch| base_type(branch) != Some("null")))
        {
            return example_value(branch);
        }
    }
    match base_type(schema) {
        Some("integer" | "number") => json!(1),
        Some("boolean") => json!(true),
        Some("array") => match schema.get("items") {
            Some(items) => json!([example_value(items)]),
            None => json!([]),
        },
        Some("object") => json!({}),
        _ => json!("..."),
    }
}

/// `gatana tools call <name>` with the first arguments filled in: required ones first. Simple
/// values go as `-a key=value`; when one value is an object, an array, or a string that `-a` would
/// read as a number, the arguments go as one JSON object.
fn example_call(name: &str, schema: &Value) -> String {
    let required = required(schema);
    let mut chosen: Vec<(&String, &Value)> = properties(schema);
    chosen.sort_by_key(|(key, _)| !required.contains(key.as_str()));
    chosen.truncate(EXAMPLE_ARGUMENTS);
    let values: Vec<(&String, Value)> =
        chosen.into_iter().map(|(key, property)| (key, example_value(property))).collect();

    let mut call = format!("gatana tools call {name}");
    if values.is_empty() {
        return call;
    }
    if values.iter().all(|(key, value)| fits_key_value(key, value)) {
        for (key, value) in &values {
            let text = match value {
                Value::String(text) => double_quote(text),
                other => js_string(other),
            };
            call.push_str(&format!(" -a {key}={text}"));
        }
    } else {
        let object: Map<String, Value> = values.into_iter().map(|(key, value)| (key.clone(), value)).collect();
        let text = Value::Object(object).to_string().replace('\'', "'\\''");
        call.push_str(&format!(" -a '{text}'"));
    }
    call
}

/// True when `-a key=value` gives the tool this exact value.
fn fits_key_value(key: &str, value: &Value) -> bool {
    let plain_key = !key.is_empty() && key.chars().all(|c| c.is_ascii_alphanumeric() || c == '_' || c == '-');
    let plain_value = match value {
        Value::String(text) => coerce_scalar(text) == *value,
        Value::Number(_) | Value::Bool(_) | Value::Null => true,
        Value::Array(_) | Value::Object(_) => false,
    };
    plain_key && plain_value
}

/// A string in double quotes for a POSIX shell.
fn double_quote(text: &str) -> String {
    let mut quoted = String::from('"');
    for c in text.chars() {
        if matches!(c, '"' | '\\' | '$' | '`') {
            quoted.push('\\');
        }
        quoted.push(c);
    }
    quoted.push('"');
    quoted
}

/// The arguments: `-f` file, else piped stdin, then `-a` on top.
fn tool_arguments(args: &ToolArgs) -> Result<Map<String, Value>> {
    let base = match &args.file {
        Some(file) => Some(std::fs::read_to_string(file).with_context(|| format!("reading {}", file.display()))?),
        None if args.arg.is_empty() => read_piped_stdin()?.filter(|text| !text.trim().is_empty()),
        None => None,
    };
    let mut arguments = match base {
        Some(text) => match serde_json::from_str(text.trim()).context("the arguments are not valid JSON")? {
            Value::Object(map) => map,
            _ => bail!("The arguments must be a JSON object"),
        },
        None => Map::new(),
    };
    if !args.arg.is_empty()
        && let Value::Object(inline) = parse_inline_object(&args.arg)?
    {
        arguments.extend(inline);
    }
    Ok(arguments)
}

/// The text items of a tool result, one after another.
fn result_text(result: &Value) -> Option<String> {
    let texts: Vec<&str> = result
        .get("content")
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter(|item| text_at(item, "/type") == Some("text"))
        .filter_map(|item| text_at(item, "/text"))
        .filter(|text| !text.is_empty())
        .collect();
    (!texts.is_empty()).then(|| texts.join("\n"))
}

/// Points at `gatana tools <name>` after a call that the arguments may have caused to fail.
fn arguments_hint(name: &str) -> String {
    format!("See the arguments of the tool: gatana tools {name}")
}

/// `gatana tools call <server>_<tool>`: calls the tool through Gatana and prints the part asked for.
async fn call_tool(context: &Context, args: ToolArgs) -> Result<()> {
    let name = args.tool_name.as_str();
    let (server, tool) = split_tool_name(name)?;
    let arguments = tool_arguments(&args)?;
    let api = context.api().await?;
    let body = v1::types::CallMcpServerToolBody { args: arguments };
    let response = match api.v1().call_mcp_server_tool(server, tool, &body).value().await {
        Ok(response) => response,
        // Gatana checks the arguments against the schema before it calls the server.
        Err(error) if error.to_string().starts_with("Invalid request body") => {
            bail!("{error}\n{}", arguments_hint(name))
        }
        Err(error) => return Err(error.into()),
    };
    // The result is read raw: MCP keeps adding content types, and printing one must not need a
    // new CLI.
    let Some(result) = response.get("result").filter(|result| !result.is_null()) else {
        bail!("Gatana returned success without a result. Contact Gatana support.");
    };
    if result.get("isError") == Some(&Value::Bool(true)) {
        output::error(&result_text(result).unwrap_or_else(|| result.to_string()));
        if text_at(result, "/errorCode") == Some("auth-required") {
            let config = api.v2().get_server_v2(server).value().await.unwrap_or_default();
            if text_at(&config, "/authorization/method") == Some("oauth") {
                output::error(&format!(
                    "The server is missing credentials. Run \"gatana create creds {server}\" to generate an authorization URL."
                ));
            } else {
                output::error(&format!(
                    "The server is missing credentials. Run \"gatana create creds {server}\" to set API key credentials."
                ));
            }
        } else if !output::machine_readable() {
            output::eprintln(&output::dim(&arguments_hint(name)));
        }
        return Err(Silent.into());
    }
    match args.part {
        ToolPart::Text => match result_text(result) {
            Some(text) => output::print(&Value::String(text)),
            None => bail!("no text content found in tool response"),
        },
        ToolPart::Structured => {
            let structured =
                result.get("structuredContent").filter(|value| !value.is_null()).cloned().unwrap_or(json!({}));
            output::output(&structured, Options::yaml());
        }
        ToolPart::Unstructured => output::output(result.get("content").unwrap_or(&Value::Null), Options::yaml()),
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn schema() -> Value {
        json!({
            "type": "object",
            "properties": {
                "format": { "type": "string", "enum": ["html", "markdown"] },
                "title": { "type": "string", "description": "The title\nMore text" },
                "limit": { "type": ["integer", "null"], "default": 10 },
                "tags": { "type": "array", "items": { "type": "string" } }
            },
            "required": ["title"]
        })
    }

    #[test]
    fn arguments_list_required_first_with_short_types() {
        let rows = argument_rows(&schema());
        let names: Vec<&str> = rows.iter().filter_map(|row| text_at(row, "/name")).collect();
        assert_eq!(names, ["title", "format", "limit", "tags"]);
        assert_eq!(rows[0]["description"], "The title");
        assert_eq!(rows[1]["type"], "html|markdown");
        assert_eq!(rows[2]["type"], "integer");
        assert_eq!(rows[3]["type"], "string[]");
        assert_eq!(type_label(&json!({ "anyOf": [{ "type": "string" }, { "type": "null" }] })), "string");
        assert_eq!(type_label(&json!({})), "any");
    }

    #[test]
    fn the_example_fills_the_first_three_arguments() {
        assert_eq!(
            example_call("srv_tool", &schema()),
            r#"gatana tools call srv_tool -a title="..." -a format="html" -a limit=10"#
        );
        let complex = json!({ "properties": { "tags": { "type": "array", "items": { "type": "string" } } } });
        assert_eq!(example_call("srv_tool", &complex), r#"gatana tools call srv_tool -a '{"tags":["..."]}'"#);
        // "-a id=42" sends a number, so a string that looks like one goes as JSON.
        let numeric = json!({ "properties": { "id": { "type": "string", "default": "42" } } });
        assert_eq!(example_call("srv_tool", &numeric), r#"gatana tools call srv_tool -a '{"id":"42"}'"#);
        assert_eq!(example_call("srv_tool", &json!({ "type": "object" })), "gatana tools call srv_tool");
    }

    #[test]
    fn quotes_and_cuts_text() {
        assert_eq!(double_quote(r#"a "b" $c"#), r#""a \"b\" \$c""#);
        assert_eq!(first_line("one\ntwo", 80), "one");
        assert_eq!(first_line("abcdef", 4), "abc…");
    }

    #[test]
    fn overrides_win_when_they_are_on() {
        let tool = json!({
            "description": "original", "descriptionOverride": "changed", "overrideDescription": true,
            "schema": { "a": 1 }, "inputSchemaOverride": { "b": 2 }, "overrideInputSchema": false
        });
        assert_eq!(description(&tool), "changed");
        assert_eq!(input_schema(&tool), &json!({ "a": 1 }));
    }
}
