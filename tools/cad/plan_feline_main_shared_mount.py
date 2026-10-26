"""Constructive MAIN support and common four-lead restraint, before N03 release.

Uses the two retained translated screw stacks. OD2.1 and straight source12 are
the existing project recipe, not supplier measurements. Physical pull/fit and
production features remain gates. Do not Boolean against shared cached shapes.
"""
import FreeCAD as A
import Part


def isolated(shape):
    result = Part.Shape()
    result.importBrepFromString(shape.exportBrepToString())
    return result


def box(lo, hi):
    return Part.makeBox(*(b-a for a, b in zip(lo, hi)), A.Vector(*lo))


def build(current):
    pieces = [box([22,-65,54],[26,-48,55.5]),
              box([22,-65,54],[26,-61,93.25]),
              box([22,-52,54],[26,-48,93.25]),
              box([-7,-71,91.25],[26,-45,93.25])]
    axes = []
    for index in (0, 1):
        b = current[f'Ref_Material_MAIN_{index}_shaft_0_0'].BoundBox
        x, y = b.Center.x, b.Center.y
        axes.append((x, y))
        pieces.append(Part.makeCylinder(3,8,A.Vector(x,y,91.25)))
    support = isolated(pieces[0]).multiFuse([isolated(s) for s in pieces[1:]])
    for x, y in axes:
        support = support.cut(Part.makeCylinder(1.15,12,A.Vector(x,y,89)))
    support = support.fuse(box([5.7,-65,93.05],[14.7,-51.2,95.5]))
    for ya, yb in ((-66.6,-64.9),(-51.3,-49.6)):
        support = support.cut(box([9.05,ya,90.95],[11.95,yb,93.5]))
    support = support.removeSplitter()
    loop = box([9.25,-66.4,89.85],[11.75,-49.8,98.8]).cut(
        box([9.05,-65.2,91.05],[11.95,-51,97.6]))
    head = box([8,-49.8,94],[13,-45.5,99.3])
    nylon = loop.fuse(head).removeSplitter()
    for shape in (support, nylon):
        shape.check(True)
        assert len(shape.Solids) == 1
    return support, nylon, dict(screw_axes_mm=axes,
        selected_T18I_blank_mm=100, neutral_loop_mm=loop.Volume/3,
        head_and_trim_allowance_mm=25, nominal_lead_OD_mm=2.1,
        full_common_jacket_bed_mm=9, protected_straight_source_mm=12,
        manufacturing_release=False, physical_pass=False)
