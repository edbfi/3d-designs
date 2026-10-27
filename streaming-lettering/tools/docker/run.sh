#!/bin/sh
# Run a command in the toolchain image with streaming-lettering/ mounted as the working directory,
# for example: tools/docker/run.sh python3 tools/build.py --only 'a1-mini$'
# Builds the image on first use (a few minutes, nothing is compiled). CPUS caps the container
# (default 3), which keeps small fanless boards from overheating during a full build.
set -eu
IMAGE=${STREAMING_LETTERING_IMAGE:-streaming-lettering-tools}
HERE=$(cd "$(dirname "$0")" && pwd)
PROJECT=$(cd "$HERE/../.." && pwd)
docker image inspect "$IMAGE" >/dev/null 2>&1 || docker build -t "$IMAGE" "$HERE"
# Bambu Studio renders plate thumbnails with OpenGL: give it a virtual X display
exec docker run --rm --init --cpus "${CPUS:-3}" --user "$(id -u):$(id -g)" -e HOME=/tmp -e DISPLAY=:99 \
    -v "$PROJECT:/work" -w /work "$IMAGE" sh -c '
        Xvfb :99 -screen 0 1280x1024x24 -nolisten tcp >/dev/null 2>&1 &
        while [ ! -S /tmp/.X11-unix/X99 ]; do sleep 0.2; done
        exec "$@"' sh "$@"
