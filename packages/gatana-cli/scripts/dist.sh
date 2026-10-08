#!/usr/bin/env bash
# Builds the release binaries of the gatana CLI and packs them into dist/<version>/: per target a
# gatana-<target>.tar.gz (the binary and LICENSE) with a .sha256 file, plus install.sh.
#
# The macOS binaries are built on this Mac with a rustup toolchain kept in a cache folder, so the Rust
# used for development (Homebrew's, for example) stays as it is. They cannot be built in Docker:
# reqwest and rustls link Apple frameworks, which need the macOS SDK.
#
# The Linux binaries are built in the cargo-zigbuild image: aws-lc-sys contains C code, and zig is the
# C cross compiler. They link musl statically, so one binary runs on every distribution.
set -euo pipefail

cd "$(dirname "$0")/.."

RUST_VERSION=1.96.0
ZIGBUILD_IMAGE=ghcr.io/rust-cross/cargo-zigbuild:0.23.4
MAC_TARGETS=(aarch64-apple-darwin x86_64-apple-darwin)
LINUX_TARGETS=(aarch64-unknown-linux-musl x86_64-unknown-linux-musl)
TOOLS=${GATANA_RELEASE_TOOLS:-${XDG_CACHE_HOME:-$HOME/.cache}/gatana-cli-release}

VERSION=$(sed -n 's/^version = "\(.*\)"$/\1/p' crates/gatana-cli/Cargo.toml | head -n1)
OUT=dist/$VERSION

step() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }
die() { printf '\033[31mError: %s\033[0m\n' "$1" >&2; exit 1; }

[[ $(uname -s) == Darwin ]] || die "the macOS binaries can only be built on a Mac"
command -v docker >/dev/null && docker info >/dev/null 2>&1 || die "Docker must be running to build the Linux binaries"

# ── macOS ─────────────────────────────────────────────────────────────

step "Rust $RUST_VERSION toolchain in $TOOLS"
# rustup finds its own files through RUSTUP_HOME and CARGO_HOME. They are set for rustup only: the
# builds keep the default CARGO_HOME, and with it the crates that are already downloaded.
rustup() { RUSTUP_HOME=$TOOLS/rustup CARGO_HOME=$TOOLS/cargo "$TOOLS/cargo/bin/rustup" "$@"; }
if [[ ! -x $TOOLS/cargo/bin/rustup ]]; then
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs |
    RUSTUP_HOME=$TOOLS/rustup CARGO_HOME=$TOOLS/cargo RUSTUP_INIT_SKIP_PATH_CHECK=yes \
      sh -s -- -y --quiet --no-modify-path --default-toolchain none
fi
rustup toolchain install "$RUST_VERSION" --profile minimal --target "$(IFS=,; echo "${MAC_TARGETS[*]}")"
toolchain_bin=$(dirname "$(rustup which --toolchain "$RUST_VERSION" cargo)")

for target in "${MAC_TARGETS[@]}"; do
  step "Building $target"
  # The toolchain's own cargo and rustc, not the rustup proxies: the default CARGO_HOME (and its
  # crate cache) stays in use.
  PATH="$toolchain_bin:$PATH" RUSTC="$toolchain_bin/rustc" \
    cargo build --release --locked -p gatana-cli --target "$target"
done

# ── Linux ─────────────────────────────────────────────────────────────

step "Building ${LINUX_TARGETS[*]} in $ZIGBUILD_IMAGE"
linux_args=()
for target in "${LINUX_TARGETS[@]}"; do linux_args+=(--target "$target"); done
# A separate target folder: the container's rustc is a different compiler from the one on the Mac. The
# volume keeps the downloaded crates between builds.
docker run --rm \
  -v "$PWD":/io -w /io \
  -v gatana-cli-cargo-registry:/usr/local/cargo/registry \
  -e CARGO_TARGET_DIR=/io/target/zigbuild \
  "$ZIGBUILD_IMAGE" \
  cargo zigbuild --release --locked -p gatana-cli "${linux_args[@]}"

# ── Check and pack ────────────────────────────────────────────────────

binary() {
  case $1 in
    *-apple-darwin) echo "target/$1/release/gatana" ;;
    *) echo "target/zigbuild/$1/release/gatana" ;;
  esac
}

step "Checking that every binary runs and reports $VERSION"
expected="gatana $VERSION"
check() {
  local target=$1 got
  shift
  got=$("$@" --version) || die "$target: the binary did not start"
  [[ $got == "$expected" ]] || die "$target: reports '$got', expected '$expected'"
  echo "  ✓ $target"
}
check aarch64-apple-darwin "$(binary aarch64-apple-darwin)"
if arch -x86_64 /usr/bin/true 2>/dev/null; then
  check x86_64-apple-darwin arch -x86_64 "$(binary x86_64-apple-darwin)"
else
  echo "  - x86_64-apple-darwin: not run, Rosetta is not installed"
fi
for target in "${LINUX_TARGETS[@]}"; do
  platform=linux/${target%%-*}
  platform=${platform/aarch64/arm64}
  platform=${platform/x86_64/amd64}
  # busybox has no libc of its own to fall back on: the binary must be static.
  check "$target" docker run --rm --platform "$platform" -v "$PWD/$(binary "$target")":/gatana:ro busybox /gatana
done

step "Packing into $OUT"
rm -rf "$OUT"
mkdir -p "$OUT"
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT
for target in "${MAC_TARGETS[@]}" "${LINUX_TARGETS[@]}"; do
  rm -rf "${stage:?}"/*
  cp "$(binary "$target")" "$stage/gatana"
  cp ../../LICENSE "$stage/LICENSE"
  tar -czf "$OUT/gatana-$target.tar.gz" -C "$stage" gatana LICENSE
  (cd "$OUT" && shasum -a 256 "gatana-$target.tar.gz" >"gatana-$target.tar.gz.sha256")
done
cp install.sh "$OUT/install.sh"
ls -lh "$OUT"
