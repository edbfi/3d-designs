# 3d-designs

My parametric 3D-print designs. Each one is a parametric source you can customise, in build123d or OpenSCAD, plus ready-to-print Bambu Studio projects.

## Designs

| Design | What it is | Path |
|--------|------------|------|
| Streaming-style lettering | Bent streaming-style lettering for a library display: a stand, a plaque, loose wall letters and two pinboard frames | [`streaming-lettering`](streaming-lettering) |
| Q6A fan stand | A stand that holds a Noctua NF-A8 80 mm fan over a Radxa Dragon Q6A in its Armor Case 7056A, with the 40-pin header free | [`q6a-fan-stand`](q6a-fan-stand) |

## Layout

Every design has its own folder, and they share one build toolchain:

```
tools/
├── docker/          # the pinned build toolchain (OpenSCAD, build123d, Bambu Studio) every design builds in
└── openscad         # OpenSCAD from that toolchain, for AI agents' OpenSCAD tooling
<design>/
├── README.md        # what to print, assembly, customising
├── <design>.py      # the parametric source: build123d,
│   or <design>.scad #   or OpenSCAD where MakerWorld's customiser should offer it
├── fonts/           # bundled fonts with their licences, if any
├── docs/            # design notes; build summary and images (generated)
├── print-files/     # ready-to-print Bambu Studio projects (generated)
├── templates/       # paper templates, if any (generated)
├── makerworld/      # MakerWorld edition of a .scad, or a build123d design's STEP (generated)
└── tools/           # the build script that generates the rest
```

## Licence

[AGPL-3.0](LICENSE), except bundled fonts, which keep their own licence (see each design's `fonts/`).
