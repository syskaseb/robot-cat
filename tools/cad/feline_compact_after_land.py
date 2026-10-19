"""Move the FULL existing common grip AFTER one shared30degree fan.

Same bought case/mouths/pitch/OD and9mm cap/whole tie/head. Three mm entry is
a project routing allowance, not a guaranteed manufacturer dimension. Common
R is at least EVERY source minimum; both caps and stock rotate properly.
"""
import math
import numpy as np
import FreeCAD as A
import Part
from feline_station_zone_domains import materialise
from feline_zone_station_templates import zone_build
from feline_remaining_kits import candidates,materialise as remaining_material
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


def projections(box,axis):
    return [A.Vector(x,y,z).dot(A.Vector(*axis)) for x in (box.XMin,box.XMax)
            for y in (box.YMin,box.YMax) for z in (box.ZMin,box.ZMax)]


def unit(st,choice):
    slot=choice['slot'];recipe=choice['base_recipe']
    assert recipe['family']=='FLAT' and not st['fixed_identity_pose']
    parts,kinds=materialise(st,slot,recipe);base=zone_build(st,slot,recipe['departure'],recipe['bend_mode'])
    R=max(12.4,*[p['minimum_project_R_mm'] for p in st['ports']])
    angle=math.radians(30);bend=np.array([0.,0.,1.]);wires=[]
    source=np.asarray(base['wires'][0]['point_mm']);d=np.asarray(base['wires'][0]['departure_axis'])
    axis=math.cos(angle)*d+math.sin(angle)*bend
    target=source+(3+R*math.sin(angle))*d+R*(1-math.cos(angle))*bend
    rot=A.Rotation(A.Vector(*d),A.Vector(*axis))
    pose=A.Placement(A.Vector(*target)-rot.multVec(A.Vector(*source)),rot)
    for n,s in parts.items():
        if n!='case' and not n.startswith('wire:'):
            s.Placement=pose*s.Placement
    # Whole-head/washer/nut envelope, not just wire clearance to screw top.
    # Boxes prove SUFFICIENT half-space separation only, never collision.
    groups,_=candidates();reference=next(r for r in groups['Anchor:Rear'] if r['axis_X_mm']==72)
    hardware,_=remaining_material('Anchor:Rear',reference)
    obstacle_max=max(max(projections(s.BoundBox,axis)) for s in hardware.values())
    grip_min=min(min(projections(s.BoundBox,axis)) for n,s in parts.items() if n!='case' and not n.startswith('wire:'))
    guard=max(0.,obstacle_max+1.25-grip_min)
    for n,s in parts.items():
        if n!='case' and not n.startswith('wire:'):s.translate(A.Vector(*(guard*axis)))
    for w in base['wires']:
        q=np.asarray(w['point_mm']);d=np.asarray(w['departure_axis']);radius=w['radius'];a=q+3*d
        point=lambda t:a+R*math.sin(t)*d+R*(1-math.cos(t))*bend
        end=point(angle);grip_start=end+guard*axis;tip=grip_start+9*axis
        path=Part.Wire([Part.makeLine(A.Vector(*q),A.Vector(*a)),
             Part.Arc(A.Vector(*a),A.Vector(*point(angle/2)),A.Vector(*end)).toShape(),
             Part.makeLine(A.Vector(*end),A.Vector(*tip))])
        shape=path.makePipeShell([Part.Wire([Part.makeCircle(radius,A.Vector(*q),A.Vector(*d))])],True,False)
        assert shape.isValid() and len(shape.Solids)==1
        parts['wire:'+w['endpoint']]=shape
        wires.append(dict(endpoint=w['endpoint'],wire=w['wire'],point_mm=q.tolist(),departure_axis=d.tolist(),
            radius=radius,R_mm=R,minimum_R_mm=next(p['minimum_project_R_mm'] for p in st['ports'] if p['endpoint']==w['endpoint']),
            first_mm=3,grip_start_mm=grip_start.tolist(),grip_end_mm=tip.tolist(),grip_axis=axis.tolist(),
            grip_length_mm=9,sweep_degrees=30,entry3_is_project_assumption=True))
    old_min=min(9+w['R_mm']*math.pi/2+9 for w in base['wires'])
    new_length=3+R*angle+guard+9
    assert new_length<=old_min+1e-6,'This compact prefix must not consume more than old accepted prefix budget'
    for n in list(parts):
        if kinds[n]=='project_stock_reservation':
            parts['Tie:'+n]=parts.pop(n);kinds['Tie:'+n]=kinds.pop(n)
    return dict(parts=parts,kinds=kinds,wires=wires,reused_jacket_lands=[],
                full_stock_guard_mm=guard,old_shortest_prefix_mm=old_min,new_prefix_mm=new_length,
                clearance_basis=dict(reference_rear_axis_mm=72,minimum_mm=1.25,
                    complete_hardware_and_grip_halfspace_support=True,boxes_not_collision_verdict=True,
                    source='n01-flat20-actual-clamp-kits.json',source_sha256=sha(OUT/'n01-flat20-actual-clamp-kits.json')),
                common_full9_grip_and_whole_stock_rigid_moved_after_turn=True,
                supplier_entry_fit_not_guaranteed=True,roots_and_source_length_capacity_open=True)
