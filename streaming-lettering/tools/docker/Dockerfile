# Toolchain for tools/build.py on Linux, native on arm64 and amd64, from prebuilt binaries:
#   - OpenSCAD: the official image, a snapshot with the Manifold backend
#   - Bambu Studio 02.08.02.61: Flathub's build, run straight from its files through its own
#     runtime (the flatpak sandbox cannot start inside Docker); see the bambu-studio launcher
#   - glfw-shim.c, the only thing compiled, so headless plate thumbnails render
# Built by run.sh on first use: a few minutes, mostly a 1.5 GB download.
FROM openscad/openscad:dev.2026-10-26@sha256:3268ba487a3b92e605f44431c890d71ed576d5cc71a249c24a4af489d88990c6

# Flathub commits, per architecture: Bambu Studio 02.08.02.61 and the runtimes it runs on.
# To bump, find the new commits with `flatpak remote-info --log flathub <ref>` for each arch,
# update them and the version check at the end, then rebuild and compare docs/build-summary.md.
ARG BAMBU_COMMIT_aarch64=fa17d48b6e2a3bd367c8a534a651826a5b14b23477d69d823471a215aeda60da
ARG BAMBU_COMMIT_x86_64=68a634d4d733ce7acf79009095db6f7ca76625f0eb810eef1e92dc7adeba7852
ARG GNOME_COMMIT_aarch64=f4e7c6946a0a4555a5667366edeab61ebce9f4357eb6901f58ca0dbbaccdcb2d
ARG GNOME_COMMIT_x86_64=d607f3df26df30485d50f07c69f2a4750483cc644625a1eda0f2062c59bd6848
ARG GL_COMMIT_aarch64=25f04d6733339a81714109e04fb6719cacb4f3a1b8327b8fd76be553397ef330
ARG GL_COMMIT_x86_64=c8dc1156588776045866acd53f9090c90fa84fdff0e74ee4e859ebfc80fb671d

COPY bambu-studio glfw-shim.c /tmp/toolchain/
RUN set -eu; \
    arch=$(uname -m); \
    apt-get update; \
    apt-get install -y --no-install-recommends python3 xvfb flatpak ca-certificates gcc libc6-dev; \
    flatpak remote-add flathub https://dl.flathub.org/repo/flathub.flatpakrepo; \
    # bwrap cannot create namespaces in Docker: the install triggers fail, harmlessly
    for pin in "app/com.bambulab.BambuStudio/$arch/stable BAMBU" "runtime/org.gnome.Platform/$arch/50 GNOME" \
               "runtime/org.freedesktop.Platform.GL.default/$arch/25.08 GL"; do \
        set -- $pin; eval "commit=\${$2_COMMIT_$arch}"; \
        flatpak install -y --noninteractive --no-related flathub "$1"; \
        flatpak update -y --noninteractive --no-related --commit="$commit" "$1"; \
        test "$(readlink "/var/lib/flatpak/$1/active")" = "$commit"; \
    done; \
    # the binary looks for its resources under /app
    ln -s /var/lib/flatpak/app/com.bambulab.BambuStudio/$arch/stable/active/files /app; \
    ln -s /var/lib/flatpak/runtime/org.gnome.Platform/$arch/50/active/files /opt/bambu-runtime; \
    ln -s /var/lib/flatpak/runtime/org.freedesktop.Platform.GL.default/$arch/25.08/active/files /opt/bambu-gl; \
    gcc -shared -fPIC -O2 -o /usr/local/lib/libbambu-glfw-shim.so /tmp/toolchain/glfw-shim.c; \
    install -m 755 /tmp/toolchain/bambu-studio /usr/local/bin/bambu-studio; \
    apt-get purge -y --auto-remove gcc libc6-dev; \
    rm -rf /var/lib/apt/lists/* /tmp/toolchain; \
    bambu-studio --help 2>/dev/null | grep -q 'BambuStudio-02.08.02.61'; \
    openscad --help 2>&1 | grep -q Manifold

ENV BAMBU_STUDIO=/usr/local/bin/bambu-studio \
    BAMBU_PROFILES=/app/share/BambuStudio/profiles/BBL
WORKDIR /work
