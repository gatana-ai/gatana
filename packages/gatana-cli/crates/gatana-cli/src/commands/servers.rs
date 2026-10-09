//! Tool calls, deployments, effective credentials, FaaS servers and sandboxes.

use super::resources::split_tool_name;
use super::{Silent, text_at};
use crate::cli::{CredsArgs, DeploymentCommand, FaasCommand, SandboxCommand, ToolArgs, ToolPart};
use crate::context::Context;
use crate::faas::{self, deployment};
use crate::output::{self, Options};
use crate::sse::EventStream;
use crate::util::{from_age, parse_inline_object, read_piped_stdin};
use anyhow::{Context as _, Result, anyhow, bail};
use gatana_api::{v1, v2};
use serde_json::{Map, Value, json};
use std::path::Path;
use std::time::Duration;

/// The arguments: `-f` file, else piped stdin, then `-a` on top.
fn tool_arguments(args: &ToolArgs) -> Result<Map<String, Value>> {
    let base = match &args.file {
        Some(file) => Some(std::fs::read_to_string(file).with_context(|| format!("reading {}", file.display()))?),
        None if args.arg.is_empty() => read_piped_stdin()?.filter(|text| !text.trim().is_empty()),
        None => None,
    };
    let mut arguments = match base {
        Some(text) => match serde_json::from_str(text.trim()).context("the arguments are not valid JSON")? {
            Value::Object(map) => map,
            _ => bail!("The arguments must be a JSON object"),
        },
        None => Map::new(),
    };
    if !args.arg.is_empty()
        && let Value::Object(inline) = parse_inline_object(&args.arg)?
    {
        arguments.extend(inline);
    }
    Ok(arguments)
}

/// `gatana tool <server>_<tool>`: calls the tool through Gatana and prints the part asked for.
pub async fn call_tool(context: &Context, args: ToolArgs) -> Result<()> {
    let (server, tool) = split_tool_name(&args.tool_name)?;
    let arguments = tool_arguments(&args)?;
    let api = context.api().await?;
    let body = v1::types::CallMcpServerToolBody { args: arguments };
    let response = api.v1().call_mcp_server_tool(server, tool, &body).value().await?;
    // The result is read raw: MCP keeps adding content types, and printing one must not need a
    // new CLI.
    let Some(result) = response.get("result").filter(|result| !result.is_null()) else {
        bail!("Gatana returned success but no result was returned! Please contact Gatana support.");
    };
    if result.get("isError") == Some(&Value::Bool(true)) {
        output::error(&result.to_string());
        if text_at(result, "/errorCode") == Some("auth-required") {
            let config = api.v2().get_server_v2(server).value().await.unwrap_or_default();
            if text_at(&config, "/authorization/method") == Some("oauth") {
                output::error(&format!(
                    "The server is missing credentials. Run \"gatana create creds {server}\" to generate an authorization URL."
                ));
            } else {
                output::error(&format!(
                    "The server is missing credentials. Run \"gatana create creds {server}\" to set API key credentials."
                ));
            }
        }
        return Err(Silent.into());
    }
    match args.part {
        ToolPart::Text => {
            let text = result
                .get("content")
                .and_then(Value::as_array)
                .and_then(|content| content.iter().find(|item| text_at(item, "/type") == Some("text")))
                .and_then(|item| item.get("text"))
                .and_then(Value::as_str)
                .filter(|text| !text.is_empty());
            match text {
                Some(text) => output::print(&Value::String(text.to_string())),
                None => bail!("no text content found in tool response"),
            }
        }
        ToolPart::Structured => {
            let structured =
                result.get("structuredContent").filter(|value| !value.is_null()).cloned().unwrap_or(json!({}));
            output::output(&structured, Options::yaml());
        }
        ToolPart::Unstructured => output::output(result.get("content").unwrap_or(&Value::Null), Options::yaml()),
    }
    Ok(())
}

/// `gatana creds <server>`: the token or API keys a tool call would use.
pub async fn effective_credentials(context: &Context, args: CredsArgs) -> Result<()> {
    let query = v1::query::GetMcpServerCredentialsToken { credentials_id: args.cred_id };
    let token = context.api().await?.v1().get_mcp_server_credentials_token(&args.server_slug, &query).typed().await?;
    let shown = match token.access_token.filter(|token| !token.is_empty()) {
        Some(token) => Value::String(token),
        None => Value::Object(token.apikeys.into_iter().map(|(name, value)| (name, Value::String(value))).collect()),
    };
    output::output(&shown, Options::yaml());
    Ok(())
}

async fn deployment_names(api: &gatana_api::Client, slug: &str) -> Result<Vec<String>> {
    let query = v1::query::GetDeploymentsStatus { server_slug: Some(slug.to_string()), ..Default::default() };
    let status = api.v1().get_deployments_status(&query).typed().await?;
    Ok(status.deployments.into_iter().map(|deployment| deployment.name).collect())
}

async fn print_crash_logs(api: &gatana_api::Client, pod: &str) {
    if let Some((stdout, stderr)) = deployment::fetch_crash_logs(api, pod).await {
        if !stdout.is_empty() {
            output::print(&Value::String(stdout));
        }
        if !stderr.is_empty() {
            output::print(&Value::String(stderr));
        }
    }
}

pub async fn deployment(context: &Context, command: DeploymentCommand) -> Result<()> {
    let api = context.api().await?;
    match command {
        DeploymentCommand::Get { name } => {
            let query = v1::query::GetDeploymentsStatus { server_slug: Some(name), ..Default::default() };
            let status = api.v1().get_deployments_status(&query).value().await?;
            output::print(&status);
        }
        DeploymentCommand::Logs { name, follow, previous, id } => {
            let names = deployment_names(api, &name).await?;
            let pod = match &id {
                Some(id) => names.iter().find(|name| *name == id).cloned(),
                None => names.first().cloned(),
            };
            let Some(pod) = pod else {
                output::info("No deployments found.");
                return Ok(());
            };
            if follow {
                follow_logs(api, &pod, previous).await?;
            } else {
                let query =
                    v1::query::ListDeploymentsLogs { previous: Some(previous.to_string()), ..Default::default() };
                let logs =
                    api.v1().list_deployments_logs(&pod, &query).header("accept", "application/json").typed().await?;
                // stderr is included in stdout by the backend.
                output::println(&logs.logs.stdout);
            }
        }
        DeploymentCommand::Wait { name, timeout } => {
            let timeout = from_age(&timeout).unwrap_or(10 * 60 * 1000);
            let result = deployment::wait_for_deployment_done(api, &name, Duration::from_millis(timeout)).await?;
            if !result.stabilized {
                return Err(Silent.into());
            }
        }
        DeploymentCommand::Stop { name } => {
            api.v1().stop_mcp_server(&name).send().await?;
            output::success(&format!("Server '{name}' stopped."));
        }
        DeploymentCommand::Start { name, wait } => {
            let started = api.v1().start_mcp_server(&name).typed().await?;
            if !started.success {
                bail!("Failed to start server: {}", started.detail.unwrap_or_else(|| "unknown reason".into()));
            }
            if !wait {
                output::success(&format!("Server '{name}' started."));
                return Ok(());
            }
            let result = deployment::wait_for_deployment_done(api, &name, Duration::from_secs(600)).await?;
            output::print(&json!({ "deployed": result.deployed, "stabilized": result.stabilized }));
            if !result.stabilized {
                if let Some(pod) = &result.pod_name {
                    print_crash_logs(api, pod).await;
                }
                return Err(Silent.into());
            }
            output::success(&format!("Server '{name}' started and stabilized."));
        }
    }
    Ok(())
}

/// Prints log lines as the server sends them, until it closes the stream.
async fn follow_logs(api: &gatana_api::Client, pod: &str, previous: bool) -> Result<()> {
    let mut url = api.url("/api/v1/deployments/logs")?;
    url.query_pairs_mut().append_pair("podName", pod).append_pair("previous", if previous { "true" } else { "false" });
    let response = api
        .request(reqwest::Method::GET, url)
        .header(reqwest::header::ACCEPT, "text/event-stream")
        .send()
        .await?
        .error_for_status()?;
    let mut events = EventStream::new(response);
    while let Some(event) = events.next().await {
        let event = event?;
        if event.event == "stdout" || event.event == "stderr" {
            let line: Value = serde_json::from_str(&event.data).unwrap_or_default();
            output::println(text_at(&line, "/line").unwrap_or_default());
        }
    }
    Ok(())
}

pub async fn faas(context: &Context, command: FaasCommand) -> Result<()> {
    match command {
        FaasCommand::Init { path } => faas::init(&path),
        FaasCommand::Verify { path } => faas::print_verification(&path).await,
        FaasCommand::Run { path, tool_name, input, file, param } => {
            let input = faas::tool_input(input.as_deref(), file.as_deref(), &param)?;
            faas::run_tool(&path, &tool_name, &input).await
        }
        FaasCommand::Upload { name, path, create, no_logs, no_wait, force } => {
            upload(context, &name, &path, UploadOptions { create, no_logs, no_wait, force }).await
        }
        FaasCommand::Download { name, out_file } => {
            faas::download(context.api().await?, &name, out_file.as_deref()).await
        }
    }
}

struct UploadOptions {
    create: bool,
    no_logs: bool,
    no_wait: bool,
    force: bool,
}

/// Verifies, zips and uploads the source code, starts the server, waits until it is ready and
/// refreshes its tools.
async fn upload(context: &Context, slug: &str, path: &Path, options: UploadOptions) -> Result<()> {
    output::info("Verifying deployment package...");
    match faas::verify(path).await {
        Ok(result) => {
            for tool in result.get("tools").and_then(Value::as_array).into_iter().flatten() {
                if tool.get("valid") != Some(&Value::Bool(true)) {
                    let issues: Vec<&str> = tool
                        .get("issues")
                        .and_then(Value::as_array)
                        .into_iter()
                        .flatten()
                        .filter_map(Value::as_str)
                        .collect();
                    output::info(&format!("Warning: {}: {}", text_at(tool, "/name").unwrap_or("?"), issues.join(", ")));
                }
            }
        }
        Err(error) if faas::runner::is_node_missing(&error) && faas::check_index_js(path)?.has_schema => {
            output::info("Node.js not found: index.js was checked for a schema export only.");
        }
        Err(error) if options.force => {
            output::info(&format!("Source code verification failed, but proceeding due to --force flag: {error}"));
        }
        Err(error) => bail!("{error}\nSource code verification failed. Use --force to proceed with deployment anyway."),
    }

    output::info("Creating deployment package...");
    let archive = faas::create_zip(path)?;

    let api = context.api().await?;
    let servers = api.v2().list_servers_v2().value().await?;
    let exists = servers
        .get("servers")
        .and_then(Value::as_array)
        .is_some_and(|servers| servers.iter().any(|server| text_at(server, "/slug") == Some(slug)));
    if !exists {
        if !options.create {
            bail!("Server '{slug}' not found. Use --create to create a new server if it does not exist.");
        }
        output::info(&format!("Server '{slug}' not found. Creating new server..."));
        api.v2().create_server_v2(&new_faas_server(slug)).send().await?;
    }

    output::info("Deploying...");
    faas::upload(api, slug, archive.path()).await?;
    api.v1().start_mcp_server(slug).send().await?;
    if options.no_wait {
        output::success(&format!(
            "Deployment started. You can use \"gatana deploy wait {slug}\" to wait for deployment to finish."
        ));
        return Ok(());
    }
    let result = deployment::wait_for_deployment_done(api, slug, Duration::from_secs(600)).await?;
    if !result.stabilized {
        if let (false, Some(pod)) = (options.no_logs, &result.pod_name) {
            print_crash_logs(api, pod).await;
        }
        bail!("Deployment of '{slug}' did not become ready.");
    }
    // The tools may not answer the moment the deployment reports ready.
    tokio::time::sleep(Duration::from_millis(250)).await;
    let refresh = v1::query::RefreshTools { server_slug: Some(slug.to_string()) };
    api.v1().refresh_tools(&refresh).header("accept", "text/event-stream").send().await?;
    let tools = api.v1().list_mcp_server_tools(slug, &v1::query::ListMcpServerTools::default()).typed().await?.tools;
    let rows: Vec<Value> = tools.iter().map(|tool| json!({ "tool": tool.tool_name })).collect();
    output::print(&Value::Array(rows));
    output::success(&format!("\nDeployment successful. {} tool(s) available on server '{slug}'.", tools.len()));
    Ok(())
}

/// A FaaS server on the Node 24 runtime, everything else at the server's defaults.
fn new_faas_server(slug: &str) -> v2::types::V2CreateServerRequest {
    use v2::types::{
        V2CreateServerRequest, V2CreateServerRequestTransportConfig, V2CreateServerRequestTransportConfigRuntime,
    };
    V2CreateServerRequest {
        slug: slug.to_string(),
        transport_config: Some(V2CreateServerRequestTransportConfig::Hosted {
            env: Vec::new(),
            limits: None,
            requests: None,
            runtime: V2CreateServerRequestTransportConfigRuntime::Node24,
            storage: None,
            tailscale: None,
        }),
        authorization: None,
        created_at: None,
        description: None,
        firewall_rules: Vec::new(),
        id: None,
        is_enabled: None,
        is_output_compression_enabled: None,
        is_output_compression_transform_enabled: None,
        last_tool_refresh_at: None,
        mcp_protocol_detected_at: None,
        mcp_protocol_version: None,
        oauth_client_configuration: None,
        oauth_metadata: None,
        output_compression_threshold_bytes: None,
        reset_timeout_on_progress_notification: None,
        tenant_id: None,
        timeout_protocol: None,
        timeout_total: None,
        transport_config_type: None,
        updated_at: None,
        visibility: None,
    }
}

pub async fn sandbox(context: &Context, command: SandboxCommand) -> Result<()> {
    let SandboxCommand::Shell { id } = command;
    let session = context.api().await?.v1().create_sandbox_ssh_session(&id).typed().await?;
    let port = session.port as u16;
    output::info(&format!("Connecting to sandbox {id} via SSH ({}:{port})...", session.host));
    let status = std::process::Command::new("ssh")
        .args(["-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-p", &port.to_string()])
        .arg(format!("{}@{}", session.token, session.host))
        .status()
        .map_err(|error| anyhow!("Failed to spawn ssh: {error}"))?;
    std::process::exit(status.code().unwrap_or(1));
}
