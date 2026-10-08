//! `gatana config ...`, `auth-info` and `schema`.

use super::{Silent, text_at};
use crate::cli::{ConfigCommand, SchemaCommand};
use crate::config::{self, get_organization, list_organizations, set_organization_config};
use crate::context::Context;
use crate::output::{self, Format, Options};
use crate::util::get_path;
use anyhow::{Context as _, Result, anyhow};
use serde_json::{Value, json};

pub async fn run(context: &Context, command: ConfigCommand) -> Result<()> {
    match command {
        ConfigCommand::Current => {
            output::print(&context.config()?.describe());
            output::info(
                "Note: This is the resolved configuration after applying all strategies (env vars, config file, etc). For more info, run with DEBUG=gatana",
            );
        }
        ConfigCommand::Token => {
            let token = context.config()?.token(context.http()).await?;
            output::print(&Value::String(token));
        }
        ConfigCommand::Login { org_id_or_url, pat, base_url, no_browser } => {
            if let Err(error) = login(context, &org_id_or_url, pat, base_url, !no_browser).await {
                output::error(&format!("Error during login: {error:#}"));
                return Err(Silent.into());
            }
        }
        ConfigCommand::Ls => list(),
        ConfigCommand::SetDefault { org_id } => match config::set_default_organization(&org_id) {
            Ok(()) => output::println(&format!("✅ Set {org_id} as default organization")),
            Err(error) => {
                output::error(&format!("❌ Error setting default organization: {error}"));
                return Err(Silent.into());
            }
        },
        ConfigCommand::Remove { org_id } => match config::remove_organization(&org_id) {
            Ok(()) => output::println(&format!("✅ Removed organization {org_id}")),
            Err(error) => {
                output::error(&format!("❌ Error removing organization: {error}"));
                return Err(Silent.into());
            }
        },
    }
    Ok(())
}

/// With a PAT the token is stored as given; without one the CLI runs the browser device login
/// and stores the OIDC tokens.
async fn login(
    context: &Context,
    org_id_or_url: &str,
    pat: Option<String>,
    base_url: Option<String>,
    browser: bool,
) -> Result<()> {
    let (org_id, derived_base_url) = if org_id_or_url.starts_with("http://") || org_id_or_url.starts_with("https://") {
        let url = url::Url::parse(org_id_or_url).context("invalid URL")?;
        let host = url.host_str().ok_or_else(|| anyhow!("the URL has no host"))?;
        (host.split('.').next().unwrap_or_default().to_string(), Some(url.origin().ascii_serialization()))
    } else {
        (org_id_or_url.to_string(), None)
    };
    let base_url = base_url.or(derived_base_url).unwrap_or_else(|| format!("https://{org_id}.gatana.ai"));
    match pat {
        Some(pat) => set_organization_config(&org_id, json!({ "baseUrl": base_url, "pat": pat }))?,
        None => {
            let scope = "openid profile email offline_access gatana.selfservice";
            let device =
                crate::oidc::start_device_login(context.http(), &base_url, &format!("{org_id}-cli"), scope).await?;
            let url = device.authorization.url().to_string();
            output::println(&format!(
                "Please open {url} to complete the login. If required enter {}",
                device.authorization.user_code
            ));
            // A machine without a browser still has the link above.
            if browser {
                let _ = open::that_detached(&url);
            }
            let tokens = device.wait(context.http()).await?;
            let stored = json!({
                "access_token": tokens.access_token,
                "refresh_token": tokens.refresh_token.as_deref().unwrap_or_default(),
                "expires_at": tokens.expires_at(),
            });
            set_organization_config(&org_id, json!({ "baseUrl": base_url, "tokens": stored }))?;
        }
    }
    output::println("Login successful! You can now use the CLI commands.");
    config::set_default_organization(&org_id)?;
    output::println(&format!("{org_id} is now the active organization."));
    Ok(())
}

fn list() {
    let orgs = list_organizations();
    let default = config::default_organization();
    if orgs.is_empty() {
        output::println("No orgs configured.");
        return;
    }
    output::println("Configured orgs:");
    for org in &orgs {
        let entry = get_organization(org).unwrap_or_default();
        let marker = if default.as_deref() == Some(org.as_str()) { "* " } else { "  " };
        output::println(&format!("  {marker}Org ID: {org}"));
        if let Some(base_url) = text_at(&entry, "/baseUrl") {
            output::println(&format!("    Base URL: {base_url}"));
        }
        let saved = |pointer: &str| text_at(&entry, pointer).is_some_and(|value| !value.is_empty());
        if saved("/pat") {
            output::println("    Personal Access Token: [SAVED]");
        }
        if saved("/tokens/access_token") {
            output::println("    Access Token: [SAVED]");
        }
        if let Some(expires_at) =
            entry.pointer("/tokens/expires_at").and_then(Value::as_f64).filter(|seconds| *seconds > 0.0)
            && let Some(date) = chrono::DateTime::from_timestamp_millis((expires_at * 1000.0) as i64)
        {
            output::println(&format!(
                "    Access Token Expiry: {}",
                date.to_rfc3339_opts(chrono::SecondsFormat::Millis, true)
            ));
        }
        if saved("/tokens/refresh_token") {
            output::println("    Refresh Token: [SAVED]");
        }
        output::println("");
    }
    if let Some(default) = default {
        output::println(&format!("\nDefault organization: {default}"));
    }
}

/// Who the credentials belong to. Read raw and projected: the full answer also carries the API key.
pub async fn auth_info(context: &Context) -> Result<()> {
    let me = context.api().await?.v1().get_auth_me().value().await?;
    let pick = |path: &str| get_path(&me, path).cloned().unwrap_or(Value::Null);
    let shown = json!({
        "user": { "id": pick("user.id"), "email": pick("user.email"), "name": pick("user.name") },
        "org": {
            "id": pick("tenant.id"),
            "displayName": pick("tenant.displayName"),
            "isTrial": pick("tenant.isTrial"),
            "subscriptionPlan": pick("tenant.subscriptionPlan"),
        },
    });
    output::output(&shown, Options::yaml());
    Ok(())
}

/// Replaces `$ref` pointers into the document with what they point at. A reference met again
/// inside itself stays a reference.
fn resolve_refs(node: &Value, root: &Value, stack: &mut Vec<String>) -> Value {
    match node {
        Value::Object(map) => {
            if let Some(Value::String(reference)) = map.get("$ref") {
                if stack.contains(reference) {
                    return node.clone();
                }
                let Some(target) = reference.strip_prefix('#').and_then(|pointer| root.pointer(pointer)) else {
                    return node.clone();
                };
                stack.push(reference.clone());
                let resolved = resolve_refs(target, root, stack);
                stack.pop();
                return resolved;
            }
            Value::Object(map.iter().map(|(key, value)| (key.clone(), resolve_refs(value, root, stack))).collect())
        }
        Value::Array(items) => Value::Array(items.iter().map(|item| resolve_refs(item, root, stack)).collect()),
        other => other.clone(),
    }
}

pub async fn schema(context: &Context, command: SchemaCommand) -> Result<()> {
    let SchemaCommand::Server = command;
    let url = url::Url::parse(&context.config()?.base_url)?.join("/api/v2/openapi.json")?;
    let document: Value = context.http().get(url.clone()).send().await?.error_for_status()?.json().await?;
    let schema = document.pointer("/components/schemas/V2ServerDto").cloned().unwrap_or(Value::Null);
    output::output(&resolve_refs(&schema, &document, &mut Vec::new()), Options::default_format(Format::Json));
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn references_resolve_and_cycles_stay_references() {
        let root = json!({
            "components": { "schemas": {
                "A": { "type": "object", "properties": { "b": { "$ref": "#/components/schemas/B" }, "again": { "$ref": "#/components/schemas/B" } } },
                "B": { "type": "string" },
                "Loop": { "type": "object", "properties": { "self": { "$ref": "#/components/schemas/Loop" } } },
            } }
        });
        let a = resolve_refs(&root["components"]["schemas"]["A"], &root, &mut Vec::new());
        assert_eq!(a["properties"]["b"], json!({ "type": "string" }));
        assert_eq!(a["properties"]["again"], json!({ "type": "string" }));
        let looped = resolve_refs(&json!({ "$ref": "#/components/schemas/Loop" }), &root, &mut Vec::new());
        assert_eq!(looped["properties"]["self"], json!({ "$ref": "#/components/schemas/Loop" }));
    }
}
