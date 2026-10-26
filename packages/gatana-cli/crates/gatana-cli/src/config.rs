//! `~/.gatana.config` and the strategies that resolve which organization and credentials a command
//! uses. The file format is the TypeScript CLI's: a user can switch between the two without logging
//! in again.
//!
//! ```json
//! { "orgs": { "acme": { "orgId": "acme", "baseUrl": "https://acme.gatana.ai", "pat": "gk_...",
//!                       "tokens": { "access_token": "...", "refresh_token": "...", "expires_at": 1760000000 },
//!                       "clientId": "apx_..." },
//!             "acme.s.gatana.ai": { "orgId": "acme", "baseUrl": "https://acme.s.gatana.ai", ... } },
//!   "defaultOrgId": "acme",
//!   "apexClients": { "https://gatana.ai": "apx_..." } }
//! ```
//!
//! A key in `orgs` is the name a login is saved under, and `defaultOrgId` holds one. The name is
//! the organization ID, or the host when that ID is already saved for another address: the same
//! organization can be signed in on production and staging side by side. Without `orgId` (files
//! the TypeScript CLI wrote), the name is the organization ID.
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

/// Merges into the entry saved under this name (lodash merge, as before), and makes it the default
/// when there is none yet.
pub fn set_organization_config(name: &str, update: Value) -> Result<()> {
    let mut config = read_config();
    merge_organization(&mut config, name, &update)?;
    write_config(&config)
}

/// What a login writes; returns the name it is saved under. The credentials are replaced, not
/// merged: a personal access token wins over OIDC tokens, and tokens refresh with `clientId`, so
/// either one left over from an earlier login would outlive this one.
pub fn set_organization_login(org_id: &str, base_url: &str, credentials: Value) -> Result<String> {
    let mut config = read_config();
    let name = login_name(config.get("orgs").and_then(Value::as_object), org_id, base_url);
    if let Some(org) = config.get_mut("orgs").and_then(|orgs| orgs.get_mut(&name)).and_then(Value::as_object_mut) {
        for key in ["pat", "tokens", "clientId"] {
            org.shift_remove(key);
        }
    }
    let mut login = json!({ "orgId": org_id, "baseUrl": base_url });
    deep_merge(&mut login, &credentials);
    merge_organization(&mut config, &name, &login)?;
    write_config(&config)?;
    Ok(name)
}

/// The entry that already holds this organization at this address, else the organization ID, else
/// the host when the ID is saved for another address.
fn login_name(orgs: Option<&Map<String, Value>>, org_id: &str, base_url: &str) -> String {
    let empty = Map::new();
    let orgs = orgs.unwrap_or(&empty);
    let saved = orgs.iter().find(|(name, org)| {
        organization_id(name, org) == org_id
            && org.get("baseUrl").and_then(Value::as_str).is_some_and(|saved| same_origin(saved, base_url))
    });
    if let Some((name, _)) = saved {
        return name.clone();
    }
    let host = url::Url::parse(base_url)
        .ok()
        .and_then(|url| url.host_str().map(str::to_string))
        .unwrap_or_else(|| base_url.to_string());
    [org_id.to_string(), host.clone()]
        .into_iter()
        .chain((2..).map(|n| format!("{host}-{n}")))
        .find(|name| !orgs.contains_key(name))
        .unwrap_or_default()
}

fn same_origin(a: &str, b: &str) -> bool {
    match (url::Url::parse(a), url::Url::parse(b)) {
        (Ok(a), Ok(b)) => a.origin() == b.origin(),
        _ => a.trim_end_matches('/') == b.trim_end_matches('/'),
    }
}

/// The organization ID of a saved entry.
pub fn organization_id(name: &str, org: &Value) -> String {
    org.get("orgId").and_then(Value::as_str).filter(|id| !id.is_empty()).unwrap_or(name).to_string()
}

/// The command that signs in to this organization at this address again.
pub fn login_command(org_id: &str, base_url: &str) -> String {
    if same_origin(base_url, &format!("https://{org_id}.gatana.ai")) {
        format!("gatana config login {org_id}")
    } else if tenant_from_url(base_url) == org_id {
        format!("gatana config login {base_url}")
    } else {
        format!("gatana config login {org_id} --base-url {base_url}")
    }
}

fn merge_organization(config: &mut Value, name: &str, update: &Value) -> Result<()> {
    let root = config.as_object_mut().ok_or_else(|| anyhow!("the configuration must be a JSON object"))?;
    let orgs = root.entry("orgs").or_insert_with(|| Value::Object(Map::new()));
    if !orgs.is_object() {
        *orgs = Value::Object(Map::new());
    }
    deep_merge(orgs, &json!({ name: update }));
    if root.get("defaultOrgId").and_then(Value::as_str).is_none_or(str::is_empty) {
        root.insert("defaultOrgId".into(), Value::String(name.to_string()));
    }
    Ok(())
}

/// The client this CLI registered at a base domain, by its origin (`https://gatana.ai`).
pub fn apex_client(origin: &str) -> Option<String> {
    read_config().get("apexClients")?.get(origin)?.as_str().filter(|id| !id.is_empty()).map(str::to_string)
}

pub fn set_apex_client(origin: &str, client_id: &str) -> Result<()> {
    let mut config = read_config();
    let root = config.as_object_mut().ok_or_else(|| anyhow!("the configuration must be a JSON object"))?;
    let clients = root.entry("apexClients").or_insert_with(|| Value::Object(Map::new()));
    if !clients.is_object() {
        *clients = Value::Object(Map::new());
    }
    clients[origin] = Value::String(client_id.to_string());
    write_config(&config)
}

/// The saved entry a selector names, with its name: the name itself (also in lower case), or the
/// address it was saved with, as a URL (`https://acme.gatana.ai`) or a host (`acme.gatana.ai`).
pub fn find_organization(selector: &str) -> Option<(String, Value)> {
    find_saved(&read_config(), selector)
}

fn find_saved(config: &Value, selector: &str) -> Option<(String, Value)> {
    let orgs = config.get("orgs")?.as_object()?;
    let by_name = [selector.to_string(), selector.to_lowercase()].into_iter().find(|name| orgs.contains_key(name));
    let name = by_name.or_else(|| {
        orgs.iter()
            .find(|(_, org)| org.get("baseUrl").and_then(Value::as_str).is_some_and(|url| at_address(url, selector)))
            .map(|(name, _)| name.clone())
    })?;
    orgs.get(&name).filter(|org| org.is_object()).map(|org| (name, org.clone()))
}

fn at_address(base_url: &str, selector: &str) -> bool {
    let Ok(base) = url::Url::parse(base_url) else {
        return false;
    };
    if selector.contains("://") {
        url::Url::parse(selector).is_ok_and(|url| url.origin() == base.origin())
    } else {
        base.host_str().is_some_and(|host| host.eq_ignore_ascii_case(selector))
    }
}

/// Every saved entry with its name, in file order.
pub fn list_organizations() -> Vec<(String, Value)> {
    read_config()
        .get("orgs")
        .and_then(Value::as_object)
        .map(|orgs| orgs.iter().map(|(name, org)| (name.clone(), org.clone())).collect())
        .unwrap_or_default()
}

pub fn default_organization() -> Option<String> {
    read_config().get("defaultOrgId").and_then(Value::as_str).filter(|id| !id.is_empty()).map(str::to_string)
}

/// Returns the name of the entry that is now the default.
pub fn set_default_organization(selector: &str) -> Result<String> {
    let mut config = read_config();
    let Some((name, _)) = find_saved(&config, selector) else {
        bail!("{selector} not found in config");
    };
    config["defaultOrgId"] = Value::String(name.clone());
    write_config(&config)?;
    Ok(name)
}

/// Returns the name of the entry it removed.
pub fn remove_organization(selector: &str) -> Result<String> {
    let mut config = read_config();
    let Some((name, _)) = find_saved(&config, selector) else {
        bail!("{selector} not found in config");
    };
    let Some(orgs) = config.get_mut("orgs").and_then(Value::as_object_mut) else {
        bail!("{selector} not found in config");
    };
    orgs.shift_remove(&name);
    let next_default = orgs.keys().next().cloned();
    if config.get("defaultOrgId").and_then(Value::as_str) == Some(name.as_str()) {
        match next_default {
            Some(next) => config["defaultOrgId"] = Value::String(next),
            None => {
                if let Some(root) = config.as_object_mut() {
                    root.remove("defaultOrgId");
                }
            }
        }
    }
    write_config(&config)?;
    Ok(name)
}

/// Where a command's credentials come from.
#[derive(Clone, Debug)]
pub enum Credentials {
    /// GATANA_API_KEY.
    ApiKey(String),
    /// An organization in the config file, by the name it is saved under: a PAT, or OIDC tokens
    /// that may need a refresh.
    File { name: String, org: Value },
}

#[derive(Clone, Debug)]
pub struct ResolvedConfig {
    pub org_id: String,
    pub base_url: String,
    pub credentials: Credentials,
}

impl ResolvedConfig {
    /// What `gatana config current` shows. The saved name only when it is not the organization ID.
    pub fn describe(&self) -> Value {
        let mut described = json!({ "orgId": self.org_id, "baseUrl": self.base_url });
        if let Credentials::File { name, .. } = &self.credentials
            && *name != self.org_id
        {
            described["name"] = Value::String(name.clone());
        }
        described
    }

    /// The bearer token for requests. An OIDC access token about to expire is refreshed and the new
    /// tokens are written back to the config file.
    pub async fn token(&self, http: &reqwest::Client) -> Result<String> {
        let (name, org) = match &self.credentials {
            Credentials::ApiKey(key) => return Ok(key.clone()),
            Credentials::File { name, org } => (name, org),
        };
        let now = chrono::Utc::now().timestamp();
        if let Some(token) = usable_token(org, now) {
            return Ok(token);
        }
        // The server rotates the refresh token on every use and revokes the whole login when a used
        // one comes back. Agents run their session-start hooks side by side, so two processes would
        // refresh with the same token at once, and the one that came second would revoke the tokens
        // the first had just saved. One process refreshes at a time; the next one reads its tokens.
        let _lock = lock_config().await?;
        let org = read_config().get("orgs").and_then(|orgs| orgs.get(name)).cloned().unwrap_or_else(|| org.clone());
        if let Some(token) = usable_token(&org, chrono::Utc::now().timestamp()) {
            gatana_api::debug!("gatana", "Using the access token another process saved");
            return Ok(token);
        }
        let tokens = org.get("tokens");
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
        let fresh = crate::oidc::refresh(http, &self.base_url, &client_id, refresh).await.map_err(|error| {
            let login = login_command(&self.org_id, &self.base_url);
            anyhow!("Could not refresh the access token. Sign in again with {login}. ({error})")
        })?;
        let tokens = json!({
            "access_token": fresh.access_token,
            "refresh_token": fresh.refresh_token.as_deref().unwrap_or(refresh),
            "expires_at": fresh.expires_at(),
        });
        set_organization_config(name, json!({ "tokens": tokens }))?;
        gatana_api::debug!("gatana", "Token refreshed successfully");
        Ok(fresh.access_token)
    }
}

/// The personal access token, or the OIDC access token while it is valid for at least another minute.
fn usable_token(org: &Value, now: i64) -> Option<String> {
    if let Some(pat) = org.get("pat").and_then(Value::as_str).filter(|pat| !pat.is_empty()) {
        return Some(pat.to_string());
    }
    let tokens = org.get("tokens")?;
    let access = tokens.get("access_token").and_then(Value::as_str).filter(|t| !t.is_empty())?;
    let expires_at = tokens.get("expires_at").and_then(Value::as_f64).unwrap_or(0.0);
    (expires_at > (now + 60) as f64).then(|| access.to_string())
}

/// An exclusive lock, held until the file is dropped. It is taken on a file of its own because
/// `write_config` replaces the config file, and a lock on the replaced file would guard nothing.
/// The system releases it when the process ends, so a crash leaves no stale lock behind.
async fn lock_config() -> Result<std::fs::File> {
    let path = config_file_path().with_extension("config.lock");
    let mut options = std::fs::OpenOptions::new();
    options.write(true).create(true).truncate(false);
    #[cfg(unix)]
    std::os::unix::fs::OpenOptionsExt::mode(&mut options, 0o600);
    let file = options.open(&path).with_context(|| format!("Failed to open lock file {}", path.display()))?;
    tokio::task::spawn_blocking(move || file.lock().map(|()| file))
        .await?
        .with_context(|| format!("Failed to lock {}", path.display()))
}

/// A source of configuration, tried in order.
#[derive(Clone, Debug)]
pub enum Strategy {
    /// GATANA_API_KEY with GATANA_ORG_ID or GATANA_BASE_URL.
    Env,
    /// The config file: the given organization, else GATANA_ORG_ID, else the default one.
    File { selector: Option<String> },
}

impl Strategy {
    pub fn help(&self) -> &'static str {
        match self {
            Strategy::Env => "Environment variables: set GATANA_API_KEY and either GATANA_ORG_ID or GATANA_BASE_URL.",
            Strategy::File { .. } => {
                "Saved settings: use \"gatana config\" commands to change them. GATANA_ORG_ID selects a saved \
                 organization. If unset, the CLI uses the default organization."
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
            Strategy::File { selector } => {
                let selector = selector.clone().or_else(|| env("GATANA_ORG_ID")).or_else(default_organization)?;
                gatana_api::debug!("gatana", "FileConfigLoader loading config for {selector}");
                let (name, org) = find_organization(&selector)?;
                let base_url = org.get("baseUrl").and_then(Value::as_str).unwrap_or_default().to_string();
                Some(ResolvedConfig {
                    org_id: organization_id(&name, &org),
                    base_url,
                    credentials: Credentials::File { name, org },
                })
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

    #[test]
    fn usable_token_needs_a_minute_of_validity_left() {
        let tokens = |expires_at: i64| json!({ "tokens": { "access_token": "at", "refresh_token": "rt", "expires_at": expires_at } });
        assert_eq!(usable_token(&tokens(1_000), 900).as_deref(), Some("at"));
        assert_eq!(usable_token(&tokens(1_000), 940), None);
        assert_eq!(usable_token(&json!({ "tokens": { "refresh_token": "rt" } }), 0), None);
        assert_eq!(
            usable_token(&json!({ "pat": "gk_1", "tokens": { "access_token": "at" } }), 0).as_deref(),
            Some("gk_1")
        );
    }

    fn saved() -> Value {
        json!({ "orgs": {
            "acme": { "baseUrl": "https://acme.gatana.ai" },
            "acme.s.gatana.ai": { "orgId": "acme", "baseUrl": "https://acme.s.gatana.ai" },
        } })
    }

    #[test]
    fn a_login_at_another_address_is_saved_under_the_host() {
        let config = saved();
        let orgs = config["orgs"].as_object();
        assert_eq!(login_name(orgs, "acme", "https://acme.gatana.ai/"), "acme");
        assert_eq!(login_name(orgs, "acme", "https://acme.s.gatana.ai"), "acme.s.gatana.ai");
        assert_eq!(login_name(orgs, "acme", "https://acme.d.gatana.ai"), "acme.d.gatana.ai");
        assert_eq!(login_name(orgs, "acme", "http://acme.s.gatana.ai"), "acme.s.gatana.ai-2");
        assert_eq!(login_name(orgs, "other", "https://other.gatana.ai"), "other");
        assert_eq!(login_name(None, "acme", "https://acme.s.gatana.ai"), "acme");
    }

    #[test]
    fn a_saved_organization_is_found_by_name_or_address() {
        let config = saved();
        let name = |selector: &str| find_saved(&config, selector).map(|(name, _)| name);
        assert_eq!(name("acme").as_deref(), Some("acme"));
        assert_eq!(name("ACME").as_deref(), Some("acme"));
        assert_eq!(name("acme.s.gatana.ai").as_deref(), Some("acme.s.gatana.ai"));
        assert_eq!(name("https://acme.s.gatana.ai/").as_deref(), Some("acme.s.gatana.ai"));
        assert_eq!(name("acme.gatana.ai").as_deref(), Some("acme"));
        assert_eq!(name("https://acme.d.gatana.ai"), None);
        let (found, org) = find_saved(&config, "acme.s.gatana.ai").unwrap();
        assert_eq!(organization_id(&found, &org), "acme");
    }

    #[test]
    fn the_login_command_names_the_address_when_it_is_not_the_default() {
        assert_eq!(login_command("acme", "https://acme.gatana.ai"), "gatana config login acme");
        assert_eq!(login_command("acme", "https://acme.s.gatana.ai"), "gatana config login https://acme.s.gatana.ai");
        assert_eq!(
            login_command("acme", "https://gatana.acme.internal"),
            "gatana config login acme --base-url https://gatana.acme.internal"
        );
    }
}
