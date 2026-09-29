// MakerWorld Parametric Model Maker edition. GENERATED from ../netflix-lettering.scad by
// tools/build.py: edit the source, not this file. Output comes from mw_plate_1/2 only.

// Netflix-style lettering display (parametric, OpenSCAD Customizer / MakerWorld style)
//
// Three designs share one lettering core:
//   "stand"   red letters standing on a black plinth whose top follows the arc
//   "plaque"  black screen-style plaque, raised red letters, Netflix progress bar, ledge stand
//   "letters" loose chunky letters for a wall, pinboard or shelf
//
// Units mm, Z up. Display datum: centred in X and Y on the text, base at Z = 0.
// Print parts ("part" = anything except "display") sit on Z = 0 in print pose: flat,
// except the one-piece stand parts, which print upright as displayed.
//
// The lettering is a free font (Bebas Neue, SIL OFL) bent like the Netflix wordmark:
// flat top edge, bottom edge on a parabolic arc, so the middle letters are shorter
// than the outer ones. Measured on the Netflix logo: middle letters 13.4 % shorter,
// word 3.70 x its height. Bebas Neue's letter widths match the logo's within about 2 %
// of the letter height; letter_spacing = 1.08 gives the best overlap (83 %) with it.
//
// No experimental features are used: text size is never measured numerically.
// Everything that depends on the text width is derived from the geometry itself
// (bounding bands and resize anchors), so any text, font or size just works.


/* [Text] */
// Text to show
text_string = "NETFLIX";
// Font (Bebas Neue matches the Netflix letter widths best; Google fonts also work on MakerWorld)
font_name = "Bebas Neue"; // [Bebas Neue, Anton, League Gothic, Impact]
// Turn the text into capitals
force_caps = true;

/* [Netflix look] */
// How much shorter the middle letters are than the outer ones (0 = straight; Netflix logo = 0.134)
arc_depth = 0.134; // [0:0.002:0.3]
// Letter spacing factor (1 = font default; 1.08 gives the Netflix word proportions with Bebas Neue)
letter_spacing = 1.08; // [0.8:0.01:1.4]
// Extra stroke weight in mm (0 = font as drawn; positive = bolder)
stroke_weight = 0; // [-0.5:0.05:1.5]

/* [Size] */
// Height of the outermost letters (baseline to top) in mm; the width follows from the text
letter_height = 42; // [15:1:150]

/* [Design] */
// Which display to build
design = "stand"; // [stand, plaque, letters]

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
// Show the Netflix progress bar under the text
plaque_progress_bar = true;
// How far the bar is filled (0..1)
plaque_progress = 0.62; // [0:0.01:1]
// Bar thickness (in the plaque plane)
plaque_bar_width = 2.4; // [1:0.1:6]
// Depth of the bar's track groove
plaque_track_depth = 0.6; // [0.2:0.2:2]
// Height of the red bar fill above the plaque face
plaque_bar_relief = 1; // [0.2:0.2:4]
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
// Recess depth and wall thickness
letters_recess_depth = 3; // [1:0.5:10]
letters_recess_wall = 2.4; // [1.2:0.2:6]

/* [Fit and print] */
// Clearance per side for push-fit joints
clearance = 0.15; // [0:0.05:0.5]
// Layer height the stepped chamfers are drawn for
layer_height = 0.2; // [0.08:0.02:0.32]

/* [Colours] */
color_letters = "#E50914"; // color
color_base    = "#141414"; // color
color_track   = "#5A5A5A"; // color

/* [MakerWorld] */
// Stand plates in MakerWorld's 3MF: two parts to press together (any printer), or one upright multi-colour piece (AMS)
makerworld_stand = "two parts"; // [two parts, one piece]

/* [Hidden] */
// What to output: "display" = coloured preview; the rest are print parts laid flat
part = "display";
// Which letter for the single-letter parts (0 = first)
letter_index = 0;
// Turn print parts about Z (e.g. 90 so tall letters run along a bed-slinger's Y axis)
print_rotate = 0;
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
module warp2d() {
    if (arc_depth == 0) children();
    else warp2d_strips() children();
}

module warp2d_strips() {
    x_start = -NORM_W / 2 - 2;
    dx = (NORM_W + 4) / warp_strips;
    for (i = [0 : warp_strips - 1]) {
        x0 = x_start + i * dx;
        x1 = x_start + (i + 1) * dx;
        scale([1, arc_scale((x0 + x1) / NORM_W)])
            intersection() {
                translate([x0, -BIG]) square([x1 - x0, 2 * BIG]);
                children();
            }
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
module clean2d() { offset(delta = 0.02, chamfer = true) offset(delta = -0.02, chamfer = true) children(); }

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
    intersection() {
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

// One-piece letters stop exactly on the plinth (round letters' overshoot is trimmed),
// so the two colours never overlap in the slicer.
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
    if (design == "stand") {
        if (makerworld_stand == "one piece") {
            color(color_base) stand_base(pockets = false);
            color(color_letters) stand_letters_upright();
        } else color(color_letters) stand_letters_flat();
    } else if (design == "plaque") {
        color(color_base) plaque_body();
        color(color_letters) plaque_red();
        color(color_track) plaque_track();
    } else {
        color(color_base) loose_word("body", "left");
        color(color_letters) loose_word("face", "left");
    }
}

module mw_plate_2() {
    if (design == "stand") {
        if (makerworld_stand != "one piece") color(color_base) stand_base(pockets = true);
    } else if (design == "plaque") color(color_base) plaque_stand();
    else {
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
    } else {
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
    else if (part == "onepiece_letters") stand_letters_upright();
    else if (part == "onepiece_base")    stand_base(pockets = false);
    else if (part == "plaque_body")      plaque_body();
    else if (part == "plaque_red")       plaque_red();
    else if (part == "plaque_track")     plaque_track();
    else if (part == "plaque_stand")     plaque_stand();
    else if (part == "letter")           loose_letter(letter_index, "all");
    else if (part == "letter_face")      loose_letter(letter_index, "face");
    else if (part == "letter_body")      loose_letter(letter_index, "body");
}

// Desktop output. The MakerWorld edition (made by tools/build.py) turns this off, because
// MakerWorld adds any top-level geometry to every plate; its output is mw_plate_N() above.
if (desktop_output) {
    if (part == "display") display();
    else if (part == "template") template2d();
    else rotate([0, 0, print_rotate]) print_part();
}
