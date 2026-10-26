---
name: gatana
description: 'Set up and explain the Gatana MCP gateway. Use when the user wants to add, connect or create an MCP server in Gatana (a remote MCP URL, an npx or uvx command, an OpenAPI specification, or hosted Node.js or Python code). Also use to create, assign or explain Gatana profiles, and to set up, explain or debug Gatana credentials: server, user and profile scope, OAuth, API keys, "need-credentials" errors and authorize links. Also use for "who can use this server" questions about Gatana, and when the user has no Gatana organization yet and wants to create one.'
---

# Gatana

[Gatana](https://www.gatana.ai) is an MCP gateway. An organization adds its MCP servers to Gatana one time. Its people and agents then get the tools of all these servers through one MCP endpoint. Gatana keeps the credentials, decides who can use each server, and writes each tool call to an audit log. For a longer explanation for the user, link [What is an MCP gateway?](https://www.gatana.ai/guides/what-is-an-mcp-gateway).

The documentation is at [docs.gatana.ai](https://docs.gatana.ai/). Each section below names its page. Read the page when this skill does not answer a question, and link it when the user wants to read more.

This skill has four jobs:

1. Add an MCP server to Gatana.
2. Explain and set up profiles.
3. Explain and set up credentials, and how their scope works.
4. Create an organization for a user who has none.

## Words in this skill

| Word                 | Meaning                                                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Organization         | One Gatana customer. Its dashboard is at `https://<org>.gatana.ai`. The API calls it a tenant.                           |
| Server               | One MCP server in Gatana: a remote URL, a command that Gatana runs, code that Gatana hosts, or an OpenAPI specification. |
| Slug                 | The short ID of a server: lowercase letters, digits and hyphens, 20 characters or fewer, unique in the organization.     |
| Tool name            | Clients see each tool as `<slug>_<tool>`, for example `github_create_issue`.                                             |
| Authorization method | What kind of secret a server needs: `none`, `apikey`, `oauth` or `oauth-client-credentials`.                             |
| Credential           | The stored secret: API key values or an OAuth token set. Gatana keeps it. The client never gets it.                      |
| Scope                | Who a credential belongs to: `server` (shared by all), `user` (one person), or `profile` (a named group or context).     |
| Profile              | A named set of servers, tool settings and credentials. It applies to users, teams, tokens or clients.                    |

## Step 1: Find how you can act

Use the first surface that is available:

1. **Gatana MCP tools.** Look for tools that start with `gatana-api_`, for example `gatana-api_createServerV2`. If the gateway runs in Code Mode, you see only `codemode_search_tools` and `codemode_execute_code`. Then search first, and call `codemode.gatanaApi.<operation>({ ... })` from code.
2. **The `gatana` CLI.** Run `gatana auth-info`. The CLI can create servers and set up their OAuth, patch them, set server and user credentials, upload hosted code, and manage accounts, teams, profiles and who has access to a server. See [references/api.md](references/api.md).
3. **The REST API.** Use it only when the user gives you a personal access token in an environment variable. Base URLs: `https://<org>.gatana.ai/api/v1` and `/api/v2`. See [Public API](https://docs.gatana.ai/public-api-introduction/).

If none of these is available, give the user the dashboard steps. Each reference file has them. If the user has no organization yet, see [Create an organization](#create-an-organization). If the user has one but is not connected to it, see [Connecting to Gatana](https://docs.gatana.ai/connecting-to-gatana/).

The operation names are the same on all surfaces. `createServerV2` is the MCP tool `gatana-api_createServerV2`, the Code Mode call `codemode.gatanaApi.createServerV2`, and the REST route `POST /api/v2/servers`. [references/api.md](references/api.md) lists all of them.

**If the Gatana tools are missing but the user is connected to Gatana:** `gatana-api` is a built-in server. It is private by default. An organization owner must give the user access to it: add the user as a member of the `gatana-api` server, or add the server to a profile that the user has. An owner can also turn on **Settings > Make all tools available to organization owners over MCP**.

## Rules

- **Confirm before you change something.** Creating, changing and deleting servers, credentials, profiles and access change the organization. Say in one sentence what you will change. Then make the call.
- **Never invent a server address or a command.** Find it in the vendor's documentation or in the official MCP registry, or ask the user. A wrong address makes a server that fails on first use.
- **Keep secrets out of the chat.** Prefer an authorize link: the user types the key into Gatana, and the key never passes through you. See [references/credentials.md](references/credentials.md). If the user pastes a key, use it, but do not write it again in your answers.
- **Do not open access as a side effect.** `visibility: "organization"`, `isOpenToAllUsers: true` and the organization base role each give access to every member. Set them only when the user asks for that.
- **You act as the signed-in user.** You have their permissions only. If Gatana refuses a call ("No permissions", HTTP 403), say which permission is missing and who can give it. Do not try the same call again.
- **Read the result shape before you use it.** Most list operations return an envelope, for example `{ servers: [...] }`.

## Create an organization

Do this only when the user has no Gatana organization yet. The `gatana` CLI creates the organization and signs in to it. To install the CLI, see [references/api.md](references/api.md#the-gatana-cli).

Get these values from the user. Then confirm them in one sentence, because the command creates an organization and sends an email.

| Value             | Flag         | Rule                                                                                                                                                                                   |
| ----------------- | ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Organization name | `--org-name` | 1 to 50 characters.                                                                                                                                                                    |
| Organization ID   | `--org-id`   | Lowercase letters, digits and hyphens, 40 characters or fewer. The address is `https://<id>.gatana.ai`. Without the flag, the CLI makes it from the name: `Acme Inc` gives `acme-inc`. |
| Email address     | `--email`    | 50 characters or fewer. This person becomes the owner. Gatana sends a 6-digit code to the address.                                                                                     |

Then sign up in two steps:

1. Run `gatana signup --org-name "Acme Inc" --email you@acme.com`. Gatana sends a 6-digit code to the address. The CLI prints the command that finishes the sign-up. That command has the organization ID in it and ends with `--code <code>`. This will create an organization with 14 days free Pro trial. When it expires the organization will revert to the free plan.
2. Ask the user for the code from the email. Run the printed command with `<code>` replaced by the code. The CLI creates the organization and signs in to it.

About the code:

- It is valid for 30 minutes. After 5 wrong tries, it stops working.
- If the CLI says that the code is wrong, ask the user to check it. Then run the printed command again.
- Run step 1 only one time. Each run without `--code` sends a new code, and the new code replaces the old one.

Two other ways:

- The user runs `gatana signup` in their own terminal. The CLI asks for each value and for the code.
- You run `gatana signup --browser --org-name "Acme Inc" --email you@acme.com` in the background. The CLI opens the sign-up page with the name and the email filled in, and waits up to 10 minutes. Give the user the link that the CLI prints, in case the browser does not open. The user finishes the sign-up in the browser.

For an on-premise install, add `--base-url https://<address of the install>`.

After the sign-up:

- `gatana auth-info` shows the new organization.
- `gatana install` connects every AI agent it finds on the machine (Claude Code, Codex, Hermes, OpenClaw) to the gateway, without a question. To connect only some agents, name them: `gatana install claude` (or `codex`, `hermes`, `openclaw`).
- In the cloud, a new organization starts with a 14-day trial. Plans: [www.gatana.ai/pricing](https://www.gatana.ai/pricing).
- An owner who signed up in the terminal has no password for the dashboard yet. On the sign-in page, the owner clicks **Forgot your password?** and sets one from the email.

## Add an MCP server

Do these steps in order. Details and full examples are in [references/servers.md](references/servers.md). Docs: [Tool servers](https://docs.gatana.ai/tool-servers-fundamentals/).

### 1. Find the right server

- Prefer the vendor's official server. A server from another publisher can look official. When there are several candidates, show them and let the user choose.
- Prefer a remote endpoint. Many vendors publish an `npx` or `uvx` package and also run a remote MCP endpoint. A remote server needs no hosting and supports per-user OAuth.
- For popular services (GitHub, Linear, Notion, Slack, Google Workspace and more), the dashboard has **Add Server > Popular servers**. It installs the official server and sets up OAuth in one click. Recommend it when it fits. There is no API for it.
- For a remote server that signs users in with OAuth, `gatana create server remote <url> --slug <slug>` does the OAuth setup too: it finds the OAuth metadata, registers a client when the provider permits it, and sets per-user OAuth. Prefer it to the steps below when you have the CLI.

### 2. Choose the transport

| `transportConfig.type` | Use it for                                                             | Notes                                                |
| ---------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------- |
| `httpstreaming`        | A remote MCP server over HTTP                                          | The default choice.                                  |
| `sse`                  | A remote server that uses the older Server-Sent Events transport       | Only when the server needs it.                       |
| `stdio`                | A server that starts from a command, such as `npx -y pkg` or `uvx pkg` | Gatana runs it in an isolated VM. Needs a paid plan. |
| `hosted`               | Your own tool functions in Node.js 24 or Python 3.13                   | Gatana runs the code. Needs a paid plan.             |
| `openapi`              | A REST API with an OpenAPI 3 or Swagger 2 specification                | One tool per operation. No code.                     |

Docs per type: [Standard MCP](https://docs.gatana.ai/servers-standard-mcp/) (`httpstreaming`, `sse`, `stdio`), [Runnable code](https://docs.gatana.ai/servers-runnable-code/) (`hosted`), [OpenAPI](https://docs.gatana.ai/servers-openapi-swagger/). Plans: [www.gatana.ai/pricing](https://www.gatana.ai/pricing).

### 3. Choose the slug

Derive it from the service: `linear`, `github-eu`. Keep it short, because clients limit tool names to about 64 characters. Call `listServersV2` and make sure that the slug is not in use.

### 4. Choose the authorization

Set the method and the scope in `authorization`:

| The server needs                  | `method`                   | Put the secret in the config like this                                                                                |
| --------------------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Nothing                           | `none`                     | Nothing.                                                                                                              |
| A static key or token             | `apikey`                   | Name the keys in `apikeys: ["MY_KEY"]`. Use `{{ credentials.keys.MY_KEY }}` in a header, the URL, `env` or `command`. |
| An OAuth login                    | `oauth`                    | Nothing. Gatana sends `Authorization: Bearer <token>` itself.                                                         |
| A machine-to-machine OAuth client | `oauth-client-credentials` | Nothing. Each credential holds a client ID and secret.                                                                |

Then choose `credentialsScope`:

- `server`: one shared credential for everybody, for example a service account or a team API key.
- `user`: each person signs in with their own account, for example email, calendar or GitHub as themselves.

`profile` is not a value of `credentialsScope`. A profile credential overrides either scope. See the credential section below.

Also set `toolRefreshCredentialPolicy`. It controls the credential that Gatana uses to read the tool list:

- `user` scope: use `any` (or `skip` if the server lists its tools without a login). The default, `server-scoped`, fails when no shared credential exists.
- `server` scope: `server-scoped` is correct.
- Tool list needs no login (most OpenAPI servers): `skip`.

**Limit:** a `stdio` server reads `env` and `command` one time, when Gatana starts it. These values always use the server-scoped credential. Per-user API keys cannot reach a `stdio` server. Per-user OAuth reaches it only when the process speaks HTTP (`transport: "httpstreaming"` or `"sse"`), because Gatana then adds the token to each request.

### 5. Create the server in one call

```typescript
await codemode.gatanaApi.createServerV2({
  body: {
    slug: 'perplexity',
    description: 'Web search with Perplexity',
    visibility: 'private',
    transportConfig: {
      type: 'httpstreaming',
      url: 'https://api.perplexity.ai/mcp',
      headers: [['Authorization', 'Bearer {{ credentials.keys.PERPLEXITY_API_KEY }}']],
    },
    authorization: {
      method: 'apikey',
      apikeys: ['PERPLEXITY_API_KEY'],
      credentialsScope: 'server',
      toolRefreshCredentialPolicy: 'server-scoped',
    },
  },
});
```

Two traps:

1. **Put the payload in `body`.** The tool takes its parameters by name: `body` for the request body, plus path parameters such as `serverSlug` or `slug`. If you put the fields at the top level, Gatana gets an empty body and answers `400 Failed body validation` with `"input":{}`. That error means the `body` wrapper is missing. It does not mean that the fields are wrong.
2. **Use tuples, not objects.** `headers` and `env` are arrays of `[name, value]` pairs. `authorization.apikeys` is an array of key names. The credential's `apikeys` is an array of `[name, value]` pairs.

Over plain MCP, call the tool `gatana-api_createServerV2` with the same `{ "body": { ... } }` arguments.

### 6. Give the credentials

| Scope and method    | What to do                                                                                                                                                                         |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `server` + `apikey` | Get a link with `getMcpServerCredentialsAuthorizeUrl({ serverSlug, scope: 'server', returnTo: 'thank-you-page' })`. Give the link to the user. The user types the key into Gatana. |
| `user` + any method | Do nothing now. Each user gets a link on their first tool call. To set up the current user now, get a link with `scope: 'user'`.                                                   |
| `oauth`             | The server needs OAuth metadata and an OAuth client first. `gatana create server remote` sets up both. Or see [references/credentials.md](references/credentials.md#oauth-setup).  |

Setting credentials on a `stdio` or `hosted` server restarts it.

### 7. Check the tools

Gatana caches the tool list of each server. It refreshes enabled servers every few hours. For a new server, ask the user to click **Refresh** in the **Tools** section of the server page, or call the REST route `POST /api/v1/tools/refresh?serverSlug=<slug>` with `Accept: text/event-stream`. Then call `listMcpServerTools({ serverSlug })`.

A server with no tools usually needs credentials. It is usually not broken. For `stdio` and `hosted` servers, `gatana deploy logs <slug>` shows the output of the process.

### 8. Give access

A new server is private. Its creator is its admin. Organization owners can manage it. Nobody else can use it until one of these is true:

- A user or team is a member: `updateMcpServerMember({ serverSlug, memberType: 'users' | 'teams', memberId, body: { role: 'member' } })`, or `gatana server grant <slug> --account <email> | --team <name>`. `gatana server access <slug>` lists the members and the profiles. Roles: `member` calls tools, `maintainer` changes the configuration, `admin` also manages members and deletes.
- A profile that the user has includes the server.
- The server has `visibility: "organization"`. Then every member can use it.
- The organization base role is not `none`. Then every member has that role on every server.

Docs: [Permissions and roles](https://docs.gatana.ai/permissions-and-roles/).

### 9. Report

Tell the user the slug, the transport, the authorization and scope, what is still missing (credentials, access, plan), and the server page: `https://<org>.gatana.ai/dashboard/servers/<slug>`.

## Explain and set up profiles

A profile is a named set of servers, tool settings and credentials. Use a profile when access or credentials must depend on **who** or **which client**: a team, a project, an agent, one MCP client.

What a profile can do:

- Give access to its servers. Each server in the profile gives member access to everyone who has the profile.
- Hold its own credentials for a server. They override the server and user credentials.
- Limit, rename and promote tools for each server.
- Restrict the session to its servers only (`isRestrictive`). This applies to organization owners too.
- Force Code Mode (`isCodeModeForced`).

How a profile becomes active in a session:

- Direct assignment to a user, a team or a service account.
- A claim mapping: a claim from the identity provider, for example `groups` contains `support`.
- A personal access token or a connected OAuth client that carries the profile.
- The MCP URL parameter `?p=<profileId>` or the header `x-gatana-profile-id`. Both take a comma-separated list. Both work only for profiles that are open to all users. A closed profile gives HTTP 400.

Typical setup:

```typescript
const { profile } = await codemode.gatanaApi.createProfile({
  body: {
    name: 'Support team',
    description: 'Zendesk and Slack with the support service account',
    isOpenToAllUsers: false,
    isRestrictive: false,
  },
});
// serverIds REPLACES the list. Send every slug the profile must keep.
await codemode.gatanaApi.updateProfile({ profileId: profile.id, body: { serverIds: ['zendesk', 'slack'] } });
await codemode.gatanaApi.createTeamProfile({ teamId, body: { profileId: profile.id } });
```

**`serverIds` replaces the full list.** To add one server, read the profile with `getProfile`, take the slugs from `profile.servers`, add the new slug, and send the full list. Send slugs: every Gatana version accepts them. Older versions accept only slugs and remove the servers that they cannot match.

Full details: [references/profiles.md](references/profiles.md). Docs: [Profiles](https://docs.gatana.ai/profiles/).

## Explain credential scoping

When a tool is called, Gatana finds the credential like this:

1. **Profile credentials first.** Gatana checks the active profiles in priority order. It uses the first profile credential for this server that is valid: same type as the server's method and, for API keys, the same number of keys.
2. **Else the server's `credentialsScope` decides.**
   - `server`: Gatana uses the shared server credential. If there is none, the call fails.
   - `user`: Gatana uses the calling user's own credential. If there is none, the call fails with `need-credentials` and an `authorizeUrl`.

There is no fallback from `user` to `server`. A user-scoped server never uses a shared server credential. To share one credential with a group on a user-scoped server, put the credential on a profile and give the profile to the group.

Profile priority, highest first: locked user assignment, locked team assignment, user assignment, team assignment, then all others (URL parameter, header, claim mapping, token, client). Inside one level, Gatana sorts by profile name.

When a tool result has `errorCode: "need-credentials"`, give the user the `authorizeUrl` as a link. The link works one time and for 24 hours. The user does not sign in to Gatana: the link identifies them. After the user authorizes, try the call again. If the message says that only an administrator can provide the credential, tell the user to contact their Gatana administrator.

Full details, OAuth setup and the per-transport table: [references/credentials.md](references/credentials.md). Docs: [Credentials](https://docs.gatana.ai/credentials/).

## Troubleshooting

| Symptom                                                     | Cause and fix                                                                                                                                           |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `400 Failed body validation` with `"input":{}`              | The `{ body: {...} }` wrapper is missing.                                                                                                               |
| `A server with this slug already exists`                    | Choose another slug.                                                                                                                                    |
| `This organization ID is already taken` or `is not allowed` | `gatana signup` needs another organization ID. In a terminal, the CLI asks for one.                                                                     |
| `does not support sign-up in the terminal`                  | The Gatana version is older. Use `gatana signup --browser`.                                                                                             |
| `The code is wrong or has expired`                          | Ask the user to check the code. After 30 minutes or 5 wrong tries, run `gatana signup` without `--code` for a new code.                                 |
| Server created but disabled                                 | The plan limit is reached. Creating a server is free. Enabling it counts. The user must raise the limit or disable another server.                      |
| `No permission to create a server`                          | The organization does not let members add this kind of server. An owner can change it in **Settings**.                                                  |
| `Tool refresh policy requires server-scoped credential`     | The server is user-scoped, but `toolRefreshCredentialPolicy` is `server-scoped`. Patch it to `any` or `skip`.                                           |
| Server lists no tools                                       | It needs credentials, or the tool cache was not refreshed yet. See step 7.                                                                              |
| `need-credentials` on every call for one user               | That user has no user credential. Give them the `authorizeUrl`.                                                                                         |
| A profile lost all its servers                              | An older Gatana version got IDs in `serverIds`. Send slugs.                                                                                             |
| The provider rejected a stored login                        | The OAuth login was revoked or expired. The result has a new `authorizeUrl`. For a shared login, everybody who uses it acts as the person who signs in. |
| A user cannot see a server                                  | Check all four access reasons in step 8. An empty member list does not mean that nobody has access.                                                     |

## References

- [references/servers.md](references/servers.md): each transport in full, with examples, hosted code and OpenAPI.
- [references/credentials.md](references/credentials.md): methods, scopes, OAuth setup, authorize links, secret stores.
- [references/profiles.md](references/profiles.md): all profile settings, how profiles apply, tool configuration.
- [references/api.md](references/api.md): operation names for MCP, Code Mode, REST and the CLI.
- Website: [www.gatana.ai](https://www.gatana.ai). Guides: [What is an MCP gateway?](https://www.gatana.ai/guides/what-is-an-mcp-gateway), [How to run serverless functions as MCP tools](https://www.gatana.ai/guides/run-serverless-functions-as-mcp-tools).
- Documentation: [docs.gatana.ai](https://docs.gatana.ai/). Start with [Quick start](https://docs.gatana.ai/quick-start/).
