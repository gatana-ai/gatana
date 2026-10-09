//! `~/.gatana.config` and the strategies that resolve which organization and credentials a command
//! uses. The file format is the TypeScript CLI's: a user can switch between the two without logging
//! in again.
//!
//! ```json
//! { "orgs": { "acme": { "baseUrl": "https://acme.gatana.ai", "pat": "gk_...",
//!                       "tokens": { "access_token": "...", "refresh_token": "...", "expires_at": 1760000000 },
//!                       "clientId": "apx_..." } },
//!   "defaultOrgId": "acme",
//!   "apexClients": { "https://gatana.ai": "apx_..." } }
//! ```
//!
//! `clientId` is set when the tokens came from a sign-in through the base domain (apex.rs): they
//! were issued to that client and refresh with it. Without it they belong to `<org>-cli`.
//! `apexClients` keeps the client the CLI registered at each base domain.

use crate::util::deep_merge;
use anyhow::{Context, Result, anyhow, bail};
use serde_json::{Map, Value, json};
use std::path::PathBuf;

pub fn config_file_path() -> PathBuf {
    std::env::home_dir().unwrap_or_default().join(".gatana.config")
}

/// The whole file. A missing or unreadable file is an empty configuration, as in the TypeScript CLI.
pub fn read_config() -> Value {
    std::fs::read_to_string(config_file_path())
        .ok()
        .and_then(|text| serde_json::from_str::<Value>(&text).ok())
        .filter(Value::is_object)
        .unwrap_or_else(|| Value::Object(Map::new()))
}

/// Written readable by the owner only: the file holds tokens.
pub fn write_config(config: &Value) -> Result<()> {
    let path = config_file_path();
    let text = serde_json::to_string_pretty(config)?;
    let tmp = path.with_extension(format!("config.{}.tmp", std::process::id()));
    {
        let mut options = std::fs::OpenOptions::new();
        options.write(true).create(true).truncate(true);
        #[cfg(unix)]
        std::os::unix::fs::OpenOptionsExt::mode(&mut options, 0o600);
        let mut file = options.open(&tmp).with_context(|| format!("Failed to write config file {}", tmp.display()))?;
        std::io::Write::write_all(&mut file, text.as_bytes())?;
    }
    std::fs::rename(&tmp, &path).with_context(|| format!("Failed to write config file {}", path.display()))?;
    Ok(())
}

/// The first host label: `https://acme.gatana.ai` is `acme`.
pub fn tenant_from_url(base_url: &str) -> String {
    url::Url::parse(base_url)
        .ok()
        .and_then(|url| url.host_str().map(|host| host.split('.').next().unwrap_or_default().to_string()))
        .unwrap_or_default()
}

/// Merges into the organization's entry (lodash merge, as before), and makes it the default when
/// there is none yet.
pub fn set_organization_config(org_id: &str, update: Value) -> Result<()> {
    let mut config = read_config();
    merge_organization(&mut config, org_id, &update)?;
    write_config(&config)
}

/// What a login writes. The credentials of the organization are replaced, not merged: a personal
/// access token wins over OIDC tokens, and tokens refresh with `clientId`, so either one left over
/// from an earlier login would outlive this one.
pub fn set_organization_login(org_id: &str, login: Value) -> Result<()> {
    let mut config = read_config();
    if let Some(org) = config.get_mut("orgs").and_then(|orgs| orgs.get_mut(org_id)).and_then(Value::as_object_mut) {
        for key in ["pat", "tokens", "clientId"] {
            org.shift_remove(key);
        }
    }
    merge_organization(&mut config, org_id, &login)?;
    write_config(&config)
}

fn merge_organization(config: &mut Value, org_id: &str, update: &Value) -> Result<()> {
    let root = config.as_object_mut().ok_or_else(|| anyhow!("config is not an object"))?;
    let orgs = root.entry("orgs").or_insert_with(|| Value::Object(Map::new()));
    if !orgs.is_object() {
        *orgs = Value::Object(Map::new());
    }
    deep_merge(orgs, &json!({ org_id: update }));
    if root.get("defaultOrgId").and_then(Value::as_str).is_none_or(str::is_empty) {
        root.insert("defaultOrgId".into(), Value::String(org_id.to_string()));
    }
    Ok(())
}

/// The client this CLI registered at a base domain, by its origin (`https://gatana.ai`).
pub fn apex_client(origin: &str) -> Option<String> {
    read_config().get("apexClients")?.get(origin)?.as_str().filter(|id| !id.is_empty()).map(str::to_string)
}

pub fn set_apex_client(origin: &str, client_id: &str) -> Result<()> {
    let mut config = read_config();
    let root = config.as_object_mut().ok_or_else(|| anyhow!("config is not an object"))?;
    let clients = root.entry("apexClients").or_insert_with(|| Value::Object(Map::new()));
    if !clients.is_object() {
        *clients = Value::Object(Map::new());
    }
    clients[origin] = Value::String(client_id.to_string());
    write_config(&config)
}

/// Organization ids are looked up in lower case.
pub fn get_organization(org_id: &str) -> Option<Value> {
    read_config().get("orgs")?.get(org_id.to_lowercase())?.as_object().map(|org| Value::Object(org.clone()))
}

pub fn list_organizations() -> Vec<String> {
    read_config().get("orgs").and_then(Value::as_object).map(|orgs| orgs.keys().cloned().collect()).unwrap_or_default()
}

pub fn default_organization() -> Option<String> {
    read_config().get("defaultOrgId").and_then(Value::as_str).filter(|id| !id.is_empty()).map(str::to_string)
}

pub fn set_default_organization(org_id: &str) -> Result<()> {
    let mut config = read_config();
    if config.pointer(&format!("/orgs/{}", escape_pointer(org_id))).is_none() {
        bail!("{org_id} not found in config");
    }
    config["defaultOrgId"] = Value::String(org_id.to_string());
    write_config(&config)
}

pub fn remove_organization(org_id: &str) -> Result<()> {
    let mut config = read_config();
    let orgs = config.get_mut("orgs").and_then(Value::as_object_mut);
    let Some(orgs) = orgs.filter(|orgs| orgs.contains_key(org_id)) else {
        bail!("{org_id} not found in config");
    };
    orgs.shift_remove(org_id);
    let next_default = orgs.keys().next().cloned();
    if config.get("defaultOrgId").and_then(Value::as_str) == Some(org_id) {
        match next_default {
            Some(next) => config["defaultOrgId"] = Value::String(next),
            None => {
                if let Some(root) = config.as_object_mut() {
                    root.remove("defaultOrgId");
                }
            }
        }
    }
    write_config(&config)
}

fn escape_pointer(key: &str) -> String {
    key.replace('~', "~0").replace('/', "~1")
}

/// Where a command's credentials come from.
#[derive(Clone, Debug)]
pub enum Credentials {
    /// GATANA_API_KEY.
    ApiKey(String),
    /// An organization in the config file: a PAT, or OIDC tokens that may need a refresh.
    File { org: Value },
}

#[derive(Clone, Debug)]
pub struct ResolvedConfig {
    pub org_id: String,
    pub base_url: String,
    pub credentials: Credentials,
}

impl ResolvedConfig {
    /// What `gatana config current` shows.
    pub fn describe(&self) -> Value {
        json!({ "orgId": self.org_id, "baseUrl": self.base_url })
    }

    /// The bearer token for requests. An OIDC access token about to expire is refreshed and the new
    /// tokens are written back to the config file.
    pub async fn token(&self, http: &reqwest::Client) -> Result<String> {
        let org = match &self.credentials {
            Credentials::ApiKey(key) => return Ok(key.clone()),
            Credentials::File { org } => org,
        };
        if let Some(pat) = org.get("pat").and_then(Value::as_str).filter(|pat| !pat.is_empty()) {
            return Ok(pat.to_string());
        }
        let tokens = org.get("tokens");
        let access = tokens.and_then(|t| t.get("access_token")).and_then(Value::as_str).filter(|t| !t.is_empty());
        let expires_at = tokens.and_then(|t| t.get("expires_at")).and_then(Value::as_f64).unwrap_or(0.0);
        let now = chrono::Utc::now().timestamp() as f64;
        if let Some(access) = access
            && expires_at > now + 60.0
        {
            return Ok(access.to_string());
        }
        let Some(refresh) =
            tokens.and_then(|t| t.get("refresh_token")).and_then(Value::as_str).filter(|t| !t.is_empty())
        else {
            bail!("No valid API key, access token or refresh token available.");
        };
        gatana_api::debug!("gatana", "Access token expired or about to expire, attempting to refresh");
        let client_id = org
            .get("clientId")
            .and_then(Value::as_str)
            .filter(|id| !id.is_empty())
            .map_or_else(|| format!("{}-cli", self.org_id), str::to_string);
        let fresh = crate::oidc::refresh(http, &self.base_url, &client_id, refresh)
            .await
            .map_err(|error| anyhow!("Failed to refresh access token. Please log in again. ({error})"))?;
        let tokens = json!({
            "access_token": fresh.access_token,
            "refresh_token": fresh.refresh_token.as_deref().unwrap_or(refresh),
            "expires_at": fresh.expires_at(),
        });
        set_organization_config(&self.org_id, json!({ "tokens": tokens }))?;
        gatana_api::debug!("gatana", "Token refreshed successfully");
        Ok(fresh.access_token)
    }
}

/// A source of configuration, tried in order.
#[derive(Clone, Debug)]
pub enum Strategy {
    /// GATANA_API_KEY with GATANA_ORG_ID or GATANA_BASE_URL.
    Env,
    /// The config file: the given organization, else GATANA_ORG_ID, else the default one.
    File { org_id: Option<String> },
}

impl Strategy {
    pub fn help(&self) -> &'static str {
        match self {
            Strategy::Env => {
                "EnvConfigStrategy: Provide configuration via environment variables. Required: GATANA_API_KEY and either \
                 GATANA_ORG_ID or GATANA_BASE_URL. Example: export GATANA_API_KEY=your_api_key; export GATANA_ORG_ID=your_org_id"
            }
            Strategy::File { .. } => {
                "FileConfigStrategy: Provide configuration via a local config file. Use the \"gatana config\" commands to \
                 manage this configuration. The CLI will look for the default organization in the config file or use the org \
                 specified by GATANA_ORG_ID env var."
            }
        }
    }

    fn resolve(&self) -> Option<ResolvedConfig> {
        let env = |name: &str| std::env::var(name).ok().filter(|value| !value.is_empty());
        match self {
            Strategy::Env => {
                let key = env("GATANA_API_KEY")?;
                let org_id = env("GATANA_ORG_ID");
                let base_url = env("GATANA_BASE_URL");
                if org_id.is_none() && base_url.is_none() {
                    return None;
                }
                Some(ResolvedConfig {
                    org_id: org_id.clone().unwrap_or_else(|| tenant_from_url(base_url.as_deref().unwrap_or_default())),
                    base_url: base_url.unwrap_or_else(|| format!("https://{}.gatana.ai", org_id.unwrap_or_default())),
                    credentials: Credentials::ApiKey(key),
                })
            }
            Strategy::File { org_id } => {
                let org_id = org_id.clone().or_else(|| env("GATANA_ORG_ID")).or_else(default_organization)?;
                gatana_api::debug!("gatana", "FileConfigLoader loading config for orgId={org_id}");
                let org = get_organization(&org_id)?;
                let base_url = org.get("baseUrl").and_then(Value::as_str).unwrap_or_default().to_string();
                Some(ResolvedConfig { org_id, base_url, credentials: Credentials::File { org } })
            }
        }
    }
}

pub const NO_CONFIGURATION: &str =
    "No valid configuration found. Run \"gatana config login\" to set up your credentials.";

pub fn resolve(strategies: &[Strategy]) -> Result<ResolvedConfig> {
    strategies.iter().find_map(Strategy::resolve).ok_or_else(|| anyhow!(NO_CONFIGURATION))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tenant_is_the_first_host_label() {
        assert_eq!(tenant_from_url("https://acme.gatana.ai"), "acme");
        assert_eq!(tenant_from_url("https://acme.local.gatana.ai/x"), "acme");
        assert_eq!(tenant_from_url("not a url"), "");
    }
}
