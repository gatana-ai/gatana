//! Follows a deployment over the server's event stream until the server is ready, crashed, or the
//! time is up, printing the state of each container as it changes.

use crate::output::{self, Format, Options};
use crate::sse::EventStream;
use anyhow::Result;
use gatana_api::v1::types::DeploymentLogPayload;
use serde_json::{Map, Value};
use std::collections::HashMap;
use std::time::Duration;

#[derive(Debug, Clone, Default)]
pub struct DeploymentResult {
    pub deployed: bool,
    pub stabilized: bool,
    pub pod_name: Option<String>,
}

#[derive(Clone, Copy, PartialEq)]
enum ContainerKind {
    Init,
    Main,
}

struct State {
    pod: Option<String>,
    /// Init containers then main containers, in the order the pod lists them.
    order: Vec<String>,
    containers: HashMap<String, (ContainerKind, &'static str)>,
    errors: Vec<String>,
    is_ready: bool,
    has_crashed: bool,
    last: Option<Map<String, Value>>,
}

impl State {
    fn result(&self, deployed: bool, stabilized: bool) -> DeploymentResult {
        DeploymentResult { deployed, stabilized, pod_name: self.pod.clone() }
    }

    fn set_main(&mut self, status: &'static str) {
        for (kind, current) in self.containers.values_mut() {
            if *kind == ContainerKind::Main {
                *current = status;
            }
        }
    }

    /// One table row per change: the deployment, then each container's status.
    fn print(&mut self) {
        let mut row = Map::new();
        if let Some(pod) = &self.pod {
            row.insert("deploymentId".into(), Value::String(pod.clone()));
            for name in &self.order {
                let status = self.containers.get(name).map(|(_, status)| *status).unwrap_or("pending");
                row.insert(name.clone(), Value::String(status.to_string()));
            }
        }
        if !self.errors.is_empty() {
            row.insert("errors".into(), Value::String(self.errors.join(", ")));
        }
        if self.last.as_ref() == Some(&row) {
            return;
        }
        let first = self.last.is_none();
        output::output(
            &Value::Array(vec![Value::Object(row.clone())]),
            Options { no_headers: !first, default_format: Some(Format::Table), ..Options::default() },
        );
        self.last = Some(row);
    }

    /// Applies one event. Some(result) when the deployment has settled.
    fn apply(&mut self, payload: DeploymentLogPayload) -> Option<DeploymentResult> {
        match payload {
            DeploymentLogPayload::Done => {
                self.print();
                return Some(self.result(true, !self.has_crashed));
            }
            DeploymentLogPayload::PodInfo { pod, init_containers, containers, .. } => {
                self.pod = Some(pod);
                self.order = init_containers.iter().chain(&containers).cloned().collect();
                for name in init_containers {
                    self.containers.insert(name, (ContainerKind::Init, "pending"));
                }
                for name in containers {
                    self.containers.insert(name, (ContainerKind::Main, "pending"));
                }
            }
            DeploymentLogPayload::InitContainerRunning { name } => {
                if let Some(entry) = self.containers.get_mut(&name) {
                    entry.1 = "running";
                }
            }
            DeploymentLogPayload::InitContainerTerminated { name, exit_code, .. } => {
                if let Some(entry) = self.containers.get_mut(&name) {
                    entry.1 = if exit_code == 0.0 { "completed" } else { "failed" };
                }
            }
            DeploymentLogPayload::MainContainerRunning => self.set_main("running"),
            DeploymentLogPayload::MainContainerReady => {
                self.set_main("ready");
                self.is_ready = true;
            }
            DeploymentLogPayload::MainContainerCrashed { .. } => {
                self.set_main("failed");
                self.has_crashed = true;
            }
            DeploymentLogPayload::MainContainerCrashBackOff { .. } => self.set_main("crashBackOff"),
            DeploymentLogPayload::MainContainerImagePullBackOff { reason, detail, .. } => {
                // Final: the backend sends `done` right after it, and the container never starts.
                self.set_main("imagePullBackOff");
                self.errors.push(match detail.filter(|detail| !detail.is_empty()) {
                    Some(detail) => format!("{reason}: {detail}"),
                    None => reason,
                });
                self.has_crashed = true;
            }
            DeploymentLogPayload::Error { message } => self.errors.push(message),
            _ => {}
        }
        self.print();
        if self.is_ready {
            return Some(self.result(true, true));
        }
        if self.has_crashed {
            return Some(self.result(true, false));
        }
        None
    }
}

pub async fn wait_for_deployment_done(
    api: &gatana_api::Client,
    server_slug: &str,
    timeout: Duration,
) -> Result<DeploymentResult> {
    let mut state = State {
        pod: None,
        order: Vec::new(),
        containers: HashMap::new(),
        errors: Vec::new(),
        is_ready: false,
        has_crashed: false,
        last: None,
    };
    let follow = async {
        let mut url = api.url("/api/v1/deployments/deployment-logs")?;
        url.query_pairs_mut().append_pair("serverSlug", server_slug);
        let response = match api
            .request(reqwest::Method::GET, url)
            .header(reqwest::header::ACCEPT, "text/event-stream")
            .send()
            .await
            .and_then(reqwest::Response::error_for_status)
        {
            Ok(response) => response,
            Err(error) => return Ok(connection_error(&mut state, error.to_string())),
        };
        let mut events = EventStream::new(response);
        while let Some(event) = events.next().await {
            let event = match event {
                Ok(event) => event,
                Err(error) => return Ok(connection_error(&mut state, error.to_string())),
            };
            if event.event != "DeploymentLogPayload" {
                continue;
            }
            let Ok(value) = serde_json::from_str::<Value>(&event.data) else {
                output::eprintln(&format!("Error parsing deployment log: {}", event.data));
                state.errors.push("Failed to parse deployment log".into());
                state.print();
                return Ok(state.result(false, false));
            };
            // An event type this version does not know yet changes nothing.
            if let Ok(payload) = serde_json::from_value::<DeploymentLogPayload>(value)
                && let Some(result) = state.apply(payload)
            {
                return Ok(result);
            }
        }
        Ok(connection_error(&mut state, "the server closed the stream".into()))
    };
    match tokio::time::timeout(timeout, follow).await {
        Ok(result) => result,
        Err(_) => Ok(DeploymentResult { deployed: false, stabilized: false, pod_name: state_pod(&state) }),
    }
}

fn state_pod(state: &State) -> Option<String> {
    state.pod.clone()
}

fn connection_error(state: &mut State, message: String) -> DeploymentResult {
    state.errors.push(format!("Connection error occurred: {message}"));
    state.print();
    output::eprintln(&format!("EventSource error: {message}"));
    state.result(false, false)
}

/// The logs of the container before its last restart, for a deployment that crashed. The previous
/// container's logs can take a moment to appear, so this asks again for a few seconds.
pub async fn fetch_crash_logs(api: &gatana_api::Client, pod_name: &str) -> Option<(String, String)> {
    let query = gatana_api::v1::query::ListDeploymentsLogs { previous: Some("true".into()), ..Default::default() };
    for attempt in 0..=50 {
        tokio::time::sleep(Duration::from_millis(200)).await;
        match api.v1().list_deployments_logs(pod_name, &query).typed().await {
            Ok(response) => {
                let logs = response.logs;
                if logs.stdout.is_empty() && attempt < 50 {
                    tokio::time::sleep(Duration::from_millis(200)).await;
                    continue;
                }
                return Some((logs.stdout, logs.stderr));
            }
            Err(error) => {
                output::eprintln(&format!("Error fetching crash logs: {error}"));
                return None;
            }
        }
    }
    None
}
