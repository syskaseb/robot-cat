"""One dimension-derived fore packet, including BOTH full tails and grips.

Not a return to the rejected fore-Y stack or a series of scalar offsets.
Uses existing FHAC prototype OD3.4/R6 and minimum84.5 reference, explicitly
not manufacturer OD/bend data. Actual source geometry receives the proposal.
"""
import json
import math
import hashlib
import subprocess
import sys
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


def fore_datum(aux_min_x,s0_max_y,floor_z,tab_min_x,tab_max_z,s1_min_x):
    # The actual upright, NOT a floor plate, governs full case and lower
    # factory band. The opposite source S1 and S0 govern body-side clearance.
    x=min(aux_min_x-1.25-20.25/2-.5,s1_min_x-20.25/2-1.25,
        tab_min_x-(1.7+1.2)-1.25-.2)
    y=s0_max_y+22/2+1.25
    z=tab_max_z+1.25+51/2
    assert z-51/2-9-14-18-3.55>=floor_z+3.25
    return [x,y,z]


def upper_angle(qz,roof_z):
    # Entire custom wire reaches tip+18, not only the arc. Solve roof cone
    # continuously, then round UP to a whole-degree nominal recipe.
    a=6+1.55;b=14+18;limit=roof_z-3.25-qz-9
    amplitude=math.hypot(a,b);assert a<=limit<=amplitude
    value=math.atan2(a,b)+math.acos(limit/amplitude)
    return math.radians(math.ceil(math.degrees(value)))


def prefix(q,d,b,angle,first=9):
    if angle<1e-10:return Part.makeCylinder(1.7,first,q,d),q+d*first,d
    start=q+d*first
    mid=start+d*(6*math.sin(angle/2))+b*(6*(1-math.cos(angle/2)))
    end=start+d*(6*math.sin(angle))+b*(6*(1-math.cos(angle)))
    tangent=d*math.cos(angle)+b*math.sin(angle)
    wire=Part.Wire([Part.makeLine(q,start),Part.Arc(start,mid,end).toShape()])
    profile=Part.Wire([Part.makeCircle(1.7,q,d)])
    shape=wire.makePipeShell([profile],True,False)
    assert shape.isValid() and len(shape.Solids)==1
    return shape,end,tangent


def grip(q,d,r,custom):
    """Full9mm channelled seat, actual2.5mm band budget and6mm head budget.

    No filled circular PETG collar: factory seat on fore(-X) side, custom
    quarter-seat bodyward(+X)/below normal. Source dimensions are provisional.
    """
    x=A.Vector(1,0,0);n=x.cross(d);n.normalize()
    rotation=np.column_stack((list(x),list(-n),list(d)))
    tf=placement(rotation,list(q));outer=r+2
    annulus=Part.makeCylinder(outer,9).cut(Part.makeCylinder(r,9))
    clip=Part.makeBox(outer,outer,9) if custom else Part.makeBox(outer,2*outer,9,A.Vector(-outer,-outer,0))
    seat=annulus.common(clip);seat.Placement=tf*seat.Placement
    centre=q+d*(1.25 if custom else 4.5)
    band=Part.makeCylinder(r+1.2,2.5,centre-d*1.25,d).cut(Part.makeCylinder(r,2.5,centre-d*1.25,d))
    headnormal=-n if custom and d.z>0 else n if custom else -x
    headcentre=centre+headnormal*(r+3)
    head=Part.makeBox(6,6,6,A.Vector(-3,-3,-3));head.Placement=placement(rotation,list(headcentre))*head.Placement
    assert all(s.isValid() and s.Solids for s in (seat,band,head))
    return seat,band,head

def packet(source,local,centre,roof_z):
    assert np.allclose([source.BoundBox.XLength,source.BoundBox.YLength,source.BoundBox.ZLength],[51,20.25,22],atol=1e-5)
    rot=placement(matrix_rotation([2,0,1]),[0,0,0]).Rotation
    case=source.copy();case.Placement=A.Placement(A.Vector(*centre)-rot.multVec(source.BoundBox.Center),rot)*case.Placement
    parts={'case':(case,False)};recipes=[];own=[]
    b=A.Vector(0,1,0)
    for side in ('in','out'):
        e=local['F_HY.'+side];q=A.Vector(*centre)+rot.multVec(A.Vector(*e['local_point_mm']));d=rot.multVec(A.Vector(*e['departure_axis']))
        angle=upper_angle(q.z,roof_z) if d.z>0 else 0
        factory,end,tangent=prefix(q,d,b,angle);tip=end+tangent*14
        # Sleeve begins AT arc end and covers entire14mm factory after-land.
        sleeve=Part.makeCylinder(2.4,20,end,tangent);custom=Part.makeCylinder(1.55,26,tip-tangent*8,tangent)
        parts[side+':factory']=(factory,True);parts[side+':sleeve']=(sleeve,True);parts[side+':custom']=(custom,True)
        for kind,point,axis,radius in (('factory',q,d,1.7),('custom',tip+tangent*9,tangent,1.55)):
            for name,shape in zip(('seat','band','head'),grip(point,axis,radius,kind=='custom')):parts[side+':'+kind+'_full_grip_'+name]=(shape,False)
        trimmed,_,_=prefix(q+d*2.5,d,b,angle,6.5)
        own.extend((trimmed,sleeve,custom))
        recipes.append(dict(side=side,point_mm=list(q),departure_axis=list(d),bend_unit=list(b),
            first_mm=9,R_mm=6,bend_angle_degrees=math.degrees(angle),factory_radius_mm=1.7,sleeve_radius_mm=2.4,
            sleeve_line_mm=[list(end),list(tip+tangent*6)],custom_line_mm=[list(tip-tangent*8),list(tip+tangent*18)],
            factory_grip_line_mm=[list(q),list(q+d*9)],custom_grip_line_mm=[list(tip+tangent*9),list(tip+tangent*18)],
            nominal_factory_blank_with3internal_mm=3+9+6*angle+14,
            full_grips_are_conservative_planning_volumes_not_printed_features=True))
    # One horizontal3mm case-retention ring, channelled rather than a filled
    # block through the case. Its structural arm/fastener is not fabricated.
    bb=case.BoundBox
    ring_z=bb.ZMin+5.5
    ring=Part.makeBox(bb.XLength+4,bb.YLength+4,3,A.Vector(bb.XMin-2,bb.YMin-2,ring_z-1.5))
    channel=Part.makeBox(bb.XLength+.5,bb.YLength+.5,5,A.Vector(bb.XMin-.25,bb.YMin-.25,ring_z-2.5))
    parts['case_retention_ring_budget']=(ring.cut(channel),False)
    assert all(s.isValid() and s.Solids for s,_ in parts.values())
    return parts,recipes,Part.makeCompound(own)


def main():
    tick=time.monotonic();dest=OUT/'n01-fore-vertical-full-packet.json';previous=None
    if dest.exists():
        assert '--replace-rejected-from' in sys.argv
        commit=sys.argv[sys.argv.index('--replace-rejected-from')+1]
        raw=subprocess.run(['git','show',commit+':'+dest.relative_to(ROOT).as_posix()],cwd=ROOT,check=True,capture_output=True).stdout
        assert json.loads(raw)==json.loads(dest.read_text()) and json.loads(raw)['status']=='FORE_VERTICAL_FULL_PACKET_REJECTED'
        previous=dict(commit=commit,path=dest.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(raw).hexdigest(),reused_positive_geometry=False)
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
    tab=scene.parts['Ref_Material_P0_Part__Feature_0_0'].BoundBox
    s1=scene.parts['Ref_Material_current_S1_body_CP2_0_0'].BoundBox
    centre=fore_datum(aux_min,s0_max,scene.outer.BoundBox.ZMin,tab.XMin,tab.ZMax,s1.XMin)
    shapes,recipes,own=packet(scene.templates['F_HY'][1],local,centre,scene.outer.BoundBox.ZMax)
    pins=dict(scene.pins)
    hardware_refs=[OUT.parent/'wiring-checkpoint/pi-wire-support-plan.json',OUT.parent/'head-wiring-checkpoint/anchor-plan.json']
    for f in (ref,nominal,contract,*hardware_refs,Path(__file__),Path(__file__).with_name('feline_solid_distance.py'),Path(__file__).with_name('check_feline_shared_space.py')):pins[f.relative_to(ROOT).as_posix()]=sha(f)
    result=dict(status='RUNNING_FORE_VERTICAL_PACKET',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=pins,prior_rejected_receipt_retained_in_git=previous,centre_mm=centre,source_axis_to_world_axis=[2,0,1],
        dimensional_allocation=dict(aux_actual_minX=aux_min,s0_actual_maxY=s0_max,actual_outer_minZ=scene.outer.BoundBox.ZMin,
            upright_bounds_mm=[[tab.XMin,tab.YMin,tab.ZMin],[tab.XMax,tab.YMax,tab.ZMax]],s1_body_minX=s1.XMin,
            formula='min(AUXminX-11.875,S1minX-11.375,uprightminX-2.9-1.25-.2);S0maxY+11+1.25;uprighttop+1.25+25.5'),
        grip_budget=dict(PETG_seat_mm=2,band_width_mm=2.5,band_thickness_mm=1.2,head_cube_mm=6,nominal_not_delivered=True),
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
            for name,(shape,_) in shapes.items():
                if '_full_grip_' not in name:continue
                if name.endswith(':factory_full_grip_seat'):
                    volume=shape.common(shapes['case'][0]).Volume
                    if volume>1e-5:result['failures'].append(dict(name=name,own_case_overlap_mm3=volume))
                else:
                    gap=distance(shape,shapes['case'][0])
                    if gap<1.25-1e-5:result['failures'].append(dict(name=name,own_case_gap_mm=gap,minimum_mm=1.25))
        result['status']='FORE_VERTICAL_FULL_PACKET_REJECTED' if result['failures'] else 'FORE_VERTICAL_FULL_PACKET_CLEAR_ROOTS_TOOLS_SHARED_REAR_OPEN'
    except Exception as e:result['errors'].append(repr(e));result['status']='FORE_VERTICAL_FULL_PACKET_PARTIAL'
    save();print(json.dumps({k:result[k] for k in ('status','worker_seconds','centre_mm','failures','errors')}),flush=True)


if __name__=='__main__':main()
