# Rust CLI

A port of the `gatana` CLI to Rust. It is not released yet: npm still ships the last TypeScript CLI
(3.4.3), whose source was removed from this repository. The Rust CLI reads and writes the same
`~/.gatana.config` and the same skills folders, so the two can be used side by side.

## Crates

| Crate            | What it is                                                                                                       |
| ---------------- | ---------------------------------------------------------------------------------------------------------------- |
| `gatana-api`     | Typed API client. `src/v1.rs` and `src/v2.rs` are generated; `src/lib.rs` is the hand-written runtime they call. |
| `gatana-codegen` | The generator that writes `v1.rs` and `v2.rs` from the backend's OpenAPI documents.                              |
| `gatana-cli`     | The CLI. The binary is called `gatana`.                                                                          |

## Commands

Run these from the repository root.

```sh
just rs-build                 # packages/gatana-cli/target/release/gatana
just rs get servers           # run from source
just rs-test                  # tests, clippy, format check
just generate-rs              # regenerate the client from hello.gatana.ai
just generate-rs https://acme.local.gatana.ai   # from a local backend
```

## The generated client

Only the operations listed in `crates/gatana-api/operations.json` are generated. To call a new
endpoint, add its `operationId` there and run `just generate-rs`. The build then fails wherever the
CLI uses a path parameter, query parameter, request body or response field that changed in the
backend.

The generator simplifies the schemas before typify turns them into Rust types:

- It inlines the anonymous `__schemaN` components, so types get names like `ServerDtoTransportConfig`.
- It drops validation keywords and `format`, and opens closed objects. A typed read then keeps
  working when the server adds a field or returns an old value.
- It turns unions of objects that carry a `type` tag into `#[serde(tag = "type")]` enums.
- It moves the nullability of a nullable named schema to the places that reference it.

Every operation returns a `Call`. `.value()` gives the response JSON as sent, `.typed()` gives the
generated type, and `.send()` gives both. The CLI prints the raw JSON, so `-o json` shows every field
in the server's order. It reads typed fields where it makes a decision on them.

Read raw, not typed, when the response contains a server object. Its transport configuration is a
union that the backend extends, and a command that only needs a slug must not break on a new transport.
The audit log list is also read raw, because the backend omits `onlySuperadminVisibility`, which its
schema marks as required.

## Differences from the TypeScript CLI

Fixes:

- Errors go to stderr and the exit code is 1. The TypeScript CLI printed most errors to stdout and
  exited with 0.
- With `-o json` or `-o yaml`, progress lines go to stderr, so stdout holds only the result.
- `-o` accepts only `json`, `yaml` and `table`.
- `hosted download` writes to `-O, --out-file`. Its old `-o` never worked, because the global `-o`
  took the value.
- `hosted verify` prints its result and exits with 1 when a tool is not valid. Before, it printed
  nothing.
- `hosted upload` fails, with the container's logs, when the deployment does not become ready.
  Before, it reported success. `--no-logs` now skips those logs. `--force` now also covers a module
  that does not import. Tools that fail the check are listed as warnings.
- An image pull failure during a deployment is reported with its reason. Before, it was ignored and
  the deployment counted as successful.
- `deploy wait` exits with 1 when the deployment does not become ready.
- `tool` reads its arguments from stdin when neither `-f` nor `-a` is given, as its help text says.
- The config file is written readable by the owner only (mode 600), because it holds tokens.

Changes:

- `hosted verify` and `hosted run` start `node` to load the source code. When the source folder
  cannot resolve `zod`, the CLI installs it once into its cache folder with npm and links it in for
  the run. `hosted upload` without Node.js checks `index.js` for a schema export only.
- `create server` without `--transport-type` shows a list to pick from, not a text prompt.
- `config login --no-browser` prints the link without opening a browser.
- `-o yaml` does not fold long strings at 80 columns. Tables have no trailing spaces.
- The skills manifest lists its entries in the order of the server's list, not in download order.

## Releasing

`just rs-release` (from the repository root) releases the version in `crates/gatana-cli/Cargo.toml`.
Bump that version first and commit it. `just rs-release --dry-run` builds and stages everything
without publishing anything.

The release runs on a Mac with Docker. It needs `gh` and `npm` logins, and a GPG key for the signed
tag. It does these steps:

1. `scripts/dist.sh` builds four binaries and checks that each one starts:
   - macOS arm64 and x64, with a rustup toolchain kept in `~/.cache/gatana-cli-release`
   - Linux arm64 and x64, static musl, in the `cargo-zigbuild` Docker image
2. It tags `gatana@<version>` and makes a GitHub release with one `gatana-<target>.tar.gz` and one
   `.sha256` file per target, plus `install.sh`.
3. It publishes one npm package per platform (`@gatana/cli-<os>-<cpu>`), then `gatana`. `gatana`
   has the platform packages as optional dependencies, so npm installs only the one for the
   machine. Its `bin/gatana` is a shell script that starts that binary. It is not a Node script,
   because the skills hooks run `gatana` at every session start.
4. It writes `Formula/gatana.rb` in `gatana-ai/homebrew-tap`. It asks before it creates that
   repository the first time.

A version with a pre-release part, such as `4.0.0-alpha.0`, is released as a pre-release:

- On npm it gets the dist-tag `next`, so users get it with `npm install -g gatana@next`.
- On GitHub it is not marked as latest, so `install.sh` keeps installing the previous version. Use
  `GATANA_VERSION=4.0.0-alpha.0` to install it.
- The Homebrew formula is not changed.

The release files are the source for the three ways to install a release:

```sh
npm install -g gatana
brew install gatana-ai/tap/gatana
curl -fsSL https://github.com/gatana-ai/gatana-js/releases/latest/download/install.sh | sh
```

`install.sh` puts the binary in `~/.local/bin`. `GATANA_INSTALL_DIR` changes the folder, and
`GATANA_VERSION` installs a given version.

SDK releases (`scripts/release.sh`) are not marked as latest on GitHub, so
`releases/latest/download/install.sh` always gets the newest CLI release.

## Not done yet

- Windows: the CLI has not been built or run there, and there is no Windows binary in the release.
  The npm package refuses to install on Windows.
- macOS notarization. Binaries that curl, brew or npm download do not get the quarantine flag, so
  Gatekeeper does not check them. A binary downloaded in a browser would be blocked.
- The hooks run `gatana` without a path. An agent that starts without the user's shell PATH does not
  find it in `~/.local/bin` or in an nvm folder.
- The device login was tested up to the polling step, not through an approval in the browser. The
  token refresh was not run against a server: it would rotate a real refresh token.
