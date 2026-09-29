# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Parametric 3D-print designs. Each design lives in its own folder with an OpenSCAD source, a build script and the generated Bambu Studio projects. There is no package manifest.

## Local commands

Each design folder has a `tools/build.py` that regenerates its `print-files/`, `templates/` and `docs/`. See that design's README for requirements and options.

## Generated files: regenerate, don't hand-edit

`print-files/`, `templates/`, `docs/build-summary.*` and `docs/images/` are written by the design's build script. Change the `.scad` or the build script and rerun it.

## OpenSCAD rules

- Keep the `.scad` free of experimental features (`textmetrics`, `fill`, `import` as a function, ...). It has to run in the stock Customizer and in MakerWorld's Parametric Model Maker. Text size is never measured numerically; everything that depends on the text's width or height comes from geometry (bounding bands, resize anchors, Minkowski shifts).
- Units are mm and Z is up. Put each part's datum somewhere meaningful (normally centred, base at Z = 0) and say so in the file's header.

## Naming

Lowercase, hyphen-separated slugs. Design folder = `.scad` name. Print files are `<text>-<design>-<printer-setup>.3mf` inside `print-files/<printer-setup>/`.

## Commits

Use Conventional Commits, scoped to the design slug for design changes (`feat(<design>): ...`). Commits carry a `Signed-off-by` (`git commit -s`). `prek.toml` blocks commits to `main`, so work on a branch.
