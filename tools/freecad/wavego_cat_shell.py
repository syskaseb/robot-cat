"""Parametric generator for the CAT enclosure, head, neck and tail.

Rebuilds every ``CAT_*`` body of ``WAVEGO_cat_mechanical.FCStd`` from the
numbers in ``PARAMS`` and from the installation envelopes in
``hardware/wavego/mechanics/components.json``.  Nothing here is hand-modelled:
running this script twice produces the same solids, so the geometry can be
reviewed as a diff instead of as a binary document.

Run headless::

    freecadcmd tools/freecad/wavego_cat_shell.py

Coordinate frame: millimetres, **-X front, -Y left, +Z up**, hip-axis centre at
X=21.  The imported WAVEGO chassis is never modified; the shell sits on its
top cover plane Z=38.52 and bolts through the eight existing 2.6 mm holes.

Design intent of this revision
------------------------------
* the trunk is a lofted rounded-rectangle skin, not a filleted box, and it is
  split into three printable segments so a module can be reached without
  taking the whole animal apart;
* the ears are cone-plus-sphere solids, so every ear tip is a real R5 dome;
* the tail is a driven, segmented chain: one servo inside the trunk, a pinned
  four-segment chain outside, two tendon channels per segment;
* the skin carries ventilation: low front intakes, flank slots beside the
  computer, and a dorsal grille above it.

This is prototype geometry.  It is not print-released: fastener lengths,
threaded inserts, tendon hardware, load paths and thermals are all unverified.
"""

import json
import math
from pathlib import Path

import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[2]
HARDWARE = ROOT / "hardware/wavego"
MECHANICS = HARDWARE / "mechanics"
LAYOUT = HARDWARE / "layout"
DOCUMENT = HARDWARE / "WAVEGO_cat_mechanical.FCStd"

V = App.Vector
REPAIRED = set()

PARAMS = {
    "wall": 2.4,
    "chassis_top": 38.52,
    "chassis_bolts": {"x": [-80, -70, 112, 122], "y": [-22.5, 22.5],
                      "clearance_d": 2.7, "boss_d": 7.4, "boss_top": 46.0},
    # Trunk skin.  Sections are (x, half_width, z_bottom, z_top, corner_radius)
    # and were sized against the component envelopes, not chosen for looks:
    # every station leaves at least one wall thickness around the reserves that
    # cross it.  The two end stations close the skin into a blunt nose and rump.
    "trunk_sections": [
        (-111.0, 26.0, 60.00, 88.0, 10.0),
        (-104.0, 42.0, 52.00, 94.0, 14.0),
        (-96.0, 60.0, 44.00, 108.0, 18.0),
        (-84.0, 68.0, 40.00, 122.0, 20.0),
        (-64.0, 72.0, 38.52, 128.0, 20.0),
        (-30.0, 77.0, 38.52, 132.0, 22.0),
        (10.0, 78.0, 38.52, 134.0, 22.0),
        (55.0, 78.0, 38.52, 134.0, 22.0),
        (100.0, 76.0, 38.52, 130.0, 22.0),
        (125.0, 70.0, 38.52, 122.0, 20.0),
        (145.0, 58.0, 38.52, 110.0, 18.0),
        (158.0, 51.0, 38.52, 94.0, 16.0),
        (166.0, 32.0, 44.00, 80.0, 10.0),
    ],
    "loft_step": 6.0,          # station spacing after monotone resampling
    "floor_plate": 2.0,
    "floor_gap": 2.0,           # leg horns reach Z=39.52; the plate clears them
    "floor_keep_out": [(-96.0, -60.0), (100.0, 134.0)],  # neck foot, tail foot
    "floor_window": (30.0, 30.0, 8.0, 36.0),  # x, y, corner r, pitch step
    "cable_ports": [(136.0, 154.0, 18.0, 32.0), (136.0, 154.0, -32.0, -18.0),
                    (-67.0, -33.0, -17.0, 17.0)],
    "trunk_split_z": 72.0,      # belt / upper shell parting plane
    "trunk_split_x": 26.0,      # front / rear upper shell parting plane
    "lap": 2.0,                 # inner overlap band thickness at both partings
    "lap_clearance": 0.8,
    "lap_blend": 6.0,           # how far the thickened collar runs past a parting
    "lap_width": 12.0,
    # Head skull, same section convention.
    "head_sections": [
        (-96.0, 34.0, 150.0, 196.0, 14.0),
        (-108.0, 41.0, 144.0, 204.0, 17.0),
        (-130.0, 44.0, 144.0, 208.0, 18.0),
        (-152.0, 44.0, 142.0, 208.0, 18.0),
        (-170.0, 42.0, 140.0, 210.0, 14.0),
        (-182.0, 41.0, 140.0, 210.0, 12.0),
        (-190.0, 37.0, 146.0, 204.0, 11.0),
    ],
    "ear": {"x": -143.0, "y": 25.0, "base_z": 192.0, "height": 42.0,
            "base_r": 17.0, "tip_r": 6.0, "thickness_scale": 0.50,
            "splay_deg": 16.0, "rake_deg": 10.0,
            "pinna_r": 11.0, "pinna_depth": 8.0},
    "face": {"x_outer": -197.0, "x_inner": -188.0,
             "camera": (18.0, 174.0, 14.0, 26.0),   # y, z, width_y, height_z
             "ir": (-22.0, 190.0, 20.0),            # y, z, diameter
             "tof": (0.0, 157.0, 16.0)},            # y, z, diameter
    "camera_carrier": {"x": -168.0, "plate_t": 4.0,
                       "pattern_y": [7.5, 28.5], "pattern_z": [174.6, 187.1],
                       "bore_d": 2.2},
    "neck": {"saddle": (-102.0, -78.0, -42.0, 42.0), "saddle_t": 8.0,
             "saddle_bolts": {"x": [-98.0, -82.0], "y": [-30.0, 30.0],
                              "clearance_d": 3.4},
             "arch": [(-86.0, 44.0, 128.0, 148.0, 8.0),
                      (-104.0, 46.0, 112.0, 143.0, 10.0),
                      (-137.0, 22.0, 100.0, 143.0, 8.0)],
             "pan_pocket": (-135.0, -99.0, -18.0, 18.0, 103.0, 143.0)},
    "tail": {
        "servo_pocket": (129.0, 165.0, -11.0, 11.0, 46.0, 86.0),
        "shaft": (137.0, 0.0, 86.0),      # vertical output axis, top of pocket
        "root": (184.0, 0.0, 92.0),       # first pin, outside the rump
        "rise_deg": 18.0,
        "segments": [(34.0, 11.0, 10.0), (32.0, 10.0, 9.0),
                     (30.0, 9.0, 8.0), (28.0, 8.0, 6.5)],
        "joint": 9.0,               # half length of the tongue/fork overlap
        "fork_half": 4.5, "tongue_half": 4.0, "cheek": 3.7,
        "pin_d": 2.2, "pin_bore_d": 2.5, "tendon_d": 1.6,
        "tendon_bore_d": 1.9, "tendon_y": 5.5,
    },
    "vents": {
        "slot_w": 3.6, "slot_r": 1.8, "depth": 13.0,
        # (x_start, x_end, z_low, z_high, pitch) on both flanks
        "flank_intake": (-58.0, 4.0, 46.0, 64.0, 9.0),
        "flank_exhaust": (44.0, 122.0, 86.0, 114.0, 9.0),
        "dorsal": {"x": (32.0, 118.0), "y": (-42.0, 42.0),
                   "d": 4.2, "pitch": 10.0},
        "speaker": {"x": (-88.0, -20.0), "z": (54.0, 74.0),
                    "d": 3.4, "pitch": 8.0, "side": -1},
    },
}


# --------------------------------------------------------------------------
# primitives
# --------------------------------------------------------------------------

def _arc(x, cy, cz, r, a0, a1):
    def point(a):
        a = math.radians(a)
        return V(x, cy + r * math.cos(a), cz + r * math.sin(a))
    return Part.Arc(point(a0), point((a0 + a1) / 2.0), point(a1)).toShape()


def section(x, y0, y1, z0, z1, r):
    """Rounded rectangle in the plane X=x, always eight edges so it lofts."""
    r = min(r, (y1 - y0) / 2.0 - 1e-3, (z1 - z0) / 2.0 - 1e-3)
    edges = [
        Part.makeLine(V(x, y0 + r, z0), V(x, y1 - r, z0)),
        _arc(x, y1 - r, z0 + r, r, -90, 0),
        Part.makeLine(V(x, y1, z0 + r), V(x, y1, z1 - r)),
        _arc(x, y1 - r, z1 - r, r, 0, 90),
        Part.makeLine(V(x, y1 - r, z1), V(x, y0 + r, z1)),
        _arc(x, y0 + r, z1 - r, r, 90, 180),
        Part.makeLine(V(x, y0, z1 - r), V(x, y0, z0 + r)),
        _arc(x, y0 + r, z0 + r, r, 180, 270),
    ]
    return Part.Wire(Part.__sortEdges__(edges))


def _monotone(xs, ys):
    """Fritsch-Carlson tangents: smooth, and it never overshoots a station.

    A plain B-spline loft dipped the belly 11 mm below the chassis plane and
    reported bounding boxes that did not match the solid, which is why the
    skin is resampled here and lofted ruled.
    """
    n = len(xs)
    d = [(ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i]) for i in range(n - 1)]
    m = [d[0]] + [(d[i - 1] + d[i]) / 2.0 for i in range(1, n - 1)] + [d[-1]]
    for i in range(n - 1):
        if abs(d[i]) < 1e-12:
            m[i] = m[i + 1] = 0.0
            continue
        a, b = m[i] / d[i], m[i + 1] / d[i]
        if a < 0:
            m[i] = 0.0
        if b < 0:
            m[i + 1] = 0.0
        s = a * a + b * b
        if s > 9.0:
            t = 3.0 / math.sqrt(s)
            m[i], m[i + 1] = t * a * d[i], t * b * d[i]

    def value(x):
        if x <= xs[0]:
            return ys[0]
        if x >= xs[-1]:
            return ys[-1]
        i = max(j for j in range(n - 1) if xs[j] <= x)
        h = xs[i + 1] - xs[i]
        t = (x - xs[i]) / h
        t2, t3 = t * t, t * t * t
        return ((2 * t3 - 3 * t2 + 1) * ys[i] + (t3 - 2 * t2 + t) * h * m[i]
                + (-2 * t3 + 3 * t2) * ys[i + 1] + (t3 - t2) * h * m[i + 1])
    return value


def resample(sections, step=None):
    step = step or PARAMS["loft_step"]
    sections = sorted(sections)
    xs = [s[0] for s in sections]
    curves = [_monotone(xs, [s[i] for s in sections]) for i in range(1, 5)]
    span = xs[-1] - xs[0]
    n = max(2, int(round(span / step)))
    return [tuple([xs[0] + span * i / n] + [c(xs[0] + span * i / n)
                                            for c in curves])
            for i in range(n + 1)]


def _loft(sections):
    return Part.makeLoft([section(x, -hw, hw, z0, z1, r)
                          for x, hw, z0, z1, r in sorted(sections)], True, True)


def skin(sections, step=None):
    return _loft(resample(sections, step))


def offset_sections(sections, offset, floor=None, inset=0.0):
    """Sections shrunk by `offset` all round, optionally shortened in X.

    `inset` matters: an inner loft spanning the same X range as the outer one
    leaves the nose and the rump open, because the two end caps cancel.
    """
    res = resample(sections)
    xs = [s[0] for s in res]
    curves = [_monotone(xs, [s[i] for s in res]) for i in range(1, 5)]
    lo, hi = xs[0] + inset, xs[-1] - inset
    out = []
    for x in sorted(set([lo] + [v for v in xs if lo < v < hi] + [hi])):
        hw, z0, z1, r = [c(x) for c in curves]
        z_low = z0 + offset if floor is None else floor
        out.append((x, max(hw - offset, 2.0), z_low,
                    max(z1 - offset, z_low + 6.0), max(r - offset, 1.0)))
    return out


def hollow(sections, wall, floor=None, inset=None):
    """Inner void of a lofted skin; `floor` opens the underside when given."""
    inset = wall if inset is None else inset
    return _loft(offset_sections(sections, wall, floor, inset))


def rprism(x0, x1, y0, y1, z0, z1, r):
    """Box with the four X-parallel edges rounded."""
    wire = section(x0, y0, y1, z0, z1, r)
    return Part.Face(wire).extrude(V(x1 - x0, 0, 0))


def capsule(length, r0, r1):
    """Tapered capsule along +X, both ends spherical: no sharp tail links."""
    body = Part.makeCone(r0, r1, length, V(0, 0, 0), V(1, 0, 0))
    return body.fuse(Part.makeSphere(r0)).fuse(
        Part.makeSphere(r1, V(length, 0, 0))).removeSplitter()


def bore(p, direction, length, diameter, back=1.0):
    start = V(*p) - V(*direction).normalize() * back
    return Part.makeCylinder(diameter / 2.0, length + 2 * back, start,
                             V(*direction))


def boss(x, y, z0, z1, outer_d, bore_d):
    stud = Part.makeCylinder(outer_d / 2.0, z1 - z0, V(x, y, z0), V(0, 0, 1))
    return stud.cut(bore(( x, y, z0 - 1), (0, 0, 1), z1 - z0 + 2, bore_d))


def interp(sections, x, index):
    """Read the skin back at any X; used to aim the ventilation cutters."""
    sections = sorted(sections)
    xs = [s[0] for s in sections]
    return _monotone(xs, [s[index] for s in sections])(x)


def tight_bounds(shape):
    """BoundBox of a lofted solid follows the poles; tessellate instead."""
    try:
        b = shape.optimalBoundingBox(True)
    except Exception:
        b = shape.BoundBox
    return [round(v, 3) for v in (b.XMin, b.YMin, b.ZMin,
                                  b.XMax, b.YMax, b.ZMax)]


def clean(shape):
    """removeSplitter throws on some thin bands; the un-merged solid is fine.

    The skull is the one part where a boolean still leaves an invalid solid -
    the ears fuse into a ruled loft and refining that throws - so an explicit
    shape fix is the last resort.  It is reported, not silent: `generate`
    records `repaired` for anything that needed it.
    """
    try:
        merged = shape.removeSplitter()
    except Exception:
        merged = shape
    if not merged.isValid():
        merged = shape
    if not merged.isValid():
        repaired = merged.copy()
        if repaired.fix(1e-6, 1e-6, 1e-6) and repaired.isValid():
            REPAIRED.add(id(repaired))
            return repaired
    return merged


def fuse_all(shapes):
    if len(shapes) == 1:
        return shapes[0]
    out = shapes[0]
    for shape in shapes[1:]:
        out = out.fuse(shape)
    return clean(out)


def cut_all(shape, cutters):
    if not cutters:
        return shape
    for cutter in cutters:
        shape = shape.cut(cutter)
    return clean(shape)


def stadium(x, z0, z1, width, y_start, depth):
    """Slot cutter with semicircular ends, driven inward along -sign(y_start)."""
    r = width / 2.0
    direction = V(0, -1 if y_start > 0 else 1, 0)
    start = V(x, y_start, 0)
    parts = [Part.makeCylinder(r, depth, start + V(0, 0, z0 + r), direction),
             Part.makeCylinder(r, depth, start + V(0, 0, z1 - r), direction)]
    body = Part.makeBox(width, depth, (z1 - z0) - width,
                        V(x - r, min(y_start, y_start + direction.y * depth),
                          z0 + r))
    return fuse_all(parts + [body])


# --------------------------------------------------------------------------
# trunk: belt + two upper segments, ventilated, with the openings the neck
# rails and the tail arm need
# --------------------------------------------------------------------------

def trunk_cutters():
    P = PARAMS
    secs = P["trunk_sections"]
    v = P["vents"]
    cutters = []

    x0, x1, z0, z1, pitch = v["flank_intake"]
    for x in _steps(x0, x1, pitch):
        for side in (1, -1):
            hw = interp(secs, x, 1)
            cutters.append(stadium(x, z0, z1, v["slot_w"],
                                   side * (hw + 6.0), v["depth"]))
    x0, x1, z0, z1, pitch = v["flank_exhaust"]
    for x in _steps(x0, x1, pitch):
        for side in (1, -1):
            hw = interp(secs, x, 1)
            cutters.append(stadium(x, z0, z1, v["slot_w"],
                                   side * (hw + 6.0), v["depth"]))
    d = v["dorsal"]
    for x in _steps(d["x"][0], d["x"][1], d["pitch"]):
        top = interp(secs, x, 3)
        for y in _steps(d["y"][0], d["y"][1], d["pitch"]):
            cutters.append(Part.makeCylinder(d["d"] / 2.0, 16.0,
                                             V(x, y, top + 6.0), V(0, 0, -1)))
    s = v["speaker"]
    for x in _steps(s["x"][0], s["x"][1], s["pitch"]):
        hw = interp(secs, x, 1)
        for z in _steps(s["z"][0], s["z"][1], s["pitch"]):
            cutters.append(Part.makeCylinder(
                s["d"] / 2.0, 14.0, V(x, s["side"] * (hw + 6.0), z),
                V(0, -s["side"], 0)))

    # tail-arm opening in the rump, and the neck saddle screws
    cutters.append(rprism(148.0, 172.0, -16.0, 16.0, 42.0, 100.0, 6.0))
    cutters.extend(saddle_bores())
    return cutters


def floor_windows():
    """Lightening and cross-flow windows in the belt floor.

    Full width is not optional - a plate that stops short of the skin is an
    island, and the fuse that would reattach it is what produced loose solids
    earlier.  So the plate spans wall to wall and is opened up instead.
    """
    P = PARAMS
    wx, wy, _r, pitch = P["floor_window"]
    bolts = P["chassis_bolts"]
    out = []
    x = -50.0
    while x + wx < 158.0:
        if not any(a - 6.0 < x < b + 6.0 or a - 6.0 < x + wx < b + 6.0
                   for a, b in P["floor_keep_out"]) \
                and not any(x - 8.0 < bx < x + wx + 8.0 for bx in bolts["x"]):
            for cy in (-38.0, 0.0, 38.0):
                out.append((x, x + wx, cy - wy / 2.0, cy + wy / 2.0))
        x += pitch
    return out


def _steps(a, b, pitch):
    n = int(round((b - a) / pitch))
    if n <= 0:
        return [(a + b) / 2.0]
    span = (b - a) - n * pitch
    return [a + span / 2.0 + i * pitch for i in range(n + 1)]


def build_trunk():
    """Belt plus two upper segments.

    Every part is one `region minus cavity` expression rather than a fusion of
    bands: fusing solids that only share a face leaves OCC with a compound of
    loose pieces, which is not a printable part.  The locating collars come out
    of the cavity instead - each parting is a thickened collar on one side and
    a thin tongue that reaches into the neighbour with `lap_clearance` of slop.
    """
    P = PARAMS
    secs = P["trunk_sections"]
    wall, lap, slop = P["wall"], P["lap"], P["lap_clearance"]
    top, blend = P["chassis_top"], P["lap_blend"]
    split_z, split_x, lapw = P["trunk_split_z"], P["trunk_split_x"], P["lap_width"]

    outer = skin(secs)
    inner = hollow(secs, wall, floor=20.0)
    cavity = hollow(secs, wall, floor=top)          # closed-floor reference
    thin = hollow(secs, wall + slop, floor=top)     # tongue outer face
    core = hollow(secs, wall + lap, floor=top + lap)  # tongue inner face
    wall_band = outer.cut(thin)

    def band(shape, x0, x1, z0, z1):
        return shape.common(Part.makeBox(x1 - x0, 300, z1 - z0, V(x0, -150, z0)))

    vents = trunk_cutters()
    bolts = P["chassis_bolts"]
    plate = P["floor_plate"]

    # --- belt.  A continuous floor plate over the chassis top cover carries
    # the four existing fastener pairs; cross ribs were tried first and left
    # OCC with loose solids at every rib, which is not a printable part.
    # `inner` (open floor) sliced at the plate height, not a second loft with a
    # raised floor: a raised floor keeps its corner radius and leaves a solid
    # 34 cm3 fillet along both lower chines, disconnected from the walls.
    floor_z = top + P["floor_gap"]
    belt_cavity = [
        band(inner, -200, 200, floor_z + plate, split_z - blend),
        band(inner, -200, 200, 10.0, floor_z),
        band(core, -200, 200, split_z - blend, split_z + lapw),
        band(wall_band, -200, 200, split_z, split_z + lapw),
    ]
    for x0, x1, y0, y1 in P["cable_ports"] + floor_windows():
        belt_cavity.append(inner.common(
            rprism(x0, x1, y0, y1, floor_z - 2.0, floor_z + plate + 2.0, 5.0)))
    belt = outer.common(Part.makeBox(400, 300, split_z + lapw - top,
                                     V(-200, -150, top)))
    belt = belt.cut(Part.makeCompound(belt_cavity))
    belt = cut_all(belt, vents + [
        bore((x, y, top - 1), (0, 0, 1), 14.0, bolts["clearance_d"])
        for x in bolts["x"] for y in bolts["y"]])

    upper = outer.common(Part.makeBox(400, 300, 300, V(-200, -150, split_z)))
    ahead = Part.makeBox(split_x + 200, 300, 300, V(-200, -150, split_z))

    front = upper.common(ahead).cut(inner)
    # --- rear: mirror of the belt joint, this time about the X parting
    rear_region = upper.cut(Part.makeBox(split_x - lapw + 200, 300, 300,
                                         V(-200, -150, split_z)))
    rear_cavity = [inner.common(Part.makeBox(400, 300, 300,
                                             V(split_x + blend, -150, split_z))),
                   core.common(Part.makeBox(blend + lapw, 300, 300,
                                            V(split_x - lapw, -150, split_z))),
                   wall_band.common(Part.makeBox(lapw, 300, 300,
                                                 V(split_x - lapw, -150, split_z))),
                   Part.makeBox(lapw + 1.0, 300, split_z + lapw + 1.0 - split_z,
                                V(split_x - lapw, -150, split_z))]
    rear = rear_region.cut(Part.makeCompound(rear_cavity))
    front = cut_all(front, vents)
    rear = cut_all(rear, vents)

    # shell-to-belt and front-to-rear screws
    holes = []
    for x in (-70.0, -20.0, 60.0, 130.0):
        hw = interp(secs, x, 1)
        for side in (1, -1):
            holes.append(bore((x, side * (hw + 8.0), split_z + 7.0),
                              (0, -side, 0), 18.0, 3.4))
    for z in (88.0, 114.0):
        hw = interp(secs, split_x - lapw / 2.0, 1)
        for side in (1, -1):
            holes.append(bore((split_x - lapw / 2.0, side * (hw + 8.0), z),
                              (0, -side, 0), 18.0, 3.4))
    belt = cut_all(belt, holes)
    front = cut_all(front, holes)
    rear = cut_all(rear, holes)
    return {"CAT_Base_Chassis_Tray": belt,
            "CAT_Spine_Front": front,
            "CAT_Spine_Rear": rear}


# --------------------------------------------------------------------------
# head: rounded skull, domed ears, face mask, camera carrier
# --------------------------------------------------------------------------

def ear(side):
    """Flattened cone with a spherical tip, lofted from ellipses.

    Rounded ear tips were the point of this revision, so the tip is a real
    R`tip_r` dome sampled into the loft rather than a cone that gets a fillet
    afterwards.  Scaling a cone with `transformGeometry` also works and is
    shorter, but it turns the ear into a B-spline and the head shell then
    fails `isValid()` after the boolean.
    """
    e = PARAMS["ear"]
    height, base_r, tip_r = e["height"], e["base_r"], e["tip_r"]
    straight = height - tip_r
    heights = [-18.0, -9.0, 0.0]
    heights += [straight * i / 7.0 for i in range(1, 8)]
    heights += [straight + tip_r * math.sin(math.radians(a))
                for a in (20, 40, 60, 78)]

    def radius(h):
        if h <= 0.0:
            return base_r
        if h <= straight:
            return base_r + (tip_r - base_r) * h / straight
        t = min(1.0, (h - straight) / tip_r)
        return max(0.9, tip_r * math.sqrt(max(0.0, 1.0 - t * t)))

    wires = []
    for h in heights:
        r = radius(h)
        ellipse = Part.Ellipse(App.Vector(0, 0, h), r, r * e["thickness_scale"])
        wires.append(Part.Wire(ellipse.toShape()))
    solid = Part.makeLoft(wires, True, False)

    pinna = Part.makeCone(e["pinna_r"], 1.0, height * 0.7,
                          V(0, 0, base_r * 0.4), V(0, 0, 1))
    pinna.Placement = App.Placement(
        V(0, 0, 0), App.Rotation(V(1, 0, 0), -16.0)).multiply(pinna.Placement)
    solid = solid.cut(pinna.translate(V(0, -e["pinna_depth"] * 0.5, 0)))

    rot = (App.Rotation(V(0, 1, 0), -e["rake_deg"])
           .multiply(App.Rotation(V(1, 0, 0), side * e["splay_deg"])))
    solid.Placement = App.Placement(
        V(e["x"], side * e["y"], e["base_z"]), rot).multiply(solid.Placement)
    return solid


def build_head():
    P = PARAMS
    secs = P["head_sections"]
    wall = P["wall"]
    outer = fuse_all([skin(secs), ear(1), ear(-1)])
    inner = hollow(secs, wall)
    # the skull floor is open: the head drops onto the tilt yoke from above
    inner = inner.fuse(Part.makeBox(120, 120, 24, V(-186, -44, 132)))
    head = outer.cut(inner)
    # hard floor over the neck: the pan-servo reserve tops out at Z=143
    head = head.cut(Part.makeBox(60, 140, 6, V(-146, -70, 137.5)))

    f = P["face"]
    mask_secs = []
    for x, hw, z0, z1, r in secs[-2:]:
        mask_secs.append((x, hw, z0, z1, r))
    front = secs[-1]
    nose = (f["x_outer"], front[1] * 0.88, front[2] + 9.0,
            front[3] - 9.0, front[4] * 0.88)
    mask_outer = skin([mask_secs[0], mask_secs[1], nose])
    mask = mask_outer.cut(hollow([mask_secs[0], mask_secs[1], nose], wall))
    mask = mask.cut(Part.makeBox(300, 300, 300, V(f["x_inner"], -150, 0)))
    head = head.cut(Part.makeBox(300, 300, 300, V(-300, -150, 0))
                    .common(Part.makeBox(300 + f["x_inner"], 300, 300,
                                         V(-300, -150, 0))))

    y, z, wy, hz = f["camera"]
    apertures = [rprism(f["x_outer"] - 6, f["x_inner"] + 6, y - wy / 2.0,
                        y + wy / 2.0, z, z + hz, 4.0)]
    for cy, cz, d in (f["ir"], f["tof"]):
        apertures.append(bore((f["x_outer"] - 6, cy, cz), (1, 0, 0), 20.0, d))
    mask = cut_all(mask, apertures)
    head = cut_all(head, apertures)

    # mask-to-skull screws, matching the bore probes in the check script
    mask_screws = [bore((f["x_outer"] - 4, sy, sz), (1, 0, 0), 16.0, 2.7)
                   for sy in (-30.0, 30.0) for sz in (162.0, 194.0)]
    mask = cut_all(mask, mask_screws)
    head = cut_all(head, mask_screws)

    c = P["camera_carrier"]
    plate = rprism(c["x"], c["x"] + c["plate_t"], -4.0, 37.0, 171.0, 196.0, 5.0)
    plate = plate.cut(rprism(c["x"] - 1, c["x"] + c["plate_t"] + 1,
                             10.0, 26.0, 176.0, 186.0, 3.0))
    plate = cut_all(plate, [bore((c["x"] - 2, py, pz), (1, 0, 0), 10.0,
                                 c["bore_d"])
                            for py in c["pattern_y"] for pz in c["pattern_z"]])
    # two feet tying the carrier to the skull floor
    feet = [rprism(c["x"], c["x"] + c["plate_t"], sy - 5.0, sy + 5.0,
                   146.0, 172.0, 2.0) for sy in (20.0, 31.0)]
    plate = fuse_all([plate] + feet)
    return {"CAT_Head_Shell": head, "CAT_Face_Mask": mask,
            "CAT_Camera_Carrier": plate}


# --------------------------------------------------------------------------
# neck: chassis foot, two flank rails through the crown, lofted yoke
# --------------------------------------------------------------------------

def build_neck():
    """Saddle on the crown plus a hollow arch carrying the pan servo.

    An earlier revision ran two rails down through the shell to the chassis
    bolts.  There is no room: the speaker reserve fills the chest and the leg
    fuse holders take the shoulders, so the rails had to be so far outboard
    that they left the skin entirely.  The load path is now saddle -> front
    spine -> belt -> the four front chassis screws, which is the weakest part
    of this design and the first thing to check under load.
    """
    P = PARAMS
    n = P["neck"]
    secs = P["trunk_sections"]
    x0, x1, y0, y1 = n["saddle"]
    window = rprism(x0, x1, y0, y1, 60.0, 200.0, 10.0)
    saddle = _loft(offset_sections(secs, -n["saddle_t"])).common(window)
    saddle = saddle.cut(_loft(offset_sections(secs, -0.2)))
    yoke = skin(n["arch"]).cut(hollow(n["arch"], 3.0, inset=3.0))
    frame = fuse_all([saddle, yoke])

    px0, px1, py0, py1, pz0, pz1 = n["pan_pocket"]
    frame = frame.cut(rprism(px0 - 1.0, px1 + 1.0, py0 - 1.0, py1 + 1.0,
                             pz0 - 1.0, pz1 + 20.0, 0.5))
    frame = cut_all(frame, saddle_bores())
    return {"CAT_Neck_Load_Frame": frame}


def saddle_bores():
    b = PARAMS["neck"]["saddle_bolts"]
    return [bore((x, y, 150.0), (0, 0, -1), 60.0, b["clearance_d"])
            for x in b["x"] for y in b["y"]]


# --------------------------------------------------------------------------
# tail: one servo inside the rump, a pinned four-segment chain outside, two
# antagonistic tendons anchored in the last segment
# --------------------------------------------------------------------------

def tail_placement():
    t = PARAMS["tail"]
    return App.Placement(V(*t["root"]),
                         App.Rotation(V(0, 1, 0), -t["rise_deg"]))


def tail_segment(length, r0, r1, last):
    """One link: proximal tongue, tapered barrel, distal fork.

    The barrel is a bare cone, not a capsule - a spherical cap at the
    proximal end would sit inside the neighbour's fork and foul its cheeks.
    """
    t = PARAMS["tail"]
    j, fh, th, cheek = (t["joint"], t["fork_half"], t["tongue_half"], t["cheek"])
    h0, h1 = r0 * 0.8, r1 * 0.8
    parts = [Part.makeCone(r0, r1, length - 2 * j - 2.0, V(j + 1.0, 0, 0),
                           V(1, 0, 0)),
             rprism(-j + 1.0, j + 3.0, -th, th, -h0, h0, 1.5)]
    if last:
        parts.append(Part.makeSphere(r1, V(length - j - 1.0, 0, 0)))
    else:
        for side in (1, -1):
            lo, hi = sorted((side * (fh + 0.05), side * (fh + cheek)))
            parts.append(rprism(length - j - 3.0, length + j, lo, hi,
                                -h1, h1, 1.2))
    solid = fuse_all(parts)
    cutters = [bore((0, 0, -30), (0, 0, 1), 60.0, t["pin_bore_d"])]
    if not last:
        cutters.append(bore((length, 0, -30), (0, 0, 1), 60.0, t["pin_bore_d"]))
    reach = length + j + 4.0 if not last else length * 0.55
    for side in (1, -1):
        cutters.append(bore((-j - 4.0, side * t["tendon_y"], 0), (1, 0, 0),
                            reach + j + 4.0, t["tendon_bore_d"]))
    if last:
        # the tendons stop here; a cross bore takes the knot or a crimp
        cutters.append(bore((length * 0.55, 0, -20.0), (0, 0, 1), 40.0, 3.4))
    return cut_all(solid, cutters)


def build_tail():
    P = PARAMS
    t = P["tail"]
    bolts = P["chassis_bolts"]
    sx0, sx1, sy0, sy1, sz0, sz1 = t["servo_pocket"]
    wall = P["wall"]
    floor_top = P["chassis_top"] + P["floor_gap"] + P["floor_plate"]
    foot = rprism(108.0, 132.0, -27.0, 27.0, floor_top, 48.0, 5.0)
    cradle = rprism(sx0 - wall, sx1 + wall, sy0 - wall, sy1 + wall,
                    sz0 - wall, sz1 + wall, 4.0)
    arm = rprism(148.0, 190.0, -13.0, 13.0, 74.0, 98.0, 6.0)
    mount = fuse_all([foot, cradle, arm])
    mount = mount.cut(rprism(sx0 - 0.4, sx1 + 0.4, sy0 - 0.4, sy1 + 0.4,
                             sz0 - 0.4, sz1 + 40.0, 0.5))
    mount = mount.cut(rprism(t["root"][0] - t["joint"] - 1.0,
                             t["root"][0] + t["joint"] + 6.0,
                             -t["fork_half"], t["fork_half"], 60.0, 120.0, 1.0))

    place = tail_placement()
    axis = place.Rotation.multVec(V(1, 0, 0))
    root = V(*t["root"])
    guides = [Part.makeCylinder(t["tendon_bore_d"] / 2.0, 62.0,
                                root + place.Rotation.multVec(
                                    V(0, side * t["tendon_y"], 0)) - axis * 46.0,
                                axis)
              for side in (1, -1)]
    pin = place.Rotation.multVec(V(0, 0, 1))
    mount = cut_all(mount, guides + [
        Part.makeCylinder(t["pin_bore_d"] / 2.0, 60.0, root - pin * 30.0, pin),
    ] + [bore((x, y, floor_top - 1), (0, 0, 1), 14.0,
              bolts["clearance_d"]) for x in bolts["x"][2:] for y in bolts["y"]])

    parts = {"CAT_Tail_Mount": mount}
    offset = 0.0
    for i, (length, r0, r1) in enumerate(t["segments"], start=1):
        last = i == len(t["segments"])
        seg = tail_segment(length, r0, r1, last)
        seg.Placement = place.multiply(App.Placement(V(offset, 0, 0),
                                                     App.Rotation()))
        parts["CAT_Tail_Seg_%d" % i] = seg
        offset += length
    return parts


def _start(place, x, y):
    p = place.multVec(V(x, y, 0))
    return [round(p.x, 3), round(p.y, 3), round(p.z, 3)]


def bore_probes():
    """Fastener and pin axes to sweep for blocked bores.

    Each entry says which generated parts a probe cylinder must pass through
    without hitting solid material.  It proves the voids line up; it says
    nothing about threads, screw length or tool access.
    """
    P = PARAMS
    secs = P["trunk_sections"]
    bolts = P["chassis_bolts"]
    top, split_z, split_x = (P["chassis_top"], P["trunk_split_z"],
                             P["lap_width"])
    t = P["tail"]
    place = tail_placement()
    pin_axis = tuple(place.Rotation.multVec(V(0, 0, 1)))
    tail_axis = tuple(place.Rotation.multVec(V(1, 0, 0)))
    pins, offset = [], 0.0
    for length, _r0, _r1 in t["segments"]:
        p = place.multVec(V(offset, 0, -26.0))
        pins.append([round(c, 3) for c in (p.x, p.y, p.z)])
        offset += length
    segs = ["CAT_Tail_Seg_%d" % i for i in range(1, len(t["segments"]) + 1)]
    return [
        dict(name="shell to chassis top cover",
             parts=["CAT_Base_Chassis_Tray"],
             points=[[x, y, top - 1.0] for x in bolts["x"] for y in bolts["y"]],
             axis=(0, 0, 1), length=14.0, diameter=bolts["clearance_d"]),
        dict(name="neck foot to chassis",
             parts=["CAT_Neck_Load_Frame", "CAT_Base_Chassis_Tray"],
             points=[[x, y, top - 1.0] for x in bolts["x"][:2]
                     for y in bolts["y"]],
             axis=(0, 0, 1), length=14.0, diameter=bolts["clearance_d"]),
        dict(name="tail mount to chassis",
             parts=["CAT_Tail_Mount", "CAT_Base_Chassis_Tray"],
             points=[[x, y, top - 1.0] for x in bolts["x"][2:]
                     for y in bolts["y"]],
             axis=(0, 0, 1), length=14.0, diameter=bolts["clearance_d"]),
        dict(name="upper shell to belt",
             parts=["CAT_Base_Chassis_Tray", "CAT_Spine_Front",
                    "CAT_Spine_Rear"],
             points=[[x, -120.0, split_z + 7.0]
                     for x in (-70.0, -20.0, 60.0, 130.0)],
             axis=(0, 1, 0), length=240.0, diameter=3.4),
        dict(name="front spine to rear spine",
             parts=["CAT_Spine_Front", "CAT_Spine_Rear"],
             points=[[PARAMS["trunk_split_x"] - split_x / 2.0, -120.0, z]
                     for z in (88.0, 114.0)],
             axis=(0, 1, 0), length=240.0, diameter=3.4),
        dict(name="face mask to skull",
             parts=["CAT_Face_Mask", "CAT_Head_Shell"],
             points=[[PARAMS["face"]["x_outer"] - 4.0, y, z]
                     for y in (-30.0, 30.0) for z in (162.0, 194.0)],
             axis=(1, 0, 0), length=16.0, diameter=2.7),
        dict(name="camera carrier pattern",
             parts=["CAT_Camera_Carrier"],
             points=[[PARAMS["camera_carrier"]["x"] - 2.0, y, z]
                     for y in PARAMS["camera_carrier"]["pattern_y"]
                     for z in PARAMS["camera_carrier"]["pattern_z"]],
             axis=(1, 0, 0), length=10.0,
             diameter=PARAMS["camera_carrier"]["bore_d"]),
        dict(name="tail hinge pins", parts=["CAT_Tail_Mount"] + segs,
             points=pins, axis=pin_axis, length=52.0, diameter=t["pin_d"]),
        dict(name="tail tendon route", parts=["CAT_Tail_Mount"] + segs,
             points=[_start(place, -t["joint"] - 6.0,
                            side * t["tendon_y"]) for side in (1, -1)],
             axis=tail_axis, length=120.0, diameter=t["tendon_d"]),
    ]


# --------------------------------------------------------------------------
# document assembly
# --------------------------------------------------------------------------

def component_envelopes(doc):
    """Recreate the 26 installation envelopes the study documents.

    They are reserves, not purchased-part CAD, and are what every clearance
    number in the reports is measured against.

    Coordinates come from ``mechanics/components.json``.  ``layout/components.json``
    keeps the *earlier* study's frame - the same ids, 180 degrees apart about
    the vertical through X=21 - so mixing the two silently puts the tail servo
    in the chest.  Stale or duplicated envelope objects are removed first, so
    running the generator twice cannot leave two sets behind.
    """
    data = json.loads((MECHANICS / "components.json").read_text(encoding="utf-8"))
    mapping = json.loads((LAYOUT / "object-map.json").read_text(encoding="utf-8"))
    group = (doc.getObject("ComponentEnvelopes")
             or doc.addObject("App::DocumentObjectGroup", "ComponentEnvelopes"))
    group.Label = "BOM envelopes - reserves, not printable parts"
    wanted = set(mapping.values())
    stale = [o.Name for o in doc.Objects
             if o.Name in wanted or o.Name.rstrip("0123456789") in wanted]
    for name in stale:
        doc.removeObject(name)
    for c in data["components"]:
        name = mapping[c["id"]]
        obj = doc.addObject("Part::Feature", name)
        if obj.Name != name:
            raise RuntimeError("FreeCAD renamed %s to %s" % (name, obj.Name))
        obj.Label = c["label"]
        obj.Shape = Part.makeBox(*c["size"], V(*c["min"]))
        for prop, value in (("ComponentID", c["id"]), ("Evidence", c["status"]),
                            ("Source", c["source"]), ("StudyZone", c["zone"]),
                            ("MountingNotes", c.get("note", "")),
                            ("EnvelopeSizeMM", str(c["size"]))):
            if prop not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", prop, "Layout study")
            setattr(obj, prop, value)
        group.addObject(obj)
    return group


def generate(doc=None, save=True):
    doc = doc or App.openDocument(str(DOCUMENT))
    shapes = {}
    for builder in (build_trunk, build_head, build_neck, build_tail):
        shapes.update(builder())

    group = (doc.getObject("CatMechanicalParts")
             or doc.addObject("App::DocumentObjectGroup", "CatMechanicalParts"))
    group.Label = "CAT - mechanical prototype / NOT released for printing"
    for obj in list(group.Group):
        doc.removeObject(obj.Name)
    for name, shape in sorted(shapes.items()):
        obj = doc.getObject(name)
        if obj is None:
            obj = doc.addObject("Part::Feature", name)
        obj.Label = name.replace("CAT_", "CAT ").replace("_", " ")
        obj.Shape = shape
        for prop, value in (
                ("Material", "PETG - proposed colour; slicer settings not validated"),
                ("ReleaseStatus", "PROTOTYPE: generated by tools/freecad/"
                                  "wavego_cat_shell.py; DFM not verified")):
            if prop not in obj.PropertiesList:
                obj.addProperty("App::PropertyString", prop, "Mechanical design")
            setattr(obj, prop, value)
        group.addObject(obj)
    component_envelopes(doc)
    doc.recompute()
    report = {name: {"valid": s.isValid(), "solids": len(s.Solids),
                     "repaired": id(s) in REPAIRED,
                     "volume_mm3": round(s.Volume, 2),
                     "mass_g_petg_1p27": round(s.Volume * 1.27e-3, 1),
                     "bbox": tight_bounds(s)}
              for name, s in sorted(shapes.items())}
    if save:
        doc.save()
        (MECHANICS / "generated.json").write_text(
            json.dumps({"parameters": PARAMS, "parts": report}, indent=2),
            encoding="utf-8")
    return report


if __name__ == "__main__":
    for name, info in generate().items():
        print(name, info["valid"], info["solids"], info["volume_mm3"])
