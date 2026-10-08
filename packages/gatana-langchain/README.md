# gatana-langchain

[![PyPI](https://img.shields.io/pypi/v/gatana-langchain)](https://pypi.org/project/gatana-langchain/)
[![Python](https://img.shields.io/pypi/pyversions/gatana-langchain)](https://pypi.org/project/gatana-langchain/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A [LangChain sandbox backend](https://docs.langchain.com/oss/python/deepagents/sandboxes) for [Gatana](https://www.gatana.ai). Use Gatana sandboxes as isolated execution environments for LangChain [deep agents](https://docs.langchain.com/oss/python/deepagents/harness).

## Features

- Drop-in sandbox backend for LangChain's `deepagents` framework
- Isolated command execution, file upload/download, and full filesystem tool support
- Auto-creates and cleans up sandboxes via context manager
- Fully typed with [PEP 561](https://peps.python.org/pep-0561/) support
- Python 3.11+

## Installation

```bash
pip install gatana-langchain
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add gatana-langchain
```

## Basic usage

Create a Gatana sandbox and pass it as the `backend` to a deep agent. The agent gets filesystem tools (`ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep`) and an `execute` tool for running shell commands — all inside the sandbox.

```python
from gatana_client import GatanaClient
from langchain_anthropic import ChatAnthropic

from deepagents import create_deep_agent
from gatana_langchain import GatanaSandbox

# Env variables: GATANA_API_KEY and GATANA_ORG_ID
# Or, ~/.gatana.config

client = GatanaClient()

with GatanaSandbox(client=client) as backend:
    agent = create_deep_agent(
        model=ChatAnthropic(model="claude-sonnet-4-20250514"),
        system_prompt="You are a coding assistant with sandbox access.",
        backend=backend,
    )

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Create a Python script that prints the Fibonacci sequence and run it",
                }
            ]
        }
    )
    print(result["messages"][-1].content)
# Sandbox is automatically deleted when the `with` block exits.
```

See the [`gatana-client` configuration](https://github.com/gatana-ai/gatana/tree/main/packages/gatana-python#configuration) for the environment variables and the `~/.gatana.config` file. You can also pass credentials explicitly:

```python
client = GatanaClient(org_id="YOUR_ORG_ID", token="your-gatana-pat")
```

### Wrapping an existing sandbox

If you already have a sandbox ID (e.g. from a previous session), pass it directly. The sandbox will **not** be auto-deleted on exit:

```python
backend = GatanaSandbox(client=client, sandbox_id="existing-sandbox-id")
result = backend.execute("echo hello from existing sandbox")
print(result.output)
```

### Running commands directly

You can call `execute()` without creating an agent:

```python
with GatanaSandbox(client=client) as backend:
    result = backend.execute("python --version")
    print(result.output)  # e.g. "Python 3.12.0\n"
    print(result.exit_code)  # 0
```

### Uploading and downloading files

Seed the sandbox with files before the agent runs, or retrieve artifacts afterwards:

```python
with GatanaSandbox(client=client) as backend:
    # Upload files into the sandbox
    backend.upload_files(
        [
            ("/src/main.py", b"print('Hello')\n"),
            ("/pyproject.toml", b"[project]\nname = 'my-app'\n"),
        ]
    )

    # Run the agent or execute commands...
    backend.execute("cd /src && python main.py")

    # Download artifacts from the sandbox
    results = backend.download_files(["/src/main.py"])
    for r in results:
        if r.content is not None:
            print(f"{r.path}: {r.content.decode()}")
        else:
            print(f"Failed to download {r.path}: {r.error}")
```

## Development

This package holds the Python dev setup for both Python packages in this repository: the dev
dependency groups, the ruff, mypy and pytest config, the pre-commit hook and the tests. It installs
`gatana-client` from `packages/gatana-python` in editable mode. You need
[uv](https://docs.astral.sh/uv/) and [just](https://github.com/casey/just).

Run these from the repository root:

```bash
just py-init        # install the dependencies and the pre-commit hook
just py-install     # install the dependencies only
just py-lint        # ruff check and format check
just py-format      # format and fix lint issues
just py-typecheck   # mypy on gatana_langchain
just py-test        # pytest
just py-test-cov    # pytest with a coverage report
just py-build gatana-langchain   # build the sdist and wheel into dist/
just py-clean       # remove build artifacts and caches
```

### Releasing

`just release` in the repository root releases every package with changes, this one included. To
release only this package:

```bash
just py-release gatana-langchain patch           # checks, tag and GitHub release
just py-release gatana-langchain patch publish   # also publish to PyPI
```

`py-release` runs the lint, type check and tests first. It needs a clean package folder.

## License

[MIT](https://github.com/gatana-ai/gatana/blob/main/LICENSE). Copyright (c) 2026 Gatana.
