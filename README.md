# 3d-designs

My parametric 3D-print designs. Each one is an OpenSCAD source you can customise, plus ready-to-print Bambu Studio projects.

## Designs

| Design | What it is | Path |
|--------|------------|------|
| Netflix-style lettering | `NETFLIX` and `SERIER` in Netflix-style bent lettering for a school library display: a stand, a plaque and loose wall letters. Built for the Bambu Lab A1 mini (with or without AMS lite) and A2L Combo | [`netflix-lettering`](netflix-lettering) |

## Layout

Every design has its own folder:

```
<design>/
├── README.md            # what it is, which file to print, how to customise
├── <design>.scad        # the parametric source (OpenSCAD Customizer)
├── fonts/               # bundled fonts with their licences, if any
├── print-files/         # ready-to-print Bambu Studio projects, one folder per printer setup
├── templates/           # paper templates, if any
├── docs/                # design notes, build summary, images
└── tools/               # the script that regenerates print-files/ and docs/
```

## Licence

[AGPL-3.0](LICENSE), except bundled fonts, which keep their own licence (see each design's `fonts/`).
