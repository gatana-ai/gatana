---
name: gatana
description: 'Set up and explain the Gatana MCP gateway. Use when the user wants to add, connect or create an MCP server in Gatana (a remote MCP URL, an npx or uvx command, an OpenAPI specification, or hosted Node.js or Python code). Also use to create, assign or explain Gatana profiles, and to set up, explain or debug Gatana credentials: server, user and profile scope, OAuth, API keys, "need-credentials" errors and authorize links. Also use for "who can use this server" questions about Gatana, when an MCP App (the interactive view of a tool) does not show through Gatana, and when the user has no Gatana organization yet and wants to create one.'
---

# Gatana

[Gatana](https://www.gatana.ai) is an MCP gateway. An organization adds its MCP servers to Gatana one time. Its people and agents then get the tools of all these servers through one MCP endpoint. Gatana keeps the credentials, decides who can use each server, and writes each tool call to an audit log. For a longer explanation for the user, link [What is an MCP gateway?](https://www.gatana.ai/guides/what-is-an-mcp-gateway).

The documentation is at [docs.gatana.ai](https://docs.gatana.ai/). Each section below names its page. Read the page when this skill does not answer a question, and link it when the user wants to read more.

This skill has four jobs:

1. Add an MCP server to Gatana.
2. Explain and set up profiles.
3. Explain and set up credentials, and how their scope works.
4. Create an organization for a user who has none. See [references/signup.md](references/signup.md).

## Words in this skill

| Word                 | Meaning                                                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Organization         | One Gatana customer. Its dashboard is at `https://<org>.gatana.ai`. The API calls it a tenant.                           |
| Server               | One MCP server in Gatana: a remote URL, a command that Gatana runs, code that Gatana hosts, or an OpenAPI specification. |
| Slug                 | The short ID of a server: lowercase letters, digits and hyphens, 20 characters or fewer, unique in the organization.     |
| Tool name            | The default tool name uses `<slug>_<tool>` (for example `github_create_issue`).                                             |
| Authorization method | What kind of secret a server needs: `none`, `apikey`, `oauth` or `oauth-client-credentials`.                             |
| Credential           | The stored secret: API key values or an OAuth token set. Gatana keeps it. The client never gets it.                      |
| Scope                | Who a credential belongs to: `server` (shared by all), `user` (one person), or `profile` (a named group or context).     |
| Profile              | A named set of servers, tool settings and credentials. It applies to users, teams, tokens or clients.                    |

## Choose how to use Gatana

If the user has no organization and wants to create one, start with the [sign-up instructions](references/signup.md). If the user already has an organization but has no connection to it, see [Connecting to Gatana](https://docs.gatana.ai/connecting-to-gatana/).

Use the first option available for the task.

1. **Gatana MCP tools.** Look for tools that start with `gatana-api_`. If `codemode_search_tools` and `codemode_execute_code` are available, use `codemode_search_tools` to find the exact tool name and arguments.
2. **Gatana CLI.** Run `gatana auth-info` to check the active organization. For installation instructions and commands, read **The gatana CLI** in [references/api.md](references/api.md).
3. **REST API.** Use a personal access token that the user provides in an environment variable. For cloud organizations, use `https://<org>.gatana.ai/api/v1` or `https://<org>.gatana.ai/api/v2`. For on-premise installations, use the organization's own host. See [Public API](https://docs.gatana.ai/public-api-introduction/).
4. **Dashboard.** Give the user the steps for [servers](references/servers.md), [profiles](references/profiles.md) or [credentials](references/credentials.md).

`createServerV2` is the MCP tool `gatana-api_createServerV2`, the Code Mode call `codemode.gatanaApi.createServerV2`, and the REST route `POST /api/v2/servers`. See [references/api.md](references/api.md) for more operations.

If the user is connected but the Gatana API tools are missing, ask an organization owner to check that the built-in `gatana-api` server is installed and enabled. New organizations start with a private `gatana-api` server. An owner can add the user as a server member or add the server to a profile that the user has. An owner can also turn on **Settings > Make all tools available to organization owners over MCP**. This setting applies to all servers.

## Rules

- **State the change before you make it.** If the user already asked for the change, say what you will change and then make the call. Ask first if the change needs an access decision the user has yet to make.
- **Never invent a server address or a command.** Find it in the vendor's documentation or in the official MCP registry, or ask the user. A wrong address makes a server that fails on first use.
- **Keep secrets out of the chat.** Prefer an authorize link: the user types the key into Gatana, and the key never passes through you. See [references/credentials.md](references/credentials.md). If the user pastes a key, use it, but do not write it again in your answers.
- **Keep access within the user's request.** Server visibility and the organization base role can grant access to every member. An open profile lets every member apply it and use its servers. Change these settings only when the user asks.
- **You act as the signed-in user.** If Gatana denies permission, explain who can grant it. If the response does not name the missing permission, report the error. Retry after the permissions change.
- **Check the response fields before you use them.** Most list operations return an envelope, for example `{ servers: [...] }`.

## Add an MCP server

Do these steps in order. Details and full examples are in [references/servers.md](references/servers.md). Docs: [Tool servers](https://docs.gatana.ai/tool-servers-fundamentals/).

### 1. Find the right server

- Prefer the vendor's official server. A server from another publisher can look official. When there are several candidates, show them and let the user choose.
- Prefer a remote endpoint. Many vendors publish an `npx` or `uvx` package and also run a remote MCP endpoint. Gatana can connect to the remote endpoint directly. If the server supports OAuth, each user can sign in with their own account.
- For popular services (GitHub, Linear, Notion, Slack, Google Workspace and more), the dashboard has **Add Server > Popular servers**. It installs the official server and sets up OAuth in one click. Recommend it when it fits. There is no API for it.
- For a remote server that signs users in with OAuth, use `gatana create server remote <url> --slug <slug>` if the CLI is available. It looks for OAuth metadata and sets up per-user OAuth if it finds it. If the CLI creates the server, continue at step 6.

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

This example uses the [official Perplexity MCP server](https://github.com/perplexityai/modelcontextprotocol#remote-mcp-server) with a shared API key.

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

Format the request as follows.

1. **Put the payload in `body`.** The tool takes its parameters by name: `body` for the request body, plus path parameters such as `serverSlug` or `slug`. If you put the fields at the top level, Gatana gets an empty body and answers `400 Failed body validation` with `"input":{}`. If the error shows an empty input, add the `body` wrapper.
2. **Use arrays of pairs.** `headers` and `env` are arrays of `[name, value]` pairs. `authorization.apikeys` is an array of key names. The credential's `apikeys` is an array of `[name, value]` pairs.

Over plain MCP, call the tool `gatana-api_createServerV2` with the same `{ "body": { ... } }` arguments.

### 6. Give the credentials

If the method is `none`, go to step 7.

1. For `oauth`, check that the server has OAuth metadata and an OAuth client. For `oauth-client-credentials`, check that it has OAuth metadata. Read **OAuth setup** in [references/credentials.md](references/credentials.md).
2. If the scope is `server`, call `getMcpServerCredentialsAuthorizeUrl({ serverSlug, scope: 'server', returnTo: 'thank-you-page' })`. Give the returned `url` to the user. For a shared OAuth login, tell the user that everyone who uses the credential will act as the account that signs in.
3. If the scope is `user`, each user can authorize when Gatana asks for a credential. To set up the current user now, get a link with `scope: 'user'`.

Setting credentials on a `stdio` or `hosted` server restarts it.

### 7. Check the tools

Refresh the tool list after the server is enabled and has the credentials it needs for refresh.

- **CLI.** Run `gatana tools refresh --server <slug>`.
- **REST API.** Send `POST /api/v1/tools/refresh?serverSlug=<slug>` with `Accept: text/event-stream`.
- **Dashboard.** Open the server's **Tools** tab and click **Refresh** or **Refresh tools**.

To read the cached list, call `listMcpServerTools({ serverSlug })`.

If the server has no tools, check that it is enabled. Check the refresh result for a credential or connection error. For `stdio` and `hosted` servers, `gatana deploy logs <slug>` shows the output of the process.

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

An organization owner can create a profile.

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

When an MCP tool returns `errorCode: "need-credentials"` with an `authorizeUrl`, give the user the link. The link opens without a Gatana sign-in. After the user authorizes, try the call again. If the message says that only an administrator can provide the credential, tell the user to contact their Gatana administrator.

Full details, OAuth setup and the per-transport table: [references/credentials.md](references/credentials.md). Docs: [Credentials](https://docs.gatana.ai/credentials/).

## Troubleshooting

| Symptom                                                 | Cause and fix                                                                                                                                           |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `400 Failed body validation` with `"input":{}`          | The `{ body: {...} }` wrapper is missing.                                                                                                               |
| `A server with this slug already exists`                | Choose another slug.                                                                                                                                    |
| Server created but disabled                             | The plan limit is reached. Creating a server is free. Enabling it counts. The user must raise the limit or disable another server.                      |
| `No permission to create a server`                      | The organization does not let members add this kind of server. An owner can change it in **Settings**.                                                  |
| `Cannot refresh tools: no server-scoped credential exists` | Set a shared credential if the server should use one. For a user-scoped server, set `toolRefreshCredentialPolicy` to `any`, or use `skip` if the tool list needs no login. |
| Server lists no tools                                   | Check that it is enabled, then check the refresh result. See step 7.                                                                                     |
| `need-credentials`                                      | A credential is missing or the provider rejected it. Give the user the `authorizeUrl` if the result includes one.                                         |
| A profile lost all its servers                          | An older Gatana version got IDs in `serverIds`. Send slugs.                                                                                             |
| A user cannot see a server                              | Check all four access reasons in step 8. An empty member list does not mean that nobody has access.                                                     |
| The interactive view of a tool (an MCP App) does not show | The client must support MCP Apps, and a session in Code Mode shows an app only for a promoted tool. See **MCP Apps** in [references/servers.md](references/servers.md#mcp-apps). |

## References

- [references/servers.md](references/servers.md): each transport in full, with examples, hosted code and OpenAPI.
- [references/credentials.md](references/credentials.md): methods, scopes, OAuth setup, authorize links, secret stores.
- [references/profiles.md](references/profiles.md): all profile settings, how profiles apply, tool configuration.
- [references/api.md](references/api.md): operation names for MCP, Code Mode, REST and the CLI.
- [references/signup.md](references/signup.md): create an organization with `gatana signup`, for a user who has none.
- Website: [www.gatana.ai](https://www.gatana.ai). Guides: [What is an MCP gateway?](https://www.gatana.ai/guides/what-is-an-mcp-gateway), [How to run serverless functions as MCP tools](https://www.gatana.ai/guides/run-serverless-functions-as-mcp-tools).
- Documentation: [docs.gatana.ai](https://docs.gatana.ai/). Start with [Quick start](https://docs.gatana.ai/quick-start/).
