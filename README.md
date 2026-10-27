# 3d-designs

My parametric 3D-print designs. Each one is an OpenSCAD source you can customise, plus ready-to-print Bambu Studio projects.

## Designs

| Design | What it is | Path |
|--------|------------|------|
| Streaming-style lettering | Bent streaming-style lettering for a library display: a stand, a plaque and loose wall letters | [`streaming-lettering`](streaming-lettering) |

## Layout

Every design has its own folder:

```
<design>/
├── README.md        # what to print, assembly, customising
├── <design>.scad    # the parametric source (OpenSCAD Customizer)
├── fonts/           # bundled fonts with their licences, if any
├── docs/            # design notes; build summary and images (generated)
├── print-files/     # ready-to-print Bambu Studio projects (generated)
├── templates/       # paper templates, if any (generated)
├── makerworld/      # MakerWorld edition of the .scad, if any (generated)
└── tools/           # the build script that generates the rest
```

## Licence

[AGPL-3.0](LICENSE), except bundled fonts, which keep their own licence (see each design's `fonts/`).
