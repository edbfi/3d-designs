#!/bin/sh
# Publish a design's print files as its rolling GitHub release, <design>-latest. Run it on main
# after the design's PR has merged, from anywhere in the repo:
#   tools/release.sh q6a-fan-stand
# It rebuilds the design in the shared toolchain and refuses to publish if the rebuild changes
# any tracked file: what main says (build summary, images) must be what the release holds. Then
# it replaces the release and its tag with <design>/build/release/* on the current commit, so
# download links stay the same:
#   https://github.com/<owner>/<repo>/releases/download/<design>-latest/<file>
# CPUS caps the build's container as in docker/run.sh.
set -eu
die() { echo "release.sh: $*" >&2; exit 1; }
[ $# -eq 1 ] || die "usage: tools/release.sh <design>"
design=${1%/}
cd "$(git rev-parse --show-toplevel)"
[ -f "$design/tools/build.py" ] && [ -f "$design/README.md" ] || die "no design '$design'"

git fetch -q origin main
[ -z "$(git status --porcelain --untracked-files=no)" ] || die "commit or stash your changes first"
sha=$(git rev-parse HEAD)
[ "$sha" = "$(git rev-parse origin/main)" ] || die "check out origin/main first (HEAD is $sha)"

rm -rf "$design/build/release"
(cd "$design" && ../tools/docker/run.sh python3 tools/build.py --jobs 2) || die "the build failed"
if [ -n "$(git status --porcelain -- "$design")" ]; then
    git status --short -- "$design" >&2
    die "the rebuild changed $design: commit its generated files through a PR first"
fi
set -- "$design"/build/release/*
[ -e "$1" ] || die "the build wrote nothing to $design/build/release/"

tag="$design-latest"
repo=$(gh repo view --json nameWithOwner -q .nameWithOwner)
title="$(sed -n '1s/^# *//p' "$design/README.md"): print files"
notes=$(mktemp)
trap 'rm -f "$notes"' EXIT
{
    printf 'Print files for [%s](https://github.com/%s/tree/%s/%s#readme), built from %s.\n\n' \
        "${title%: print files}" "$repo" "$sha" "$design" "$sha"
    grep '^|' "$design/docs/build-summary.md"
} >"$notes"

if gh release view "$tag" >/dev/null 2>&1; then
    gh release delete "$tag" --cleanup-tag --yes
fi
gh release create "$tag" --target "$sha" --title "$title" --notes-file "$notes" --latest=false "$@"
echo "published https://github.com/$repo/releases/tag/$tag"
