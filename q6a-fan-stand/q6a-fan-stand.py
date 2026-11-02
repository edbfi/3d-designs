"""A fan stand for a Radxa Dragon Q6A in its Radxa Armor Case 7056A: a Noctua NF-A8 80 mm fan
blows down onto the case's fins from a hood that plugs into a base the case sits in.

Parts, all in Bambu PETG Basic:
  hood      a top plate with the finger guard and four NA-AV1 mount holes, the fan hanging under
            it on Noctua's rubber mounts, on four legs; a cable duct down the leg at the header's
            pin-1 end, ending in a holster for the fan-plug-to-Dupont joint
  base      a flat frame the case sits in, sockets for the hood's legs, and two sleeves that
            hold the Wi-Fi antennas upright at the microSD end
  fit_test  samples of every fit, to print first: the case pocket, a leg tip and its socket, the
            NA-AV1 mount webs, an antenna sleeve and the bottom of the cable duct

Frame, in use: x along the board from its microSD end (the USB/Ethernet end is at x = 85), y
across it from the 40-pin header's edge (the HDMI edge is at y = 56), z up from the desk. Board
positions come from Radxa's Dragon Q6A STEP v1.21, the case from Radxa's Armor Case 7056A 2D
drawings v1.00 (dl.radxa.com); docs/design-notes.md says what was read from where.

Plain build123d: tools/build.py imports the part functions. Run it with text-to-cad's
`cad run q6a-fan-stand.py` to see the parts and the assembly in the CAD Viewer.
"""

import build123d as bd

# ----------------------------------------------------------------------------- the case
# Radxa Armor Case 7056A around the Dragon Q6A, from the drawings, case bottom at z = 0.
CASE_L, CASE_W = 85.0, 56.0      # bottom cover and board outline
CASE_R = 3.0                     # corner radius of both covers
BOTTOM_H = 4.97                  # bottom cover with its corner bosses: the PCB rests on them
PCB_T = 1.6
TOP_COVER_L = 69.29              # the top cover stops short of the USB/Ethernet block
TOP_COVER_H = 14.49              # top cover, PCB top to fin tops
PCB_TOP = BOTTOM_H + PCB_T       # 6.57
CASE_H = PCB_TOP + TOP_COVER_H   # 21.06, fin tops
FIN_Y = (6.9, 51.1)              # the fin field across the cover; the grooves run along x

# ----------------------------------------------------------------------------- the fan
# Noctua NF-A8 5V PWM: 80 x 80 x 25 mm, holes on a 71.5 mm square, rotor bore about 77 mm.
FAN = 80.0
FAN_T = 25.0
FAN_HOLES = 71.5
FAN_BORE = 77.0
FAN_HUB = 31.0                   # motor hub diameter: the guard's solid centre disc

# ----------------------------------------------------------------------------- the fit
FLOOR = 2.0                      # base floor under the case: the case stands on it
FAN_CX = TOP_COVER_L / 2         # fan centred on the top cover...
FAN_CY = sum(FIN_Y) / 2          # ...and on its fin field
FAN_GAP = 13.0                   # fin tops to the fan's underside: hub dead zone, and Dupont
                                 # housings on the header (PCB top + 16.5) with their wire bends
AV_GAP = 2.0                     # NA-AV1 rubber between the fan's frame and the plate's mount web
AV_HOLE = 4.6                    # NA-AV1 pull-through hole (fit_test tries 4.3 / 4.6 / 5.0)
AV_WEB = 1.5                     # plate thickness the NA-AV1 grips (fit_test tries 1.2 / 1.5 / 1.8)
AV_POCKET = 10.0                 # counterbore under each mount web, for the rubber shoulder

PLATE_T = 3.0                    # top plate, guard bars included
GUARD_BAR = 1.2                  # guard ring and spoke width: two 0.4 mm nozzle lines + a bit
GUARD_RINGS = (23.5, 31.0)       # ring radii between the hub disc and the bore edge (gaps ~6.3 mm)
GUARD_SPOKES = 8
FAN_CLEAR = 1.0                  # fan frame to the legs, all round (the fan swings a little on rubber)

LEG_W = 9.0                      # leg width along x
LEG_T = 4.0                      # leg thickness across y
# Leg positions along x (centres). MicroSD end: the leg's socket stays clear of the USB-C plug's
# overmould (x 5.2-17.6). USB end: beside the unused audio jack, clear of the EDL button (x 64.6-69.2).
LEG_X = (-2.0, 56.0)
SOCKET_DEPTH = 8.0               # leg tip in the base socket
SOCKET_WALL = 2.4
FIT = 0.2                        # PETG sliding clearance per side (sockets, case pocket)
RIB = 0.35                       # crush-rib height: interference 0.15 mm per side over FIT

LIP_H = 2.0                      # case pocket lip, under the bottom cover's 2.5 mm plate top
LIP_W = 2.4
RING_IN = 5.0                    # how far the floor runs in under the case's edge

# AC019 dual-band FPC antenna (Radxa: 42 x 11.9 mm), in an upright sleeve at the microSD end.
ANT_L, ANT_W, ANT_T = 42.0, 11.9, 0.6     # thickness with its 3M liner
ANT_FIT = 0.35
ANT_WALL = 1.6                   # free-standing 44 mm tall: FDM wants >= 1.6 mm
ANT_SLIT = 3.0                   # full-height slit on the case side for the lead
ANT_X = -8.5                     # sleeve centre: 8.5 mm off the case's end face
ANT_Y = (1.0, 55.0)              # beside the corners: clear of the microSD slot (y 22-33),
                                 # the power button (y 35-39) and most of the fin grooves

CABLE_D = 3.6                    # NF-A8 cable; the duct's slot is 75 % of it, so the cable snaps in
HOLSTER = (12.0, 6.8, 20.0)      # fan 4-pin plug with Dupont male pins in it: width, depth, length
WALL = 1.6

# Heights in use, from the desk.
CASE_Z = FLOOR
FAN_Z0 = CASE_Z + CASE_H + FAN_GAP          # fan underside
FAN_Z1 = FAN_Z0 + FAN_T                     # fan top
PLATE_Z0 = FAN_Z1 + AV_GAP - (PLATE_T - AV_WEB)   # plate underside (outside the mount pockets)
PLATE_Z1 = PLATE_Z0 + PLATE_T                     # plate top: the guard's face
LEG_Y = (FAN_CY - FAN / 2 - FAN_CLEAR - LEG_T,   # header side: outer face
         FAN_CY + FAN / 2 + FAN_CLEAR)           # HDMI side: inner face
LEG_Z0 = FLOOR                                   # leg tips stand on the socket floors


def box(x0, x1, y0, y1, z0, z1):
    """An axis-aligned box from its extents."""
    return bd.Pos(x0, y0, z0) * bd.Box(x1 - x0, y1 - y0, z1 - z0, align=bd.Align.MIN)


def rounded_box(x0, x1, y0, y1, z0, z1, r):
    """A box with vertical edges rounded to r."""
    sk = bd.RectangleRounded(x1 - x0, y1 - y0, r)
    return bd.Pos((x0 + x1) / 2, (y0 + y1) / 2, z0) * bd.extrude(sk, z1 - z0)


def case_outline(grow=0.0):
    """The bottom cover's 85 x 56 R3 outline, grown by `grow`, as a face at z = 0."""
    return bd.Pos(CASE_L / 2, CASE_W / 2) * bd.RectangleRounded(CASE_L + 2 * grow, CASE_W + 2 * grow,
                                                               max(CASE_R + grow, 1.0))


# ----------------------------------------------------------------------------- reference geometry

def case():
    """Envelope of the case with the board, standing in the base (not printed). Covers, PCB and
    the connectors that stand proud of them, from Radxa's drawings and STEP."""
    bottom = bd.extrude(case_outline(), BOTTOM_H)
    pcb = bd.Pos(0, 0, BOTTOM_H) * bd.extrude(case_outline(), PCB_T)
    cover = bd.Pos(TOP_COVER_L / 2, CASE_W / 2, PCB_TOP) * bd.extrude(
        bd.RectangleRounded(TOP_COVER_L, CASE_W, CASE_R), TOP_COVER_H)
    header_slot = box(6.13, 58.93, -1, 6.9, PCB_TOP, CASE_H + 1)
    cover -= header_slot
    parts = bottom + pcb + cover
    for x0, x1, y0, y1, h in [
        (7.17, 57.97, 0.15, 7.36, 9.65),      # 40-pin header J20
        (67.04, 88.29, 2.03, 18.26, 13.6),    # Ethernet
        (70.29, 87.75, 21.07, 36.74, 16.25),  # USB-A stacks
        (70.29, 87.75, 39.58, 55.25, 16.25),
    ]:
        parts += box(x0, x1, y0, y1, PCB_TOP, PCB_TOP + h)
    out = bd.Pos(0, 0, CASE_Z) * parts
    out.label, out.color = "case", "#2b2b2b"
    return out


def fan():
    """NF-A8 envelope with its bore (not printed)."""
    f = bd.Pos(FAN_CX, FAN_CY, FAN_Z0) * (
        bd.Box(FAN, FAN, FAN_T, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        - bd.Cylinder(FAN_BORE / 2, FAN_T, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
        + bd.Cylinder(FAN_HUB / 2, FAN_T, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)))
    f.label, f.color = "fan", "#c8b39a"
    return f


def keepouts():
    """Space that must stay empty, in use: plugs and their cables, fingers on buttons and cards,
    the jumpers on the header, and the air path. Name -> box."""
    p = CASE_Z + PCB_TOP
    b = CASE_Z + BOTTOM_H
    return {
        # Dupont housings on the header (16.5 above the PCB), their wires bending out sideways
        "header jumpers": box(7.17, 57.97, 0.0, 7.36, p, p + 17.0),
        "jumper wires": box(7.17, 57.97, -10.0, 7.36, p + 14.0, p + 24.0),
        "USB-C plug": box(5.2, 17.6, 56.0, 90.0, p - 2.5, p + 5.5),
        "HDMI plug": box(21.5, 42.6, 56.0, 95.0, p - 3.5, p + 9.5),
        "USB-A plugs": box(85.0, 125.0, 19.0, 57.5, p - 4.0, p + 18.5),
        "Ethernet plug": box(85.0, 125.0, 1.0, 19.5, p - 4.5, p + 15.0),
        "microSD card": box(-20.0, 0.0, 20.0, 35.0, b - 4.0, b + 0.5),
        "power button": box(-15.0, 0.0, 33.0, 41.0, p - 0.5, p + 5.0),
        "EDL button": box(63.0, 71.0, 56.0, 66.0, p - 0.5, p + 5.0),
        "J11 RTC connector": box(78.8, 85.0, 22.3, 32.3, -1.0, b),
        "antenna leads": box(-6.0, 0.0, 6.0, 33.0, b, p + 6.0),
        "plenum": box(0.0, TOP_COVER_L, 0.0, CASE_W, CASE_Z + CASE_H + 0.3, FAN_Z0),
    }


# ----------------------------------------------------------------------------- hood

def guard(t):
    """The finger guard filling the fan's bore in the top plate: a hub disc, rings and spokes."""
    r_out = FAN_BORE / 2 + 0.5
    g = bd.Cylinder(FAN_HUB / 2, t, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    for r in GUARD_RINGS:
        g += (bd.Cylinder(r + GUARD_BAR / 2, t, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
              - bd.Cylinder(r - GUARD_BAR / 2, t, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)))
    spoke_len = r_out - FAN_HUB / 2 + 1.0
    for k in range(GUARD_SPOKES):
        g += bd.Rot(0, 0, 360 / GUARD_SPOKES * (k + 0.5)) * bd.Pos(FAN_HUB / 2 - 0.5, -GUARD_BAR / 2, 0) * \
            bd.Box(spoke_len, GUARD_BAR, t, align=bd.Align.MIN)
    return g


def plate():
    """Top plate in use position: covers the fan and reaches out over the legs."""
    x0 = FAN_CX - FAN / 2
    x1 = FAN_CX + FAN / 2
    y0, y1 = LEG_Y[0], LEG_Y[1] + LEG_T
    p = rounded_box(x0, x1, y0, y1, PLATE_Z0, PLATE_Z1, 4.0)
    dx0, dx1, dy0, _, _ = duct_box()             # an ear over the cable duct, which hangs from it
    p += rounded_box(dx0, dx1 + 4.0, dy0, y0 + 4.0, PLATE_Z0, PLATE_Z1, 2.0)
    bore = bd.Pos(FAN_CX, FAN_CY, PLATE_Z0 - 1) * bd.Cylinder(
        FAN_BORE / 2 + 0.5, PLATE_T + 2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    p = p - bore + bd.Pos(FAN_CX, FAN_CY, PLATE_Z0) * guard(PLATE_T)
    for sx in (-1, 1):
        for sy in (-1, 1):
            at = bd.Pos(FAN_CX + sx * FAN_HOLES / 2, FAN_CY + sy * FAN_HOLES / 2)
            p -= at * bd.Pos(0, 0, PLATE_Z0 - 1) * bd.Cylinder(
                AV_HOLE / 2, PLATE_T + 2, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
            p -= at * bd.Pos(0, 0, PLATE_Z0 - 1) * bd.Cylinder(
                AV_POCKET / 2, PLATE_T - AV_WEB + 1, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
    return p


def leg(x_c, y0):
    """One leg from the socket floor to the plate, its tip chamfered as a lead-in."""
    l = box(x_c - LEG_W / 2, x_c + LEG_W / 2, y0, y0 + LEG_T, LEG_Z0, PLATE_Z0 + 0.5)
    tip = l.edges().group_by(bd.Axis.Z)[0]
    return bd.chamfer(tip, 0.6)


def duct_box():
    """Outer extents of the cable duct on the pin-1-end leg: x0, x1, y0, y1, z0."""
    w, d, l = HOLSTER
    xc, y1 = LEG_X[0], LEG_Y[0]
    return xc - w / 2 - WALL, xc + w / 2 + WALL, y1 - d - 2 * WALL, y1, FAN_Z0 - 2.0 - l


def duct(z_top=None):
    """A cable duct down the outer face of the pin-1-end leg, from the plate to just under the fan.
    The fan cable presses in through the slot down its front; at the bottom, the fan's plug with
    the Dupont pins in it snaps in through a window and stands on a ledge, and the jumpers leave
    under it and loop up to the header, which takes up their slack. Printed upside down, the
    walls rise from the plate's ear and the ledge bridges the bottom."""
    w, d, l = HOLSTER
    x0, x1, y0, y1, z0 = duct_box()
    xc = (x0 + x1) / 2
    z1 = PLATE_Z0 + 0.5 if z_top is None else z_top
    outer = box(x0, x1, y0, y1 + 0.5, z0, z1)
    inner = box(xc - w / 2, xc + w / 2, y0 + WALL, y1 - WALL, z0 - 1, z1 + 1)
    slot = box(xc - 0.375 * CABLE_D, xc + 0.375 * CABLE_D, y0 - 1, y0 + WALL + 0.1, z0 - 1, z1 + 1)
    window = box(xc - 5.0, xc + 5.0, y0 - 1, y0 + WALL + 0.1, z0 + 1.6, z0 + l)
    ledge = box(xc - w / 2, xc + w / 2, y0 + WALL - 0.1, y1 - WALL + 0.1, z0, z0 + 1.6)
    gap = box(xc - 3.0, xc + 3.0, y0 - 1, y1 - WALL - 1.5, z0 - 1, z0 + 2.0)
    return (outer - inner - slot - window) + ledge - gap


def hood():
    """Plate, guard, legs and cable duct, in use position."""
    h = plate()
    for x_c in LEG_X:
        for y0 in LEG_Y:
            h += leg(x_c, y0)
    h += duct()
    h.label, h.color = "hood", "#3c6e71"
    return h


# ----------------------------------------------------------------------------- base

def socket(x_c, y0):
    """A socket boss for one leg tip, with crush ribs on its long walls."""
    sx = LEG_W / 2 + FIT
    sy0, sy1 = y0 - FIT, y0 + LEG_T + FIT
    top = FLOOR + SOCKET_DEPTH
    boss = rounded_box(x_c - sx - SOCKET_WALL, x_c + sx + SOCKET_WALL, sy0 - SOCKET_WALL, sy1 + SOCKET_WALL,
                       0, top, 1.5)
    pocket = box(x_c - sx, x_c + sx, sy0, sy1, FLOOR, top + 1)
    boss -= pocket
    for k in (-1, 1):
        for y_face, s in ((sy0, 1), (sy1, -1)):
            rib = bd.Pos(x_c + k * LEG_W / 4, y_face, FLOOR) * bd.Cylinder(
                RIB, SOCKET_DEPTH, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
            boss += rib
    # a 45-degree lead-in at the mouth
    mouth = bd.Pos(x_c, (sy0 + sy1) / 2, top - 0.8) * bd.extrude(
        bd.Rectangle(2 * sx, sy1 - sy0), 0.8, taper=-45)
    return boss - mouth


def antenna_sleeve(yc):
    """An upright sleeve for one FPC antenna, slit on the case side for its lead."""
    iw, it = ANT_W + 2 * ANT_FIT, ANT_T + 2 * ANT_FIT
    h = ANT_L + 2.0
    s = box(ANT_X - it / 2 - ANT_WALL, ANT_X + it / 2 + ANT_WALL, yc - iw / 2 - ANT_WALL, yc + iw / 2 + ANT_WALL,
            0, FLOOR + h)
    s -= box(ANT_X - it / 2, ANT_X + it / 2, yc - iw / 2, yc + iw / 2, FLOOR, FLOOR + h + 1)
    s -= box(ANT_X, ANT_X + it / 2 + ANT_WALL + 1, yc - ANT_SLIT / 2, yc + ANT_SLIT / 2, FLOOR, FLOOR + h + 1)
    return s


def base():
    """Floor frame, case pocket lip, leg sockets and antenna sleeves, in use position."""
    ring_out = case_outline(FIT + LIP_W)
    ring_in = case_outline(-RING_IN)
    floor = bd.extrude(ring_out, FLOOR) - bd.Pos(0, 0, -1) * bd.extrude(ring_in, FLOOR + 2)
    lip = bd.extrude(ring_out, FLOOR + LIP_H) - bd.Pos(0, 0, -1) * bd.extrude(case_outline(FIT), FLOOR + LIP_H + 2)
    b = floor + lip
    # outriggers from the frame to the leg sockets
    for x_c in LEG_X:
        half = LEG_W / 2 + FIT + SOCKET_WALL
        b += rounded_box(x_c - half, x_c + half, LEG_Y[0] - FIT - SOCKET_WALL, 1.0, 0, FLOOR, 1.5)
        b += rounded_box(x_c - half, x_c + half, CASE_W - 1.0, LEG_Y[1] + LEG_T + FIT + SOCKET_WALL, 0, FLOOR, 1.5)
    # a tongue under the antenna sleeves
    b += rounded_box(ANT_X - 4.0, 1.0, ANT_Y[0] - 8.0, ANT_Y[1] + 8.0, 0, FLOOR, 1.5) - \
        box(ANT_X + 3.0, 2.0, ANT_Y[0] + 8.0, ANT_Y[1] - 8.0, -1, FLOOR + 1)
    for x_c in LEG_X:
        for y0 in LEG_Y:
            b -= box(x_c - LEG_W / 2 - FIT, x_c + LEG_W / 2 + FIT, y0 - FIT, y0 + LEG_T + FIT, FLOOR, 50)
            b += socket(x_c, y0)
    for yc in ANT_Y:
        b += antenna_sleeve(yc)
    # keep the microSD end open between the corners (card, power button, antenna leads), and the
    # RTC connector J11 under its notch at the USB end
    b -= box(-10.0, 0.5, 9.0, 47.0, FLOOR, 20.0)
    b -= box(76.0, 90.0, 20.5, 34.0, -1.0, 20.0)
    b.label, b.color = "base", "#3c6e71"
    return b


# ----------------------------------------------------------------------------- fit test

def marks(n, x, y, z):
    """n small dimples in a row on a top face at z: which sample is which."""
    m = None
    for k in range(n):
        d = bd.Pos(x + 2.0 * k, y, z - 0.4) * bd.Cylinder(0.5, 1.0, align=(bd.Align.CENTER, bd.Align.CENTER,
                                                                         bd.Align.MIN))
        m = d if m is None else m + d
    return m


def fit_test():
    """Samples of every fit, laid out flat in print pose, to print before the real parts:
    a frame with the case pocket (drop the case in) and, inside it, a leg tip and its socket,
    the NA-AV1 mount webs, a short antenna sleeve and the bottom of the cable duct."""
    samples = []
    sock = socket(LEG_X[0], LEG_Y[0]) + box(LEG_X[0] - 8, LEG_X[0] + 8, LEG_Y[0] - 5, LEG_Y[0] + LEG_T + 5,
                                            0, FLOOR)
    samples.append(sock)
    stub = box(-LEG_W / 2, LEG_W / 2, 0, LEG_T, FLOOR, FLOOR + 12)
    samples.append(bd.chamfer(stub.edges().group_by(bd.Axis.Z)[-1], 0.6) + box(-7, 7, -3, LEG_T + 3, 0, FLOOR))
    samples.append(antenna_sleeve(0) - box(-50, 50, -50, 50, FLOOR + 15, 100)
                   + box(ANT_X - 4, ANT_X + 4, -10, 10, 0, FLOOR))
    samples.append(duct(z_top=duct_box()[4] + HOLSTER[2] + 4.0))
    # NA-AV1 webs, (hole, web), printed like the plate: web on the bed, pocket open upwards.
    # 1-5 dimples name them in the README.
    for k, (hole, web) in enumerate([(AV_HOLE, 1.2), (AV_HOLE, AV_WEB), (AV_HOLE, 1.8),
                                     (4.3, AV_WEB), (5.0, AV_WEB)]):
        t = rounded_box(-6, 6, -9, 9, 0, PLATE_T, 1.5)
        t -= bd.Pos(0, 0, -1) * bd.Cylinder(hole / 2, PLATE_T + 2, align=(bd.Align.CENTER,) * 2 + (bd.Align.MIN,))
        t -= bd.Pos(0, 0, web) * bd.Cylinder(AV_POCKET / 2, PLATE_T, align=(bd.Align.CENTER,) * 2 + (bd.Align.MIN,))
        samples.append(t - marks(k + 1, -4.0, -7.0, PLATE_T))
    # the case pocket: a thin floor ring with the full lip, the samples in rows inside it
    ring_out = case_outline(FIT + LIP_W)
    floor = bd.extrude(ring_out, 1.2) - bd.Pos(0, 0, -1) * bd.extrude(case_outline(-RING_IN), 3)
    lip = bd.extrude(ring_out, 1.2 + LIP_H) - bd.Pos(0, 0, -1) * bd.extrude(case_outline(FIT), LIP_H + 3)
    pieces = [floor + lip]
    x, y, row, gap = RING_IN + 1.5, RING_IN + 1.5, 0.0, 2.0
    for smp in samples:
        bb = smp.bounding_box()
        w, d = bb.max.X - bb.min.X, bb.max.Y - bb.min.Y
        if x + w > CASE_L - RING_IN - 1.5:
            x, y, row = RING_IN + 1.5, y + row + gap, 0.0
        pieces.append(bd.Pos(x - bb.min.X, y - bb.min.Y, -bb.min.Z) * smp)
        x, row = x + w + gap, max(row, d)
    assert y + row <= CASE_W - RING_IN - 1.5, "fit-test samples overflow the frame"
    t = bd.Compound(children=pieces)
    t.label, t.color = "fit-test", "#3c6e71"
    return t


def assembly():
    """Base, case, fan and hood in place."""
    return bd.Compound(children=[base(), case(), fan(), hood()], label="q6a-fan-stand")


if __name__ == "__main__":
    from cad import model

    for f in (hood, base, fit_test, assembly):
        model(f(), name=f.__name__)
