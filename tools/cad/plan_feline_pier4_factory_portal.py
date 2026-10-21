"""Shared cable portal in the NEW PETG foundation, not in P0 or bank R47."""
import FreeCAD as A
import Part
from plan_feline_n01_shared import pipe


def construct(parent, routes, joint_mates):
    tools = {w: pipe(routes[w]['parts'], .925+1.25)
             for w in ('XP02.module','XP03.module')}
    changed = parent.cut(tools['XP02.module']).cut(tools['XP03.module'])
    assert changed.isValid() and len(changed.Solids)==1
    assert changed.cut(parent).Volume<1e-5
    b = parent.BoundBox
    core = Part.makeBox(4,4,b.ZLength,A.Vector(64,16.5,b.ZMin))
    assert core.cut(parent).Volume<1e-5 and core.cut(changed).Volume<1e-5
    joints = {}
    for n, mate in joint_mates.items():
        old, new = parent.common(mate).Volume, changed.common(mate).Volume
        if old>1e-6:
            assert abs(new-old)<1e-5 and new>0,n
            joints[n] = dict(prior_common_mm3=old,current_common_mm3=new)
    assert len(joints)==3
    return changed, dict(
        status='SHARED_PIER4_PORTAL_ONE_SOLID_PRESERVED_LOAD_JOINTS',
        routing_tool_radii_mm={w:2.175 for w in tools},
        foreign_wire_clearance_mm=1.25,
        complete_preserved_vertical_core_mm=[4,4,b.ZLength],
        preserved_structural_joints=joints,
        changed_is_subset_of_parent=True,
        unchanged_foreign_clearance_and_motion_lower_bounds_cannot_decrease=True,
        actual_load_strength_not_tested=True,
        P0_and_purchased_R47_bank_unchanged=True,
        N01_complete=False,physical_pass=False)
