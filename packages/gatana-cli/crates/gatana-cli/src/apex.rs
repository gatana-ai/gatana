//! `gatana config login` without an organization: the sign-in goes through the OAuth server of the
//! base domain (https://gatana.ai), and the person chooses the organization in the browser. It is
//! the authorization code grant with PKCE and a loopback redirect (RFC 8252).
//!
//! The apex hands out codes and tokens as `acme~<token>`. The prefix names the organization; the
//! bare token is the organization's own and works on its host, so the CLI keeps the bare token and
//! from then on talks to `https://acme.gatana.ai` only, refreshes included. The device login cannot
//! go through the apex: a device code belongs to one organization from its first request.

use crate::oidc::{Tokens, oauth_error, post_form};
use anyhow::{Context, Result, anyhow, bail};
use base64::Engine as _;
use serde::Deserialize;
use serde_json::{Value, json};
use sha2::{Digest, Sha256};
use std::time::Duration;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpListener;

pub const DEFAULT_APEX_URL: &str = "https://gatana.ai";

/// Registered without a port: the apex takes a loopback redirect on any port (RFC 8252, 7.3), so
/// one registration serves every sign-in whatever port is free.
const REGISTERED_REDIRECT_URI: &str = "http://127.0.0.1/callback";
const CALLBACK_PATH: &str = "/callback";
const SCOPE: &str = "email profile offline_access";
const LOGIN_TIMEOUT: Duration = Duration::from_secs(10 * 60);
/// The apex writes this between the organization and the token.
const TOKEN_SEPARATOR: char = '~';

#[derive(Deserialize)]
struct Metadata {
    issuer: String,
    authorization_endpoint: String,
    token_endpoint: String,
    registration_endpoint: Option<String>,
}

/// What a sign-in through the apex found out: the organization, and the tokens for its host.
pub struct ApexLogin {
    pub org_id: String,
    pub base_url: String,
    pub client_id: String,
    pub tokens: Tokens,
}

pub async fn login(http: &reqwest::Client, apex_url: &str, browser: bool) -> Result<ApexLogin> {
    let apex = url::Url::parse(apex_url).with_context(|| format!("invalid URL {apex_url}"))?;
    let origin = apex.origin().ascii_serialization();
    let metadata = discover(http, &origin).await?;

    let listener = TcpListener::bind(("127.0.0.1", 0)).await.context("could not listen on a local port")?;
    let redirect_uri = format!("http://127.0.0.1:{}{CALLBACK_PATH}", listener.local_addr()?.port());
    let verifier = random_token();
    let challenge = base64::engine::general_purpose::URL_SAFE_NO_PAD.encode(Sha256::digest(verifier.as_bytes()));
    let state = random_token();

    let client_id = client_id(http, &origin, &metadata, &redirect_uri, &challenge, &state).await?;
    let authorize = authorize_url(&metadata, &client_id, &redirect_uri, &challenge, &state)?;
    crate::output::println(&format!("Please open {authorize} to sign in and choose your organization."));
    if browser {
        let _ = open::that_detached(authorize.as_str());
    }

    let code = tokio::time::timeout(LOGIN_TIMEOUT, wait_for_code(&listener, &state, &metadata.issuer))
        .await
        .map_err(|_| anyhow!("The sign-in did not finish in time. Run the login again."))??;

    let fields = [
        ("grant_type", "authorization_code"),
        ("code", code.as_str()),
        ("redirect_uri", redirect_uri.as_str()),
        ("client_id", client_id.as_str()),
        ("code_verifier", verifier.as_str()),
    ];
    let (status, value) = post_form(http, &metadata.token_endpoint, &fields).await?;
    if !status.is_success() {
        bail!("Failed with message: {}", oauth_error(&value));
    }
    let mut tokens: Tokens = serde_json::from_value(value).context("unexpected token response")?;
    let (org_id, access_token) =
        split_token(&tokens.access_token).ok_or_else(|| anyhow!("the access token names no organization"))?;
    tokens.access_token = access_token;
    if let Some(refresh) = tokens.refresh_token.take() {
        match split_token(&refresh) {
            Some((org, token)) if org == org_id => tokens.refresh_token = Some(token),
            _ => bail!("the refresh token does not name the organization of the access token"),
        }
    }
    let base_url = organization_url(&apex, &org_id)?;
    Ok(ApexLogin { org_id, base_url, client_id, tokens })
}

async fn discover(http: &reqwest::Client, origin: &str) -> Result<Metadata> {
    let url = format!("{origin}/.well-known/oauth-authorization-server");
    let hint = "Name the organization instead: gatana config login <org-id>";
    let response = http.get(&url).send().await.with_context(|| format!("could not reach {origin}"))?;
    if !response.status().is_success() {
        bail!("{origin} does not offer a sign-in without an organization ({}). {hint}", response.status());
    }
    response.json().await.with_context(|| format!("{url} returned an unexpected document. {hint}"))
}

/// The client this CLI registered at the apex before, when the apex still knows it; otherwise a new
/// registration. Kept in the config file so a person approves the CLI once per organization and not
/// at every sign-in. The apex forgets a registration that no sign-in has used for a long time; the
/// authorize endpoint then answers `invalid_client` instead of a redirect, which is what the check
/// looks for before the browser opens.
async fn client_id(
    http: &reqwest::Client,
    origin: &str,
    metadata: &Metadata,
    redirect_uri: &str,
    challenge: &str,
    state: &str,
) -> Result<String> {
    if let Some(known) = crate::config::apex_client(origin) {
        let probe = reqwest::Client::builder()
            .user_agent(concat!("gatana-cli/", env!("CARGO_PKG_VERSION")))
            .redirect(reqwest::redirect::Policy::none())
            .build()?;
        let url = authorize_url(metadata, &known, redirect_uri, challenge, state)?;
        let response = probe.get(url).send().await.with_context(|| format!("could not reach {origin}"))?;
        if response.status().is_redirection() {
            return Ok(known);
        }
        let status = response.status();
        let body: Value = response.json().await.unwrap_or(Value::Null);
        match body.get("error").and_then(Value::as_str) {
            Some("invalid_client" | "invalid_request") => {}
            _ => bail!("{origin} refused the sign-in ({status}): {}", oauth_error(&body)),
        }
    }
    let endpoint = metadata
        .registration_endpoint
        .as_deref()
        .ok_or_else(|| anyhow!("{origin} does not offer client registration"))?;
    let registration = json!({
        "client_name": "Gatana CLI",
        "redirect_uris": [REGISTERED_REDIRECT_URI],
        "grant_types": ["authorization_code", "refresh_token"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
        "software_id": "gatana-cli",
        "software_version": env!("CARGO_PKG_VERSION"),
    });
    let response = http.post(endpoint).json(&registration).send().await.context("client registration failed")?;
    let status = response.status();
    let body: Value = response.json().await.unwrap_or(Value::Null);
    let Some(id) = body.get("client_id").and_then(Value::as_str).filter(|_| status.is_success()) else {
        bail!("Client registration at {origin} failed: {}", oauth_error(&body));
    };
    crate::config::set_apex_client(origin, id)?;
    Ok(id.to_string())
}

fn authorize_url(
    metadata: &Metadata,
    client_id: &str,
    redirect_uri: &str,
    challenge: &str,
    state: &str,
) -> Result<url::Url> {
    let mut url = url::Url::parse(&metadata.authorization_endpoint).context("invalid authorization endpoint")?;
    url.query_pairs_mut()
        .append_pair("client_id", client_id)
        .append_pair("redirect_uri", redirect_uri)
        .append_pair("response_type", "code")
        .append_pair("scope", SCOPE)
        .append_pair("code_challenge", challenge)
        .append_pair("code_challenge_method", "S256")
        .append_pair("state", state);
    Ok(url)
}

/// Serves the loopback redirect until the browser arrives with the answer to this sign-in. Other
/// requests (a favicon, a stray connection, an answer with another state) are refused and the
/// wait goes on.
async fn wait_for_code(listener: &TcpListener, state: &str, issuer: &str) -> Result<String> {
    loop {
        let (mut stream, _) = listener.accept().await?;
        let Some(target) = read_request_target(&mut stream).await else {
            continue;
        };
        let answer = callback_answer(&target, state, issuer);
        let (status, page) = match &answer {
            Callback::Code(_) => ("200 OK", "Signed in to Gatana. You can close this tab and go back to the terminal."),
            Callback::Failed(_) => ("400 Bad Request", "The sign-in failed. The terminal says why."),
            Callback::Ignored => ("404 Not Found", "Not found."),
        };
        let html = format!(
            "<!doctype html><meta charset=\"utf-8\"><title>Gatana CLI</title>\
             <body style=\"font-family:system-ui,sans-serif;margin:4rem auto;max-width:32rem\"><p>{page}</p>"
        );
        let response = format!(
            "HTTP/1.1 {status}\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{html}",
            html.len()
        );
        let _ = stream.write_all(response.as_bytes()).await;
        let _ = stream.shutdown().await;
        match answer {
            Callback::Code(code) => return Ok(code),
            Callback::Failed(reason) => bail!("{reason}"),
            Callback::Ignored => {}
        }
    }
}

/// The request target of the request line (`/callback?code=...`), or None for anything that is
/// not a request.
async fn read_request_target(stream: &mut tokio::net::TcpStream) -> Option<String> {
    let mut buffer = Vec::new();
    let mut chunk = [0u8; 4096];
    while !buffer.windows(4).any(|window| window == b"\r\n\r\n") && buffer.len() < 16 * 1024 {
        let read = tokio::time::timeout(Duration::from_secs(10), stream.read(&mut chunk)).await.ok()?.ok()?;
        if read == 0 {
            break;
        }
        buffer.extend_from_slice(&chunk[..read]);
    }
    let head = String::from_utf8_lossy(&buffer);
    let mut parts = head.lines().next()?.split(' ');
    match (parts.next(), parts.next()) {
        (Some("GET"), Some(target)) => Some(target.to_string()),
        _ => None,
    }
}

#[derive(Debug, PartialEq)]
enum Callback {
    Code(String),
    Failed(String),
    Ignored,
}

fn callback_answer(target: &str, state: &str, issuer: &str) -> Callback {
    let Ok(url) = url::Url::parse(&format!("http://127.0.0.1{target}")) else {
        return Callback::Ignored;
    };
    if url.path() != CALLBACK_PATH {
        return Callback::Ignored;
    }
    let query: std::collections::HashMap<_, _> = url.query_pairs().into_owned().collect();
    if query.get("state").map(String::as_str) != Some(state) {
        return Callback::Ignored;
    }
    // RFC 9207: an answer that names another server is not the answer to this request.
    if query.get("iss").is_some_and(|iss| iss != issuer) {
        return Callback::Failed(format!("The answer came from {}, not from {issuer}.", query["iss"]));
    }
    if let Some(error) = query.get("error") {
        let description = query.get("error_description").map(|d| format!(": {d}")).unwrap_or_default();
        return Callback::Failed(format!("The sign-in was refused ({error}{description})"));
    }
    match query.get("code") {
        Some(code) if !code.is_empty() => Callback::Code(code.clone()),
        _ => Callback::Failed("The answer carried no code.".to_string()),
    }
}

/// `acme~<token>` as the organization and the bare token.
fn split_token(value: &str) -> Option<(String, String)> {
    let (org, token) = value.split_once(TOKEN_SEPARATOR)?;
    let slug = !org.is_empty() && org.bytes().all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'-');
    (slug && !token.is_empty()).then(|| (org.to_string(), token.to_string()))
}

/// The organization's host under the apex: `https://gatana.ai` and `acme` give `https://acme.gatana.ai`.
fn organization_url(apex: &url::Url, org_id: &str) -> Result<String> {
    let host = apex.host_str().ok_or_else(|| anyhow!("the URL has no host"))?;
    let mut url = apex.clone();
    url.set_host(Some(&format!("{org_id}.{host}")))?;
    Ok(url.origin().ascii_serialization())
}

/// 32 random bytes as base64url: a PKCE verifier (RFC 7636 asks for 43 to 128 characters) or a state.
fn random_token() -> String {
    let mut bytes = [0u8; 32];
    getrandom::fill(&mut bytes).expect("the operating system has no random source");
    base64::engine::general_purpose::URL_SAFE_NO_PAD.encode(bytes)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tokens_split_into_organization_and_bare_token() {
        assert_eq!(split_token("acme~abc~def"), Some(("acme".into(), "abc~def".into())));
        assert_eq!(split_token("abc"), None);
        assert_eq!(split_token("~abc"), None);
        assert_eq!(split_token("acme~"), None);
        assert_eq!(split_token("Acme~abc"), None);
    }

    #[test]
    fn the_organization_lives_under_the_apex_host() {
        let url = |s: &str| url::Url::parse(s).unwrap();
        assert_eq!(organization_url(&url("https://gatana.ai"), "acme").unwrap(), "https://acme.gatana.ai");
        assert_eq!(
            organization_url(&url("https://local.gatana.ai:8443/"), "acme").unwrap(),
            "https://acme.local.gatana.ai:8443"
        );
    }

    #[test]
    fn only_the_answer_to_this_request_counts() {
        let issuer = "https://gatana.ai";
        let answer = |target: &str| callback_answer(target, "s1", issuer);
        assert_eq!(
            answer("/callback?code=acme~c&state=s1&iss=https%3A%2F%2Fgatana.ai"),
            Callback::Code("acme~c".into())
        );
        assert_eq!(answer("/callback?code=acme~c&state=s1"), Callback::Code("acme~c".into()));
        assert_eq!(answer("/favicon.ico"), Callback::Ignored);
        assert_eq!(answer("/callback?code=acme~c&state=other"), Callback::Ignored);
        assert!(matches!(answer("/callback?code=c&state=s1&iss=https%3A%2F%2Fevil.example"), Callback::Failed(_)));
        assert!(matches!(answer("/callback?error=access_denied&state=s1"), Callback::Failed(_)));
        assert!(matches!(answer("/callback?state=s1"), Callback::Failed(_)));
    }
}
