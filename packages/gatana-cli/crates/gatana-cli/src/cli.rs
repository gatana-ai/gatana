//! The command line: every command, flag and help text.

use crate::output::Format;
use crate::skills::hooks::HookAgent;
use clap::{Args, Parser, Subcommand, ValueEnum};
use std::path::PathBuf;

const ROOT_HELP: &str = "\
{about} {version}

{usage-heading} {usage}

Get Started:
  signup        Create a new organization and sign in to it
  install       Sign in and connect the AI agents on this machine: gateway, skills and hooks

Basic Commands:
  get           List or show resources: server, tool, creds, account, profile, pat, org, sandbox, skill
  describe      Show details of a specific resource
  create        Create a resource: a server, credentials, an account, a profile, a token or a sandbox
  delete        Delete resources
  patch         Patch a resource

Server Management:
  tools         Call a tool (alias: tool)
  deployment    Manage server deployments (alias: deploy)
  creds         Get the effective credentials for a server
  faas          Manage FaaS servers (hosted source code)
  sandbox       Manage sandboxes (requires early access)

Access:
  profile       Manage the servers, members, maintainers and tools of a profile

Skills:
  skills        Managing skills and installing them to this computer

Utility Commands:
  config        Show and change the configuration; log in
  auth-info     Show the signed-in user
  schema        Print OpenAPI resource schemas
  upgrade       Upgrade gatana to the latest release, using the original installation method
  help          Show help for this command or a subcommand

Options:
{options}{after-help}

Learn More:
  https://github.com/gatana-ai/gatana/tree/main/packages/gatana-cli";

/// `ROOT_HELP` with every heading in clap's header style, so they look like "Usage:". clap removes
/// the style when the output is not a terminal or NO_COLOR is set.
fn root_help() -> String {
    let header = *clap::builder::Styles::default().get_header();
    ROOT_HELP
        .lines()
        .map(|line| {
            if line.ends_with(':') && !line.starts_with(' ') {
                format!("{header}{line}{header:#}")
            } else {
                line.to_string()
            }
        })
        .collect::<Vec<_>>()
        .join("\n")
}

#[derive(Parser, Debug)]
#[command(
    name = "gatana",
    version,
    about = "Gatana CLI",
    help_template = root_help(),
    propagate_version = true
)]
pub struct Cli {
    /// Output format
    #[arg(short = 'o', long = "output", global = true, value_enum, value_name = "FORMAT")]
    pub output: Option<Format>,

    #[command(subcommand)]
    pub command: Command,
}

#[derive(Subcommand, Debug)]
pub enum Command {
    /// List or show resources: server, tool, creds, account, profile, pat, org, sandbox, skill
    Get {
        #[command(subcommand)]
        resource: GetCommand,
    },
    /// Show details of a specific resource
    Describe {
        #[command(subcommand)]
        resource: DescribeCommand,
    },
    /// Create a resource
    Create {
        #[command(subcommand)]
        resource: CreateCommand,
    },
    /// Delete resources
    Delete {
        #[command(subcommand)]
        resource: DeleteCommand,
    },
    /// Patch a resource
    Patch {
        #[command(subcommand)]
        resource: PatchCommand,
    },
    /// Call a tool. See "gatana get tools" for the list of available tools
    #[command(visible_alias = "tool", after_help = TOOL_EXAMPLES)]
    Tools(ToolArgs),
    /// Manage server deployments (stdio and hosted)
    #[command(name = "deployment", visible_alias = "deploy")]
    Deployment {
        #[command(subcommand)]
        command: DeploymentCommand,
    },
    /// Get the effective credentials for a server
    Creds(CredsArgs),
    /// Manage FaaS servers (hosted source code)
    Faas {
        #[command(subcommand)]
        command: FaasCommand,
    },
    /// Manage sandboxes (requires early access)
    Sandbox {
        #[command(subcommand)]
        command: SandboxCommand,
    },
    /// Manage the servers, members, maintainers and tools of a profile
    #[command(after_help = PROFILE_EXAMPLES)]
    Profile {
        #[command(subcommand)]
        command: ProfileCommand,
    },
    /// Install skills for AI agents, follow collections, and push local changes to Gatana
    Skills {
        #[command(subcommand)]
        command: SkillsCommand,
    },
    /// Show configuration requirements and current status
    #[command(long_about = CONFIG_ABOUT)]
    Config {
        #[command(subcommand)]
        command: ConfigCommand,
    },
    /// Show the signed-in user
    AuthInfo,
    /// Create a new organization and sign in to it
    #[command(after_help = SIGNUP_EXAMPLES)]
    Signup(SignupArgs),
    /// Sign in and connect AI agents to Gatana. Add the MCP gateway, organization skills,
    /// and hooks that update skills when a session starts
    #[command(after_help = INSTALL_EXAMPLES)]
    Install(InstallAgentsArgs),
    /// Print OpenAPI resource schemas
    Schema {
        #[command(subcommand)]
        command: SchemaCommand,
    },
    /// Upgrade gatana to the latest release, using the original installation method: install.sh, npm, pnpm,
    /// bun or Homebrew
    Upgrade(UpgradeArgs),
}

const CONFIG_ABOUT: &str = "Show and change the configuration. The CLI checks these sources in order:

1. Environment variables
   Set GATANA_API_KEY and either GATANA_ORG_ID or GATANA_BASE_URL.
   Example:
     export GATANA_API_KEY=your_api_key
     export GATANA_ORG_ID=your_org_id

2. Saved settings in ~/.gatana.config
   Use \"gatana config\" commands to change these settings.
   GATANA_ORG_ID selects a saved organization. If unset, the CLI uses the default organization.";

#[derive(Subcommand, Debug)]
pub enum GetCommand {
    /// List servers or show one server
    #[command(visible_alias = "servers")]
    Server {
        /// Server slug (omit to list all)
        name: Option<String>,
    },
    /// List tools or show one tool
    #[command(visible_alias = "tools")]
    Tool {
        /// Tool name (omit to list all). Use "gatana tool <name>" to call the tool
        name: Option<String>,
        /// Only show enabled tools
        #[arg(long)]
        enabled: bool,
    },
    /// Get credentials for a server
    #[command(visible_aliases = ["credential", "credentials"])]
    Creds {
        /// Credential ID (omit to list all)
        id: Option<String>,
        /// Server slug
        #[arg(short = 's', long = "server", value_name = "SLUG")]
        server: Option<String>,
        /// Resolve credentials, using a refresh token if needed
        #[arg(short = 'e', long = "with-effective")]
        with_effective: bool,
    },
    /// List sandboxes or show one sandbox
    #[command(visible_alias = "sandboxes")]
    Sandbox {
        /// Sandbox ID (omit to list all)
        id: Option<String>,
        /// Also include archived sandboxes
        #[arg(long)]
        all: bool,
    },
    /// List skills or show one skill
    #[command(visible_alias = "skills")]
    Skill {
        /// Skill name (omit to list all)
        name: Option<String>,
        /// Filter skills by text in their name or description
        #[arg(short = 'q', long = "query", value_name = "TEXT")]
        query: Option<String>,
    },
    /// List accounts or show one account
    #[command(visible_aliases = ["accounts", "user", "users"])]
    Account {
        /// Email address or ID (omit to list all)
        name: Option<String>,
        /// Only list accounts of this kind
        #[arg(long = "type", value_enum, value_name = "KIND")]
        kind: Option<AccountKind>,
    },
    /// List profiles or show one profile
    #[command(visible_alias = "profiles")]
    Profile {
        /// Profile name or ID (omit to list all)
        name: Option<String>,
        /// Only list the profiles that hold this server
        #[arg(short = 's', long = "server", value_name = "SLUG")]
        server: Option<String>,
    },
    /// List the personal access tokens of a service account
    #[command(visible_aliases = ["pats", "token", "tokens"])]
    Pat {
        /// The service account: email address or ID
        #[arg(short = 'a', long, value_name = "ACCOUNT")]
        account: String,
        /// Show the API keys instead of hiding them
        #[arg(long = "show-secrets")]
        show_secrets: bool,
    },
    /// Show the settings of the organization (organization owners only)
    #[command(visible_aliases = ["organization", "settings"])]
    Org {
        /// Show secrets, such as the client secret of the identity provider, instead of hiding them
        #[arg(long = "show-secrets")]
        show_secrets: bool,
    },
}

#[derive(Clone, Copy, Debug, ValueEnum)]
pub enum AccountKind {
    /// People, who sign in with a browser
    User,
    /// Accounts for scripts and agents, which sign in with a token
    ServiceAccount,
    /// Both
    All,
}

#[derive(Subcommand, Debug)]
pub enum DescribeCommand {
    /// Show server deployment status and tools
    Server {
        /// Server slug
        name: String,
    },
    /// Show a skill with its instructions
    Skill {
        /// Skill name
        name: String,
    },
    /// Show an account with its profiles and teams, and the tokens of a service account
    #[command(visible_alias = "user")]
    Account {
        /// Email address or ID
        name: String,
    },
    /// Show a profile with its servers, members, maintainers and claim mappings
    Profile {
        /// Profile name or ID
        name: String,
    },
    /// Show the plan, the accounts and the quotas of the organization (organization owners only)
    #[command(visible_alias = "organization")]
    Org,
}

#[derive(Clone, Copy, Debug, ValueEnum)]
pub enum CredentialScope {
    User,
    Server,
}

#[derive(Subcommand, Debug)]
pub enum CreateCommand {
    /// Create an MCP server, as the Add Server page of the dashboard does. Omit the kind to choose it
    /// from a menu
    #[command(after_help = CREATE_SERVER_EXAMPLES)]
    Server {
        #[command(subcommand)]
        kind: Option<ServerKind>,
    },
    /// Create or replace server credentials. The server configuration selects OAuth or API keys.
    /// For OAuth, omit input to get an authorization URL, or provide tokens as JSON with -f or stdin.
    /// For API keys, provide JSON with -f or stdin: [["header","value"], …]
    #[command(visible_alias = "creds")]
    Credentials {
        /// Server slug
        server_slug: String,
        /// JSON file with credentials
        #[arg(short = 'f', long = "file", value_name = "PATH")]
        file: Option<PathBuf>,
        /// Credential scope (defaults to the server setting)
        #[arg(long, value_enum)]
        scope: Option<CredentialScope>,
    },
    /// Create a new sandbox
    Sandbox,
    /// Invite a user. Gatana sends an email with a link to set a password
    #[command(visible_alias = "user")]
    Account(CreateAccountArgs),
    /// Create a service account, for a script or an agent, and print its API key
    ServiceAccount(CreateServiceAccountArgs),
    /// Create a profile. Add servers with --server, or later with "gatana profile add-server"
    Profile(CreateProfileArgs),
    /// Create a personal access token for a service account and print its API key
    #[command(visible_alias = "token")]
    Pat(CreatePatArgs),
}

#[derive(Args, Debug)]
pub struct CreateAccountArgs {
    /// Email address of the user
    pub email: String,
    /// Display name. Default: the part of the email address before the @
    #[arg(long)]
    pub name: Option<String>,
    /// Role in the organization
    #[arg(long, value_enum, default_value_t)]
    pub role: Role,
}

#[derive(Args, Debug)]
pub struct CreateServiceAccountArgs {
    /// Display name, for example "Deploy bot". The email address of the account is made from it
    pub name: String,
    /// Role in the organization
    #[arg(long, value_enum, default_value_t)]
    pub role: Role,
}

#[derive(Clone, Copy, Debug, Default, ValueEnum)]
pub enum Role {
    /// Uses the servers that teams, profiles and grants give access to
    #[default]
    Member,
    /// Manages the organization: every server, account and setting
    Owner,
}

#[derive(Args, Debug)]
pub struct CreateProfileArgs {
    /// Profile name
    pub name: String,
    /// What the profile is for
    #[arg(long, default_value = "")]
    pub description: String,
    /// Every member can apply the profile themselves, and so gets member access to all its servers
    #[arg(long = "open-to-all")]
    pub open_to_all: bool,
    /// A session with this profile reaches only the servers of the profile, organization owners too
    #[arg(long)]
    pub restrictive: bool,
    /// Sessions with this profile run in Code Mode for all servers
    #[arg(long = "code-mode")]
    pub code_mode: bool,
    /// A server to put in the profile. Repeat for more servers
    #[arg(short = 's', long = "server", value_name = "SLUG")]
    pub servers: Vec<String>,
}

#[derive(Args, Debug)]
pub struct CreatePatArgs {
    /// The service account: email address or ID
    #[arg(short = 'a', long, value_name = "ACCOUNT")]
    pub account: String,
    /// Name of the token, for example the script that uses it
    #[arg(long)]
    pub name: String,
    /// Confine the token to this profile. Repeat for more profiles
    #[arg(short = 'p', long = "profile", value_name = "PROFILE")]
    pub profiles: Vec<String>,
}

const CREATE_SERVER_EXAMPLES: &str = r#"Examples:
  # Choose the kind of server in a menu, then answer the questions
  $ gatana create server

  # A remote MCP server. The CLI looks for its OAuth and registers a client when it can
  $ gatana create server remote https://mcp.example.com/mcp

  # A remote that uses server-sent events (legacy), with a slug of your choice
  $ gatana create server remote https://mcp.example.com/sse --sse --slug example

  # Tools made from an OpenAPI specification
  $ gatana create server openapi https://api.example.com/openapi.json

  # A command that Gatana runs in a container of its own. Put the options before the command
  $ gatana create server local --slug github npx -y @modelcontextprotocol/server-github

  # Your own code, in Python
  $ gatana create server code --slug my-tools --runtime python313

  # A server that Gatana provides itself
  $ gatana create server built-in artifacts"#;

#[derive(Subcommand, Debug)]
pub enum ServerKind {
    /// A remote MCP server at a URL. The CLI looks for its OAuth and registers a client when it can
    Remote(RemoteServerArgs),
    /// Tools made from an OpenAPI or Swagger specification at a URL
    #[command(name = "openapi")]
    Openapi(OpenApiServerArgs),
    /// A command such as npx or uvx. Gatana runs it in a container of its own
    #[command(visible_alias = "stdio")]
    Local(LocalServerArgs),
    /// Tools that you write yourself in Node.js or Python, AWS Lambda-style
    #[command(visible_alias = "hosted")]
    Code(CodeServerArgs),
    /// A server that Gatana provides itself, with nothing to host
    #[command(name = "built-in", visible_alias = "builtin")]
    BuiltIn(BuiltInServerArgs),
}

/// The settings that every new server takes.
#[derive(Args, Debug, Default)]
pub struct NewServerArgs {
    /// The server slug: 1 to 20 lowercase letters, digits and hyphens. Tool names start with it.
    /// Omit to choose it, with a default made from the URL or the command
    #[arg(short = 's', long)]
    pub slug: Option<String>,
    /// Who can see and use the server
    #[arg(long, value_enum, default_value_t)]
    pub visibility: Visibility,
    /// Compress large tool results, so that they use fewer tokens
    #[arg(long = "output-compression")]
    pub output_compression: bool,
}

#[derive(Clone, Copy, Debug, Default, ValueEnum)]
pub enum Visibility {
    /// Only members with access through a team or a direct assignment
    #[default]
    Private,
    /// All members of the organization
    Organization,
}

#[derive(Args, Debug, Default)]
pub struct RemoteServerArgs {
    /// The URL of the MCP endpoint. Omit to type it at a prompt
    pub url: Option<String>,
    /// The server uses server-sent events (legacy) instead of HTTP streaming
    #[arg(long)]
    pub sse: bool,
    #[command(flatten)]
    pub server: NewServerArgs,
}

#[derive(Args, Debug, Default)]
pub struct OpenApiServerArgs {
    /// The URL of the OpenAPI or Swagger document. Omit to type it at a prompt
    pub url: Option<String>,
    #[command(flatten)]
    pub server: NewServerArgs,
}

#[derive(Args, Debug, Default)]
pub struct LocalServerArgs {
    /// The command that starts the server, for example: npx -y @modelcontextprotocol/server-github.
    /// Omit to type it at a prompt
    #[arg(value_name = "COMMAND", trailing_var_arg = true, allow_hyphen_values = true)]
    pub command: Vec<String>,
    /// Attach a persistent volume
    #[arg(long)]
    pub storage: bool,
    #[command(flatten)]
    pub server: NewServerArgs,
}

#[derive(Args, Debug, Default)]
pub struct CodeServerArgs {
    /// The runtime of the code. Omit to choose it from a menu
    #[arg(long, value_enum)]
    pub runtime: Option<Runtime>,
    /// Attach a persistent volume
    #[arg(long)]
    pub storage: bool,
    #[command(flatten)]
    pub server: NewServerArgs,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, ValueEnum)]
pub enum Runtime {
    /// Node.js 24. The source code exports its tools from index.js
    Node24,
    /// Python 3.13. The source code exports its tools from main.py; Gatana installs requirements.txt on start
    Python313,
}

#[derive(Args, Debug, Default)]
pub struct BuiltInServerArgs {
    /// The built-in server. Omit to choose from the servers that are not installed
    #[arg(value_enum, value_name = "ID")]
    pub id: Option<BuiltIn>,
}

/// The servers that Gatana provides itself. The value is the ID of the install-predefined route in
/// the backend, and the slug the server gets.
#[derive(Clone, Copy, Debug, PartialEq, Eq, ValueEnum)]
pub enum BuiltIn {
    /// Create and share generated content (Markdown or HTML) as artifacts, stored on Gatana
    Artifacts,
    /// A registry of reusable instructions that agents find at the start of a task
    Skills,
    /// The search_tools and execute_code tools, to find other MCP tools and use them together in TypeScript
    Codemode,
    /// The full Gatana API over MCP
    GatanaApi,
    /// Tools for debugging, such as slow responses and the authorization data of the caller
    GatanaDebug,
    /// Gets the main content of a web page
    Fetch,
    /// Searches the full content of large tool results that Gatana compressed
    Compression,
}

#[derive(Subcommand, Debug)]
pub enum DeleteCommand {
    /// Delete a server
    Server {
        /// Server slug
        name: String,
    },
    /// Delete credentials for a server
    #[command(visible_alias = "creds")]
    Credentials {
        /// Credential ID
        id: String,
        /// Server slug
        #[arg(short = 's', long = "server", value_name = "SLUG", required = true)]
        server: String,
    },
    /// Delete a sandbox
    Sandbox {
        /// Sandbox ID
        id: String,
    },
    /// Delete an account permanently
    #[command(visible_alias = "user")]
    Account {
        /// Email address or ID
        name: String,
    },
    /// Delete a profile. It is also removed from every personal access token
    Profile {
        /// Profile name or ID
        name: String,
    },
    /// Delete a personal access token of a service account
    #[command(visible_alias = "token")]
    Pat {
        /// Token ID or name
        token: String,
        /// The service account: email address or ID
        #[arg(short = 'a', long, value_name = "ACCOUNT")]
        account: String,
    },
}

const PATCH_EXAMPLES: &str = r#"To get the schema, run "gatana schema server".

Examples:
  # Dot-notation key=value pairs
  $ gatana patch server my-server -p description="Updated description"
  $ gatana patch server my-server -p isEnabled=false -p oauthMetadata.as.deviceAuthorizationEndpoint="https://auth.example.com/device"

  # Inline JSON
  $ gatana patch server my-server -p '{"description": "New desc", "isEnabled": true}'

  # From a JSON file
  $ gatana patch server my-server -f patch.json

  # From stdin
  $ echo '{"description": "Piped"}' | gatana patch server my-server"#;

const PATCH_ACCOUNT_EXAMPLES: &str = r#"To get the schema, run "gatana schema account".

Examples:
  $ gatana patch account ada@example.com -p role=owner
  $ gatana patch account ada@example.com -p isDisabled=true"#;

const PATCH_PROFILE_EXAMPLES: &str = r#"To get the schema, run "gatana schema profile".

Examples:
  $ gatana patch profile Engineering -p description="Tools for the platform team"
  $ gatana patch profile Engineering -p isRestrictive=true

  # serverIds replaces the full list. To add or remove one server, use "gatana profile add-server"
  $ gatana patch profile Engineering -p '{"serverIds": ["github", "linear"]}'"#;

const PATCH_ORG_EXAMPLES: &str = r#"To get the schema, run "gatana schema org".

Examples:
  $ gatana patch org -p allowMemberAddLocalServers=false

  # A nested setting merges with the stored one, so one field is enough
  $ gatana patch org -p upstreamOidcConfiguration.clientId=new-client-id

  # The logo in the sidebar of the app
  $ gatana patch org --logo ./logo.png"#;

#[derive(Subcommand, Debug)]
pub enum PatchCommand {
    /// Patch an existing server (JSON Merge Patch RFC 7396 strategy). To get the schema, run
    /// "gatana schema server".
    #[command(after_help = PATCH_EXAMPLES)]
    Server {
        /// Server slug
        server_slug: String,
        #[command(flatten)]
        input: PatchInput,
    },
    /// Patch an account. Organization owners can change every field; members only their own name
    #[command(after_help = PATCH_ACCOUNT_EXAMPLES, visible_alias = "user")]
    Account {
        /// Email address or ID
        name: String,
        #[command(flatten)]
        input: PatchInput,
    },
    /// Patch a profile. The keys you leave out keep their values
    #[command(after_help = PATCH_PROFILE_EXAMPLES)]
    Profile {
        /// Profile name or ID
        name: String,
        #[command(flatten)]
        input: PatchInput,
    },
    /// Patch the settings of the organization (organization owners only). The keys you leave out
    /// keep their values, and a nested setting merges with the stored one
    #[command(after_help = PATCH_ORG_EXAMPLES, visible_aliases = ["organization", "settings"])]
    Org {
        #[command(flatten)]
        input: PatchInput,
        /// Set the logo in the sidebar of the app: a PNG, JPEG, WebP or SVG file of at most 256 KB
        #[arg(long, value_name = "PATH", conflicts_with = "remove_logo")]
        logo: Option<PathBuf>,
        /// Remove the logo
        #[arg(long = "remove-logo")]
        remove_logo: bool,
    },
}

/// The patch of a `patch` command: one of these, or JSON piped to stdin.
#[derive(Args, Debug)]
pub struct PatchInput {
    /// JSON file with the patch (omit to read from stdin)
    #[arg(short = 'f', long = "file", value_name = "PATH")]
    pub file: Option<PathBuf>,
    /// Inline patch: JSON string or dot-notation key=value pairs
    #[arg(short = 'p', long = "patch", value_name = "KV", num_args = 1.., action = clap::ArgAction::Append)]
    pub patch: Vec<String>,
}

const TOOL_EXAMPLES: &str = r#"Get the tool schema by running "gatana get tools <tool_name>"
Examples:
  # Dot-notation key=value pairs
  $ gatana tool my_tool -a argument1="arg1 value" -a argument2.nested="nested value"

  # Inline JSON
  $ gatana tool my_tool -a '{"argument1": "arg1 value", "argument2": {"nested": "nested value"}}'

  # From a JSON file
  $ gatana tool my_tool -f arg.json

  # From stdin
  $ echo '{"argument1": "Piped"}' | gatana tool my_tool"#;

#[derive(Clone, Copy, Debug, ValueEnum, PartialEq)]
pub enum ToolPart {
    Text,
    Structured,
    Unstructured,
}

#[derive(Args, Debug)]
pub struct ToolArgs {
    /// Name of the tool to call. See "gatana get tools" for the list of available tools
    #[arg(value_name = "TOOL_NAME")]
    pub tool_name: String,
    /// JSON file with tool arguments (omit to read from stdin)
    #[arg(short = 'f', long = "file", value_name = "PATH")]
    pub file: Option<PathBuf>,
    /// Tool arguments: JSON string or dot-notation key=value pairs
    #[arg(short = 'a', long = "arg", value_name = "KV", num_args = 1.., action = clap::ArgAction::Append)]
    pub arg: Vec<String>,
    /// Output part of the raw response
    #[arg(short = 'p', long = "part", value_enum, default_value = "text")]
    pub part: ToolPart,
}

#[derive(Subcommand, Debug)]
pub enum DeploymentCommand {
    /// Show server deployment status
    Get {
        /// Server slug
        name: String,
    },
    /// Show logs for a server (for stdio and hosted servers)
    Logs {
        /// Server slug
        name: String,
        /// Follow log output
        #[arg(short = 'f', long)]
        follow: bool,
        /// Show previous logs instead of current logs (useful if the server keeps restarting)
        #[arg(short = 'p', long)]
        previous: bool,
        /// Deployment ID to get logs for (defaults to latest)
        #[arg(long = "id", value_name = "DEPLOYMENT_ID")]
        id: Option<String>,
    },
    /// Wait for deployment to finish
    Wait {
        /// Server slug
        name: String,
        /// Maximum wait time, for example 1m30s
        #[arg(long, value_name = "DURATION", default_value = "10m")]
        timeout: String,
    },
    /// Stop a server. Unless disabled, it starts again when a tool is called
    Stop {
        /// Server slug
        name: String,
    },
    /// Start a server
    Start {
        /// Server slug
        name: String,
        /// Wait for deployment to finish before returning
        #[arg(long)]
        wait: bool,
    },
}

#[derive(Args, Debug)]
pub struct CredsArgs {
    /// Server slug
    pub server_slug: String,
    /// ID of a specific credential to retrieve the token for. If omitted, the effective credentials
    /// for the current user are resolved automatically.
    #[arg(long = "cred-id", value_name = "ID")]
    pub cred_id: Option<String>,
}

#[derive(Subcommand, Debug)]
pub enum FaasCommand {
    /// Create a FaaS server source directory from a template
    Init {
        /// Path to the source code directory
        #[arg(default_value = ".")]
        path: PathBuf,
    },
    /// Verify local source code (requires Node.js)
    Verify {
        /// Path to the source code directory
        path: PathBuf,
    },
    /// Call a tool in the local source code for testing (requires Node.js)
    Run {
        /// Path to the source code directory. Use . for current directory
        path: PathBuf,
        /// Name of the tool to run
        #[arg(value_name = "TOOL_NAME")]
        tool_name: String,
        /// Inline input JSON for the tool call
        #[arg(short = 'i', long = "input", value_name = "JSON")]
        input: Option<String>,
        /// Path to JSON file with input for the tool call (ignored if --input is used)
        #[arg(short = 'f', long = "file", value_name = "PATH")]
        file: Option<PathBuf>,
        /// Set input parameter (dot-path supported, e.g. -p a=1 -p b.nested=2)
        #[arg(short = 'p', long = "param", value_name = "KEY=VALUE")]
        param: Vec<String>,
    },
    /// Upload new source code
    Upload {
        /// Server slug
        name: String,
        /// Root directory path for deployment
        #[arg(default_value = ".")]
        path: PathBuf,
        /// Create a new server if it does not exist
        #[arg(long)]
        create: bool,
        /// Skip fetching crash logs on deployment failure
        #[arg(long = "no-logs")]
        no_logs: bool,
        /// Skip waiting for deployment to finish before returning
        #[arg(long = "no-wait")]
        no_wait: bool,
        /// Force deployment even if validation checks fail
        #[arg(long)]
        force: bool,
    },
    /// Download the deployed source code as a zip file
    Download {
        /// Server slug
        name: String,
        /// Output file path (default: <name>.zip)
        #[arg(short = 'O', long = "out-file", value_name = "PATH")]
        out_file: Option<PathBuf>,
    },
}

#[derive(Subcommand, Debug)]
pub enum SandboxCommand {
    /// Open an interactive SSH shell in a sandbox
    Shell {
        /// Sandbox ID
        id: String,
    },
}

const PROFILE_EXAMPLES: &str = r#"Examples:
  # Put the GitHub and Linear servers in the profile "Engineering"
  $ gatana profile add-server Engineering github linear

  # Give the profile to a team, and to one account
  $ gatana profile assign Engineering --team platform
  $ gatana profile assign Engineering --account ada@example.com

  # Everyone whose identity provider sends the claim department=engineering gets the profile
  $ gatana profile claims add Engineering department=engineering

  # Save the tool settings of the profile for one server, change them, and send them back
  $ gatana profile tools Engineering github -o json > tools.json
  $ gatana profile tools Engineering github -f tools.json"#;

#[derive(Subcommand, Debug)]
pub enum ProfileCommand {
    /// Put servers in a profile
    AddServer {
        /// Profile name or ID
        profile: String,
        /// Server slugs
        #[arg(required = true, value_name = "SLUG")]
        servers: Vec<String>,
    },
    /// Take servers out of a profile, together with the tool settings of the profile for them
    RemoveServer {
        /// Profile name or ID
        profile: String,
        /// Server slugs
        #[arg(required = true, value_name = "SLUG")]
        servers: Vec<String>,
    },
    /// Give a profile to an account or a team
    Assign {
        /// Profile name or ID
        profile: String,
        #[command(flatten)]
        member: ProfileMember,
        /// Lock the assignment, so that only organization owners can remove it (organization owners only)
        #[arg(long)]
        lock: bool,
    },
    /// Take a profile away from an account or a team
    Unassign {
        /// Profile name or ID
        profile: String,
        #[command(flatten)]
        member: ProfileMember,
    },
    /// Add or remove the users who maintain a profile
    #[command(visible_alias = "maintainer")]
    Maintainers {
        #[command(subcommand)]
        command: MaintainerCommand,
    },
    /// Add or remove the identity provider claims that give a profile to everyone who has them
    #[command(visible_alias = "claim")]
    Claims {
        #[command(subcommand)]
        command: ClaimCommand,
    },
    /// Show the tool settings of a profile for one server, or replace them with -f or stdin
    Tools {
        /// Profile name or ID
        profile: String,
        /// Server slug
        server: String,
        /// JSON file with the new tool settings (omit to show the current ones, or pipe JSON to stdin)
        #[arg(short = 'f', long = "file", value_name = "PATH")]
        file: Option<PathBuf>,
    },
}

/// Who a profile goes to: one account or one team.
#[derive(Args, Debug)]
#[group(required = true, multiple = false)]
pub struct ProfileMember {
    /// The account: email address or ID
    #[arg(short = 'a', long, value_name = "ACCOUNT")]
    pub account: Option<String>,
    /// The team: name or ID
    #[arg(short = 't', long, value_name = "TEAM")]
    pub team: Option<String>,
}

#[derive(Subcommand, Debug)]
pub enum MaintainerCommand {
    /// Make a user a maintainer of the profile
    Add {
        /// Profile name or ID
        profile: String,
        /// The user: email address or ID
        account: String,
    },
    /// Remove a maintainer. The last maintainer cannot be removed
    #[command(visible_alias = "remove")]
    Rm {
        /// Profile name or ID
        profile: String,
        /// The user: email address or ID
        account: String,
    },
}

#[derive(Subcommand, Debug)]
pub enum ClaimCommand {
    /// Give the profile to everyone whose identity provider sends this claim
    Add {
        /// Profile name or ID
        profile: String,
        /// The claim and the value that gives the profile
        #[arg(value_name = "KEY=VALUE")]
        claim: String,
    },
    /// Remove a claim mapping
    #[command(visible_alias = "remove")]
    Rm {
        /// Profile name or ID
        profile: String,
        /// The claim and the value of the mapping
        #[arg(value_name = "KEY=VALUE")]
        claim: String,
    },
}

#[derive(Subcommand, Debug)]
pub enum SkillsCommand {
    /// Download and install one or more skills
    Install(InstallArgs),
    /// Update the skills in each folder. If the folder has no saved sync settings, install all
    /// skills you can access
    Sync(SyncArgs),
    /// Remove the hooks that update local skills
    RemoveHooks {
        /// The agent. Omit to remove the hook from every agent
        #[arg(value_enum)]
        agent: Option<HookAgent>,
    },
    /// Send local changes back to Gatana
    Push {
        /// SKILL.md, skill folder, or directory of skill folders. Default: claude and agents
        #[arg(value_name = "PATH")]
        paths: Vec<PathBuf>,
        /// Put the pushed skills in this collection
        #[arg(short = 'c', long = "collection", value_name = "NAME")]
        collection: Option<String>,
        /// Overwrite the server copy even when it changed after yours
        #[arg(long)]
        force: bool,
        /// Show what would be created or updated without writing
        #[arg(long = "dry-run")]
        dry_run: bool,
        /// Organization from the config file, instead of the default
        #[arg(long = "org", value_name = "ID")]
        org: Option<String>,
    },
    /// List the skills you can access
    Ls {
        /// Filter skills by text in their name or description
        #[arg(short = 'q', long = "query", value_name = "TEXT")]
        query: Option<String>,
        /// Show only skills in this collection
        #[arg(short = 'c', long = "collection", value_name = "NAME")]
        collection: Option<String>,
        /// List the collections instead of the skills
        #[arg(long)]
        collections: bool,
        /// Organization from the config file, instead of the default
        #[arg(long = "org", value_name = "ID")]
        org: Option<String>,
    },
    /// Show the hook configuration snippet
    Hook {
        /// The agent
        #[arg(value_enum)]
        agent: HookAgent,
        /// Write the hook into the agent's configuration instead of printing it
        #[arg(long)]
        install: bool,
    },
}

#[derive(Args, Debug)]
pub struct InstallArgs {
    /// The collection or skill name. Omit to install all
    pub name: Option<String>,
    /// Directories or preset names (claude, agents, hermes). Omit to install into the default agent folders
    #[arg(value_name = "TARGET")]
    pub targets: Vec<String>,
    /// Show what would change without writing
    #[arg(long = "dry-run")]
    pub dry_run: bool,
    /// Keep skills locally that are removed from Gatana
    #[arg(long = "no-prune")]
    pub no_prune: bool,
    /// Overwrite local edits and skills not tracked by Gatana. Allow installation into a nonempty directory
    /// or one synced from another organization
    #[arg(long)]
    pub force: bool,
    /// Clear the selected skills and collections, then sync all skills you can access
    #[arg(long)]
    pub reset: bool,
    /// Treat the name as a collection if a skill has the same name
    #[arg(long, conflicts_with = "skill")]
    pub collection: bool,
    /// Treat the name as a skill if a collection has the same name
    #[arg(long)]
    pub skill: bool,
    /// Do not add the session-start hooks
    #[arg(long = "no-hooks")]
    pub no_hooks: bool,
    /// Print nothing on success; warnings and errors still go to stderr
    #[arg(long)]
    pub quiet: bool,
    /// Organization from the config file, instead of the default
    #[arg(long = "org", value_name = "ID")]
    pub org: Option<String>,
}

#[derive(Args, Debug)]
pub struct SyncArgs {
    /// Directories or preset names. Omit to refresh the default agent folders
    #[arg(value_name = "TARGET")]
    pub targets: Vec<String>,
    /// Show what would change without writing
    #[arg(long = "dry-run")]
    pub dry_run: bool,
    /// Keep skills locally that are removed from Gatana
    #[arg(long = "no-prune")]
    pub no_prune: bool,
    /// Overwrite local edits and skills not tracked by Gatana. Allow syncing from a different organization
    #[arg(long)]
    pub force: bool,
    /// Print nothing on success; warnings and errors still go to stderr
    #[arg(long)]
    pub quiet: bool,
    /// Organization from the config file, instead of the default
    #[arg(long = "org", value_name = "ID")]
    pub org: Option<String>,
}

#[derive(Subcommand, Debug)]
pub enum ConfigCommand {
    /// Show the organization and configuration in use
    Current,
    /// Print the token used for requests
    Token,
    /// Sign in with a browser or personal access token. Examples: gatana config login,
    /// gatana config login my-organization, gatana config login my-organization --pat gk_...
    Login {
        /// Organization ID (e.g., org123) or instance URL (e.g., https://org123.gatana.ai). For a
        /// URL, the org ID is the first hostname label. Leave it out to choose the organization in
        /// the browser; name it to log in with a code instead, e.g. over SSH.
        #[arg(value_name = "ORG_ID_OR_URL")]
        org_id_or_url: Option<String>,
        /// Personal access token (PAT). Requires an organization
        #[arg(short = 'p', long = "pat")]
        pat: Option<String>,
        /// With an organization: its base URL, for development. Without one: the base domain to
        /// sign in at (default: https://gatana.ai), e.g. the address of an on-premise install
        #[arg(short = 'b', long = "base-url")]
        base_url: Option<String>,
        /// Print the login link without opening a browser
        #[arg(long = "no-browser")]
        no_browser: bool,
    },
    /// List all configured organizations
    Ls,
    /// Set default organization
    SetDefault {
        /// ID of the organization to set as default
        org_id: String,
    },
    /// Remove an organization configuration
    Remove {
        /// ID of the organization to remove
        org_id: String,
    },
}

const INSTALL_EXAMPLES: &str = r#"Examples:
  # Connect every agent found on this machine
  $ gatana install

  # Connect only the agents you name
  $ gatana install claude codex"#;

#[derive(Args, Debug)]
pub struct InstallAgentsArgs {
    /// The agents to connect. Omit to connect every agent found on this machine
    #[arg(value_enum, value_name = "AGENT")]
    pub agents: Vec<HookAgent>,
    /// Print the sign-in link without opening a browser
    #[arg(long = "no-browser")]
    pub no_browser: bool,
    /// Overwrite local edits and skills not tracked by Gatana. Allow syncing from a different organization
    #[arg(long)]
    pub force: bool,
}

const SIGNUP_EXAMPLES: &str = r#"Examples:
  # Answer the questions in the terminal
  $ gatana signup

  # Give the answers first. Then the CLI asks only for the code from the email
  $ gatana signup --org-name "Acme Inc" --email you@acme.com

  # Without a terminal (an agent or a script): the first run sends the code and prints the
  # command that finishes the sign-up
  $ gatana signup --org-name "Acme Inc" --email you@acme.com
  $ gatana signup --org-name 'Acme Inc' --org-id acme-inc --email you@acme.com --code 123456

  # Sign up on the sign-up page in the browser
  $ gatana signup --browser"#;

#[derive(Args, Debug)]
pub struct SignupArgs {
    /// The name of the new organization
    #[arg(long = "org-name", value_name = "NAME")]
    pub org_name: Option<String>,
    /// The organization ID, the first part of its address (ID.gatana.ai). Omit to make it from the name
    #[arg(long = "org-id", value_name = "ID", conflicts_with = "browser")]
    pub org_id: Option<String>,
    /// Your email address. Gatana sends the sign-up code to it
    #[arg(long)]
    pub email: Option<String>,
    /// The code from the email. It finishes a sign-up that an earlier run started without a
    /// terminal; that run prints the full command
    #[arg(long, value_name = "CODE", conflicts_with = "browser")]
    pub code: Option<String>,
    /// Sign up on the sign-up page in the browser instead of in the terminal
    #[arg(long)]
    pub browser: bool,
    /// The base domain to sign up at (default: https://gatana.ai), e.g. the address of an
    /// on-premise install
    #[arg(short = 'b', long = "base-url")]
    pub base_url: Option<String>,
}

#[derive(Args, Debug)]
pub struct UpgradeArgs {
    /// Show the installation method and planned upgrade without making changes
    #[arg(long = "dry-run")]
    pub dry_run: bool,
}

#[derive(Subcommand, Debug)]
pub enum SchemaCommand {
    /// Server data schema
    Server,
    /// What "gatana patch account" takes
    #[command(visible_alias = "user")]
    Account,
    /// What "gatana patch profile" takes
    Profile,
    /// What "gatana patch org" takes
    #[command(visible_aliases = ["organization", "settings"])]
    Org,
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::CommandFactory;

    #[test]
    fn the_command_line_is_consistent() {
        Cli::command().debug_assert();
    }

    #[test]
    fn global_output_works_anywhere_and_variadic_flags_collect() {
        let cli = Cli::try_parse_from(["gatana", "get", "servers", "-o", "json"]).unwrap();
        assert_eq!(cli.output, Some(Format::Json));
        let cli = Cli::try_parse_from(["gatana", "tool", "srv_tool", "-a", "x=1", "y=2", "-p", "structured"]).unwrap();
        let Command::Tools(args) = cli.command else { panic!("not a tool call") };
        assert_eq!(args.arg, vec!["x=1", "y=2"]);
        assert_eq!(args.part, ToolPart::Structured);
        let cli = Cli::try_parse_from(["gatana", "skills", "install", "release", "hermes", "--no-hooks"]).unwrap();
        let Command::Skills { command: SkillsCommand::Install(args) } = cli.command else { panic!("not install") };
        assert_eq!(args.name.as_deref(), Some("release"));
        assert_eq!(args.targets, vec!["hermes"]);
        assert!(args.no_hooks);
        assert!(Cli::try_parse_from(["gatana", "skills", "install", "x", "--collection", "--skill"]).is_err());
    }

    #[test]
    fn create_server_takes_the_command_after_its_options() {
        let kind = |args: &[&str]| {
            let cli = Cli::try_parse_from(["gatana", "create", "server"].iter().chain(args)).unwrap();
            let Command::Create { resource: CreateCommand::Server { kind } } = cli.command else {
                panic!("not create server")
            };
            kind
        };
        let Some(ServerKind::Local(args)) = kind(&["local", "--slug", "gh", "npx", "-y", "@x/server", "--slug"]) else {
            panic!("not local")
        };
        assert_eq!(args.server.slug.as_deref(), Some("gh"));
        // After the command starts, every word is part of it
        assert_eq!(args.command, vec!["npx", "-y", "@x/server", "--slug"]);
        let Some(ServerKind::Remote(args)) = kind(&["remote", "mcp.example.com", "--sse"]) else {
            panic!("not remote")
        };
        assert_eq!(args.url.as_deref(), Some("mcp.example.com"));
        assert!(args.sse);
        let Some(ServerKind::BuiltIn(args)) = kind(&["built-in", "gatana-api"]) else { panic!("not built-in") };
        assert_eq!(args.id, Some(BuiltIn::GatanaApi));
        assert!(kind(&[]).is_none());
        assert!(Cli::try_parse_from(["gatana", "create", "server", "code", "--runtime", "ruby"]).is_err());
    }

    #[test]
    fn a_profile_goes_to_exactly_one_account_or_team() {
        let parse =
            |args: &[&str]| Cli::try_parse_from(["gatana", "profile", "assign", "Engineering"].iter().chain(args));
        let Command::Profile { command: ProfileCommand::Assign { member, lock, .. } } =
            parse(&["--team", "platform", "--lock"]).unwrap().command
        else {
            panic!("not assign")
        };
        assert_eq!(member.team.as_deref(), Some("platform"));
        assert!(member.account.is_none() && lock);
        assert!(parse(&[]).is_err());
        assert!(parse(&["--team", "platform", "--account", "ada@example.com"]).is_err());
    }

    #[test]
    fn new_resources_parse_with_their_aliases() {
        let cli =
            Cli::try_parse_from(["gatana", "create", "profile", "Sales team", "-s", "github", "-s", "linear"]).unwrap();
        let Command::Create { resource: CreateCommand::Profile(args) } = cli.command else {
            panic!("not create profile")
        };
        assert_eq!(args.servers, vec!["github", "linear"]);
        let cli = Cli::try_parse_from(["gatana", "get", "users", "--type", "service-account"]).unwrap();
        assert!(matches!(
            cli.command,
            Command::Get { resource: GetCommand::Account { kind: Some(AccountKind::ServiceAccount), .. } }
        ));
        let cli = Cli::try_parse_from(["gatana", "delete", "token", "ci", "--account", "bot"]).unwrap();
        assert!(matches!(cli.command, Command::Delete { resource: DeleteCommand::Pat { .. } }));
        assert!(Cli::try_parse_from(["gatana", "get", "pats"]).is_err());
        let cli = Cli::try_parse_from(["gatana", "patch", "settings", "--logo", "logo.png"]).unwrap();
        let Command::Patch { resource: PatchCommand::Org { logo, input, .. } } = cli.command else {
            panic!("not patch org")
        };
        assert_eq!(logo.as_deref(), Some(std::path::Path::new("logo.png")));
        assert!(input.patch.is_empty());
        assert!(Cli::try_parse_from(["gatana", "patch", "org", "--logo", "a.png", "--remove-logo"]).is_err());
    }
}
