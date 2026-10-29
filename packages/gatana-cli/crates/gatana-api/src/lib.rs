//! Typed client for the Gatana API.
//!
//! `v1` and `v2` are generated from the backend's OpenAPI documents by `gatana-codegen`; this file
//! is the hand-written part they call into. Every operation returns a [`Call`] that keeps the raw
//! JSON of the response next to its type: commands print what the server sent, field for field and
//! in its order, and read the fields they act on through the generated types, so a change in the
//! API breaks the build instead of a user's command.

// An error is built once per failed request; boxing its fields would only make matching on it clumsier.
#![allow(clippy::result_large_err)]

pub mod debug;
// Generated: formatted by the generator, so regenerating never leaves a diff.
#[rustfmt::skip]
pub mod v1;
#[rustfmt::skip]
pub mod v2;

use percent_encoding::{AsciiSet, NON_ALPHANUMERIC, utf8_percent_encode};
use reqwest::{Method, StatusCode};
use serde::Serialize;
use serde::de::DeserializeOwned;
use serde_json::Value;
use std::marker::PhantomData;
use url::Url;

/// An authenticated connection to one Gatana organization.
#[derive(Clone)]
pub struct Client {
    http: reqwest::Client,
    base_url: Url,
    token: String,
}

impl Client {
    /// `base_url` is the organization's origin, e.g. `https://acme.gatana.ai`; any path on it is
    /// ignored, as the operation paths are absolute.
    pub fn new(http: reqwest::Client, base_url: &str, token: impl Into<String>) -> Result<Self, Error> {
        let base_url = Url::parse(base_url).map_err(|source| Error::Url { url: base_url.to_string(), source })?;
        Ok(Self { http, base_url, token: token.into() })
    }

    pub fn base_url(&self) -> &Url {
        &self.base_url
    }

    pub fn token(&self) -> &str {
        &self.token
    }

    pub fn v1(&self) -> v1::Api<'_> {
        v1::Api::new(self)
    }

    pub fn v2(&self) -> v2::Api<'_> {
        v2::Api::new(self)
    }

    /// The absolute URL of a path on this organization.
    pub fn url(&self, path: &str) -> Result<Url, Error> {
        self.base_url.join(path).map_err(|source| Error::Url { url: path.to_string(), source })
    }

    /// An authorized request for the few endpoints the generated client does not cover: uploads,
    /// downloads and event streams.
    pub fn request(&self, method: Method, url: Url) -> reqwest::RequestBuilder {
        self.http.request(method, url).bearer_auth(&self.token)
    }
}

/// encodeURIComponent: what the TypeScript SDK used for path parameters.
const PATH_SEGMENT: &AsciiSet = &NON_ALPHANUMERIC
    .remove(b'-')
    .remove(b'_')
    .remove(b'.')
    .remove(b'!')
    .remove(b'~')
    .remove(b'*')
    .remove(b'\'')
    .remove(b'(')
    .remove(b')');

#[doc(hidden)]
pub fn encode_path_segment(value: &str) -> String {
    utf8_percent_encode(value, PATH_SEGMENT).to_string()
}

/// One request to an operation, typed with what a successful response holds.
#[must_use = "a call does nothing until it is sent"]
pub struct Call<'a, T> {
    client: &'a Client,
    method: Method,
    path: String,
    query: Vec<(String, String)>,
    headers: Vec<(String, String)>,
    body: Option<Result<Value, serde_json::Error>>,
    response: PhantomData<fn() -> T>,
}

impl<'a, T> Call<'a, T> {
    #[doc(hidden)]
    pub fn new(client: &'a Client, method: Method, path: String) -> Self {
        Self { client, method, path, query: Vec::new(), headers: Vec::new(), body: None, response: PhantomData }
    }

    pub fn query(mut self, name: &str, value: impl AsRef<str>) -> Self {
        self.query.push((name.to_string(), value.as_ref().to_string()));
        self
    }

    pub fn header(mut self, name: &str, value: &str) -> Self {
        self.headers.push((name.to_string(), value.to_string()));
        self
    }

    pub fn json<B: Serialize + ?Sized>(mut self, body: &B) -> Self {
        self.body = Some(serde_json::to_value(body));
        self
    }

    pub fn json_value(mut self, body: Value) -> Self {
        self.body = Some(Ok(body));
        self
    }

    /// Sends the request. Any status outside 2xx is an [`Error::Status`].
    pub async fn send(self) -> Result<Response<T>, Error> {
        let mut url = self.client.url(&self.path)?;
        if !self.query.is_empty() {
            url.query_pairs_mut().extend_pairs(&self.query);
        }
        let mut request = self.client.request(self.method.clone(), url.clone());
        for (name, value) in &self.headers {
            request = request.header(name, value);
        }
        if let Some(body) = self.body {
            let body = body.map_err(Error::Encode)?;
            crate::debug!("gatana:http", "→ {} {} {}", self.method, url, body);
            request = request.json(&body);
        } else {
            crate::debug!("gatana:http", "→ {} {}", self.method, url);
        }
        let response = request.send().await.map_err(Error::Transport)?;
        let status = response.status();
        crate::debug!("gatana:http", "← {} {} {}", status, self.method, url);
        let bytes = response.bytes().await.map_err(Error::Transport)?;
        let value = if bytes.is_empty() {
            Value::Null
        } else {
            serde_json::from_slice(&bytes)
                .unwrap_or_else(|_| Value::String(String::from_utf8_lossy(&bytes).into_owned()))
        };
        if !status.is_success() {
            return Err(Error::Status {
                message: message_of(&value, status, &url),
                status,
                method: self.method,
                url,
                body: value,
            });
        }
        Ok(Response { status, value, path: self.path, response: PhantomData })
    }
}

impl<T: DeserializeOwned> Call<'_, T> {
    /// The response as the server sent it.
    pub async fn value(self) -> Result<Value, Error> {
        Ok(self.send().await?.value)
    }

    /// The response read into its generated type.
    pub async fn typed(self) -> Result<T, Error> {
        self.send().await?.typed()
    }
}

/// A successful response: the JSON as sent, readable as `T` on demand.
pub struct Response<T> {
    pub status: StatusCode,
    pub value: Value,
    path: String,
    response: PhantomData<fn() -> T>,
}

impl<T: DeserializeOwned> Response<T> {
    pub fn typed(&self) -> Result<T, Error> {
        T::deserialize(&self.value).map_err(|source| Error::Decode { path: self.path.clone(), source })
    }
}

/// The backend answers errors as `{ message }`; older routes use `detail` or `error`. A body without
/// any of them is shown whole, after the status.
///
/// A 502, 503 or 504 without such a message comes from a proxy in front of Gatana, or from a
/// backend that is still starting. Its body is often an HTML page, so the message names the
/// address instead.
fn message_of(body: &Value, status: StatusCode, url: &Url) -> String {
    let text = ["message", "detail", "error"]
        .iter()
        .filter_map(|key| body.get(*key).and_then(Value::as_str))
        .find(|text| !text.is_empty());
    if let Some(text) = text {
        return text.to_string();
    }
    let reason = format!("{} {}", status.as_u16(), status.canonical_reason().unwrap_or(""));
    let reason = reason.trim_end();
    let origin = url.origin().ascii_serialization();
    if status == StatusCode::SERVICE_UNAVAILABLE && body.get("status").and_then(Value::as_str) == Some("starting") {
        return format!("Gatana at {origin} is starting ({reason}). Try again in a moment.");
    }
    if matches!(status, StatusCode::BAD_GATEWAY | StatusCode::SERVICE_UNAVAILABLE | StatusCode::GATEWAY_TIMEOUT) {
        return format!("Gatana at {origin} did not answer ({reason}).");
    }
    match body {
        Value::Null => reason.to_string(),
        Value::String(text) if !text.trim().is_empty() => text.trim().to_string(),
        Value::String(_) => reason.to_string(),
        other => format!("{reason}: {other}"),
    }
}

#[derive(Debug, thiserror::Error)]
pub enum Error {
    /// The server answered with a status outside 2xx.
    #[error("{message}")]
    Status { status: StatusCode, method: Method, url: Url, message: String, body: Value },
    /// The request did not get a response.
    #[error("{}", error_chain(.0))]
    Transport(#[source] reqwest::Error),
    /// The response does not have the shape the generated type expects.
    #[error("unexpected response from {path}: {source}")]
    Decode { path: String, source: serde_json::Error },
    #[error("could not encode the request body: {0}")]
    Encode(serde_json::Error),
    #[error("invalid URL {url}: {source}")]
    Url { url: String, source: url::ParseError },
}

impl Error {
    pub fn status(&self) -> Option<StatusCode> {
        match self {
            Error::Status { status, .. } => Some(*status),
            _ => None,
        }
    }
}

/// reqwest's own message hides the cause ("error sending request for url"); the chain names it
/// ("dns error: failed to lookup address information").
fn error_chain(error: &dyn std::error::Error) -> String {
    let mut text = error.to_string();
    let mut source = error.source();
    while let Some(cause) = source {
        let cause_text = cause.to_string();
        if !text.contains(&cause_text) {
            text.push_str(": ");
            text.push_str(&cause_text);
        }
        source = cause.source();
    }
    text
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn path_segments_are_encoded_like_encode_uri_component() {
        assert_eq!(encode_path_segment("my server/x?y"), "my%20server%2Fx%3Fy");
        assert_eq!(encode_path_segment("a-b_c.d!e~f*g'h(i)"), "a-b_c.d!e~f*g'h(i)");
        assert_eq!(encode_path_segment("åäö"), "%C3%A5%C3%A4%C3%B6");
    }

    #[test]
    fn error_messages_prefer_the_body() {
        let status = StatusCode::BAD_REQUEST;
        let url = Url::parse("https://acme.gatana.ai/api/v1/tools?schemas=false").unwrap();
        let message = |body: &Value, status| message_of(body, status, &url);
        assert_eq!(message(&serde_json::json!({"message": "Skill not found"}), status), "Skill not found");
        assert_eq!(message(&serde_json::json!({"error": "nope"}), status), "nope");
        assert_eq!(message(&Value::String("plain text".into()), status), "plain text");
        assert_eq!(message(&Value::Null, StatusCode::NOT_FOUND), "404 Not Found");
        assert_eq!(message(&serde_json::json!({"code": 1}), status), r#"400 Bad Request: {"code":1}"#);
    }

    #[test]
    fn gateway_errors_name_the_address() {
        let url = Url::parse("https://acme.gatana.ai/api/v1/tools?schemas=false").unwrap();
        assert_eq!(
            message_of(&Value::Null, StatusCode::BAD_GATEWAY, &url),
            "Gatana at https://acme.gatana.ai did not answer (502 Bad Gateway)."
        );
        let html = Value::String("<html><body>504 Gateway Time-out</body></html>".into());
        assert_eq!(
            message_of(&html, StatusCode::GATEWAY_TIMEOUT, &url),
            "Gatana at https://acme.gatana.ai did not answer (504 Gateway Timeout)."
        );
        assert_eq!(
            message_of(&serde_json::json!({"status": "starting"}), StatusCode::SERVICE_UNAVAILABLE, &url),
            "Gatana at https://acme.gatana.ai is starting (503 Service Unavailable). Try again in a moment."
        );
        // A message from Gatana itself still wins.
        let body = serde_json::json!({"message": "Upstream server failed"});
        assert_eq!(message_of(&body, StatusCode::BAD_GATEWAY, &url), "Upstream server failed");
    }
}
