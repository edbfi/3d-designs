# 3d-designs

Parametric 3D-print designs with ready-to-print Bambu Studio projects, one folder per design.
`CLAUDE.md` is a symlink to this file.

## Where to look

One home per topic. Read it there, change it there, link to it from anywhere else.

| Topic | Home |
|---|---|
| What the repo is, the design list, the folder layout, the licence | [`README.md`](README.md) |
| What to print, assembly, print settings, customising, rebuilding, MakerWorld and licence notes, written for someone printing | `<design>/README.md` |
| Measurements, experiments and decisions, with numbers | `<design>/docs/design-notes.md` |
| Current times, grams and plate counts (generated) | `<design>/docs/build-summary.*` |
| How the model and its build work, and why | the source: its comments, docstrings and `<design>/tools/build.py` |
| The pinned build toolchain: OpenSCAD and Bambu Studio in Docker, shared by every design | [`tools/docker/`](tools/docker) |
| OpenSCAD for the `openscad` MCP server | [`tools/openscad`](tools/openscad) |
| Agent setup: the text-to-cad plugin and MCP servers for Claude Code, Codex and OpenCode | [`.claude/settings.json`](.claude/settings.json), [`.mcp.json`](.mcp.json), [`.codex/config.toml`](.codex/config.toml), [`opencode.json`](opencode.json) |
| A worked example of all of the above | [`streaming-lettering/`](streaming-lettering) |

## Modelling

Each design has one source in one toolchain. Never keep the same geometry in two.

- **build123d with text-to-cad, by default.** Model with the `text-to-cad:cad` skill, fit against
  real purchased parts (boards, fans, fasteners) found with `text-to-cad:step-parts`, and make
  dimensioned drawings with `text-to-cad:engineering-drawing`. The MakerWorld listing gets the
  design's Bambu Studio projects and a STEP export.
- **OpenSCAD only when the MakerWorld listing should be customisable**: something the person
  printing chooses, such as their own text, a name or a size, set in MakerWorld's Parametric Model
  Maker. The `.scad` is the source and the build generates its MakerWorld edition, as in
  `streaming-lettering`, whose design notes record MakerWorld's limits. Write and check it with
  the `openscad` MCP server.
- Whichever toolchain made it, check the exported mesh with text-to-cad: `cad_show` opens an STL
  or 3MF in the CAD Viewer, and `text-to-cad:dfam-check` measures overhangs and print orientations.
- text-to-cad and the `openscad` server are set up for this repo only, not per user. Codex loads
  `.codex/config.toml` only once you trust the repo. If an agent lacks either tool, say so: don't
  switch toolchains to work around it.

## Printing

- Design every part to print without supports in PLA and PETG: pick the print pose, keep
  overhangs within 45° of vertical (chamfers, teardrops), or split it into parts that fit together.
  Measure the overhangs of new or reshaped parts in their print pose with
  `text-to-cad:dfam-check` (`measure`, `orientations`); bridges and 0.2 mm stepped chamfers are fine.
- If a support can't be avoided, use [Support Fins](https://github.com/gittrahan/support-fins)
  and nothing else: no slicer supports, no home-made fins. Run its CLI with bun
  (`bun support-fins.mjs`; it isn't on npm), pinned by commit or checksum in `tools/docker/`.
  Record why in the design notes, with the test-print result.
- A design's build must fail on slicer supports and on Bambu Studio's overhang warnings. Don't
  weaken those checks: if a part with Support Fins trips one, add a narrow exemption to that
  check in the same change, with the reason in a code comment.

## Building

- From the design folder: `../tools/docker/run.sh python3 tools/build.py --jobs 2`.
  Always pass `--jobs 2`: the container is CPU-capped but Python still sees every core.
  `CPUS=2` caps it lower on a fanless board. Don't run two builds in one checkout.
- Check the exit status: successful variants are written even when others fail.
- Every design builds in the one image in `tools/docker/`. When a design needs a new tool, add it
  there (build123d with the first build123d design), not in a per-design image. A toolchain
  change can change any design's output: rebuild every design and commit what changes.
- Never hand-edit generated files. Commit regenerated `print-files/`, `templates/`,
  `makerworld/`, `docs/build-summary.*` and `docs/images/` together with the source change
  that caused them.
- `build/` and `reference/` stay out of git; third-party logos never go in.

## Documentation

Code is the documentation for how things work. Prose is for what code can't say: what to
print, how to assemble it, intent, trade-offs and measured results.

- Keep each topic in its home ([Where to look](#where-to-look)). Link to it; never copy it.
- Don't restate code, list functions or options, or copy defaults into Markdown.
- Don't copy current build figures (times, grams, counts) into READMEs. Design notes may
  keep a measured comparison that backs a decision, but not the current totals.
- No machine-specific notes (host paths, plugin installs, board specs) in the repo.
- No new doc files, changelogs or status reports unless asked.
- Change the owning doc in the same commit as the behaviour, and delete what it replaces.
  A doc that no longer matches the code is a bug.
- Cleanup: on every change that touches a doc, prune stale claims and duplication there.
  Before adding a design or after a large change, review all docs the same way.
  Prefer deleting to rewording.
- Keep the MakerWorld listing, licence and trademark notes.

## Commits

Conventional Commits.
