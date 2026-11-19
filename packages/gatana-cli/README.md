# gatana CLI

The `gatana` CLI manages the servers, tools, credentials, accounts, profiles, settings, sandboxes
and skills of a Gatana organization. It is a native binary for macOS and Linux (arm64 and x64), written in Rust.

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

To get a new release, run `gatana upgrade`. It finds out from the path of the binary how gatana was
installed (install.sh, npm, pnpm, bun or Homebrew) and upgrades it the same way. `gatana upgrade
--dry-run` only shows the install method and what the upgrade would do.

## Quick start

```bash
gatana install
```

`install` signs you in (it opens the browser when you are not signed in yet), finds the AI agents
on this machine, and gives each one the Gatana gateway as an MCP server, the skills of your
organization, and the hook that keeps the skills current. It does not ask which agents: it connects
every agent whose folder it finds (`~/.claude`, `~/.codex`, `~/.hermes`, `~/.openclaw`). Then sign
in from the agent: for Claude Code, run `/mcp`, select `gatana` and Authenticate. The agents it
knows are Claude Code, Codex, Hermes and OpenClaw; name them to connect only those:
`gatana install claude codex`.

No organization yet? Run `gatana signup` first. It asks for the name of the organization, its ID
and your email address, then for the code that Gatana sends to that address. When the organization
exists, the CLI is signed in to it and makes it the active organization. Give the answers as flags
to skip the questions: `gatana signup --org-name "Acme Inc" --email you@acme.com`. Without a
terminal (an agent or a script), that run stops after the code goes out and prints the command
that finishes the sign-up with `--code <code>`. To sign up on the sign-up page in the browser
instead, add `--browser`.

For the rest of the CLI:

```bash
gatana config login
gatana auth-info
gatana get servers
```

`config login` opens the browser, where you choose your organization and sign in. To skip the
choice, name the organization: `gatana config login my-org`. That login uses a code, so it also
works on a machine without a browser, for example over SSH (add `--no-browser` to only print the
link). Add `--pat <token>` to log in with a personal access token: `gatana config login my-org --pat gk_...`.

On-premise, give the address of the install: `gatana config login --base-url https://gatana.example.com`.

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

### Get started

| Command     | Syntax                                                                                                       | Description                                                                                                                                                                                                                                                                                                                                                                         |
| ----------- | ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **signup**  | `gatana signup [--org-name name] [--org-id id] [--email address] [--code code] [--browser] [--base-url url]` | Create a new organization and sign in to it. Asks in the terminal for what the flags do not give, then for the code from the email. Without a terminal, it sends the code and prints the command that finishes with `--code`. `--browser` uses the sign-up page instead; `--org-name` and `--email` then fill in its form. The new organization becomes the active organization.    |
| **install** | `gatana install [agent...] [--no-browser] [--force]`                                                         | Sign in if needed. Connect the named agents (`claude`, `codex`, `hermes`, `openclaw`), or every agent found on this machine when none are named. Add the gateway as an MCP server, your organization's skills, and the session-start hook to each agent. `--force` allows a skill folder to sync from a different organization and overwrites locally edited and non-Gatana skills. |

> `install` writes the gateway URL of your organization into the agent's own configuration:
> `~/.claude.json` (Claude Code), `~/.codex/config.toml`, `~/.hermes/config.yaml` or
> `~/.openclaw/openclaw.json`. It holds no token: each agent signs in by itself, in the browser, the
> first time it connects. An entry named `gatana` that is already there is left as it is. The skills
> and the hook are what `skills install` writes, for the folders of the chosen agents.

### Basic commands

Operations on servers and credentials.

| Command             | Syntax                                                        | Description                                                                           |
| ------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| **get server**      | `gatana get server [name]`                                    | List all servers, or get one server by its slug                                       |
| **get tool**        | `gatana get tool [name] [--enabled]`                          | List all tools, or get the schema of one tool                                         |
| **get creds**       | `gatana get creds [id] -s <slug> [-e]`                        | List the credentials of a server, or get one by its ID                                |
| **describe server** | `gatana describe server <name>`                               | Show a server with its last 5 events, its credentials and who has access to it        |
| **create server**   | `gatana create server [kind] [args]`                          | Create a server, as the dashboard does. See [Create a server](#create-a-server) below |
| **create creds**    | `gatana create creds <slug> [-f file] [--scope user\|server]` | Create or replace the credentials of a server                                         |
| **delete server**   | `gatana delete server <name>`                                 | Delete a server                                                                       |
| **delete creds**    | `gatana delete creds <id> -s <slug>`                          | Delete one credential of a server                                                     |
| **patch server**    | `gatana patch server <slug> [-p kv...] [-f file]`             | Change a server with a JSON Merge Patch (RFC 7396)                                    |

> **Credential types**: `create creds` gets the type (OAuth or API key) from the server. For OAuth,
> omit `-f` to get an authorize URL, or give a token set with `-f` or on stdin. For API keys, give
> `[["header","value"], …]` with `-f` or on stdin.

### Create a server

`gatana create server` creates a server as the Add Server page of the dashboard does. Without a
kind, it shows a menu. An argument can answer each question. Without a terminal, a missing answer
is an error, unless a default can stand in.

| Command                    | Syntax                                                                          | Description                                                                                                                                            |
| -------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **create server remote**   | `gatana create server remote [url] [--sse] [-s slug]`                           | A remote MCP server. Gatana looks for its OAuth while you choose the slug. When the authorization server permits it, the CLI registers an OAuth client |
| **create server openapi**  | `gatana create server openapi [url] [-s slug]`                                  | Tools made from an OpenAPI or Swagger specification. It also looks for OAuth                                                                           |
| **create server local**    | `gatana create server local [-s slug] [--storage] [command...]`                 | A command such as `npx` or `uvx`, run in a container of its own. Put the options before the command                                                    |
| **create server code**     | `gatana create server code [-s slug] [--runtime node24\|python313] [--storage]` | Code that you write in Node.js or Python                                                                                                               |
| **create server built-in** | `gatana create server built-in [id]`                                            | A server that Gatana provides. Without an ID, a menu shows the ones that are not installed                                                             |
| **create server email**    | `gatana create server email [provider] [--login l] [--access a] [-s slug]`      | A mailbox: `gmail`, `microsoft365`, `fastmail`, `icloud`, `imap` (`--imap-host`, `--smtp-host`) or `jmap` (`--session-url`)                            |

> Each kind except `built-in` also takes `--visibility private|organization` (default `private`) and
> `--output-compression`. When you omit the slug, the CLI makes it from the domain or the package,
> as the dashboard does, and adds a number when another server has that slug. An email server gets
> the name of the provider, or a slug made from the host. Its `--login` is `password`, `token` or
> `oauth`, as the provider permits, and its `--access` is `send` (default), `organize` or `read`.

### Server management

Deployments, tool calls, FaaS servers and effective credentials.

| Command           | Syntax                                                                          | Description                                                            |
| ----------------- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **tools ls**      | `gatana tools ls [-s slug] [--all]`                                             | List the enabled tools, of all servers or of one server                |
| **tools \<name>** | `gatana tools <name>`                                                           | Show the description and arguments of a tool, and an example call      |
| **tools call**    | `gatana tools call <name> [-a kv...] [-f file] [-p part]`                       | Call a tool by its universal name (`serverSlug_toolName`). Alias: `x`  |
| **tools refresh** | `gatana tools refresh [-s slug]`                                                | Load the tools again from all servers or from one server               |
| **deploy get**    | `gatana deploy get <name>`                                                      | Get the deployment status of a server                                  |
| **deploy logs**   | `gatana deploy logs <name> [-f] [-p] [--id <deploymentId>]`                     | Show the logs of a stdio or hosted server                              |
| **deploy wait**   | `gatana deploy wait <name> [--timeout 10m]`                                     | Wait until the deployment is ready                                     |
| **deploy stop**   | `gatana deploy stop <name>`                                                     | Stop a deployment. The next tool call starts it again, if enabled      |
| **deploy start**  | `gatana deploy start <name> [--wait]`                                           | Start a deployment                                                     |
| **faas init**     | `gatana faas init [path]`                                                       | Make a new FaaS server folder from a template                          |
| **faas verify**   | `gatana faas verify <path>`                                                     | Verify the local source code (needs Node.js)                           |
| **faas run**      | `gatana faas run <path> <tool> [-i json] [-f file] [-p k=v]`                    | Call a tool in the local source code, without a deploy (needs Node.js) |
| **faas upload**   | `gatana faas upload <name> [path] [--create] [--no-wait] [--no-logs] [--force]` | Upload the source code, deploy it and wait until it is ready           |
| **faas download** | `gatana faas download <name> [-O file]`                                         | Download the deployed source code as a zip file                        |
| **creds**         | `gatana creds <slug> [--cred-id <id>]`                                          | Get the effective credentials or token of a server                     |

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

### Accounts

Users, service accounts, and the personal access tokens of a service account. An account goes by
its email address or its ID.

| Command                    | Syntax                                                               | Description                                                                                    |
| -------------------------- | -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **get account**            | `gatana get account [email] [--type user\|service-account\|all]`     | List the accounts, or show one                                                                 |
| **describe account**       | `gatana describe account <email>`                                    | Show an account with its profiles and teams, and the tokens of a service account, without keys |
| **create account**         | `gatana create account <email> [--name name] [--role member\|owner]` | Invite a user. Gatana sends an email with a link to set a password                             |
| **create service-account** | `gatana create service-account <name> [--role member\|owner]`        | Create a service account and print the API key of its first token                              |
| **patch account**          | `gatana patch account <email> [-p kv...] [-f file]`                  | Change the name, email, role or `isDisabled`. Members can change only their own name           |
| **delete account**         | `gatana delete account <email>`                                      | Delete an account permanently                                                                  |
| **get pat**                | `gatana get pat --account <email> [--show-secrets]`                  | List the tokens of a service account. The keys show only with `--show-secrets`                 |
| **create pat**             | `gatana create pat --account <email> --name name [--profile p...]`   | Create a token for a service account and print its key. `--profile` confines the token         |
| **delete pat**             | `gatana delete pat <id-or-name> --account <email>`                   | Delete a token of a service account                                                            |

> The service account email is made from the name, as the dashboard does:
> `Deploy bot` becomes `deploy-bot@service-account.<org>.gatana`. The token commands work only for
> a service account. Your own tokens need a browser session, so manage them in the dashboard. A
> token that Gatana made for the assistant or for Code Mode cannot manage tokens at all.

### Server access

Who can use a server, and what they can do with it. An account or a team gets a role of its own on
the server. A profile that holds the server gives the role `member` to everyone who has the profile.

| Command           | Syntax                                                                                             | Description                                                                                                        |
| ----------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **server access** | `gatana server access <slug>`                                                                      | List the accounts, teams and profiles with a role on the server, and the settings that give access to every member |
| **server grant**  | `gatana server grant <slug> --account <email> \| --team <name> [--role member\|maintainer\|admin]` | Give a role on the server, or change the role. Default: `member`                                                   |
| **server revoke** | `gatana server revoke <slug> --account <email> \| --team <name>`                                   | Take the role away. Access through a team or a profile stays                                                       |

> `member` calls the tools, `maintainer` also changes the configuration, and `admin` also changes
> who has access and deletes the server. Two settings give access to every member of the
> organization: the visibility of the server (`gatana patch server <slug> -p visibility=organization`)
> and the base role of the organization (`memberDefaultRole` in `gatana patch org`).

### Teams

A team goes by its name or its ID. A team gets its access from a role on a server
(`gatana server grant --team`) or from a profile (`gatana profile assign --team`).

| Command                      | Syntax                                                                      | Description                                                                                               |
| ---------------------------- | --------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| **get team**                 | `gatana get team [name] [--account email]`                                  | List the teams, or the teams of one account, or show one team                                             |
| **describe team**            | `gatana describe team <name>`                                               | Show a team with its members, open invitations, server roles, profiles and claim mappings                 |
| **create team**              | `gatana create team <name> [--description text] [-a email...]`              | Create a team, with members if you name them                                                              |
| **patch team**               | `gatana patch team <name> [-p kv...] [-f file]`                             | Change the name or the description                                                                        |
| **delete team**              | `gatana delete team <name>`                                                 | Delete a team. Its members lose the access that the team gave them                                        |
| **team add-member**          | `gatana team add-member <team> <email...> [--role member\|maintainer]`      | Add accounts to the team, or change their role. A maintainer adds and removes members                     |
| **team remove-member**       | `gatana team remove-member <team> <email...>`                               | Remove accounts from the team                                                                             |
| **team invitations add\|rm** | `gatana team invitations add <team> <email...> [--role member\|maintainer]` | Invite people by email, or delete the open invitations for an address. An invitation expires after 7 days |
| **team claims add\|rm**      | `gatana team claims add <team> <key>=<value>`                               | Make everyone whose identity provider sends the claim a member at sign-in, or stop                        |

### Profiles

A profile goes by its name or its ID. Put the name in quotes when it holds spaces.

| Command                         | Syntax                                                                                                         | Description                                                                   |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **get profile**                 | `gatana get profile [name] [-s slug]`                                                                          | List the profiles, or the ones that hold a server, or show one                |
| **describe profile**            | `gatana describe profile <name>`                                                                               | Show a profile with its servers, members, maintainers and claim mappings      |
| **create profile**              | `gatana create profile <name> [--description text] [--open-to-all] [--restrictive] [--code-mode] [-s slug...]` | Create a profile, with servers if you name them                               |
| **patch profile**               | `gatana patch profile <name> [-p kv...] [-f file]`                                                             | Change a profile. `serverIds` replaces the full list                          |
| **delete profile**              | `gatana delete profile <name>`                                                                                 | Delete a profile. It is also removed from every personal access token         |
| **profile add-server**          | `gatana profile add-server <profile> <slug...>`                                                                | Put servers in a profile                                                      |
| **profile remove-server**       | `gatana profile remove-server <profile> <slug...>`                                                             | Take servers out, with the tool settings of the profile for them              |
| **profile assign**              | `gatana profile assign <profile> --account <email> \| --team <name> [--lock]`                                  | Give a profile to an account or a team. Only owners can lock                  |
| **profile unassign**            | `gatana profile unassign <profile> --account <email> \| --team <name>`                                         | Take a profile away                                                           |
| **profile maintainers add\|rm** | `gatana profile maintainers add <profile> <email>`                                                             | Add or remove a maintainer. The last maintainer stays                         |
| **profile claims add\|rm**      | `gatana profile claims add <profile> <key>=<value>`                                                            | Give the profile to everyone whose identity provider sends the claim, or stop |
| **profile tools**               | `gatana profile tools <profile> <slug> [-f file]`                                                              | Show the tool settings of a profile for one server, or replace them           |

### Organization

The settings, plan and quotas of the organization. Only organization owners can read them.

| Command          | Syntax                                                                | Description                                                                                    |
| ---------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **get org**      | `gatana get org [--show-secrets]`                                     | Show the settings. The client secret of the identity provider shows only with `--show-secrets` |
| **describe org** | `gatana describe org`                                                 | Show the plan, the accounts and the servers in use, and the limits                             |
| **patch org**    | `gatana patch org [-p kv...] [-f file] [--logo file] [--remove-logo]` | Change settings. A nested setting merges with the stored one, so one field is enough           |

> `patch org` reads the settings first. For each key that holds an object, it merges your change
> into the stored value and sends the whole object, because the backend replaces such a key whole.
> A patch that holds the mask `********` is refused, so output pasted back in cannot overwrite a
> secret. `--logo` takes a PNG, JPEG, WebP or SVG file of at most 256 KB.

### Alerts

An alert rule is an audit log filter with a threshold. When enough events match, Gatana notifies
the channels of the rule. A channel is a destination of one kind, such as email addresses or a
webhook. Only organization owners can use these commands, and the organization needs a paid plan.
A rule and a channel go by their name or their ID. Names are not unique, so the CLI asks for the
ID when several have the name.

| Command                              | Syntax                                                                                                                                       | Description                                                                                  |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **get alert**                        | `gatana get alert [name]`                                                                                                                    | List the rules with their channels and 7-day match counts, or show one rule                  |
| **describe alert**                   | `gatana describe alert <name>`                                                                                                               | Show a rule with its conditions and channels, and the daily limit of the organization        |
| **create alert**                     | `gatana create alert <name> -w <condition>... [--threshold n] [--window min] [--cooldown min] [-c channel...] [--all-channels] [--disabled]` | Create a rule. Defaults: 1 event in 5 minutes, at most one alert in 60 minutes               |
| **patch alert**                      | `gatana patch alert <name> [-p kv...] [-f file]`                                                                                             | Change a rule. `conditions` and `channelIds` replace the full list                           |
| **delete alert**                     | `gatana delete alert <name>`                                                                                                                 | Delete a rule                                                                                |
| **alert enable\|disable**            | `gatana alert enable <alert>`                                                                                                                | Start or stop a rule. An enabled rule starts at the newest audit log event                   |
| **alert preview**                    | `gatana alert preview -w <condition>...`                                                                                                     | Count the events of the last 7, 30 and 90 days that conditions match. Creates nothing        |
| **alert add-channel**                | `gatana alert add-channel <alert> <channel...>`                                                                                              | Add channels to a rule                                                                       |
| **alert remove-channel**             | `gatana alert remove-channel <alert> <channel...>`                                                                                           | Remove channels from a rule. A rule without channels sends nothing                           |
| **get channel**                      | `gatana get channel [name] [--show-secrets]`                                                                                                 | List the channels with their delivery status, or show one channel                            |
| **describe channel**                 | `gatana describe channel <name> [--show-secrets]`                                                                                            | Show a channel with its settings and the rules that send to it                               |
| **create channel**                   | `gatana create channel <name> --kind <kind> [-s field=value...] [--secret field=value...]`                                                   | Create a channel, and print the secrets that Gatana generated for it                         |
| **patch channel**                    | `gatana patch channel <name> [-p kv...] [-f file]`                                                                                           | Change `name`, `isEnabled` or the settings under `values`                                    |
| **delete channel**                   | `gatana delete channel <name>`                                                                                                               | Delete a channel. The rules that use it stop sending to it                                   |
| **channel kinds**                    | `gatana channel kinds`                                                                                                                       | List the channel kinds of this installation, with the fields of each kind                    |
| **channel test**                     | `gatana channel test <channel>`                                                                                                              | Send a test message. The exit code is 1 if the delivery fails                                |
| **channel rotate-secret**            | `gatana channel rotate-secret <channel> [field]`                                                                                             | Replace a generated secret, such as the signing secret of a webhook, and print the new value |
| **channel enable\|disable**          | `gatana channel disable <channel>`                                                                                                           | Start or stop every delivery to a channel                                                    |
| **get channel-notification-history** | `gatana get channel-notification-history [--limit n] [--page n]`                                                                             | List what Gatana sent, newest first, with the delivery status for each channel               |

> **Conditions**: a condition is `field:operator:value`, the same form as a filter in the address
> of the Audit Logs page, so you can build a filter there and copy it. The operators are `eq`,
> `neq` and `contains`. An event must match every condition of a rule. `gatana schema alert` lists
> the fields.
>
> **Channel settings**: the CLI reads the kinds and their fields from the API, so `create channel`
> has no flag per kind. `-s` sets a plain field, and a list such as `recipients` takes commas.
> `--secret` sets a secret field: the value itself, `@<file>`, or `-` for stdin. `patch channel`
> keeps the settings and the secrets that the patch leaves out. In a patch, `null` removes a value.
> The API never returns a secret that you typed. It returns the secrets that Gatana generated, and
> the CLI hides them unless you pass `--show-secrets`.

### Skills

Install the skills of your organization into the folders that AI agents read, and push local
changes back. See the [skills documentation](https://docs.gatana.ai/skills) for the full story.

| Command                 | Syntax                                                                                                         | Description                                                                                                                                                                                                                                                                                        |
| ----------------------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **skills install**      | `gatana skills install [name] [target...] [--dry-run] [--no-prune] [--force] [--reset] [--no-hooks] [--quiet]` | Write each skill you can read into `<dir>/<name>/`: its `SKILL.md` and its supporting files. Without a name: every skill, or what the targets follow. With a name: one collection or skill, or with `--server` every skill of one MCP server, which the targets follow from then on. Also installs the session-start hooks (`--no-hooks` skips them) |
| **skills sync**         | `gatana skills sync [target...] [--dry-run] [--no-prune] [--force] [--quiet]`                                  | Refresh what each folder follows, as the session-start hooks do: download the files that changed, remove the files that are gone. A folder without an install gets every skill you can read                                                                                                        |
| **skills remove-hooks** | `gatana skills remove-hooks [agent]`                                                                           | Remove the session-start hooks: from every agent on this machine, or from one                                                                                                                                                                                                                      |
| **skills push**         | `gatana skills push [path...] [-c collection] [--force] [--dry-run]`                                           | Send local changes back, each skill as its whole folder. Default: every skill in `claude` and `agents` that changed on this machine. Conflicts are printed and left alone                                                                                                                          |
| **skills ls**           | `gatana skills ls [-q text] [-c collection] [--collections]`                                                   | List the skills you can read, or the collections you can see                                                                                                                                                                                                                                       |
| **skills hook**         | `gatana skills hook <claude\|codex\|hermes\|openclaw> [--install]`                                             | Print, or install, the configuration that runs `gatana skills sync --quiet` when an agent session starts                                                                                                                                                                                           |
| **get skill**           | `gatana get skill [name] [-q text]`                                                                            | List skills, or show one with its instructions                                                                                                                                                                                                                                                     |
| **describe skill**      | `gatana describe skill <name>`                                                                                 | Show a skill with its instructions                                                                                                                                                                                                                                                                 |

> **Targets** for `skills install` and `skills sync`:
>
> - `claude` is `~/.claude/skills` (Claude Code).
> - `agents` is `~/.agents/skills` (Codex, Cursor, Gemini CLI, OpenCode, Copilot, Amp).
> - `hermes` is `~/.hermes/skills`.
> - Any other value is a path.
>
> The default targets are `claude` and `agents`. Without `--force`, the CLI does not change a folder
> that it did not create. It does not overwrite a locally edited file of a skill until you push the
> skill. The exception is a folder whose `SKILL.md` was deleted: the sync writes the skill again and
> names each local edit that it replaced. Each directory stores what it follows in its
> `.gatana-skills.json`, so the session-start hook keeps following it. `--reset` clears that state.
>
> **Skill folders.** A skill is a folder: a `SKILL.md` and supporting files in any subfolders.
>
> - `install` and `sync` write every file byte for byte as the server stores it, and add nothing to
>   a file. `.gatana-skills.json` (version 3) holds a hash per file. A file that you add to the folder
>   of a skill stays yours: a sync does not touch it.
> - `push` sends the whole folder and the server replaces the files of the skill in one step. A push
>   does not change the local files. It refuses a folder with more than 512 files or more than
>   4 MiB.
> - In a synced directory, a push deletes a file on the server only when the folder had the file
>   and you removed it. When the server holds a file that the folder never got, the push stops
>   until you sync, or until you push with `--force`.
> - A push refuses a folder that a sync of another organization wrote. `--force` creates a copy in
>   the organization of the push.
> - A file or folder whose name starts with a dot, such as `.env`, is pushed only when the skill on
>   the server already has that file. The push names what it left out. `.git` folders and
>   `.DS_Store` files are left out without a message.
> - Symlinks are never followed, written through or pushed.
> - A file path that some machine cannot hold is skipped by a sync, with a warning, and refused by
>   a push: a path that differs from another only in letter case or Unicode form, a name that
>   Windows does not allow, a `SKILL.md` in a subfolder and a path longer than 255 bytes.
> - A server without the file routes (backend v1.53.5 and older) still works: the CLI then syncs
>   and pushes only the `SKILL.md`.
> - CLI 5.2 and older wrote metadata (`gatana-id` and others) into each `SKILL.md`. A sync leaves
>   such a file until the skill changes on the server. A push still sends it as name, description
>   and body.
>
> **Skills of MCP servers.** A sync also writes the skills that connected MCP servers publish, for
> every server that you can use and that serves its skills.
>
> - A directory that follows nothing by name takes every server skill. A directory that follows
>   names takes a server only after `gatana skills install <slug> --server`.
> - A server skill keeps its name. When two skills want one folder, an organization skill gets it,
>   and between two servers the lower slug. The other skill gets the folder `<slug>-<name>`, and
>   the written `SKILL.md` has that name in its frontmatter and no other change.
> - The sync asks for the list of server skills once (`GET /server-skills`) and reads only the
>   files whose digest changed. The backend reads each file from the server with your credentials
>   and verifies it. Without credentials for a server, the sync skips its skills and prints the
>   authorize link once.
> - `.gatana-skills.json` holds server skills in `serverSkills`, by server ID and URI, with the
>   digest of the listing and the hash of each file as written. The version stays 3.
> - Every path and name from a server passes the same checks as above. A skill is written whole or
>   not at all. `push` skips the folder of a server skill.
> - For an agent, a synced server skill is a local skill: no origin, no approval per skill. The
>   per-server setting **Serve Skills** is the control.
> - A backend without the route (v1.53.5 and older) has no server skills. A failed listing removes
>   no folder.
>
> **Errors.** A skill that fails does not stop a sync. The sync writes and records the other
> skills, prints the failed skill on stderr and exits with an error code. The sync writes
> `.gatana-skills.json` after each skill, so a sync that a hook stops at its time limit keeps what
> it finished. Skills are read four at a time, server skills included.
>
> **Pushes outside a synced directory.** A folder with no `.gatana-skills.json` next to it has no
> manifest entry. `push` records such a folder in `~/.gatana.skill-pushes.json`: organization ID,
> canonical path, skill ID and the `updatedAt` after the push. The next push compares the server
> copy with that record, so a changed folder needs no `--force`. A new machine or a CI runner has
> no record and needs `--force` for the first push of a changed skill.
>
> When a skill and a collection have the same name, `--skill` or `--collection` selects one.
> `install`, `sync`, `push` and `ls` accept `--org <id>` to use an organization other than the
> default.

### Utility commands

Configuration, authentication and schemas.

| Command                | Syntax                                                        | Description                                                                  |
| ---------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **config current**     | `gatana config current`                                       | Show the resolved organization and configuration                             |
| **config token**       | `gatana config token`                                         | Print the token that requests use                                            |
| **config login**       | `gatana config login [org-id-or-url] [-p pat] [--no-browser]` | Log in in the browser or with a personal access token                        |
| **config ls**          | `gatana config ls`                                            | List all configured organizations                                            |
| **config set-default** | `gatana config set-default <name-or-url>`                     | Set the default organization                                                 |
| **config remove**      | `gatana config remove <name-or-url>`                          | Remove an organization from the config file                                  |
| **auth-info**          | `gatana auth-info`                                            | Show the authenticated user and organization                                 |
| **schema server**      | `gatana schema server`                                        | Print the resolved OpenAPI schema of the Server DTO                          |
| **schema account**     | `gatana schema account`                                       | Print what `patch account` takes                                             |
| **schema team**        | `gatana schema team`                                          | Print what `patch team` takes                                                |
| **schema profile**     | `gatana schema profile`                                       | Print what `patch profile` takes                                             |
| **schema org**         | `gatana schema org`                                           | Print what `patch org` takes                                                 |
| **schema alert**       | `gatana schema alert`                                         | Print what `patch alert` takes, with the fields and operators of a condition |
| **schema channel**     | `gatana schema channel`                                       | Print what `patch channel` takes                                             |
| **upgrade**            | `gatana upgrade [--dry-run]`                                  | Upgrade to the latest release, the way it was installed                      |

---

## Resource types

| Resource  | Aliases                            | Description                                 |
| --------- | ---------------------------------- | ------------------------------------------- |
| `server`  | `servers`                          | MCP server registrations                    |
| `tool`    | `tools`                            | Tools that the servers expose               |
| `creds`   | `credential`, `credentials`        | Credentials for servers                     |
| `sandbox` | `sandboxes`                        | Sandboxes (early access)                    |
| `skill`   | `skills`                           | Markdown instructions that agents follow    |
| `account` | `accounts`, `user`, `users`        | Users and service accounts                  |
| `profile` | `profiles`                         | Sets of servers, tools and credentials      |
| `pat`     | `pats`, `token`, `tokens`          | Personal access tokens of a service account |
| `org`     | `organization`, `settings`         | The settings of the organization            |
| `alert`   | `alerts`, `alert-rule`             | Alert rules on the audit log                |
| `channel` | `channels`, `notification-channel` | Destinations for notifications              |

---

## Examples

### Get started

```bash
# Install, sign in and connect the agents on this machine
curl -fsSL https://github.com/gatana-ai/gatana/releases/latest/download/install.sh | sh
gatana install

# Or only sign in
gatana config login

# Verify your identity
gatana auth-info

# List your servers
gatana get servers
```

### Manage servers

```bash
# Create a server (choose the kind in a menu, then answer the questions)
gatana create server

# Create a server with arguments
gatana create server remote https://mcp.example.com/mcp -s my-server
gatana create server code -s my-server --runtime node24

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

### Manage access

```bash
# A team with two members, which may change the configuration of the GitHub server
gatana create team platform --description "Platform engineers" -a ada@example.com -a bob@example.com
gatana server grant github --team platform --role maintainer
gatana server access github

# A profile with two servers, for one team and one account
gatana create profile Engineering --description "Tools for engineers" -s github -s linear
gatana profile assign Engineering --team platform
gatana profile assign Engineering --account ada@example.com

# A service account for a CI job, with a token that only the profile reaches
gatana create service-account "CI runner"
gatana create pat --account ci-runner@service-account.acme.gatana --name deploy --profile Engineering

# Turn off local servers for members, and point the sign-in at a new client ID
gatana patch org -p allowMemberAddLocalServers=false
gatana patch org -p upstreamOidcConfiguration.clientId=new-client-id
```

### Alerts

```bash
# A channel for email, and a webhook with a key from a file
gatana create channel ops-email --kind email -s recipients=ada@example.com,bob@example.com
gatana create channel pager --kind webhook -s url=https://hooks.example.com/gatana \
  -s authHeaderName=X-Api-Key --secret authHeaderValue=@key.txt

# Check that the channel delivers
gatana channel test pager

# How often the conditions matched, then the rule
gatana alert preview -w outcome:eq:denied -w serverSlug:eq:github
gatana create alert "GitHub denials" -w outcome:eq:denied -w serverSlug:eq:github --threshold 3 --window 10 -c ops-email

# Add the webhook, and change the threshold
gatana alert add-channel "GitHub denials" pager
gatana patch alert "GitHub denials" -p threshold=5

# What was sent, and whether each channel got it
gatana get channel-notification-history
```

### Develop a FaaS server

```bash
# Make a new server folder
gatana faas init ./my-server

# Verify the source code locally
gatana faas verify ./my-server

# Call a tool locally before you deploy
gatana faas run ./my-server my_tool -p input="hello"

# Upload, deploy and wait until it is ready
gatana faas upload my-server ./my-server --create

# Show and follow the deployment logs
gatana deploy logs my-server -f

# Wait for the deployment, with a timeout
gatana deploy wait my-server --timeout 5m

# Download the deployed source code
gatana faas download my-server -O my-server.zip

# Stop and start the deployment
gatana deploy stop my-server
gatana deploy start my-server --wait
```

### Call tools

```bash
# List the enabled tools, of all servers or of one server
gatana tools ls
gatana tools ls --server my_server

# Also list the disabled tools and the tools of disabled servers
gatana tools ls --all

# Show the description and arguments of a tool, and an example call
gatana tools my_server_search

# Call a tool with dot-notation arguments ("x" is short for "call")
gatana tools call my_server_search -a query="hello world" -a limit=10

# Call a tool with inline JSON
gatana tools x my_server_search -a '{"query": "hello world", "limit": 10}'

# Call a tool with arguments from a JSON file
gatana tools call my_server_search -f args.json

# Call a tool with arguments from stdin
echo '{"query": "hello"}' | gatana tools call my_server_search
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
gatana config login                       # choose org-one in the browser
gatana config login org-two --pat gk_...

# List the configured organizations
gatana config ls

# Change the default organization
gatana config set-default org-two

# Remove an organization
gatana config remove org-one
```

Each login is saved under a name. The name is the organization ID, unless that ID is already saved
for another address: then the name is the host. So the same organization can be signed in on two
addresses side by side:

```bash
gatana config login acme                        # saved as acme
gatana config login https://acme.s.gatana.ai    # saved as acme.s.gatana.ai
gatana config ls                                # shows the Name line for the second one

# --org, GATANA_ORG_ID, set-default and remove take the name, the URL or the host
GATANA_ORG_ID=acme.s.gatana.ai gatana get servers
gatana config set-default https://acme.s.gatana.ai
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

# Every skill that the MCP server "github" publishes
gatana skills install github --server

# Each install adds the session-start hooks of the agents on this machine
# (Claude Code, Codex, Hermes, OpenClaw). The hooks run "gatana skills sync --quiet"
gatana skills install --no-hooks   # do not add the hooks
gatana skills remove-hooks         # remove them again, or: remove-hooks claude

# Refresh the folders by hand, or print a hook to paste
gatana skills sync
gatana skills hook claude   # paste the output into .claude/settings.json

# Edit the files of an installed skill, then send all changes on this machine back.
# A skill that also changed on the server is printed as a conflict and left alone.
gatana skills push

# Push one skill: its SKILL.md and every file in its folder
gatana skills push ~/.claude/skills/release-checklist

# Create a skill from a folder that you wrote
gatana skills push ./my-skill
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
- `faas download` writes to `-O, --out-file`. Its old `-o` never worked, because the global `-o`
  took the value.
- `faas verify` prints its result and exits with 1 when a tool is not valid. Before, it printed
  nothing.
- `faas upload` fails, with the container's logs, when the deployment does not become ready.
  Before, it reported success. `--no-logs` now skips those logs. `--force` now also covers a module
  that does not import. Tools that fail the check are listed as warnings.
- An image pull failure during a deployment is reported with its reason. Before, it was ignored and
  the deployment counted as successful.
- `deploy wait` exits with 1 when the deployment does not become ready.
- `tool` reads its arguments from stdin when neither `-f` nor `-a` is given, as its help text says.
- The config file is written readable by the owner only (mode 600), because it holds tokens.

Changes:

- The `hosted` command group is now `faas`. `hosted local-verify` and `hosted local-run` are now
  `faas verify` and `faas run`.
- `config show` is now `config current`. `config set-api-key` is gone: use
  `config login <org> --pat <token>`.
- `create server` asks the questions of the Add Server page of the dashboard. The kind is a
  subcommand, for example `create server remote <url>`, and `-t, --transport-type` is gone.
- `delete creds` deletes one credential by its ID. It has no `--all`.
- `faas verify` and `faas run` start `node` to load the source code. When the source folder
  cannot resolve `zod`, the CLI installs it once into its cache folder with npm and links it in for
  the run. `faas upload` without Node.js checks `index.js` for a schema export only.
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
