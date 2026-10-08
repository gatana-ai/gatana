//! The command line: every command, flag and help text.

use crate::output::Format;
use crate::skills::hooks::HookAgent;
use clap::{Args, Parser, Subcommand, ValueEnum};
use std::path::PathBuf;

const ROOT_HELP: &str = "\
{about-with-newline}
{usage-heading} {usage}

Basic Commands:
  get           Display one or many resources
  describe      Show details of a specific resource
  create        Create a resource
  delete        Delete resources
  patch         Patch a resource

Server Management:
  tools         Call a tool (alias: tool)
  deployment    Manage server deployments (alias: deploy)
  creds         Get the effective credentials for a server
  hosted        Manage hosted servers (FaaS)
  sandbox       Manage sandboxes (requires early access)

Skills:
  skills        Install your organization's skills for AI agents, and push changes back

Utility Commands:
  config        Show and change the configuration; log in
  auth-info     Display info about the authenticated user
  schema        Print OpenAPI resource schemas
  help          Print this message or the help of the given subcommand(s)

Options:
{options}{after-help}";

#[derive(Parser, Debug)]
#[command(
    name = "gatana",
    version,
    about = "CLI tool for Gatana - AI agent management and querying",
    help_template = ROOT_HELP,
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
    /// Display one or many resources
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
    /// Manage hosted servers (FaaS)
    Hosted {
        #[command(subcommand)]
        command: HostedCommand,
    },
    /// Manage sandboxes (requires early access)
    Sandbox {
        #[command(subcommand)]
        command: SandboxCommand,
    },
    /// Install the skills of your organization into the folders AI agents read, follow collections,
    /// and push local changes back
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
    /// Display info about the authenticated user
    AuthInfo,
    /// Print OpenAPI resource schemas
    Schema {
        #[command(subcommand)]
        command: SchemaCommand,
    },
}

const CONFIG_ABOUT: &str = "Show configuration requirements and current status. Available configuration strategies:

* EnvConfigStrategy: Provide configuration via environment variables. Required: GATANA_API_KEY and either GATANA_ORG_ID or GATANA_BASE_URL. Example: export GATANA_API_KEY=your_api_key; export GATANA_ORG_ID=your_org_id
* FileConfigStrategy: Provide configuration via a local config file (~/.gatana.config). Use the \"gatana config\" commands to manage this configuration. The CLI will look for the default organization in the config file or use the org specified by GATANA_ORG_ID env var.";

#[derive(Subcommand, Debug)]
pub enum GetCommand {
    /// Get server(s)
    #[command(visible_alias = "servers")]
    Server {
        /// Server slug (omit to list all)
        name: Option<String>,
    },
    /// Get tool(s)
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
        /// Resolve effective credentials (e.g. using refresh token)
        #[arg(short = 'e', long = "with-effective")]
        with_effective: bool,
    },
    /// Get sandbox(es)
    #[command(visible_alias = "sandboxes")]
    Sandbox {
        /// Sandbox ID (omit to list all)
        id: Option<String>,
        /// Also include archived sandboxes
        #[arg(long)]
        all: bool,
    },
    /// Get skill(s)
    #[command(visible_alias = "skills")]
    Skill {
        /// Skill name (omit to list all)
        name: Option<String>,
        /// Only skills whose name or description contains the text
        #[arg(short = 'q', long = "query", value_name = "TEXT")]
        query: Option<String>,
    },
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
}

#[derive(Clone, Copy, Debug, ValueEnum)]
pub enum TransportType {
    Hosted,
    Stdio,
    Httpstreaming,
    Sse,
}

#[derive(Clone, Copy, Debug, ValueEnum)]
pub enum CredentialScope {
    User,
    Server,
}

#[derive(Subcommand, Debug)]
pub enum CreateCommand {
    /// Create a new server
    Server {
        /// Server slug
        #[arg(short = 's', long = "slug")]
        slug: Option<String>,
        /// Transport type
        #[arg(short = 't', long = "transport-type", value_enum, value_name = "TYPE")]
        transport_type: Option<TransportType>,
    },
    /// Create or replace credentials for a server. The credential type (oauth/apikey) is inferred from
    /// the server config. For OAuth, omit -f to get an authorize URL, or provide -f to file upload a
    /// token-set, or use stdin as JSON. For API keys, provide keys via -f or stdin as JSON:
    /// [["header","value"], …]
    #[command(visible_alias = "creds")]
    Credentials {
        /// Server slug
        server_slug: String,
        /// JSON file with credentials
        #[arg(short = 'f', long = "file", value_name = "PATH")]
        file: Option<PathBuf>,
        /// Credential scope. If omitted will default to servers default credential scope
        #[arg(long, value_enum)]
        scope: Option<CredentialScope>,
    },
    /// Create a new sandbox
    Sandbox,
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

#[derive(Subcommand, Debug)]
pub enum PatchCommand {
    /// Patch an existing server (JSON Merge Patch RFC 7396 strategy). To get the schema, run
    /// "gatana schema server".
    #[command(after_help = PATCH_EXAMPLES)]
    Server {
        /// Server slug
        server_slug: String,
        /// JSON file with server config to patch (omit to read from stdin)
        #[arg(short = 'f', long = "file", value_name = "PATH")]
        file: Option<PathBuf>,
        /// Inline patch: JSON string or dot-notation key=value pairs
        #[arg(short = 'p', long = "patch", value_name = "KV", num_args = 1.., action = clap::ArgAction::Append)]
        patch: Vec<String>,
    },
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
    /// JSON file with argument (omit to read from stdin)
    #[arg(short = 'f', long = "file", value_name = "PATH")]
    pub file: Option<PathBuf>,
    /// Inline argument: JSON string or dot-notation key=value pairs
    #[arg(short = 'a', long = "arg", value_name = "KV", num_args = 1.., action = clap::ArgAction::Append)]
    pub arg: Vec<String>,
    /// Output part of the raw response
    #[arg(short = 'p', long = "part", value_enum, default_value = "text")]
    pub part: ToolPart,
}

#[derive(Subcommand, Debug)]
pub enum DeploymentCommand {
    /// Gets the deployment status of a server
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
        /// The length of time to wait before giving up, like 1m30s
        #[arg(long, value_name = "DURATION", default_value = "10m")]
        timeout: String,
    },
    /// Stops a server's deployment. Unless disabled, Gatana will start it automatically again if a
    /// tool call comes in
    Stop {
        /// Server slug
        name: String,
    },
    /// Starts a server's deployment
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
pub enum HostedCommand {
    /// Initialize a new hosted server source-code directory with a template
    Init {
        /// Path to the source-code directory
        #[arg(default_value = ".")]
        path: PathBuf,
    },
    /// Verify local source-code (needs Node.js)
    Verify {
        /// Path to the source-code directory
        path: PathBuf,
    },
    /// Call a tool in the local source-code for testing (needs Node.js)
    Run {
        /// Path to the source-code directory. Use . for current directory
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
    /// Upload new source-code
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
    /// Download the deployed source-code as a zip file
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
    /// Open an interactive SSH shell into a sandbox
    Shell {
        /// Sandbox ID
        id: String,
    },
}

#[derive(Subcommand, Debug)]
pub enum SkillsCommand {
    /// Download and install one or more skills
    Install(InstallArgs),
    /// Refresh the skills in each folder, as the session-start hooks do. A folder nothing was
    /// installed into gets every skill you can read.
    Sync(SyncArgs),
    /// Uninstall any hooks that keep your local skills up-to-date
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
    /// List the skills you can read
    Ls {
        /// Only skills whose name or description contains the text
        #[arg(short = 'q', long = "query", value_name = "TEXT")]
        query: Option<String>,
        /// Only the skills in this collection
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
    /// Skip safe-guards: overwrite non-Gatana skills, and install into a directory that is not empty
    /// or is synced from another organization
    #[arg(long)]
    pub force: bool,
    /// Forget any previous state. Download and re-install every skill you can read again
    #[arg(long)]
    pub reset: bool,
    /// Only if name is provided: if a skill and a collection share the name, use the collection
    #[arg(long, conflicts_with = "skill")]
    pub collection: bool,
    /// Only if name is provided: if a skill and a collection share the name, use the skill
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
    /// Skip safe-guards: overwrite locally edited and non-Gatana skills
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
    /// Show resolved organization and configuration
    Current,
    /// Print the token which would be used for any request
    Token,
    /// Log in with a personal access token or in the browser. Examples: gatana config login
    /// my-organization, gatana config login https://my-organization.gatana.ai
    Login {
        /// Organization ID (e.g., org123) or instance URL (e.g., https://org123.gatana.ai). For a
        /// URL, the org ID is the first hostname label.
        #[arg(value_name = "ORG_ID_OR_URL")]
        org_id_or_url: String,
        /// Personal Access Token (PAT) for authentication
        #[arg(short = 'p', long = "pat")]
        pat: Option<String>,
        /// Base URL (default: none) - experimental - hardcodes the base URL for development purposes only
        #[arg(short = 'b', long = "base-url")]
        base_url: Option<String>,
        /// Print the login link without opening a browser, e.g. over SSH
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

#[derive(Subcommand, Debug)]
pub enum SchemaCommand {
    /// Server DTO
    Server,
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
}
