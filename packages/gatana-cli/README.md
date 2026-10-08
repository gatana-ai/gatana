# gatana CLI

The `gatana` CLI manages the servers, tools, credentials, sandboxes and skills of a Gatana
organization. It is a native binary for macOS and Linux (arm64 and x64), written in Rust.

Version 4 is a port of the TypeScript CLI (3.x) to Rust. It reads and writes the same
`~/.gatana.config` and the same skills folders, so you can update without a new login. See
[Changes from the TypeScript CLI](#changes-from-the-typescript-cli).

---

## Table of contents

- [Install](#install)
- [Quick start](#quick-start)
- [Syntax](#syntax)
- [Global options](#global-options)
- [Commands](#commands)
- [Resource types](#resource-types)
- [Examples](#examples)
- [Development](#development)
- [Changes from the TypeScript CLI](#changes-from-the-typescript-cli)
- [Releasing](#releasing)
- [Not done yet](#not-done-yet)

---

## Install

```bash
npm install -g gatana
brew install gatana-ai/tap/gatana
curl -fsSL https://github.com/gatana-ai/gatana/releases/latest/download/install.sh | sh
```

npm installs the binary for your machine from an optional dependency, `@gatana/cli-<os>-<cpu>`.

`install.sh` puts the binary in `~/.local/bin`. Set `GATANA_INSTALL_DIR` to use a different folder,
and `GATANA_VERSION` to install a given version.

## Quick start

```bash
gatana config login my-org
gatana auth-info
gatana get servers
```

`config login` opens the browser. Add `--pat <token>` to log in with a personal access token, or
`--no-browser` to print the link, for example over SSH.

The CLI also reads `GATANA_API_KEY` and `GATANA_ORG_ID`. See
[Configuration](../../README.md#configuration) for the order in which it reads the credentials.

## Syntax

```
gatana [command] [resource] [name] [flags]
```

- `command`: the operation, for example `get`, `create`, `describe`, `delete` or `patch`.
- `resource`: the resource type, for example `server`, `tool` or `creds`.
- `name`: the name or ID of the resource. Omit it to list all resources of that type.
- `flags`: options such as `-o json`, `-f file.json` or `-s server-slug`. Each command has its own
  flags.

The singular and plural forms of a resource are the same command:

```bash
gatana get server
gatana get servers
```

## Global options

| Flag                    | Description              | Values                            |
| ----------------------- | ------------------------ | --------------------------------- |
| `-o, --output <format>` | Output format            | `json`, `yaml`, `table` (default) |
| `-V, --version`         | Print the version        |                                   |
| `-h, --help`            | Print help for a command |                                   |

The table format has uppercase headers, no borders and columns as wide as their content, as in
`kubectl`. With `-o json` or `-o yaml`, stdout holds only the result. Progress lines go to stderr.

---

## Commands

### Basic commands

Operations on servers and credentials.

| Command             | Syntax                                                        | Description                                                     |
| ------------------- | ------------------------------------------------------------- | --------------------------------------------------------------- |
| **get server**      | `gatana get server [name]`                                    | List all servers, or get one server by its slug                 |
| **get tool**        | `gatana get tool [name] [--enabled]`                          | List all tools, or get the schema of one tool                   |
| **get creds**       | `gatana get creds [id] -s <slug> [-e]`                        | List the credentials of a server, or get one by its ID          |
| **describe server** | `gatana describe server <name>`                               | Show the deployment status and the tools of a server            |
| **create server**   | `gatana create server [-s slug] [-t type]`                    | Create a server. Asks for the values that the flags do not give |
| **create creds**    | `gatana create creds <slug> [-f file] [--scope user\|server]` | Create or replace the credentials of a server                   |
| **delete server**   | `gatana delete server <name>`                                 | Delete a server                                                 |
| **delete creds**    | `gatana delete creds <id> -s <slug>`                          | Delete one credential of a server                               |
| **patch server**    | `gatana patch server <slug> [-p kv...] [-f file]`             | Change a server with a JSON Merge Patch (RFC 7396)              |

> **Transport types** for `create server -t`: `hosted`, `stdio`, `httpstreaming`, `sse`.
>
> **Credential types**: `create creds` gets the type (OAuth or API key) from the server. For OAuth,
> omit `-f` to get an authorize URL, or give a token set with `-f` or on stdin. For API keys, give
> `[["header","value"], …]` with `-f` or on stdin.

### Server management

Deployments, tool calls, hosted servers and effective credentials.

| Command             | Syntax                                                                            | Description                                                            |
| ------------------- | --------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **tool**            | `gatana tool <name> [-a kv...] [-f file] [-p part]`                               | Call a tool by its universal name (`serverSlug_toolName`)              |
| **deploy get**      | `gatana deploy get <name>`                                                        | Get the deployment status of a server                                  |
| **deploy logs**     | `gatana deploy logs <name> [-f] [-p] [--id <deploymentId>]`                       | Show the logs of a stdio or hosted server                              |
| **deploy wait**     | `gatana deploy wait <name> [--timeout 10m]`                                       | Wait until the deployment is ready                                     |
| **deploy stop**     | `gatana deploy stop <name>`                                                       | Stop a deployment. The next tool call starts it again, if enabled      |
| **deploy start**    | `gatana deploy start <name> [--wait]`                                             | Start a deployment                                                     |
| **hosted init**     | `gatana hosted init [path]`                                                       | Make a new hosted server folder from a template                        |
| **hosted verify**   | `gatana hosted verify <path>`                                                     | Verify the local source code (needs Node.js)                           |
| **hosted run**      | `gatana hosted run <path> <tool> [-i json] [-f file] [-p k=v]`                    | Call a tool in the local source code, without a deploy (needs Node.js) |
| **hosted upload**   | `gatana hosted upload <name> [path] [--create] [--no-wait] [--no-logs] [--force]` | Upload the source code, deploy it and wait until it is ready           |
| **hosted download** | `gatana hosted download <name> [-O file]`                                         | Download the deployed source code as a zip file                        |
| **creds**           | `gatana creds <slug> [--cred-id <id>]`                                            | Get the effective credentials or token of a server                     |

> `tool` reads its arguments from stdin when you give neither `-a` nor `-f`. `-p` selects the part
> of the response to print: `text` (default), `structured` or `unstructured`.

### Sandboxes

Sandboxes need early access.

| Command            | Syntax                            | Description                                                     |
| ------------------ | --------------------------------- | --------------------------------------------------------------- |
| **get sandbox**    | `gatana get sandbox [id] [--all]` | List the sandboxes, or get one. `--all` adds archived sandboxes |
| **create sandbox** | `gatana create sandbox`           | Create a sandbox                                                |
| **delete sandbox** | `gatana delete sandbox <id>`      | Delete a sandbox                                                |
| **sandbox shell**  | `gatana sandbox shell <id>`       | Open an interactive SSH shell in a sandbox                      |

### Skills

Install the skills of your organization into the folders that AI agents read, and push local
changes back. See the [skills documentation](https://docs.gatana.ai/skills) for the full story.

| Command                 | Syntax                                                                                                         | Description                                                                                                                                                                                                                                                     |
| ----------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **skills install**      | `gatana skills install [name] [target...] [--dry-run] [--no-prune] [--force] [--reset] [--no-hooks] [--quiet]` | Write the skills you can read as `<dir>/<name>/SKILL.md`. Without a name: every skill, or what the targets follow. With a name: one collection or skill, which the targets follow from then on. Also installs the session-start hooks (`--no-hooks` skips them) |
| **skills sync**         | `gatana skills sync [target...] [--dry-run] [--no-prune] [--force] [--quiet]`                                  | Refresh what each folder follows, as the session-start hooks do. A folder without an install gets every skill you can read                                                                                                                                      |
| **skills remove-hooks** | `gatana skills remove-hooks [agent]`                                                                           | Remove the session-start hooks: from every agent on this machine, or from one                                                                                                                                                                                   |
| **skills push**         | `gatana skills push [path...] [-c collection] [--force] [--dry-run]`                                           | Send local changes back. Default: every skill in `claude` and `agents` that changed on this machine. Conflicts are printed and left alone                                                                                                                       |
| **skills ls**           | `gatana skills ls [-q text] [-c collection] [--collections]`                                                   | List the skills you can read, or the collections you can see                                                                                                                                                                                                    |
| **skills hook**         | `gatana skills hook <claude\|codex\|hermes\|openclaw> [--install]`                                             | Print, or install, the configuration that runs `gatana skills sync --quiet` when an agent session starts                                                                                                                                                        |
| **get skill**           | `gatana get skill [name] [-q text]`                                                                            | List skills, or show one with its instructions                                                                                                                                                                                                                  |
| **describe skill**      | `gatana describe skill <name>`                                                                                 | Show a skill with its instructions                                                                                                                                                                                                                              |

> **Targets** for `skills install` and `skills sync`:
>
> - `claude` is `~/.claude/skills` (Claude Code).
> - `agents` is `~/.agents/skills` (Codex, Cursor, Gemini CLI, OpenCode, Copilot, Amp).
> - `hermes` is `~/.hermes/skills`.
> - Any other value is a path.
>
> The default targets are `claude` and `agents`. Without `--force`, the CLI does not change a folder
> that it did not create. It does not overwrite a locally edited `SKILL.md` until you push it. Each
> directory stores what it follows in its `.gatana-skills.json`, so the session-start hook keeps
> following it. `--reset` clears that state.
>
> When a skill and a collection have the same name, `--skill` or `--collection` selects one.
> `install`, `sync`, `push` and `ls` accept `--org <id>` to use an organization other than the
> default.

### Utility commands

Configuration, authentication and schemas.

| Command                | Syntax                                                        | Description                                           |
| ---------------------- | ------------------------------------------------------------- | ----------------------------------------------------- |
| **config current**     | `gatana config current`                                       | Show the resolved organization and configuration      |
| **config token**       | `gatana config token`                                         | Print the token that requests use                     |
| **config login**       | `gatana config login <org-id-or-url> [-p pat] [--no-browser]` | Log in with a personal access token or in the browser |
| **config ls**          | `gatana config ls`                                            | List all configured organizations                     |
| **config set-default** | `gatana config set-default <org-id>`                          | Set the default organization                          |
| **config remove**      | `gatana config remove <org-id>`                               | Remove an organization from the config file           |
| **auth-info**          | `gatana auth-info`                                            | Show the authenticated user and organization          |
| **schema server**      | `gatana schema server`                                        | Print the resolved OpenAPI schema of the Server DTO   |

---

## Resource types

| Resource  | Aliases                     | Description                              |
| --------- | --------------------------- | ---------------------------------------- |
| `server`  | `servers`                   | MCP server registrations                 |
| `tool`    | `tools`                     | Tools that the servers expose            |
| `creds`   | `credential`, `credentials` | Credentials for servers                  |
| `sandbox` | `sandboxes`                 | Sandboxes (early access)                 |
| `skill`   | `skills`                    | Markdown instructions that agents follow |

---

## Examples

### Get started

```bash
# Install and log in
npm install -g gatana
gatana config login my-org

# Verify your identity
gatana auth-info

# List your servers
gatana get servers
```

### Manage servers

```bash
# Create a server (interactive)
gatana create server

# Create a server with flags
gatana create server -s my-server -t hosted

# Show the details of a server
gatana describe server my-server

# Patch a server with dot-notation
gatana patch server my-server -p description="Updated description"
gatana patch server my-server -p isEnabled=false -p oauthMetadata.as.deviceAuthorizationEndpoint="https://auth.example.com/device"

# Patch from a JSON file
gatana patch server my-server -f patch.json

# Patch from stdin
echo '{"description": "Piped"}' | gatana patch server my-server

# Delete a server
gatana delete server my-server
```

### Develop a hosted server

```bash
# Make a new server folder
gatana hosted init ./my-server

# Verify the source code locally
gatana hosted verify ./my-server

# Call a tool locally before you deploy
gatana hosted run ./my-server my_tool -p input="hello"

# Upload, deploy and wait until it is ready
gatana hosted upload my-server ./my-server --create

# Show and follow the deployment logs
gatana deploy logs my-server -f

# Wait for the deployment, with a timeout
gatana deploy wait my-server --timeout 5m

# Download the deployed source code
gatana hosted download my-server -O my-server.zip

# Stop and start the deployment
gatana deploy stop my-server
gatana deploy start my-server --wait
```

### Call tools

```bash
# List all tools
gatana get tools

# List only the enabled tools
gatana get tools --enabled

# Show the schema of one tool
gatana get tool serverSlug_toolName

# Call a tool with dot-notation arguments
gatana tool my_server_search -a query="hello world" -a limit=10

# Call a tool with inline JSON
gatana tool my_server_search -a '{"query": "hello world", "limit": 10}'

# Call a tool with arguments from a JSON file
gatana tool my_server_search -f args.json

# Call a tool with arguments from stdin
echo '{"query": "hello"}' | gatana tool my_server_search
```

### Credentials

```bash
# Create credentials for a server (the type comes from the server: OAuth or API key)
gatana create creds my-server

# Create credentials from a file
gatana create creds my-server -f creds.json

# List the credentials of a server
gatana get creds -s my-server

# Get the effective credentials
gatana creds my-server

# Delete one credential
gatana delete creds <id> -s my-server
```

### Sandboxes

```bash
gatana create sandbox
gatana get sandboxes
gatana sandbox shell <id>
gatana delete sandbox <id>
```

### More than one organization

```bash
# Log in to two organizations
gatana config login org-one
gatana config login org-two --pat gk_...

# List the configured organizations
gatana config ls

# Change the default organization
gatana config set-default org-two

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

# One collection or one skill. The targets follow it from then on
gatana skills install release-engineering
gatana skills install deploy-checklist

# Each install adds the session-start hooks of the agents on this machine
# (Claude Code, Codex, Hermes, OpenClaw). The hooks run "gatana skills sync --quiet"
gatana skills install --no-hooks   # do not add the hooks
gatana skills remove-hooks         # remove them again, or: remove-hooks claude

# Refresh the folders by hand, or print a hook to paste
gatana skills sync
gatana skills hook claude   # paste the output into .claude/settings.json

# Edit an installed SKILL.md, then send all changes on this machine back.
# A skill that also changed on the server is printed as a conflict and left alone.
gatana skills push

# Push one skill
gatana skills push ~/.claude/skills/release-checklist

# Create a skill from a SKILL.md that you wrote
gatana skills push ./my-skill/SKILL.md
```

### Output formats

```bash
# Table (default)
gatana get servers

# JSON
gatana get servers -o json

# YAML
gatana describe server my-server -o yaml
```

---

## Development

### Crates

| Crate            | What it is                                                                                                       |
| ---------------- | ---------------------------------------------------------------------------------------------------------------- |
| `gatana-api`     | Typed API client. `src/v1.rs` and `src/v2.rs` are generated; `src/lib.rs` is the hand-written runtime they call. |
| `gatana-codegen` | The generator that writes `v1.rs` and `v2.rs` from the backend's OpenAPI documents.                              |
| `gatana-cli`     | The CLI. The binary is called `gatana`.                                                                          |

### Build and test

Run these from the repository root.

```sh
just rs-build                 # packages/gatana-cli/target/release/gatana
just rs get servers           # run from source
just rs-test                  # tests, clippy, format check
just rs-dist                  # release binaries for every platform (needs Docker)
just generate-rs              # regenerate the client from hello.gatana.ai
just generate-rs https://acme.local.gatana.ai   # from a local backend
```

### The generated client

Only the operations listed in `crates/gatana-api/operations.json` are generated. To call a new
endpoint, add its `operationId` there and run `just generate-rs`. The build then fails wherever the
CLI uses a path parameter, query parameter, request body or response field that changed in the
backend.

The generator simplifies the schemas before typify turns them into Rust types:

- It inlines the anonymous `__schemaN` components, so types get names like `ServerDtoTransportConfig`.
- It drops validation keywords and `format`, and opens closed objects. A typed read then keeps
  working when the server adds a field or returns an old value.
- It turns unions of objects that carry a `type` tag into `#[serde(tag = "type")]` enums.
- It moves the nullability of a nullable named schema to the places that reference it.

Every operation returns a `Call`. `.value()` gives the response JSON as sent, `.typed()` gives the
generated type, and `.send()` gives both. The CLI prints the raw JSON, so `-o json` shows every field
in the server's order. It reads typed fields where it makes a decision on them.

Read raw, not typed, when the response contains a server object. Its transport configuration is a
union that the backend extends, and a command that only needs a slug must not break on a new transport.
The audit log list is also read raw, because the backend omits `onlySuperadminVisibility`, which its
schema marks as required.

---

## Changes from the TypeScript CLI

Fixes:

- Errors go to stderr and the exit code is 1. The TypeScript CLI printed most errors to stdout and
  exited with 0.
- With `-o json` or `-o yaml`, progress lines go to stderr, so stdout holds only the result.
- `-o` accepts only `json`, `yaml` and `table`.
- `hosted download` writes to `-O, --out-file`. Its old `-o` never worked, because the global `-o`
  took the value.
- `hosted verify` prints its result and exits with 1 when a tool is not valid. Before, it printed
  nothing.
- `hosted upload` fails, with the container's logs, when the deployment does not become ready.
  Before, it reported success. `--no-logs` now skips those logs. `--force` now also covers a module
  that does not import. Tools that fail the check are listed as warnings.
- An image pull failure during a deployment is reported with its reason. Before, it was ignored and
  the deployment counted as successful.
- `deploy wait` exits with 1 when the deployment does not become ready.
- `tool` reads its arguments from stdin when neither `-f` nor `-a` is given, as its help text says.
- The config file is written readable by the owner only (mode 600), because it holds tokens.

Changes:

- `hosted local-verify` and `hosted local-run` are now `hosted verify` and `hosted run`.
- `config show` is now `config current`. `config set-api-key` is gone: use
  `config login <org> --pat <token>`.
- `create server` takes the slug with `-s, --slug`.
- `delete creds` deletes one credential by its ID. It has no `--all`.
- `hosted verify` and `hosted run` start `node` to load the source code. When the source folder
  cannot resolve `zod`, the CLI installs it once into its cache folder with npm and links it in for
  the run. `hosted upload` without Node.js checks `index.js` for a schema export only.
- `create server` without `--transport-type` shows a list to pick from, not a text prompt.
- `config login --no-browser` prints the link without opening a browser.
- `-o yaml` does not fold long strings at 80 columns. Tables have no trailing spaces.
- The skills manifest lists its entries in the order of the server's list, not in download order.
- The CLI has no `DEBUG` logging.

---

## Releasing

`just release` in the repository root bumps the version in `crates/gatana-cli/Cargo.toml`, commits
it and then runs this release. To run only this release, bump and commit the version yourself, then
run `just rs-release`. `just rs-release --dry-run` builds and stages everything without publishing
anything.

The release runs on a Mac with Docker. It needs `gh` and `npm` logins, and a GPG key for the signed
tag. It does these steps:

1. `scripts/dist.sh` builds four binaries and checks that each one starts:
   - macOS arm64 and x64, with a rustup toolchain kept in `~/.cache/gatana-cli-release`
   - Linux arm64 and x64, static musl, in the `cargo-zigbuild` Docker image
2. It tags `gatana@<version>` and makes a GitHub release with one `gatana-<target>.tar.gz` and one
   `.sha256` file per target, plus `install.sh`.
3. It publishes one npm package per platform (`@gatana/cli-<os>-<cpu>`), then `gatana`. `gatana`
   has the platform packages as optional dependencies, so npm installs only the one for the
   machine. Its `bin/gatana` is a shell script that starts that binary. It is not a Node script,
   because the skills hooks run `gatana` at every session start. Its README is `npm/README.md`.
4. It writes `Formula/gatana.rb` in `gatana-ai/homebrew-tap`. It asks before it creates that
   repository the first time.

A version with a pre-release part, such as `4.0.0-alpha.0`, is released as a pre-release:

- On npm it gets the dist-tag `next`, so users get it with `npm install -g gatana@next`.
- On GitHub it is not marked as latest, so `install.sh` keeps installing the previous version. Use
  `GATANA_VERSION=4.0.0-alpha.0` to install it.
- The Homebrew formula is not changed.

Releases of the other packages in this repository are not marked as latest on GitHub, so
`releases/latest/download/install.sh` always gets the newest CLI release.

---

## Not done yet

- Windows: the CLI has not been built or run there, and there is no Windows binary in the release.
  The npm package refuses to install on Windows.
- macOS notarization. Binaries that curl, brew or npm download do not get the quarantine flag, so
  Gatekeeper does not check them. A binary downloaded in a browser would be blocked.
- The hooks run `gatana` without a path. An agent that starts without the user's shell PATH does not
  find it in `~/.local/bin` or in an nvm folder.
- The device login was tested up to the polling step, not through an approval in the browser. The
  token refresh was not run against a server: it would rotate a real refresh token.
