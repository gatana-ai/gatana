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
    cd packages/gatana-sdk && pnpm pack

# Clean all build artifacts
clean:
    rm -rf packages/gatana-sdk/dist

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
