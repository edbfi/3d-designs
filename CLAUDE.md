# 3d-designs

Parametric OpenSCAD designs with ready-to-print Bambu Studio projects, one folder per design.

## Documentation

Code is the documentation for how things work. Prose is for what code can't say: what to
print, how to assemble it, intent, trade-offs and measured results.

- One home per topic. Link to it; never copy it.
  - `README.md`: what the repo is, the design list, the folder layout, the licence.
  - `<design>/README.md`: which file to print, assembly, print settings, customising,
    rebuilding, MakerWorld and licence notes. Written for someone printing, not for agents.
  - `<design>/docs/design-notes.md`: measurements, experiments and decisions, with numbers.
  - `<design>/docs/build-summary.*`: generated. Owns the current times, grams and plate counts.
  - Source comments and docstrings: how the code works and why.
- Don't restate code, list functions or options, or copy defaults into Markdown.
- Don't copy current build figures (times, grams, counts) into READMEs. Design notes may
  keep a measured comparison that backs a decision, but not the current totals.
- No machine-specific notes (host paths, plugin installs, board specs) in the repo.
- No new doc files, changelogs, status reports or AGENTS.md unless asked.
- Change the owning doc in the same commit as the behaviour, and delete what it replaces.
  A doc that no longer matches the code is a bug.
- Cleanup: on every change that touches a doc, prune stale claims and duplication there.
  Before adding a design or after a large change, review all docs the same way.
  Prefer deleting to rewording.
- Keep the MakerWorld listing, licence and trademark notes.

## Printing

- Design every part to print without supports in PLA and PETG: pick the print pose, keep
  overhangs within 45° of vertical (chamfers, teardrops), or split it into parts that fit together.
  Check new or reshaped parts in their print pose with the `text-to-cad:dfam-check` skill
  (`measure`, `orientations`); bridges and 0.2 mm stepped chamfers are fine.
- If a support can't be avoided, use [Support Fins](https://github.com/gittrahan/support-fins)
  and nothing else: no slicer supports, no home-made fins. Run its CLI with bun
  (`bun support-fins.mjs`; it isn't on npm), pinned by commit or checksum in the design's
  Docker image. Record why in the design notes, with the test-print result.
- Each design's build fails on slicer supports and on Bambu Studio's overhang warnings. Don't weaken
  those checks; if Support Fins trips one, scope the exception to that object.

## Building

- From the design folder: `tools/docker/run.sh python3 tools/build.py --jobs 2`.
  Always pass `--jobs 2`: the container is CPU-capped but Python still sees every core.
  `CPUS=2` caps it lower on a fanless board. Don't run two builds in one checkout.
- Check the exit status: successful variants are written even when others fail.
- Never hand-edit generated files. Commit regenerated `print-files/`, `templates/`,
  `makerworld/`, `docs/build-summary.*` and `docs/images/` together with the source change
  that caused them.
- `build/` and `reference/` stay out of git; third-party logos never go in.

## Commits

Conventional Commits.
