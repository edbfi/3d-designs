# Design notes

How the Netflix look was measured and rebuilt, and the techniques that keep the model fully parametric in plain OpenSCAD.

## Measuring the Netflix wordmark

The 2015 Netflix wordmark (the Wikimedia Commons SVG, used only as a local reference and not included in this repo) was rasterised and measured column by column:

| Property | Netflix logo |
|---|---|
| Top edge | Flat: every letter starts at the same line |
| Bottom edge | Arc, lowest at the outer letters and highest in the middle |
| Middle letters vs. outer letters | 13.4 % shorter |
| Arc shape | A parabola: at 10/20/30/40 % across, the bottom sits at 0.951/0.915/0.888/0.874 of the full height; a parabola with depth 0.134 gives 0.952/0.914/0.887/0.873 |
| Word width | 3.70 × the outer letter height |
| Stem width | 0.15–0.17 × letter height |
| Letter widths (× height) | N 0.51, E 0.43, T 0.48, F 0.44, L 0.42, I 0.15, X 0.57 |
| Gap between letters | About 0.10 × height |

The top edge is flat and only the bottom curves. That is what makes it read as "Netflix", and a first attempt that curved both edges looked wrong.

## Choosing the font

The Netflix lettering is custom, and Netflix Sans is proprietary. Free condensed fonts, measured with OpenSCAD's `textmetrics` (widths as a fraction of cap height):

| Font | Stem | N | E | T | F | L | I | X | Word (spacing 1) |
|---|---|---|---|---|---|---|---|---|---|
| **Netflix logo** | 0.15–0.17 | 0.51 | 0.43 | 0.48 | 0.44 | 0.42 | 0.15 | 0.57 | 3.70 |
| **Bebas Neue** | 0.16 | 0.49 | 0.43 | 0.49 | 0.42 | 0.42 | 0.16 | 0.55 | 3.41 |
| Anton | 0.19 | 0.49 | 0.41 | 0.44 | 0.40 | 0.41 | 0.19 | 0.53 | 3.21 |
| League Gothic | 0.15 | 0.43 | 0.34 | 0.42 | 0.35 | 0.34 | 0.15 | 0.47 | 2.93 |

Bebas Neue matches every letter within about 0.02 of the letter height. The only real difference is spacing. Sweeping `letter_spacing`, `arc_depth` and `stroke_weight` against the rasterised logo (overlap measured as intersection over union) gave the defaults:

| letter_spacing | 1.00 | 1.04 | 1.06 | **1.08** | 1.10 | 1.12 |
|---|---|---|---|---|---|---|
| overlap with the logo | 0.41 | 0.52 | 0.69 | **0.83** | 0.73 | 0.55 |

`arc_depth` 0.134 (the measured value) scored best. Any extra stroke weight made it worse. The rest of the gap to a perfect overlap comes from the logo's custom N and X diagonals.

## Bending text in plain OpenSCAD

OpenSCAD can't warp geometry, so `warp2d` cuts the word into vertical strips and scales each one vertically about the top edge, by `1 − arc_depth · (1 − u²)` (u = −1…1 across the word). Neighbouring strips abut exactly. The number of strips follows from the letter height and arc depth, so the step between two strips along the bottom edge stays around `bend_step` = 0.1 mm, well below what a 0.4 mm nozzle can show. That's about 240 strips for 42 mm letters and the 800-strip cap at 120 mm. Straight text (`arc_depth` = 0) isn't cut at all.

Everything else that has to meet the lettering is bent with the same strips, so the surfaces match to within 0.01 mm:

- the plinth's arched top,
- the region under the arc used for tabs and pockets.

The arc is anchored to the text's **baseline**, not its lowest point. Round letters (S, O) dip slightly below the baseline, and anchoring to them would leave the flat letters floating above the plinth. The dip is trimmed from the one-piece letters so the two colours never overlap in the slicer.

## Parametric without measuring text

A MakerWorld-style model must react to any text, font and size, but `textmetrics` is experimental: it's off by default, and MakerWorld can't be relied on to have it. So the `.scad` never measures the text numerically. Instead:

- **Bounding boxes** come from hulls of copies pushed ±10 km along one axis (`bbox2d`, `xband2d`).
- **Normalising width**: the word is resized to exactly 100 units wide so the bend's u-coordinate is known. Sub-shapes (such as one letter's column) ride along with a far-away copy of the whole word's box, so they get the word's scale factor, not their own (`to_norm`).
- **Final size**: a box three times the letter height rides along 2000 units to the right, so every shape gets the letters' scale. It's then cut off again (`to_final`).
- **Centring**: the font's side bearings would push the word off-centre and make the arc lopsided. A Minkowski sum with a tiny square at minus the ink centre fixes that. The square is built from the ink box's corners scaled by −½ (`centre_shift2d`).
- **Proportional positions**: the progress bar's fill end is the word's right edge scaled by `2f − 1`.
- **Cleanup**: a morphological opening (`offset(r = 0.02) offset(r = −0.02)`) drops scraps thinner than 0.04 mm that coincident edges can leave. The stepped chamfers use round-join insets, because mitred insets turn microscopic notches into long spikes.

The bend instantiates its child once per strip, so that child is kept tiny (bare text or a box). An early version that passed richer subtrees through it took 1 min 40 s per render.

Three more habits keep a full render at 0.3–2 s (stand 1.3 s, plaque 0.3 s, loose letters 2.1 s at 42 mm):

- Offsets use bevelled joins (`chamfer = true`). Round joins put an arc on every strip corner.
- The word's x-range comes from the unbent box, because the bend only moves points vertically.
- The loose-letters preview extrudes the whole word at once instead of letter by letter.

## MakerWorld's Parametric Model Maker

Tested on MakerWorld with the logged-in account (unpublished):

- **Backend:** MakerWorld runs OpenSCAD with the Manifold backend and a render limit of about 10 s. The first upload timed out at 11 s local render time; after the speedups above it generates in about 13–20 s wall-clock, including MakerWorld's own overhead.
- **Plates:** MakerWorld builds a multi-plate, multi-colour 3MF from `mw_plate_N()` modules and `color()`, and previews `mw_assembly_view()`. It also adds any top-level geometry to every plate. So `tools/build.py` generates `makerworld/netflix-lettering-makerworld.scad` with the desktop output switched off. That edition also drops the local font includes, marks `font_name` with `// font` (MakerWorld's picker of 500+ Google Fonts; Bebas Neue is among them) and hides the desktop-only settings. The build checks that the edition has no top-level geometry and that every plate renders.
- **What its 3MF gets right:** the downloaded stand project has two plates, the red letters on filament 1 and the black plinth on filament 2. It carries the fully resolved A1 mini profile: real start G-code, 0.20 mm Standard, PLA Basic. Sliced, it takes 38 + 45 min, the same as our own files.
- **What it gets wrong:** the bed type is Cool Plate, so the bed heats to 35 °C, and supports are on (no supports actually get generated for these parts). Change the plate type to Textured PEI Plate in Bambu Studio before printing. MakerWorld can only preset profile options from a model's upload/edit page.
- **What it can't do:** there are no filament-swap pauses, so the no-AMS plaque and loose letters come out single-colour unless you print on an AMS printer or add the pause in Bambu Studio yourself. Multi-plate scripts can't offer STL download.

## Printability decisions

- **Stand, two-part (no AMS)**: letters print face down, so the textured PEI plate gives the visible face. Tabs follow each letter's bent bottom edge into matching pockets, with 0.15 mm clearance per side (0.146 mm measured).
- **Stand, one piece (AMS)**: letters print upright. The horizontal arms of E, F and T overhang 7–13 mm, so the project turns on tree supports. The word is turned to run along Y: on a bed-slinger, the thin letters then see the bed's motion along their stiff direction.
- **Plaque (no AMS)**: one filament swap. Black is used up to the plaque's top face (4.0 mm), and a pause runs at the start of the 4.2 mm layer. The progress bar's track is a groove in the plaque; the red fill and scrubber dot rise out of it, so the no-AMS version still reads as a two-colour bar.
- **Loose letters**: printed face up, with a 45° chamfer drawn in 0.2 mm steps (one per layer). The face is the top 3 mm, so a two-tone print needs only one colour change per plate. Letters are split over two plates by width, so two printers share the work.
- **Plate layout**: AMS plates keep a 45 × 55 mm corner free for the prime tower.

## Verification

Checked for these designs:

- **Overlap with the Netflix logo**: 83 % (above).
- **One-piece contact**: letters meet the plinth with 0.008 mm³ of overlap. Vertical rays through every letter run solid into the plinth.
- **Two-part fit**: letter tabs clear the plinth pockets by 0.146 mm.
- **Every build variant**:
  - no slivers in any part,
  - real Bambu start G-code (textured-plate bed temperature, A1 mini/A2L calibration routine),
  - each plate on the intended filament,
  - pauses exactly at the intended layer,
  - no slicer warnings.
- **Customisation stress test**: lowercase text, a space (`LES MER`), Norwegian `Ø`, Anton and League Gothic, `arc_depth` 0 and 0.25, and letter heights from 36 to 120 mm.

## Known limits

- `letter_height` runs from the baseline to the top of the text, so a round top overshoot (S, O) counts in it. Flat-topped outer letters of a word that contains round letters are about 1.5 % shorter (0.6 mm at 42 mm).
- In the Customizer, check that the text fits your bed. The build script checks the fit and splits the loose letters over extra plates automatically.
- `Impact` is only there if it's installed on the computer (it is on macOS and Windows). On MakerWorld, stick to Google Fonts.
- The upright one-piece stand needs supports. For the cleanest letter faces on an AMS printer, you can still print the two-part A1 mini version.
