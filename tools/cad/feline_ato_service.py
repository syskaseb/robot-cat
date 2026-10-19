"""Whole lateral ATO access reservation with side skin removed.

Tool dimensions below are explicit project budgets, not a bought puller's
manufacturer specification. A rectangular continuous sweep is a conservative
reservation. Its rejection is NOT proof the real ATO collides. A full clear
reservation, however, includes the complete translation and tool approach.
"""
import FreeCAD as A
import Part
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound


def reservation(name, fuse):
    b = fuse.BoundBox
    side = 1 if b.Center.y > 0 else -1
    assert '_CP2_ATO_' in name
    assert abs(b.XLength-5.1) < 1e-4
    assert abs(b.YLength-18.8) < 1e-4
    assert abs(b.ZLength-19.1) < 1e-4
    withdrawal = 25.0
    lo = A.Vector(b.XMin, b.YMin + min(0,side*withdrawal), b.ZMin)
    sweep = Part.makeBox(b.XLength, b.YLength+withdrawal, b.ZLength, lo)
    outside = fuse.copy().cut(sweep.copy())
    assert outside.isNull() or outside.isValid()
    assert outside.Volume < 1e-7
    tip = b.YMax if side > 0 else b.YMin
    # Six millimetres of engagement on the exposed plastic head, 35mm
    # exterior approach, 12mm total width and 25mm height around the fuse.
    ys = sorted((tip-side*6,tip+side*35))
    tool = Part.makeBox(12,ys[1]-ys[0],25,
                       A.Vector(b.Center.x-6,ys[0],b.Center.z-12.5))
    return dict(continuous_fuse_sweep=sweep,tool_budget=tool), dict(
        name=name,side=side,withdrawal_mm=withdrawal,
        tool_project_budget_XY_Z_mm=[12,41,25],tool_engagement_mm=6,
        supplier_tool_or_physical_fit_verified=False,
        side_panel_removed=True,no_WAGO_disconnections_required_by_sequence=True,
        actual_case_frame_preserved=True,fuse_inside_sweep_outside_mm3=outside.Volume)


def receive(world, fixed, other_parts=None):
    """Keep every blocker; no housing mate is silently deleted."""
    actual = [(n,s) for n,s in fixed.items() if '_CP2_ATO_' in n
              and n.startswith('Ref_Material_F_')]
    assert len(actual)==12
    obstacles = dict(fixed)
    for n,s in (other_parts or {}).items():
        assert n not in obstacles, 'A new proposal cannot overwrite a retained owner'
        obstacles[n]=s
    query=SolidQueries();records=[];shapes={}
    for n,s in actual:
        tools,record=reservation(n,s);record.update(pairs=[],reservation_blockers=[])
        for kind,part in tools.items():
            shapes['Service:'+n+':'+kind]=part
            for other,target in obstacles.items():
                if other==n:continue # The fuse inside its own sweep/tool is intentional.
                if bbox_lower_bound(part.BoundBox,target.BoundBox)>=1.25:continue
                p=part
                if other==world.bus['name']:
                    p=part.copy();p.Placement=world.bus['inverse']*p.Placement
                    target=world.bus['original']
                gap=query.distance(p,target)
                row=dict(reservation=kind,other=other,gap_mm=gap,required_mm=1.25)
                if (kind=='continuous_fuse_sweep' and
                        other==n.replace('_ATO_','_Housing_')):
                    # Start is the selected face mate. No permission for
                    # penetration or an exemption for any other bank part.
                    common=p.copy().common(target.copy())
                    assert common.isNull() or common.isValid()
                    row.update(required_mm=0,own_selected_housing_start_mate=True,
                               positive_common_mm3=common.Volume)
                    record['pairs'].append(row)
                    if common.Volume>1e-7:record['reservation_blockers'].append(row)
                    continue
                record['pairs'].append(row)
                if gap<1.25-1e-6:record['reservation_blockers'].append(row)
        record['all_reservations_clear']=not record['reservation_blockers']
        record['blocked_budget_is_NOT_actual_part_collision']=True
        record['physical_pass']=False
        records.append(record)
    return records,shapes
