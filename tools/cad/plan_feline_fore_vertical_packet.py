"""One dimension-derived fore packet, including BOTH full tails and grips.

Not a return to the rejected fore-Y stack or a series of scalar offsets.
Uses existing FHAC prototype OD3.4/R6 and minimum84.5 reference, explicitly
not manufacturer OD/bend data. Actual source geometry receives the proposal.
"""
import json
import math
import time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_candidate_collision_scene import Scene
from feline_solid_distance import distance
from receive_feline_global_case_candidates import matrix_rotation,placement
from check_feline_shared_space import tube_prefix


def fore_datum(aux_min_x,s0_max_y,floor_z):
    # Full case widthX20.25/widthY22, source51 axis vertical. Additional0.5
    # and1mm are explicit project margins, not tuned after a failed run.
    x=aux_min_x-1.25-20.25/2-.5
    y=s0_max_y+22/2+1.25+1
    z=floor_z+51/2+9+6+(1.55+2)+3.25+1
    return [x,y,z]


def packet(source,local,centre):
    rot=placement(matrix_rotation([2,0,1]),[0,0,0]).Rotation
    case=source.copy();case.Placement=A.Placement(A.Vector(*centre)-rot.multVec(source.BoundBox.Center),rot)*case.Placement
    parts={'case':(case,False)};recipes=[];own=[]
    b=A.Vector(0,1,0)
    for side in ('in','out'):
        e=local['F_HY.'+side];q=A.Vector(*centre)+rot.multVec(A.Vector(*e['local_point_mm']));d=rot.multVec(A.Vector(*e['departure_axis']))
        end=q+d*(9+6)+b*6;tip=end+b*14
        factory=tube_prefix(list(q),list(d),1.7,list(b),6,9)
        # Sleeve begins AT arc end and covers entire14mm factory after-land.
        sleeve=Part.makeCylinder(2.4,20,end,b);custom=Part.makeCylinder(1.55,26,tip-b*8,b)
        parts[side+':factory']=(factory,True);parts[side+':sleeve']=(sleeve,True);parts[side+':custom']=(custom,True)
        parts[side+':factory_full_grip_budget']=(Part.makeCylinder(3.7,9,q,d),False)
        parts[side+':custom_full_grip_budget']=(Part.makeCylinder(3.55,9,tip+b*9,b),False)
        trimmed=tube_prefix(list(q+d*2.5),list(d),1.7,list(b),6,6.5)
        own.extend((trimmed,sleeve,custom))
        recipes.append(dict(side=side,point_mm=list(q),departure_axis=list(d),bend_unit=list(b),
            first_mm=9,R_mm=6,factory_radius_mm=1.7,sleeve_radius_mm=2.4,
            sleeve_line_mm=[list(end),list(tip+b*6)],custom_line_mm=[list(tip-b*8),list(tip+b*18)],
            factory_grip_line_mm=[list(q),list(q+d*9)],custom_grip_line_mm=[list(tip+b*9),list(tip+b*18)],
            nominal_factory_blank_with3internal_mm=3+9+6*math.pi/2+14,
            full_grips_are_conservative_planning_volumes_not_printed_features=True))
    # One horizontal3mm case-retention ring, channelled rather than a filled
    # block through the case. Its structural arm/fastener is not fabricated.
    bb=case.BoundBox
    ring=Part.makeBox(bb.XLength+4,bb.YLength+4,3,A.Vector(bb.XMin-2,bb.YMin-2,centre[2]-1.5))
    channel=Part.makeBox(bb.XLength+.5,bb.YLength+.5,5,A.Vector(bb.XMin-.25,bb.YMin-.25,centre[2]-2.5))
    parts['case_retention_ring_budget']=(ring.cut(channel),False)
    assert all(s.isValid() and s.Solids for s,_ in parts.values())
    return parts,recipes,Part.makeCompound(own)


def main():
    tick=time.monotonic();dest=OUT/'n01-fore-vertical-full-packet.json';assert not dest.exists()
    scene=Scene();ref=ROOT/'hardware/reference/fhac0001zxj-2026-10-02/README.md'
    nominal=OUT/'n01-central-spine-power-plan-r4.json';p=json.loads(nominal.read_text())
    source_wire=next(r for r in p['routes'] if r['wire']=='W043')
    assert source_wire['radius_mm']==1.7 and min(r['radius_mm'] for r in source_wire['parts'] if r['kind']=='arc')==6
    contract=OUT/'n01-all-extra-interface-contract.json';extra=json.loads(contract.read_text())
    local={e['endpoint']:e for sec in extra['sections'] for e in sec['ends'] if e.get('local_point_mm') is not None}
    aux={n:s for n,s in scene.parts.items() if n.startswith('Ref_Material_AUX4092')}
    s0={n:s for n,s in scene.parts.items() if n.startswith('Ref_Material_S0_')}
    assert aux and s0,(list(aux),list(s0))
    aux_min=min(s.BoundBox.XMin for s in aux.values());s0_max=max(s.BoundBox.YMax for s in s0.values())
    centre=fore_datum(aux_min,s0_max,scene.outer.BoundBox.ZMin)
    shapes,recipes,own=packet(scene.templates['F_HY'][1],local,centre)
    pins=dict(scene.pins)
    for f in (ref,nominal,contract,Path(__file__),Path(__file__).with_name('feline_solid_distance.py'),Path(__file__).with_name('check_feline_shared_space.py')):pins[f.relative_to(ROOT).as_posix()]=sha(f)
    result=dict(status='RUNNING_FORE_VERTICAL_PACKET',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=pins,centre_mm=centre,source_axis_to_world_axis=[2,0,1],
        dimensional_allocation=dict(aux_actual_minX=aux_min,s0_actual_maxY=s0_max,actual_outer_minZ=scene.outer.BoundBox.ZMin,
            formula='AUXminX-1.25-10.125-.5;S0maxY+11+1.25+1;floor+25.5+9+6+3.55+3.25+1'),
        source84_5minimum_mm=84.5,prototype_OD_mm=3.4,prototype_R_mm=6,
        OD_and_R_not_manufacturer_data=True,unchanged_parts_or_prior_rejections_not_turned_green=True,
        recipes=recipes,receipts=[],failures=[],errors=[],roots_tools_and_three_case_mutual_allocation_OPEN=True)
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save()
    try:
        for name,(shape,wire) in shapes.items():
            failure,queries=scene.receive(shape,wire=wire)
            result['receipts'].append(dict(name=name,failure=failure,completed_queries=queries))
            if failure:result['failures'].append(dict(name=name,**failure))
            save();print(name,'CLEAR' if failure is None else failure,flush=True)
            if failure and name=='case':break
            if time.monotonic()-tick>180:raise TimeoutError('180s fore full packet gate; preserve named receipts')
        if not result['failures']:
            gap=distance(own,shapes['case'][0]);result['own_case_gap_mm']=gap
            if gap<1.25-1e-5:result['failures'].append(dict(name='own_case_trimmed_wires',gap_mm=gap,minimum_mm=1.25))
        result['status']='FORE_VERTICAL_FULL_PACKET_REJECTED' if result['failures'] else 'FORE_VERTICAL_FULL_PACKET_CLEAR_ROOTS_TOOLS_SHARED_REAR_OPEN'
    except Exception as e:result['errors'].append(repr(e));result['status']='FORE_VERTICAL_FULL_PACKET_PARTIAL'
    save();print(json.dumps({k:result[k] for k in ('status','worker_seconds','centre_mm','failures','errors')}),flush=True)


if __name__=='__main__':main()
