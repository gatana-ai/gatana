#!/usr/bin/env bash
# Releases every package in this repository that changed since its last release:
#
#   package           folder                     published to               tag
#   gatana-sdk        packages/gatana-js         npm, GitHub                gatana-sdk@<version>
#   gatana-cli        packages/gatana-cli        GitHub, npm, Homebrew      gatana@<version>
#   gatana-client     packages/gatana-python     GitHub, PyPI               gatana-client/v<version>
#   gatana-langchain  packages/gatana-langchain  GitHub, PyPI               gatana-langchain/v<version>
#
# A package has changes when a commit touched its folder after its last release tag in the
# history of HEAD. The script asks for a version bump per package with changes, checks the git
# state, logins and tools that the chosen releases need, shows one summary, and then releases
# the packages in the order above with their own release: packages/gatana-js/scripts/release.sh,
# packages/gatana-cli/scripts/release.sh (after this script commits the new CLI version) and
# `just py-release`. Each of those commits, tags and pushes on its own. After a failure, run this
# script again: a package that was released has no changes any more, and a CLI version that was
# committed but not tagged is offered as it is.
#
# Usage: scripts/release.sh [--force] [--dry-run]
#   --force    also offers the packages without changes
#   --dry-run  stops after the summary; nothing is changed
set -euo pipefail

cd "$(dirname "$0")/.."

BOLD="\033[1m"
DIM="\033[2m"
GREEN="\033[32m"
YELLOW="\033[33m"
CYAN="\033[36m"
RESET="\033[0m"

FORCE=false
DRY_RUN=false
for arg in "$@"; do
  case $arg in
    --force) FORCE=true ;;
    --dry-run) DRY_RUN=true ;;
    -h | --help) sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

step() { printf "\n${BOLD}▸ %s${RESET}\n" "$1"; }
die() { printf '\033[31mError: %s\033[0m\n' "$1" >&2; exit 1; }

# ── Packages ──────────────────────────────────────────────────────────
# Name, folder and tag prefix, in release order

PACKAGES=(
  "gatana-sdk packages/gatana-js gatana-sdk@"
  "gatana-cli packages/gatana-cli gatana@"
  "gatana-client packages/gatana-python gatana-client/v"
  "gatana-langchain packages/gatana-langchain gatana-langchain/v"
)
CLI_TOML=packages/gatana-cli/crates/gatana-cli/Cargo.toml

current_version() {
  case $1 in
    gatana-sdk) node -p "require('./packages/gatana-js/package.json').version" ;;
    gatana-cli) sed -n 's/^version = "\(.*\)"$/\1/p' "$CLI_TOML" | head -n1 ;;
    *) grep 'current_version = ' "$2/.bumpsemver.cfg" | cut -d= -f2 | tr -d '[:space:]' ;;
  esac
}

# next_version <version> <bump>: the version after the bump. "pre" counts up the pre-release
# (4.0.0-alpha.0 → 4.0.0-alpha.1), "final" drops it (→ 4.0.0), "current" keeps the version.
next_version() {
  local base=${1%%-*} pre="" major minor patch
  [[ $1 == *-* ]] && pre=${1#*-}
  IFS=. read -r major minor patch <<<"$base"
  case $2 in
    major) echo "$((major + 1)).0.0" ;;
    minor) echo "$major.$((minor + 1)).0" ;;
    patch) echo "$major.$minor.$((patch + 1))" ;;
    pre)
      [[ $pre =~ ^(.*[^0-9])?([0-9]+)$ ]] || die "cannot count up the pre-release of $1"
      echo "$base-${BASH_REMATCH[1]}$((BASH_REMATCH[2] + 1))"
      ;;
    final) echo "$base" ;;
    current) echo "$1" ;;
  esac
}

bump_label() {
  case $1 in
    pre) echo "pre-release" ;;
    final) echo "final" ;;
    current) echo "as is" ;;
    *) echo "$1" ;;
  esac
}

# tag_exists <tag>: the tag is in this clone or on origin
tag_exists() {
  git rev-parse -q --verify "refs/tags/$1" >/dev/null || [[ -n $(git ls-remote --tags origin "refs/tags/$1") ]]
}

# ask_bump <name> <folder> <version> <option>...: prints the chosen option
ask_bump() {
  local name=$1 dir=$2 version=$3 i choice
  shift 3
  local options=("$@")
  printf "\n${BOLD}Version bump for ${CYAN}%s${RESET} ${DIM}(%s)${RESET}${BOLD}?${RESET}  ${DIM}current: %s${RESET}\n" "$name" "$dir" "$version" >&2
  i=1
  for option in "$@"; do
    if [[ $option == skip ]]; then
      printf "  ${DIM}%d) skip         (do not release this package)${RESET}\n" "$i" >&2
    else
      printf "  %d) %-12s %s → ${BOLD}%s${RESET}\n" "$i" "$(bump_label "$option")" "$version" "$(next_version "$version" "$option")" >&2
    fi
    i=$((i + 1))
  done
  while true; do
    read -rp "  Choose [1]: " choice
    choice=${choice:-1}
    if [[ $choice =~ ^[0-9]+$ ]] && ((choice >= 1 && choice <= $#)); then
      echo "${options[choice - 1]}"
      return
    fi
    echo "  Enter a number from 1 to $#." >&2
  done
}

# ── Changes ───────────────────────────────────────────────────────────

git fetch -q origin || die "cannot fetch from origin"

echo ""
printf "${BOLD}Changes since the last release${RESET}\n"
CANDIDATES=()
for entry in "${PACKAGES[@]}"; do
  read -r name dir prefix <<<"$entry"
  tag=$(git describe --tags --abbrev=0 --match "${prefix}*" HEAD 2>/dev/null || true)
  if [[ -z $tag ]]; then
    changed=true note="no release tag in the history of HEAD"
  else
    count=$(git rev-list --count "$tag..HEAD" -- "$dir")
    if ((count == 1)); then changed=true note="1 commit since $tag"
    elif ((count > 1)); then changed=true note="$count commits since $tag"
    else changed=false note="no changes since $tag"; fi
  fi
  if [[ $changed == true ]]; then
    printf "  ${GREEN}●${RESET} %-17s ${DIM}%-26s${RESET} %s\n" "$name" "$dir" "$note"
  else
    printf "  ${DIM}○ %-17s %-26s %s${RESET}\n" "$name" "$dir" "$note"
  fi
  if [[ $changed == true || $FORCE == true ]]; then CANDIDATES+=("$entry"); fi
done

if ((${#CANDIDATES[@]} == 0)); then
  printf "\nNothing to release. Use --force to release a package without changes.\n"
  exit 0
fi

# ── Version bumps ─────────────────────────────────────────────────────

SELECTED=() # "name dir bump from to"
for entry in "${CANDIDATES[@]}"; do
  read -r name dir prefix <<<"$entry"
  version=$(current_version "$name" "$dir")
  if [[ $name == gatana-cli ]]; then
    options=()
    # A version in Cargo.toml without a tag was committed by a release that failed later on
    tag_exists "gatana@$version" || options+=(current)
    if [[ $version == *-* ]]; then options+=(pre final); else options+=(patch minor major); fi
  else
    options=(patch minor major)
  fi
  bump=$(ask_bump "$name" "$dir" "$version" "${options[@]}" skip)
  [[ $bump == skip ]] || SELECTED+=("$name $dir $bump $version $(next_version "$version" "$bump")")
done

if ((${#SELECTED[@]} == 0)); then
  printf "\nNothing to release.\n"
  exit 0
fi

# ── Preflight ─────────────────────────────────────────────────────────
# Everything a release needs is checked here, before the first release changes anything

step "Checking the git state, logins and tools"

git rev-parse -q --verify '@{upstream}' >/dev/null || die "the current branch has no upstream to push to"
(($(git rev-list --count 'HEAD..@{upstream}') == 0)) || die "the current branch is behind its upstream; pull first"
# The SDK release commits what is staged, so the index must hold nothing else
git diff --cached --quiet || die "there are staged changes; commit or unstage them first"

needs_npm=false needs_pypi=false
for selected in "${SELECTED[@]}"; do
  read -r name dir bump from to <<<"$selected"
  [[ -z $(git status --porcelain -- "$dir") ]] || die "$dir has uncommitted changes; a release must match its commit"
  case $name in
    gatana-sdk) tag=gatana-sdk@$to needs_npm=true ;;
    gatana-cli)
      tag=gatana@$to needs_npm=true
      command -v cargo >/dev/null || die "cargo is not installed"
      docker info >/dev/null 2>&1 || die "Docker is not running; the CLI binaries are built in it"
      ;;
    *)
      tag=$name/v$to needs_pypi=true
      command -v bumpsemver >/dev/null || die "bumpsemver is not installed"
      ;;
  esac
  ! tag_exists "$tag" || die "the tag $tag already exists"
done

gh auth status >/dev/null 2>&1 || die "not logged in to GitHub; run 'gh auth login'"
echo "  GitHub: logged in"
if [[ $needs_npm == true ]]; then
  npm_user=$(npm whoami 2>/dev/null) || die "not logged in to npm; run 'npm login'"
  echo "  npm: logged in as $npm_user"
fi
if [[ $needs_pypi == true ]]; then
  uv auth token pypi >/dev/null 2>&1 || die "no PyPI token; run 'uv auth login pypi'"
  echo "  PyPI: token found"
fi

# ── Summary ───────────────────────────────────────────────────────────

echo ""
printf "${BOLD}────────────────────────────────────────${RESET}\n"
printf "${BOLD}  Release summary${RESET}\n"
printf "${BOLD}────────────────────────────────────────${RESET}\n"
for selected in "${SELECTED[@]}"; do
  read -r name dir bump from to <<<"$selected"
  case $name in
    gatana-sdk) target="npm, GitHub release" ;;
    gatana-cli)
      if [[ $to == *-* ]]; then target="GitHub pre-release, npm (tag next)"; else target="GitHub release, npm, Homebrew"; fi
      ;;
    *) target="GitHub release, PyPI" ;;
  esac
  printf "  ${CYAN}%-17s${RESET} ${DIM}%-26s${RESET} %s → ${GREEN}%s${RESET}  ${DIM}%s${RESET}\n" "$name" "$dir" "$from" "$to" "$target"
done
printf "${BOLD}────────────────────────────────────────${RESET}\n"

if [[ $DRY_RUN == true ]]; then
  printf "\n${YELLOW}Dry run: nothing was changed.${RESET}\n"
  exit 0
fi

echo ""
read -rp "  Release these packages? [y/N]: " confirm
case $confirm in
  [yY]*) ;;
  *) printf "\nAborted.\n"; exit 0 ;;
esac

# ── Release ───────────────────────────────────────────────────────────

RELEASED=()
CURRENT=""
report() {
  local status=$?
  if ((status == 0)) && [[ -z $CURRENT ]]; then return; fi
  printf "\n${BOLD}Released:${RESET} %s\n" "${RELEASED[*]:-nothing}" >&2
  printf "${BOLD}Failed:${RESET}   %s\n" "$CURRENT" >&2
  case $CURRENT in
    gatana-cli*) printf "Fix the problem, then run 'just rs-release': it skips the steps that are done.\n" >&2 ;;
    *) printf "Fix the problem, then check what the release of %s did (version bump, commit, tag, upload) and finish it by hand.\n" "${CURRENT%%@*}" >&2 ;;
  esac
  printf "Then run 'just release' again for the packages that were not released yet.\n" >&2
}
trap report EXIT

for selected in "${SELECTED[@]}"; do
  read -r name dir bump from to <<<"$selected"
  CURRENT="$name@$to"
  step "Releasing $name $to"
  case $name in
    gatana-sdk)
      packages/gatana-js/scripts/release.sh --sdk-bump "$bump" --force --yes
      ;;
    gatana-cli)
      if [[ $bump != current ]]; then
        perl -0pi -e "s/^version = \"[^\"]*\"/version = \"$to\"/m" "$CLI_TOML"
        cargo update --workspace --offline -q --manifest-path packages/gatana-cli/Cargo.toml
        git commit -q -m "release: gatana@$to" -- "$CLI_TOML" packages/gatana-cli/Cargo.lock
      fi
      packages/gatana-cli/scripts/release.sh
      # The CLI release pushes only its tag
      git push -q
      ;;
    *)
      just py-release "$name" "$bump" publish
      ;;
  esac
  RELEASED+=("$name@$to")
done
CURRENT=""

printf "\n${GREEN}${BOLD}Released:${RESET} %s\n" "${RELEASED[*]}"
