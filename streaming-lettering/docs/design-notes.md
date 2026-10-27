# Design notes

How the streaming look was measured and rebuilt, and the techniques that keep the model fully parametric in plain OpenSCAD.

## Measuring the reference wordmark

A streaming service's wordmark (an SVG used only as a local reference and not included in this repo) was rasterised and measured column by column:

| Property | Reference wordmark |
|---|---|
| Top edge | Flat: every letter starts at the same line |
| Bottom edge | Arc, lowest at the outer letters and highest in the middle |
| Middle letters vs. outer letters | 13.4 % shorter |
| Arc shape | A parabola: at 10/20/30/40 % across, the bottom sits at 0.951/0.915/0.888/0.874 of the full height; a parabola with depth 0.134 gives 0.952/0.914/0.887/0.873 |
| Word width | 3.70 × the outer letter height |
| Stem width | 0.15–0.17 × letter height |
| Letter widths (× height) | N 0.51, E 0.43, T 0.48, F 0.44, L 0.42, I 0.15, X 0.57 |
| Gap between letters | About 0.10 × height |

The top edge is flat and only the bottom curves. That is what gives it the streaming look, and a first attempt that curved both edges looked wrong.

## Choosing the font

The reference lettering is custom, and its typeface is proprietary. Free condensed fonts, measured with OpenSCAD's `textmetrics` (widths as a fraction of cap height):

| Font | Stem | N | E | T | F | L | I | X | Word (spacing 1) |
|---|---|---|---|---|---|---|---|---|---|
| **Reference wordmark** | 0.15–0.17 | 0.51 | 0.43 | 0.48 | 0.44 | 0.42 | 0.15 | 0.57 | 3.70 |
| **Bebas Neue** | 0.16 | 0.49 | 0.43 | 0.49 | 0.42 | 0.42 | 0.16 | 0.55 | 3.41 |
| Anton | 0.19 | 0.49 | 0.41 | 0.44 | 0.40 | 0.41 | 0.19 | 0.53 | 3.21 |
| League Gothic | 0.15 | 0.43 | 0.34 | 0.42 | 0.35 | 0.34 | 0.15 | 0.47 | 2.93 |

Bebas Neue matches every letter within about 0.02 of the letter height. The only real difference is spacing. Sweeping `letter_spacing`, `arc_depth` and `stroke_weight` against the rasterised wordmark (overlap measured as intersection over union) gave the defaults:

| letter_spacing | 1.00 | 1.04 | 1.06 | **1.08** | 1.10 | 1.12 |
|---|---|---|---|---|---|---|
| overlap with the wordmark | 0.41 | 0.52 | 0.69 | **0.83** | 0.73 | 0.55 |

`arc_depth` 0.134 (the measured value) scored best. Any extra stroke weight made it worse. The rest of the gap to a perfect overlap comes from the wordmark's custom N and X diagonals.

## Bending text in plain OpenSCAD

OpenSCAD can't warp geometry, so `warp2d` cuts the word into vertical strips and scales each one vertically about the top edge, by `1 − arc_depth · (1 − u²)` (u = −1…1 across the word). Neighbouring strips abut exactly. There are enough strips that neighbours step less than 0.1 mm along the bottom edge, well below what a 0.4 mm nozzle can show.

Everything else that has to meet the lettering is bent with the same strips, so the surfaces match to within 0.01 mm:

- the plinth's arched top,
- the region under the arc used for tabs and pockets.

The arc is anchored to the text's **baseline**, not its lowest point. Round letters (S, O) dip slightly below the baseline, and anchoring to them would leave the flat letters floating above the plinth. The dip is trimmed from the one-piece letters so the two colours never overlap in the slicer.

## Parametric without measuring text

A MakerWorld-style model must react to any text, font and size, but `textmetrics` is experimental: it's off by default, and MakerWorld can't be relied on to have it. So the `.scad` never measures the text numerically. Every size and position comes from the geometry itself: bounding bands from hulls of far-shifted copies, resize anchors that carry the word's scale to every sub-shape, a Minkowski shift that centres the ink, and a small opening and closing that remove scraps and seal slits where glyph outlines meet (a slit would leave the mesh not a closed solid). The comments on `bbox2d`, `to_norm`, `to_final`, `centre_shift2d`, `clean2d` and `seal2d` explain each one.

The bend instantiates its child once per strip, so that child is kept tiny (bare text or a box). An early version that passed richer subtrees through it took 1 min 40 s per render. Three more habits keep a full render down to seconds, which MakerWorld's time limit needs:

- Offsets use bevelled joins (`chamfer = true`). Round joins put an arc on every strip corner.
- The word's x-range comes from the unbent box, because the bend only moves points vertically.
- The loose-letters preview extrudes the whole word at once instead of letter by letter.

## MakerWorld's Parametric Model Maker

Tested on MakerWorld (unpublished draft):

- **Backend:** MakerWorld runs OpenSCAD with the Manifold backend and a render limit of about 10 s. The first upload timed out; after the speedups above it generates in about 13–20 s wall-clock, including MakerWorld's own overhead.
- **Plates:** MakerWorld builds a multi-plate, multi-colour 3MF from `mw_plate_N()` modules and `color()`, and previews `mw_assembly_view()`. It also adds any top-level geometry to every plate. So `tools/build.py` generates `makerworld/streaming-lettering-makerworld.scad` with the desktop output switched off, the local font includes dropped, `font_name` marked `// font` (MakerWorld's Google Fonts picker) and the desktop-only settings hidden. The build checks that the edition has no top-level geometry and that every plate renders.
- **Its 3MF:** two plates with the right filaments, and the fully resolved A1 mini profile with real start G-code. But the bed type is Cool Plate (35 °C bed) and supports are on, and MakerWorld can only preset profile options from a model's upload page. It can't add filament-swap pauses, and multi-plate scripts can't offer STL download. The README tells users what to change.

## Printability decisions

- **Stand, two-part (no AMS)**: letters print face down, so the textured PEI plate gives the visible face. Tabs follow each letter's bent bottom edge into matching pockets, with 0.15 mm clearance per side (0.146 mm measured).
- **Stand, one piece (AMS)**: letters print upright. The horizontal arms of letters such as E, F and T overhang 7–13 mm, so the project turns on tree supports, in Bambu's "Tree Strong" style. On the A2L that's 11.5 g of support against 28.2 g for the default style, and 317 min against 362 min. The word is turned to run along Y: on a bed-slinger, the thin letters then see the bed's motion along their stiff direction.
  - *Colour changes:* the arched plinth top shares about 51 layers with the letters on the A2L (29 on the A1 mini), and each of those layers needs a colour change. That's the price of a one-piece stand; the two-part stand needs none.
- **Breakaway fins (option)**: `stand_fins` builds supports into the model, in the spirit of [Support Fins](https://printfins.com/). printfins.com itself is a browser tool with manual orientation and no command-line interface, so the build can't call it.
  - *Where fins go:* a 1 mm skin is taken under every downward-facing edge and opened with r = 0.35 mm, which keeps only the overhangs flatter than 45°.
  - *Shape:* the region under those overhangs becomes twin 0.8 mm walls with one-layer rungs every 5 mm. They stand on the plinth or on a lower arm and stop 0.25 mm short of the letters, above and beside.
  - *Why off by default:* Bambu Studio can't see model-built supports and reports a "floating cantilever", while its own tree supports are warning-free here. The build fails on either warning, so the files use tree supports.
- **Stand, colour swap**: the arched plinth has no single layer where black could end, so the stand can't be swapped mid-print. Its colour-swap version is the two-part stand, with the spool changed between plates.
- **Plaque (AMS)**: the plaque and its stand are on separate plates. On one plate, the black stand keeps rising beside the red letters, which costs a colour change on every one of their layers: 22 changes on the A2L, against 8 for the plaque alone.
- **Plaque (single colour)**: the red letters and bar fill print face down as separate pieces. They press into 1.2 mm pockets in the black plaque, with 0.15 mm clearance per side. The pockets leave 2.8 mm of plaque below; the pieces stand 2 mm (letters) and 1 mm (bar) proud, like the other versions.
- **Plaque (colour swap)**: one filament swap. Black is used up to the plaque's top face (4.0 mm), and a pause runs at the start of the 4.2 mm layer. The progress bar's track is a groove in the plaque; the red fill and scrubber dot rise out of it, so the no-AMS version still reads as a two-colour bar.
- **Loose letters**: printed face down (`letters_face_down`), so the textured plate gives the face its finish, as on the stand letters. The 45° chamfer, drawn in 0.2 mm steps (one per layer), then prints as a gentle overhang, and a back recess opens upwards with nothing to bridge. The face is the bottom 3 mm (4 mm on the A2L), so a two-tone print needs one colour change per plate, from red to black (the cheaper direction to purge). Lightning infill: only the back needs support, and lighter letters stay put on tape or putty (89 g instead of 126 g for the A2L set). The no-AMS sets split the letters over two plates by width, so two printers share the work.
- **Seams**: `tools/build.py` paints seam enforcers (Bambu's `paint_seam` triangle attribute) onto every face that points to a part's hidden side: the back of upright letters and plinths, and the bottom edge of flat-printed letters, tabs and plaques. On the A2L stand, 99 % of the letters' seams now sit on their backs; with the stock aligned seams, 76 % were on the fronts.
- **Plinth arch**: printed in the standard 0.2 mm layers. 0.1 mm layers on the arch (a height-range modifier) were tried on the two-part plinth: half-height steps on the gentle arc, but 17 min more on a 48 min plate, for a difference that matte PLA mostly hides.
- **Prime tower**: off on purpose. Bambu Studio's command-line slicer used to drop it by accident: with the same filament preset in every slot and no colours on the command line, it decides the print is single-filament. The build now passes the colours and sets the tower off explicitly. Measured on the A2L stand: a tower adds 16 min and 6 g, and flushing into infill (which needs the tower) saves less than the tower costs.
- **Plate layout**: AMS plates keep a 45 × 55 mm corner free, in case you turn the prime tower on.

## Verification

Checked by hand for these designs:

- **Overlap with the reference wordmark**: 83 % (above).
- **One-piece contact**: letters meet the plinth with 0.008 mm³ of overlap. Vertical rays through every letter run solid into the plinth.
- **Two-part fit**: letter tabs clear the plinth pockets by 0.146 mm.
- **Customisation stress test**: lowercase text, a space (`LES MER`), Norwegian `Ø`, Anton and League Gothic, `arc_depth` 0 and 0.25, and letter heights from 36 to 120 mm.

Every build also runs the automatic checks listed in [`build-summary.md`](build-summary.md).

## Known limits

- `letter_height` runs from the baseline to the top of the text, so a round top overshoot (S, O) counts in it. Flat-topped outer letters of a word that contains round letters are about 1.5 % shorter (0.6 mm at 42 mm).
- In the Customizer, check that the text fits your bed. The build script checks the fit and splits the loose letters over extra plates automatically.
- `Impact` is only there if it's installed on the computer (it is on macOS and Windows). On MakerWorld, stick to Google Fonts.
- The upright one-piece stand needs supports. For the cleanest letter faces on an AMS printer, you can still print the two-part A1 mini version.
