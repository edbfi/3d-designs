#!/bin/sh
# Run a command in the shared toolchain image with the repo mounted at /work, in the folder it is
# run from, for example from streaming-lettering/:
#   ../tools/docker/run.sh python3 tools/build.py --jobs 2 --only 'a1-mini$'
# Builds the image first: a few minutes the first time, cached after that.
# CPUS caps the container (default 3), which keeps small fanless boards from overheating.
# MEMORY caps it (default 4.5g, no swap), so a runaway export is killed inside the container instead
# of starving the machine; the kernel also kills the container first if the machine runs out.
set -eu
IMAGE=${TOOLS_IMAGE:-3d-designs-tools}
HERE=$(cd "$(dirname "$0")" && pwd -P)
ROOT=$(cd "$HERE/../.." && pwd -P)
CWD=$(pwd -P)
case "$CWD/" in
    "$ROOT"/*) ;;
    *) echo "run.sh: run it from inside the repo ($ROOT)" >&2; exit 2 ;;
esac
docker build -q -t "$IMAGE" "$HERE" >/dev/null
# Bambu Studio renders plate thumbnails with OpenGL: give it a virtual X display
exec docker run --rm --init --cpus "${CPUS:-3}" --memory "${MEMORY:-4.5g}" --memory-swap "${MEMORY:-4.5g}" \
    --oom-score-adj 1000 --user "$(id -u):$(id -g)" -e HOME=/tmp -e DISPLAY=:99 \
    -v "$ROOT:/work" -w "/work${CWD#"$ROOT"}" "$IMAGE" sh -c '
        Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp >/tmp/xvfb.log 2>&1 &
        for _ in $(seq 50); do [ -S /tmp/.X11-unix/X99 ] && exec "$@"; sleep 0.2; done
        echo "run.sh: Xvfb did not start:" >&2; cat /tmp/xvfb.log >&2; exit 1' sh "$@"
