#!/usr/bin/env python3
"""Build ready-to-print Bambu Studio projects for the Q6A fan stand.

For every project x printer this script
  1. checks the fit in use: no part touches the case, the fan or a keep-out (plugs, buttons, the
     microSD card, the jumpers, the antenna leads, the air gap), and the hood meets the base
     only at the sockets' crush ribs,
  2. exports the parts from q6a-fan-stand.py with build123d, in their print poses, and checks
     each mesh is a closed solid with no stray slivers,
  3. lays the parts out on plates and builds a Bambu Studio project with the Bambu Studio CLI,
  4. slices every plate with the stock Bambu profiles (Bambu PETG Basic) and fails on slicer
     supports and on overhangs Bambu Studio would leave unsupported,
  5. writes the sliced .3mf, plate previews, a summary, and the STEP export for MakerWorld.

Usage:
  python3 tools/build.py --jobs 2            # everything
  python3 tools/build.py --only fit-test     # filter projects (regex on the project key)
  python3 tools/build.py --list              # show projects

Needs build123d 0.13 and Bambu Studio 02.08.02.61; the repo's ../tools/docker/ provides both:
`../tools/docker/run.sh python3 tools/build.py --jobs 2`.
"""

import argparse
import concurrent.futures as cf
import importlib.util
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
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "q6a-fan-stand.py"
BUILD = ROOT / "build"                           # scratch, git-ignored
PRINT_FILES = ROOT / "print-files"               # ready-to-print Bambu projects, one folder per printer
MAKERWORLD = ROOT / "makerworld"                 # the STEP export for the MakerWorld listing
DOCS = ROOT / "docs"
PLATE_IMAGES = DOCS / "images" / "plates"

BAMBU = os.environ.get("BAMBU_STUDIO", "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
PROFILES = Path(os.environ.get("BAMBU_PROFILES", "/Applications/BambuStudio.app/Contents/Resources/profiles/BBL"))

COLOUR = "#2B2B2D"  # PETG Basic Black: the case is black, and black hides the guard's layer lines

PRINTERS = {
    "a1-mini": dict(
        name="Bambu Lab A1 mini", bed=(180, 180), margin=6,
        machine="Bambu Lab A1 mini 0.4 nozzle", process="0.20mm Standard @BBL A1M",
        filament="Bambu PETG Basic @BBL A1M 0.4 nozzle"),
    "a2l-combo": dict(
        name="Bambu Lab A2L Combo", bed=(330, 320), margin=8,
        machine="Bambu Lab A2L 0.4 nozzle", process="0.20mm Standard @BBL A2L",
        filament="Bambu PETG Basic @BBL A2L 0.4 nozzle"),
}

# Parts: model function and print pose. The hood prints upside down, the guard on the bed.
PARTS = {
    "hood": ("hood", (180, 0, 0)),
    "base": ("base", (0, 0, 0)),
    "fit-test": ("fit_test", (0, 0, 0)),
}

# Projects: plates per printer, each plate a list of parts.
PROJECTS = {
    "fit-test": dict(label="Fit test: print this first",
                     plates={"a1-mini": [["fit-test"]], "a2l-combo": [["fit-test"]]}),
    "fan-stand": dict(label="Fan stand: hood and base",
                      plates={"a1-mini": [["hood"], ["base"]], "a2l-combo": [["hood", "base"]]}),
}
PLATE_NAMES = {("hood",): "Hood", ("base",): "Base", ("hood", "base"): "Hood and base",
               ("fit-test",): "Fit test"}


@dataclass
class Variant:
    project: str
    printer: str

    @property
    def key(self):
        return f"q6a-fan-stand-{self.project}-{self.printer}"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def load_source():
    spec = importlib.util.spec_from_file_location("q6a_fan_stand", SOURCE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ----------------------------------------------------------------------------- export

def export_part(name):
    """Export one part in its print pose to build/stl/<name>.stl; returns (name, bbox)."""
    import build123d as bd
    src = load_source()
    func, rot = PARTS[name]
    shape = bd.Rot(*rot) * getattr(src, func)()
    path = BUILD / "stl" / f"{name}.stl"
    path.parent.mkdir(parents=True, exist_ok=True)
    bd.export_stl(shape, str(path), tolerance=0.01, angular_tolerance=0.15)
    bad = stl_bad_edges(path)
    if bad:
        raise RuntimeError(f"{name}: {len(bad)} edges not shared by exactly two triangles "
                           f"(not a closed solid), e.g. at {bad[:3]}")
    slivers = stl_slivers(path)
    if slivers:
        raise RuntimeError(f"{name}: stray sliver pieces in the mesh (size, min corner): {slivers[:3]}")
    return name, stl_bbox(path)


RIB_OVERLAP_MAX = 10.0  # mm3: the crush ribs' designed interference with the leg tips is ~6.5


def check_fit():
    """Interference volumes in use, from the B-rep: [problem]."""
    src = load_source()
    hood, base = src.hood(), src.base()
    others = {"case": src.case(), "fan": src.fan(), **{f"keep-out '{k}'": b for k, b in src.keepouts().items()}}
    problems = []
    for name, part in (("hood", hood), ("base", base)):
        for oname, other in others.items():
            v = (part & other).volume
            if v > 1e-3:
                problems.append(f"{name} cuts into the {oname} ({v:.2f} mm3)")
    v = (hood & base).volume
    if v > RIB_OVERLAP_MAX:
        problems.append(f"hood and base overlap by {v:.1f} mm3, more than the crush ribs' {RIB_OVERLAP_MAX}")
    return problems


def export_step():
    """The parts in use position, as one STEP for the MakerWorld listing. The STEP header's
    timestamp is pinned so an unchanged model rebuilds to the same file."""
    import build123d as bd
    src = load_source()
    hood, base = src.hood(), src.base()
    hood.label, base.label = "hood", "base"
    asm = bd.Compound(children=[hood, base], label="q6a-fan-stand")
    MAKERWORLD.mkdir(parents=True, exist_ok=True)
    path = MAKERWORLD / "q6a-fan-stand.step"
    bd.export_step(asm, str(path))
    text = path.read_text()
    text = re.sub(r"(FILE_NAME\('[^']*',)'[^']*'", r"\1'2026-01-01T00:00:00'", text, count=1)
    path.write_text(text)
    return path


def stl_triangles(path: Path):
    data = path.read_bytes()
    n = struct.unpack_from("<I", data, 80)[0]
    if n == 0:
        raise RuntimeError(f"{path} is empty")
    for rec in struct.iter_unpack("<12fH", data[84:84 + 50 * n]):
        yield [(round(rec[k], 4), round(rec[k + 1], 4), round(rec[k + 2], 4)) for k in (3, 6, 9)]


def stl_bad_edges(path: Path):
    """Edges used by other than two triangles: holes, or zero-volume shells glued onto the solid.
    Triangles that collapse when the STL rounds to single precision are skipped (slicers drop them)."""
    count = {}
    for vs in stl_triangles(path):
        if len(set(vs)) < 3:
            continue
        for a, b in ((0, 1), (1, 2), (2, 0)):
            e = (vs[a], vs[b]) if vs[a] < vs[b] else (vs[b], vs[a])
            count[e] = count.get(e, 0) + 1
    return [e[0] for e, c in count.items() if c != 2]


def stl_slivers(path: Path, min_width=0.4):
    """Connected mesh pieces thinner than min_width in X or Y, or with a handful of triangles:
    geometry artefacts, never real features of this design."""
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    firsts = []
    for vs in stl_triangles(path):
        firsts.append(vs[0])
        for v in vs[1:]:
            ra, rb = find(vs[0]), find(v)
            if ra != rb:
                parent[ra] = rb
    lo, hi, count = {}, {}, {}
    for t in parent:
        r = find(t)
        l, h = lo.setdefault(r, list(t)), hi.setdefault(r, list(t))
        for a in range(3):
            l[a], h[a] = min(l[a], t[a]), max(h[a], t[a])
    for t in firsts:
        r = find(t)
        count[r] = count.get(r, 0) + 1
    bad = []
    for r in lo:
        size = [round(hi[r][a] - lo[r][a], 3) for a in range(3)]
        if min(size[0], size[1]) < min_width or count.get(r, 0) < 12:  # a plain box has 12
            bad.append((size, [round(c, 2) for c in lo[r]]))
    return bad


def stl_bbox(path: Path):
    lo, hi = [float("inf")] * 3, [float("-inf")] * 3
    for vs in stl_triangles(path):
        for v in vs:
            for a in range(3):
                lo[a], hi[a] = min(lo[a], v[a]), max(hi[a], v[a])
    return tuple(lo), tuple(hi)


# ----------------------------------------------------------------------------- Bambu

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


def flat_presets(v: Variant):
    """Write fully resolved presets (the CLI does not resolve includes on its own)."""
    pr = PRINTERS[v.printer]
    d = BUILD / "presets" / v.key
    d.mkdir(parents=True, exist_ok=True)
    machine = resolve_preset("machine", pr["machine"])
    process = resolve_preset("process", pr["process"])
    process["curr_bed_type"] = "Textured PEI Plate"
    # Every part is designed to print without supports; check_gcode fails any that slices with them
    process["enable_support"] = "0"
    fil = resolve_preset("filament", pr["filament"])
    fil["filament_colour"] = [COLOUR]
    for name, data in (("machine", machine), ("process", process), ("filament", fil)):
        (d / f"{name}.json").write_text(json.dumps(data, indent=1))
    return d / "machine.json", d / "process.json", d / "filament.json"


def layout(v: Variant, bboxes):
    """Each plate's parts in a row, centred on the bed: [(plate name, [(part, x, y)])]."""
    pr = PRINTERS[v.printer]
    W, D = pr["bed"]
    gap = 10
    plates = []
    for parts in PROJECTS[v.project]["plates"][v.printer]:
        sizes = [(p, bboxes[p][1][0] - bboxes[p][0][0], bboxes[p][1][1] - bboxes[p][0][1]) for p in parts]
        total = sum(w for _, w, _ in sizes) + gap * (len(sizes) - 1)
        if total > W - 2 * pr["margin"] or max(d for _, _, d in sizes) > D - 2 * pr["margin"]:
            raise RuntimeError(f"{v.key}: {parts} do not fit the {pr['name']} bed")
        x = (W - total) / 2
        placed = []
        for p, w, _ in sizes:
            placed.append((p, x + w / 2, D / 2))
            x += w + gap
        plates.append((PLATE_NAMES[tuple(parts)], placed))
    return plates


def run_bambu(args, cwd: Path, logname: str):
    cwd.mkdir(parents=True, exist_ok=True)
    with open(cwd / logname, "w") as fh:
        r = subprocess.run([BAMBU] + [str(a) for a in args], cwd=cwd, stdout=fh, stderr=subprocess.STDOUT)
    res = cwd / "result.json"
    info = json.loads(res.read_text()) if res.exists() else {}
    return r.returncode, info


def assemble_json(plates, bboxes):
    out = []
    for name, placed in plates:
        objs = []
        for gi, (p, cx, cy) in enumerate(placed, start=1):
            lo, hi = bboxes[p]
            objs.append({"path": str(BUILD / "stl" / f"{p}.stl"), "count": 1, "filaments": [1],
                         "assemble_index": [gi], "pos_x": [cx - (lo[0] + hi[0]) / 2],
                         "pos_y": [cy - (lo[1] + hi[1]) / 2], "pos_z": [-lo[2]]})
        out.append({"plate_name": name, "need_arrange": False, "objects": objs})
    return {"plates": out}


def set_meta(elem, key, value):
    """Set <metadata key=.. value=..> on an element (first one wins, added if missing)."""
    for m in elem.findall("metadata"):
        if m.get("key") == key:
            m.set("value", value)
            return
    elem.insert(0, ET.Element("metadata", {"key": key, "value": value}))


def name_project(src: Path, dst: Path, plates):
    """Name the objects after their parts and the plates after what is on them (the CLI drops
    plate names when it slices, so this runs on the sliced project too)."""
    with zipfile.ZipFile(src) as zin:
        files = {n: zin.read(n) for n in zin.namelist()}
    root = ET.fromstring(files["Metadata/model_settings.config"])
    for obj in root.findall("object"):
        names = [m.get("value") for pt in obj.findall("part") for m in pt.findall("metadata")
                 if m.get("key") == "name"]
        part = next((n.removesuffix("_1") for n in names if n.removesuffix("_1") in PARTS), None)
        if part is None:
            raise RuntimeError(f"unknown object with parts {names}")
        set_meta(obj, "name", f"Q6A fan stand {part}")
    for plate, (name, _) in zip(root.findall("plate"), plates):
        set_meta(plate, "plater_name", name)
    files["Metadata/model_settings.config"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode")).encode()
    tmp = dst.with_suffix(".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for n, b in files.items():
            zout.writestr(n, b)
    tmp.replace(dst)


def check_overhangs(info):
    """Bambu's slice report flags overhangs it would leave unsupported: "It seems object %s has
    floating regions / floating cantilever / large overhangs. Please re-orient the object or
    enable support generation." """
    return [f"plate {p['id']}: {p['warning_message'].strip()}" for p in info.get("sliced_plates", [])
            if any(k in (p.get("warning_message") or "").lower()
                   for k in ("floating", "cantilever", "overhang", "support generation"))]


def check_gcode(final: Path, plates):
    """Start G-code must be the real one; no slicer supports; one filament, used on every plate."""
    problems = []
    with zipfile.ZipFile(final) as z:
        info = ET.fromstring(z.read("Metadata/slice_info.config"))
        for i in range(1, len(plates) + 1):
            g = z.read(f"Metadata/plate_{i}.gcode").decode(errors="replace")
            if "M1002 gcode_claim_action" not in g:
                problems.append(f"plate {i}: Bambu start G-code missing")
            if "; FEATURE: Support" in g:
                problems.append(f"plate {i}: slicer supports (design the part to print without them)")
        for i, plate in enumerate(info.findall("plate"), start=1):
            used = sorted(int(f.get("id")) for f in plate.findall("filament") if float(f.get("used_g", 0)) > 0)
            if used != [1]:
                problems.append(f"plate {i}: filaments {used}, expected [1]")
    return problems


def build_variant(v: Variant, bboxes):
    work = BUILD / "work" / v.key
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    plates = layout(v, bboxes)
    (work / "assemble.json").write_text(json.dumps(assemble_json(plates, bboxes), indent=1))
    machine, process, fil = flat_presets(v)
    settings = f"{machine};{process}"

    rc, info = run_bambu(["--load-settings", settings, "--load-filaments", fil,
                          "--load-assemble-list", work / "assemble.json",
                          "--outputdir", work, "--export-3mf", "assembled.3mf"], work, "assemble.log")
    if rc != 0 or not (work / "assembled.3mf").exists():
        raise RuntimeError(f"{v.key}: Bambu assemble failed ({rc}) {info.get('error_string')}")
    name_project(work / "assembled.3mf", work / "project.3mf", plates)

    sliced = work / "sliced"
    rc, info = run_bambu(["--load-settings", settings, "--load-filaments", fil,
                          "--slice", "0", "--outputdir", sliced, "--export-3mf", "final.3mf",
                          work / "project.3mf"], sliced, "slice.log")
    final = sliced / "final.3mf"
    if rc != 0 or info.get("return_code") != 0 or not final.exists():
        warn = [p.get("warning_message") for p in info.get("sliced_plates", []) if p.get("warning_message")]
        raise RuntimeError(f"{v.key}: slicing failed ({rc}) {info.get('error_string')} {warn}")
    name_project(final, final, plates)
    problems = check_gcode(final, plates) + check_overhangs(info)
    if problems:
        raise RuntimeError(f"{v.key}: " + "; ".join(problems))

    out_dir = PRINT_FILES / v.printer
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(final, out_dir / f"{v.key}.3mf")
    PLATE_IMAGES.mkdir(parents=True, exist_ok=True)
    stats = []
    with zipfile.ZipFile(final) as z:
        info_xml = ET.fromstring(z.read("Metadata/slice_info.config"))
        for i, plate in enumerate(info_xml.findall("plate"), start=1):
            png = f"Metadata/plate_{i}.png"
            if png in z.namelist():
                (PLATE_IMAGES / f"{v.key}-plate-{i}.png").write_bytes(z.read(png))
            meta = {m.get("key"): m.get("value") for m in plate.findall("metadata")}
            grams = sum(float(f.get("used_g", 0)) for f in plate.findall("filament"))
            stats.append((int(meta["prediction"]), round(grams, 1)))
    return dict(key=v.key, project=v.project, printer=v.printer, printer_label=PRINTERS[v.printer]["name"],
                label=PROJECTS[v.project]["label"], file=f"{v.printer}/{v.key}.3mf",
                plates=[dict(plate=i, name=name, minutes=round(s / 60), grams=g)
                        for i, ((name, _), (s, g)) in enumerate(zip(plates, stats), start=1)])


# ----------------------------------------------------------------------------- summary

def write_summary(results):
    lines = ["# Build summary", "",
             "Generated by `tools/build.py`. Every project was sliced with the stock Bambu Studio",
             "profiles (0.20 mm Standard, Bambu PETG Basic, textured PEI plate) and checked: real",
             "printer start G-code, every part a closed solid with no stray sliver pieces, and no",
             "supports and no overhang Bambu Studio would leave unsupported.", "",
             "Times and weights are Bambu Studio's estimates; the time includes the printer's",
             "warm-up and calibration.", "",
             "| Project | Printer | Plates | Print time | Filament |", "|---|---|---|---|---|"]
    for r in results:
        mins = sum(p["minutes"] for p in r["plates"])
        grams = sum(p["grams"] for p in r["plates"])
        lines.append(f"| [`{r['file']}`](../print-files/{r['file']}) | {r['printer_label']} | {len(r['plates'])} | "
                     f"{mins // 60} h {mins % 60:02d} min | {grams:.0f} g |")
    lines += ["", "## Plates", ""]
    for r in results:
        lines += [f"### {r['file']}", "", r["label"], ""]
        for p in r["plates"]:
            lines.append(f"- Plate {p['plate']}: **{p['name']}**: {p['minutes']} min, {p['grams']:.0f} g")
        lines.append("")
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "build-summary.md").write_text("\n".join(lines))
    (DOCS / "build-summary.json").write_text(json.dumps(results, indent=1) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", action="append", default=[], help="build projects whose key matches this regex")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 4, help="parallel part exports")
    a = ap.parse_args()

    variants = [Variant(p, pr) for p in PROJECTS for pr in PRINTERS]
    variants = [v for v in variants if all(re.search(o, v.key) for o in a.only)]
    if a.list:
        for v in variants:
            print(v.key)
        return
    if not variants:
        sys.exit("no project matches")

    log("checking the fit in use")
    with cf.ProcessPoolExecutor(1) as ex:  # the kernel stays out of this process
        problems = ex.submit(check_fit).result()
    if problems:
        sys.exit("fit check failed:\n  " + "\n  ".join(problems))

    needed = sorted({p for v in variants for plate in PROJECTS[v.project]["plates"][v.printer] for p in plate})
    log(f"exporting {', '.join(needed)} with build123d ({a.jobs} jobs)")
    with cf.ProcessPoolExecutor(a.jobs) as ex:
        bboxes = dict(ex.map(export_part, needed))
    log(f"STEP: {export_step().relative_to(ROOT)}")

    # Bambu projects, one at a time: the CLI shares its data directory
    results, failed = [], []
    for v in variants:
        try:
            r = build_variant(v, bboxes)
            results.append(r)
            log(f"ok   {v.key}: " + ", ".join(f"p{p['plate']} {p['minutes']} min {p['grams']} g"
                                              for p in r["plates"]))
        except Exception as e:  # keep going, report at the end
            failed.append((v.key, str(e)))
            log(f"FAIL {v.key}: {e}")
    if results:  # merge with earlier runs so a partial rebuild keeps the full summary
        old = DOCS / "build-summary.json"
        merged = {r["key"]: r for r in (json.loads(old.read_text()) if old.exists() else [])}
        merged.update({r["key"]: r for r in results})
        order = [Variant(p, pr).key for p in PROJECTS for pr in PRINTERS]
        write_summary([merged[k] for k in order if k in merged])
    if failed:
        sys.exit(f"{len(failed)} project(s) failed")


if __name__ == "__main__":
    main()
