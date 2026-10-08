#!/usr/bin/env bash
set -e

# ──────────────────────────────────────────────────────────────────────
# Gatana Release Script
#
# Checks the npm login, detects whether gatana-sdk has changed, asks how to
# bump its version, then builds, publishes to npm, and creates a git tag.
# The Rust CLI (packages/gatana-cli) is not released by this script.
#
# Usage:
#   ./scripts/release.sh                       Interactive mode (recommended)
#   ./scripts/release.sh --sdk-bump patch       Non-interactive SDK bump
#   ./scripts/release.sh --force                Release even without changes
# ──────────────────────────────────────────────────────────────────────

BOLD="\033[1m"
DIM="\033[2m"
GREEN="\033[32m"
YELLOW="\033[33m"
CYAN="\033[36m"
RED="\033[31m"
RESET="\033[0m"

FORCE=false
SDK_BUMP=""

usage() {
  echo ""
  echo -e "${BOLD}Gatana Release Script${RESET}"
  echo ""
  echo "Usage: ./scripts/release.sh [options]"
  echo ""
  echo "Options:"
  echo "  --force                Release even if no changes detected"
  echo "  --sdk-bump <level>     Set gatana-sdk bump level: patch, minor, or major"
  echo "  -h, --help             Show this help"
  echo ""
  echo "If the bump level is not specified, the script will ask interactively."
  echo ""
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force) FORCE=true; shift ;;
    --sdk-bump) SDK_BUMP="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) echo -e "${RED}Unknown option: $1${RESET}"; usage ;;
  esac
done

if [[ -n "$SDK_BUMP" && "$SDK_BUMP" != "patch" && "$SDK_BUMP" != "minor" && "$SDK_BUMP" != "major" ]]; then
  echo -e "${RED}Error: bump level must be patch, minor, or major (got '$SDK_BUMP')${RESET}"
  exit 1
fi

# ── Helpers ───────────────────────────────────────────────────────────

latest_tag() {
  local prefix="$1"
  git tag --list "${prefix}@*" --sort=-v:refname | head -n1
}

has_changes() {
  local tag="$1"
  local dir="$2"
  if [[ -z "$tag" ]]; then
    return 0 # no previous tag = always has changes
  fi
  [[ -n "$(git diff --name-only "$tag" -- "$dir")" ]]
}

# Extract version from a tag like "gatana-sdk@2.1.3" → "2.1.3"
version_from_tag() {
  echo "$1" | sed 's/.*@//'
}

# Compute what the next version would be for a given bump
next_version() {
  local current="$1"
  local bump="$2"
  local major minor patch
  IFS='.' read -r major minor patch <<< "$current"
  case "$bump" in
    major) echo "$((major + 1)).0.0" ;;
    minor) echo "${major}.$((minor + 1)).0" ;;
    patch) echo "${major}.${minor}.$((patch + 1))" ;;
  esac
}

ask_bump() {
  local pkg="$1"
  local current_tag="$2"
  local current_version=""

  if [[ -n "$current_tag" ]]; then
    current_version=$(version_from_tag "$current_tag")
  else
    # Read from package.json
    current_version=$(node -p "require('./packages/${pkg}/package.json').version")
  fi

  echo "" >&2
  echo -e "${BOLD}Version bump for ${CYAN}${pkg}${RESET}${BOLD}?${RESET}  ${DIM}(current: ${current_version})${RESET}" >&2
  echo "" >&2

  local patch_v minor_v major_v
  patch_v=$(next_version "$current_version" "patch")
  minor_v=$(next_version "$current_version" "minor")
  major_v=$(next_version "$current_version" "major")

  echo -e "  ${GREEN}1)${RESET} patch  →  ${current_version} → ${BOLD}${patch_v}${RESET}  ${DIM}(bug fixes, safe changes)${RESET}" >&2
  echo -e "  ${YELLOW}2)${RESET} minor  →  ${current_version} → ${BOLD}${minor_v}${RESET}  ${DIM}(new features, backwards compatible)${RESET}" >&2
  echo -e "  ${RED}3)${RESET} major  →  ${current_version} → ${BOLD}${major_v}${RESET}  ${DIM}(breaking changes)${RESET}" >&2
  echo -e "  ${DIM}4) skip   (don't release this package)${RESET}" >&2
  echo "" >&2
  read -rp "  Choose [1]: " choice
  case "$choice" in
    2) echo "minor" ;;
    3) echo "major" ;;
    4) echo "skip" ;;
    *) echo "patch" ;;
  esac
}

confirm_release() {
  echo ""
  echo -e "${BOLD}────────────────────────────────────────${RESET}"
  echo -e "${BOLD}  Release Summary${RESET}"
  echo -e "${BOLD}────────────────────────────────────────${RESET}"

  local sdk_cur sdk_next
  sdk_cur=$(node -p "require('./packages/gatana-js/package.json').version")
  sdk_next=$(next_version "$sdk_cur" "$SDK_BUMP")
  echo -e "  ${CYAN}gatana-sdk${RESET}  ${sdk_cur} → ${GREEN}${sdk_next}${RESET}  (${SDK_BUMP})"

  echo -e "${BOLD}────────────────────────────────────────${RESET}"
  echo ""
  echo "  This will: bump the version, build, publish to npm, commit & tag."
  echo ""
  read -rp "  Proceed? [Y/n]: " confirm
  case "$confirm" in
    [nN]*) echo ""; echo "Aborted."; exit 0 ;;
  esac
}

step() {
  echo ""
  echo -e "${BOLD}▸ $1${RESET}"
}

# ── Banner ────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}Gatana Release${RESET}"
echo ""

# ── Preflight: npm login ──────────────────────────────────────────────
# Publishing without a valid npm login fails with a misleading E404 from
# the registry, and only after the version bump has already changed
# package.json. Check the login first, before anything is modified.

if ! NPM_USER=$(pnpm whoami 2>/dev/null); then
  echo -e "  ${RED}✗ npm${RESET}  not logged in (or the login has expired)"
  echo ""
  echo -e "${RED}Error: an npm login is required to publish.${RESET}"
  echo -e "${DIM}  Run 'npm login' and try again.${RESET}"
  echo ""
  exit 1
fi
echo -e "  ${GREEN}✓ npm${RESET}  logged in as ${BOLD}${NPM_USER}${RESET}"
echo ""

# ── Detect changes ────────────────────────────────────────────────────

SDK_TAG=$(latest_tag "gatana-sdk")

if has_changes "$SDK_TAG" "packages/gatana-js"; then
  echo -e "  ${GREEN}●${RESET} ${BOLD}gatana-sdk${RESET}  has changes since ${DIM}${SDK_TAG:-first release}${RESET}"
elif [[ "$FORCE" == true ]]; then
  echo -e "  ${DIM}○ gatana-sdk  no changes since ${SDK_TAG} (--force)${RESET}"
else
  echo -e "  ${DIM}○ gatana-sdk  no changes since ${SDK_TAG}${RESET}"
  echo ""
  echo "Nothing to release."
  exit 0
fi

if [[ -z "$SDK_BUMP" ]]; then
  SDK_BUMP=$(ask_bump "gatana-sdk" "$SDK_TAG")
fi
if [[ "$SDK_BUMP" == "skip" ]]; then
  echo ""
  echo "Nothing to release."
  exit 0
fi

# ── Confirm before proceeding ─────────────────────────────────────────

confirm_release

# ── Bump version ──────────────────────────────────────────────────────

step "Bumping gatana-sdk version (${SDK_BUMP})..."
pnpm --filter gatana-sdk exec pnpm version "$SDK_BUMP" --no-git-tag-version --no-git-checks

SDK_VERSION=$(node -p "require('./packages/gatana-js/package.json').version")
TAG="gatana-sdk@$SDK_VERSION"

# ── Build ─────────────────────────────────────────────────────────────

step "Building gatana-sdk..."
pnpm --filter gatana-sdk build

# ── Publish ───────────────────────────────────────────────────────────

step "Publishing ${TAG} to npm..."
pnpm --filter gatana-sdk publish --access public --no-git-checks

# ── Git commit & tag ──────────────────────────────────────────────────

step "Creating git commit and tag..."

git add packages/gatana-js/package.json
git commit -S -m "release: ${TAG}"
git tag -s "$TAG" -m "Release ${TAG}"

# ── Push ──────────────────────────────────────────────────────────────

step "Pushing to remote..."
git push
git push --tags

# ── GitHub Release ────────────────────────────────────────────────────

if ! command -v gh &>/dev/null; then
  echo ""
  echo -e "${YELLOW}Warning: 'gh' CLI not found — skipping GitHub release creation.${RESET}"
  echo -e "${DIM}  Install it with: brew install gh${RESET}"
else
  step "Creating GitHub release..."

  if [[ -n "$SDK_TAG" ]]; then
    # Commits between the two tags, scoped to the package directory
    SDK_NOTES=$(git log --pretty=format:"- %s (%h)" "${SDK_TAG}..${TAG}" -- packages/gatana-js)
  else
    # First release: list the commits that touch the package
    SDK_NOTES=$(git log --pretty=format:"- %s (%h)" "${TAG}" -- packages/gatana-js | head -20)
  fi
  if [[ -z "$SDK_NOTES" ]]; then
    SDK_NOTES="Release ${TAG}"
  fi
  echo -e "  Creating release for ${CYAN}${TAG}${RESET}..."
  # Not marked as latest: releases/latest belongs to the CLI, whose install.sh downloads from it.
  gh release create "$TAG" --title "$TAG" --notes "$SDK_NOTES" --latest=false
fi

# ── Done ──────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}${BOLD}✓ Release complete!${RESET}"
echo ""
echo -e "  ${CYAN}${TAG}${RESET}"
echo ""
