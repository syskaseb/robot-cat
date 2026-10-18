"""Coherent occupied-edge correction, reusing the unchanged frozen assembly.

Fore Pi is flipped as a complete functional module: GPIO opposite S1, data
down thenR30 back into body, sealed power above. Monitor/F_PWM occupy separate
vacated central Pi bays. Not a scalar offset retry or selected assembly.
"""
import hashlib
import json
import math
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from check_feline_shared_space import tube_prefix


def line_tube(a,b,r):
    a,b=A.Vector(*a),A.Vector(*b);wire=Part.Wire([Part.makeLine(a,b)])
    return wire.makePipeShell([Part.Wire([Part.makeCircle(r,a,b-a)])],True,False)


def main():
    tick=time.monotonic();src=OUT/'n01-front-bulkhead-architecture.json'
    prior=OUT/'n01-front-bulkhead-static-received.json';dest=OUT/'n01-front-service-split-plan.json'
    assert not dest.exists();p=json.loads(src.read_text());proof=json.loads(prior.read_text())
    assert proof['status']=='SAVED_WHOLE_TOPOLOGY_STATIC_REJECTED' and not proof['errors']
    changed_groups={'PiBulkhead','Monitor5015','F_PWM'}
    assert all(c['group'] in changed_groups or c['other_group'] in changed_groups
        for c in proof['actual_geometry_clearance_failures']+proof['reservation_conflicts'])
    for n,h in proof['source_sha256'].items():assert sha(ROOT/n)==h,n
    oldbundle=ROOT/p['bundle'];assert sha(oldbundle)==p['bundle_sha256']
    shapes={};rows={};raws={}
    with zipfile.ZipFile(oldbundle) as z:
        for r in p['parts']:
            raw=z.read(r['entry']);assert hashlib.sha256(raw).hexdigest()==r['sha256']
            s=Part.Shape();s.importBrepFromString(raw.decode('utf-8'));shapes[r['name']]=s;rows[r['name']]=dict(r);raws[r['name']]=raw
    oldpi=A.Placement(A.Vector(-108,0,-19.65)-A.Rotation(A.Vector(0,1,0),-90).multVec(A.Vector(0,0,47.72)),A.Rotation(A.Vector(0,1,0),-90))
    rot=A.Rotation(A.Vector(0,1,0),90)*A.Rotation(A.Vector(1,0,0),180)
    newpi=A.Placement(A.Vector(-125,0,86.15)-rot.multVec(A.Vector(0,0,47.72)),rot)
    relative=newpi*oldpi.inverse();changed=set();removed=[]
    def put(n,s,group,kind='reservation'):
        assert s.isValid() and len(s.Solids)==1,(n,'Invalid revision geometry')
        shapes[n]=s;rows[n]=dict(name=n,group=group,kind=kind);changed.add(n)
    for n,r in list(rows.items()):
        if r['group']=='PiBulkhead':
            if n.startswith('PiGPIO:'):
                shapes.pop(n);rows.pop(n);removed.append(n);continue
            s=shapes[n].copy();s.Placement=relative*s.Placement;put(n,s,r['group'],r['kind'])
        elif r['group']=='Monitor5015':
            s=shapes[n].copy();rr=A.Rotation(A.Vector(1,0,0),-90)
            s.Placement=A.Placement(A.Vector(25,0,102)-rr.multVec(A.Vector(50,68,0)),rr)*s.Placement
            put(n,s,r['group'],r['kind'])
        elif r['group']=='F_PWM':
            s=shapes[n].copy();s.translate(A.Vector(-10,61,66));put(n,s,r['group'],r['kind'])
    pi=json.loads((OUT/'n01-pi-full-port-contract.json').read_text())
    overrides=dict(p['changed_endpoints']);GPIOcurves={}
    for e in pi['GPIO_endpoints']:
        q=relative.multVec(A.Vector(*p['changed_endpoints'][e['endpoint']]['point_mm']))
        d=relative.Rotation.multVec(A.Vector(*p['changed_endpoints'][e['endpoint']]['departure_axis']))
        # Opposite header row fans away, preventing overlapping collinear
        # after-turn lands. Four first-row wires remain parallel graded lanes.
        ysign=-1 if abs(q.y+25.77)<1e-4 else 1
        bend=A.Vector(0,ysign/math.sqrt(2),-1/math.sqrt(2))
        wire=tube_prefix(list(q),list(d),.7,list(bend),10,3)
        end=q+d*13+bend*10;finish=end+bend*9
        put('PiGPIO:'+e['endpoint'],wire,'PiBulkhead')
        put('PiGPIOAfterGrip:'+e['endpoint'],line_tube(list(end),list(finish),.7),'PiBulkhead')
        overrides[e['endpoint']]=dict(point_mm=list(q),departure_axis=list(d),first_straight_mm=3,
            bend_direction=list(bend),R_mm=10,grip_after_turn_line_mm=[list(end),list(finish)],
            shared_firstrow_grip_group='GPIOrow1' if ysign>0 else 'GPIOrow2')
        GPIOcurves[e['endpoint']]=wire.fuse(shapes['PiGPIOAfterGrip:'+e['endpoint']])
    # Exact cable-to-cable separation before any world queries; no silent
    # self-crossing route family enters the expensive shared-space gate.
    separations=[]
    for i,(n,s) in enumerate(GPIOcurves.items()):
        for m,t in list(GPIOcurves.items())[i+1:]:
            gap=s.distToShape(t)[0];assert gap>=.2-1e-5,(n,m,gap)
            separations.append(dict(a=n,b=m,jacket_gap_mm=gap))
    mouth=newpi.multVec(A.Vector(*pi['USB_A_data_plug_budget']['source_wire_mouth_mm']))
    d=rot.multVec(A.Vector(1,0,0));bend=A.Vector(1,0,0);end=mouth+d*33+bend*30
    put('PiBudget:USB_A_after_turn_grip',line_tube(list(end),list(end+bend*9),2.5),'PiBulkhead')
    for wid,q in pi['full_selected_USB_C_receiver']['free_wire_mouths_mm'].items():
        overrides[wid+'/Pi']=dict(point_mm=list(newpi.multVec(A.Vector(*q))),departure_axis=list(d))
    for side,sgn in [('in',-1),('out',1)]:
        q=A.Vector(50+21*sgn,-15,46);axis=A.Vector(sgn,0,0)
        put('F_PWM:'+side+'_first_bend',tube_prefix(list(q),list(axis),1.55,[0,-1,0],12.4),'F_PWM','proposal_wire')
        finish=q+axis*(9+12.4)+A.Vector(0,-12.4,0)
        put('F_PWM:'+side+'_after_turn_grip',line_tube(list(finish),list(finish+A.Vector(0,-9,0)),1.55),'F_PWM','proposal_wire')
        overrides['F_PWM.'+side]=dict(jacket_exit_mm=list(q),departure_axis=list(axis),
            accounting_point_mm=[50+(-11.5 if sgn<0 else 8.9),-15,46],
            grip_after_turn_line_mm=[list(finish),list(finish+A.Vector(0,-9,0))])
    # Necessary aperture in each vertical floor: do not let a preserved solid
    # floor silently obstruct its own DOWN factory exit. Other geometry reused.
    for role in ('F_HY','F_HP','F_TY'):
        e=next(v for k,v in p['changed_endpoints'].items() if k.startswith(role+'.') and v['departure_axis'][2]<-.99)
        q=A.Vector(*e['point_mm']);n=role+':floor';s=shapes[n];b=s.BoundBox
        opening=Part.makeCylinder(3.25,b.ZLength+.2,A.Vector(q.x,q.y,b.ZMin-.1))
        put(n,s.cut(opening),role,rows[n]['kind']);changed_groups.add(role)
    extra=json.loads((OUT/'n01-all-extra-interface-contract.json').read_text())
    for e in [e for r in extra['sections'] for e in r['ends'] if e['group']=='HeadMechanism']:
        overrides[e['endpoint']]=dict(point_mm=[e['point_mm'][0],e['point_mm'][1],e['point_mm'][2]+35],
            departure_axis=e['departure_axis'],basis='Selected CP2 boundary ->R5 once ->wholehead+35, not anotherCP2SHIFT')
    bundle=dest.with_suffix('.zip');outrows=[]
    with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
        for n,r in rows.items():
            raw=shapes[n].exportBrepToString().encode('utf-8') if n in changed else raws[n]
            entry=f'{len(outrows):04}.brep';z.writestr(entry,raw)
            outrows.append(dict(r,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    unchanged=[n for n in rows if n not in changed]
    assert all(rows[n]['sha256']==next(r['sha256'] for r in outrows if r['name']==n) for n in unchanged)
    result=dict(p,status='FRONT_SERVICE_SPLIT_PROPOSAL_SAVED_NOT_STATIC_QUALIFIED',parts=outrows,
        source_parent=src.relative_to(ROOT).as_posix(),parent_static_receipt=prior.relative_to(ROOT).as_posix(),
        changed_part_names=sorted(changed),removed_part_names=removed,unchanged_part_names=unchanged,
        changed_groups=sorted(changed_groups),unchanged_raw_BRep_bytes_verified=True,
        bundle=bundle.relative_to(ROOT).as_posix(),bundle_sha256=sha(bundle),changed_endpoints=overrides,
        proposed_group_parts={g:[n for n,r in rows.items() if r['group']==g] for g in p['proposed_group_parts']},
        old_failures_all_owned_by_changed_geometry=True,GPIO_jacket_separation=separations,
        fore_Pi_functional_pose=dict(source_origin_target_mm=[-125,0,86.15],rotation_rows=[[getattr(rot.toMatrix(),f'A{i+1}{j+1}') for j in range(3)] for i in range(3)],
            GPIO_opposite_S1=True,USB_A_down_then_R30_back=True,neck_roof_candidate_mm=111,
            reason='FullS1/AUX/MTA fore cluster, occupied edges and complete first bends determine registration; not a smallX trial'),
        source_sha256={src.relative_to(ROOT).as_posix():sha(src),prior.relative_to(ROOT).as_posix():sha(prior),
            oldbundle.relative_to(ROOT).as_posix():sha(oldbundle),
            (OUT/'n01-pi-full-port-contract.json').relative_to(ROOT).as_posix():sha(OUT/'n01-pi-full-port-contract.json'),
            (OUT/'n01-all-extra-interface-contract.json').relative_to(ROOT).as_posix():sha(OUT/'n01-all-extra-interface-contract.json'),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
    result.pop('own_worker_cancelled',None)
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],parts=len(outrows),changed=len(changed),unchanged=len(unchanged),
        minimum_GPIO_jacket_gap_mm=min(r['jacket_gap_mm'] for r in separations),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
