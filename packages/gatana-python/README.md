# gatana-client

[![PyPI](https://img.shields.io/pypi/v/gatana-client)](https://pypi.org/project/gatana-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python client for the [Gatana](https://gatana.ai) API. It is generated from the backend's OpenAPI
document with [openapi-python-client](https://github.com/openapi-generators/openapi-python-client),
and adds the loading of the credentials. Python 3.10+.

## Install

```bash
pip install gatana-client
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add gatana-client
```

## Usage

The easiest way to start is `GatanaClient`. It finds the configuration in parameters, environment
variables or `~/.gatana.config`.

```python
from gatana_client import GatanaClient

# Explicit
client = GatanaClient(token="gk_...", org_id="my-org")

# Or no configuration in code: reads GATANA_API_KEY and GATANA_ORG_ID,
# or else ~/.gatana.config
client = GatanaClient()
```

### Configuration

`GatanaClient` uses the first source that is complete:

1. `token`, and `org_id` or `base_url`, passed to `GatanaClient`
2. The environment variables `GATANA_API_KEY`, and `GATANA_ORG_ID` or `GATANA_BASE_URL`
3. The config file `~/.gatana.config`

See [Configuration](https://github.com/gatana-ai/gatana#configuration) for the environment
variables and the config file, which the CLI and the JavaScript SDK also use. This package has two
differences:

- `base_url` and `GATANA_BASE_URL` are the base of the API, for example
  `https://my-org.gatana.ai/api/v1`. An organization ID gives that URL automatically.
- It does not refresh OIDC tokens from the config file. Use an API key or a personal access token
  for scripts and CI.

To select the strategies yourself, give a `config_loader`:

```python
from gatana_client import ConfigLoader, EnvConfigStrategy, FileConfigStrategy, GatanaClient

client = GatanaClient(
    config_loader=ConfigLoader([EnvConfigStrategy(), FileConfigStrategy(org_id="other-org")])
)
```

### Calling endpoints

Each API endpoint is a Python module with sync and async variants:

```python
from gatana_client.api.sandboxes import list_sandboxes

with client as client:
    sandboxes = list_sandboxes.sync(client=client)
```

Async:

```python
async with client as client:
    sandboxes = await list_sandboxes.asyncio(client=client)
```

Every endpoint module has four functions:

| Function           | Description                             |
| ------------------ | --------------------------------------- |
| `sync`             | Blocking, returns parsed data or `None` |
| `sync_detailed`    | Blocking, returns the full `Response`   |
| `asyncio`          | Async version of `sync`                 |
| `asyncio_detailed` | Async version of `sync_detailed`        |

## Development

Most of this package is generated. Run these from the repository root:

```bash
just generate-py   # download the OpenAPI document and regenerate the client
just generate-py https://acme.local.gatana.ai/api/v1/openapi.json   # from a local backend
```

The generator replaces `api/`, `models/`, `types.py`, `errors.py` and `_base_client.py` in
`gatana_client/`. These files are hand-written, and the generator keeps them: `client.py`,
`config.py`, `__init__.py` and `py.typed`.

The Python dev environment, the lint and type-check config and the tests (`tests/test_config.py`
for this package) are in
[`packages/gatana-langchain`](https://github.com/gatana-ai/gatana/tree/main/packages/gatana-langchain).
That package installs this one from its folder. See its README for the `just py-*` recipes.

### Releasing

`just release` in the repository root releases every package with changes, this one included. To
release only this package:

```bash
just py-release gatana-client patch           # tag and make a GitHub release
just py-release gatana-client patch publish   # also publish to PyPI
```

## License

[MIT](https://github.com/gatana-ai/gatana/blob/main/LICENSE)
