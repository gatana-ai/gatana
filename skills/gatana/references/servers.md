# Servers in Gatana

Use this file when you add or change a server. The examples use Code Mode. Over plain MCP, call `gatana-api_<operation>` with the same arguments. Over REST, send the `body` value as the JSON request body.

Docs: [Tool servers](https://docs.gatana.ai/tool-servers-fundamentals/), [Adding a server](https://docs.gatana.ai/gateway-introduction/), [Standard MCP](https://docs.gatana.ai/servers-standard-mcp/), [Runnable code](https://docs.gatana.ai/servers-runnable-code/), [OpenAPI](https://docs.gatana.ai/servers-openapi-swagger/), [Persistent storage](https://docs.gatana.ai/persistent-storage/), [Tailscale](https://docs.gatana.ai/tailscale/). Guide: [How to run serverless functions as MCP tools](https://www.gatana.ai/guides/run-serverless-functions-as-mcp-tools).

## Contents

- [The server record](#the-server-record)
- [Remote server: httpstreaming and sse](#remote-server-httpstreaming-and-sse)
- [Executable app: stdio](#executable-app-stdio)
- [Hosted code: hosted](#hosted-code-hosted)
- [OpenAPI specification: openapi](#openapi-specification-openapi)
- [Change a server](#change-a-server)
- [Tools of a server](#tools-of-a-server)
- [Dashboard steps](#dashboard-steps)

## The server record

`createServerV2` needs `slug` and one of these two fields:

- `transportConfig`: the full configuration. Use it when you know the address, the command or the specification.
- `transportConfigType`: only the kind (`httpstreaming`, `sse`, `stdio`, `hosted` or `openapi`). Gatana makes a default configuration. Fill it in later with `patchServerV2`.

Optional fields:

| Field                                       | Default                | Meaning                                                          |
| ------------------------------------------- | ---------------------- | ---------------------------------------------------------------- |
| `description`                               | empty                  | Shown to people and to the model. Say what the server is for.    |
| `visibility`                                | `private`              | `organization` lets every member use the server.                 |
| `isEnabled`                                 | `true`                 | A disabled server keeps its configuration and has no tools.      |
| `authorization`                             | `none`, `server` scope | See [credentials.md](credentials.md).                            |
| `oauthMetadata`, `oauthClientConfiguration` | none                   | OAuth setup. See [credentials.md](credentials.md#oauth-setup).   |
| `timeoutProtocol`, `timeoutTotal`           | organization default   | Seconds for one protocol request, and for one tool call.         |
| `resetTimeoutOnProgressNotification`        |                        | A progress notification resets the protocol timeout.             |
| `isOutputCompressionEnabled`                | `true`                 | Large outputs are compressed and indexed.                        |
| `firewallRules`                             | none                   | `[{ condition: '<CEL>', action: 'deny' \| 'log' \| 'modify' }]`. |

The slug: lowercase letters, digits and hyphens, starts with a letter or digit, 20 characters or fewer, unique in the organization.

## Remote server: httpstreaming and sse

The server runs somewhere else. Gatana connects to its URL.

```typescript
await codemode.gatanaApi.createServerV2({
  body: {
    slug: 'linear',
    description: 'Linear issues and projects',
    transportConfig: { type: 'httpstreaming', url: 'https://mcp.linear.app/mcp' },
    authorization: { method: 'oauth', credentialsScope: 'user', toolRefreshCredentialPolicy: 'any' },
  },
});
```

- `url`: the MCP endpoint. It can hold a credential expression, for example `https://example.com/mcp?key={{ credentials.keys.API_KEY }}`.
- `headers`: `[name, value]` pairs. Values can hold credential expressions and secret references.
- Use `sse` only for a server that still speaks the Server-Sent Events transport.
- An OAuth server needs OAuth metadata and a client before anybody can sign in. See [credentials.md](credentials.md#oauth-setup).

## Executable app: stdio

Gatana starts the command in a container, in an isolated virtual machine (Kata Containers, Debian Bookworm). Use it for `npx` and `uvx` servers. It needs a paid plan, and the organization must let members add local servers.

```typescript
// "@acme/mcp-server" is a placeholder. Use the package that the vendor documents.
await codemode.gatanaApi.createServerV2({
  body: {
    slug: 'acme',
    description: 'Acme tickets, read and write',
    transportConfig: {
      type: 'stdio',
      command: 'npx -y @acme/mcp-server',
      transport: 'stdio',
      env: [['ACME_API_KEY', '{{ credentials.keys.ACME_API_KEY }}']],
    },
    authorization: {
      method: 'apikey',
      apikeys: ['ACME_API_KEY'],
      credentialsScope: 'server',
      toolRefreshCredentialPolicy: 'server-scoped',
    },
  },
});
```

| Field                 | Meaning                                                                                                                              |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `command`             | The command line. It can hold `{{ credentials.keys.X }}` and secret references.                                                      |
| `transport`           | What the process speaks: `stdio`, `httpstreaming` or `sse`.                                                                          |
| `httpPort`, `urlPath` | For an HTTP process: the port it listens on, and the path of its MCP endpoint.                                                       |
| `dockerImage`         | A different image to run the command in.                                                                                             |
| `env`                 | `[name, value]` pairs.                                                                                                               |
| `healthCheck`         | `{ enabled, url, delaySeconds, intervalSeconds, failureThreshold }` for an HTTP process.                                             |
| `requests`            | CPU and memory to reserve.                                                                                                           |
| `storage`             | `{ enabled: true }` gives a persistent volume at the path in `GATANA_DATA_DIR`.                                                      |
| `tailscale`           | `{ enabled: true, authKey, hostname? }` lets the process reach hosts on the organization's tailnet. Use a tagged, non-ephemeral key. |

Files: upload service-account files and similar with `createMcpServerFile`, or in the dashboard. They appear in the working folder of the process.

**Credential limit:** `command` and `env` are filled one time, when Gatana starts the process, with the **server-scoped** credential. A user-scoped API key never reaches them. For per-user OAuth, the process must speak HTTP (`transport: 'httpstreaming'` or `'sse'`). Gatana then adds `Authorization: Bearer <token>` to each request. OAuth is not possible for a process with `transport: 'stdio'`.

Gatana deploys the server when you create or change it. Check it with `getMcpServerRunningStatus({ serverSlug })`, or with `gatana deploy get <slug>` and `gatana deploy logs <slug>`.

## Hosted code: hosted

Gatana runs your tool functions in Node.js 24 or Python 3.13. It needs a paid plan.

With the CLI, which is the easiest way:

```bash
gatana faas init my-tools          # makes a Node.js template
gatana faas verify my-tools        # checks the package (needs Node.js)
gatana faas run my-tools add -p a=1 -p b=2
gatana faas upload my-tools-server my-tools --create   # creates the server, deploys, waits
```

`faas init`, `verify` and `run` work with Node.js packages. `faas upload` works with both runtimes. `--create` makes a Node.js server. For Python, create the server first with `transportConfig: { type: 'hosted', runtime: 'python313' }`, then upload.

The package needs one entry file in its root: `index.js` (Node.js) or `main.py` (Python). It exports `schema` and one function per tool:

```javascript
import z from 'zod';

export const schema = {
  add: {
    description: 'Adds two numbers',
    input: z.object({ a: z.number(), b: z.number() }),
  },
};

export function add({ a, b }, credentials) {
  return String(a + b);
}
```

```python
from pydantic import BaseModel

class AddInput(BaseModel):
    a: float
    b: float

schema = {"add": {"description": "Adds two numbers", "input": AddInput}}

def add(args, credentials):
    return str(args["a"] + args["b"])
```

The second argument, `credentials`, holds the credential that Gatana resolved for this call. This is the only server kind where per-user API keys reach your code:

```javascript
{
  headers: { authorization: 'Bearer <token>' }, // for OAuth
  apikeys: [['KEY_NAME', 'value']],            // for API keys
  gatanaUserEmail: 'jane@example.com'           // null when no user called
}
```

- `env` in `transportConfig` sets environment variables. They use the server-scoped credential only.
- Node.js: put `node_modules` in the package. Python: add `requirements.txt` (installed with uv at each start, about one minute at most) or a `vendor` folder.
- The file system resets at each deploy. Turn on `storage` and write to `GATANA_DATA_DIR` to keep files.

## OpenAPI specification: openapi

Gatana makes one tool for each operation in the specification. No code runs.

```typescript
await codemode.gatanaApi.createServerV2({
  body: {
    slug: 'petstore',
    transportConfig: {
      type: 'openapi',
      method: 'specUrl',
      specUrl: 'https://petstore3.swagger.io/api/v3/openapi.json',
      baseUrl: '', // empty: use the servers entry of the specification
      headers: [['X-Api-Key', '{{ credentials.keys.PETSTORE_KEY }}']],
    },
    authorization: {
      method: 'apikey',
      apikeys: ['PETSTORE_KEY'],
      credentialsScope: 'user',
      toolRefreshCredentialPolicy: 'skip',
    },
  },
});
```

- `method: 'specUrl'` fetches the specification from `specUrl` and keeps it current. `method: 'spec'` takes the document in `spec` as a string. Use it when the URL is private or to pin a version.
- Test a URL first with `testMcpServerOpenapi`.
- The tool name comes from `operationId`. Without one, Gatana uses `<method>_<path>`.
- Use `toolRefreshCredentialPolicy: 'skip'`: reading the specification needs no credential.
- With OAuth, Gatana adds the bearer token when no `Authorization` header is set.

## Change a server

- `patchServerV2({ slug, body: { ... } })`: send only the fields to change (JSON Merge Patch). `null` clears `oauthMetadata` or `oauthClientConfiguration`.
- `updateServerV2({ slug, body })`: send the full object from `getServerV2`.
- CLI: `gatana patch server <slug> -f patch.json`, or `-p key=value`.
- Turn a server on or off: `patchServerV2({ slug, body: { isEnabled: false } })`.
- Delete: `deleteServerV2({ slug })`. This stops the process and removes the tools from all clients. Confirm with the user first.

## Tools of a server

- `listMcpServerTools({ serverSlug })`: the cached tools, also the disabled ones.
- `updateMcpServerToolIsEnabled({ serverSlug, toolName, body: { value: false } })`: turn off one tool for everybody. The field is `value`, not `isEnabled`.
- `updateMcpServerAllToolsIsEnabled({ serverSlug, body: { value: true } })`: all tools.
- `patchMcpServerTool({ serverSlug, toolName, body })`: change what clients see. Each override has a switch and a value: `overrideToolName` + `toolNameOverride`, `overrideDescription` + `descriptionOverride`, `overrideInputSchema` + `inputSchemaOverride`.
- Refresh: the dashboard **Refresh** button on the server page, or `POST /api/v1/tools/refresh?serverSlug=<slug>` with `Accept: text/event-stream`. Gatana also refreshes enabled servers every few hours. There is no `gatana-api` tool for it.

To limit tools for one group only, use a profile. See [profiles.md](profiles.md#tool-configuration).

## Dashboard steps

1. Click **Add Server** at the top right.
2. Choose one:
   - **Popular servers**: one click for well-known services. Sets up OAuth when the vendor allows it.
   - **By transport**: remote, executable app, hosted code or OpenAPI.
   - **Search MCP registries**: the official MCP registry and Glama.
   - **Built-in**: tools that Gatana provides.
3. Fill in the configuration and save.
4. On the server page, open **Settings > Authorization** for the method and scope, and **Credentials** for the values.
5. Open **Access** to add members.
