#!/usr/bin/env python3
"""Generate the body skin as a lofted mesh, and write it out as two STLs.

Why this exists
---------------
The skin used to be a hull of spheres. That is cheap and always watertight,
but a convex hull cannot produce a concavity, and a cat is mostly
concavities: the tuck behind the ribcage, the hollow ahead of the shoulder,
the dip where the neck leaves the chest, the belly rising towards the rump.
Every attempt with hulls landed on a bulging loaf, because a union of convex
blobs gives bumps and never hollows.

A loft has no such ceiling. Each station names its own half-width, its top
and its bottom independently, and the envelope between stations is whatever
the interpolation does - so the width can dip at the waist and the belly can
rise at the rear.

What comes out
--------------
Two solids, not a shell: `body_outer.stl` and `body_inner.stl`. shell_lib's
body_form() imports one or the other, so everything downstream - panel
splitting, hip reliefs, seam tabs - keeps working exactly as it did against
the hulls.

Run from hardware/cad:

    python3 skin/loft.py
"""

import math
import pathlib
import sys

import numpy as np
from scipy.interpolate import PchipInterpolator

HERE = pathlib.Path(__file__).resolve().parent

# The box the torque budget and the gait were computed on. The skin has to
# stay inside it; this file asserts that rather than trusting the table.
BOX_L, BOX_W, BOX_H = 300.0, 111.0, 141.0

# Sections along the spine. Unlike the old hull stations these are points ON
# THE SURFACE, which is the whole reason a loft is easier to reason about:
# a station says where the skin is, not where a sphere's centre is.
#
#   x        along the body, nose positive
#   hw       half-width, so the section is 2*hw across at z = 0
#   top      top of the section
#   bot      bottom of the section
#   n        superellipse exponent. 2 is a plain ellipse; higher is squarer.
#            The middle of the body runs near 2.6 so the flanks flatten
#            slightly, which is what gives a panel somewhere to sit.
#
# The waist is the point of the whole exercise: hw dips from 54.5 at the
# ribcage to 49 behind it, and the belly line rises from -70 to -44 over the
# same stretch. Neither is reachable with a convex hull.
SECTIONS = [
    # x,     hw,   top,   bot,   n
    #
    # The ends close to a near-point rather than to a small slab. A slab
    # leaves a flat disc for the cap fan to close, which shows up as a
    # vertical ledge in the silhouette. The last stations at each end also
    # keep the SLOPE of the top line changing gently: tripling it over the
    # final few millimetres creases the back.
    #
    # The width is held out to about |x| = 126 and then dropped quickly. A
    # width that starts falling from the waist gives a cone for a rump; a cat
    # keeps its haunches full and tucks in late.
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

N_RINGS = 160      # sections generated along the body
N_POINTS = 72      # points around each section


def superellipse(hw, top, bot, n, m=N_POINTS):
    """One closed section, spanning z = bot .. top with its widest line at
    the midpoint between them.

    The midpoint matters. An earlier version measured both halves from z = 0
    instead, on the theory that the flank seam wants to sit on the widest
    line. That silently collapsed every section whose bottom is ABOVE z = 0 -
    which is both ends of the body, where the tail and neck rise - into a
    section running from 0 up. The result was a 24mm flat wall at each end
    that looked like a modelling artefact and was really a units error.
    """
    t = np.linspace(0.0, 2.0 * math.pi, m, endpoint=False)
    c, s = np.cos(t), np.sin(t)
    p = 2.0 / n
    zc = (top + bot) / 2.0
    y = hw * np.sign(c) * np.abs(c) ** p
    half_h = np.where(s >= 0.0, top - zc, zc - bot)
    z = zc + half_h * np.sign(s) * np.abs(s) ** p
    return y, z


def resample(inset):
    """Interpolate the section table, shrunk by `inset` all round."""
    a = np.array(SECTIONS, dtype=float)
    xs = a[:, 0]
    fs = [PchipInterpolator(xs, a[:, i]) for i in (1, 2, 3, 4)]
    x = np.linspace(xs[0], xs[-1], N_RINGS)
    hw, top, bot, n = (f(x) for f in fs)
    # Shrink towards the section's own centre line. Clamped so the nearly
    # closed ends cannot invert and fold the mesh inside out.
    hw = np.maximum(hw - inset, 0.05)
    mid = (top + bot) / 2.0
    top = np.maximum(top - inset, mid + 0.05)
    bot = np.minimum(bot + inset, mid - 0.05)
    return x, hw, top, bot, n


def build(inset):
    """A closed triangle mesh of the body, shrunk by `inset`."""
    x, hw, top, bot, n = resample(inset)
    rings = []
    for i in range(N_RINGS):
        y, z = superellipse(hw[i], top[i], bot[i], n[i])
        rings.append(np.column_stack([np.full(N_POINTS, x[i]), y, z]))

    verts = [np.array([x[0], 0.0, (top[0] + bot[0]) / 2.0])]     # tail cap
    for r in rings:
        verts.extend(r)
    verts.append(np.array([x[-1], 0.0, (top[-1] + bot[-1]) / 2.0]))  # nose cap
    verts = np.array(verts)

    faces = []
    first, last = 1, 1 + (N_RINGS - 1) * N_POINTS
    for j in range(N_POINTS):
        k = (j + 1) % N_POINTS
        faces.append([0, first + k, first + j])                  # tail fan
        faces.append([len(verts) - 1, last + j, last + k])        # nose fan
    for i in range(N_RINGS - 1):
        a0, b0 = 1 + i * N_POINTS, 1 + (i + 1) * N_POINTS
        for j in range(N_POINTS):
            k = (j + 1) % N_POINTS
            faces.append([a0 + j, a0 + k, b0 + k])
            faces.append([a0 + j, b0 + k, b0 + j])
    return verts, np.array(faces)


def check(verts):
    ext = verts.max(axis=0) - verts.min(axis=0)
    ok = True
    for name, got, limit in (("length", ext[0], BOX_L),
                             ("width", ext[1], BOX_W),
                             ("height", ext[2], BOX_H)):
        slack = limit - got
        if slack < -1e-6:
            ok = False
        print(f"  {'OK ' if slack >= -1e-6 else 'OVER'} {name:7s} "
              f"{got:6.1f} of {limit:6.1f}  ({slack:+.1f} mm spare)")
    return ok


def main():
    import trimesh
    wall = 1.8
    for name, inset in (("body_outer", 0.0), ("body_inner", wall)):
        verts, faces = build(inset)
        m = trimesh.Trimesh(vertices=verts, faces=faces, process=True)
        m.fix_normals()
        out = HERE / f"{name}.stl"
        m.export(out)
        print(f"{name}: watertight={m.is_watertight} bodies={m.body_count} "
              f"volume={m.volume:.0f}mm3")
        if inset == 0.0:
            good = check(verts)
    print(f"\nskin volume = {trimesh.load(HERE / 'body_outer.stl').volume - trimesh.load(HERE / 'body_inner.stl').volume:.0f} mm3")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
