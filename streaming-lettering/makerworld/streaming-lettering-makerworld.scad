// MakerWorld Parametric Model Maker edition. GENERATED from ../streaming-lettering.scad by
// tools/build.py: edit the source, not this file. Output comes from mw_plate_1/2 only.

// Streaming-style lettering display (parametric, OpenSCAD Customizer / MakerWorld style)
//
// Five designs share one lettering core:
//   "stand"      red letters standing on a black plinth whose top follows the arc
//   "plaque"     black screen-style plaque, raised red letters, progress bar, ledge stand
//   "letters"    loose chunky letters for a wall, pinboard or shelf
//   "frame"      the loose letters glued onto a black backing panel with a border, pinned to
//                a pinboard through the border; printed in sections that dovetail together
//   "open-frame" the same frame without the panel: two rails hidden behind the letters'
//                top and bottom strokes carry them, and the board shows through
//
// Units mm, Z up. Display datum: centred in X and Y on the text, base at Z = 0.
// Print parts ("part" = anything except "display") sit on Z = 0 in print pose. Every part
// prints without supports.
//
// The lettering is a free font (Bebas Neue, SIL OFL) bent like a streaming wordmark:
// flat top edge, bottom edge on a parabolic arc, so the middle letters are shorter
// than the outer ones. Measured on the reference wordmark: middle letters 13.4 % shorter,
// word 3.70 x its height. Bebas Neue's letter widths match the wordmark's within about 2 %
// of the letter height; letter_spacing = 1.08 gives the best overlap (83 %) with it.
//
// No experimental features are used: text size is never measured numerically.
// Everything that depends on the text width is derived from the geometry itself
// (bounding bands and resize anchors), so any text, font or size just works.


/* [Text] */
// Text to show
text_string = "SERIER";
// Font (Bebas Neue matches the reference letter widths best; Google fonts also work on MakerWorld)
font_name = "Bebas Neue"; // font
// Turn the text into capitals
force_caps = true;

/* [Streaming look] */
// How much shorter the middle letters are than the outer ones (0 = straight; reference wordmark = 0.134)
arc_depth = 0.134; // [0:0.002:0.3]
// Letter spacing factor (1 = font default; 1.08 gives the reference word proportions with Bebas Neue)
letter_spacing = 1.08; // [0.8:0.01:1.4]
// Extra stroke weight in mm (0 = font as drawn; positive = bolder)
stroke_weight = 0; // [-0.5:0.05:1.5]

/* [Size] */
// Height of the outermost letters (baseline to top) in mm; the width follows from the text
letter_height = 42; // [15:1:150]

/* [Design] */
// Which display to build
design = "stand"; // [stand, plaque, letters, frame, open-frame]

/* [Stand] */
// Letter thickness, front to back
stand_letter_depth = 8; // [3:0.5:20]
// Plinth height under the outer letters
stand_base_height = 9; // [4:0.5:30]
// Plinth depth, front to back
stand_base_depth = 30; // [10:1:80]
// Plinth overhang past the first and last letter
stand_base_margin = 7; // [0:0.5:30]
// Plinth corner radius (plan view)
stand_base_radius = 5; // [0:0.5:20]
// Chamfer on the plinth's top edges
stand_base_chamfer = 1.2; // [0:0.2:4]
// How far the letter tabs reach into the plinth (two-part build)
stand_tab_depth = 4; // [1:0.5:10]
// Letter position front to back on the plinth (0 = centred, negative = towards the front)
stand_letter_offset = 0; // [-20:0.5:20]

/* [Plaque] */
// Plaque thickness (black body)
plaque_thickness = 4; // [2:0.2:10]
// Height of the raised letters above the plaque
plaque_relief = 2; // [0.6:0.2:6]
// Border left and right of the text
plaque_margin_x = 12; // [3:0.5:40]
// Border above the text
plaque_margin_top = 11; // [3:0.5:40]
// Border below the text (holds the progress bar and the part hidden in the stand)
plaque_margin_bottom = 22; // [6:0.5:60]
// Distance from the lowest letter to the progress bar's centre line
plaque_bar_gap = 6; // [2:0.5:30]
// Corner radius
plaque_radius = 6; // [0:0.5:30]
// Chamfer on the top edge
plaque_chamfer = 1; // [0:0.2:4]
// Show the progress bar under the text
plaque_progress_bar = true;
// How far the bar is filled (0..1)
plaque_progress = 0.62; // [0:0.01:1]
// Bar thickness (in the plaque plane)
plaque_bar_width = 2.4; // [1:0.1:6]
// Depth of the bar's track groove
plaque_track_depth = 0.6; // [0.2:0.2:2]
// Height of the red bar fill above the plaque face
plaque_bar_relief = 1; // [0.2:0.2:4]
// Single-colour version: how deep the separate red letters and bar sit in their pockets
plaque_inlay_depth = 1.2; // [0.6:0.2:3]
// Lean of the plaque in its stand (degrees back from vertical)
plaque_tilt = 12; // [0:1:30]
// Stand length as a fraction of the plaque width
plaque_stand_fraction = 0.72; // [0.3:0.01:1]
// Stand height
plaque_stand_height = 12; // [6:0.5:40]
// Stand depth front to back
plaque_stand_depth = 36; // [15:1:80]

/* [Loose letters] */
// Letter thickness
letters_depth = 10; // [3:0.5:30]
// Front edge chamfer (0 = none)
letters_chamfer = 1.2; // [0:0.2:4]
// Red face thickness in the two-colour version (the rest is the black body)
letters_face_depth = 3; // [0.6:0.2:10]
// Flatten each letter's bottom so it can stand on a shelf
letters_flat_bottom = false;
// Back: "none" or a "recess" for tape, putty or magnet sheet
letters_mount = "none"; // [none, recess]
// Print the letters face down: the textured plate gives the face its finish, the chamfer
// prints as a gentle 45-degree overhang and a back recess needs no bridging
letters_face_down = true;
// Recess depth and wall thickness
letters_recess_depth = 3; // [1:0.5:10]
letters_recess_wall = 2.4; // [1.2:0.2:6]

/* [Pinboard frames] */
// The frames hold the loose letters (see above); these settings shape the frame itself.
// Frame thickness: the pins go through it, so keep it thin (3 mm leaves 5 mm of an 8 mm pin)
frame_thickness = 3; // [2:0.2:6]
// Width of the border the pins go through (a thumbtack head is about 10 mm across)
frame_border = 14; // [10:0.5:40]
// Space between the letters and the border
frame_gap = 8; // [4:0.5:40]
// Corner radius
frame_radius = 4; // [0:0.5:20]
// Chamfer on the front edges
frame_chamfer = 1; // [0:0.2:3]
// Depth of the pockets the letters sit in
frame_pocket_depth = 1.2; // [0.4:0.2:3]
// Pin hole diameter (a thumbtack shank is about 1 mm, a push pin's 1.2-1.5 mm)
frame_pin_d = 1.8; // [1:0.1:3]
// Pin holes along the top and along the bottom of each section (2 = at its ends, 3 = also mid-way)
frame_edge_pins = 2; // [2:1:3]
// Open frame: rail height, and its inset from the letters' top and bottom edges (x letter height)
frame_rail = 0.09; // [0.04:0.01:0.2]
frame_rail_inset = 0.03; // [0:0.01:0.1]
// Clearance per side in the dovetails between sections
frame_joint_clearance = 0.2; // [0:0.05:0.5]

/* [Fit and print] */
// Clearance per side for push-fit joints
clearance = 0.15; // [0:0.05:0.5]
// Layer height the stepped chamfers are drawn for
layer_height = 0.2; // [0.08:0.02:0.32]

/* [Colours] */
color_letters = "#E50914"; // color
color_base    = "#141414"; // color
color_track   = "#5A5A5A"; // color
color_board   = "#B8B0A0"; // color

/* [Hidden] */
// What to output: "display" = coloured preview; the rest are print parts laid flat
part = "display";
// Which letter for the single-letter parts (0 = first)
letter_index = 0;
// Number of sections the frame is printed in (each must fit the bed)
frame_sections = 2;
// Which section the frame_section part is (0 = leftmost)
frame_index = 0;
desktop_output = false;  // false in the MakerWorld edition
$fn = 48;
eps = 0.01;          // overlap for coplanar booleans
BIG = 1e4;           // "infinity" for bounding bands
NORM_W = 100;        // normalised word width used while bending
// Bend resolution: enough vertical strips that the step between neighbours along the
// bottom edge stays under bend_step (mm). Straight text (arc_depth = 0) needs none.
bend_step = 0.1;
warp_strips = min(800, max(60, ceil(4.2 * letter_height * arc_depth / bend_step)));
H = letter_height;

txt = force_caps ? upper(text_string) : text_string;
n_letters = len(txt);

assert(n_letters > 0, "text_string is empty");
assert(arc_depth >= 0 && arc_depth < 0.5, "arc_depth must be in [0, 0.5)");
assert(letter_index >= 0 && letter_index < n_letters, "letter_index is past the end of the text");
assert(stand_tab_depth < stand_base_height, "stand_tab_depth must be less than stand_base_height");
assert(stand_base_height < 0.85 * letter_height && plaque_margin_bottom < 0.85 * letter_height, "base height and plaque bottom margin must stay under 0.85 x letter_height");
assert(letters_face_depth < letters_depth, "letters_face_depth must be less than letters_depth");
assert(frame_index >= 0 && frame_index < frame_sections, "frame_index is past the last frame section");
assert(frame_pocket_depth < frame_thickness - 0.8, "frame_pocket_depth must leave at least 0.8 mm of frame under the pockets");
assert(frame_rail_inset + frame_rail < 0.45, "frame_rail_inset + frame_rail must stay under 0.45 so the two rails stay apart");
assert(frame_chamfer < frame_thickness, "frame_chamfer must be less than frame_thickness");
assert(frame_radius <= frame_border, "frame_radius must not exceed frame_border, or the corner pin holes break out");
assert(!(design == "frame" || design == "open-frame") || (force_caps && !letters_flat_bottom),
       "the frames need capitals (force_caps) and letters without flat bottoms");
assert(!(design == "frame" || design == "open-frame") || frame_sections <= 2
       || frame_sections <= len([for (c = txt) if (c != " ") c]) / 2,
       "with 3 or more frame_sections, each section needs at least two letters");
assert(plaque_inlay_depth < plaque_thickness - 0.8, "plaque_inlay_depth must leave at least 0.8 mm of plaque under the pockets");
assert(plaque_margin_bottom - plaque_bar_gap - plaque_bar_width > (plaque_stand_height - 3) / cos(plaque_tilt) + 1,
       "progress bar would be hidden by the stand: raise plaque_margin_bottom or lower plaque_stand_height");
echo(str("Text '", txt, "', font ", font_name, ", outer letters ", H, " mm, design ", design, ", part ", part));

// ------------------------------------------------------------------ functions

function upper(s) = chr([for (c = s) let(o = ord(c))
    (o >= 97 && o <= 122) || (o >= 224 && o <= 254 && o != 247) ? o - 32 : o]);

function prefix(s, n) = n <= 0 ? "" : chr([for (k = [0 : n - 1]) ord(s[k])]);

// Vertical scale at normalised position u in [-1, 1]: 1 at the ends, 1 - arc_depth in the middle.
function arc_scale(u) = let(v = max(-1, min(1, u))) 1 - arc_depth * (1 - v * v);

// ------------------------------------------------------------------ 2D helpers

// Bounding rectangle of 2D children.
module bbox2d() {
    intersection() {
        hull() { translate([0,  BIG]) children(); translate([0, -BIG]) children(); }
        hull() { translate([ BIG, 0]) children(); translate([-BIG, 0]) children(); }
    }
}

// Vertical band covering the children's x-range.
module xband2d() {
    hull() { translate([0, BIG]) children(); translate([0, -BIG]) children(); }
}

// Half plane y >= y0 (a finite but huge square).
module above2d(y0) { translate([-BIG, y0]) square([2 * BIG, BIG]); }

// Text in the raw frame, left aligned, top edge at y = 0 (not yet centred).
module raw_text_left(s = txt) {
    if (len(s) > 0)
        text(s, size = 10, font = font_name, spacing = letter_spacing,
             halign = "left", valign = "top");
}

// A tiny square at minus the centre of the word's ink x-range. A Minkowski sum with it
// moves a shape so the ink is centred on x = 0 (the font's side bearings would otherwise
// push the word off-centre and make the arc lopsided). Built from the ink box's top
// corners: top-left scaled by (-1/2, -1) plus top-right scaled by (-1/2, 1) gives
// x = -(xmin + xmax) / 2 while the y parts cancel. Adds < 0.004 raw units.
module centre_shift2d() {
    e = 0.002;
    minkowski() {
        scale([-0.5, -1]) ink_corner2d(e, left = true);
        scale([-0.5,  1]) ink_corner2d(e, left = false);
    }
}

// e x e square in the top-left (or top-right) corner of the raw word's ink box.
module ink_corner2d(e, left) {
    intersection() {
        difference() { bbox2d() raw_text_left(); translate([left ? e : -e, 0]) bbox2d() raw_text_left(); }
        difference() { bbox2d() raw_text_left(); translate([0, -e]) bbox2d() raw_text_left(); }
    }
}

module centred2d() { minkowski() { children(); centre_shift2d(); } }

// Text in the raw frame: ink centred on x = 0, top edge at y = 0 (valign = "top").
module raw_text(s = txt) { centred2d() raw_text_left(s); }

// Raw text -> normalised frame: word width NORM_W, centred on x = 0, top edge y = 0.
module norm_text() {
    resize([NORM_W, 0], auto = true) raw_text();
}

// Any sub-shape of the (centred) raw text -> normalised frame, exactly where it sits in the
// word. The whole word's bbox rides along far above as a width anchor and is cut off again.
module to_norm() {
    intersection() {
        resize([NORM_W, 0], auto = true) union() {
            children();
            translate([0, 1000]) bbox2d() raw_text();
        }
        translate([-BIG, -BIG]) square([2 * BIG, BIG + eps]);
    }
}

// Box from the baseline to the top of the text, raw frame: x = the ink's x-range,
// y = [-c, 0]. The arc is anchored to the baseline (where flat letters end), not to
// the lowest ink, so round letters (S, O, ...) dip slightly into the plinth instead
// of flat letters floating above it.
module cap_box_raw() {
    intersection() {
        xband2d() raw_text_left();
        mirror([0, 1]) intersection() {
            bbox2d() text(txt, size = 10, font = font_name, spacing = letter_spacing,
                          halign = "left", valign = "baseline");
            above2d(0);
        }
    }
}

// The same box in the normalised frame: x = [-50, 50] (the word is centred), y = [-c, 0].
// Built from the un-centred box (only its height is used) to keep the CSG tree small.
module norm_box() {
    intersection() {
        translate([-NORM_W / 2, -BIG]) square([NORM_W, 2 * BIG]);
        hull() {
            translate([ BIG, 0]) resize([NORM_W, 0], auto = true) cap_box_raw();
            translate([-BIG, 0]) resize([NORM_W, 0], auto = true) cap_box_raw();
        }
    }
}

// Bend normalised-frame children strip by strip (y scales about the top edge y = 0).
// Strips abut exactly (no overlap), so the union has no slivers.
module warp2d(strips = warp_strips) {
    if (arc_depth == 0) children();
    else warp2d_strips(strips) children();
}

module warp2d_strips(strips) {
    x_start = -NORM_W / 2 - 2;
    dx = (NORM_W + 4) / strips;
    for (i = [0 : strips - 1]) {
        x0 = x_start + i * dx;
        x1 = x_start + (i + 1) * dx;
        scale([1, arc_scale((x0 + x1) / NORM_W)])
            intersection() {
                translate([x0, -BIG]) square([x1 - x0, 2 * BIG]);
                children();
            }
    }
    // beyond the word the arc has ended (scale 1): anything there passes through unbent
    for (s = [-1, 1]) intersection() {
        translate([s < 0 ? -BIG : -x_start, -BIG]) square([BIG + x_start, 2 * BIG]);
        children();
    }
}

// Normalised frame -> final frame (outer letters H tall, top edge y = 0).
// A box 3x the word height rides along far to the right as a height anchor and is
// cut off again, so every shape passed through here gets the letters' scale.
// Keeps x < 900 mm and y > -1.9 H.
module to_final() {
    intersection() {
        resize([0, 3 * H], auto = true) union() {
            children();
            translate([2000, 0]) scale([1, 3]) norm_box();
        }
        translate([-BIG, -1.9 * H]) square([BIG + 900, BIG]);
    }
}

// ------------------------------------------------------------------ lettering

// The bent word, final frame: top edge y = 0, outer letters' bottom at y = -H.
module word2d() {
    clean2d() offset(delta = stroke_weight) to_final() warp2d() norm_text();
}

// Morphological opening: drops scraps thinner than 0.04 mm left by coincident edges.
// Bevelled rather than rounded joins: round joins add an arc at every strip corner.
module clean2d() { seal2d() offset(delta = 0.02, chamfer = true) offset(delta = -0.02, chamfer = true) children(); }

// Tiny mitred closing: seals zero-width slits (where glyph outlines meet, or left by an
// intersection), which would otherwise extrude into walls inside the solid, so the mesh
// would not be a closed solid.
module seal2d() { offset(delta = -0.002) offset(delta = 0.002) children(); }

// Region under the bent bottom edge (between the first and last letter), down to y = -1.9H.
// Bent with the same strips as the letters, so the two meet exactly.
module under2d() {
    to_final() difference() {
        scale([1, 2]) warp2d() norm_box();
        warp2d() norm_box();
    }
}

// The word's x-range as a vertical band, and its bbox (y is known: [-H, 0]), final frame.
// The bend only moves points vertically, so the unbent box gives the same x-range far more
// cheaply than the bent letters (which would rebuild every bend strip).
module word_xband() { offset(delta = stroke_weight) xband2d() to_final() norm_box(); }
module word_box() { intersection() { word_xband(); translate([-BIG, -H]) square([2 * BIG, H]); } }

// Band / box widened by d on both sides in x.
module word_xband_wide(d) { offset(delta = d) word_xband(); }

// Column that holds letter i (widened a little into the gaps), final frame.
module letter_column(i) {
    xband2d() to_final() intersection() {
        to_norm() intersection() {
            offset(delta = 0.2) xband2d() centred2d() difference() {
                raw_text_left(prefix(txt, i + 1));
                raw_text_left(prefix(txt, i));
            }
            bbox2d() raw_text();
        }
        norm_box();
    }
}

// One letter in the final frame (optionally with a flat bottom).
module letter2d(i) {
    seal2d() intersection() {
        letter_column(i);
        union() {
            word2d();
            if (letters_flat_bottom) intersection() {
                smear_down(H) intersection() { word2d(); letter_column(i); }
                under2d();
                bbox2d() intersection() { word2d(); letter_column(i); }
            }
        }
    }
}

// Children swept straight down by d.
module smear_down(d) {
    minkowski() {
        children();
        translate([-eps / 2, -d]) square([eps, d]);
    }
}

// Extrude with a 45-degree top chamfer drawn in layer-height steps.
module chamfer_extrude(h, c) {
    n = c > 0 ? max(1, round(c / layer_height)) : 0;
    s = n > 0 ? c / n : 0;
    linear_extrude(h - c + (n > 0 ? eps : 0)) children();
    if (n > 0) for (k = [1 : n])
        translate([0, 0, h - c + (k - 1) * s])
            // bevelled joins: a mitred inset turns microscopic notches into long spikes,
            // and round joins multiply the vertex count
            linear_extrude(s + (k < n ? eps : 0)) offset(delta = -k * s, chamfer = true) children();
}

// Rounded rectangle from a 2D shape's bbox.
module rounded_box(r) {
    if (r > 0) offset(r = r) offset(delta = -r) children();
    else children();
}

// ------------------------------------------------------------------ design: stand

// Profile (final frame) of the plinth: slab under the outer letters plus the arc region.
module stand_profile2d() {
    m = stand_base_margin;
    union() {
        intersection() {
            word_xband_wide(m);
            translate([-BIG, -H - stand_base_height]) square([2 * BIG, stand_base_height + eps]);
        }
        intersection() { under2d(); above2d(-H - eps); }
    }
}

// Plinth outline in plan view (XY), inset by d.
module stand_plan2d(d = 0) {
    m = stand_base_margin;
    offset(delta = -d) rounded_box(stand_base_radius) intersection() {
        word_xband_wide(m);
        square([2 * BIG, stand_base_depth], center = true);
    }
}

// Final-frame 2D -> display pose in the XZ plane, thickness t centred on y0.
module stand_place(t, y0 = 0) {
    translate([0, y0 + t / 2, H + stand_base_height]) rotate([90, 0, 0])
        linear_extrude(t) children();
}

// Tabs under the letters that reach into the plinth.
module stand_tab2d() {
    clean2d() intersection() {
        smear_down(stand_tab_depth) word2d();
        under2d();
    }
}

module stand_base(pockets = true) {
    c = stand_base_chamfer;
    n = c > 0 ? max(1, round(c / layer_height)) : 0;
    s = n > 0 ? c / n : 0;
    difference() {
        union() for (k = [0 : n])
            intersection() {
                translate([0, 0, -(n - k) * s])
                    stand_place(stand_base_depth + 2) stand_profile2d();
                linear_extrude(H + stand_base_height + 2) stand_plan2d(k * s);
            }
        if (pockets)
            stand_place(stand_letter_depth + 2 * clearance, stand_letter_offset)
                offset(delta = clearance) stand_tab2d();
    }
}

// Letters as displayed: they stop exactly on the plinth (round letters' overshoot is
// trimmed), so the two colours never overlap.
module stand_letters_upright() {
    stand_place(stand_letter_depth, stand_letter_offset) clean2d() difference() { word2d(); under2d(); }
}

// Two-part letters, print pose: face down (mirrored so the front is on the bed).
module stand_letters_flat() {
    mirror([1, 0, 0]) linear_extrude(stand_letter_depth)
        union() { word2d(); stand_tab2d(); }
}

// ------------------------------------------------------------------ design: plaque

// Plaque outline, final frame.
module plaque_outline2d(d = 0) {
    offset(delta = -d) rounded_box(plaque_radius) intersection() {
        word_xband_wide(plaque_margin_x);
        translate([-BIG, -H - plaque_margin_bottom]) square([2 * BIG, H + plaque_margin_bottom + plaque_margin_top]);
    }
}

// Bar centre line, a fixed gap under the outer letters.
bar_y = -H - plaque_bar_gap;

module plaque_track2d() {
    intersection() {
        word_xband();
        translate([-BIG, bar_y - plaque_bar_width / 2]) square([2 * BIG, plaque_bar_width]);
    }
}

// Left and right edge slivers (0.2 mm) of the word's x-range, as vertical bands.
module left_sliver2d()  { difference() { word_xband(); translate([ 0.2, 0]) word_xband(); } }
module right_sliver2d() { difference() { word_xband(); translate([-0.2, 0]) word_xband(); } }

// Sliver at the fill's end: the word is centred on x = 0, so the point at fraction f
// of its width is the right edge scaled by (2f - 1) (mirrored when f < 0.5).
module fill_end2d() { scale([2 * plaque_progress - 1, 1]) right_sliver2d(); }

// Filled part of the bar plus the round scrubber at its end.
module plaque_fill2d() {
    intersection() {
        plaque_track2d();
        hull() { left_sliver2d(); fill_end2d(); }
    }
    // scrubber dot: a 0.2 mm seed at the fill end, grown to the dot size
    minkowski() {
        intersection() { fill_end2d(); translate([-BIG, bar_y - 0.1]) square([2 * BIG, 0.2]); }
        circle(d = plaque_bar_width * 2.2 - 0.2);
    }
}

module plaque_body() {
    difference() {
        chamfer_extrude(plaque_thickness, plaque_chamfer) plaque_outline2d();
        if (plaque_progress_bar)
            translate([0, 0, plaque_thickness - plaque_track_depth])
                linear_extrude(plaque_track_depth + 1) plaque_track2d();
    }
}

module plaque_red() {
    translate([0, 0, plaque_thickness - eps]) linear_extrude(plaque_relief + eps) word2d();
    if (plaque_progress_bar)
        translate([0, 0, plaque_thickness - plaque_track_depth])
            linear_extrude(plaque_track_depth + plaque_bar_relief) plaque_fill2d();
}

// Single-colour version, black part: the plaque with pockets for the separate red pieces.
module plaque_body_inlay() {
    difference() {
        plaque_body();
        translate([0, 0, plaque_thickness - plaque_inlay_depth])
            linear_extrude(plaque_inlay_depth + 1) offset(delta = clearance) {
                word2d();
                if (plaque_progress_bar) plaque_fill2d();
            }
    }
}

// Single-colour version, red part: letters and bar fill as press-in pieces, face down
// (mirrored so the front is on the textured plate).
module plaque_inlays() {
    mirror([1, 0, 0]) {
        linear_extrude(plaque_inlay_depth + plaque_relief) word2d();
        if (plaque_progress_bar)
            linear_extrude(plaque_inlay_depth + plaque_bar_relief) plaque_fill2d();
    }
}

module plaque_track() {
    if (plaque_progress_bar)
        translate([0, 0, plaque_thickness - plaque_track_depth])
            linear_extrude(plaque_track_depth) difference() { plaque_track2d(); plaque_fill2d(); }
}

// Ledge stand, print pose: long bar with a leaning slot.
module plaque_stand() {
    slot = plaque_thickness + 2 * clearance;
    D = plaque_stand_depth;
    h = plaque_stand_height;
    difference() {
        // rounded ends in plan, chamfered top in section
        intersection() {
            linear_extrude(h) rounded_box(min(D / 2 - eps, 8)) intersection() {
                xband2d() scale([plaque_stand_fraction, 1]) plaque_outline2d();
                square([2 * BIG, D], center = true);
            }
            rotate([90, 0, 90]) linear_extrude(2 * BIG, center = true)
                polygon([[-D / 2, 0], [D / 2, 0], [D / 2 - 6, h], [-D / 2 + 6, h]]);
        }
        // slot leaning back by plaque_tilt, floor at 3 mm
        translate([0, 0, 3]) rotate([-plaque_tilt, 0, 0])
            translate([-BIG, -slot / 2, 0]) cube([2 * BIG, slot, 3 * h]);
    }
}

// ------------------------------------------------------------------ design: loose letters

module loose_letter(i, zone = "all") {
    f = letters_depth - letters_face_depth;
    difference() {
        intersection() {
            chamfer_extrude(letters_depth, letters_chamfer) letter2d(i);
            if (zone == "face") translate([-BIG, -BIG, f]) cube([2 * BIG, 2 * BIG, BIG]);
            if (zone == "body") translate([-BIG, -BIG, -1]) cube([2 * BIG, 2 * BIG, f + 1]);
        }
        if (letters_mount == "recess")
            translate([0, 0, -1]) linear_extrude(letters_recess_depth + 1)
                offset(delta = -letters_recess_wall) letter2d(i);
    }
}

// Loose letters, face up -> print pose: turned over onto the face when letters_face_down
// (a rotation, not a mirror, so the letters read correctly once picked up).
module letters_print_pose() {
    if (letters_face_down) translate([0, 0, letters_depth]) rotate([0, 180, 0]) children();
    else children();
}

// All letters in place, flat, face up (preview and MakerWorld plates; no flat bottoms).
// half = "left"/"right" keeps only the letters before/from the middle one.
module loose_word(zone, half = "all") {
    f = letters_depth - letters_face_depth;
    m = floor(n_letters / 2);
    difference() {
        intersection() {
            chamfer_extrude(letters_depth, letters_chamfer) word2d();
            if (zone == "face") translate([-BIG, -BIG, f]) cube([2 * BIG, 2 * BIG, BIG]);
            if (zone == "body") translate([-BIG, -BIG, -1]) cube([2 * BIG, 2 * BIG, f + 1]);
            if (half == "left")  translate([0, 0, -1]) linear_extrude(BIG) hull() { letter_column(0); letter_column(m - 1); }
            if (half == "right") translate([0, 0, -1]) linear_extrude(BIG) hull() { letter_column(m); letter_column(n_letters - 1); }
        }
        if (letters_mount == "recess")
            translate([0, 0, -1]) linear_extrude(letters_recess_depth + 1)
                offset(delta = -letters_recess_wall) word2d();
    }
}

// ------------------------------------------------------------------ design: pinboard frames
// The frame prints back down in frame_sections sections that dovetail together; each
// section is pinned to the board through its border, and the loose letters (printed as in
// the letters design) are glued into word-shaped pockets. Nothing here measures the text:
// the section cuts are placed from the letters' own columns.

frame_open = design == "open-frame";
frame_out = frame_gap + frame_border;                // word box -> outer edge
frame_top_y = frame_gap + frame_border / 2;          // centre lines of the top and bottom border
frame_bottom_y = -H - frame_gap - frame_border / 2;

module frame_xband() { word_xband_wide(frame_out); }

module frame_outline2d() {
    rounded_box(frame_radius) intersection() {
        frame_xband();
        translate([-BIG, -H - frame_out]) square([2 * BIG, H + 2 * frame_out]);
    }
}

module frame_window2d() { offset(delta = -frame_border) frame_outline2d(); }

// A capital "H" in the raw frame, from the baseline (y = 0) up.
module cap_h_raw() {
    intersection() {
        bbox2d() text("H", size = 10, font = font_name, valign = "baseline");
        above2d(0);
    }
}

// Band between fractions [a, b] of a capital's height above the baseline, normalised frame,
// right across. Measured on an "H" rather than the whole text, so accents that reach above
// the capitals (Å) don't move it. Built like norm_box() (the
// band rides on the baseline of cap_box_raw() and gets the word's scale from its x-range):
// the bend instantiates it once per strip, and the centred text would cost far more memory.
module cap_band_norm(a, b) {
    intersection() {
        translate([-BIG, -BIG]) square([2 * BIG, BIG]);  // below the top edge, which to_final() scales from
        hull() for (s = [-1, 1]) translate([s * BIG, 0]) resize([NORM_W, 0], auto = true) intersection() {
            xband2d() cap_box_raw();
            minkowski() {
                hull() for (s = [-1, 1]) translate([s * BIG, 0]) difference() {
                    scale([1, b]) cap_h_raw();
                    if (a > 0) scale([1, a]) cap_h_raw();
                }
                difference() { cap_box_raw(); translate([0, eps]) cap_box_raw(); }  // the baseline
            }
        }
    }
}

// The open frame's rails behind the letters' top and bottom strokes, so they show only
// between the letters: bent with the letters, so they keep their place in every letter, and
// straight beyond the word, where the arc has ended.
// They bend in coarser strips than the letters (0.3 mm steps along their edges, finer than an
// extrusion line): every strip instantiates the band, which costs memory.
rail_strips = min(warp_strips, max(60, ceil(4.2 * letter_height * arc_depth / 0.3)));
module frame_rails2d() {
    to_final() warp2d(rail_strips) render() {
        cap_band_norm(frame_rail_inset, frame_rail_inset + frame_rail);
        cap_band_norm(1 - frame_rail_inset - frame_rail, 1 - frame_rail_inset);
    }
}

module frame2d() {
    if (frame_open) {
        difference() { frame_outline2d(); frame_window2d(); }
        intersection() {
            union() { frame_rails2d(); if (frame_has_marks) frame_marks2d(); }
            offset(delta = eps) frame_window2d();
        }
    } else frame_outline2d();
}

// Open frame: a pad behind each mark above the capitals (an Å's ring), so it has a pocket to
// sit in, tied down to the top rail by a 2 mm strip through the middle of its letter. Only
// letters past ASCII can carry such marks, and the pads double the frame's memory, so plain
// text skips them.
frame_has_marks = len([for (c = txt) if (ord(c) > 127) c]) > 0;
module frame_marks2d() {
    frame_marks_ink2d();
    // the strip starts below the mark, so it doesn't show through a ring's hole
    difference() {
        smear_down(0.15 * H) frame_marks_mid2d();
        minkowski() { frame_marks_mid2d(); square([eps, 0.15 * H]); }
    }
}

module frame_marks_ink2d() {
    intersection() { word2d(); to_final() warp2d(rail_strips) render() cap_band_norm(1, 3); }
}

// The marks where they cross the 2 mm strips through the middle of each letter.
module frame_marks_mid2d() {
    intersection() {
        frame_marks_ink2d();
        for (j = [0 : len(frame_letters) - 1]) offset(delta = 1) frame_mid2d(frame_letters[j]);
    }
}

// Each cut between two sections runs through the middle of a letter (spaces skipped), so a
// glued letter, one rigid piece, splices the joint: on the open frame it is all that joins
// the rails. Cut j goes through the letter whose share of the word (counting every letter
// as equally wide) holds the point (j + 1) / frame_sections of the way along; on a tie, the
// left one.
frame_letters = [for (i = [0 : n_letters - 1]) if (txt[i] != " ") i];
frame_cut_letters = frame_sections < 2 ? [] :
    [for (j = [0 : frame_sections - 2]) frame_letters[ceil((j + 1) * len(frame_letters) / frame_sections) - 1]];

// Vertical sliver through the middle of cut j's letter.
module frame_cut2d(j) { frame_mid2d(frame_cut_letters[j]); }

// Vertical sliver through the middle of letter i: the mean of its column's edges, as a
// Minkowski sum of both edge slivers scaled by 1/2.
module frame_mid2d(i) {
    minkowski() {
        scale([0.5, 1]) difference() { letter_column(i); translate([eps, 0]) letter_column(i); }
        scale([0.5, 1]) difference() { letter_column(i); translate([-eps, 0]) letter_column(i); }
    }
}

// Left (s = -1) or right (s = 1) end of section k: the frame's edge or a cut.
module frame_end2d(k, s) {
    if (s < 0 && k > 0) frame_cut2d(k - 1);
    else if (s > 0 && k < frame_sections - 1) frame_cut2d(k);
    else difference() { frame_xband(); translate([-s * eps, 0]) frame_xband(); }
}

// Seed (eps square) on a vertical sliver at height y: a Minkowski sum with it puts a shape
// drawn around the origin there.
module frame_seed2d(y) { intersection() { children(); translate([-BIG, y]) square([2 * BIG, eps]); } }

// Dovetail tongue pointing +x: neck at x = 0, head at x = len, and 1 mm of root.
module dovetail2d(neck, head, len) {
    polygon([[-1, -neck / 2], [0, -neck / 2], [len, -head / 2], [len, head / 2], [0, neck / 2], [-1, neck / 2]]);
}

frame_tongue_len = 0.45 * frame_border;

// Tongues of section j into section j + 1, in the top and bottom border.
module frame_tongues2d(j) {
    for (y = [frame_top_y, frame_bottom_y])
        minkowski() {
            frame_seed2d(y) frame_cut2d(j);
            dovetail2d(0.4 * frame_border, 0.55 * frame_border, frame_tongue_len);
        }
}

// Section k's share of the plane: between its ends, plus its tongues, minus sockets for
// the tongues of the section to its left.
module frame_section2d(k) {
    difference() {
        union() {
            hull() { frame_end2d(k, -1); frame_end2d(k, 1); }
            if (k < frame_sections - 1) frame_tongues2d(k);
        }
        if (k > 0) offset(delta = frame_joint_clearance) frame_tongues2d(k - 1);
    }
}

// Pin holes of section k, in the middle of the top and bottom border: at its outer ends,
// either side of each joint (so the pin heads hold the joint flat), and mid-way if asked.
module frame_holes2d(k) {
    N = frame_sections;
    socket = frame_tongue_len + frame_joint_clearance;
    left = k == 0 ? frame_border / 2 : socket + 3;
    right = k == N - 1 ? -frame_border / 2 : -3;
    for (y = [frame_top_y, frame_bottom_y]) minkowski() {
        union() {
            translate([left, 0]) frame_seed2d(y) frame_end2d(k, -1);
            translate([right, 0]) frame_seed2d(y) frame_end2d(k, 1);
            if (frame_edge_pins == 3) frame_seed2d(y) minkowski() {  // half-way between those two
                scale([0.5, 1]) translate([left, 0]) frame_end2d(k, -1);
                scale([0.5, 1]) translate([right, 0]) frame_end2d(k, 1);
            }
        }
        circle(d = frame_pin_d - eps);
    }
}

// Frame body: only the outer edge is chamfered, so the rails keep their full width.
module frame_body(k = -1) {
    intersection() {
        chamfer_extrude(frame_thickness, frame_chamfer) frame_outline2d();
        translate([0, 0, -1]) linear_extrude(frame_thickness + 2) intersection() {
            frame2d();
            if (k >= 0) frame_section2d(k);
        }
    }
}

// One section, print pose: back down, so the pockets open upwards and nothing overhangs.
module frame_section(k) {
    t = frame_thickness;
    difference() {
        frame_body(k);
        translate([0, 0, t - frame_pocket_depth]) linear_extrude(frame_pocket_depth + 1)
            offset(delta = clearance) word2d();
        translate([0, 0, -1]) linear_extrude(t + 2) frame_holes2d(k);
        if (!frame_open) translate([0, 0, t - 0.6]) linear_extrude(1) frame_groove2d();
    }
}

// Backing panel: a groove along the border's inner edge, so the border reads as a frame.
module frame_groove2d() {
    difference() { offset(delta = 0.6) frame_window2d(); offset(delta = -0.6) frame_window2d(); }
}

// Frame with its letters, upright; the desktop preview adds a strip of pinboard behind it.
module frame_display() {
    board = desktop_output ? 25 : 0;
    translate([0, 0, H + frame_out + board]) rotate([90, 0, 0]) {
        if (desktop_output)
            color(color_board) translate([0, 0, -2]) linear_extrude(2) offset(delta = board) frame_outline2d();
        color(color_base) difference() {
            frame_body();
            if (!frame_open) translate([0, 0, frame_thickness - 0.6]) linear_extrude(1) frame_groove2d();
        }
        translate([0, 0, frame_thickness - frame_pocket_depth]) {
            color(color_base) loose_word("body");
            color(color_letters) loose_word("face");
        }
    }
}

// ------------------------------------------------------------------ template (2D, 1:1)

module template2d() {
    difference() {
        offset(delta = 0.4) word2d();
        word2d();
    }
    // top alignment line and centre tick
    intersection() {
        word_xband_wide(10);
        translate([-BIG, 1.5]) square([2 * BIG, 0.4]);
    }
    translate([-0.2, 1.5]) square([0.4, 5]);
}

// ------------------------------------------------------------------ output

// ------------------------------------------------------------------ MakerWorld plates
// MakerWorld's Parametric Model Maker calls these itself to build a multi-plate, multi-colour
// 3MF (never call them from this file). Desktop OpenSCAD ignores them. Plate 1 and plate 2
// can print on two printers at once; colours come from color().
module mw_plate_1() {
    if (design == "stand") color(color_letters) stand_letters_flat();
    else if (design == "plaque") {
        color(color_base) plaque_body();
        color(color_letters) plaque_red();
        color(color_track) plaque_track();
    } else if (design == "frame" || design == "open-frame") color(color_base) frame_section(0);
    else letters_print_pose() {
        color(color_base) loose_word("body", "left");
        color(color_letters) loose_word("face", "left");
    }
}

module mw_plate_2() {
    if (design == "stand") color(color_base) stand_base(pockets = true);
    else if (design == "plaque") color(color_base) plaque_stand();
    else if (design == "frame" || design == "open-frame") color(color_base) frame_section(1);
    else letters_print_pose() {
        color(color_base) loose_word("body", "right");
        color(color_letters) loose_word("face", "right");
    }
}

module mw_assembly_view() { display(); }

module display() {
    if (design == "stand") {
        color(color_base) stand_base(pockets = false);
        color(color_letters) stand_letters_upright();
    } else if (design == "plaque") {
        // plaque leaning in its stand
        color(color_base) plaque_stand();
        translate([0, 0, 3]) rotate([-plaque_tilt, 0, 0])
            translate([0, plaque_thickness / 2, 0]) rotate([90, 0, 0])
                translate([0, H + plaque_margin_bottom, 0]) {
                    color(color_base) plaque_body();
                    color(color_letters) plaque_red();
                    color(color_track) plaque_track();
                }
    } else if (design == "frame" || design == "open-frame") frame_display();
    else {
        // the whole word at once: splitting it into letters is only needed for printing
        translate([0, letters_depth / 2, H]) rotate([90, 0, 0]) {
            color(color_base) loose_word("body");
            color(color_letters) loose_word("face");
        }
    }
}

module print_part() {
    if      (part == "letters")          stand_letters_flat();
    else if (part == "base")             stand_base(pockets = true);
    else if (part == "plaque_body")      plaque_body();
    else if (part == "plaque_red")       plaque_red();
    else if (part == "plaque_track")     plaque_track();
    else if (part == "plaque_stand")     plaque_stand();
    else if (part == "plaque_body_inlay") plaque_body_inlay();
    else if (part == "plaque_inlays")    plaque_inlays();
    else if (part == "letter")           letters_print_pose() loose_letter(letter_index, "all");
    else if (part == "letter_face")      letters_print_pose() loose_letter(letter_index, "face");
    else if (part == "letter_body")      letters_print_pose() loose_letter(letter_index, "body");
    else if (part == "frame_section")    frame_section(frame_index);
}

// Desktop output. The MakerWorld edition (made by tools/build.py) turns this off, because
// MakerWorld adds any top-level geometry to every plate; its output is mw_plate_N() above.
if (desktop_output) {
    if (part == "display") display();
    else if (part == "template") template2d();
    else print_part();
}
