//! `gatana create server`: create an MCP server, as the Add Server page of the dashboard does
//! (AddServerPage.tsx and new-server-form.tsx in the frontend).
//!
//! The questions follow the page. For a remote or an OpenAPI specification: the URL, then the slug,
//! made from the domain. For a command: the command, then the slug, made from the package. For
//! code: the slug and the runtime. For a built-in server: which one. Each answer can also come from
//! an argument. Without a terminal, a missing answer is an error, unless a default can stand in.
//!
//! For a URL, Gatana looks for the OAuth of the remote while the slug question is on screen. After
//! the server is created, the CLI registers an OAuth client when the authorization server permits
//! it, and saves both on the server, as the popular-server tiles do (server-oauth-setup.ts in the
//! frontend).

use super::text_at;
use crate::cli::{
    BuiltIn, BuiltInServerArgs, CodeServerArgs, LocalServerArgs, NewServerArgs, RemoteServerArgs, Runtime, ServerKind,
    Visibility,
};
use crate::context::Context;
use crate::output;
use anyhow::{Context as _, Result, anyhow, bail};
use clap::ValueEnum;
use gatana_api::v2::types::{V2CreateServerRequest, V2CreateServerRequestTransportConfig as TransportConfig};
use gatana_api::{v1, v2};
use serde_json::{Value, json};
use std::collections::HashSet;
use std::future::Future;
use std::io::IsTerminal;
use std::time::Duration;

/// What the backend accepts (CreateServerRequest in the backend).
const MAX_SLUG_LENGTH: usize = 20;
/// The slug that code starts with, as on the dashboard.
const CODE_DEFAULT_SLUG: &str = "my-new-app";
/// The discovery tries many well-known addresses, with a long timeout for each. A remote that does
/// not answer must not stop the server from being created.
const DISCOVERY_TIMEOUT: Duration = Duration::from_secs(30);
/// Labels that have no meaning alone, so the label before them is the name (slugFromUrl in the
/// frontend).
const PUBLIC_SUFFIX_LABELS: [&str; 7] = ["co", "com", "net", "org", "gov", "edu", "ac"];

pub async fn run(context: &Context, kind: Option<ServerKind>) -> Result<()> {
    let kind = match kind {
        Some(kind) => kind,
        None => choose_kind()?,
    };
    let api = context.api().await?;
    // First, so that a failed sign-in stops the command before the first question.
    let list = api.v2().list_servers_v2().value().await?;
    let servers = list.get("servers").and_then(Value::as_array).cloned().unwrap_or_default();
    let new = NewServer { api, base_url: context.config()?.base_url.trim_end_matches('/'), servers: &servers };
    match kind {
        ServerKind::Remote(RemoteServerArgs { url, sse, server }) => {
            new.with_url(if sse { UrlKind::Sse } else { UrlKind::Streaming }, url, server).await
        }
        ServerKind::Openapi(args) => new.with_url(UrlKind::OpenApi, args.url, args.server).await,
        ServerKind::Local(args) => new.with_command(args).await,
        ServerKind::Code(args) => new.with_code(args).await,
        ServerKind::BuiltIn(BuiltInServerArgs { id }) => new.built_in(id).await,
    }
}

/// The menu of AddServerPage.tsx, in its order.
fn choose_kind() -> Result<ServerKind> {
    if !std::io::stdin().is_terminal() {
        bail!(
            "Name the kind of server, for example: gatana create server remote <URL>. Run \"gatana create server --help\" to see all kinds"
        );
    }
    let choices = [
        ("Remote: HTTP streaming", "The standard for a hosted MCP server"),
        ("Remote: server-sent events (legacy)", "The older remote transport, still used by some services"),
        ("Runnable code", "Write the tools yourself, AWS Lambda-style"),
        ("Executable app", "A command such as npx or uvx, run in a container of its own"),
        ("Built-in", "Tools Gatana provides itself, with nothing to host"),
        ("HTTP OpenAPI", "Turn an OpenAPI or Swagger specification into tools"),
    ];
    let labels: Vec<String> = choices
        .iter()
        .map(|(label, description)| format!("{label} {}", output::dim(&format!("({description})"))))
        .collect();
    let index = dialoguer::Select::new()
        .with_prompt("Which kind of server do you want to add?")
        .items(&labels)
        .default(0)
        .interact()?;
    Ok(match index {
        0 => ServerKind::Remote(RemoteServerArgs::default()),
        1 => ServerKind::Remote(RemoteServerArgs { sse: true, ..RemoteServerArgs::default() }),
        2 => ServerKind::Code(CodeServerArgs::default()),
        3 => ServerKind::Local(LocalServerArgs::default()),
        4 => ServerKind::BuiltIn(BuiltInServerArgs::default()),
        _ => ServerKind::Openapi(Default::default()),
    })
}

#[derive(Clone, Copy)]
enum UrlKind {
    Streaming,
    Sse,
    OpenApi,
}

/// What Gatana found out about the OAuth of a remote.
enum Discovery {
    /// The OAuth metadata, as the backend sent it. It goes back to the backend unchanged.
    Found(Value),
    NotFound,
    Failed(String),
    TimedOut,
}

/// How far the OAuth setup got (OAuthSetupOutcome in the frontend).
enum OAuthSetup {
    /// The issuer and a registered client are on the server: the user can sign in.
    Client,
    /// The issuer is on the server, but somebody must add a client ID and secret.
    Issuer,
    /// The remote asks for OAuth, but its authorization server was not found.
    Unfinished,
}

/// The organization a server is added to, and the servers it has.
struct NewServer<'a> {
    api: &'a gatana_api::Client,
    base_url: &'a str,
    /// Read raw: a server of a transport that this version does not know must not stop the command.
    servers: &'a [Value],
}

impl NewServer<'_> {
    fn taken_slugs(&self) -> HashSet<String> {
        self.servers.iter().filter_map(|server| text_at(server, "/slug")).map(str::to_string).collect()
    }

    /// The page of the server in the dashboard.
    fn page(&self, slug: &str) -> String {
        format!("{}/dashboard/servers/{slug}", self.base_url)
    }

    async fn create(&self, slug: &str, transport: TransportConfig, args: &NewServerArgs) -> Result<()> {
        let mut request = new_server_request(slug, transport);
        request.visibility = Some(match args.visibility {
            Visibility::Private => v2::types::ServerVisibility::Private,
            Visibility::Organization => v2::types::ServerVisibility::Organization,
        });
        request.is_output_compression_enabled = Some(args.output_compression);
        output::spinner("Creating the server...", self.api.v2().create_server_v2(&request).send()).await?;
        output::success(&format!("Created server {slug}."));
        Ok(())
    }

    /// A remote (HTTP streaming or server-sent events) or an OpenAPI specification.
    async fn with_url(&self, kind: UrlKind, url: Option<String>, args: NewServerArgs) -> Result<()> {
        let taken = self.taken_slugs();
        let (prompt, missing) = match kind {
            UrlKind::Streaming => ("URL (for example https://mcp.example.com/mcp)", "the URL"),
            UrlKind::Sse => ("URL (for example https://mcp.example.com/sse)", "the URL"),
            UrlKind::OpenApi => ("Specification URL (for example https://api.example.com/openapi.json)", "the URL"),
        };
        let url = with_scheme(&ask(url, missing, prompt, None, check_url)?);

        // The server does not exist yet, so any slug does for the discovery. The one it will most
        // likely get reads best in the logs of the backend.
        let derived = free_slug(&slug_from_url(&url), &taken);
        let probe = args.slug.clone().or_else(|| derived.clone()).unwrap_or_else(|| "new-server".to_string());
        let given = args.slug.clone();
        let (slug, discovery) = ask_during(
            discover(self.api, &probe, &url),
            &format!("Looking for the OAuth of {}...", host_of(&url)),
            move || ask_slug(given, derived, &taken),
        )
        .await?;
        report_discovery(&discovery);

        let transport = match kind {
            UrlKind::Streaming => TransportConfig::Httpstreaming { headers: Vec::new(), url: url.clone() },
            UrlKind::Sse => TransportConfig::Sse { headers: Vec::new(), url: url.clone() },
            UrlKind::OpenApi => TransportConfig::Openapi {
                base_url: None,
                headers: Vec::new(),
                method: v2::types::V2CreateServerRequestTransportConfigMethod::SpecUrl,
                spec: None,
                spec_url: Some(url.clone()),
            },
        };
        self.create(&slug, transport, &args).await?;

        let setup = match &discovery {
            Discovery::Found(metadata) => Some(
                self.set_up_oauth(&slug, metadata)
                    .await
                    .context("The server exists, but its OAuth settings were not saved")?,
            ),
            _ => None,
        };

        let page = self.page(&slug);
        let sign_in = format!("Sign in to the service: gatana create creds {slug}");
        let steps = match setup {
            Some(OAuthSetup::Client) => vec![sign_in, format!("Choose who can use it: {page}")],
            Some(OAuthSetup::Issuer) => {
                vec![format!("Add an OAuth client ID and secret: {page}?tab=settings#oauth-issuer"), sign_in]
            }
            Some(OAuthSetup::Unfinished) => {
                vec![format!("Set the OAuth issuer and client: {page}?tab=settings#oauth-issuer"), sign_in]
            }
            None => vec![
                format!("If the server needs an API key or a header, add it: {page}?tab=settings"),
                format!("Choose who can use it: {page}"),
            ],
        };
        next_steps(&steps);
        Ok(())
    }

    /// Registers an OAuth client when the authorization server permits it, then saves the OAuth
    /// metadata and the client on the server, with credentials per user (OAUTH_PER_USER in the
    /// frontend).
    async fn set_up_oauth(&self, slug: &str, metadata: &Value) -> Result<OAuthSetup> {
        let issuer = text_at(metadata, "/as/issuer").filter(|issuer| !issuer.is_empty());
        let can_register = text_at(metadata, "/as/registrationEndpoint").is_some_and(|endpoint| !endpoint.is_empty());
        let mut client = None;
        if can_register {
            let body = json!({ "oauthMetadata": metadata });
            let call = self.api.v1().register_mcp_server_oauth_client_without_saving_raw(slug, body).value();
            match output::spinner("Registering an OAuth client...", call).await {
                Ok(answer) => client = answer.get("clientConfiguration").filter(|client| client.is_object()).cloned(),
                Err(error) => warn(&format!("No OAuth client was registered: {error}")),
            }
        }
        let mut patch = json!({
            "authorization": { "method": "oauth", "credentialsScope": "user", "toolRefreshCredentialPolicy": "any" },
            "oauthMetadata": metadata,
        });
        if let Some(client) = &client {
            patch["oauthClientConfiguration"] = client.clone();
        }
        self.api.v2().patch_server_v2_raw(slug, patch).send().await?;
        Ok(match (&client, issuer) {
            (Some(_), _) => {
                output::success(&format!("Registered an OAuth client at {}.", issuer.unwrap_or("the issuer")));
                OAuthSetup::Client
            }
            (None, Some(_)) => OAuthSetup::Issuer,
            (None, None) => OAuthSetup::Unfinished,
        })
    }

    /// A command, run in a container of its own.
    async fn with_command(&self, args: LocalServerArgs) -> Result<()> {
        let taken = self.taken_slugs();
        let command = ask(
            command_line(&args.command)?,
            "the command",
            "Command (for example npx -y @modelcontextprotocol/server-github)",
            None,
            check_command,
        )?;
        // Gatana splits the command at each space, so one space between the words.
        let command = command.split_whitespace().collect::<Vec<_>>().join(" ");
        let slug = ask_slug(args.server.slug.clone(), free_slug(&slug_from_command(&command), &taken), &taken)?;
        let transport = TransportConfig::Stdio {
            command,
            docker_image: None,
            env: Vec::new(),
            health_check: None,
            http_port: None,
            limits: None,
            requests: None,
            storage: args.storage.then_some(v2::types::StdioTransportStorage { enabled: true }),
            tailscale: None,
            transport: v2::types::V2CreateServerRequestTransportConfigTransport::Stdio,
            url_path: None,
        };
        self.create(&slug, transport, &args.server).await?;
        let page = self.page(&slug);
        next_steps(&[
            format!("If the command needs environment variables, add them: {page}?tab=settings"),
            format!("Start the server and wait until it is ready: gatana deploy start {slug} --wait"),
            format!("Choose who can use it: {page}"),
        ]);
        Ok(())
    }

    /// Code that the user writes, run by Gatana.
    async fn with_code(&self, args: CodeServerArgs) -> Result<()> {
        let taken = self.taken_slugs();
        let slug = ask_slug(args.server.slug.clone(), free_slug(CODE_DEFAULT_SLUG, &taken), &taken)?;
        let runtime = match args.runtime {
            Some(runtime) => runtime,
            None if std::io::stdin().is_terminal() => {
                let runtimes = Runtime::value_variants();
                let labels: Vec<String> = runtimes.iter().map(|runtime| help_of(*runtime)).collect();
                let index = dialoguer::Select::new().with_prompt("Runtime").items(&labels).default(0).interact()?;
                runtimes[index]
            }
            None => Runtime::Node24,
        };
        let transport = TransportConfig::Hosted {
            env: Vec::new(),
            limits: None,
            requests: None,
            runtime: match runtime {
                Runtime::Node24 => v2::types::V2CreateServerRequestTransportConfigRuntime::Node24,
                Runtime::Python313 => v2::types::V2CreateServerRequestTransportConfigRuntime::Python313,
            },
            storage: args.storage.then_some(v2::types::HostedTransportStorage { enabled: true }),
            tailscale: None,
        };
        self.create(&slug, transport, &args.server).await?;
        let editor = format!("{}/source-code", self.page(&slug));
        let steps = match runtime {
            Runtime::Node24 => vec![
                format!("Make a folder with the template: gatana faas init {slug}"),
                format!("Write the tools in {slug}/index.js, then deploy them: gatana faas upload {slug} {slug}"),
                format!("Or write the code in the browser: {editor}"),
            ],
            // The CLI checks only Node.js code before an upload, so a Python upload needs --force.
            Runtime::Python313 => vec![
                "Write the tools in main.py, and the packages they need in requirements.txt".to_string(),
                format!("Deploy the folder: gatana faas upload {slug} <folder> --force"),
                format!("Or write the code in the browser: {editor}"),
            ],
        };
        next_steps(&steps);
        Ok(())
    }

    /// One of the servers that Gatana provides itself.
    async fn built_in(&self, id: Option<BuiltIn>) -> Result<()> {
        let installed: HashSet<&str> = self
            .servers
            .iter()
            .filter(|server| text_at(server, "/transportConfig/type") == Some("self"))
            .filter_map(|server| text_at(server, "/transportConfig/id"))
            .collect();
        let built_in = match id {
            Some(built_in) => built_in,
            None => match choose_built_in(&installed)? {
                Some(built_in) => built_in,
                None => return Ok(()),
            },
        };
        let id = id_of(built_in);
        if installed.contains(id.as_str()) {
            output::info(&format!("{} is installed already, as server {id}.", label_of(built_in)));
            return Ok(());
        }
        let call = self.api.v1().install_predefined_built_in_server(&id).send();
        output::spinner(&format!("Installing {}...", label_of(built_in)), call).await?;
        output::success(&format!("Installed {} as server {id}.", label_of(built_in)));
        next_steps(&[format!("Choose who can use it: {}", self.page(&id))]);
        Ok(())
    }
}

/// The built-in servers that are not installed, in a menu. The installed ones are on a line above it.
fn choose_built_in(installed: &HashSet<&str>) -> Result<Option<BuiltIn>> {
    if !std::io::stdin().is_terminal() {
        bail!("Name the built-in server, for example: gatana create server built-in artifacts");
    }
    let (done, available): (Vec<BuiltIn>, Vec<BuiltIn>) =
        BuiltIn::value_variants().iter().copied().partition(|built_in| installed.contains(id_of(*built_in).as_str()));
    if !done.is_empty() {
        let names: Vec<&str> = done.iter().map(|built_in| label_of(*built_in)).collect();
        output::println(&output::dim(&format!("Installed already: {}", names.join(", "))));
    }
    if available.is_empty() {
        output::success("All built-in servers are installed.");
        return Ok(None);
    }
    let labels: Vec<String> = available
        .iter()
        .map(|built_in| format!("{} {}", label_of(*built_in), output::dim(&format!("({})", help_of(*built_in)))))
        .collect();
    let index = dialoguer::Select::new()
        .with_prompt("Which built-in server do you want to install?")
        .items(&labels)
        .default(0)
        .interact()?;
    Ok(Some(available[index]))
}

/// The ID of a built-in server, which is also its slug.
fn id_of(built_in: BuiltIn) -> String {
    built_in.to_possible_value().map(|value| value.get_name().to_string()).unwrap_or_default()
}

/// The name on the dashboard (built-in-server-picker.tsx in the frontend).
fn label_of(built_in: BuiltIn) -> &'static str {
    match built_in {
        BuiltIn::Artifacts => "Artifacts",
        BuiltIn::Skills => "Skills",
        BuiltIn::Codemode => "CodeMode",
        BuiltIn::GatanaApi => "Gatana API",
        BuiltIn::GatanaDebug => "Debug Tools",
        BuiltIn::Fetch => "Web Fetch",
        BuiltIn::Compression => "Compression",
    }
}

/// The help text of a value, which is its doc comment in cli.rs.
fn help_of(value: impl ValueEnum) -> String {
    value.to_possible_value().and_then(|value| value.get_help().map(ToString::to_string)).unwrap_or_default()
}

/// Asks a question while `work` runs, then waits for `work` with a spinner if it is not done.
/// The question runs on a thread of its own: the runtime has one thread, and a prompt blocks it.
async fn ask_during<T: Send + 'static, W: Future>(
    work: W,
    waiting: &str,
    question: impl FnOnce() -> Result<T> + Send + 'static,
) -> Result<(T, W::Output)> {
    tokio::pin!(work);
    let mut question = tokio::task::spawn_blocking(question);
    let mut done = None;
    let answer = loop {
        tokio::select! {
            output = &mut work, if done.is_none() => done = Some(output),
            answer = &mut question => break answer.context("the question stopped")??,
        }
    };
    let output = match done {
        Some(output) => output,
        None => output::spinner(waiting, work).await,
    };
    Ok((answer, output))
}

async fn discover(api: &gatana_api::Client, slug: &str, url: &str) -> Discovery {
    let query = v1::query::DiscoverMcpServerOauth { url: Some(url.to_string()) };
    let call = api.v1().discover_mcp_server_oauth(slug, &query).value();
    match tokio::time::timeout(DISCOVERY_TIMEOUT, call).await {
        Err(_) => Discovery::TimedOut,
        Ok(Err(error)) => Discovery::Failed(error.to_string()),
        Ok(Ok(answer)) => match answer.get("oauthMetadata") {
            Some(metadata) if metadata.is_object() => Discovery::Found(metadata.clone()),
            _ => Discovery::NotFound,
        },
    }
}

fn report_discovery(discovery: &Discovery) {
    match discovery {
        Discovery::Found(metadata) => match text_at(metadata, "/as/issuer").filter(|issuer| !issuer.is_empty()) {
            Some(issuer) => output::info(&format!("OAuth found: {issuer}")),
            None => output::info("The server asks for OAuth, but its authorization server was not found."),
        },
        Discovery::NotFound => output::info("No OAuth found."),
        Discovery::Failed(error) => warn(&format!("The search for OAuth failed: {error}")),
        Discovery::TimedOut => {
            warn(&format!("The search for OAuth stopped after {} seconds.", DISCOVERY_TIMEOUT.as_secs()))
        }
    }
}

fn warn(message: &str) {
    output::eprintln(&format!("{} {message}", output::yellow("warning:")));
}

fn next_steps(steps: &[String]) {
    output::println(&format!("\n{}", output::bold("Next steps:")));
    for (index, step) in steps.iter().enumerate() {
        output::println(&format!("  {}. {step}", index + 1));
    }
}

/// A create request with only the slug and the transport; the server sets everything else.
pub(crate) fn new_server_request(slug: &str, transport: TransportConfig) -> V2CreateServerRequest {
    V2CreateServerRequest {
        slug: slug.to_string(),
        transport_config: Some(transport),
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

/// The value given as an argument, or one typed at a prompt. Without a terminal, a default that
/// passes the check stands in for the prompt.
fn ask(
    given: Option<String>,
    missing: &str,
    prompt: &str,
    default: Option<String>,
    check: impl Fn(&str) -> Result<(), String>,
) -> Result<String> {
    if let Some(value) = given {
        let value = value.trim().to_string();
        check(&value).map_err(|problem| anyhow!("{problem}"))?;
        return Ok(value);
    }
    let default = default.filter(|value| check(value).is_ok());
    if !std::io::stdin().is_terminal() {
        return default.ok_or_else(|| anyhow!("Give {missing}, or run the command in a terminal"));
    }
    let mut input =
        dialoguer::Input::<String>::new().with_prompt(prompt).validate_with(|value: &String| check(value.trim()));
    if let Some(default) = default {
        input = input.default(default);
    }
    Ok(input.interact_text()?.trim().to_string())
}

fn ask_slug(given: Option<String>, default: Option<String>, taken: &HashSet<String>) -> Result<String> {
    ask(given, "--slug", "Slug", default, |slug| check_slug(slug, taken))
}

fn check_slug(slug: &str, taken: &HashSet<String>) -> Result<(), String> {
    let allowed = |b: u8| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'-';
    if slug.is_empty() || slug.len() > MAX_SLUG_LENGTH || !slug.bytes().all(allowed) {
        return Err(format!("Use 1 to {MAX_SLUG_LENGTH} lowercase letters, digits and hyphens for the slug"));
    }
    if slug.starts_with('-') || slug.ends_with('-') {
        return Err("Do not start or end the slug with a hyphen".into());
    }
    if taken.contains(slug) {
        return Err(format!("A server with the slug {slug} exists already. Use a different slug"));
    }
    Ok(())
}

fn check_url(value: &str) -> Result<(), String> {
    match url::Url::parse(&with_scheme(value)) {
        Ok(url) if matches!(url.scheme(), "http" | "https") && url.host().is_some() => Ok(()),
        _ => Err("Enter an http or https URL".into()),
    }
}

fn check_command(value: &str) -> Result<(), String> {
    if value.trim().is_empty() { Err("Enter the command that starts the server".into()) } else { Ok(()) }
}

/// The command from the arguments: one argument is the full command line, typed in quotes; more
/// arguments are its words. Gatana splits the command at each space, so a word cannot hold one.
fn command_line(words: &[String]) -> Result<Option<String>> {
    match words {
        [] => Ok(None),
        [line] => Ok(Some(line.clone())),
        words => {
            if let Some(word) = words.iter().find(|word| word.contains(char::is_whitespace)) {
                bail!("The argument \"{word}\" has a space in it. Gatana splits the command at each space");
            }
            Ok(Some(words.join(" ")))
        }
    }
}

/// A URL typed without a scheme still means https (withScheme in the frontend).
fn with_scheme(value: &str) -> String {
    let value = value.trim();
    let has_scheme = value.split_once("://").is_some_and(|(scheme, _)| {
        scheme.starts_with(|c: char| c.is_ascii_alphabetic())
            && scheme.chars().all(|c| c.is_ascii_alphanumeric() || "+.-".contains(c))
    });
    if has_scheme { value.to_string() } else { format!("https://{value}") }
}

fn host_of(url: &str) -> String {
    url::Url::parse(url).ok().and_then(|url| url.host_str().map(str::to_string)).unwrap_or_else(|| url.to_string())
}

/// Lowercase letters, digits and single hyphens, without a hyphen first (toSlug in the frontend).
fn to_slug(value: &str) -> String {
    let mut slug = String::new();
    for ch in value.to_lowercase().chars() {
        let hyphen_allowed = ch == '-' && !slug.is_empty() && !slug.ends_with('-');
        if ch.is_ascii_lowercase() || ch.is_ascii_digit() || hyphen_allowed {
            slug.push(ch);
        }
    }
    slug
}

/// A slug made from a name rather than typed: no hyphen at either end, and at most 20 characters
/// (toDerivedSlug in the frontend).
fn derived_slug(value: &str) -> String {
    let slug: String = to_slug(value).trim_end_matches('-').chars().take(MAX_SLUG_LENGTH).collect();
    slug.trim_end_matches('-').to_string()
}

/// The name of the service that a URL belongs to: `https://copilot.github.com/mcp` gives `github`.
/// Empty for a URL without a name, such as an IP address (slugFromUrl in the frontend).
fn slug_from_url(value: &str) -> String {
    let Ok(url) = url::Url::parse(&with_scheme(value)) else {
        return String::new();
    };
    let Some(url::Host::Domain(host)) = url.host() else {
        return String::new();
    };
    let host = host.to_lowercase();
    let mut labels: Vec<&str> = host.strip_prefix("www.").unwrap_or(&host).split('.').collect();
    // Remove the top-level domain, then a label such as `co` below it, and keep the last one left.
    if labels.len() > 1 {
        labels.pop();
    }
    if labels.len() > 1 && labels.last().is_some_and(|label| PUBLIC_SUFFIX_LABELS.contains(label)) {
        labels.pop();
    }
    derived_slug(labels.last().copied().unwrap_or_default())
}

/// The package that a command runs: its first argument that is not a flag, without its scope or
/// version. `npx -y @scope/server-github@2` gives `server-github` (slugFromCommand in the frontend).
fn slug_from_command(value: &str) -> String {
    let Some(argument) = value.split_whitespace().skip(1).find(|word| !word.starts_with('-')) else {
        return String::new();
    };
    let name = argument.rsplit('/').next().unwrap_or_default();
    let without_version = name.rfind('@').map_or(name, |index| &name[..index]);
    derived_slug(if without_version.is_empty() { name } else { without_version })
}

/// `slug`, or the first of `slug-2`, `slug-3` and so on that no server has. None for an empty slug.
fn free_slug(slug: &str, taken: &HashSet<String>) -> Option<String> {
    if slug.is_empty() {
        return None;
    }
    if !taken.contains(slug) {
        return Some(slug.to_string());
    }
    (2..100)
        .map(|number| {
            let suffix = format!("-{number}");
            let stem: String = slug.chars().take(MAX_SLUG_LENGTH - suffix.len()).collect();
            format!("{}{suffix}", stem.trim_end_matches('-'))
        })
        .find(|candidate| !taken.contains(candidate))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_slug_comes_from_the_domain_as_on_the_dashboard() {
        assert_eq!(slug_from_url("https://copilot.github.com/mcp"), "github");
        assert_eq!(slug_from_url("api.example.co.uk/v1"), "example");
        assert_eq!(slug_from_url("https://www.notion.so/mcp"), "notion");
        assert_eq!(slug_from_url("https://mcp.linear.app/sse"), "linear");
        assert_eq!(slug_from_url("http://localhost:8080/mcp"), "localhost");
        assert_eq!(slug_from_url("https://a-very-long-service-name-here.io"), "a-very-long-service");
        // Nothing to take a name from
        assert_eq!(slug_from_url("http://10.0.0.1/mcp"), "");
        assert_eq!(slug_from_url("http://[::1]:3000/mcp"), "");
        assert_eq!(slug_from_url("not a url"), "");
    }

    #[test]
    fn the_slug_comes_from_the_package_of_a_command() {
        assert_eq!(slug_from_command("npx -y @modelcontextprotocol/server-github"), "server-github");
        assert_eq!(slug_from_command("npx -y @scope/server-github@2"), "server-github");
        assert_eq!(slug_from_command("uvx google-workspace"), "google-workspace");
        assert_eq!(slug_from_command("npx -y @scope"), "scope");
        assert_eq!(slug_from_command("node"), "");
        assert_eq!(slug_from_command("npx --yes"), "");
    }

    #[test]
    fn slugs_are_checked_as_the_backend_checks_them() {
        let taken: HashSet<String> = ["github".to_string()].into();
        assert!(check_slug("linear-2", &taken).is_ok());
        assert!(check_slug("", &taken).is_err());
        assert!(check_slug(&"a".repeat(21), &taken).is_err());
        assert!(check_slug("Linear", &taken).is_err());
        assert!(check_slug("my_server", &taken).is_err());
        assert!(check_slug("-linear", &taken).is_err());
        assert!(check_slug("linear-", &taken).is_err());
        assert!(check_slug("github", &taken).unwrap_err().contains("exists already"));
    }

    #[test]
    fn a_taken_default_gets_a_number() {
        let taken: HashSet<String> =
            ["github", "github-2", "a-very-long-service"].iter().map(|slug| slug.to_string()).collect();
        assert_eq!(free_slug("linear", &taken).as_deref(), Some("linear"));
        assert_eq!(free_slug("github", &taken).as_deref(), Some("github-3"));
        assert_eq!(free_slug("a-very-long-service", &taken).as_deref(), Some("a-very-long-servic-2"));
        assert_eq!(free_slug("", &taken), None);
        for slug in [free_slug("github", &taken), free_slug("a-very-long-service", &taken)].into_iter().flatten() {
            assert!(check_slug(&slug, &taken).is_ok(), "{slug}");
        }
    }

    #[test]
    fn a_url_without_a_scheme_means_https() {
        assert_eq!(with_scheme("mcp.example.com/mcp"), "https://mcp.example.com/mcp");
        assert_eq!(with_scheme(" http://localhost:3000 "), "http://localhost:3000");
        assert!(check_url("mcp.example.com").is_ok());
        assert!(check_url("ftp://example.com").is_err());
        assert!(check_url("").is_err());
    }

    #[test]
    fn the_command_is_one_argument_or_its_words() {
        assert_eq!(command_line(&[]).unwrap(), None);
        let line = command_line(&["npx -y @scope/server".to_string()]).unwrap();
        assert_eq!(line.as_deref(), Some("npx -y @scope/server"));
        let words = ["npx", "-y", "@scope/server"].map(String::from);
        assert_eq!(command_line(&words).unwrap().as_deref(), Some("npx -y @scope/server"));
        assert!(command_line(&["node".to_string(), "my server.js".to_string()]).is_err());
    }

    #[test]
    fn built_in_ids_are_the_ids_of_the_backend() {
        let ids: Vec<String> = BuiltIn::value_variants().iter().map(|built_in| id_of(*built_in)).collect();
        assert_eq!(ids, ["artifacts", "skills", "codemode", "gatana-api", "gatana-debug", "fetch", "compression"]);
    }
}
