"""Read-only changed-interface screen for ONE analytic source/BUS plan.

Only correct saved actual material can establish a collision. Proposed
support/grip/plug boxes are classified separately as reservation overlaps.
No native documents, stock selections or historical results are overwritten.
"""
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,BASE
from plan_feline_n01_shared import pipe
from check_feline_shared_space import tube_prefix
from plan_feline_factory_links import routes

def main():
    tick=time.monotonic(); reader=SavedShapes()
    target=OUT/'n01-coupled-pi-bus-checks.json'
    assert not target.exists(),'Receive existing result; do not repeat unchanged geometry'
    paths=[OUT/n for n in ('n01-coupled-pi-bus-plan.json','n01-module-plan-r5.json',
        'n01-shared-preflight-r5.json','n01-compact-bank-plan-r2.json',
        'n01-common-backbone-preflight-r4.json','motion-layout.json')]
    candidate,plan,rear,bank,backbone,motion=[json.loads(p.read_text()) for p in paths]
    for p,h in candidate['source_sha256'].items(): assert sha(ROOT/p)==h,p
    assert all(candidate['necessary_length_gate'][k] for k in ('W043','W077','W078','exact_endpoint_match'))
    native=OUT/'FelineInteriorMotion.FCStd'
    assert sha(native)==bank['source_native_sha256']
    report=dict(status='RUNNING',selected=False,N01_complete=False,physical_pass=False,native_changed=False,
        contacts=[],reservation_overlaps=[],errors=[],exact_pairs=0,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths+[Path(__file__),native]},
        scope='Changed complete F_PI/P_SYS/MAIN/JPWM/BUS cases plus full W043/W077/W078, all24bank bends and8MTAfactory routes. Proposed support/plug/grip reservation overlaps distinguished from actual collisions. Not full80nets, tools or motion.',
        old_other_wire_routes_not_accepted=True)
    def save():
        report.update(worker_seconds=round(time.monotonic()-tick,3),updated_utc=datetime.now(timezone.utc).isoformat())
        target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def gate():
        if time.monotonic()-tick>240:
            report['status']='TIME_BOUNDED_PARTIAL_NOT_SELECTED';save();raise TimeoutError('240s cap')
    def placement(rr,t):
        m=A.Matrix()
        for i in range(3):
            for j in range(3):setattr(m,f'A{i+1}{j+1}',rr[i][j])
        return A.Placement(A.Vector(*t),A.Rotation(m))
    scene={}; roles={}; changed={}; bounds={}; valid={}; seen=set()
    def check(an,a,bn,b,scope,reservation=False):
        gate();key=tuple(sorted((an,bn)))+(scope,)
        if key in seen:return
        seen.add(key)
        if an not in bounds:bounds[an]=a.BoundBox
        if bn not in bounds:bounds[bn]=b.BoundBox
        if not bounds[an].intersect(bounds[bn]):return
        report['exact_pairs']+=1
        try:
            for n,s in ((an,a),(bn,b)):
                if n not in valid:valid[n]=s.isValid() and bool(s.Solids)
                assert valid[n], 'Invalid material is not a clearance proof: '+n
            c=a.common(b);assert c.isNull() or c.isValid(),'Invalid common'
            if c.Volume>1e-5:
                v=c.BoundBox
                row=dict(a=an,b=bn,scope=scope,volume_mm3=c.Volume,
                    witness_bounds_mm=[[v.XMin,v.YMin,v.ZMin],[v.XMax,v.YMax,v.ZMax]])
                report['reservation_overlaps' if reservation else 'contacts'].append(row)
        except Exception as exc:report['errors'].append(dict(a=an,b=bn,scope=scope,error=str(exc)))
        if report['exact_pairs']%15==0:save()
    common_delta={'JPWM':[-90,44,30],'W041_Joint':[0,15,3],'W042_Joint':[0,-15,3]}
    effective=json.loads(json.dumps(plan))
    for g in effective['groups']:
        if g['role'] in common_delta:g['translation_mm']=(np.array(g['translation_mm'])+common_delta[g['role']]).tolist()
    for g in plan['groups']:
        role=g['role']
        for n in g['objects']:
            gate();s=reader.shape(native,n)
            if role in rear['changed_complete_receiving_groups']:
                rr=rear['relative_rotations'].get(role,np.eye(3).tolist())
                s.Placement=placement(rr,rear['changed_complete_receiving_groups'][role])*s.Placement
            if role in common_delta:s.translate(A.Vector(*common_delta[role]))
            if role=='F_PI':
                r=candidate['F_PI']; rr=np.array(r['rotation_relative_current'])
                delta=np.array(r['centre_mm'])-rr@np.array(r['old_centre_mm'])
                s.Placement=placement(rr,delta.tolist())*s.Placement; changed[n]=s
            elif role in candidate['shifts_mm']:
                s.translate(A.Vector(*candidate['shifts_mm'][role]));changed[n]=s
            scene[n]=s;roles[n]=role
    holder={}
    for key,p in bank['relative_holder_poses'].items():
        pose=placement(p['rotation_rows'],p['translation_mm'])
        for kind in ('Housing','IN','OUT','ATO'):
            n=f'Ref_Material_F_{key}_CP2_{kind}_0_0'
            scene[n].Placement=pose*scene[n].Placement;holder[n]=key
    stages={n for groups in motion['membership'].values() for ns in groups.values() for n in ns}
    for row in motion['inventory']:
        n=row['object']
        if n not in scene and row['kind']=='surface' and (n in stages or n.startswith(('Print_P0_','Ref_Material_P0_','Battery','Print_CP2_TailRiser'))):
            if not n.startswith('BatteryFrameHardware'):scene[n]=reader.shape(native,n)
    for i in range(1,5):scene[f'BellyFoot{i}']=reader.shape(native,f'BellyFoot{i}')
    wires={};own={}
    for row in backbone['bend_allocations']:
        p=np.array(row['start_mm']);q=np.array(row['end_mm']);b=np.array(row['bend']);R=row['bend_R_mm'];land=row['land_mm']
        d=(q-p-R*b)/(land+R)
        wires[row['id']]=tube_prefix(p,d,row['radius_mm'],b,R,land);own[row['id']]={row['holder']}
    for row in routes(effective):
        n='Factory:'+row['wire'];wires[n]=pipe(row['parts'],row['radius_mm']);own[n]={row['source_group'],row['joint_group']}
    actual_new={r['wire']:pipe(r['parts'],r['radius_mm']) for r in candidate['routes']}
    for n,s in changed.items():
        for bn,b in scene.items():
            if n==bn or roles.get(n)==roles.get(bn):continue
            check(n,s,bn,b,'changed_case_vs_actual_static_material')
        for bn,b in wires.items():check(n,s,bn,b,'changed_case_vs_complete_existing_bank_or_MTA_prefix')
    save();print('Cases',len(report['contacts']),len(report['errors']),flush=True)
    for n,s in actual_new.items():
        for bn,b in scene.items():
            if n in ('W043','W077') and roles.get(bn)=='F_PI':continue # endpoint embedded in molded relief
            if n=='W043' and roles.get(bn)=='WAGO:P_SYS_new':continue # intended bare insertion
            if n=='W078' and roles.get(bn)=='MAIN':continue # termination is qualified separately
            check(n,s,bn,b,'complete_new_wire_vs_actual_static_material')
        for bn,b in wires.items():check(n,s,bn,b,'complete_new_wire_vs_complete_bank_and_MTA_prefixes')
        for bn,b in actual_new.items():
            if n<bn:check(n,s,bn,b,'new_wires_mutual')
        save();print('Wire',n,'contacts',len(report['contacts']),flush=True)
    reserves={}
    def box(n,lo,hi):
        reserves[n]=Part.makeBox(*(np.array(hi)-lo),A.Vector(*lo))
    # ONE inboard detour around vertical F_PI instead of crossing its case.
    box('LowerRail1Fore',[-72,17,39.72],[-64,23,42.72])
    box('LowerRail1ForeTurn',[-70,-3,39.72],[-64,23,42.72])
    box('LowerRail1Inboard',[-67,-3,39.72],[-33,3,42.72])
    box('LowerRail1RearTurn',[-36,-3,39.72],[-30,23,42.72])
    box('LowerRail1Rear',[-33,17,39.72],[108,23,42.72])
    box('SpliceClip',*candidate['splice']['clip_reservation_mm'])
    box('MainCarrier',[-52,-12,84],[-23,12,87])
    # rear branch below BUS, rooted at the existing rear post, not on skin
    for y in (-18.5,18.5):box('BUSRearBranch'+str(y),[102,y-3,67],[145,y+3,70])
    box('JPWMForeSeat',[-102,-22,72],[-70,-8,74])
    box('BUSNominalMating',*candidate['BUS']['nominal_mating_reserve_mm'])
    box('BUSSharedTwoLaneGrip',*candidate['BUS']['shared_two_lane_after_bend_grip_mm'])
    for entry in candidate['BUS']['ports']:
        r=entry['first_bend_and_after_bend_grip'];actual_new['Nominal'+r['wire']]=pipe(r['parts'],r['radius_mm'])
    for rn,r in reserves.items():
        for bn,b in scene.items():
            if rn=='BUSNominalMating' and roles.get(bn)=='BUS':continue
            check(rn,r,bn,b,'proposed_reservation_vs_actual_material',True)
        for bn,b in wires.items():check(rn,r,bn,b,'proposed_reservation_vs_bank_and_MTA_prefix',True)
        for bn,b in actual_new.items():
            if rn=='SpliceClip' and bn in ('W077','W078'):continue
            if rn in ('BUSSharedTwoLaneGrip','BUSNominalMating') and bn.startswith('NominalBUS.'):continue
            check(rn,r,bn,b,'proposed_reservation_vs_new_wire',True)
    # Nominal new BUS wire paths against every actual neighbor and prefixes.
    for n,s in actual_new.items():
        if not n.startswith('NominalBUS.'):continue
        for bn,b in scene.items():
            if roles.get(bn)=='BUS':continue
            check(n,s,bn,b,'nominal_BUS_wire_vs_actual_material')
        for bn,b in wires.items():check(n,s,bn,b,'nominal_BUS_wire_vs_bank_and_MTA_prefix')
    report.update(source_sha256={**report['source_sha256'],**reader.hashes},
        changed_case_objects=len(changed),bank_bends_included=24,MTA_factory_paths_included=8,
        proposed_reservations=list(reserves),motion_not_checked=True,full_other80net_curves_open=True,
        status='CHANGED_INTERFACES_REJECTED' if report['contacts'] or report['reservation_overlaps'] or report['errors'] else 'CHANGED_STATIC_INTERFACES_CLEAR_FULL_PLAN_OPEN')
    save();print(json.dumps(dict(status=report['status'],contacts=len(report['contacts']),reservation_overlaps=len(report['reservation_overlaps']),errors=len(report['errors']),pairs=report['exact_pairs'],seconds=report['worker_seconds'])),flush=True)

if __name__=='__main__':main()
