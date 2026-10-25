//! The organization: its settings, plan and quotas. The backend calls it the tenant, and only its
//! owners can read it.

use super::MASK;
use crate::context::Context;
use crate::output::{self, Format, Options};
use crate::util::{deep_merge, get_path, set_path};
use anyhow::{Result, anyhow, bail};
use base64::Engine as _;
use serde_json::{Map, Value, json};
use std::path::Path;

/// The settings that hold a secret, hidden unless `--show-secrets` is given.
const SECRET_PATHS: [&str; 1] = ["upstreamOidcConfiguration.clientSecret"];

/// The largest logo the backend takes.
const LOGO_MAX_BYTES: usize = 256 * 1024;

async fn read_tenant(context: &Context) -> Result<Value> {
    let org_id = &context.config()?.org_id;
    let response = context.api().await?.v1().get_tenant(org_id).value().await?;
    Ok(response.get("tenant").cloned().unwrap_or(response))
}

pub async fn get(context: &Context, show_secrets: bool) -> Result<()> {
    let tenant = read_tenant(context).await?;
    let json_out = output::format_explicit() && output::format() == Format::Json;
    output::output(&shown(tenant, show_secrets, json_out), Options::yaml());
    Ok(())
}

/// The tenant as `get org` prints it: secrets masked, and the logo, a data URL of up to 256 KB,
/// as its type and size except in JSON, where a script may want to save it.
fn shown(mut tenant: Value, show_secrets: bool, full_logo: bool) -> Value {
    if !show_secrets {
        for path in SECRET_PATHS {
            if get_path(&tenant, path).and_then(Value::as_str).is_some_and(|secret| !secret.is_empty()) {
                set_path(&mut tenant, path, json!(MASK));
            }
        }
    }
    if !full_logo
        && let Some(logo) = tenant.get_mut("logo")
        && let Some(summary) = logo.as_str().and_then(logo_summary)
    {
        *logo = json!(summary);
    }
    tenant
}

/// `<image/png, 12 KB>` for a data URL.
fn logo_summary(url: &str) -> Option<String> {
    let (header, data) = url.strip_prefix("data:")?.split_once(',')?;
    let mime = header.split(';').next().unwrap_or(header);
    let bytes = data.len() * 3 / 4;
    Some(format!("<{mime}, {} KB>", bytes.div_ceil(1024)))
}

/// The plan, the accounts and the servers, in place of seats and credits, which are gone.
pub async fn describe(context: &Context) -> Result<()> {
    let tenant = read_tenant(context).await?;
    let api = context.api().await?;
    let org_id = &context.config()?.org_id;
    let subscription = api.v1().get_tenant_subscription(org_id).value().await.ok();
    let quotas = api.v1().get_quota_and_usage().value().await.ok();
    let pick = |value: &Option<Value>, path: &str| {
        value.as_ref().and_then(|value| get_path(value, path)).cloned().unwrap_or(Value::Null)
    };
    let usage = |kind: &str| {
        json!({
            "inUse": pick(&quotas, &format!("quotas.{kind}.current")),
            "limit": pick(&quotas, &format!("quotas.{kind}.quota")),
        })
    };
    let shown = json!({
        "id": tenant.get("id"),
        "displayName": tenant.get("displayName"),
        "plan": {
            "name": pick(&subscription, "subscriptionPlan"),
            "status": pick(&subscription, "subscription.status"),
            "trialEndsAt": pick(&subscription, "subscription.trialEndsAt"),
            "cancelsAt": pick(&subscription, "subscription.cancelsAt"),
        },
        "accounts": usage("accounts"),
        "servers": usage("mcpServers"),
    });
    output::output(&shown, Options::yaml());
    Ok(())
}

pub async fn patch(context: &Context, input: Option<Value>, logo: Option<&Path>, remove_logo: bool) -> Result<()> {
    let mut patch = match input {
        Some(Value::Object(map)) => map,
        Some(_) => bail!("The patch must be a JSON object."),
        None => Map::new(),
    };
    if let Some(path) = logo {
        patch.insert("logo".into(), json!(logo_data_url(path)?));
    }
    if remove_logo {
        patch.insert("logo".into(), json!(""));
    }
    if patch.is_empty() {
        bail!("No input provided. Use -f <file>, -p, --logo, or pipe JSON via stdin.");
    }
    let tenant = read_tenant(context).await?;
    let body = merge_patch(&tenant, &patch)?;
    let keys: Vec<String> = body.keys().cloned().collect();
    let org_id = &context.config()?.org_id;
    context.api().await?.v1().update_tenant_raw(org_id, Value::Object(body)).send().await?;
    output::success(&format!("Updated the organization: {}.", keys.join(", ")));
    Ok(())
}

/// What the update is sent. The backend changes only the keys it is given, but a key that holds an
/// object it replaces whole, so each such key is merged here into the stored value first. With
/// that, `upstreamOidcConfiguration.clientId=x` changes one field and keeps the rest, the client
/// secret included.
pub(crate) fn merge_patch(tenant: &Value, patch: &Map<String, Value>) -> Result<Map<String, Value>> {
    if holds_mask(&Value::Object(patch.clone())) {
        bail!(
            "The patch holds \"{MASK}\", which only hides a secret. Give the real value, or leave the key out to keep the stored one."
        );
    }
    let mut body = Map::new();
    for (key, value) in patch {
        let stored = match key.as_str() {
            "assistantLlmConfiguration" => assistant_base(tenant, value),
            _ => tenant.get(key).cloned(),
        };
        let merged = match stored {
            Some(mut stored) if stored.is_object() && value.is_object() => {
                deep_merge(&mut stored, value);
                stored
            }
            _ => value.clone(),
        };
        body.insert(key.clone(), merged);
    }
    Ok(body)
}

fn holds_mask(value: &Value) -> bool {
    match value {
        Value::String(text) => text == MASK,
        Value::Array(items) => items.iter().any(holds_mask),
        Value::Object(map) => map.values().any(holds_mask),
        _ => false,
    }
}

/// The stored model endpoint of the assistant, as an update would send it. Reading the tenant
/// gives only its status, without the credentials, and an update that leaves a credential out
/// keeps the stored one. None when the patch names another provider, whose fields differ.
fn assistant_base(tenant: &Value, patch: &Value) -> Option<Value> {
    let status = tenant.get("assistantLlmConfigurationStatus")?.as_object()?;
    if let Some(provider) = patch.get("provider")
        && Some(provider) != status.get("provider")
    {
        return None;
    }
    let fields = status.iter().filter(|(key, value)| !value.is_null() && !key.starts_with("has"));
    Some(Value::Object(fields.map(|(key, value)| (key.clone(), value.clone())).collect()))
}

/// A logo file as the data URL that the backend stores.
fn logo_data_url(path: &Path) -> Result<String> {
    let extension = path.extension().and_then(|ext| ext.to_str()).map(str::to_ascii_lowercase);
    let mime = match extension.as_deref() {
        Some("png") => "image/png",
        Some("jpg" | "jpeg") => "image/jpeg",
        Some("webp") => "image/webp",
        Some("svg") => "image/svg+xml",
        _ => bail!("The logo must be a PNG, JPEG, WebP or SVG file: {}", path.display()),
    };
    let bytes = std::fs::read(path).map_err(|error| anyhow!("{}: {error}", path.display()))?;
    if bytes.len() > LOGO_MAX_BYTES {
        bail!("The logo is {} KB. The limit is {} KB.", bytes.len().div_ceil(1024), LOGO_MAX_BYTES / 1024);
    }
    Ok(format!("data:{mime};base64,{}", base64::engine::general_purpose::STANDARD.encode(bytes)))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn tenant() -> Value {
        json!({
            "id": "acme",
            "displayName": "Acme",
            "upstreamOidcConfiguration": { "issuer": "https://idp.example.com", "clientId": "old", "clientSecret": "s3cret" },
            "defaultResourceRequests": { "cpu": "100m", "memory": "128Mi" },
            "assistantLlmConfigurationStatus": {
                "provider": "openai-compatible", "model": "m1", "baseUrl": "https://llm.example.com",
                "region": null, "resourceName": null, "apiVersion": null, "hasApiKey": true, "hasAwsAccessKey": false
            },
            "logo": "data:image/png;base64,AAAA"
        })
    }

    fn patch(value: Value) -> Map<String, Value> {
        value.as_object().unwrap().clone()
    }

    #[test]
    fn a_nested_setting_keeps_its_other_fields() {
        let body =
            merge_patch(&tenant(), &patch(json!({ "upstreamOidcConfiguration": { "clientId": "new" } }))).unwrap();
        assert_eq!(
            body,
            patch(
                json!({ "upstreamOidcConfiguration": { "issuer": "https://idp.example.com", "clientId": "new", "clientSecret": "s3cret" } })
            )
        );
    }

    #[test]
    fn plain_and_unset_settings_go_as_given() {
        let body = merge_patch(
            &tenant(),
            &patch(json!({ "displayName": "Acme Inc", "upstreamSamlConfiguration": { "entryPoint": "https://x" } })),
        )
        .unwrap();
        assert_eq!(
            body,
            patch(json!({ "displayName": "Acme Inc", "upstreamSamlConfiguration": { "entryPoint": "https://x" } }))
        );
        let cleared = merge_patch(&tenant(), &patch(json!({ "upstreamOidcConfiguration": null }))).unwrap();
        assert_eq!(cleared["upstreamOidcConfiguration"], Value::Null);
    }

    #[test]
    fn the_mask_is_refused_wherever_it_is() {
        let error = merge_patch(&tenant(), &patch(json!({ "upstreamOidcConfiguration": { "clientSecret": MASK } })))
            .unwrap_err();
        assert!(error.to_string().contains("only hides a secret"));
    }

    #[test]
    fn the_assistant_endpoint_merges_onto_its_status_without_credentials() {
        let body = merge_patch(&tenant(), &patch(json!({ "assistantLlmConfiguration": { "model": "m2" } }))).unwrap();
        assert_eq!(
            body["assistantLlmConfiguration"],
            json!({ "provider": "openai-compatible", "model": "m2", "baseUrl": "https://llm.example.com" })
        );
        let other =
            json!({ "assistantLlmConfiguration": { "provider": "bedrock", "model": "m3", "region": "eu-west-1" } });
        assert_eq!(
            merge_patch(&tenant(), &patch(other.clone())).unwrap()["assistantLlmConfiguration"],
            other["assistantLlmConfiguration"]
        );
    }

    #[test]
    fn secrets_and_the_logo_are_shortened_for_reading() {
        let read = shown(tenant(), false, false);
        assert_eq!(read["upstreamOidcConfiguration"]["clientSecret"], json!(MASK));
        assert_eq!(read["logo"], json!("<image/png, 1 KB>"));
        let full = shown(tenant(), true, true);
        assert_eq!(full["upstreamOidcConfiguration"]["clientSecret"], json!("s3cret"));
        assert_eq!(full["logo"], json!("data:image/png;base64,AAAA"));
        // No secret stored: nothing to hide, and nothing that looks like one
        let mut bare = tenant();
        bare["upstreamOidcConfiguration"] = Value::Null;
        assert_eq!(shown(bare, false, false)["upstreamOidcConfiguration"], Value::Null);
    }

    #[test]
    fn logos_become_data_urls_and_wrong_files_are_refused() {
        let dir = tempfile::tempdir().unwrap();
        let png = dir.path().join("logo.PNG");
        std::fs::write(&png, [0x89, b'P', b'N', b'G']).unwrap();
        assert_eq!(logo_data_url(&png).unwrap(), "data:image/png;base64,iVBORw==");
        let gif = dir.path().join("logo.gif");
        std::fs::write(&gif, b"GIF89a").unwrap();
        assert!(logo_data_url(&gif).is_err());
        let large = dir.path().join("large.svg");
        std::fs::write(&large, vec![b' '; LOGO_MAX_BYTES + 1]).unwrap();
        assert_eq!(logo_data_url(&large).unwrap_err().to_string(), "The logo is 257 KB. The limit is 256 KB.");
    }
}
