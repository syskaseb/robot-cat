"""Move the existing power restraint to the same leads' long axial straight.

Planning candidate only: full remote leads/service slack remain unqualified.
Do not rebuild the scene or change bought parts to use this constructor.
"""
import FreeCAD as A
import Part
from feline_shared_pi_carrier import saddle
from feline_solid_distance import bbox_lower_bound


def construct(upper, components):
    retired = ['upper_power_beam', 'upper_power_beam:round', 'power_pad_post',
               'power_pad_post:round', 'Power2:pad']
    retained = upper.copy()
    for name in retired:
        retained = retained.cut(components[name].copy())
    removed = upper.cut(retained)
    protected = {}
    for name, source in components.items():
        if name in retired or bbox_lower_bound(source.BoundBox, removed.BoundBox) > 0:
            continue
        piece = removed.common(source.copy())
        if piece.Volume > 1e-7:
            piece.check(True)
            protected[name] = piece.Volume
            retained = retained.fuse(piece)
    # removeSplitter introduces self-intersecting vertices here; keep valid CSG.
    retained.check(True)
    assert len(retained.Solids) == 1
    # Entire unplugged boot ends at47.7+15; retain a3mm jacket neck before grip.
    start = 47.7 + 15 + 3
    pad, kit, recipe = saddle([
        ([start, 46.618109634713775, 101.6], [1, 0, 0]),
        ([start, 50.118109634713775, 101.6], [1, 0, 0])], 1.55)
    points = [A.Vector(*p) for p in [(91, 29, 106.38),
        (91, 48.3681096347, 106.38), (start+7, 48.3681096347, 106.38),
        (start+7, 48.3681096347, 104.3)]]
    rods = [Part.makeCylinder(1.5, (b-a).Length, a, b-a).fuse(Part.makeSphere(1.5, b))
            for a, b in zip(points, points[1:])]
    body = pad.multiFuse(rods).cut(kit['band']).removeSplitter()
    body.check(True)
    assert len(body.Solids) == 1
    joint = body.common(retained)
    joint.check(True)
    assert joint.Volume > 1e-6
    recipe.update(retired_components=retired, protected_shared_material_mm3=protected,
                  initial_boot_exit_X_mm=47.7, unplug_stroke_mm=15, released_neck_mm=3,
                  positive_root_joint_mm3=joint.Volume, full_remote_leads_OPEN=True,
                  selected=False, N01_complete=False, physical_pass=False)
    return {'retained_upper': retained, 'body': body, **kit}, recipe
