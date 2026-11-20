//! The audit log: what accounts, agents and Gatana itself did in the organization. The list holds
//! summaries of the events. One event, read by its ID, holds all its details. An account without
//! full access reads only its own events. The backend applies that limit, so the commands do not.
//!
//! Read raw: the list leaves out `onlySuperadminVisibility`, which the schema requires.
//!
//! A credential has an audit log of its own: the changes to it, with the credential before and
//! after, and its token refreshes and rejections. Only an account that may read the secret of the
//! credential reads it, and the backend sends the secret decrypted in the snapshots.

use super::{MASK, array_at, resolve, text_at};
use crate::cli::GetAuditLogArgs;
use crate::context::Context;
use crate::output::{self, Column, Options};
use crate::util::{format_age, from_age, get_path, parse_date};
use anyhow::{Result, bail};
use chrono::{DateTime, NaiveDate, SecondsFormat, TimeDelta, Utc};
use gatana_api::v1::query;
use gatana_api::v1::types::AuditLogFilterConditionField as Field;
use serde_json::{Map, Value, json};

/// The window of a list without --since, as on the Audit Logs page. Without it, the backend counts
/// every event that the organization ever had.
const DEFAULT_SINCE: &str = "7d";

const AUDIT_LOG_COLUMNS: [Column; 7] = [
    Column::path("ID", "id"),
    Column::computed("When", |row| json!(format_age(row.get("eventTime")))),
    Column::path("Type", "entityType"),
    Column::path("Event", "eventName"),
    Column::computed("Entity", entity),
    Column::computed("Detail", detail),
    Column::computed("Account", |row| json!(first_text(row, &["userEmail", "userId"]).unwrap_or("<system>"))),
];

const CREDENTIAL_AUDIT_LOG_COLUMNS: [Column; 5] = [
    Column::path("ID", "id"),
    Column::computed("When", |row| json!(format_age(row.get("createdAt")))),
    Column::path("Event", "eventName"),
    Column::computed("Detail", credential_detail),
    Column::computed("Account", |row| json!(first_text(row, &["userEmail", "userId"]).unwrap_or("<system>"))),
];

fn first_text<'a>(row: &'a Value, paths: &[&str]) -> Option<&'a str> {
    paths.iter().find_map(|path| get_path(row, path).and_then(Value::as_str).filter(|text| !text.is_empty()))
}

/// The thing that the event changed or used, by name where the backend found one.
fn entity(row: &Value) -> Value {
    // The names in the details stay when the thing is deleted
    let names = ["profileName", "serverSlug", "teamName", "details.entityName", "details.serverSlug"];
    if let Some(name) = first_text(row, &names) {
        return json!(name);
    }
    match (text_at(row, "/entityType"), text_at(row, "/entityId")) {
        // A tool call without a server is a call to the gateway itself
        (Some("mcp"), None) => json!("<gateway>"),
        (_, Some(id)) => json!(id),
        _ => Value::Null,
    }
}

/// The part of the entity that the event was about: the tool of a tool call and how the call
/// ended, the server of a profile, or the account or team that a profile got.
fn detail(row: &Value) -> Value {
    if let Some(tool) = first_text(row, &["details.toolName", "details.exposedName"]) {
        let ending = match (text_at(row, "/details/outcome"), row.pointer("/details/isError")) {
            (Some("denied"), _) => match text_at(row, "/details/reason") {
                Some(reason) => format!(" (denied: {reason})"),
                None => " (denied)".into(),
            },
            (Some(outcome), _) if outcome != "ok" => format!(" ({outcome})"),
            (_, Some(Value::Bool(true))) => " (error)".into(),
            _ => String::new(),
        };
        return json!(format!("{tool}{ending}"));
    }
    let name = match text_at(row, "/entityType") {
        Some("profile_server" | "profile_tool") => first_text(row, &["serverSlug"]),
        Some("team_profile") => first_text(row, &["teamName"]),
        _ => first_text(row, &["targetUserName", "details.secretIdentifier"]),
    };
    name.map_or(Value::Null, |name| json!(name))
}

/// The fields that an update changed, or the error of a refresh that failed or of a token that the
/// service rejected.
fn credential_detail(row: &Value) -> Value {
    // A diff is empty when the secret was saved again unchanged: the stored ciphertext differs
    if let Some(diff) = row.pointer("/details/diff").and_then(Value::as_object).filter(|diff| !diff.is_empty()) {
        return json!(diff.keys().map(String::as_str).collect::<Vec<_>>().join(", "));
    }
    let paths = ["details.message", "details.error.error_description", "details.error.message", "details.error.error"];
    first_text(row, &paths).map_or(Value::Null, |text| json!(text))
}

/// Replaces the texts of the decrypted secret in the snapshots of a credential event with the mask.
/// The keys, numbers and nulls stay, so the event still shows which parts changed.
fn mask_credentials(event: &mut Value) {
    fn mask_texts(value: &mut Value) {
        match value {
            Value::String(text) => *text = MASK.into(),
            Value::Array(items) => items.iter_mut().for_each(mask_texts),
            Value::Object(map) => map.values_mut().for_each(mask_texts),
            _ => {}
        }
    }
    for part in ["old", "new", "diff"] {
        if let Some(secret) = event.pointer_mut(&format!("/details/{part}/credentials")) {
            mask_texts(secret);
        }
    }
}

/// The line under a table that has more than one page.
fn print_page(pagination: &Value, page: u32) {
    let number = |key: &str| pagination.get(key).and_then(Value::as_u64).unwrap_or(0);
    if number("totalPages") > 1 {
        let mut line = format!("Page {page} of {}, {} events.", number("totalPages"), number("total"));
        if pagination.get("hasNext") == Some(&Value::Bool(true)) {
            line.push_str(&format!(" Next page: --page {}", page + 1));
        }
        output::println(&output::dim(&line));
    }
}

/// A `--where` condition, checked here because the list ignores a condition that it cannot read: a
/// mistyped field would show every event. The match has no catch-all, so a field that the backend
/// adds stops the build until its operators are here.
fn check_condition(text: &str) -> Result<()> {
    let condition = super::alerts::parse_condition(text)?;
    let field_name = condition["field"].as_str().unwrap_or_default();
    let operator = condition["operator"].as_str().unwrap_or_default();
    let Ok(field) = field_name.parse::<Field>() else {
        bail!(
            "Unknown field \"{field_name}\" in \"{text}\". The fields are in \"gatana schema alert\", under conditions"
        )
    };
    let operators: &[&str] = match field {
        Field::Date => &["after", "before"],
        // A protection field compares whole elements of an array
        Field::ProtectionCheck | Field::ProtectionAction => &["eq", "neq"],
        Field::EventName
        | Field::EntityType
        | Field::EntityId
        | Field::UserId
        | Field::ClientId
        | Field::PatId
        | Field::ServerSlug
        | Field::ToolName
        | Field::Outcome
        | Field::Reason
        | Field::ProfileId
        | Field::TeamId
        | Field::CredentialId
        | Field::SecretStoreId => &["eq", "neq", "contains"],
    };
    if !operators.contains(&operator) {
        bail!("The field {field_name} takes the operators {}, not \"{operator}\"", operators.join(", "));
    }
    Ok(())
}

/// `--since` and `--until`: an age before now (30m, 1h30m, 7d), a day (midnight UTC) or a time. The
/// backend takes UTC with a Z.
fn parse_time(text: &str, now: DateTime<Utc>) -> Result<String> {
    let is_age = text.starts_with(|ch: char| ch.is_ascii_digit())
        && text.ends_with(['s', 'm', 'h', 'd'])
        && text.chars().all(|ch| ch.is_ascii_digit() || "smhd".contains(ch));
    let time = if let Some(age) = from_age(text).filter(|_| is_age) {
        now - TimeDelta::milliseconds(age as i64)
    } else if let Ok(day) = NaiveDate::parse_from_str(text, "%Y-%m-%d") {
        day.and_time(Default::default()).and_utc()
    } else if let Some(time) = parse_date(text) {
        time
    } else {
        bail!(
            "Invalid time \"{text}\". Use an age such as 30m, 12h or 7d, a day such as 2026-11-01 or a time such as 2026-11-01T08:00:00Z"
        )
    };
    Ok(time.to_rfc3339_opts(SecondsFormat::Millis, true))
}

pub async fn list(context: &Context, args: GetAuditLogArgs) -> Result<()> {
    for text in &args.conditions {
        check_condition(text)?;
    }
    let mut filter = args.conditions.clone();
    if let Some(slug) = &args.server {
        // Matches the tool calls of the server and the changes to it
        filter.push(format!("serverSlug:eq:{slug}"));
    }
    let on_date = args.conditions.iter().any(|text| text.starts_with("date:"));
    let since = args.since.clone().or_else(|| (!on_date).then(|| DEFAULT_SINCE.to_string()));
    let now = Utc::now();
    let start_date = since.as_deref().map(|text| parse_time(text, now)).transpose()?;
    let end_date = args.until.as_deref().map(|text| parse_time(text, now)).transpose()?;

    let api = context.api().await?;
    let user_id = match &args.account {
        Some(name) => Some(resolve::id(&resolve::account(api, name).await?).to_string()),
        None => None,
    };
    let query = query::ListAuditLogs {
        page: Some(args.page.to_string()),
        limit: Some(args.limit.to_string()),
        user_id,
        start_date,
        end_date,
        search: args.search,
        filter,
        ..Default::default()
    };
    let list = api.v1().list_audit_logs(&query).value().await?;
    let pagination = list.get("pagination").cloned().unwrap_or(Value::Null);
    output::output(
        &json!({ "events": array_at(&list, "data"), "pagination": pagination }),
        Options::columns(&AUDIT_LOG_COLUMNS),
    );
    if !output::machine_readable() {
        print_page(&pagination, args.page);
        if args.since.is_none() && !on_date && pagination.get("hasNext") != Some(&Value::Bool(true)) {
            output::println(&output::dim(&format!("Events of the last {DEFAULT_SINCE}. Older events: --since 30d")));
        }
    }
    Ok(())
}

pub async fn describe(context: &Context, id: &str) -> Result<()> {
    let event = context.api().await?.v1().get_audit_log(id).value().await?;
    output::output(&event, Options::yaml());
    Ok(())
}

pub async fn list_credential(
    context: &Context,
    credential: &str,
    limit: u32,
    page: u32,
    show_secrets: bool,
) -> Result<()> {
    let api = context.api().await?;
    // The route reads the page from the query, but its OpenAPI document does not declare it
    let call = api.v2().list_credential_audit_logs_v2(credential);
    let list = call.query("page", page.to_string()).query("limit", limit.to_string()).value().await?;
    let mut events = array_at(&list, "data");
    if !show_secrets {
        events.iter_mut().for_each(mask_credentials);
    }
    // The events name the account by ID only. Someone who may read the secret of their own
    // credential may not read the account list, so the IDs then stay.
    if !output::machine_readable()
        && let Ok(users) = api.v1().list_users(&query::ListUsers { type_: Some("all".into()) }).value().await
    {
        let emails: Map<String, Value> = array_at(&users, "users")
            .iter()
            .filter_map(|user| Some((text_at(user, "/id")?.to_string(), user.get("email")?.clone())))
            .collect();
        for event in &mut events {
            if let Some(email) = text_at(event, "/userId").and_then(|id| emails.get(id)) {
                event["userEmail"] = email.clone();
            }
        }
    }
    let pagination = list.get("pagination").cloned().unwrap_or(Value::Null);
    output::output(
        &json!({ "events": events, "pagination": pagination }),
        Options::columns(&CREDENTIAL_AUDIT_LOG_COLUMNS),
    );
    if !output::machine_readable() {
        print_page(&pagination, page);
    }
    Ok(())
}

pub async fn describe_credential(context: &Context, credential: &str, id: &str, show_secrets: bool) -> Result<()> {
    let mut event = context.api().await?.v2().get_credential_audit_log_v2(credential, id).value().await?;
    if !show_secrets {
        mask_credentials(&mut event);
    }
    output::output(&event, Options::yaml());
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn conditions_are_checked_against_the_fields_and_their_operators() {
        assert!(check_condition("outcome:eq:denied").is_ok());
        assert!(check_condition("date:after:2026-11-01T00:00:00Z").is_ok());
        assert!(check_condition("toolName:contains:search").is_ok());
        assert!(check_condition("outcom:eq:denied").unwrap_err().to_string().contains("Unknown field \"outcom\""));
        assert!(check_condition("date:eq:2026-11-01").unwrap_err().to_string().contains("after, before"));
        assert!(check_condition("protectionCheck:contains:pii").is_err());
        assert!(check_condition("outcome:eq:").is_err());
    }

    #[test]
    fn credential_secrets_are_masked_and_the_rest_stays() {
        let mut event = json!({ "eventName": "update", "details": {
            "old": { "id": "cred_1", "credentials": { "tokenSet": { "accessToken": "a1", "expiresAt": 100 } } },
            "new": { "id": "cred_1", "credentials": { "tokenSet": { "accessToken": "a2", "expiresAt": 200 } } },
            "diff": { "credentials": { "tokenSet": { "accessToken": { "from": "a1", "to": "a2" } } }, "lastUsedAt": { "from": null, "to": "t" } },
        } });
        mask_credentials(&mut event);
        assert_eq!(event.pointer("/details/old/credentials/tokenSet/accessToken"), Some(&json!(MASK)));
        assert_eq!(event.pointer("/details/new/credentials/tokenSet/expiresAt"), Some(&json!(200)));
        assert_eq!(event.pointer("/details/diff/credentials/tokenSet/accessToken/to"), Some(&json!(MASK)));
        assert_eq!(event.pointer("/details/diff/lastUsedAt/to"), Some(&json!("t")));
        assert_eq!(event.pointer("/details/new/id"), Some(&json!("cred_1")));
        assert_eq!(credential_detail(&event), json!("credentials, lastUsedAt"));
        let failed =
            json!({ "details": { "error": { "error": "invalid_grant", "error_description": "Token expired" } } });
        assert_eq!(credential_detail(&failed), json!("Token expired"));
    }

    #[test]
    fn times_are_ages_days_or_times_in_utc() {
        let now = parse_date("2026-11-20T12:00:00Z").unwrap();
        assert_eq!(parse_time("7d", now).unwrap(), "2026-11-13T12:00:00.000Z");
        assert_eq!(parse_time("1h30m", now).unwrap(), "2026-11-20T10:30:00.000Z");
        assert_eq!(parse_time("2026-11-01", now).unwrap(), "2026-11-01T00:00:00.000Z");
        assert_eq!(parse_time("2026-11-01T10:00:00+02:00", now).unwrap(), "2026-11-01T08:00:00.000Z");
        assert!(parse_time("7days", now).is_err());
        assert!(parse_time("yesterday", now).is_err());
        assert!(parse_time("2026-11", now).is_err());
    }

    #[test]
    fn tool_calls_show_the_tool_and_how_the_call_ended() {
        let call = |details: Value| json!({ "entityType": "mcp", "serverSlug": "github", "details": details });
        assert_eq!(detail(&call(json!({ "toolName": "search", "outcome": "ok", "isError": false }))), json!("search"));
        assert_eq!(
            detail(&call(json!({ "toolName": "search", "outcome": "ok", "isError": true }))),
            json!("search (error)")
        );
        assert_eq!(
            detail(&call(json!({ "toolName": "search", "outcome": "denied", "reason": "scope" }))),
            json!("search (denied: scope)")
        );
        assert_eq!(detail(&call(json!({ "exposedName": "x", "outcome": "not-found" }))), json!("x (not-found)"));
        assert_eq!(entity(&call(json!({}))), json!("github"));
        let rule =
            json!({ "entityType": "alert_rule", "entityId": "alertrule_1", "details": { "entityName": "Denied" } });
        assert_eq!(entity(&rule), json!("Denied"));
        assert_eq!(entity(&json!({ "entityType": "mcp", "entityId": null })), json!("<gateway>"));
        assert_eq!(entity(&json!({ "entityType": "team", "entityId": "team_1", "teamName": null })), json!("team_1"));
    }
}
