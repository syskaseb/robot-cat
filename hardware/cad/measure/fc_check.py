"""Check printed parts as SOLIDS in FreeCAD, not just as meshes.

trimesh answers "is this mesh closed?". FreeCAD answers "is this a valid
solid?" - self-intersections, degenerate faces, wrong orientation and zero
volume shells all get caught by the OCC geometry checker, and none of them
are visible to a watertight test. A mesh can be watertight and still be
rejected by a slicer.

It also does the thing trimesh does badly: honest collision between two
parts, as a real boolean rather than Monte Carlo sampling.

Run it through the portable FreeCAD, from hardware/cad:

    "$FREECAD/freecadcmd.exe" measure/fc_check.py

Set FREECAD, or edit FC_DEFAULT below. With no arguments it checks every
_c_*.stl / _check_*.stl left by verify.py; pass paths to check specific ones.
"""

import glob
import os
import sys

import FreeCAD as App
import Mesh
import Part

# The mesh checks stream a percentage bar to stdout that drowns the report.
App.Console.SetStatusBar = lambda *a, **k: None
try:
    App.Base.ProgressIndicator = None
except AttributeError:
    pass

TOL = 0.1        # mm, mesh-to-solid sewing tolerance


def as_solid(path):
    """Load an STL and sew it into a solid OCC shape."""
    m = Mesh.Mesh(path)
    shape = Part.Shape()
    shape.makeShapeFromMesh(m.Topology, TOL)
    solid = Part.makeSolid(shape)
    return m, solid


def check(path):
    name = os.path.basename(path).replace(".stl", "")
    try:
        mesh, solid = as_solid(path)
    except Exception as exc:                       # noqa: BLE001
        print(f"{name:22s} FAILED TO LOAD: {exc}")
        return False

    problems = []
    if not mesh.isSolid():
        problems.append("mesh not solid")
    if mesh.hasSelfIntersections():
        # Count them. A handful usually means facets that merely touch at a
        # tangency, which slicers cope with; hundreds means the boolean
        # genuinely folded the surface through itself.
        n = len(mesh.getSelfIntersections())
        problems.append(f"self-intersecting x{n}")
    if mesh.countComponents() != 1:
        problems.append(f"{mesh.countComponents()} components")
    if not solid.isValid():
        problems.append("invalid solid")
    if solid.Volume <= 0:
        problems.append("non-positive volume")

    bb = solid.BoundBox
    verdict = "OK " if not problems else "PROBLEM"
    print(f"{name:22s} {verdict} vol={solid.Volume / 1000:8.1f}cm3 "
          f"faces={len(solid.Faces):5d} "
          f"bbox={bb.XLength:6.1f} x {bb.YLength:6.1f} x {bb.ZLength:6.1f}"
          + ("   " + ", ".join(problems) if problems else ""))
    return not problems


def collide(a_path, b_path):
    """Volume the two parts genuinely share. A real boolean, so unlike a
    sampled estimate a small overlap cannot be missed by bad luck."""
    _, a = as_solid(a_path)
    _, b = as_solid(b_path)
    common = a.common(b)
    return common.Volume if common.Solids else 0.0


def main():
    args = [a for a in sys.argv[1:] if a.endswith(".stl")]
    if not args:
        args = sorted(glob.glob("_c_*.stl") + glob.glob("_check_*.stl"))
    if not args:
        print("no STLs to check - run verify.py first, or pass paths")
        return 1
    bad = 0
    for path in args:
        if not check(path):
            bad += 1
    print(f"\n{len(args)} parts, {bad} with problems")
    return 1 if bad else 0


main()
