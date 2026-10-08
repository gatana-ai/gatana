//! `gatana skills`: install the skills of an organization into the folders AI agents read, follow
//! collections, and push local changes back.

pub mod api;
pub mod frontmatter;
pub mod hooks;
pub mod manifest;
pub mod plan;
pub mod push;
pub mod subscriptions;
pub mod sync;
pub mod targets;

use crate::output::{self, Column, Options};
use crate::util::format_age;
use anyhow::Result;
use api::SkillsApi;
use serde_json::{Value, json};

fn format_bytes(bytes: Option<f64>) -> Value {
    let Some(bytes) = bytes else {
        return Value::Null;
    };
    if bytes < 1024.0 {
        return json!(format!("{bytes}B"));
    }
    json!(format!("{}K", (bytes / 1024.0 + 0.5).floor()))
}

const SKILL_COLUMNS: [Column; 7] = [
    Column::path("Name", "name"),
    Column::computed("Collection", |row| {
        row.get("collectionName").cloned().filter(|v| !v.is_null()).unwrap_or(json!(""))
    }),
    Column::path("Visibility", "visibility"),
    Column::computed("Size", |row| format_bytes(row.get("contentBytes").and_then(Value::as_f64))),
    Column::path("Owner", "createdByUserEmail"),
    Column::computed("Updated", |row| json!(format_age(row.get("updatedAt")))),
    Column::computed("Age", |row| json!(format_age(row.get("createdAt")))),
];

const COLLECTION_COLUMNS: [Column; 6] = [
    Column::path("Name", "name"),
    Column::path("Description", "description"),
    Column::path("Visibility", "visibility"),
    Column::path("Skills", "skillCount"),
    Column::path("Owner", "createdByUserEmail"),
    Column::computed("Updated", |row| json!(format_age(row.get("updatedAt")))),
];

/// List the skills the caller can read, or show one by name with its instructions.
/// `gatana get skills [name]`, `gatana skills ls`
pub async fn show_skills(
    api: &impl SkillsApi,
    name: Option<&str>,
    query: Option<&str>,
    collection: Option<&str>,
) -> Result<()> {
    if let Some(name) = name {
        let skills = api.list(None, None).await?;
        let Some(found) = skills.iter().find(|skill| skill.name == name) else {
            anyhow::bail!("Skill '{name}' not found.");
        };
        let skill = api.get(&found.id).await?;
        output::output(&skill.skill.raw, Options::yaml());
        return Ok(());
    }
    let skills: Vec<Value> = api.list(query, collection).await?.into_iter().map(|skill| skill.raw).collect();
    output::output(&json!({ "skills": skills }), Options::columns(&SKILL_COLUMNS));
    Ok(())
}

/// List the collections the caller can see, with how many of their skills the caller can read.
/// `gatana skills ls --collections`
pub async fn show_collections(api: &impl SkillsApi) -> Result<()> {
    let collections: Vec<Value> = api.list_collections().await?.into_iter().map(|collection| collection.raw).collect();
    output::output(&json!({ "collections": collections }), Options::columns(&COLLECTION_COLUMNS));
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sizes_round_like_javascript() {
        assert_eq!(format_bytes(Some(10.0)), json!("10B"));
        assert_eq!(format_bytes(Some(1536.0)), json!("2K"));
        assert_eq!(format_bytes(Some(1535.0)), json!("1K"));
    }
}
