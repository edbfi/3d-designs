"""Ajrak-inspired Do Guti set. Coordinates are millimetres, with the open side at -Y."""
from math import atan2, cos, degrees, hypot, pi, sin
from pathlib import Path

import build123d as bd

INDIGO = "#283953"
MADDER = "#A24135"
WHITE = "#FAF5E8"  # one warm white spool for the flag, block print and counters
GREEN = "#01411C"
BOARD_HEIGHT = 6
INLAY_DEPTH = 0.6
MARK_MAX_SIDE = 16
MARK_CENTER = (-77, -63)
SCHOOL_MARK = Path(__file__).resolve().parent / "reference" / "school-mark.svg"

SITES = [(-73, 50), (73, 50), (-73, -39), (73, -39), (0, 3.5)]
LINKS = [(0, 1), (0, 2), (1, 3), (0, 4), (1, 4), (2, 4), (3, 4)]


def finish(shape, name, color):
    shape.label = name
    shape.color = color
    return shape


def layer(profile, z, height):
    return bd.Pos(0, 0, z) * bd.extrude(profile, amount=height, dir=(0, 0, 1))


def inlay(profile, name, color):
    return finish(layer(profile, BOARD_HEIGHT - INLAY_DEPTH, INLAY_DEPTH), name, color)


def pathwork():
    routes = []
    for start, end in LINKS:
        x, y = SITES[start]
        u, v = SITES[end]
        angle = degrees(atan2(v - y, u - x))
        midpoint = bd.Pos((u + x) / 2, (v + y) / 2)
        routes.append(midpoint * bd.Rot(0, 0, angle) * bd.Rectangle(hypot(u - x, v - y), 1.65))
    outer = [bd.Pos(x, y) * bd.Circle(12) for x, y in SITES]
    inner = [bd.Pos(x, y) * bd.Circle(10.4) for x, y in SITES]
    return routes[0].fuse(*routes[1:], *outer).cut(*inner)


def flag():
    width, height = 27, 18
    angle = atan2(height, 0.75 * width)
    dx, dy = cos(angle), sin(angle)
    center = (width / 8, 0)
    offset = (width / 2 - 0.65 * height * dx, height / 2 - 0.65 * height * dy)
    moon = bd.Pos(*center) * bd.Circle(0.30 * height) - bd.Pos(*offset) * bd.Circle(0.275 * height)
    star_center = (center[0] + 0.20 * height * dx, center[1] + 0.20 * height * dy)
    points = []
    for i in range(10):
        r = height * (0.10 if i % 2 == 0 else 0.0382)
        points.append((star_center[0] + r * cos(angle + i * pi / 5),
                       star_center[1] + r * sin(angle + i * pi / 5)))
    star = bd.Polygon(*points, align=None)
    stripe = bd.Pos(-3 * width / 8, 0) * bd.Rectangle(width / 4, height)
    green = (bd.Pos(width / 8, 0) * bd.Rectangle(3 * width / 4, height)).cut(moon, star)
    place = bd.Pos(-24, -60)
    return [inlay(place * green, "Flag field", GREEN),
            inlay(place * bd.Compound(children=[stripe, moon, star]), "Flag devices", WHITE)]


def selvedges():
    """Eight-petal flowers and lozenges flank the graph, outside all legal moves."""
    flowers, details = [], []
    petals = [(r * cos(i * pi / 8), r * sin(i * pi / 8))
              for i, r in enumerate([7, 4.1] * 8)]
    diamond = bd.Rot(0, 0, 45) * bd.Rectangle(3.8, 3.8)
    rosette = bd.Polygon(*petals) - diamond
    for x in (-102, 102):
        for y in (-52, -26, 0, 26, 52):
            flowers.append(bd.Pos(x, y) * rosette)
            details.append(bd.Pos(x, y) * bd.Rot(0, 0, 45) * bd.Rectangle(2, 2))
        for y in (-39, -13, 13, 39):
            details.append(bd.Pos(x, y) * bd.Rot(0, 0, 45) * bd.Rectangle(3.6, 3.6))
        for inset in (-8.8, 8.8):
            details.append(bd.Pos(x + inset, 0) * bd.Rectangle(0.85, 116))
    return [inlay(bd.Compound(children=flowers), "Rosettes", MADDER),
            inlay(bd.Compound(children=details), "Border details", WHITE)]


def school_mark(svg):
    """Centre the supplied filled outline by its ink bounds, preserving its holes and aspect."""
    faces = bd.import_svg(svg, align=bd.Align.CENTER)
    if not faces or any(not isinstance(face, bd.Face) for face in faces):
        raise ValueError("Use an SVG containing filled paths for the school mark")
    profile = bd.Compound(children=list(faces))
    size = profile.bounding_box().size
    profile = profile.scale(MARK_MAX_SIDE / max(size.X, size.Y))
    center = profile.bounding_box().center()
    x, y = MARK_CENTER
    return inlay(bd.Pos(x - center.X, y - center.Y) * profile, "School mark", GREEN)


def board(mark=None):
    outline = bd.Polygon((-106, -77), (106, -77), (116, -67), (116, 67),
                         (106, 77), (-106, 77), (-116, 67), (-116, -67))
    foot = finish(layer(outline, 0, 2), "Lower edge", MADDER)
    face = layer(outline, 2, BOARD_HEIGHT - 2)
    face = bd.chamfer(face.faces().sort_by(bd.Axis.Z)[-1].edges(), 0.8)
    title = bd.Pos(13, -60) * bd.Text("DO GUTI", font_size=8, font="DejaVu Serif")
    artwork = [inlay(pathwork(), "Routes and stations", WHITE), inlay(title, "Title", WHITE),
               *flag(), *selvedges()]
    if mark is not None:
        artwork.append(school_mark(mark))
    face = face.cut(*artwork)
    return [foot, finish(face, "Playing surface", INDIGO), *artwork]


def counter(single):
    # (height, radius): the first millimetre flares at 45 degrees for a support-free foot.
    sections = [(0, 9), (1, 10), (4.8, 10), (7, 8.5), (8, 6.4)]
    faces = [bd.Pos(0, 0, z) * bd.RegularPolygon(r, 8 if single else 12) for z, r in sections]
    body = bd.loft(faces, ruled=True)
    for x in ([0] if single else [-2.8, 2.8]):
        body = body - bd.Pos(x, 0, 9.5) * bd.Sphere(2.8)
    return finish(body, "One dimple" if single else "Two dimples", MADDER if single else WHITE)


def playing_set(mark=None):
    components = board(mark)
    for site, single in [(0, True), (3, True), (1, False), (4, False)]:
        x, y = SITES[site]
        components.append(counter(single).moved(bd.Location((x, y, BOARD_HEIGHT))))
    return bd.Compound(children=components, label="Do Guti")


if __name__ == "__main__":
    from cad import model

    model(playing_set(SCHOOL_MARK if SCHOOL_MARK.is_file() else None), name="Ajrak")
