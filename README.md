<div align="center">
  <img alt="Gatana Logo" height="86" src="https://gatana.gatana.ai/favicon-prod.png" width="86">
  <h1 align="center"><b>gatana</b></h1>
  <p align="center">🚀 CLI and JavaScript SDK for managing Gatana</p>
</div>
<br/>

<p align="center">
  <a href="https://opensource.org/license/mit" rel="nofollow"><img src="https://img.shields.io/github/license/gatana-ai/gatana-js" alt="MIT License"></a>
  <a href="https://www.npmjs.com/package/gatana-sdk" rel="nofollow"><img src="https://img.shields.io/npm/v/gatana-sdk?label=gatana-sdk" alt="gatana-sdk on npm" /></a>
  <a href="https://www.npmjs.com/package/gatana" rel="nofollow"><img src="https://img.shields.io/npm/v/gatana?label=gatana%20(cli)" alt="gatana CLI on npm" /></a>
</p>

<p align="center">
  <a href="https://gatana.ai">Homepage</a>
  <span>&nbsp;•&nbsp;</span>
  <a href="https://docs.gatana.ai/">Documentation</a>
  <span>&nbsp;•&nbsp;</span>
  <a href="https://discord.gg/6TvjvmSP">Discord</a>
  <span>&nbsp;•&nbsp;</span>
  <a href="https://github.com/gatana-ai/gatana-python">Python SDK & LangChain Sandbox</a>
</p>

<br/>

This monorepo contains two packages:

| Package                             | npm                      | Description                                  |
| ----------------------------------- | ------------------------ | -------------------------------------------- |
| [`gatana-sdk`](packages/gatana-js) | `npm install gatana-sdk` | JavaScript/TypeScript SDK for the Gatana API |
| [`gatana`](packages/gatana-cli)     | `npm install -g gatana`  | CLI tool for managing Gatana                 |

The CLI source in this repository is a Rust port (`packages/gatana-cli`) and is not released yet.
`npm install -g gatana` installs the last TypeScript release (3.4.3), whose source was removed from
this repository.

For configuration, you can prepare a file at `~/.gatana.config`, see [Config File](#config-file) for details. You can override configuration using environment variables or by passing options directly in the SDK.

---

## Table of Contents

- [Install](#install)
- [CLI Tool Example](#cli-tool-example)
- [SDK Example](#sdk-example)
- [Syntax](#syntax)
- [Global Options](#global-options)
- [Commands](#commands)
  - [Basic Commands](#basic-commands)
  - [Server Management](#server-management)
  - [Utility Commands](#utility-commands)
- [Resource Types](#resource-types)
- [Examples](#examples)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Config File](#config-file)
- [SDK](#sdk)
  - [Custom Authentication](#custom-authentication)
  - [V2 API Client](#v2-api-client)
  - [Exports](#exports)
- [Development](#development)
- [Debugging](#debugging)
- [License](#license)
- [Contributing](#contributing)

---

## Install

```bash
# SDK (for use in your own projects)
npm install gatana-sdk

# CLI (global)
npm install -g gatana
```

## CLI Tool Example

```bash
gatana config login ORG_ID
gatana get servers
```

## SDK Example

```typescript
import { Gatana } from 'gatana-sdk';

// Env varaibles: GATANA_API_KEY and GATATA_ORG_ID
// Or, ~/.gatana.config

const client = new Gatana();
const servers = await client.api.listMcpServers();
```

## Syntax

Use the following syntax to run `gatana` commands from your terminal:

```
gatana [command] [resource] [name] [flags]
```

where `command`, `resource`, `name`, and `flags` are:

- `command`: The operation to perform — `get`, `create`, `describe`, `delete`, `patch`.
- `resource`: The target resource type — `server`, `tool`, `creds` (credentials).
- `name`: The name or identifier of the resource. If omitted, all resources of that type are listed.
- `flags`: Optional flags such as `-o json`, `-f file.json`, `-s server-slug`. Flags are specific to each command.

> **Example:** The following commands are equivalent ways to list servers:
>
> ```bash
> gatana get server
> gatana get servers
> ```

## Global Options

| Flag                    | Description              | Values                            |
| ----------------------- | ------------------------ | --------------------------------- |
| `-o, --output <format>` | Output format            | `json`, `yaml`, `table` (default) |
| `-V, --version`         | Print version            |                                   |
| `-h, --help`            | Display help for command |                                   |

The default table format uses kubectl-style rendering: uppercase headers, no borders, and auto-width columns.

---

## Commands

### Basic Commands

Operations on core resources (servers, tools, credentials).

| Command             | Syntax                                                        | Description                                                |
| ------------------- | ------------------------------------------------------------- | ---------------------------------------------------------- |
| **get server**      | `gatana get server [name]`                                    | List all servers or get a specific server by slug          |
| **get tool**        | `gatana get tool [name] [--enabled]`                          | List all tools or get a specific tool's schema             |
| **get creds**       | `gatana get creds [id] -s <slug>`                             | List credentials for a server, or get one by ID            |
| **describe server** | `gatana describe server <name>`                               | Show deployment status, tools, audit logs, and credentials |
| **create server**   | `gatana create server [-n name] [-t type]`                    | Create a new server (interactive prompts if flags omitted) |
| **create creds**    | `gatana create creds <slug> [-f file] [--scope user\|server]` | Create or replace credentials for a server                 |
| **delete server**   | `gatana delete server <name>`                                 | Delete a server                                            |
| **delete creds**    | `gatana delete creds [id] -s <slug> [--all]`                  | Delete one or all credentials for a server                 |
| **patch server**    | `gatana patch server <slug> [-p kv...] [-f file]`             | JSON Merge Patch (RFC 7396) a server                       |

> **Transport types** for `create server -t`: `hosted`, `stdio`, `httpstreaming`, `sse`

### Server Management

Commands for deployments, tools, hosted server lifecycle, and credentials.

| Command                 | Syntax                                                               | Description                                                    |
| ----------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------- |
| **tool**                | `gatana tool <name> [-a kv...] [-f file]`                            | Call a tool by its universal name (`serverSlug_toolName`)      |
| **deploy get**          | `gatana deploy get <name>`                                           | Get deployment status of a server                              |
| **deploy logs**         | `gatana deploy logs <name> [--id <deploymentId>]`                    | Get logs of a running server deployment                        |
| **deploy wait**         | `gatana deploy wait <name> [--timeout 10m]`                          | Wait for deployment to finish                                  |
| **deploy stop**         | `gatana deploy stop <name>`                                          | Stop a server deployment                                       |
| **deploy start**        | `gatana deploy start <name> [--wait]`                                | Start a server deployment                                      |
| **hosted init**         | `gatana hosted init [path]`                                          | Scaffold a new hosted server from a template                   |
| **hosted local-verify** | `gatana hosted local-verify <path>`                                  | Verify local source code (checks `index.js` + `schema` export) |
| **hosted local-run**    | `gatana hosted local-run <path> <tool> [-i json] [-f file] [-p k=v]` | Test a tool locally without deploying                          |
| **hosted upload**       | `gatana hosted upload <name> [path] [--create] [--force]`            | Upload source code, deploy, and wait for stabilization         |
| **hosted download**     | `gatana hosted download <name> [-o path]`                            | Download deployed source code as a zip                         |
| **creds**               | `gatana creds <slug> [--cred-id <id>]`                               | Get the effective (resolved) credentials/token for a server    |

### Skills

Install the skills of your organization into the folders AI agents read, and push local changes back. See the [skills documentation](https://docs.gatana.ai/skills) for the full story.

| Command                 | Syntax                                                                                                                                          | Description                                                                                                                                                                                                                                                 |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **skills install**      | `gatana skills install [name] [target...] [--dry-run] [--no-prune] [--force] [--reset] [--no-hooks] [--quiet]` | Write the skills you can read as `<dir>/<name>/SKILL.md`: every skill, what the targets follow, or one collection or skill by name, which the targets follow from then on. Installs the session-start hooks (`--no-hooks` skips them). Targets: `claude`, `agents`, `hermes`, or a path |
| **skills sync**         | `gatana skills sync [target...] [--dry-run] [--no-prune] [--force] [--quiet]` | Refresh what each folder follows, as the session-start hooks do. A folder nothing was installed into gets every skill you can read |
| **skills remove-hooks** | `gatana skills remove-hooks [agent]`                                                                                                            | Remove the session-start hooks again: every agent found on this machine, or one                                                                                                                                                                             |
| **skills push**         | `gatana skills push [path...] [-c collection] [--force] [--dry-run]`                                                                            | Send local changes back. Default: every skill in `claude` and `agents` that changed on this machine; conflicts are printed and left alone                                                                                                                   |
| **skills ls**           | `gatana skills ls [-q text] [-c collection] [--collections]`                                                                                    | List the skills you can read, or the collections you can see                                                                                                                                                                                                |
| **skills hook**         | `gatana skills hook <claude\|codex\|hermes\|openclaw> [--install]`                                                                              | Print, or install, the configuration that runs `gatana skills sync --quiet` when an agent session starts                                                                                                                                                                 |
| **get skill**           | `gatana get skill [name] [-q text]`                                                                                                             | List skills, or show one with its instructions                                                                                                                                                                                                              |
| **describe skill**      | `gatana describe skill <name>`                                                                                                                  | Show a skill with its instructions                                                                                                                                                                                                                          |

> **Targets** for `skills install`: `claude` = `~/.claude/skills` (Claude Code), `agents` = `~/.agents/skills` (Codex, Cursor, Gemini CLI, OpenCode, Copilot, Amp), `hermes` = `~/.hermes/skills`. Default: `claude` and `agents`. Folders the install did not create are never touched, and a locally edited `SKILL.md` is not overwritten until it is pushed. What a directory follows is stored in its `.gatana-skills.json`, so the session-start hook keeps following it; `--reset` resets it. All skills commands accept `--org <id>`.

### Utility Commands

Configuration, authentication, and introspection.

| Command                | Syntax                                                       | Description                                          |
| ---------------------- | ------------------------------------------------------------ | ---------------------------------------------------- |
| **config show**        | `gatana config show`                                         | Show current configuration (base URL, token)         |
| **config token**       | `gatana config token`                                        | Print the token that would be used for requests      |
| **config login**       | `gatana config login <org-id> [-b base-url]`                 | Login via OIDC device authorization flow             |
| **config set-api-key** | `gatana config set-api-key -t <key> -o <org-id> [--default]` | Set an API key for an organization                   |
| **config ls**          | `gatana config ls`                                           | List all configured organizations                    |
| **config set-default** | `gatana config set-default <org-id>`                         | Set the default organization                         |
| **config remove**      | `gatana config remove <org-id>`                              | Remove an organization from config                   |
| **auth-info**          | `gatana auth-info`                                           | Display authenticated user and organization info     |
| **schema server**      | `gatana schema server`                                       | Print the resolved OpenAPI schema for the Server DTO |

---

## Resource Types

| Resource      | Aliases   | Description                            |
| ------------- | --------- | -------------------------------------- |
| `server`      | `servers` | MCP server registrations               |
| `tool`        | `tools`   | Tools exposed by servers               |
| `credentials` | `creds`   | Authentication credentials for servers |
| `skill`       | `skills`  | Markdown instructions agents follow    |

---

## Examples

### Getting Started

```bash
# Install and log in
npm install -g gatana
gatana config login my-org

# Verify your identity
gatana auth-info

# List your servers
gatana get servers
```

### Managing Servers

```bash
# Create a new hosted server (interactive)
gatana create server

# Create with flags
gatana create server -n my-server -t hosted

# View server details
gatana describe server my-server

# Patch a server using dot-notation
gatana patch server my-server -p description="Updated description"
gatana patch server my-server -p isEnabled=false -p oauthMetadata.as.deviceAuthorizationEndpoint="https://auth.example.com/device"

# Patch from a JSON file
gatana patch server my-server -f patch.json

# Patch from stdin
echo '{"description": "Piped"}' | gatana patch server my-server

# Delete a server
gatana delete server my-server
```

### Hosted Server Lifecycle

```bash
# Scaffold a new server directory
gatana hosted init ./my-server

# Verify the source code locally
gatana hosted local-verify ./my-server

# Test a tool locally before deploying
gatana hosted local-run ./my-server my_tool -p input="hello"

# Upload, deploy, and wait for stabilization
gatana hosted upload my-server ./my-server --create

# View deployment logs
gatana deploy logs my-server

# Wait for deployment to finish (with timeout)
gatana deploy wait my-server --timeout 5m

# Download the deployed source code
gatana hosted download my-server -o my-server.zip

# Stop and start deployments
gatana deploy stop my-server
gatana deploy start my-server --wait
```

### Calling Tools

```bash
# List all tools
gatana get tools

# List only enabled tools
gatana get tools --enabled

# View a specific tool's schema
gatana get tool serverSlug_toolName

# Call a tool with dot-notation arguments
gatana tool my_server_search -a query="hello world" -a limit=10

# Call a tool with inline JSON
gatana tool my_server_search -a '{"query": "hello world", "limit": 10}'

# Call a tool from a JSON file
gatana tool my_server_search -f args.json

# Call a tool from stdin
echo '{"query": "hello"}' | gatana tool my_server_search
```

### Credentials

```bash
# Create credentials for a server (auto-detects OAuth vs API key)
gatana create creds my-server

# Create credentials from a file
gatana create creds my-server -f creds.json

# List credentials for a server
gatana get creds -s my-server

# Get effective (resolved) credentials
gatana creds my-server

# Delete all credentials for a server
gatana delete creds -s my-server --all
```

### Multi-Org Configuration

```bash
# Log in to multiple organizations
gatana config login org-one
gatana config login org-two

# List configured organizations
gatana config ls

# Switch default organization
gatana config set-default org-two

# Set an API key for an organization
gatana config set-api-key -t sk-abc123 -o my-org --default

# Remove an organization
gatana config remove org-one
```

### Skills

```bash
# Write every skill you can read into ~/.claude/skills and ~/.agents/skills
gatana skills install

# Only Hermes, or any directory
gatana skills install hermes
gatana skills install ./team-skills

# One collection or one skill; the targets follow it from then on
gatana skills install release-engineering
gatana skills install deploy-checklist

# Every install adds the session-start hooks of the agents on this machine
# (Claude Code, Codex, Hermes, OpenClaw); they run "gatana skills sync --quiet"
gatana skills install --no-hooks   # skip the hooks
gatana skills remove-hooks         # take them out again, or: remove-hooks claude

# Refresh by hand what the folders follow, or print a hook to paste
gatana skills sync
gatana skills hook claude   # paste the output into .claude/settings.json

# Edit any installed SKILL.md, then send everything that changed on this machine back.
# A skill that also changed on the server is printed as a conflict and left alone.
gatana skills push

# Or one skill
gatana skills push ~/.claude/skills/release-checklist

# Create a skill from a hand-written SKILL.md
gatana skills push ./my-skill/SKILL.md
```

### Output Formats

```bash
# Default table output
gatana get servers

# JSON output
gatana get servers -o json

# YAML output
gatana describe server my-server -o yaml
```

---

## Configuration

`gatana` resolves authentication in the following order:

1. **Passed options** (SDK only) — `apiKey` + `orgId` or `baseUrl`
2. **Environment variables** — `GATANA_API_KEY` + `GATANA_ORG_ID` (or `GATANA_BASE_URL`)
3. **Config file** `~/.gatana.config` — API key or OIDC tokens per organization

### Environment Variables

| Variable          | Description                                            |
| ----------------- | ------------------------------------------------------ |
| `GATANA_API_KEY`  | API key for authentication                             |
| `GATANA_ORG_ID`   | Organization ID (derives `https://<org-id>.gatana.ai`) |
| `GATANA_BASE_URL` | Override the base URL directly                         |

### Config File

The config file at `~/.gatana.config` supports multiple organizations:

```json
{
  "orgs": {
    "my-org": {
      "baseUrl": "https://my-org.gatana.ai",
      "apiKey": "sk-...",
      "tokens": {
        "access_token": "...",
        "refresh_token": "...",
        "expires_at": 1234567890
      }
    }
  },
  "defaultOrgId": "my-org"
}
```

Authentication methods per organization:

- **API key** — set via `gatana config set-api-key` or directly in the config file
- **OIDC tokens** — set via `gatana config login`, automatically refreshed when expired

---

## SDK

The SDK is published as a separate package, [`gatana-sdk`](https://www.npmjs.com/package/gatana-sdk):

```bash
npm install gatana-sdk
```

```typescript
import { Gatana } from 'gatana-sdk';

const client = new Gatana();
const servers = await client.api.listMcpServers();
```

### Custom Authentication

Provide a `ConfigLoader` or explicit options:

```typescript
import { Gatana, ConfigLoader, OptionsConfigStrategy } from 'gatana-sdk';

// Using options
const client = new Gatana({
  configLoader: new ConfigLoader([
    new OptionsConfigStrategy({ apiKey: 'sk-...', orgId: 'my-org' })
  ])
});

// Using a custom config loader
const client = new Gatana({
  configLoader: {
    getConfig(): { baseUrl: string; token: () => Promise<string> }
  }
});
```

### V2 API Client

A `Gatana2` client is also exported for the newer REST-style API (v2):

```typescript
import { Gatana2 } from 'gatana-sdk';
```

### Exports

| Export                  | Description                                           |
| ----------------------- | ----------------------------------------------------- |
| `Gatana`                | V1 API client — wraps the generated SDK at `/api/v1/` |
| `Gatana2`               | V2 API client — REST-style API at `/api/v2/`          |
| `ConfigLoader`          | Chains config strategies in priority order            |
| `ConfigStrategy`        | Abstract base class for auth strategies               |
| `OptionsConfigStrategy` | Auth from explicit `{ apiKey, orgId }` options        |
| `EnvConfigStrategy`     | Auth from environment variables                       |
| `FileConfigStrategy`    | Auth from `~/.gatana.config` (supports token refresh) |

---

## Development

This is a pnpm monorepo. Use [just](https://github.com/casey/just) to run common tasks:

```bash
just build          # Build the SDK
just dev            # Watch the SDK for changes
just test           # Run the SDK tests
just generate       # Regenerate API clients from OpenAPI specs
just fmt            # Format code with prettier
just release        # Interactive SDK release with change detection
just rs-build       # Build the Rust CLI
just rs-test        # Test, lint and format-check the Rust CLI
just rs-release     # Release the Rust CLI to GitHub, npm and Homebrew
```

See [packages/gatana-cli/README.md](packages/gatana-cli/README.md) for the Rust CLI.

### Project Structure

```
packages/
  gatana-sdk/   # JavaScript/TypeScript SDK (npm: gatana-sdk)
  gatana-cli/   # CLI, written in Rust (not released yet)
scripts/
  release.sh    # Interactive release script
```

---

## Debugging

The SDK and CLI use the `debug` package for logging. Enable debug output with:

```bash
# General debug output
DEBUG=gatana node your-script.js

# HTTP request/response traces
DEBUG=gatana:http node your-script.js
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

## Contributing

We welcome contributions!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request
