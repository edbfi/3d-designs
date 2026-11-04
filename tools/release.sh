#!/bin/sh
# Publish a design's print files as its rolling GitHub release, <design>-latest. Run it on main
# after the design's PR has merged, from anywhere in the repo:
#   tools/release.sh q6a-fan-stand
# It rebuilds the design in the shared toolchain and refuses to publish if the rebuild changes
# any tracked file: what main says (build summary, images) must be what the release holds. Then
# it replaces the release and its tag with <design>/build/release/* on the current commit, so
# download links stay the same:
#   https://github.com/<owner>/<repo>/releases/download/<design>-latest/<file>
# CPUS caps the build's container as in tools/docker/run.sh.
set -eu
die() { echo "release.sh: $*" >&2; exit 1; }
[ $# -eq 1 ] || die "usage: tools/release.sh <design>"
design=${1#./}
while [ "${design%/}" != "$design" ]; do design=${design%/}; done
case $design in "" | .* | */*) die "give the design's folder name, like q6a-fan-stand" ;; esac
cd "$(git rev-parse --show-toplevel)"
[ -f "$design/tools/build.py" ] && [ -f "$design/README.md" ] || die "no design '$design'"
heading=$(sed -n '1s/^# *//p' "$design/README.md")
[ -n "$heading" ] || die "$design/README.md must start with a '# ' title"
repo=$(gh repo view --json nameWithOwner -q .nameWithOwner) || die "gh can't see this repo; run gh auth login"

git fetch -q origin main
[ -z "$(git status --porcelain --untracked-files=no)" ] || die "commit or stash your changes first"
sha=$(git rev-parse HEAD)
[ "$sha" = "$(git rev-parse origin/main)" ] || die "check out origin/main first (HEAD is $sha)"
[ -z "$(git status --porcelain -- "$design")" ] || die "remove the untracked files in $design first"

rm -rf "$design/build/release"
(cd "$design" && ../tools/docker/run.sh python3 tools/build.py --jobs 2) || die "the build failed"
if [ -n "$(git status --porcelain -- "$design")" ]; then
    git status --short -- "$design" >&2
    die "the rebuild changed $design: commit its generated files through a PR first"
fi
set -- "$design"/build/release/*
[ -e "$1" ] || die "the build wrote nothing to $design/build/release/"

tag="$design-latest"
title="$heading: print files"
notes=$(mktemp)
trap 'rm -f "$notes"' EXIT
{
    printf 'Print files for [%s](https://github.com/%s/tree/%s/%s#readme), built from %s.\n\n' \
        "$heading" "$repo" "$sha" "$design" "$sha"
    grep '^|' "$design/docs/build-summary.md" || die "no table in $design/docs/build-summary.md"
} >"$notes"

# Delete the old release, then its tag on its own: gh release create reuses a tag that is still
# there and ignores --target, which would put the new files on the old commit.
if out=$(gh release view -R "$repo" "$tag" --json tagName 2>&1); then
    gh release delete -R "$repo" "$tag" --yes
else
    case $out in *"release not found"*) ;; *) die "can't look up release $tag: $out" ;; esac
fi
rc=0
git ls-remote --exit-code --tags origin "refs/tags/$tag" >/dev/null || rc=$?
case $rc in
    0) git push -q origin ":refs/tags/$tag" ;;
    2) ;;
    *) die "can't list the tags on origin" ;;
esac
gh release create -R "$repo" "$tag" --target "$sha" --title "$title" --notes-file "$notes" --latest=false "$@" ||
    die "release $tag is gone until it publishes: rerun tools/release.sh $design"
echo "published https://github.com/$repo/releases/tag/$tag"
