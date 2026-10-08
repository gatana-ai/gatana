//! get, describe, create, delete and patch.
//!
//! Server objects are read raw: their transport configuration is a union the backend grows, and a
//! command that only needs a slug or an id must not break on a transport this version does not know.

use super::{Silent, text_at};
use crate::cli::{
    CreateCommand, CredentialScope, DeleteCommand, DescribeCommand, GetCommand, PatchCommand, TransportType,
};
use crate::context::Context;
use crate::output::{self, Column, Options};
use crate::skills::api::HttpSkillsApi;
use crate::util::{format_age, get_path, parse_inline_object, read_piped_stdin};
use anyhow::{Result, anyhow, bail};
use gatana_api::v1::{self, query};
use serde_json::{Map, Value, json};
use std::path::Path;

const SERVER_COLUMNS: [Column; 5] = [
    Column::path("Slug", "slug"),
    Column::path("Enabled", "isEnabled"),
    Column::path("Type", "transportConfig.type"),
    Column::computed("Last Updated", |row| json!(format_age(row.get("updatedAt")))),
    Column::computed("Age", |row| json!(format_age(row.get("createdAt")))),
];

const TOOL_COLUMNS: [Column; 3] =
    [Column::path("Name", "universalName"), Column::path("Server", "serverSlug"), Column::path("Enabled", "isEnabled")];

const CREDENTIAL_COLUMNS: [Column; 7] = [
    Column::path("ID", "id"),
    Column::path("Server", "serverSlug"),
    Column::path("Scope", "scope"),
    Column::path("Type", "type"),
    Column::computed("Owner", |row| {
        ["userEmail", "profileName"]
            .iter()
            .find_map(|key| row.get(*key).filter(|value| !value.is_null()).cloned())
            .unwrap_or(json!("<server>"))
    }),
    Column::computed("Last Used", |row| json!(format_age(row.get("lastUsedAt")))),
    Column::computed("Authorized", |row| json!(format_age(row.get("authorizedAt")))),
];

const SANDBOX_COLUMNS: [Column; 5] = [
    Column::path("ID", "id"),
    Column::computed("User", |row| {
        get_path(row, "user.email").filter(|v| !v.is_null()).cloned().unwrap_or(json!("<unknown>"))
    }),
    Column::path("Archived", "isArchived"),
    Column::computed("Last Activity", |row| json!(format_age(row.get("lastActivityAt")))),
    Column::computed("Age", |row| json!(format_age(row.get("createdAt")))),
];

/// `server_tool` is the tool `tool` of the server `server`; the server slug holds no underscore.
pub(crate) fn split_tool_name(name: &str) -> Result<(&str, &str)> {
    name.split_once('_')
        .filter(|(server, tool)| !server.is_empty() && !tool.is_empty())
        .ok_or_else(|| anyhow!("Invalid tool name: \"{name}\". Expected format: <server>_<tool_name>"))
}

async fn server_id(context: &Context, slug: &str) -> Result<String> {
    let server = context.api().await?.v2().get_server_v2(slug).value().await?;
    text_at(&server, "/id").map(str::to_string).ok_or_else(|| anyhow!("Server '{slug}' has no id"))
}

fn array_at(value: &Value, key: &str) -> Vec<Value> {
    value.get(key).and_then(Value::as_array).cloned().unwrap_or_default()
}

pub async fn get(context: &Context, resource: GetCommand) -> Result<()> {
    match resource {
        GetCommand::Server { name: Some(slug) } => {
            let server = context.api().await?.v2().get_server_v2(&slug).value().await?;
            output::output(&server, Options::yaml());
        }
        GetCommand::Server { name: None } => {
            let list = context.api().await?.v2().list_servers_v2().value().await?;
            output::output(&json!({ "servers": array_at(&list, "servers") }), Options::columns(&SERVER_COLUMNS));
        }
        GetCommand::Tool { name: Some(name), .. } => {
            let (server, tool) = split_tool_name(&name)?;
            let found = context.api().await?.v1().get_mcp_server_tool(server, tool).value().await?;
            output::output(&found, Options::yaml());
        }
        GetCommand::Tool { name: None, enabled } => {
            let list = context.api().await?.v1().list_tools(&query::ListTools::default()).value().await?;
            let tools: Vec<Value> = array_at(&list, "tools")
                .into_iter()
                .filter(|tool| !enabled || tool.get("isEnabled") == Some(&Value::Bool(true)))
                .collect();
            if tools.is_empty() && !output::machine_readable() {
                output::println("No tools found.");
            } else {
                output::output(&Value::Array(tools), Options::columns(&TOOL_COLUMNS));
            }
        }
        GetCommand::Creds { id, server, with_effective } => {
            let api = context.api().await?;
            let server_id = match &server {
                Some(slug) => Some(server_id(context, slug).await?),
                None => None,
            };
            let list =
                api.v2().list_credentials_v2(&gatana_api::v2::query::ListCredentialsV2 { server_id }).value().await?;
            let credentials = array_at(&list, "credentials");
            let Some(id) = id else {
                output::output(&json!({ "credentials": credentials }), Options::columns(&CREDENTIAL_COLUMNS));
                return Ok(());
            };
            let Some(Value::Object(credential)) =
                credentials.into_iter().find(|credential| text_at(credential, "/id") == Some(&id))
            else {
                let on = server.map(|slug| format!(" on server '{slug}'")).unwrap_or_default();
                bail!("Credential '{id}' not found{on}.");
            };
            let mut shown = credential.clone();
            if let Ok(secret) = api.v2().get_credential_secret_v2(&id).value().await {
                shown.insert("secret".into(), secret);
            }
            if with_effective {
                let slug = credential.get("serverSlug").and_then(Value::as_str).unwrap_or_default();
                let query = query::GetMcpServerCredentialsToken { credentials_id: Some(id.clone()) };
                if let Ok(effective) = api.v1().get_mcp_server_credentials_token(slug, &query).value().await {
                    shown.insert("effective".into(), effective);
                }
            }
            output::output(&Value::Object(shown), Options::yaml());
        }
        GetCommand::Sandbox { id: Some(id), .. } => {
            let sandbox = context.api().await?.v1().get_sandbox(&id).value().await?;
            output::output(&sandbox, Options::yaml());
        }
        GetCommand::Sandbox { id: None, all } => {
            let query = query::ListSandboxes { all: Some(all.to_string()) };
            let list = context.api().await?.v1().list_sandboxes(&query).value().await?;
            output::output(&json!({ "sandboxes": array_at(&list, "sandboxes") }), Options::columns(&SANDBOX_COLUMNS));
        }
        GetCommand::Skill { name, query } => {
            let api = context.api().await?;
            let skills = HttpSkillsApi::new(api, &context.config()?.base_url);
            crate::skills::show_skills(&skills, name.as_deref(), query.as_deref(), None).await?;
        }
    }
    Ok(())
}

pub async fn describe(context: &Context, resource: DescribeCommand) -> Result<()> {
    match resource {
        DescribeCommand::Server { name } => {
            let api = context.api().await?;
            let server = api.v2().get_server_v2(&name).value().await?;
            let id = text_at(&server, "/id").unwrap_or_default().to_string();
            let audit = query::ListAuditLogs {
                entity_types: vec!["mcp_server".into(), "mcp".into()],
                limit: Some("5".into()),
                entity_id: Some(id.clone()),
                ..Default::default()
            };
            // Read raw: the list leaves out `onlySuperadminVisibility`, which the schema requires.
            let logs: Vec<Value> = array_at(&api.v1().list_audit_logs(&audit).value().await?, "data")
                .iter()
                .map(|log| {
                    let mut row = Map::new();
                    row.insert("eventName".into(), log.get("eventName").cloned().unwrap_or(Value::Null));
                    row.insert("age".into(), json!(format_age(log.get("createdAt"))));
                    if text_at(log, "/eventName") == Some("tools/call") {
                        row.insert("tool".into(), get_path(log, "details.toolName").cloned().unwrap_or(json!("n/a")));
                    }
                    Value::Object(row)
                })
                .collect();
            let query = gatana_api::v2::query::ListCredentialsV2 { server_id: Some(id) };
            let credentials: Vec<Value> = array_at(&api.v2().list_credentials_v2(&query).value().await?, "credentials")
                .iter()
                .map(|credential| {
                    let scope = credential.get("scope").cloned().unwrap_or(Value::Null);
                    let owner = if scope == json!("server") {
                        json!("<self>")
                    } else {
                        ["profileName", "userEmail"]
                            .iter()
                            .find_map(|key| credential.get(*key).filter(|value| !value.is_null()).cloned())
                            .unwrap_or(json!("<unknown>"))
                    };
                    json!({ "id": credential.get("id"), "scope": scope, "owner": owner })
                })
                .collect();
            output::output(&json!({ "server": server, "logsTop5": logs, "credentials": credentials }), Options::yaml());
        }
        DescribeCommand::Skill { name } => {
            let api = context.api().await?;
            let skills = HttpSkillsApi::new(api, &context.config()?.base_url);
            crate::skills::show_skills(&skills, Some(&name), None, None).await?;
        }
    }
    Ok(())
}

/// Lower case letters, digits and single dashes, as the backend wants slugs.
fn normalize_slug(slug: &str) -> String {
    let cleaned: String =
        slug.to_lowercase().chars().filter(|ch| ch.is_ascii_lowercase() || ch.is_ascii_digit() || *ch == '-').collect();
    let mut collapsed = String::new();
    for ch in cleaned.chars() {
        if ch == '-' && collapsed.ends_with('-') {
            continue;
        }
        collapsed.push(ch);
    }
    collapsed.trim_matches('-').to_string()
}

fn transport_type(transport: TransportType) -> v1::types::CreateServerRequestTransportType {
    use v1::types::CreateServerRequestTransportType as Wire;
    match transport {
        TransportType::Hosted => Wire::Hosted,
        TransportType::Stdio => Wire::Stdio,
        TransportType::Httpstreaming => Wire::Httpstreaming,
        TransportType::Sse => Wire::Sse,
    }
}

/// The text of `-f <file>`, or of stdin when something is piped in.
fn file_or_stdin(file: Option<&Path>) -> Result<Option<String>> {
    match file {
        Some(file) => Ok(Some(std::fs::read_to_string(file).map_err(|error| anyhow!("{}: {error}", file.display()))?)),
        None => Ok(read_piped_stdin()?.filter(|text| !text.trim().is_empty())),
    }
}

pub async fn create(context: &Context, resource: CreateCommand) -> Result<()> {
    match resource {
        CreateCommand::Server { slug, transport_type: transport } => {
            let slug = match slug {
                Some(slug) => slug,
                None => dialoguer::Input::<String>::new()
                    .with_prompt("Enter the slug for the server")
                    .validate_with(|value: &String| match value.trim() {
                        "" => Err("Server slug is required"),
                        text if text.len() < 3 => Err("Server slug must be at least 3 characters long"),
                        _ => Ok(()),
                    })
                    .interact_text()?,
            };
            let transport = match transport {
                Some(transport) => transport,
                None => {
                    let choices =
                        [TransportType::Httpstreaming, TransportType::Sse, TransportType::Stdio, TransportType::Hosted];
                    let labels = ["httpstreaming", "sse", "stdio", "hosted"];
                    let index = dialoguer::Select::new()
                        .with_prompt("Select the transport type for the server")
                        .items(labels)
                        .default(0)
                        .interact()?;
                    choices[index]
                }
            };
            let body = v1::types::CreateServerRequest {
                slug: normalize_slug(&slug),
                transport_type: transport_type(transport),
                is_output_compression_enabled: None,
                visibility: None,
            };
            let created = context.api().await?.v1().create_mcp_server(&body).value().await?;
            let slug = text_at(&created, "/server/slug")
                .ok_or_else(|| anyhow!("Failed to create server: no server data returned"))?;
            output::success(&format!("Created server {slug}"));
        }
        CreateCommand::Credentials { server_slug, file, scope } => {
            create_credentials(context, &server_slug, file.as_deref(), scope).await?;
        }
        CreateCommand::Sandbox => {
            let created = context.api().await?.v1().create_sandbox().value().await?;
            output::output(created.get("sandbox").unwrap_or(&created), Options::yaml());
        }
    }
    Ok(())
}

/// The credential type follows the server's authorization method: OAuth takes a token set (or
/// prints the URL that starts the flow), API keys take header and value pairs.
async fn create_credentials(
    context: &Context,
    slug: &str,
    file: Option<&Path>,
    scope: Option<CredentialScope>,
) -> Result<()> {
    let api = context.api().await?;
    let server = api.v1().get_mcp_server(slug).value().await?;
    let method = text_at(&server, "/server/authorization/method").unwrap_or("none");
    if method == "none" {
        output::success("This server does not require credentials.");
        return Ok(());
    }
    let scope = match scope {
        Some(CredentialScope::User) => "user".to_string(),
        Some(CredentialScope::Server) => "server".to_string(),
        None => text_at(&server, "/server/authorization/credentialsScope").unwrap_or("user").to_string(),
    };
    let raw = file_or_stdin(file)?;

    if method == "oauth" {
        let Some(raw) = raw else {
            let query = query::GetMcpServerCredentialsAuthorizeUrl { scope: Some(scope.clone()), ..Default::default() };
            let response = api.v1().get_mcp_server_credentials_authorize_url(slug, &query).send().await?;
            match response.typed()?.url {
                Some(url) => output::success(&format!(
                    "Open this URL to authorize (you can also provide token set directly via -f <file> or stdin):\n{url}"
                )),
                None => output::output(&response.value, Options::yaml()),
            }
            return Ok(());
        };
        let token_set: Value =
            serde_json::from_str(raw.trim()).map_err(|_| anyhow!("Failed to parse OAuth token-set JSON."))?;
        // The token set goes through as given: it may carry fields this version does not model.
        let body = json!({ "type": "oauth", "tokenSet": token_set });
        if scope == "server" {
            api.v1().update_mcp_server_credentials_server_raw(slug, body).send().await?;
        } else {
            api.v1().update_mcp_server_credentials_user_raw(slug, body).send().await?;
        }
        output::success(&format!("OAuth credentials set for server '{slug}'."));
        return Ok(());
    }

    let Some(raw) = raw else {
        bail!("API key credentials require input via -f <file> or stdin as JSON: [[\"header\",\"value\"], …]");
    };
    let parsed: Value = serde_json::from_str(raw.trim())
        .map_err(|_| anyhow!("Failed to parse API keys JSON. Expected format: [[\"header\",\"value\"], …]"))?;
    let apikeys: Vec<(String, String)> = serde_json::from_value(parsed)
        .map_err(|_| anyhow!("API keys must be an array of [string, string] pairs: [[\"header\",\"value\"], …]"))?;
    let body = v1::types::ServerCredentialsCredential::Apikey { apikeys };
    if scope == "server" {
        api.v1().update_mcp_server_credentials_server(slug, &body).send().await?;
    } else {
        api.v1().update_mcp_server_credentials_user(slug, &body).send().await?;
    }
    output::success(&format!("API key credentials set for server '{slug}'."));
    Ok(())
}

pub async fn delete(context: &Context, resource: DeleteCommand) -> Result<()> {
    let api = context.api().await?;
    match resource {
        DeleteCommand::Server { name } => {
            api.v1().delete_mcp_server(&name).send().await?;
            output::success(&format!("Server '{name}' deleted successfully."));
        }
        DeleteCommand::Credentials { id, server } => {
            api.v1().delete_mcp_server_credential(&server, &id).send().await?;
            output::success(&format!("Credential '{id}' deleted from server '{server}'."));
        }
        DeleteCommand::Sandbox { id } => {
            api.v1().delete_sandbox(&id).send().await?;
            output::success(&format!("Sandbox '{id}' deleted successfully."));
        }
    }
    Ok(())
}

pub async fn patch(context: &Context, resource: PatchCommand) -> Result<()> {
    let PatchCommand::Server { server_slug, file, patch } = resource;
    let body = if !patch.is_empty() {
        let body = parse_inline_object(&patch)?;
        if !patch.join(" ").trim_start().starts_with('{') {
            output::info(&format!("Constructed patch object from key=value pairs: {body}"));
        }
        body
    } else {
        let Some(raw) = file_or_stdin(file.as_deref())? else {
            output::error("No input provided. Use -f <file>, -p, or pipe JSON via stdin.");
            return Err(Silent.into());
        };
        serde_json::from_str(raw.trim()).map_err(|_| anyhow!("Failed to parse JSON input."))?
    };
    // A merge patch is whatever the user wrote; the server validates it.
    context.api().await?.v2().patch_server_v2_raw(&server_slug, body).send().await?;
    output::success(&format!("Server '{server_slug}' patched successfully."));
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn slugs_are_normalized_like_the_backend_wants() {
        assert_eq!(normalize_slug("My Server!"), "myserver");
        assert_eq!(normalize_slug("--a--b--"), "a-b");
        assert_eq!(normalize_slug("GitHub-2"), "github-2");
    }

    #[test]
    fn tool_names_split_at_the_first_underscore() {
        assert_eq!(split_tool_name("github_list_repos").unwrap(), ("github", "list_repos"));
        assert!(split_tool_name("nounderscore").is_err());
    }
}
