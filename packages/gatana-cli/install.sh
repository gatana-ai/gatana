#!/bin/sh
# Installs the gatana CLI from its GitHub release:
#
#   curl -fsSL https://github.com/gatana-ai/gatana-js/releases/latest/download/install.sh | sh
#
# Environment:
#   GATANA_VERSION       the version to install, e.g. 4.0.0 (default: the latest release)
#   GATANA_INSTALL_DIR   the folder for the binary (default: ~/.local/bin)
#   GATANA_DOWNLOAD_URL  the base URL of the release files, for a mirror (default: GitHub)
#
# Everything is inside main, so a download that breaks off halfway runs nothing.
set -eu

main() {
  repo=https://github.com/gatana-ai/gatana-js
  dir=${GATANA_INSTALL_DIR:-$HOME/.local/bin}

  os=$(uname -s)
  arch=$(uname -m)
  case $os in
    Darwin)
      # A shell under Rosetta reports x86_64 on an Apple Silicon Mac, where the arm64 binary belongs.
      if [ "$arch" = x86_64 ] && [ "$(sysctl -n sysctl.proc_translated 2>/dev/null || true)" = 1 ]; then
        arch=arm64
      fi
      case $arch in
        arm64) target=aarch64-apple-darwin ;;
        x86_64) target=x86_64-apple-darwin ;;
        *) fail "no gatana binary for macOS on $arch" ;;
      esac
      ;;
    Linux)
      case $arch in
        aarch64 | arm64) target=aarch64-unknown-linux-musl ;;
        x86_64 | amd64) target=x86_64-unknown-linux-musl ;;
        *) fail "no gatana binary for Linux on $arch" ;;
      esac
      ;;
    *) fail "no gatana binary for $os" ;;
  esac

  if [ -n "${GATANA_DOWNLOAD_URL:-}" ]; then
    base=${GATANA_DOWNLOAD_URL%/}
  elif [ -n "${GATANA_VERSION:-}" ]; then
    base=$repo/releases/download/gatana%40${GATANA_VERSION#v}
  else
    base=$repo/releases/latest/download
  fi
  file=gatana-$target.tar.gz

  tmp=$(mktemp -d)
  trap 'rm -rf "$tmp"' EXIT

  echo "Downloading $base/$file"
  download "$base/$file" "$tmp/$file"
  download "$base/$file.sha256" "$tmp/$file.sha256"

  expected=$(cut -d ' ' -f 1 <"$tmp/$file.sha256")
  actual=$(sha256 "$tmp/$file")
  [ "$expected" = "$actual" ] || fail "the checksum of $file does not match (expected $expected, got $actual)"

  tar -xzf "$tmp/$file" -C "$tmp" gatana
  mkdir -p "$dir"
  # Copy next to the old binary, then rename over it: a gatana that is running keeps working.
  cp "$tmp/gatana" "$dir/.gatana.new"
  chmod 755 "$dir/.gatana.new"
  mv -f "$dir/.gatana.new" "$dir/gatana"

  echo "Installed $("$dir/gatana" --version) to $dir/gatana"
  case ":$PATH:" in
    *":$dir:"*) ;;
    *)
      echo
      echo "$dir is not on your PATH. Add this line to your shell profile (~/.zshrc, ~/.bashrc):"
      echo
      echo "  export PATH=\"$dir:\$PATH\""
      ;;
  esac
}

download() {
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$1" -o "$2" || fail "could not download $1"
  elif command -v wget >/dev/null 2>&1; then
    wget -q "$1" -O "$2" || fail "could not download $1"
  else
    fail "curl or wget is required"
  fi
}

sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -d ' ' -f 1
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | cut -d ' ' -f 1
  else
    fail "sha256sum or shasum is required to check the download"
  fi
}

fail() {
  echo "gatana install: $1" >&2
  exit 1
}

main "$@"
