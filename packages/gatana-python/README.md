# gatana-client

Python client for the Gatana API. Automatically generated based on Gatana OpenAPI specification using [openapi-generators/openapi-python-client](https://github.com/openapi-generators/openapi-python-client)

## Usage

The easiest way to get started is with `GatanaClient`, which resolves configuration automatically from explicit parameters, environment variables, or `~/.gatana.config`.

More information about the `.gatana.config` file, can be found [here in the Gatana Tools CLI repository](https://github.com/gatana-ai/gatana-js/blob/main/README.md#config-file)

```python
from gatana_client import GatanaClient

# Explicit
client = GatanaClient(token="sk-...", org_id="my-org")

# Or zero-config — picks up GATANA_API_KEY + GATANA_ORG_ID env vars,
# or falls back to ~/.gatana.config
client = GatanaClient()
```

### Configuration priority

1. Explicit `token` + `org_id` (or `base_url`) passed to `GatanaClient`
2. Environment variables: `GATANA_API_KEY`, `GATANA_ORG_ID` / `GATANA_BASE_URL`
3. Config file: `~/.gatana.config`

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

Every endpoint module exposes four functions:

| Function | Description |
|---|---|
| `sync` | Blocking, returns parsed data or `None` |
| `sync_detailed` | Blocking, returns full `Response` |
| `asyncio` | Async version of `sync` |
| `asyncio_detailed` | Async version of `sync_detailed` |
