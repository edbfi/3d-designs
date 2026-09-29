#!/usr/bin/env python3
"""Build ready-to-print Bambu Studio projects for the Netflix-style lettering.

For every text x design x printer setup this script
  1. exports the print parts from netflix_lettering.scad with OpenSCAD,
  2. lays them out on plates (one plate per printer job),
  3. builds a Bambu Studio project with the Bambu Studio CLI (plates, names, filaments),
  4. adds filament-swap pauses for the no-AMS versions,
  5. slices every plate with the stock Bambu profiles to prove the project is printable,
  6. writes the sliced .3mf, plate previews and a summary.

Usage:
  python3 tools/build.py                   # everything
  python3 tools/build.py --only netflix --only "a1-mini$"   # filter variants (regex)
  python3 tools/build.py --list            # show variants
  python3 tools/build.py --renders-only    # just the preview renders in docs/images/renders
  python3 tools/build.py --makerworld-only # just the MakerWorld edition in makerworld/

Needs OpenSCAD (2021.01 or newer; a 2025+ snapshot with the Manifold backend is much faster)
and Bambu Studio (tested with 02.08.02.61).
"""

import argparse
import concurrent.futures as cf
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import time
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAD = ROOT / "netflix-lettering.scad"
BUILD = ROOT / "build"                           # scratch, git-ignored
PRINT_FILES = ROOT / "print-files"               # ready-to-print Bambu projects, one folder per printer setup
TEMPLATES = ROOT / "templates"                   # 1:1 wall templates for the loose letters
DOCS = ROOT / "docs"
MAKERWORLD = ROOT / "makerworld"                 # MakerWorld Parametric Model Maker edition of the .scad
PLATE_IMAGES = DOCS / "images" / "plates"
RENDER_IMAGES = DOCS / "images" / "renders"

OPENSCAD = shutil.which("openscad") or "/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD"
BAMBU = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
PROFILES = Path("/Applications/BambuStudio.app/Contents/Resources/profiles/BBL")

RED, BLACK, GREY = "#E50914", "#161616", "#5A5A5A"
TEXTS = ["NETFLIX", "SERIER"]
LAYER = 0.2  # layer height of the process preset used below; pauses are placed on this grid

# ----------------------------------------------------------------------------- printers

PRINTERS = {
    "a1-mini": dict(
        label="Bambu Lab A1 mini (no AMS)", ams=False, bed=(180, 180), margin=6,
        machine="Bambu Lab A1 mini 0.4 nozzle", process="0.20mm Standard @BBL A1M",
        filament="Bambu PLA Matte @BBL A1M", size="small"),
    "a1-mini-ams-lite": dict(
        label="Bambu Lab A1 mini + AMS lite", ams=True, bed=(180, 180), margin=6,
        machine="Bambu Lab A1 mini 0.4 nozzle", process="0.20mm Standard @BBL A1M",
        filament="Bambu PLA Matte @BBL A1M", size="small"),
    "a2l-combo-ams-lite": dict(
        label="Bambu Lab A2L Combo (AMS lite)", ams=True, bed=(330, 320), margin=8,
        machine="Bambu Lab A2L 0.4 nozzle", process="0.20mm Standard @BBL A2L",
        filament="Bambu PLA Matte @BBL A2L 0.4 nozzle", size="large"),
}

# OpenSCAD parameters per size class and design (everything else uses the file's defaults).
SIZES = {
    "small": {
        "stand": dict(letter_height=42),
        "plaque": dict(letter_height=36),
        "letters": dict(letter_height=75),
    },
    "large": {
        "stand": dict(letter_height=76, stand_letter_depth=12, stand_base_height=14,
                      stand_base_depth=50, stand_base_margin=12, stand_base_radius=8,
                      stand_base_chamfer=1.6, stand_tab_depth=6),
        "plaque": dict(letter_height=70, plaque_thickness=5, plaque_relief=3,
                       plaque_margin_x=20, plaque_margin_top=18, plaque_margin_bottom=38,
                       plaque_bar_gap=10, plaque_bar_width=4, plaque_radius=10,
                       plaque_chamfer=1.4, plaque_bar_relief=1.2, plaque_track_depth=0.8,
                       plaque_stand_height=16, plaque_stand_depth=50),
        "letters": dict(letter_height=120, letters_depth=14, letters_chamfer=1.6,
                        letters_face_depth=4),
    },
}

# ----------------------------------------------------------------------------- model

@dataclass
class Part:
    name: str                 # file stem, also the part name shown in Bambu Studio
    params: dict              # OpenSCAD -D overrides for this part
    filament: int             # 1-based filament slot
    stl: Path = None
    bbox: tuple = None        # ((xmin, ymin, zmin), (xmax, ymax, zmax))


@dataclass
class Group:
    """One object on a plate (several parts are merged into one multi-colour object)."""
    label: str
    parts: list
    print_params: dict = field(default_factory=dict)


@dataclass
class PlateSpec:
    name: str
    groups: list
    pause_z: float = None     # top_z of the first layer after a manual filament swap


@dataclass
class Variant:
    text: str
    design: str
    printer: str
    filaments: list           # colours per filament slot
    plates: list
    notes: list

    @property
    def key(self):
        return f"{self.text.lower()}-{self.design}-{self.printer}"


def scad_params(printer, design, text, **extra):
    p = dict(SIZES[PRINTERS[printer]["size"]][design])
    p.update(design=design, text_string=text)
    p.update(extra)
    return p


def letters_of(text):
    """(index in the text, character) for every printable letter (spaces are skipped)."""
    return [(i, c) for i, c in enumerate(text) if not c.isspace()]


def split_balanced(items, n):
    """Split items into n consecutive chunks of similar total width (letters stay in order)."""
    total = sum(w for _, w in items)
    chunks, cur, acc = [], [], 0.0
    for it in items:
        cur.append(it)
        acc += it[1]
        if len(chunks) < n - 1 and acc >= total * (len(chunks) + 1) / n:
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


def make_variants():
    vs = []
    for text in TEXTS:
        for printer, pr in PRINTERS.items():
            ams = pr["ams"]
            sz = SIZES[pr["size"]]

            # --- stand: red letters on a black arc plinth
            p = scad_params(printer, "stand", text)
            if not ams:
                plates = [
                    PlateSpec("1/2 Letters - red - face down (printer A)",
                              [Group("Letters", [Part(f"{text}-stand-letters", dict(p, part="letters"), 1)])]),
                    PlateSpec("2/2 Plinth - black (printer B)",
                              [Group("Plinth", [Part(f"{text}-stand-plinth", dict(p, part="base"), 2)])]),
                ]
                notes = ["Print plate 1 in red and plate 2 in black, on two printers at the same time if you like.",
                         "Push the letters' tabs into the plinth pockets (press fit, a drop of glue makes it permanent)."]
            else:
                rot = dict(print_rotate=90)
                plates = [PlateSpec("1/1 One piece - red letters on black plinth (tree supports)", [
                    Group("Stand", [
                        Part(f"{text}-stand-plinth-onepiece", dict(p, part="onepiece_base", **rot), 2),
                        Part(f"{text}-stand-letters-onepiece", dict(p, part="onepiece_letters", **rot), 1)],
                        print_params={"enable_support": "1", "support_type": "tree(auto)"})])]
                notes = ["Printed upright in one piece; the AMS switches between red and black.",
                         "Tree supports hold up the arms of E, F and T; they snap off from the hidden undersides.",
                         "The word runs along the bed's Y axis so the thin letters are stiff against the moving bed."]
            vs.append(Variant(text, "stand", printer, [RED, BLACK], plates, notes))

            # --- plaque: black screen plaque with raised red letters and a progress bar
            p = scad_params(printer, "plaque", text)
            t = p.get("plaque_thickness", 4)
            if not ams:
                plates = [
                    PlateSpec(f"1/2 Plaque - start black, PAUSE at {t + LAYER:.1f} mm, load red (printer A)",
                              [Group("Plaque", [Part(f"{text}-plaque-body", dict(p, part="plaque_body"), 1),
                                                Part(f"{text}-plaque-red", dict(p, part="plaque_red"), 1)])],
                              pause_z=round(t + LAYER, 2)),
                    PlateSpec("2/2 Stand - black (printer B)",
                              [Group("Plaque stand", [Part(f"{text}-plaque-stand", dict(p, part="plaque_stand"), 1)])]),
                ]
                cols = [BLACK]
                notes = [f"Plate 1 starts in black and pauses at {t + LAYER:.1f} mm: unload black, load red, resume.",
                         "The progress bar's track stays as a black groove; the filled part and the letters come out red.",
                         "Slide the plaque into the stand's leaning slot."]
            else:
                plates = [PlateSpec("1/1 Plaque (black, red, grey) + stand (black)", [
                    Group("Plaque", [Part(f"{text}-plaque-body", dict(p, part="plaque_body"), 2),
                                     Part(f"{text}-plaque-red", dict(p, part="plaque_red"), 1),
                                     Part(f"{text}-plaque-track", dict(p, part="plaque_track"), 3)]),
                    Group("Plaque stand", [Part(f"{text}-plaque-stand", dict(p, part="plaque_stand"), 2)])])]
                cols = [RED, BLACK, GREY]
                notes = ["One print: the AMS does the black plaque, red letters and bar, and the grey bar track.",
                         "Slide the plaque into the stand's leaning slot."]
            vs.append(Variant(text, "plaque", printer, cols, plates, notes))

            # --- loose letters: two-tone chunky letters (black body, red face)
            p = scad_params(printer, "letters", text)
            depth = p.get("letters_depth", 10)
            face = p.get("letters_face_depth", 3)
            letters = letters_of(text)
            if not ams:
                groups = [Group(f"Letter {i + 1} {c}", [Part(f"{text}-letter-{i + 1}-{c}",
                                                        dict(p, part="letter", letter_index=i), 1)])
                          for i, c in letters]
                pz = round(depth - face + LAYER, 2)
                plates = [PlateSpec(f"Letters - start black, PAUSE at {pz:.1f} mm, load red", groups, pause_z=pz)]
                cols = [BLACK]
                notes = [f"Each plate starts in black and pauses at {pz:.1f} mm: swap to red and resume "
                         "(delete the pause in Bambu Studio for all-red letters).",
                         "The letters are split over two plates so two printers can share the work.",
                         "Hang them with the paper template in templates/ so the arc lines up."]
            else:
                groups = [Group(f"Letter {i + 1} {c}", [
                    Part(f"{text}-letter-{i + 1}-{c}-body", dict(p, part="letter_body", letter_index=i), 2),
                    Part(f"{text}-letter-{i + 1}-{c}-face", dict(p, part="letter_face", letter_index=i), 1)])
                    for i, c in letters]
                plates = [PlateSpec("Letters - black body, red face", groups)]
                cols = [RED, BLACK]
                notes = ["Two-tone letters: the AMS changes from black to red once per plate.",
                         "Hang them with the paper template in templates/ so the arc lines up."]
            vs.append(Variant(text, "letters", printer, cols, plates, notes))
    return vs

# ----------------------------------------------------------------------------- helpers

def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def fmt_param(v):
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, bool):
        return "true" if v else "false"
    return repr(v)


def export_stl(part: Part, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    part.stl = out_dir / f"{part.name}.stl"
    args = [OPENSCAD, "--backend=manifold", "--export-format", "binstl", "-o", str(part.stl)]
    for k, v in part.params.items():
        args += ["-D", f"{k}={fmt_param(v)}"]
    args.append(str(SCAD))
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0 or not part.stl.exists():
        raise RuntimeError(f"OpenSCAD failed for {part.name}:\n{r.stderr[-2000:]}")
    bad = [l for l in r.stderr.splitlines() if l.startswith(("ERROR", "WARNING"))]
    if bad:
        raise RuntimeError(f"OpenSCAD reported problems for {part.name}:\n" + "\n".join(bad))
    part.bbox = stl_bbox(part.stl)
    slivers = stl_slivers(part.stl)
    if slivers:
        raise RuntimeError(f"{part.name}: stray sliver pieces in the mesh (size, min corner): {slivers[:3]}")
    return part


def stl_slivers(path: Path, min_width=0.4):
    """Connected mesh pieces thinner than min_width in X or Y, or with a handful of
    triangles: these are geometry artefacts, never real features of these designs."""
    data = path.read_bytes()
    n = struct.unpack_from("<I", data, 80)[0]
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    tris = []
    for rec in struct.iter_unpack("<12fH", data[84:84 + 50 * n]):
        vs = [(round(rec[k], 4), round(rec[k + 1], 4), round(rec[k + 2], 4)) for k in (3, 6, 9)]
        tris.append(vs[0])
        for v in vs[1:]:
            ra, rb = find(vs[0]), find(v)
            if ra != rb:
                parent[ra] = rb
    lo, hi, count = {}, {}, {}
    for t in parent:
        r = find(t)
        l, h = lo.setdefault(r, list(t)), hi.setdefault(r, list(t))
        for a in range(3):
            l[a] = min(l[a], t[a])
            h[a] = max(h[a], t[a])
    for t in tris:
        r = find(t)
        count[r] = count.get(r, 0) + 1
    bad = []
    for r in lo:
        size = [round(hi[r][a] - lo[r][a], 3) for a in range(3)]
        if min(size[0], size[1]) < min_width or count.get(r, 0) < 12:  # a plain box has 12
            bad.append((size, [round(c, 2) for c in lo[r]]))
    return bad


def stl_bbox(path: Path):
    data = path.read_bytes()
    n = struct.unpack_from("<I", data, 80)[0]
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    for rec in struct.iter_unpack("<12fH", data[84:84 + 50 * n]):
        for k in (3, 6, 9):
            for a in range(3):
                v = rec[k + a]
                if v < lo[a]:
                    lo[a] = v
                if v > hi[a]:
                    hi[a] = v
    if n == 0:
        raise RuntimeError(f"{path} is empty")
    return tuple(lo), tuple(hi)


def group_bbox(g: Group):
    lo = [min(p.bbox[0][a] for p in g.parts) for a in range(3)]
    hi = [max(p.bbox[1][a] for p in g.parts) for a in range(3)]
    return lo, hi


def resolve_preset(kind, name):
    """Resolve a Bambu system preset with its inherits chain and include templates."""
    d = json.loads((PROFILES / kind / f"{name}.json").read_text())
    out = {}
    if d.get("inherits"):
        out.update(resolve_preset(kind, d["inherits"]))
    for inc in d.get("include") or []:
        out.update({k: v for k, v in resolve_preset(kind, inc).items()
                    if k not in ("name", "instantiation", "type", "from", "setting_id")})
    out.update({k: v for k, v in d.items() if k not in ("inherits", "include")})
    return out


def flat_presets(printer, colours):
    """Write fully resolved presets (the CLI does not resolve includes on its own)."""
    pr = PRINTERS[printer]
    d = BUILD / "presets" / printer
    d.mkdir(parents=True, exist_ok=True)
    machine = resolve_preset("machine", pr["machine"])
    process = resolve_preset("process", pr["process"])
    process["curr_bed_type"] = "Textured PEI Plate"
    (d / "machine.json").write_text(json.dumps(machine, indent=1))
    (d / "process.json").write_text(json.dumps(process, indent=1))
    fil = []
    for i, c in enumerate(colours):
        f = resolve_preset("filament", pr["filament"])
        f["filament_colour"] = [c]
        path = d / f"filament_{i + 1}_{c.lstrip('#')}.json"
        path.write_text(json.dumps(f, indent=1))
        fil.append(path)
    return d / "machine.json", d / "process.json", fil

# ----------------------------------------------------------------------------- layout

TOWER = (45, 55)  # reserved prime-tower corner (x, y) on AMS plates


def pack(v: Variant):
    """Shelf-pack each plate's groups; split into more plates when they do not fit.
    Returns [(PlateSpec, [(group, x_center, y_center)], tower_xy)]."""
    pr = PRINTERS[v.printer]
    W, D = pr["bed"]
    m = pr["margin"]
    gap = 8
    reserve = pr["ams"] and len(v.filaments) > 1
    tower = (W - m - TOWER[0] + 5, D - m - TOWER[1] + 5) if reserve else None
    result = []
    for spec in v.plates:
        items = []
        for g in spec.groups:
            lo, hi = group_bbox(g)
            items.append((g, hi[0] - lo[0], hi[1] - lo[1]))
        # no-AMS loose letters: always two plates so two printers can share the work
        chunks = [items]
        if v.design == "letters" and not pr["ams"]:
            chunks = [[it for it, _ in c] for c in split_balanced([(it, it[1]) for it in items], 2)]
        pending = list(chunks)
        plate_sets = []
        while pending:
            chunk = pending.pop(0)
            placed, overflow = shelf(chunk, W, D, m, gap, tower)
            if overflow:
                if not placed:
                    raise RuntimeError(f"{v.key}: {overflow[0][0].label} does not fit the bed")
                pending.insert(0, overflow)
            plate_sets.append(placed)
        n = len(plate_sets)
        for k, placed in enumerate(plate_sets):
            name = spec.name
            if v.design == "letters":  # "Letters - ..." -> "Letters N E T - ..."
                head, _, tail = name.partition(" - ")
                name = f"{head} {' '.join(g.label.split()[-1] for g, _, _ in placed)} - {tail}"
            if n > 1:
                name = f"{k + 1}/{n} {name}"
            result.append((PlateSpec(name, spec.groups, spec.pause_z), placed, tower))
    return result


def shelf(items, W, D, m, gap, tower):
    """Rows from the front edge; items keep their order. Returns (placed, overflow)."""
    placed = []
    x, y, row_h = m, m, 0.0
    for idx, (g, w, d) in enumerate(items):
        limit_x = W - m
        if tower and y + d > tower[1] - gap:           # row reaches into the tower corner
            limit_x = min(limit_x, tower[0] - gap)
        if x + w > limit_x and x > m:                  # next row
            x, y, row_h = m, y + row_h + gap, 0.0
            limit_x = W - m
            if tower and y + d > tower[1] - gap:
                limit_x = min(limit_x, tower[0] - gap)
        if y + d > D - m or x + w > limit_x:
            return placed, items[idx:]
        placed.append([g, x + w / 2, y + d / 2])
        x += w + gap
        row_h = max(row_h, d)
    # centre the block on the plate when that keeps clear of the tower
    if placed:
        xs = [(p[1] - w / 2, p[1] + w / 2) for p, (_, w, _) in zip(placed, items)]
        ys = [(p[2] - d / 2, p[2] + d / 2) for p, (_, _, d) in zip(placed, items)]
        bx0, bx1 = min(a for a, _ in xs), max(b for _, b in xs)
        by0, by1 = min(a for a, _ in ys), max(b for _, b in ys)
        dx, dy = (W - (bx1 - bx0)) / 2 - bx0, (D - (by1 - by0)) / 2 - by0

        def clear(dx, dy):
            if not tower:
                return True
            for (a, b), (c, e) in zip(xs, ys):
                if a + dx < tower[0] + TOWER[0] and b + dx > tower[0] - gap and \
                   c + dy < tower[1] + TOWER[1] and e + dy > tower[1] - gap:
                    return False
            return True
        for cand in [(dx, dy), (dx, 0), (0, dy), (0, 0)]:
            if clear(*cand):
                for p in placed:
                    p[1] += cand[0]
                    p[2] += cand[1]
                break
    return [tuple(p) for p in placed], []

# ----------------------------------------------------------------------------- Bambu

def run_bambu(args, cwd: Path, logname: str):
    cwd.mkdir(parents=True, exist_ok=True)
    with open(cwd / logname, "w") as fh:
        r = subprocess.run([BAMBU] + [str(a) for a in args], cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
    res = cwd / "result.json"
    info = json.loads(res.read_text()) if res.exists() else {}
    return r.returncode, info


def assemble_json(v: Variant, layout):
    plates = []
    for spec, placed, _ in layout:
        objs, assembled = [], []
        for gi, (g, cx, cy) in enumerate(placed, start=1):
            lo, hi = group_bbox(g)
            px = cx - (lo[0] + hi[0]) / 2
            py = cy - (lo[1] + hi[1]) / 2
            pz = -lo[2]
            for part in g.parts:
                objs.append({"path": str(part.stl), "count": 1, "filaments": [part.filament],
                             "assemble_index": [gi], "pos_x": [px], "pos_y": [py], "pos_z": [pz]})
            if g.print_params:
                assembled.append({"assemble_index": gi, "print_params": g.print_params})
        plate = {"plate_name": spec.name, "need_arrange": False, "objects": objs}
        if assembled:
            plate["assembled_params"] = assembled
        plates.append(plate)
    return {"plates": plates}


def patch_project(src: Path, dst: Path, v: Variant, layout):
    """Name plates and objects, pin single-part objects to their filament,
    add pauses and place prime towers."""
    with zipfile.ZipFile(src) as zin:
        files = {n: zin.read(n) for n in zin.namelist()}

    # model_settings.config: objects are matched to groups through their part names
    by_part = {}
    for _, placed, _ in layout:
        for g, _, _ in placed:
            for part in g.parts:
                by_part[f"{part.stl.stem}_1"] = (g, part)
    root = ET.fromstring(files["Metadata/model_settings.config"])
    for obj in root.findall("object"):
        parts = obj.findall("part")
        names = [m.get("value") for pt in parts for m in pt.findall("metadata") if m.get("key") == "name"]
        hits = [by_part[n] for n in names if n in by_part]
        if not hits:
            raise RuntimeError(f"{v.key}: unknown object with parts {names}")
        group = hits[0][0]
        set_meta(obj, "name", f"{v.text} {group.label}")
        if len(parts) == 1:  # Bambu keeps part filaments only on multi-part objects
            set_meta(obj, "extruder", str(hits[0][1].filament))
    for plate, (spec, _, _) in zip(root.findall("plate"), layout):
        set_meta(plate, "plater_name", spec.name)
    files["Metadata/model_settings.config"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")).encode()

    ps = json.loads(files["Metadata/project_settings.config"])
    towers = [t for _, _, t in layout]
    if any(towers):
        ps["wipe_tower_x"] = [f"{(t or (0, 0))[0]:.1f}" for t in towers]
        ps["wipe_tower_y"] = [f"{(t or (0, 0))[1]:.1f}" for t in towers]
    ps["filament_colour"] = list(v.filaments)
    files["Metadata/project_settings.config"] = json.dumps(ps, indent=4).encode()

    pauses = [(i + 1, spec.pause_z) for i, (spec, _, _) in enumerate(layout) if spec.pause_z]
    if pauses:
        xml = ['<?xml version="1.0" encoding="utf-8"?>', "<custom_gcodes_per_layer>"]
        for pid, z in pauses:
            xml += ["<plate>", f'<plate_info id="{pid}"/>',
                    f'<layer top_z="{z}" type="1" extruder="1" color="{RED}" extra="" gcode="M400 U1"/>',
                    '<mode value="SingleExtruder"/>', "</plate>"]
        xml.append("</custom_gcodes_per_layer>")
        files["Metadata/custom_gcode_per_layer.xml"] = ("\n".join(xml) + "\n").encode()

    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for n, b in files.items():
            zout.writestr(n, b)


def name_plates(path: Path, layout):
    """Write plate names into a (sliced) project; they are display metadata only."""
    with zipfile.ZipFile(path) as zin:
        files = {n: zin.read(n) for n in zin.namelist()}
    root = ET.fromstring(files["Metadata/model_settings.config"])
    for plate, (spec, _, _) in zip(root.findall("plate"), layout):
        set_meta(plate, "plater_name", spec.name)
    files["Metadata/model_settings.config"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")).encode()
    tmp = path.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for n, b in files.items():
            zout.writestr(n, b)
    tmp.replace(path)


def set_meta(elem, key, value):
    """Set <metadata key=.. value=..> on an element (first one wins, added if missing)."""
    for m in elem.findall("metadata"):
        if m.get("key") == key:
            m.set("value", value)
            return
    m = ET.Element("metadata", {"key": key, "value": value})
    elem.insert(0, m)


def check_project(final: Path, v: Variant, layout):
    """The sliced project must use the intended filament(s) on every plate and keep plate names."""
    problems = []
    with zipfile.ZipFile(final) as z:
        info = ET.fromstring(z.read("Metadata/slice_info.config"))
        ms = ET.fromstring(z.read("Metadata/model_settings.config"))
    names = [next((m.get("value") for m in p.findall("metadata") if m.get("key") == "plater_name"), "")
             for p in ms.findall("plate")]
    for i, (plate, (spec, placed, _)) in enumerate(zip(info.findall("plate"), layout), start=1):
        want = sorted({part.filament for g, _, _ in placed for part in g.parts})
        got = sorted(int(f.get("id")) for f in plate.findall("filament") if float(f.get("used_g", 0)) > 0)
        if got != want:
            problems.append(f"plate {i}: filaments {got}, expected {want}")
        if names[i - 1] != spec.name:
            problems.append(f"plate {i}: name {names[i - 1]!r}, expected {spec.name!r}")
    return problems


def check_gcode(final: Path, layout):
    """Every pause must land at the start of its layer; start G-code must be the real one."""
    problems = []
    with zipfile.ZipFile(final) as z:
        for i, (spec, _, _) in enumerate(layout, start=1):
            g = z.read(f"Metadata/plate_{i}.gcode").decode(errors="replace")
            if "M1002 gcode_claim_action" not in g:
                problems.append(f"plate {i}: Bambu start G-code missing")
            z_now, found = None, []
            for line in g.splitlines():
                if line.startswith("; Z_HEIGHT:"):
                    z_now = float(line.split(":")[1])
                elif line.startswith("M400 U1") and z_now is not None:
                    found.append(round(z_now, 2))
            expected = [spec.pause_z] if spec.pause_z else []
            if found != expected:
                problems.append(f"plate {i}: expected pauses {expected}, found {found}")
    return problems


def build_variant(v: Variant, out_dir: Path, keep_unsliced: bool):
    pr = PRINTERS[v.printer]
    work = BUILD / "work" / v.key
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    layout = pack(v)
    asm = assemble_json(v, layout)
    (work / "assemble.json").write_text(json.dumps(asm, indent=1))
    machine, process, fils = flat_presets(v.printer, v.filaments)
    settings = f"{machine};{process}"
    filaments = ";".join(str(f) for f in fils)

    rc, info = run_bambu(["--load-settings", settings, "--load-filaments", filaments,
                          "--load-assemble-list", work / "assemble.json",
                          "--outputdir", work, "--export-3mf", "assembled.3mf"], work, "assemble.log")
    if rc != 0 or not (work / "assembled.3mf").exists():
        raise RuntimeError(f"{v.key}: Bambu assemble failed ({rc}) {info.get('error_string')}")
    patch_project(work / "assembled.3mf", work / "project.3mf", v, layout)

    sliced = work / "sliced"
    rc, info = run_bambu(["--load-settings", settings, "--load-filaments", filaments,
                          "--slice", "0", "--outputdir", sliced, "--export-3mf", "final.3mf",
                          work / "project.3mf"], sliced, "slice.log")
    final = sliced / "final.3mf"
    if rc != 0 or info.get("return_code") != 0 or not final.exists():
        warn = [p.get("warning_message") for p in info.get("sliced_plates", []) if p.get("warning_message")]
        raise RuntimeError(f"{v.key}: slicing failed ({rc}) {info.get('error_string')} {warn}")
    name_plates(final, layout)  # the CLI drops plate names when it slices
    problems = check_gcode(final, layout) + check_project(final, v, layout)
    if problems:
        raise RuntimeError(f"{v.key}: " + "; ".join(problems))

    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(final, out_dir / f"{v.key}.3mf")
    if keep_unsliced:
        shutil.copy(work / "project.3mf", out_dir / f"{v.key}-unsliced.3mf")
    PLATE_IMAGES.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(final) as z:
        for i in range(1, len(layout) + 1):
            name = f"Metadata/plate_{i}.png"
            if name in z.namelist():
                (PLATE_IMAGES / f"{v.key}-plate-{i}.png").write_bytes(z.read(name))

    plates = []
    for i, ((spec, placed, _), p) in enumerate(zip(layout, info["sliced_plates"]), start=1):
        plates.append(dict(
            plate=i, name=spec.name, minutes=round(p["main_predication"] / 60),
            grams={f"{f['id']}": round(f["total_used_g"], 1) for f in p.get("filaments", [])},
            colour_changes=p.get("filament_change_times", 0), pause_z=spec.pause_z,
            objects=[g.label for g, _, _ in placed],
            warning=p.get("warning_message", "")))
    return dict(key=v.key, text=v.text, design=v.design, printer=v.printer,
                printer_label=pr["label"], filaments=v.filaments, notes=v.notes, plates=plates,
                file=f"{v.printer}/{v.key}.3mf")


def export_templates(texts):
    """1:1 paper placement templates for the loose letters (SVG, mm units)."""
    TEMPLATES.mkdir(parents=True, exist_ok=True)
    jobs = []
    for text in texts:
        for size, label in (("small", "a1-mini"), ("large", "a2l-combo")):
            p = dict(SIZES[size]["letters"], design="letters", text_string=text, part="template")
            out = TEMPLATES / f"{text.lower()}-letters-template-{label}.svg"
            args = [OPENSCAD, "-o", str(out)] + sum((["-D", f"{k}={fmt_param(v)}"] for k, v in p.items()), []) + [str(SCAD)]
            jobs.append((args, out))
    with cf.ThreadPoolExecutor(4) as ex:
        for (args, out), r in zip(jobs, ex.map(lambda j: subprocess.run(j[0], capture_output=True, text=True), jobs)):
            if r.returncode != 0:
                raise RuntimeError(f"template {out.name}: {r.stderr[-800:]}")
            # OpenSCAD writes unfilled hairline paths; fill them so the outline prints solid
            svg = out.read_text().replace('stroke="black" fill="none"', 'stroke="none" fill="black"')
            out.write_text(svg)


# Desktop-only settings, hidden in the MakerWorld edition (its plates replace them).
DESKTOP_ONLY = ("part", "letter_index", "print_rotate")


def export_makerworld_edition():
    """Write the MakerWorld Parametric Model Maker edition of the .scad and check it.

    MakerWorld adds any top-level geometry to every plate, so the edition switches the
    desktop output off (its output is the mw_plate_N modules), drops the local font
    includes (MakerWorld has the fonts installed) and hides the desktop-only settings."""
    src = SCAD.read_text().splitlines()
    out, hidden = [], []
    i = 0
    while i < len(src):
        line = src[i]
        name = line.split("=")[0].strip() if "=" in line and not line.startswith((" ", "/")) else None
        if name in DESKTOP_ONLY:
            if out and out[-1].startswith("//"):
                hidden.append(out.pop())          # keep its comment with it
            hidden.append(line.split(";")[0] + ";")
        elif line.startswith("use <fonts/"):
            pass
        elif line.startswith("desktop_output = true;"):
            out.append(line.replace("desktop_output = true;", "desktop_output = false;"))
        else:
            out.append(line)
        i += 1
    k = out.index("/* [Hidden] */") + 1
    out[k:k] = hidden
    header = [
        "// MakerWorld Parametric Model Maker edition. GENERATED from ../netflix-lettering.scad by",
        "// tools/build.py: edit the source, not this file. Output comes from mw_plate_1/2 only.",
        "",
    ]
    MAKERWORLD.mkdir(parents=True, exist_ok=True)
    edition = MAKERWORLD / "netflix-lettering-makerworld.scad"
    edition.write_text("\n".join(header + out) + "\n")

    # the edition must have no top-level geometry, and every plate must render cleanly
    for design in ("stand", "plaque", "letters"):
        for plate in ("", "mw_plate_1();", "mw_plate_2();"):
            probe = BUILD / "makerworld" / f"probe-{design}-{plate[:10] or 'top'}.scad"
            probe.parent.mkdir(parents=True, exist_ok=True)
            fonts = "\n".join(f"use <{f}>" for f in sorted((ROOT / "fonts").glob("*.ttf")))
            probe.write_text(f"{fonts}\ninclude <{edition}>\n{plate}\n")
            r = subprocess.run([OPENSCAD, "--backend=manifold", "--export-format", "binstl", "-o",
                                str(probe.with_suffix(".stl")), "-D", f'design="{design}"', str(probe)],
                               capture_output=True, text=True)
            empty = "Current top level object is empty" in r.stderr
            bad = [l for l in r.stderr.splitlines() if l.startswith(("ERROR", "WARNING"))]
            if bad or (plate and (r.returncode != 0 or empty)) or (not plate and not empty):
                raise RuntimeError(f"MakerWorld edition, {design} {plate or 'top level'}: "
                                   f"{'not empty' if not plate else ''} {bad or r.stderr[-400:]}")
    return edition


# Camera per design for the preview renders: OpenSCAD gimbal "tx,ty,tz,rx,ry,rz,dist".
RENDER_CAMERAS = {"stand": "0,0,0,74,0,-22,0", "plaque": "0,0,0,80,0,-20,0", "letters": "0,0,0,82,0,-16,0"}


def export_renders(texts):
    """Coloured display renders (A1 mini sizes) for the docs."""
    RENDER_IMAGES.mkdir(parents=True, exist_ok=True)
    jobs = []
    for text in texts:
        for design, cam in RENDER_CAMERAS.items():
            p = dict(SIZES["small"][design], design=design, text_string=text, part="display")
            out = RENDER_IMAGES / f"{text.lower()}-{design}.png"
            args = [OPENSCAD, "--backend=manifold", "--render", "--imgsize=1600,1000",
                    "--colorscheme=Tomorrow", "--autocenter", "--viewall", f"--camera={cam}",
                    "-o", str(out)] + sum((["-D", f"{k}={fmt_param(v)}"] for k, v in p.items()), []) + [str(SCAD)]
            jobs.append((args, out))
    with cf.ThreadPoolExecutor(4) as ex:
        for (args, out), r in zip(jobs, ex.map(lambda j: subprocess.run(j[0], capture_output=True, text=True), jobs)):
            if r.returncode != 0 or not out.exists():
                raise RuntimeError(f"render {out.name}: {r.stderr[-800:]}")


COLOUR_NAMES = {RED: "red", BLACK: "black", GREY: "grey"}


def write_summary(results):
    lines = ["# Build summary", "",
             "Generated by `tools/build.py`. Every project was sliced with the stock Bambu Studio",
             "profiles (0.20 mm Standard, Bambu PLA Matte, textured PEI plate) and checked: real",
             "printer start G-code, the intended filament on every plate, pauses exactly where the",
             "colour changes, and no stray sliver pieces in any part.", "",
             "Times and weights are Bambu Studio's estimates. On pause plates the weight is the",
             "total for both colours (black up to the pause, red after it).", "",
             "| Project | Printer | Plates | Print time | Filament |", "|---|---|---|---|---|"]
    for r in results:
        mins = sum(p["minutes"] for p in r["plates"])
        grams = {}
        for p in r["plates"]:
            for k, g in p["grams"].items():
                grams[k] = grams.get(k, 0) + g
        paused = any(p["pause_z"] for p in r["plates"])
        fil = ", ".join(f"{COLOUR_NAMES.get(r['filaments'][int(k) - 1], r['filaments'][int(k) - 1])} {g:.0f} g"
                        for k, g in sorted(grams.items()) if g > 0)
        if paused:
            fil = f"{sum(grams.values()):.0f} g black + red (manual swap)"
        lines.append(f"| [`{r['file']}`](../print-files/{r['file']}) | {r['printer_label']} | {len(r['plates'])} | "
                     f"{mins // 60} h {mins % 60:02d} min | {fil} |")
    lines += ["", "Plates of one project can run on different printers at the same time,",
              "so the wall-clock time with two A1 minis is the longest plate, not the total.",
              "", "## Plates", ""]
    for r in results:
        lines += [f"### {r['file']}", ""]
        for n in r["notes"]:
            lines.append(f"- {n}")
        lines.append("")
        for p in r["plates"]:
            extra = f", pause at {p['pause_z']} mm" if p["pause_z"] else ""
            cc = f", {p['colour_changes']} AMS changes" if p["colour_changes"] else ""
            lines.append(f"- Plate {p['plate']}: **{p['name']}**: {p['minutes']} min{extra}{cc}")
            if p["warning"]:
                lines.append(f"  - slicer note: {p['warning'].strip()}")
        lines.append("")
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "build-summary.md").write_text("\n".join(lines) + "\n")
    (DOCS / "build-summary.json").write_text(json.dumps(results, indent=1) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", action="append", default=[], help="build variants whose key matches this regex")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4, help="parallel OpenSCAD exports")
    ap.add_argument("--keep-unsliced", action="store_true", help="also write the unsliced project")
    ap.add_argument("--renders-only", action="store_true", help="only refresh docs/images/renders")
    ap.add_argument("--no-renders", action="store_true", help="skip the preview renders")
    ap.add_argument("--makerworld-only", action="store_true", help="only write makerworld/ (the MakerWorld edition)")
    a = ap.parse_args()
    if a.renders_only:
        export_renders(TEXTS)
        return
    if a.makerworld_only:
        log(f"MakerWorld edition: {export_makerworld_edition().relative_to(ROOT)}")
        return

    variants = [v for v in make_variants() if all(re.search(o, v.key) for o in a.only)]
    if a.list:
        for v in variants:
            print(v.key)
        return
    if not variants:
        sys.exit("no variant matches")

    # 1. export all parts in parallel
    parts = [(v, part) for v in variants for s in v.plates for g in s.groups for part in g.parts]
    log(f"exporting {len(parts)} parts with OpenSCAD ({a.jobs} jobs)")
    with cf.ThreadPoolExecutor(a.jobs) as ex:
        futs = {ex.submit(export_stl, part, BUILD / "stl" / v.key): part for v, part in parts}
        for f in cf.as_completed(futs):
            f.result()
    log("templates")
    export_templates(sorted({v.text for v in variants if v.design == "letters"}))
    log(f"MakerWorld edition: {export_makerworld_edition().relative_to(ROOT)}")
    if not a.no_renders:
        log("preview renders")
        export_renders(sorted({v.text for v in variants}))

    # 2. Bambu projects (sequential: the CLI shares its data directory)
    results, failed = [], []
    for v in variants:
        try:
            r = build_variant(v, PRINT_FILES / v.printer, a.keep_unsliced)
            results.append(r)
            log(f"ok   {v.key}: " + ", ".join(f"p{p['plate']} {p['minutes']} min" for p in r["plates"]))
        except Exception as e:  # keep going, report at the end
            failed.append((v.key, str(e)))
            log(f"FAIL {v.key}: {e}")
    if results:  # merge with earlier runs so a partial rebuild keeps the full summary
        old = DOCS / "build-summary.json"
        merged = {r["key"]: r for r in (json.loads(old.read_text()) if old.exists() else [])}
        merged.update({r["key"]: r for r in results})
        order = [v.key for v in make_variants()]
        write_summary([merged[k] for k in order if k in merged])
    if failed:
        sys.exit(f"{len(failed)} variant(s) failed")


if __name__ == "__main__":
    main()
