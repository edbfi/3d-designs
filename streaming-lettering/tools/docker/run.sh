#!/bin/sh
# Run a command in the toolchain image with streaming-lettering/ mounted as the working directory,
# for example: tools/docker/run.sh python3 tools/build.py --only 'a1-mini$'
# Builds the image first: a few minutes the first time (nothing is compiled), cached after
# that. CPUS caps the container (default 3), which keeps small fanless boards from overheating.
set -eu
IMAGE=${STREAMING_LETTERING_IMAGE:-streaming-lettering-tools}
HERE=$(cd "$(dirname "$0")" && pwd)
PROJECT=$(cd "$HERE/../.." && pwd)
docker build -q -t "$IMAGE" "$HERE" >/dev/null
# Bambu Studio renders plate thumbnails with OpenGL: give it a virtual X display
exec docker run --rm --init --cpus "${CPUS:-3}" --user "$(id -u):$(id -g)" -e HOME=/tmp -e DISPLAY=:99 \
    -v "$PROJECT:/work" -w /work "$IMAGE" sh -c '
        Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp >/tmp/xvfb.log 2>&1 &
        for _ in $(seq 50); do [ -S /tmp/.X11-unix/X99 ] && exec "$@"; sleep 0.2; done
        echo "run.sh: Xvfb did not start:" >&2; cat /tmp/xvfb.log >&2; exit 1' sh "$@"
