//! Names on the command line. An account goes by its email address or its ID, a profile and a team
//! by their name or ID, the way a server goes by its slug. Each is found in the list that the caller
//! can read, so a lookup needs no permission beyond what the command itself needs.

use super::{array_at, text_at};
use anyhow::{Result, bail};
use gatana_api::v1::query;
use serde_json::Value;

/// An account, as the account list shows it.
pub async fn account(api: &gatana_api::Client, name: &str) -> Result<Value> {
    let list = api.v1().list_users(&query::ListUsers { type_: Some("all".into()) }).value().await?;
    find(&array_at(&list, "users"), name, "email", "account", "\"gatana get accounts\"")
}

/// A profile, as the profile list shows it.
pub async fn profile(api: &gatana_api::Client, name: &str) -> Result<Value> {
    let list = api.v1().list_profiles(&query::ListProfiles::default()).value().await?;
    find(&array_at(&list, "profiles"), name, "name", "profile", "\"gatana get profiles\"")
}

/// A team, as the team list shows it.
pub async fn team(api: &gatana_api::Client, name: &str) -> Result<Value> {
    let list = api.v1().list_teams(&query::ListTeams::default()).value().await?;
    find(&array_at(&list, "teams"), name, "name", "team", "the Teams page of the dashboard")
}

/// The ID of a row found by one of the functions above.
pub fn id(row: &Value) -> &str {
    text_at(row, "/id").unwrap_or_default()
}

/// The row whose ID is `name`, else the one whose label is `name`, else the one row whose label
/// matches it when case is ignored. An email address is case-insensitive, and a name typed in a
/// terminal often loses its capitals.
pub(crate) fn find(rows: &[Value], name: &str, label_key: &str, kind: &str, where_listed: &str) -> Result<Value> {
    let label = |row: &Value| row.get(label_key).and_then(Value::as_str).unwrap_or_default().to_string();
    if let Some(row) = rows.iter().find(|row| id(row) == name).or_else(|| rows.iter().find(|row| label(row) == name)) {
        return Ok(row.clone());
    }
    let folded = name.to_lowercase();
    let same: Vec<&Value> = rows.iter().filter(|row| label(row).to_lowercase() == folded).collect();
    if let [row] = same.as_slice() {
        return Ok((*row).clone());
    }
    let near: Vec<String> =
        rows.iter().map(label).filter(|label| label.to_lowercase().contains(&folded)).take(3).collect();
    if near.is_empty() {
        bail!("No {kind} \"{name}\". See {where_listed} for the ones there are.");
    }
    bail!(
        "No {kind} \"{name}\". Did you mean {}?",
        near.iter().map(|label| format!("\"{label}\"")).collect::<Vec<_>>().join(", ")
    );
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn rows_are_found_by_id_then_label_then_label_without_case() {
        let rows = vec![
            json!({ "id": "prfl_1", "name": "Engineering" }),
            json!({ "id": "prfl_2", "name": "Sales team" }),
            json!({ "id": "prfl_3", "name": "prfl_1" }),
        ];
        let found = |name: &str| find(&rows, name, "name", "profile", "x").map(|row| id(&row).to_string());
        // An ID wins over a name that looks like one
        assert_eq!(found("prfl_1").unwrap(), "prfl_1");
        assert_eq!(found("Sales team").unwrap(), "prfl_2");
        assert_eq!(found("engineering").unwrap(), "prfl_1");
        let error = found("sales").unwrap_err().to_string();
        assert_eq!(error, "No profile \"sales\". Did you mean \"Sales team\"?");
        assert!(found("marketing").unwrap_err().to_string().starts_with("No profile \"marketing\". See x"));
    }

    #[test]
    fn two_rows_that_differ_only_in_case_are_not_guessed() {
        let rows = vec![json!({ "id": "a", "name": "Ops" }), json!({ "id": "b", "name": "OPS" })];
        assert_eq!(id(&find(&rows, "Ops", "name", "team", "x").unwrap()), "a");
        assert!(find(&rows, "ops", "name", "team", "x").is_err());
    }
}
