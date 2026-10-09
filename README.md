<div align="center">
  <img alt="Gatana Logo" height="86" src="https://gatana.gatana.ai/favicon-prod.png" width="86">
  <h1 align="center"><b>gatana</b></h1>
  <p align="center">🚀 CLI and SDKs for Gatana</p>
</div>
<br/>

<p align="center">
  <a href="https://opensource.org/license/mit" rel="nofollow"><img src="https://img.shields.io/github/license/gatana-ai/gatana" alt="MIT License"></a>
  <a href="https://www.npmjs.com/package/gatana" rel="nofollow"><img src="https://img.shields.io/npm/v/gatana?label=gatana%20(cli)" alt="gatana CLI on npm" /></a>
  <a href="https://www.npmjs.com/package/gatana-sdk" rel="nofollow"><img src="https://img.shields.io/npm/v/gatana-sdk?label=gatana-sdk" alt="gatana-sdk on npm" /></a>
  <a href="https://pypi.org/project/gatana-client/" rel="nofollow"><img src="https://img.shields.io/pypi/v/gatana-client?label=gatana-client" alt="gatana-client on PyPI" /></a>
  <a href="https://pypi.org/project/gatana-langchain/" rel="nofollow"><img src="https://img.shields.io/pypi/v/gatana-langchain?label=gatana-langchain" alt="gatana-langchain on PyPI" /></a>
</p>

<p align="center">
  <a href="https://gatana.ai">Homepage</a>
  <span>&nbsp;•&nbsp;</span>
  <a href="https://docs.gatana.ai/">Documentation</a>
  <span>&nbsp;•&nbsp;</span>
  <a href="https://discord.gg/6TvjvmSP">Discord</a>
</p>

<br/>

This monorepo holds the Gatana CLI and the Gatana SDKs for JavaScript and Python.

| Package                                         | Install                        | What it is                                                      |
| ----------------------------------------------- | ------------------------------ | --------------------------------------------------------------- |
| [`gatana`](packages/gatana-cli)                 | `npm install -g gatana`        | CLI for servers, tools, credentials and skills. Written in Rust |
| [`gatana-sdk`](packages/gatana-js)              | `npm install gatana-sdk`       | JavaScript and TypeScript SDK for the Gatana API                |
| [`gatana-client`](packages/gatana-python)       | `pip install gatana-client`    | Python client for the Gatana API, generated from OpenAPI        |
| [`gatana-langchain`](packages/gatana-langchain) | `pip install gatana-langchain` | LangChain sandbox backend that runs agents in Gatana sandboxes  |

Each package folder has its own README with usage, examples and development steps.

---

## CLI Quick start

```bash
npm install -g gatana
brew install gatana-ai/tap/gatana
curl -fsSL https://github.com/gatana-ai/gatana/releases/latest/download/install.sh | sh
```

```bash
gatana install
```

`install` signs you in and connects the AI agents on this machine (Claude Code, Codex, Hermes,
OpenClaw) to Gatana: the gateway as an MCP server, the skills of your organization and the hook
that keeps them current. See the [CLI README](packages/gatana-cli/README.md#quick-start).

```bash
gatana config login
gatana get servers
```

The login opens the browser, where you choose your organization. It writes `~/.gatana.config`. The SDKs read the same file, see [Configuration](#configuration).

---

## Configuration

All packages find the credentials in the same way. They use the first source that is complete:

1. **Options in code** (SDKs only): an API key, and an organization ID or a base URL.
2. **Environment variables**: `GATANA_API_KEY`, and `GATANA_ORG_ID` or `GATANA_BASE_URL`.
3. **Config file**: `~/.gatana.config`.

### Environment variables

| Variable          | Description                                                   |
| ----------------- | ------------------------------------------------------------- |
| `GATANA_API_KEY`  | API key or personal access token                              |
| `GATANA_ORG_ID`   | Organization ID. The base URL is `https://<org-id>.gatana.ai` |
| `GATANA_BASE_URL` | Base URL of the organization, instead of the ID               |

### Config file

The config file `~/.gatana.config` holds one entry for each organization:

```json
{
  "orgs": {
    "my-org": {
      "baseUrl": "https://my-org.gatana.ai",
      "pat": "gk_...",
      "tokens": {
        "access_token": "...",
        "refresh_token": "...",
        "expires_at": 1760000000
      },
      "clientId": "apx_..."
    }
  },
  "defaultOrgId": "my-org",
  "apexClients": { "https://gatana.ai": "apx_..." }
}
```

- **`pat`**: a personal access token. `gatana config login my-org --pat <token>` writes it.
- **`tokens`**: OIDC tokens from a login in the browser. `gatana config login` writes them.
  The CLI and the JavaScript SDK refresh them when they expire.
- **`clientId`**: the OAuth client the tokens belong to, when the login went through gatana.ai
  (`gatana config login` without an organization). Without it, the tokens belong to `<org-id>-cli`.
- **`apexClients`**: the client the CLI registered at gatana.ai (or at the address given with
  `--base-url`). The CLI uses it again at the next login, so you approve the CLI only once.
- **`defaultOrgId`**: the organization to use when `GATANA_ORG_ID` is not set.
  `gatana config set-default` changes it.

Use the `gatana config` commands to change the file. The CLI writes it readable by the owner only
(mode 600), because it holds tokens.

---

## Development

Run the tasks from the repository root with [just](https://github.com/casey/just). `just` with no
arguments lists all recipes.

| Package                             | Recipe prefix | Examples                        |
| ----------------------------------- | ------------- | ------------------------------- |
| `gatana-cli`                        | `rs-`         | `just rs-build`, `just rs-test` |
| `gatana-sdk`                        | none          | `just build`, `just generate`   |
| `gatana-client`, `gatana-langchain` | `py-`         | `just py-init`, `just py-test`  |

The README of each package lists its recipes. Files for one language stay in the package folders,
not in the repository root.

### Project structure

```
packages/
  gatana-cli/        # CLI, written in Rust (npm: gatana)
  gatana-js/         # JavaScript/TypeScript SDK (npm: gatana-sdk)
  gatana-python/     # Python client, generated (PyPI: gatana-client)
  gatana-langchain/  # LangChain sandbox backend (PyPI: gatana-langchain)
                     # Also holds the Python dev setup for both Python packages
scripts/
  release.sh         # Releases every package that changed
```

---

## Releasing

`just release` releases every package that has commits since its last release tag. It asks for a
version bump for each of these packages, checks the git state, the logins and the tools, and shows
one summary. Then it runs the release of each package. Each release commits, tags and pushes on its
own.

```bash
just release            # release the packages with changes
just release --dry-run  # stop after the summary
just release-force      # also offer the packages without changes
```

| Package            | Published to          | Tag                           |
| ------------------ | --------------------- | ----------------------------- |
| `gatana-sdk`       | npm, GitHub           | `gatana-sdk@<version>`        |
| `gatana-cli`       | GitHub, npm, Homebrew | `gatana@<version>`            |
| `gatana-client`    | GitHub, PyPI          | `gatana-client/v<version>`    |
| `gatana-langchain` | GitHub, PyPI          | `gatana-langchain/v<version>` |

Only CLI releases are marked as latest on GitHub. The CLI's `install.sh` downloads from
`releases/latest`, so the other packages must not take that place.

After a failure, run `just release` again. A package that was released has no changes any more.

---

## License

MIT License, see [LICENSE](LICENSE).

## Contributing

We welcome contributions!

1. Fork the repository.
2. Create a feature branch.
3. Make your changes.
4. Add tests if applicable.
5. Submit a pull request.
