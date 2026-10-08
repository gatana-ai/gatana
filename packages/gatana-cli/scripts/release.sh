#!/usr/bin/env bash
# Releases the gatana CLI at the version in crates/gatana-cli/Cargo.toml:
#
#   1. builds the binaries into dist/<version>/ (scripts/dist.sh)
#   2. tags gatana@<version> and makes a GitHub release with the tarballs and install.sh
#   3. publishes the npm packages: one per platform (@gatana/cli-<os>-<cpu>), then gatana
#   4. updates the formula in the Homebrew tap (gatana-ai/homebrew-tap)
#
# A version with a pre-release part (4.0.0-alpha.0) is a pre-release: the GitHub release is not
# marked as latest, so install.sh keeps installing the previous version; npm gets the dist-tag "next"
# instead of "latest"; the Homebrew formula is not changed.
#
# Every step skips what is already done, so after a failure the script can be run again.
#
# Usage: scripts/release.sh [--dry-run]
#   --dry-run  builds and stages everything in dist/<version>/ and runs npm publish --dry-run;
#              nothing is tagged, pushed or published.
set -euo pipefail

cd "$(dirname "$0")/.."

REPO=gatana-ai/gatana
TAP_REPO=gatana-ai/homebrew-tap
NPM_SCOPE=@gatana
# Rust target, npm os, npm cpu. The targets must match the ones scripts/dist.sh builds.
PLATFORMS=(
  "aarch64-apple-darwin darwin arm64"
  "x86_64-apple-darwin darwin x64"
  "aarch64-unknown-linux-musl linux arm64"
  "x86_64-unknown-linux-musl linux x64"
)

DRY_RUN=false
for arg in "$@"; do
  case $arg in
    --dry-run) DRY_RUN=true ;;
    -h | --help) sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

VERSION=$(sed -n 's/^version = "\(.*\)"$/\1/p' crates/gatana-cli/Cargo.toml | head -n1)
TAG=gatana@$VERSION
OUT=dist/$VERSION
DOWNLOAD_URL=https://github.com/$REPO/releases/download/gatana%40$VERSION
if [[ $VERSION == *-* ]]; then PRERELEASE=true NPM_TAG=next; else PRERELEASE=false NPM_TAG=latest; fi

step() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }
skip() { printf '  \033[2m%s\033[0m\n' "$1"; }
die() { printf '\033[31mError: %s\033[0m\n' "$1" >&2; exit 1; }

printf '\033[1mRelease %s\033[0m' "$TAG"
[[ $PRERELEASE == true ]] && printf ' (pre-release)'
[[ $DRY_RUN == true ]] && printf ' (dry run)'
printf '\n'

# ── Preflight ─────────────────────────────────────────────────────────

if [[ $DRY_RUN == false ]]; then
  [[ -z $(git status --porcelain -- .) ]] || die "packages/gatana-cli has uncommitted changes; the tag must match the build"
  if tag_commit=$(git rev-parse -q --verify "refs/tags/$TAG^{commit}"); then
    [[ $tag_commit == $(git rev-parse HEAD) ]] || die "$TAG already exists on another commit"
  fi
  gh auth status >/dev/null 2>&1 || die "not logged in to GitHub; run 'gh auth login'"
  NPM_USER=$(npm whoami 2>/dev/null) || die "not logged in to npm; run 'npm login'"
  echo "  npm user: $NPM_USER"
fi

# ── Build ─────────────────────────────────────────────────────────────

scripts/dist.sh
for platform in "${PLATFORMS[@]}"; do
  read -r target _ _ <<<"$platform"
  [[ -f $OUT/gatana-$target.tar.gz ]] || die "$OUT/gatana-$target.tar.gz is missing"
done

# ── Stage the npm packages ────────────────────────────────────────────

step "Staging the npm packages in $OUT/npm"
rm -rf "$OUT/npm"
optional_deps=()
for platform in "${PLATFORMS[@]}"; do
  read -r target os cpu <<<"$platform"
  name=$NPM_SCOPE/cli-$os-$cpu
  dir=$OUT/npm/cli-$os-$cpu
  mkdir -p "$dir/bin"
  tar -xzf "$OUT/gatana-$target.tar.gz" -C "$dir/bin" gatana
  cp ../../LICENSE "$dir/LICENSE"
  node -e '
    const [name, version, os, cpu] = process.argv.slice(1);
    const pkg = {
      name,
      version,
      description: `The gatana CLI binary for ${os} ${cpu}. Install the gatana package, not this one.`,
      repository: { type: "git", url: "git+https://github.com/gatana-ai/gatana.git", directory: "packages/gatana-cli" },
      license: "MIT",
      os: [os],
      cpu: [cpu],
      files: ["bin"],
      preferUnplugged: true,
    };
    console.log(JSON.stringify(pkg, null, 2));
  ' "$name" "$VERSION" "$os" "$cpu" >"$dir/package.json"
  optional_deps+=("$name")
done

dir=$OUT/npm/gatana
mkdir -p "$dir"
cp -R npm/bin npm/README.md "$dir/"
cp ../../LICENSE "$dir/LICENSE"
node -e '
  const fs = require("fs");
  const [template, version, ...deps] = process.argv.slice(1);
  const pkg = JSON.parse(fs.readFileSync(template, "utf8"));
  pkg.version = version;
  // Exact versions: the launcher and the binary always come from the same release.
  pkg.optionalDependencies = Object.fromEntries(deps.map(dep => [dep, version]));
  console.log(JSON.stringify(pkg, null, 2));
' npm/package.json "$VERSION" "${optional_deps[@]}" >"$dir/package.json"

# ── Homebrew formula ──────────────────────────────────────────────────

sha() { cut -d ' ' -f 1 <"$OUT/gatana-$1.tar.gz.sha256"; }
mkdir -p "$OUT/homebrew"
cat >"$OUT/homebrew/gatana.rb" <<EOF
# Written by packages/gatana-cli/scripts/release.sh in $REPO; changes made here are overwritten.
class Gatana < Formula
  desc "CLI for Gatana: manage servers, tools, credentials and skills"
  homepage "https://gatana.ai"
  version "$VERSION"
  license "MIT"

  on_macos do
    on_arm do
      url "$DOWNLOAD_URL/gatana-aarch64-apple-darwin.tar.gz"
      sha256 "$(sha aarch64-apple-darwin)"
    end
    on_intel do
      url "$DOWNLOAD_URL/gatana-x86_64-apple-darwin.tar.gz"
      sha256 "$(sha x86_64-apple-darwin)"
    end
  end

  on_linux do
    on_arm do
      url "$DOWNLOAD_URL/gatana-aarch64-unknown-linux-musl.tar.gz"
      sha256 "$(sha aarch64-unknown-linux-musl)"
    end
    on_intel do
      url "$DOWNLOAD_URL/gatana-x86_64-unknown-linux-musl.tar.gz"
      sha256 "$(sha x86_64-unknown-linux-musl)"
    end
  end

  def install
    bin.install "gatana"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/gatana --version")
  end
end
EOF
ruby -c "$OUT/homebrew/gatana.rb" >/dev/null

if [[ $DRY_RUN == true ]]; then
  step "npm publish --dry-run"
  for dir in "$OUT"/npm/cli-* "$OUT/npm/gatana"; do
    npm publish "$dir" --dry-run --access public --tag "$NPM_TAG" 2>&1 | grep -E 'name:|version:|total files:|package size:|unpacked size:|bin/' || true
  done
  step "Dry run done"
  echo "  Release files:    $OUT"
  echo "  npm packages:     $OUT/npm (dist-tag $NPM_TAG)"
  echo "  Homebrew formula: $OUT/homebrew/gatana.rb$([[ $PRERELEASE == true ]] && echo ' (not pushed for a pre-release)')"
  exit 0
fi

# ── Tag ───────────────────────────────────────────────────────────────

step "Tagging $TAG"
if git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
  skip "$TAG exists"
else
  git tag -s "$TAG" -m "Release $TAG"
fi
git push origin "refs/tags/$TAG"

# ── GitHub release ────────────────────────────────────────────────────

step "GitHub release $TAG"
assets=("$OUT"/gatana-*.tar.gz "$OUT"/gatana-*.tar.gz.sha256 "$OUT/install.sh")
if gh release view "$TAG" -R "$REPO" >/dev/null 2>&1; then
  skip "the release exists; uploading the files again"
  gh release upload "$TAG" -R "$REPO" --clobber "${assets[@]}"
else
  previous=$(git describe --tags --abbrev=0 --match 'gatana@*' "$TAG^" 2>/dev/null || true)
  notes=""
  if [[ -n $previous ]]; then
    notes=$(git log --pretty=format:'- %s (%h)' "$previous..$TAG" -- .)
  fi
  [[ -n $notes ]] || notes="Release $TAG"
  if [[ $PRERELEASE == true ]]; then latest=(--prerelease --latest=false); else latest=(--latest); fi
  gh release create "$TAG" -R "$REPO" --verify-tag --title "$TAG" --notes "$notes" "${latest[@]}" "${assets[@]}"
fi

# ── npm ───────────────────────────────────────────────────────────────

published() { npm view "$1@$VERSION" version --prefer-online >/dev/null 2>&1; }

publish() {
  local name
  name=$(node -p "require('./$1/package.json').name")
  step "npm: $name@$VERSION ($NPM_TAG)"
  if published "$name"; then
    skip "already published"
  else
    npm publish "$1" --access public --tag "$NPM_TAG"
  fi
}

# The platform packages first. npm skips an optional dependency that it cannot download, and shows no
# error, so an install of gatana before its platform packages are in the registry gets no binary.
platform_names=()
for dir in "$OUT"/npm/cli-*; do
  publish "$dir"
  platform_names+=("$(node -p "require('./$dir/package.json').name")")
done

# A new package can take minutes to appear in the registry after the publish.
step "Waiting until the registry serves the platform packages"
for name in "${platform_names[@]}"; do
  waited=0
  until published "$name"; do
    ((waited < 900)) || die "$name@$VERSION is not in the registry after 15 minutes; run the release again later"
    sleep 15
    waited=$((waited + 15))
  done
  echo "  ✓ $name ($waited s)"
done

publish "$OUT/npm/gatana"

# ── Homebrew ──────────────────────────────────────────────────────────

step "Homebrew tap $TAP_REPO"
if [[ $PRERELEASE == true ]]; then
  skip "not changed for a pre-release"
else
  if ! gh repo view "$TAP_REPO" >/dev/null 2>&1; then
    read -rp "  $TAP_REPO does not exist. Create it as a public repository? [y/N] " answer
    [[ $answer == [yY]* ]] || die "the tap was not updated; the other channels are released"
    gh repo create "$TAP_REPO" --public --description "Homebrew tap for the Gatana CLI"
  fi
  tap=$(mktemp -d)
  trap 'rm -rf "$tap"' EXIT
  gh repo clone "$TAP_REPO" "$tap" -- --quiet
  mkdir -p "$tap/Formula"
  cp "$OUT/homebrew/gatana.rb" "$tap/Formula/gatana.rb"
  git -C "$tap" add Formula/gatana.rb
  if git -C "$tap" diff --cached --quiet; then
    skip "the formula is up to date"
  else
    git -C "$tap" commit -S --quiet -m "gatana $VERSION"
    git -C "$tap" push --quiet origin HEAD:main
  fi
fi

step "Released $TAG"
echo "  https://github.com/$REPO/releases/tag/gatana%40$VERSION"
echo "  npm install -g gatana@$NPM_TAG"
[[ $PRERELEASE == true ]] || echo "  brew install gatana-ai/tap/gatana"
