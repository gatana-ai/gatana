#!/usr/bin/env bash
# Regenerates gatana-sdk (packages/gatana-js) and gatana-client (packages/gatana-python) from the
# OpenAPI documents of Gatana Cloud production, and releases each client whose generated code
# changed. The workflow .github/workflows/sdk-regen.yml runs this every 30 minutes, so both clients
# follow the production API without a manual release.
#
# A run:
#   1. Finishes a release that an earlier run committed but did not publish or release on GitHub.
#      Only commits of this script count (trailer "Released-by: sdk-regen"). A release made with
#      scripts/release.sh is never touched. The build comes from the release commit, also when
#      later commits changed the package.
#   2. Downloads the v1 and v2 documents once and regenerates both clients from them. When the two
#      documents name different API versions (a deploy in progress), the run stops without a
#      release and the next run tries again. A client whose generated code did not change is not
#      released, so a backend release that keeps the API as it was releases nothing.
#   3. Stops when a name that SDK users import is gone: a JS export, or a Python module under api/
#      or models/. A renamed or removed operation, tag or schema does that. Such a change needs a
#      major version, which a person releases with `just release`. The numbered schemas (Schema123,
#      schema_123.py) are not compared, because their numbers shift when the backend adds a schema.
#   4. Bumps the minor version when an operation was added, else the patch version.
#   5. Type-checks, builds and tests the changed clients.
#   6. Commits through the GitHub API, which signs the commit (main requires signed commits). The
#      commit expects main where the run checked it out, so a push in between fails the run, and
#      the next run starts again from the new main.
#   7. Publishes to npm and PyPI with trusted publishing, so no token is stored, and creates the
#      GitHub release, which also creates the tag.
#
# oasdiff does not decide the bump. It reports wire changes that earlier releases shipped as
# patches (a new enum value, a field that became nullable), and it reports a renamed operationId,
# which renames an SDK function, as information only.
#
# Usage: scripts/sdk-regen.sh [--dry-run]
#   --dry-run  runs steps 2, 3 and 5 and prints the releases that a real run would make. It commits
#              and publishes nothing, and leaves the regenerated code in the working tree.
#
# Outside GitHub Actions only --dry-run works. API_HOST overrides the API (default
# https://hello.gatana.ai).
set -euo pipefail

cd "$(dirname "$0")/.."

DRY_RUN=false
for arg in "$@"; do
  case $arg in
    --dry-run) DRY_RUN=true ;;
    -h | --help) awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; exit 0 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

API_HOST=${API_HOST:-https://hello.gatana.ai}
REPO=${GITHUB_REPOSITORY:-gatana-ai/gatana}
TRAILER='Released-by: sdk-regen'
JUST=(uvx --from rust-just==1.59.0 just)
BUMPSEMVER=(uvx bumpsemver==2.3.0)
JS_DIR=packages/gatana-js
PY_DIR=packages/gatana-python
NUMBERED='^js:[a-z0-9]+:[a-z]+:Schema[0-9]+[A-Za-z]*$|^py:models/schema_[0-9]+[a-z0-9_]*\.py$'

step() { printf '\n\033[1m▸ %s\033[0m\n' "$1"; }
die() { printf '\033[31mError: %s\033[0m\n' "$1" >&2; exit 1; }
# Prints a result, and adds it to the job summary in a workflow run
report() {
  echo "$1"
  if [[ -n ${GITHUB_STEP_SUMMARY:-} ]]; then echo "$1" >> "$GITHUB_STEP_SUMMARY"; fi
}

if [[ $DRY_RUN == false && ${GITHUB_ACTIONS:-} != true ]]; then
  die "outside GitHub Actions only --dry-run works: trusted publishing needs the identity of the workflow"
fi
[[ -z $(git status --porcelain -- "$JS_DIR" "$PY_DIR") ]] || die "$JS_DIR or $PY_DIR has uncommitted changes"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"; git worktree prune' EXIT

# ── Packages ──────────────────────────────────────────────────────────

version_of() {
  case $1 in
    gatana-sdk) node -p "require('./$JS_DIR/package.json').version" ;;
    gatana-client) sed -n 's/^current_version = //p' "$PY_DIR/.bumpsemver.cfg" ;;
  esac
}

tag_of() {
  case $1 in
    gatana-sdk) echo "gatana-sdk@$2" ;;
    gatana-client) echo "gatana-client/v$2" ;;
  esac
}

# Prints the commit that set the given version, found by its version line
version_commit() {
  case $1 in
    gatana-sdk) git log -1 --format=%H -S "\"version\": \"$2\"" -- "$JS_DIR/package.json" ;;
    gatana-client) git log -1 --format=%H -S "current_version = $2" -- "$PY_DIR/.bumpsemver.cfg" ;;
  esac
}

# Returns 0 when the registry has the version with all its files, and 1 when it has not. Stops the
# run when the registry does not answer: a guess can publish twice or not at all.
is_published() {
  case $1 in
    gatana-sdk)
      if [[ $(npm view "gatana-sdk@$2" version 2> "$TMP/npm-view.log") == "$2" ]]; then return 0; fi
      if grep -q E404 "$TMP/npm-view.log"; then return 1; fi
      cat "$TMP/npm-view.log" >&2
      die "npm did not say whether gatana-sdk $2 exists"
      ;;
    gatana-client)
      local code
      code=$(curl -s -o "$TMP/pypi.json" -w '%{http_code}' --max-time 60 "https://pypi.org/pypi/gatana-client/$2/json") || true
      case $code in
        404) return 1 ;;
        # A failed upload can leave the wheel without the sdist
        200) jq -e '[.urls[].packagetype] | index("sdist") and index("bdist_wheel")' "$TMP/pypi.json" > /dev/null ;;
        *) die "PyPI did not say whether gatana-client $2 exists (HTTP $code)" ;;
      esac
      ;;
  esac
}

# Returns 0 when the GitHub release exists and 1 when it does not. Stops the run when GitHub does
# not answer.
is_released() {
  local out
  if out=$(gh release view "$1" --repo "$REPO" --json tagName 2>&1); then return 0; fi
  if [[ $out == *"release not found"* ]]; then return 1; fi
  echo "$out" >&2
  die "GitHub did not say whether the release $1 exists"
}

# ── Release ───────────────────────────────────────────────────────────

# Publishes the current version of a package and creates its GitHub release, when a commit of
# this script set that version and one of the two is missing. Each part checks first, so a run can
# finish a release that failed halfway.
finish_release() {
  local pkg=$1 version tag sha published=true released=true
  version=$(version_of "$pkg")
  tag=$(tag_of "$pkg" "$version")
  sha=$(version_commit "$pkg" "$version")
  if [[ -z $sha || $(git log -1 --format=%B "$sha") != *"$TRAILER"* ]]; then return 0; fi

  is_published "$pkg" "$version" || published=false
  is_released "$tag" || released=false
  if [[ $published == true && $released == true ]]; then return 0; fi

  if [[ $DRY_RUN == true ]]; then
    report "$pkg $version is committed but not published or released. The next workflow run finishes it."
    return 0
  fi

  step "Releasing $pkg $version"
  # The build uses the code of the release commit. When later commits exist, a worktree holds it.
  local src=. title=$tag files=()
  if [[ $sha != $(git rev-parse HEAD) ]]; then
    src="$TMP/release-$pkg"
    git worktree add -q --detach "$src" "$sha"
  fi
  case $pkg in
    gatana-sdk)
      # The GitHub release of gatana-sdk has no files, so only a publish needs a build
      if [[ $published == false ]]; then
        if [[ $src != . ]]; then (cd "$src" && pnpm install --frozen-lockfile); fi
        (cd "$src" && pnpm --filter gatana-sdk build)
        # When npm refuses the trusted publisher, it reports only "need auth". Its debug log holds
        # the reason.
        (cd "$src/$JS_DIR" && npm publish --access public) || {
          grep -h ' oidc ' "$HOME"/.npm/_logs/*-debug-*.log >&2 || true
          die "npm did not publish gatana-sdk $version"
        }
      fi
      ;;
    gatana-client)
      rm -rf "$src/$PY_DIR/dist"
      (cd "$src/$PY_DIR" && uv build)
      if [[ $published == false ]]; then
        # --check-url skips the files that an earlier upload sent before it failed
        uv publish --trusted-publishing always --check-url https://pypi.org/simple/ "$src/$PY_DIR"/dist/*
      fi
      title="gatana-client v$version"
      files=("$src/$PY_DIR"/dist/*)
      ;;
  esac
  if [[ $released == false ]]; then
    # Not marked as latest: releases/latest belongs to the CLI, whose install.sh downloads from it
    gh release create "$tag" --repo "$REPO" --target "$sha" --title "$title" --latest=false \
      --notes "$(git log -1 --format=%b "$sha" | sed "/^$TRAILER\$/d")" ${files[@]+"${files[@]}"}
  fi
  report "Released $pkg $version."
}

# ── Regenerate ────────────────────────────────────────────────────────

# Prints the names that SDK users import, at a revision or (no revision) in the working tree. One
# per line: js:<api|apiv2>:<function|type>:<name>, or py:<module path under gatana_client>.
sdk_names() {
  local rev=$1 d
  for d in api apiv2; do
    if [[ -n $rev ]]; then git show "$rev:$JS_DIR/src/$d/index.ts"; else cat "$JS_DIR/src/$d/index.ts"; fi |
      grep -oE 'export (type )?[{][^}]*[}]' |
      awk -v d="$d" '{
        list_kind = ($2 == "type") ? "type" : "function"
        sub(/^export (type )?[{]/, ""); sub(/[}]$/, "")
        n = split($0, names, ",")
        for (i = 1; i <= n; i++) {
          name = names[i]; kind = list_kind
          gsub(/^ +| +$/, "", name)
          # An entry of a value list can be a type: export { type Options, getServer }
          if (sub(/^type +/, "", name)) kind = "type"
          if (name != "") print "js:" d ":" kind ":" name
        }
      }'
  done
  if [[ -n $rev ]]; then
    git ls-tree -r --name-only "$rev" -- "$PY_DIR/gatana_client/api" "$PY_DIR/gatana_client/models"
  else
    find "$PY_DIR/gatana_client/api" "$PY_DIR/gatana_client/models" -name '*.py' -not -path '*/__pycache__/*'
  fi | sed -n "s|^$PY_DIR/gatana_client/\(.*\.py\)\$|py:\1|p"
}

# Commits the staged changes to main through the GitHub API, which signs the commit, and moves the
# checkout to that commit. expectedHeadOid makes the API refuse the commit when main has moved.
commit_to_main() {
  local headline=$1 body=$2 head oid f
  head=$(git rev-parse HEAD)
  git diff --cached --name-only --no-renames --diff-filter=d | while IFS= read -r f; do
    jq -n --arg path "$f" --rawfile contents <(base64 < "$f" | tr -d '\n') '{path: $path, contents: $contents}'
  done | jq -s . > "$TMP/additions.json"
  git diff --cached --name-only --no-renames --diff-filter=D | jq -R '{path: .}' | jq -s . > "$TMP/deletions.json"
  jq -n --arg repo "$REPO" --arg head "$head" --arg headline "$headline" --arg body "$body" \
    --slurpfile additions "$TMP/additions.json" --slurpfile deletions "$TMP/deletions.json" '{
      query: "mutation($input: CreateCommitOnBranchInput!) { createCommitOnBranch(input: $input) { commit { oid } } }",
      variables: {input: {
        branch: {repositoryNameWithOwner: $repo, branchName: "main"},
        expectedHeadOid: $head,
        message: {headline: $headline, body: $body},
        fileChanges: {additions: $additions[0], deletions: $deletions[0]}
      }}
    }' > "$TMP/commit.json"
  oid=$(gh api graphql --input "$TMP/commit.json" --jq .data.createCommitOnBranch.commit.oid)
  [[ -n $oid ]] || die "the GitHub API did not return the new commit"
  git fetch -q origin main
  git diff --cached --quiet "$oid" || die "the new commit $oid does not hold the regenerated code"
  git reset -q --hard "$oid"
  report "Committed $oid: $headline"
}

# Regenerates both clients and, outside a dry run, commits the new versions. Sets COMMITTED.
COMMITTED=false
regenerate() {
  step "Downloading the API documents from $API_HOST"
  # gensdk.ts runs in $JS_DIR and finds the v2 document by replacing the first "v1" in the location
  # of the v1 document, so that location must hold no other "v1". Git ignores node_modules.
  local specs=node_modules/.cache/sdk-regen api_version v2_version js_changed=false py_changed=false
  mkdir -p "$JS_DIR/$specs"
  curl -sf --max-time 60 -o "$JS_DIR/$specs/v1.json" "$API_HOST/api/v1/openapi.json"
  curl -sf --max-time 60 -o "$JS_DIR/$specs/v2.json" "$API_HOST/api/v2/openapi.json"
  api_version=$(jq -r .info.version "$JS_DIR/$specs/v1.json")
  v2_version=$(jq -r .info.version "$JS_DIR/$specs/v2.json")
  if [[ $api_version != "$v2_version" ]]; then
    report "Production answered with two API versions ($api_version and $v2_version), probably during a deploy. The next run tries again."
    return 0
  fi

  step "Regenerating the clients from $api_version"
  OVERRIDE_OPENAPI_URL="$specs/v1.json" pnpm --filter gatana-sdk generate
  "${JUST[@]}" generate-py "file://$PWD/$JS_DIR/$specs/v1.json"
  [[ -z $(git status --porcelain -- "$JS_DIR/src") ]] || js_changed=true
  [[ -z $(git status --porcelain -- "$PY_DIR/gatana_client") ]] || py_changed=true
  # openapi.json changes in every backend release, even when only info.version is new
  if [[ $py_changed == false ]]; then git checkout -q -- "$PY_DIR"; fi
  if [[ $js_changed == false && $py_changed == false ]]; then
    report "No API change: the clients match production $api_version."
    return 0
  fi

  step "Comparing the names that SDK users import"
  sdk_names HEAD | { grep -vE "$NUMBERED" || true; } | LC_ALL=C sort -u > "$TMP/before"
  sdk_names "" | { grep -vE "$NUMBERED" || true; } | LC_ALL=C sort -u > "$TMP/after"
  local removed added new_js new_py
  removed=$(LC_ALL=C comm -23 "$TMP/before" "$TMP/after")
  added=$(LC_ALL=C comm -13 "$TMP/before" "$TMP/after")
  if [[ -n $removed ]]; then
    echo "$removed"
    report "Production $api_version removes $(wc -l <<< "$removed" | tr -d ' ') names that SDK users import (listed in the log). The change needs a major version: release it by hand with \`just release\`."
    die "names removed"
  fi
  new_js=$(sed -n 's/^js:[a-z0-9]*:function://p' <<< "$added" | paste -sd , - | sed 's/,/, /g')
  new_py=$(sed -n '/__init__\.py$/!s|^py:api/.*/\(.*\)\.py$|\1|p' <<< "$added" | paste -sd , - | sed 's/,/, /g')

  local packages=() bumps=() i
  if [[ $js_changed == true ]]; then packages+=(gatana-sdk); bumps+=("$([[ -n $new_js ]] && echo minor || echo patch)"); fi
  if [[ $py_changed == true ]]; then packages+=(gatana-client); bumps+=("$([[ -n $new_py ]] && echo minor || echo patch)"); fi

  if [[ $DRY_RUN == false ]]; then
    step "Bumping the versions"
    for i in "${!packages[@]}"; do
      case ${packages[$i]} in
        gatana-sdk) pnpm --filter gatana-sdk exec pnpm version "${bumps[$i]}" --no-git-tag-version --no-git-checks > /dev/null ;;
        gatana-client) (cd "$PY_DIR" && "${BUMPSEMVER[@]}" --allow-dirty --no-commit --no-tag "${bumps[$i]}") ;;
      esac
    done
  fi

  if [[ $js_changed == true ]]; then
    step "Checking gatana-sdk"
    pnpm exec tsc --noEmit -p "$JS_DIR"
    pnpm --filter gatana-sdk build
  fi
  if [[ $py_changed == true ]]; then
    step "Checking gatana-client"
    "${JUST[@]}" py-install py-lint py-typecheck py-test
  fi

  local tags=() body
  body="Generated from the Gatana API $api_version at $API_HOST."
  if [[ $js_changed == true && -n $new_js ]]; then body+=$'\n\n'"New in gatana-sdk: $new_js"; fi
  if [[ $py_changed == true && -n $new_py ]]; then body+=$'\n\n'"New in gatana-client: $new_py"; fi
  for i in "${!packages[@]}"; do
    if [[ $DRY_RUN == true ]]; then
      report "Would release ${packages[$i]} with a ${bumps[$i]} bump from $(version_of "${packages[$i]}")."
    else
      tags+=("$(tag_of "${packages[$i]}" "$(version_of "${packages[$i]}")")")
    fi
  done
  if [[ $DRY_RUN == true ]]; then
    report "$body"
    return 0
  fi

  step "Committing"
  git add -A -- "$JS_DIR" "$PY_DIR"
  commit_to_main "release: $(printf '%s, ' "${tags[@]}" | sed 's/, $//')" "$body"$'\n\n'"$TRAILER"
  COMMITTED=true
}

finish_release gatana-sdk
finish_release gatana-client
regenerate
if [[ $COMMITTED == true ]]; then
  finish_release gatana-sdk
  finish_release gatana-client
fi
