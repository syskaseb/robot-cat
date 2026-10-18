"""Whole flat-bank/end/grip/service allocation from source-local full parts.

One architecture: twelve unchanged holder assemblies, both TE ends retained,
24mm pitch from true21.8486mm terminal span, outward ATO service. No native build.
"""
import json
import re
import time
import sys
from datetime import datetime, timezone
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT
from plan_feline_n01_shared import near


def main():
    tick=time.monotonic();reader=SavedShapes();shared_jpwm='--shared-jpwm-bay' in sys.argv
    suffix='-r2' if shared_jpwm else '';dest=OUT/('n01-compact-bank-preflight'+suffix+'.json')
    assert not dest.exists(),'Receive existing compact bank, do not repeat'
    native=OUT/'FelineInteriorMotion.FCStd';packetfile=OUT/'n01-shared-plan.json';packet=json.loads(packetfile.read_text());recipe=packet['foundation_revision4']
    assert sha(native)==packet['reference_native_sha256']
    pf=OUT/'n01-module-plan-r5.json';plan=json.loads(pf.read_text())
    lowerfile=OUT/'n01-shared-preflight-r5.json';lower=json.loads(lowerfile.read_text())
    epfile=OUT/'endpoint-current-receivers.json';ends={e['id']:e for e in json.loads(epfile.read_text())['endpoints']}
    result=dict(status='RUNNING',selected=False,physical_pass=False,native_built=False,contacts=[],grip_conflicts=[],service_conflicts=[],errors=[],pairs=0,
        changed_complete_holder_assemblies=12,purchased_types_unchanged=True,full_TE_ends_retained=True,
        full_grip_straight_mm=9,grip_wall_reservation_mm=2,ATO_withdrawal_project_mm=60,actual_tool_verified=False,
        complete_mounts=False,full_wiring=False,full_motion=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (native,packetfile,pf,lowerfile,epfile,Path(__file__))})
    def save():
        result.update(worker_seconds=round(time.monotonic()-tick,3),updated_utc=datetime.now(timezone.utc).isoformat());dest.write_text(json.dumps(result,indent=2)+'\n')
    def gate():
        if time.monotonic()-tick>240:
            result['status']='TIME_BOUNDED_PARTIAL';save();raise TimeoutError('240s compact-bank gate')
    scene={};role_of={};holder_of={};changed={};poses={};groups={g['role']:g for g in plan['groups']}
    for g in plan['groups']:
        role=g['role']
        for n in g['objects']:
            s=reader.shape(native,n)
            if role in lower['changed_complete_receiving_groups']:
                rr=A.Rotation(A.Vector(1,0,0),90) if role in lower['relative_rotations'] else A.Rotation()
                s.Placement=A.Placement(A.Vector(*lower['changed_complete_receiving_groups'][role]),rr)*s.Placement
            if shared_jpwm and role=='JPWM':
                s.translate(A.Vector(0,44,30));changed[n]=s
            scene[n]=s;role_of[n]=role
    for side,sign in (('L',1),('R',-1)):
        group=groups['BankLeft6Oprawek12Koncow' if side=='L' else 'BankRight6Oprawek12Koncow']
        old_rotation=A.Rotation(A.Vector(1,0,0),-sign*60)
        new_rotation=A.Rotation(A.Vector(1,0,0),-sign*90)*A.Rotation(A.Vector(0,0,1),90)
        relative=new_rotation*old_rotation.inverted()
        matrix=relative.toMatrix();r=np.array([[getattr(matrix,f'A{i+1}{j+1}') for j in range(3)] for i in range(3)])
        for index in range(1,7):
            key=f'{side}{index}';housing=f'Ref_Material_F_{key}_CP2_Housing_0_0'
            b=scene[housing].optimalBoundingBox();centre=A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,(b.ZMin+b.ZMax)/2)
            target=A.Vector(recipe['left_housing_centres_x_mm' if side=='L' else 'right_housing_centres_x_mm'][index-1],sign*53.5,69 if shared_jpwm else 65)
            pose=A.Placement(target-relative.multVec(centre),relative)
            poses[key]=dict(rotation_rows=r.tolist(),translation_mm=list(pose.Base),housing_centre_old_mm=list(centre),housing_centre_new_mm=list(target))
            for kind in ('Housing','IN','OUT','ATO'):
                n=f'Ref_Material_F_{key}_CP2_{kind}_0_0';s=scene[n].copy();s.Placement=pose*s.Placement
                scene[n]=s;changed[n]=s;holder_of[n]=key
    motionfile=OUT/'motion-layout.json';motion=json.loads(motionfile.read_text())
    for row in motion['inventory']:
        n=row['object']
        if n not in scene and row['kind']=='surface' and n.startswith(('Print_P0_','Ref_Material_P0_','Battery','Print_CP2_TailRiser')):
            if not n.startswith('BatteryFrameHardware'):scene[n]=reader.shape(native,n)
    for i in range(1,5):scene[f'BellyFoot{i}']=reader.shape(native,f'BellyFoot{i}')
    valid={};bounds={n:s.BoundBox for n,s in scene.items()}
    def check(an,a,bn,b,scope,category='contacts'):
        gate()
        if not near(a,b):return
        result['pairs']+=1
        if result['pairs']%20==0:save()
        try:
            for name,s in ((an,a),(bn,b)):
                if name not in valid:valid[name]=s.isValid()
                assert valid[name],'Invalid target is not clearance: '+name
            c=a.common(b);assert c.isNull() or c.isValid(),'Invalid Boolean'
            if c.Volume>1e-5:result[category].append(dict(a=an,b=bn,scope=scope,volume_mm3=c.Volume))
        except Exception as exc:result['errors'].append(dict(a=an,b=bn,scope=scope,error=str(exc)))
    result['holder_poses']=poses
    planout=OUT/('n01-compact-bank-plan'+suffix+'.json')
    planout.write_text(json.dumps(dict(status='COMPACT_BANK_NOT_SELECTED',selected=False,source_native=native.relative_to(ROOT).as_posix(),source_native_sha256=sha(native),
        base_module_plan=pf.relative_to(ROOT).as_posix(),base_module_plan_sha256=sha(pf),relative_holder_poses=poses,source_local_recipe=recipe,
        additional_relative_whole_groups={'JPWM':[0,44,30]} if shared_jpwm else {},
        stack_budget_note='Bank Z69: complete TE bottoms63.8057 above retained P0mounts61 by2.8057; JPWM centreZ80 above full bank grip top72.55 and below Pi lowest87.999; keep side access.' if shared_jpwm else '',
        physical_pass=False),indent=2)+'\n')
    save()
    for n,s in changed.items():
        for bn,b in scene.items():
            if n==bn or (n in holder_of and holder_of.get(n)==holder_of.get(bn)) or (bn in changed and bn<n):continue
            check(n,s,bn,b,'whole_compact_bank_cases')
        save();print('Bank part',n,'contacts',len(result['contacts']),flush=True)
    if result['contacts'] or result['errors']:
        result['status']='FLAT_BANK_CASES_REJECTED_NO_NATIVE_BUILD';save();return
    specfile=OUT/'prefix-allocation.json';specs=json.loads(specfile.read_text())['specifications'];grips={};result['grip_allocations']=[]
    for spec in specs:
        if not spec['role'].startswith('Bank'):continue
        role=ends[spec['id']]['role'];m=re.fullmatch(r'F_(FL|FR|RL|RR)([1-3])\.(in|out)',role);assert m,role
        code,index,kind=m.groups();side='L' if code in ('FL','RL') else 'R';number=int(index)+(3 if code in ('RL','RR') else 0);key=f'{side}{number}'
        t=poses[key];rr=np.array(t['rotation_rows']);p=rr@np.array(spec['point'])+t['translation_mm'];d=rr@np.array(spec['direction']);d/=np.linalg.norm(d)
        s=Part.makeCylinder(spec['radius']+2,9,A.Vector(*p),A.Vector(*d));grips[spec['id']]=s
        result['grip_allocations'].append(dict(id=spec['id'],holder=key,role=role,start_mm=p.tolist(),end_mm=(p+9*d).tolist(),outer_radius_mm=spec['radius']+2))
        for bn,b in scene.items():
            if holder_of.get(bn)==key and ('_IN_' in bn or '_OUT_' in bn or '_Housing_' in bn):continue
            check(spec['id'],s,bn,b,'full9mm_grip_reservation','grip_conflicts')
    assert len(grips)==24
    for i,(n,s) in enumerate(grips.items()):
        for bn,b in list(grips.items())[i+1:]:check(n,s,bn,b,'mutual_full_grip_reservations','grip_conflicts')
    save();print('Full24grips',len(result['grip_conflicts']),flush=True)
    result['ATO_service']=[]
    for key in poses:
        n=f'Ref_Material_F_{key}_CP2_ATO_0_0';s=scene[n];b=s.optimalBoundingBox();sign=1 if key[0]=='L' else -1
        # Continuous conservative sweep of the COMPLETE ATO, plus nominal tool
        # grip25x12 on its distal6mm. Outside enclosure workspace is permitted.
        low=A.Vector(b.XMin,b.YMin if sign>0 else b.YMin-60,b.ZMin)
        swept=Part.makeBox(b.XLength,b.YLength+60,b.ZLength,low)
        y0=b.YMax-6 if sign>0 else b.YMin-60
        tool=Part.makeBox(25,66,12,A.Vector(b.Center.x-12.5,y0,b.Center.z-6))
        for probe,shape in (('ATO_sweep_'+key,swept),('Tool_'+key,tool)):
            for bn,other in scene.items():
                if bn==n or (holder_of.get(bn)==key and '_Housing_' in bn):continue
                check(probe,shape,bn,other,'continuous_conservative_ATO_extraction','service_conflicts')
        result['ATO_service'].append(dict(holder=key,axis=[0,sign,0],withdrawal_mm=60,full_ATO_sweep_checked=True,nominal_tool25x12_checked=True,actual_tool_fit_verified=False))
        save()
    result['source_sha256'].update(reader.hashes)
    for p in (specfile,motionfile,planout):result['source_sha256'][p.relative_to(ROOT).as_posix()]=sha(p)
    result['status']='COMPACT_FLAT_BANK_48PARTS24GRIPS12ATO_CLEAR_MOUNTS_WHOLE_WIRING_OPEN' if not any(result[k] for k in ('contacts','grip_conflicts','service_conflicts','errors')) else 'COMPACT_BANK_SHARED_GRIP_OR_SERVICE_REJECTED'
    save();print(json.dumps({k:result[k] for k in ('status','pairs','worker_seconds')}),flush=True)


if __name__=='__main__':main()
