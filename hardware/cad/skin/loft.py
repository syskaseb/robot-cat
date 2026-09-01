#!/usr/bin/env python3
"""Generate the organic skins - body AND head - as lofted meshes.

Why this exists
---------------
The skin used to be a hull of spheres. That is cheap and always watertight,
but a convex hull cannot produce a concavity, and a cat is mostly
concavities: the tuck behind the ribcage, the hollow ahead of the shoulder,
the step where the muzzle leaves the cheeks. Every attempt with hulls landed
on a bulging loaf, because a union of convex blobs gives bumps and never
hollows.

A loft has no such ceiling. Each section names its own half-width, top and
bottom independently, and the envelope between sections is whatever the
interpolation does. The head goes further: it is the union of TWO lofts,
skull and muzzle, and the crease where they meet is exactly the step that
makes a face read as a cat. The union is a real mesh boolean (manifold), so
the result is still one watertight solid.

What comes out
--------------
Solids, not shells - shell_lib's body_form()/head_form() import them and the
OpenSCAD layer keeps doing what it did: panel splitting, eye sockets, ear
sockets, the camera bulkhead.

    body_outer.stl / body_inner.stl      outer surface / offset in by WALL
    body_groove.stl                      offset in by GROOVE - cuts the panel
                                         lines, which follow the surface
    head_outer.stl / head_inner.stl      likewise
    head_bulge.stl                       offset OUT by BULGE - trims the eye
                                         lens to an exact protrusion
    head_ring.stl                        offset in by RING - the counterbore
                                         the illuminated eye ring sits in

Run from hardware/cad:

    python3 skin/loft.py
"""

import math
import pathlib
import sys

import numpy as np
import trimesh
from scipy.interpolate import PchipInterpolator

HERE = pathlib.Path(__file__).resolve().parent

# The box the torque budget and the gait were computed on. The body skin has
# to stay inside it; this file asserts that rather than trusting a table.
BOX_L, BOX_W, BOX_H = 300.0, 111.0, 141.0

WALL = 1.8        # cosmetic wall thickness, three 0.6 extrusions
BULGE = 5.0       # how far the eye lens stands proud of the skull
RING = 2.4        # depth of the counterbore the illuminated eye ring sits in
GROOVE = 0.9      # depth of the panel lines cut into the body

# ---------------------------------------------------------------- body
# Sections are points ON THE SURFACE: x along the body (nose positive),
# half-width, top, bottom, and the superellipse exponent (2 = ellipse,
# higher = squarer flanks, which gives a panel somewhere to sit).
#
# The ends close to a near-point. A slab end leaves a flat disc for the cap
# fan, which reads as a vertical ledge in the silhouette. The width is held
# out to about |x| = 126 and dropped late: a width that starts falling from
# the waist gives a cone for a rump, and a cat keeps its haunches full.
BODY = [
    # x,     hw,   top,   bot,   n
    (-150.0,  1.2,  24.0,  20.0, 2.0),   # tail root
    (-147.0,  7.0,  31.0,   9.0, 2.0),
    (-143.0, 13.0,  37.0,   0.0, 2.1),
    (-136.0, 23.0,  44.0, -16.0, 2.2),
    (-126.0, 34.0,  48.0, -30.0, 2.4),
    (-114.0, 42.0,  51.0, -42.0, 2.5),   # rump, over the rear hips
    (-92.0,  46.5,  52.0, -51.0, 2.6),
    (-66.0,  49.5,  54.0, -58.0, 2.6),   # waist - the narrow point
    (-32.0,  52.5,  57.0, -66.0, 2.6),
    (  4.0,  54.5,  61.0, -71.0, 2.6),   # deepest part of the chest
    ( 40.0,  54.5,  63.0, -71.0, 2.6),
    ( 72.0,  53.0,  62.0, -66.0, 2.5),
    ( 96.0,  48.0,  59.0, -54.0, 2.4),   # shoulder
    ( 118.0, 39.0,  54.0, -38.0, 2.3),
    ( 132.0, 27.0,  47.0, -20.0, 2.2),
    ( 142.0, 15.0,  39.0,  -1.0, 2.1),
    ( 147.0,  7.0,  32.0,   9.0, 2.0),
    ( 150.0,  1.2,  25.0,  21.0, 2.0),   # base of the neck
]

# ---------------------------------------------------------------- head
# Local frame: origin at the head centre, +x towards the nose. The skull is
# one loft; the muzzle is a second, narrower and lower, driven deep into it.
# Their union creases where they meet - under the eyes and at the cheek line
# - and that step is what the hull-based head could never produce.
SKULL = [
    # x,    hw,   top,   bot,   n
    #
    # The face is FLAT. On the concept render the brow, eyes and muzzle sit
    # nearly in one vertical plane with the skull's depth behind them - so
    # the width is held far forward and dropped steeply, instead of tapering
    # from the cheeks in a long egg-shaped slope.
    (-48.0,  5.0,  16.0, -12.0, 2.1),   # occiput
    (-40.0, 22.0,  27.0, -25.0, 2.2),
    (-28.0, 34.0,  35.0, -33.0, 2.2),
    (-12.0, 42.0,  39.0, -37.0, 2.2),   # cranium
    (  2.0,  44.0,  40.0, -36.0, 2.2),  # cheekbones - the widest point
    ( 14.0,  41.0,  38.0, -30.0, 2.2),  # brow
    ( 26.0,  36.0,  34.0, -24.0, 2.2),
    ( 36.0,  27.0,  27.0, -14.0, 2.1),
    ( 44.0,  14.0,  17.0,  -4.0, 2.05),
    ( 48.0,   3.0,  10.0,   0.0, 2.0),
]

MUZZLE = [
    # x,    hw,   top,   bot,   n
    #
    # Short, high, and JOINED to the nose bridge: the muzzle's top line meets
    # the skull's bottom line at the front, so the bridge flows into the nose
    # instead of running parallel above it - a parallel gap there reads as an
    # open beak. The step survives at the SIDES, on the cheek line, which is
    # where a cat actually has one.
    (  6.0, 23.0,  10.0, -30.0, 2.4),
    ( 26.0, 23.0,   8.0, -31.0, 2.5),
    ( 40.0, 21.0,   6.0, -29.0, 2.4),
    ( 49.0, 15.0,   2.0, -24.0, 2.2),
    ( 52.0,  5.0,  -4.0, -17.0, 2.0),
]


def loft(sections, inset=0.0, n_rings=140, n_points=64):
    """A closed triangle mesh lofted through superelliptic sections.

    Each section is centred between its own top and bottom, NOT on z = 0.
    Measuring both halves from z = 0 silently collapses any section whose
    bottom is above zero - both ends of the body, where the tail and neck
    rise - and leaves a flat wall there that looks like a modelling artefact
    and is really a units error. That mistake has been made once already.
    """
    a = np.array(sections, dtype=float)
    xs = a[:, 0]
    fs = [PchipInterpolator(xs, a[:, i]) for i in (1, 2, 3, 4)]
    x = np.linspace(xs[0], xs[-1], n_rings)
    hw, top, bot, n = (f(x) for f in fs)

    # Shrink towards each section's own centre line, clamped so the nearly
    # closed ends cannot invert and fold the mesh inside out. A negative
    # inset grows the form instead - that is how the eye-bulge trim works.
    hw = np.maximum(hw - inset, 0.05)
    mid = (top + bot) / 2.0
    top = np.maximum(top - inset, mid + 0.05)
    bot = np.minimum(bot + inset, mid - 0.05)

    t = np.linspace(0.0, 2.0 * math.pi, n_points, endpoint=False)
    c, s = np.cos(t), np.sin(t)
    verts = [np.array([x[0], 0.0, mid[0]])]
    for i in range(n_rings):
        p = 2.0 / n[i]
        y = hw[i] * np.sign(c) * np.abs(c) ** p
        half = np.where(s >= 0.0, top[i] - mid[i], mid[i] - bot[i])
        z = mid[i] + half * np.sign(s) * np.abs(s) ** p
        verts.append(np.column_stack([np.full(n_points, x[i]), y, z]))
    verts.append(np.array([x[-1], 0.0, mid[-1]]))
    verts = np.vstack([v if v.ndim == 2 else v[None, :] for v in verts])

    faces = []
    first, last = 1, 1 + (n_rings - 1) * n_points
    for j in range(n_points):
        k = (j + 1) % n_points
        faces.append([0, first + k, first + j])
        faces.append([len(verts) - 1, last + j, last + k])
    for i in range(n_rings - 1):
        a0, b0 = 1 + i * n_points, 1 + (i + 1) * n_points
        for j in range(n_points):
            k = (j + 1) % n_points
            faces.append([a0 + j, a0 + k, b0 + k])
            faces.append([a0 + j, b0 + k, b0 + j])
    m = trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=True)
    m.fix_normals()
    return m


def head(inset):
    """Skull united with muzzle. A real boolean, so the crease where the
    muzzle steps off the cheeks survives into one watertight solid."""
    u = trimesh.boolean.union([loft(SKULL, inset), loft(MUZZLE, inset)])
    if not u.is_watertight:
        raise SystemExit("head union came out non-watertight - check overlap")
    return u


def emit(name, mesh):
    mesh.export(HERE / f"{name}.stl")
    print(f"{name}: watertight={mesh.is_watertight} "
          f"bodies={mesh.body_count} volume={mesh.volume:.0f}mm3")
    return mesh


def main():
    good = True

    outer = emit("body_outer", loft(BODY, 0.0, n_rings=160, n_points=72))
    inner = emit("body_inner", loft(BODY, WALL, n_rings=160, n_points=72))
    emit("body_groove", loft(BODY, GROOVE, n_rings=160, n_points=72))
    ext = outer.bounds[1] - outer.bounds[0]
    for name, got, limit in (("length", ext[0], BOX_L),
                             ("width", ext[1], BOX_W),
                             ("height", ext[2], BOX_H)):
        slack = limit - got
        good = good and slack >= -1e-6
        print(f"  {'OK ' if slack >= -1e-6 else 'OVER'} {name:7s} "
              f"{got:6.1f} of {limit:6.1f}  ({slack:+.1f} mm spare)")
    print(f"  body shell: {(outer.volume - inner.volume) * 1.27e-3:.0f} g")

    ho = emit("head_outer", head(0.0))
    hi = emit("head_inner", head(WALL))
    emit("head_bulge", head(-BULGE))
    emit("head_ring", head(RING))
    hext = ho.bounds[1] - ho.bounds[0]
    print(f"  head {hext[0]:.0f} x {hext[1]:.0f} x {hext[2]:.0f} mm, "
          f"shell {(ho.volume - hi.volume) * 1.27e-3:.0f} g")

    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
