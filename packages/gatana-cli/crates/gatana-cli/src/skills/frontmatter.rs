//! SKILL.md: YAML frontmatter with name, description and metadata, then the instructions.

use crate::util::{iso_millis, js_string};
use regex_lite::Regex;
use serde_json::{Map, Value};
use std::sync::OnceLock;

/// Metadata keys the sync writes so a file can be traced back to its skill, organization, revision
/// and collection.
pub const META_ID: &str = "gatana-id";
pub const META_ORG: &str = "gatana-org";
pub const META_UPDATED_AT: &str = "gatana-updated-at";
/// The collection the skill is in, by name, so a push keeps it there; absent for a skill at root.
pub const META_COLLECTION: &str = "gatana-collection";
const OWN_KEYS: [&str; 4] = [META_ID, META_ORG, META_UPDATED_AT, META_COLLECTION];
const KNOWN_KEYS: [&str; 3] = ["name", "description", "metadata"];

#[derive(Clone, Debug, PartialEq)]
pub struct SkillFrontmatter {
    pub name: String,
    pub description: String,
    /// String to string, per the specification.
    pub metadata: Map<String, Value>,
    /// Frontmatter keys this tool does not know (`license`, `allowed-tools`, ...), kept so a rewrite
    /// does not drop them.
    pub extra: Map<String, Value>,
}

impl SkillFrontmatter {
    pub fn meta(&self, key: &str) -> Option<&str> {
        self.metadata.get(key).and_then(Value::as_str)
    }
}

#[derive(Debug, thiserror::Error)]
#[error("{0}")]
pub struct SkillMdError(pub String);

/// The same rule as the backend and the agentskills.io specification.
pub fn is_valid_skill_name(name: &str) -> bool {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"^[a-z0-9]+(-[a-z0-9]+)*$").expect("valid regex")).is_match(name)
}

/// What the stamp needs to know about a skill.
pub struct Revision<'a> {
    pub id: &'a str,
    pub name: &'a str,
    pub description: &'a str,
    pub updated_at: &'a str,
    pub collection_name: Option<&'a str>,
}

impl<'a> From<&'a super::api::Skill> for Revision<'a> {
    fn from(skill: &'a super::api::Skill) -> Self {
        Revision {
            id: &skill.id,
            name: &skill.name,
            description: &skill.description,
            updated_at: &skill.updated_at,
            collection_name: skill.collection_name.as_deref(),
        }
    }
}

pub fn frontmatter_for(
    skill: Revision,
    org_id: &str,
    extra: Map<String, Value>,
    other_metadata: &Map<String, Value>,
) -> SkillFrontmatter {
    let mut metadata = Map::new();
    for (key, value) in other_metadata {
        if !OWN_KEYS.contains(&key.as_str()) {
            metadata.insert(key.clone(), value.clone());
        }
    }
    metadata.insert(META_ID.into(), Value::String(skill.id.to_string()));
    metadata.insert(META_ORG.into(), Value::String(org_id.to_string()));
    let updated_at = iso_millis(skill.updated_at).unwrap_or_else(|| skill.updated_at.to_string());
    metadata.insert(META_UPDATED_AT.into(), Value::String(updated_at));
    if let Some(collection) = skill.collection_name.filter(|name| !name.is_empty()) {
        metadata.insert(META_COLLECTION.into(), Value::String(collection.to_string()));
    }
    SkillFrontmatter { name: skill.name.to_string(), description: skill.description.to_string(), metadata, extra }
}

/// One line: the backend treats the description as a one-liner and a multi-line scalar trips simple
/// parsers.
fn collapse(text: &str) -> String {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"\s*\r?\n\s*").expect("valid regex")).replace_all(text, " ").trim().to_string()
}

/// Renders a SKILL.md. The name is emitted bare because its pattern never needs quoting; every
/// other string is double-quoted on one line, so colons, `#`, quotes and angle brackets are safe for
/// any frontmatter parser. The body is written verbatim with one trailing newline.
pub fn render_skill_md(frontmatter: &SkillFrontmatter, body: &str) -> String {
    let mut fields = Map::new();
    fields.insert("description".into(), Value::String(collapse(&frontmatter.description)));
    for (key, value) in &frontmatter.extra {
        fields.insert(key.clone(), value.clone());
    }
    if !frontmatter.metadata.is_empty() {
        fields.insert("metadata".into(), Value::Object(frontmatter.metadata.clone()));
    }
    let rest = crate::yaml::dump_quoted(&Value::Object(fields));
    let content = if body.ends_with('\n') { body.to_string() } else { format!("{body}\n") };
    format!("---\nname: {}\n{rest}---\n\n{content}", frontmatter.name)
}

fn frontmatter_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"(?s)\A---\r?\n(.*?)\r?\n---(?:\r?\n|\z)(.*)\z").expect("valid regex"))
}

fn type_name(value: Option<&Value>) -> &'static str {
    match value {
        None => "undefined",
        Some(Value::Null) => "null",
        Some(Value::Bool(_)) => "boolean",
        Some(Value::Number(_)) => "number",
        Some(Value::String(_)) => "string",
        Some(Value::Array(_)) => "array",
        Some(Value::Object(_)) => "object",
    }
}

/// The checks the TypeScript CLI ran with zod, with zod's wording.
fn check_string(loaded: &Map<String, Value>, key: &str, max: usize) -> Result<String, SkillMdError> {
    let invalid = |detail: String| SkillMdError(format!("Invalid frontmatter: {key} {detail}"));
    let Some(Value::String(text)) = loaded.get(key) else {
        return Err(invalid(format!("Invalid input: expected string, received {}", type_name(loaded.get(key)))));
    };
    let length = text.encode_utf16().count();
    if length < 1 {
        return Err(invalid("Too small: expected string to have >=1 characters".into()));
    }
    if length > max {
        return Err(invalid(format!("Too big: expected string to have <={max} characters")));
    }
    Ok(text.clone())
}

pub fn parse_skill_md(text: &str) -> Result<(SkillFrontmatter, String), SkillMdError> {
    let captures = frontmatter_re().captures(text).ok_or_else(|| {
        SkillMdError("No frontmatter: the file must start with a --- block holding name and description".into())
    })?;
    let loaded =
        crate::yaml::load(&captures[1]).map_err(|error| SkillMdError(format!("Invalid frontmatter YAML: {error}")))?;
    let Value::Object(loaded) = loaded else {
        return Err(SkillMdError("Frontmatter must be a YAML mapping".into()));
    };

    let name = check_string(&loaded, "name", 64)?;
    if !is_valid_skill_name(&name) {
        return Err(SkillMdError(
            "Invalid frontmatter: name lowercase letters, digits and single dashes, 1-64 characters".into(),
        ));
    }
    let description = check_string(&loaded, "description", 1024)?;
    let mut metadata = Map::new();
    match loaded.get("metadata") {
        None => {}
        Some(Value::Object(entries)) => {
            for (key, value) in entries {
                match value {
                    Value::String(_) | Value::Number(_) | Value::Bool(_) => {
                        metadata.insert(key.clone(), Value::String(js_string(value)));
                    }
                    _ => return Err(SkillMdError(format!("Invalid frontmatter: metadata.{key} Invalid input"))),
                }
            }
        }
        Some(other) => {
            return Err(SkillMdError(format!(
                "Invalid frontmatter: metadata Invalid input: expected record, received {}",
                type_name(Some(other))
            )));
        }
    }

    let extra: Map<String, Value> = loaded
        .iter()
        .filter(|(key, _)| !KNOWN_KEYS.contains(&key.as_str()))
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect();
    // The render puts one blank line between the frontmatter and the body; take exactly that back.
    let rest = &captures[2];
    let body = rest.strip_prefix("\r\n").or_else(|| rest.strip_prefix('\n')).unwrap_or(rest).to_string();
    if body.trim().is_empty() {
        return Err(SkillMdError("The skill has no instructions below the frontmatter".into()));
    }
    Ok((SkillFrontmatter { name, description, metadata, extra }, body))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn revision<'a>(description: &'a str) -> Revision<'a> {
        Revision {
            id: "skill_1",
            name: "release-checklist",
            description,
            updated_at: "2026-09-10T08:00:00.000Z",
            collection_name: None,
        }
    }

    fn object(value: Value) -> Map<String, Value> {
        value.as_object().cloned().unwrap_or_default()
    }

    #[test]
    fn render_then_parse_round_trips_name_description_metadata_and_body_byte_for_byte() {
        let body = "# Release\n\nStep 1: run `just deploy`.\n\n---\n\nNot frontmatter.\n";
        let text =
            render_skill_md(&frontmatter_for(revision("Use when deploying"), "acme", Map::new(), &Map::new()), body);
        let (frontmatter, parsed_body) = parse_skill_md(&text).unwrap();
        assert_eq!(frontmatter.name, "release-checklist");
        assert_eq!(frontmatter.description, "Use when deploying");
        assert_eq!(
            Value::Object(frontmatter.metadata),
            json!({ META_ID: "skill_1", META_ORG: "acme", META_UPDATED_AT: "2026-09-10T08:00:00.000Z" })
        );
        assert_eq!(parsed_body, body);
        // The exact text the TypeScript CLI wrote, so a switch does not rewrite every skill.
        assert_eq!(
            text,
            "---\nname: release-checklist\ndescription: \"Use when deploying\"\nmetadata:\n  gatana-id: \"skill_1\"\n  \
             gatana-org: \"acme\"\n  gatana-updated-at: \"2026-09-10T08:00:00.000Z\"\n---\n\n# Release\n\nStep 1: run \
             `just deploy`.\n\n---\n\nNot frontmatter.\n"
        );
    }

    #[test]
    fn render_quotes_awkward_descriptions_on_one_line() {
        for description in
            ["Use when: x # not a comment", "Say \"hi\" to <b>them</b>", "Line one\nline two", "It's - a: list"]
        {
            let text =
                render_skill_md(&frontmatter_for(revision(description), "acme", Map::new(), &Map::new()), "body");
            let lines: Vec<&str> = text.split('\n').collect();
            assert_eq!(lines[1], "name: release-checklist");
            assert!(lines[2].starts_with("description: \"") && lines[2].ends_with('"'), "{}", lines[2]);
            let expected = Regex::new(r"\s*\n\s*").unwrap().replace_all(description, " ").to_string();
            assert_eq!(parse_skill_md(&text).unwrap().0.description, expected);
        }
    }

    #[test]
    fn render_adds_exactly_one_trailing_newline_to_the_body() {
        let frontmatter = frontmatter_for(revision("d"), "acme", Map::new(), &Map::new());
        assert!(render_skill_md(&frontmatter, "body").ends_with("\n\nbody\n"));
        assert!(render_skill_md(&frontmatter, "body\n").ends_with("\n\nbody\n"));
    }

    #[test]
    fn parse_accepts_unknown_keys_keeps_them_as_extra_and_coerces_metadata_values_to_strings() {
        let text = [
            "---",
            "name: my-skill",
            "description: Does things",
            "license: MIT",
            "allowed-tools: Bash(git:*) Read",
            "metadata:",
            "  version: 1.0",
            "  stable: true",
            "---",
            "Body",
            "",
        ]
        .join("\n");
        let (frontmatter, body) = parse_skill_md(&text).unwrap();
        assert_eq!(Value::Object(frontmatter.extra), json!({ "license": "MIT", "allowed-tools": "Bash(git:*) Read" }));
        assert_eq!(Value::Object(frontmatter.metadata), json!({ "version": "1", "stable": "true" }));
        assert_eq!(body, "Body\n");
    }

    #[test]
    fn parse_keeps_a_body_that_starts_without_a_blank_line() {
        let (_, body) = parse_skill_md("---\nname: a\ndescription: b\n---\nBody line\n").unwrap();
        assert_eq!(body, "Body line\n");
    }

    #[test]
    fn parse_rejects_missing_frontmatter_bad_names_empty_bodies_and_non_mapping_frontmatter() {
        assert!(parse_skill_md("# no frontmatter\n").is_err());
        assert!(parse_skill_md("---\nname: Bad Name\ndescription: x\n---\nbody\n").unwrap_err().0.contains("name"));
        assert!(
            parse_skill_md("---\nname: ok\ndescription: x\n---\n\n   \n").unwrap_err().0.contains("no instructions")
        );
        assert!(parse_skill_md("---\n- a\n- b\n---\nbody\n").unwrap_err().0.contains("mapping"));
        assert!(parse_skill_md("---\nname: ok\ndescription: x\nmetadata: [1]\n---\nbody\n").is_err());
        assert!(parse_skill_md("---\nname: ok\n---\nbody\n").unwrap_err().0.contains("description"));
    }

    #[test]
    fn frontmatter_for_keeps_foreign_metadata_keys_and_replaces_the_gatana_ones() {
        let frontmatter = frontmatter_for(
            revision("d"),
            "acme",
            object(json!({ "license": "MIT" })),
            &object(json!({ "author": "me", META_ID: "old", META_ORG: "other" })),
        );
        assert_eq!(Value::Object(frontmatter.extra.clone()), json!({ "license": "MIT" }));
        assert_eq!(frontmatter.meta("author"), Some("me"));
        assert_eq!(frontmatter.meta(META_ID), Some("skill_1"));
        assert_eq!(frontmatter.meta(META_ORG), Some("acme"));
    }
}
