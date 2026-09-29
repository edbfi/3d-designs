# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Parametric 3D-print designs. Each design lives in its own folder with an OpenSCAD source, a build script and the generated Bambu Studio projects. There is no package manifest.

## Local commands

```bash
cd netflix-lettering
python3 tools/build.py                                   # regenerate print-files/, templates/, docs/ (about 4 min)
python3 tools/build.py --only netflix --only 'a1-mini$'  # a subset (regex on the variant key)
python3 tools/build.py --list                            # variant keys
python3 tools/build.py --renders-only                    # only docs/images/renders
openscad -o /tmp/x.stl -D 'design="plaque"' -D 'part="plaque_body"' netflix-lettering.scad   # one part
```

`tools/build.py` needs OpenSCAD (a 2025+ snapshot with the Manifold backend; 2021.01 works but is far slower) and Bambu Studio at `/Applications/BambuStudio.app` (tested with 02.08.02.61).

## Generated files: regenerate, don't hand-edit

`print-files/`, `templates/`, `docs/build-summary.*`, `docs/images/plates/` and `docs/images/renders/` are written by `tools/build.py`. Change the `.scad` or the build script and rerun it. A partial run (`--only`) merges into the existing build summary.

The build fails loudly rather than writing a bad project. For every variant it checks:

- no stray sliver pieces in any exported part,
- the real Bambu start G-code is present (the CLI silently falls back to a generic one if presets are not fully resolved; see below),
- each plate uses exactly the intended filament slots,
- pauses land at the start of the intended layer and nowhere else,
- plate names survived.

## Bambu Studio CLI quirks the build script works around

Change these parts of `tools/build.py` only with a test slice afterwards:

- System presets must be flattened (`resolve_preset`): the CLI does not resolve `inherits` plus `include` templates, and without that the G-code gets a generic start sequence and a 35 °C bed. A modified preset that still has `inherits` crashes the CLI (exit 139).
- The assemble list's `pos_x/y/z` is added to each STL's own coordinates. Every part of one merged object therefore gets the same offset.
- On single-part objects, Bambu uses the object-level filament, not the part-level one. `patch_project` sets it.
- Slicing drops plate names, so `name_plates` writes them into the final 3MF.
- Pauses go into `Metadata/custom_gcode_per_layer.xml` (type 1, `M400 U1`). A pause at `top_z = Z` runs before the layer printed at Z.

## OpenSCAD rules

- Keep the `.scad` free of experimental features (`textmetrics`, `fill`, `import` as a function, ...). It has to run in the stock Customizer and in MakerWorld's Parametric Model Maker. Text size is never measured numerically; everything that depends on the text's width or height comes from geometry (bounding bands, resize anchors, Minkowski shifts). Read the comments on `to_norm`, `to_final`, `centre_shift2d` and `norm_box` before changing them.
- The per-strip bend (`warp2d`) instantiates its child 500 times. Keep that child cheap (bare text or a box), or render times explode.
- Units are mm, Z is up, and the display datum is centred on the text with its base at Z = 0.

## Naming

Lowercase, hyphen-separated slugs. Design folder = `.scad` name. Print files are `<text>-<design>-<printer-setup>.3mf` inside `print-files/<printer-setup>/`.

## Trademarks

`reference/` is git-ignored and holds the real Netflix logo used only to measure proportions. Never commit it, and don't add Netflix artwork anywhere. The lettering is a free font bent to match.

## Commits

Commit regularly as the work progresses, one logical change per commit, rather than one large commit at the end. Keep the categories apart: model source (`feat`/`fix`), build tooling (`build`), regenerated print files (`chore`), docs (`docs`).

Use Conventional Commits, scoped to the design slug for design changes (`feat(netflix-lettering): ...`). Commits carry a `Signed-off-by` (`git commit -s`). `prek.toml` blocks commits to `main`, so work on a branch.
