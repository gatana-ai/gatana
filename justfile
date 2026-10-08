# Default recipe: list all available commands
default:
    @just --list

# Build the SDK
build:
    pnpm -r build

# Watch the SDK for changes
dev:
    pnpm -r --parallel dev

# Run the SDK tests
test:
    pnpm -r test

# Regenerate API clients from OpenAPI specs and rebuild the SDK
generate:
    pnpm --filter gatana-sdk generate
    pnpm --filter gatana-sdk build

# Install all dependencies
install:
    pnpm install

# Format code with prettier
fmt:
    pnpm exec prettier --write .

# Check formatting without writing
fmt-check:
    pnpm exec prettier --check .

# Release the SDK with change detection
release *ARGS:
    ./scripts/release.sh {{ARGS}}

# Release the SDK even without changes
release-force *ARGS:
    ./scripts/release.sh --force {{ARGS}}

# Dry-run: build and pack the SDK without publishing
pack:
    pnpm -r build
    cd packages/gatana-js && pnpm pack

# Clean all build artifacts
clean:
    rm -rf packages/gatana-js/dist

# ── Rust CLI (packages/gatana-cli) ────────────────────────────────────

rs_manifest := "packages/gatana-cli/Cargo.toml"

# Build the Rust CLI; the binary is packages/gatana-cli/target/release/gatana
rs-build:
    cargo build --release --manifest-path {{rs_manifest}} -p gatana-cli

# Run the Rust CLI from source
rs *ARGS:
    cargo run -q --manifest-path {{rs_manifest}} -p gatana-cli -- {{ARGS}}

# Test, lint and format-check the Rust crates
rs-test:
    cargo test --manifest-path {{rs_manifest}} --workspace
    cargo clippy --manifest-path {{rs_manifest}} --workspace --all-targets -- -D warnings
    cargo fmt --manifest-path {{rs_manifest}} --all --check

# Build the release binaries for every platform into packages/gatana-cli/dist/<version>/ (needs Docker)
rs-dist:
    packages/gatana-cli/scripts/dist.sh

# Release the Rust CLI to GitHub, npm and Homebrew; --dry-run only builds and stages
rs-release *ARGS:
    packages/gatana-cli/scripts/release.sh {{ARGS}}

# Regenerate the gatana-api crate from the backend's OpenAPI documents (e.g. base_url=https://acme.local.gatana.ai)
generate-rs base_url="https://hello.gatana.ai":
    cargo run -q --manifest-path {{rs_manifest}} -p gatana-codegen -- --base-url {{base_url}}
    cargo build -q --manifest-path {{rs_manifest}} -p gatana-api

# ── Python (packages/gatana-python, packages/gatana-langchain) ────────
#
# Recipes with a pkg take the PyPI name: gatana-client (the folder is
# packages/gatana-python) or gatana-langchain. The dev environment and tool
# config live in packages/gatana-langchain, which installs gatana-client from
# its folder.

py_dev := "packages/gatana-langchain"

# Print the folder of a Python package, by its PyPI name
_py-dir pkg:
    #!/usr/bin/env bash
    case "{{ pkg }}" in
      gatana-client) echo packages/gatana-python ;;
      gatana-langchain) echo packages/gatana-langchain ;;
      *) echo "unknown Python package '{{ pkg }}': use gatana-client or gatana-langchain" >&2; exit 1 ;;
    esac

# Set up the Python dev environment and the pre-commit hook
py-init: py-install
    cd {{py_dev}} && uv run pre-commit install --config .pre-commit-config.yaml

# Install the Python dependencies (including dev)
py-install:
    cd {{py_dev}} && uv sync --all-groups

# Lint the Python code
py-lint:
    cd {{py_dev}} && uv run ruff check . && uv run ruff format --check .

# Format the Python code and fix lint issues
py-format:
    cd {{py_dev}} && uv run ruff format . && uv run ruff check --fix .

# Type-check gatana-langchain
py-typecheck:
    cd {{py_dev}} && uv run mypy gatana_langchain

# Run the Python tests
py-test:
    cd {{py_dev}} && uv run pytest

# Run the Python tests with a coverage report
py-test-cov:
    cd {{py_dev}} && uv run pytest --cov --cov-report=term-missing

# Build a Python package (sdist + wheel) into its dist/
py-build pkg:
    #!/usr/bin/env bash
    set -euo pipefail
    DIR=$(just _py-dir {{ pkg }})
    cd "$DIR"
    uv build

# Build all Python packages
py-build-all:
    just py-build gatana-client
    just py-build gatana-langchain

# Publish a Python package to PyPI (builds first)
py-publish pkg: (py-build pkg)
    #!/usr/bin/env bash
    set -euo pipefail
    DIR=$(just _py-dir {{ pkg }})
    PKG_UNDER=$(echo "{{ pkg }}" | tr '-' '_')
    UV_PUBLISH_TOKEN=$(uv auth token pypi) uv publish __token__ "$DIR"/dist/${PKG_UNDER}*

# Publish all Python packages to PyPI
py-publish-all:
    just py-publish gatana-client
    just py-publish gatana-langchain

# Release a Python package: run checks, bump the version, build, commit, tag and make a GitHub release; publish="publish" also uploads to PyPI
py-release pkg bump publish="":
    #!/usr/bin/env bash
    set -euo pipefail
    DIR=$(just _py-dir {{ pkg }})
    # The release commit takes only this folder, so it must not hold other work
    if [[ -n $(git status --porcelain -- "$DIR") ]]; then
      echo "$DIR has uncommitted changes; commit or stash them first" >&2
      exit 1
    fi
    echo "🔍 Running checks before release..."
    just py-lint
    just py-typecheck
    just py-test
    echo "✅ All checks passed. Bumping {{ bump }} version for {{ pkg }}..."
    pushd "$DIR" > /dev/null
    bumpsemver --no-commit --no-tag {{ bump }}
    NEW_VERSION=$(grep 'current_version = ' .bumpsemver.cfg | cut -d= -f2 | tr -d '[:space:]')
    popd > /dev/null
    echo "🏷️  {{ pkg }} version bumped to $NEW_VERSION"
    just py-clean
    just py-build {{ pkg }}
    TAG="{{ pkg }}/v${NEW_VERSION}"
    git commit -m "release({{ pkg }}): v${NEW_VERSION}" -- "$DIR"
    git tag "$TAG" -m "release: {{ pkg }} v${NEW_VERSION}"
    echo "✅ Released {{ pkg }} v${NEW_VERSION}"
    git push && git push origin "$TAG"
    PKG_UNDER=$(echo "{{ pkg }}" | tr '-' '_')
    NOTES=(--generate-notes)
    PREV=$(git tag --sort=-version:refname -l '{{ pkg }}/v*' | sed -n '2p')
    if [[ -n $PREV ]]; then NOTES+=(--notes-start-tag "$PREV"); fi
    # Not marked as latest: releases/latest belongs to the CLI, whose install.sh downloads from it
    gh release create "$TAG" \
      --title "{{ pkg }} v${NEW_VERSION}" \
      --latest=false \
      "${NOTES[@]}" \
      "$DIR"/dist/${PKG_UNDER}-${NEW_VERSION}*
    if [[ "{{ publish }}" == "publish" ]]; then
      echo "📦 Publishing {{ pkg }} to PyPI..."
      just py-publish {{ pkg }}
    fi

# Release all Python packages with the same bump level
py-release-all bump publish="":
    just py-release gatana-client {{ bump }} {{ publish }}
    just py-release gatana-langchain {{ bump }} {{ publish }}

# Regenerate gatana-python from the backend's OpenAPI spec
generate-py openapi_url="https://acme.gatana.ai/api/v1/openapi.json":
    #!/usr/bin/env bash
    set -euo pipefail

    DEST=packages/gatana-python
    PKG="$DEST/gatana_client"
    TMPDIR="$(mktemp -d)"
    trap 'rm -rf "$TMPDIR"' EXIT

    # 1. Fetch the latest OpenAPI spec
    curl -sf -o "$DEST/openapi.json" "{{ openapi_url }}"

    # 2. Generate into a temp directory
    openapi-python-client generate --path "$DEST/openapi.json" --overwrite --output-path "$TMPDIR/gatana-client"

    # 3. Copy generated code into the package, preserving hand-written files
    #    Generated artefacts: api/, models/, types.py, errors.py, _base_client.py (was client.py)
    GENPKG="$TMPDIR/gatana-client/gatana_client"

    rm -rf "$PKG/api" "$PKG/models"
    cp -R "$GENPKG/api"    "$PKG/api"
    cp -R "$GENPKG/models" "$PKG/models"
    cp    "$GENPKG/types.py"  "$PKG/types.py"
    cp    "$GENPKG/errors.py" "$PKG/errors.py"
    cp    "$GENPKG/client.py" "$PKG/_base_client.py"

    # 4. pyproject.toml — keep ours, but sync if the generator added a new one
    if [ -f "$TMPDIR/gatana-client/pyproject.toml" ] && ! grep -q '^\[project\]' "$DEST/pyproject.toml"; then
      HEADER='[project]\nname = "gatana-client"\nversion = "0.1.0"\ndescription = "A client library for accessing Gatana"\nrequires-python = ">=3.10"\ndependencies = [\n    "httpx>=0.23.0,<0.29.0",\n    "attrs>=22.2.0",\n    "python-dateutil>=2.8.0",\n]\n'
      printf '%b\n' "$HEADER" | cat - "$DEST/pyproject.toml" > "$DEST/pyproject.toml.tmp" && mv "$DEST/pyproject.toml.tmp" "$DEST/pyproject.toml"
    fi

    echo "✅ SDK regenerated in $PKG/"
    echo "   Hand-written files preserved: client.py, config.py, __init__.py, py.typed"

# Remove the Python build artifacts and caches
py-clean:
    rm -rf packages/gatana-python/dist packages/gatana-python/build packages/gatana-python/.ruff_cache
    cd {{py_dev}} && rm -rf dist build .mypy_cache .pytest_cache .ruff_cache htmlcov .coverage coverage.xml
    find packages/gatana-python packages/gatana-langchain -name .venv -prune -o -type d -name __pycache__ -prune -exec rm -rf {} +
