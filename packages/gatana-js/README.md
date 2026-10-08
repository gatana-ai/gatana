# gatana-sdk

[![npm](https://img.shields.io/npm/v/gatana-sdk)](https://www.npmjs.com/package/gatana-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

JavaScript and TypeScript SDK for the [Gatana](https://gatana.ai) API. It is generated from the
backend's OpenAPI documents with [`@hey-api/openapi-ts`](https://heyapi.dev), and adds the loading
of the credentials.

## Install

```bash
npm install gatana-sdk
```

## Usage

```typescript
import { Gatana } from 'gatana-sdk';

// Reads GATANA_API_KEY and GATANA_ORG_ID, or ~/.gatana.config
const client = new Gatana();

const { data: servers } = await client.api.listMcpServers();
```

Each operation of the API is a function on `client.api`. A call returns `{ data, request, response }`
and throws when the response is an error.

The SDK finds the credentials in the same way as the CLI. See
[Configuration](https://github.com/gatana-ai/gatana#configuration) for the environment variables and
the config file. Run `gatana config login <org>` to write the config file. The SDK refreshes expired
OIDC tokens from that file and writes the new tokens back.

### Custom authentication

Give the credentials in code:

```typescript
import { Gatana } from 'gatana-sdk';

// An API key or a personal access token, and an organization ID or a base URL
const client = new Gatana({ options: { apiKey: 'gk_...', orgId: 'my-org' } });
```

Give a token function, for example to read the token from a vault:

```typescript
const client = new Gatana({
  config: {
    baseUrl: 'https://my-org.gatana.ai',
    token: async () => readTokenFromVault(),
  },
});
```

Or select the strategies, in the order you want:

```typescript
import { Gatana, ConfigLoader, EnvConfigStrategy, FileConfigStrategy } from 'gatana-sdk';

// Use the environment, then the "other-org" entry of ~/.gatana.config
const client = new Gatana({
  configLoader: new ConfigLoader([new EnvConfigStrategy(), new FileConfigStrategy('other-org')]),
});
```

### V2 API client

`Gatana2` is the client for the v2 API at `/api/v2/`. In this API, you can send the object that a
GET returns back in a POST, PUT or PATCH request.

```typescript
import { Gatana2 } from 'gatana-sdk';

const client = new Gatana2();
const { data: servers } = await client.api.listServersV2();
```

`Gatana2` takes the same constructor arguments as `Gatana`.

### Exports

| Export                  | Description                                                   |
| ----------------------- | ------------------------------------------------------------- |
| `Gatana`                | V1 API client. Wraps the generated SDK at `/api/v1/`          |
| `Gatana2`               | V2 API client. REST-style API at `/api/v2/`                   |
| `ConfigLoader`          | Tries the config strategies in order                          |
| `ConfigStrategy`        | Abstract base class for a config strategy                     |
| `OptionsConfigStrategy` | Credentials from `{ apiKey, orgId }` or `{ apiKey, baseUrl }` |
| `EnvConfigStrategy`     | Credentials from environment variables                        |
| `FileConfigStrategy`    | Credentials from `~/.gatana.config`, with token refresh       |

Subpath exports:

| Import              | What it holds                                    |
| ------------------- | ------------------------------------------------ |
| `gatana-sdk/api`    | The generated v1 functions and types             |
| `gatana-sdk/apiv2`  | The generated v2 functions and types             |
| `gatana-sdk/config` | Functions that read and write `~/.gatana.config` |

### Debugging

The SDK logs with the [`debug`](https://www.npmjs.com/package/debug) package:

```bash
# General debug output
DEBUG=gatana node your-script.js

# HTTP requests and responses
DEBUG=gatana:http node your-script.js
```

## Development

Run these from the repository root.

```bash
just install    # install the dependencies
just build      # build the SDK into packages/gatana-js/dist
just dev        # build again on each change
just generate   # regenerate the v1 and v2 clients from the OpenAPI documents, then build
just pack       # build and pack the SDK, without publishing
just fmt        # format with prettier
```

`gensdk.ts` runs the generator on the OpenAPI documents of `hello.gatana.ai`. To use a local
backend, set `OVERRIDE_OPENAPI_URL` to its v1 document, for example
`https://acme.local.gatana.ai/api/v1/openapi.json`. Do not edit the files in
`src/api/` and `src/apiv2/` by hand: `just generate` overwrites them. The hand-written code is in
`src/index.ts`, `src/v2.ts` and `src/config.ts`.

### Releasing

`just release` in the repository root releases every package with changes, this one included. To
release only this package, run `just js-release`. It checks the npm login, asks for the version bump,
builds, publishes to npm, and tags `gatana-sdk@<version>`. The GitHub release is not marked as
latest, because `releases/latest` belongs to the CLI.

## License

[MIT](https://github.com/gatana-ai/gatana/blob/main/LICENSE)
