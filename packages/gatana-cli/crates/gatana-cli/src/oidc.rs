//! The OAuth parts of `gatana config login`: OpenID discovery, the device authorization grant
//! (RFC 8628) and the refresh token grant. The CLI is a public client named `<org>-cli`.

use anyhow::{Context, Result, anyhow, bail};
use serde::Deserialize;
use serde_json::Value;
use std::time::Duration;

#[derive(Deserialize)]
struct Discovery {
    token_endpoint: String,
    device_authorization_endpoint: Option<String>,
}

#[derive(Deserialize)]
pub struct DeviceAuthorization {
    device_code: String,
    pub user_code: String,
    pub verification_uri: String,
    pub verification_uri_complete: Option<String>,
    expires_in: Option<u64>,
    interval: Option<u64>,
}

impl DeviceAuthorization {
    /// The page the user opens; the complete one carries the code already.
    pub fn url(&self) -> &str {
        self.verification_uri_complete.as_deref().unwrap_or(&self.verification_uri)
    }
}

#[derive(Deserialize)]
pub struct Tokens {
    pub access_token: String,
    pub refresh_token: Option<String>,
    pub expires_in: Option<f64>,
}

impl Tokens {
    /// Unix seconds; 0 when the server did not say.
    pub fn expires_at(&self) -> i64 {
        self.expires_in.map(|seconds| chrono::Utc::now().timestamp() + seconds as i64).unwrap_or(0)
    }
}

async fn discover(http: &reqwest::Client, base_url: &str) -> Result<Discovery> {
    let url = url::Url::parse(base_url)
        .and_then(|base| base.join("/.well-known/openid-configuration"))
        .with_context(|| format!("invalid base URL {base_url}"))?;
    let response = http.get(url.clone()).send().await.context("OpenID discovery failed")?;
    if !response.status().is_success() {
        bail!("OpenID discovery at {url} answered {}", response.status());
    }
    response.json().await.with_context(|| format!("OpenID discovery at {url} returned an unexpected document"))
}

async fn post_form(http: &reqwest::Client, url: &str, fields: &[(&str, &str)]) -> Result<(reqwest::StatusCode, Value)> {
    let body = url::form_urlencoded::Serializer::new(String::new()).extend_pairs(fields).finish();
    let response = http
        .post(url)
        .header(reqwest::header::CONTENT_TYPE, "application/x-www-form-urlencoded")
        .header(reqwest::header::ACCEPT, "application/json")
        .body(body)
        .send()
        .await
        .with_context(|| format!("request to {url} failed"))?;
    let status = response.status();
    let text = response.text().await.unwrap_or_default();
    let value = serde_json::from_str(&text).unwrap_or(Value::String(text));
    Ok((status, value))
}

fn oauth_error(value: &Value) -> String {
    let code = value.get("error").and_then(Value::as_str);
    let description = value.get("error_description").and_then(Value::as_str);
    match (code, description) {
        (Some(code), Some(description)) => format!("{code}: {description}"),
        (Some(code), None) => code.to_string(),
        _ => value.to_string(),
    }
}

/// Starts a device login; the caller shows `url()` and `user_code`, then calls `wait`.
pub struct DeviceLogin {
    token_endpoint: String,
    client_id: String,
    pub authorization: DeviceAuthorization,
}

pub async fn start_device_login(
    http: &reqwest::Client,
    base_url: &str,
    client_id: &str,
    scope: &str,
) -> Result<DeviceLogin> {
    let discovery = discover(http, base_url).await?;
    let endpoint = discovery
        .device_authorization_endpoint
        .ok_or_else(|| anyhow!("{base_url} does not offer device authorization"))?;
    let (status, value) = post_form(http, &endpoint, &[("client_id", client_id), ("scope", scope)]).await?;
    if !status.is_success() {
        bail!("Failed with message: {}", oauth_error(&value));
    }
    let authorization = serde_json::from_value(value).context("unexpected device authorization response")?;
    Ok(DeviceLogin { token_endpoint: discovery.token_endpoint, client_id: client_id.to_string(), authorization })
}

impl DeviceLogin {
    /// Polls the token endpoint until the user approves, declines, or the code expires.
    pub async fn wait(self, http: &reqwest::Client) -> Result<Tokens> {
        let mut interval = Duration::from_secs(self.authorization.interval.unwrap_or(5).max(1));
        let deadline = std::time::Instant::now() + Duration::from_secs(self.authorization.expires_in.unwrap_or(900));
        loop {
            tokio::time::sleep(interval).await;
            if std::time::Instant::now() > deadline {
                bail!("The login code expired before it was approved. Run the login again.");
            }
            let fields = [
                ("grant_type", "urn:ietf:params:oauth:grant-type:device_code"),
                ("device_code", self.authorization.device_code.as_str()),
                ("client_id", self.client_id.as_str()),
            ];
            let (status, value) = post_form(http, &self.token_endpoint, &fields).await?;
            if status.is_success() {
                return serde_json::from_value(value).context("unexpected token response");
            }
            match value.get("error").and_then(Value::as_str) {
                Some("authorization_pending") => {}
                Some("slow_down") => interval += Duration::from_secs(5),
                _ => bail!("Failed with message: {}", oauth_error(&value)),
            }
        }
    }
}

pub async fn refresh(http: &reqwest::Client, base_url: &str, client_id: &str, refresh_token: &str) -> Result<Tokens> {
    let discovery = discover(http, base_url).await?;
    let fields = [("grant_type", "refresh_token"), ("refresh_token", refresh_token), ("client_id", client_id)];
    let (status, value) = post_form(http, &discovery.token_endpoint, &fields).await?;
    if !status.is_success() {
        bail!("{}", oauth_error(&value));
    }
    serde_json::from_value(value).context("unexpected token response")
}
