"""Bounded shared-space allocation, with actual material inside the planner.

No native mutation, worker duplication or repeated whole-assembly rebuilds.
Every candidate is a three-cable family; retained material, fixed wires and
both Knee guides participate BEFORE selecting a plane. Only a compact current
result is saved, not hundreds of variant files. Native load paths remain open.
"""
import copy,itertools,json,math,time,zipfile
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_moving_looms import add,sub,mul,rotation
from plan_current_hip_axial_looms import s_offset
from plan_current_mta_interfaces import line
from plan_current_joint_local_looms import scene_parts
from current_complete_harness_context import context,W,Part


def four_arcs(a,b,t,direction,length=108):
    centre=mul(add(a,b),.5)
    def at(h):
        mid=add(centre,mul(direction,h))
        return s_offset(a,mid,t)+s_offset(mid,b,t)
    low,high=0.,50.
    if not sum(p['length_mm'] for p in at(low))<=length<=sum(p['length_mm'] for p in at(high)):return None
    for _ in range(32):
        h=(low+high)/2
        if sum(p['length_mm'] for p in at(h))<length:low=h
        else:high=h
    q=at((low+high)/2)
    return q if min(p['radius_mm'] for p in q)>=31 else None


def curve_at(r,angle):
    fixed=r['fixed_anchor_world_mm'];t=r['axial_tangent'];pivot=r['pivot_mm']
    end=add(pivot,rotation(sub(r['moving_anchor_rest_world_mm'],pivot),r['joint_axis'],angle))
    a,b=add(fixed,mul(t,9)),sub(end,mul(t,9))
    q=four_arcs(a,b,t,r['midpoint_direction'])
    return [line(fixed,a)]+q+[line(b,end)] if q else None


def run(budget_seconds=600):
    tick=time.monotonic();reader,pins,targets,old=context()
    hf=OUT/'hip-axial-loom-plan.json';kf=OUT/'joint-local-knee-plan.json'
    hp=json.loads(hf.read_text());kp=json.loads(kf.read_text())
    proof=OUT/'joint-local-knee-material.json';green=json.loads(proof.read_text())
    assert green['status']=='EIGHT_KNEE_SECTIONS_SAMPLED_MATERIAL_ONLY_FULL_CABLE_OPEN'
    for p in (hp,kp,green):
        for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    archive=ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(archive) as z: components=json.loads(z.read('geometry.json'))['components']
    stages={q['name']:q['stage'].split('_')[1:] for q in components if q['stage'].startswith('Motion_')}
    pins.update((hf,kf,proof,af,archive,Path(__file__)))
    result=dict(status='PENDING',accepted_families=[],leg_results=[],pair_tests=0,errors=[],
        selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        continuous_motion_verified=False,bracket_load_paths_qualified=False,
        scope='Bounded whole-family spatial allocation with valid material, all retained fixed wires and Knee guides; no manufacturing release')
    shape_cache={};placed=[]
    def wire(parts):
        edges=[]
        for q in parts:
            if q['kind']=='bezier':
                c=Part.BezierCurve();c.setPoles([W.A.Vector(*v) for v in q['poles_mm']]);edges.append(c.toShape())
            else:edges.extend(W.makewire([q]).Edges)
        s=Part.Wire(edges);assert s.isValid()
        return s
    def collision(c,rr,t,rad=0):
        if not W.near(c,t,rr+rad):return False
        result['pair_tests']+=1
        assert c.isValid() and t.isValid()
        return c.distToShape(t)[0]<rr+rad-1e-4
    def test(family,angles):
        code=family[0]['cad_code'];h,k,a=angles
        if h not in candidate_cache:candidate_cache[h]=[wire(curve_at(r,h)) for r in family]
        curves=candidate_cache[h]
        ts={};T=W.A.Placement()
        for stage,angle in zip(('Hip','Knee','Ankle'),angles):
            ax=next(v for v in axes if v['code']==code and v['stage']==stage)
            pv=W.A.Vector(*ax['pivot_mm']);rot=W.A.Rotation(W.A.Vector(*ax['axis']),angle)
            T=T*W.A.Placement(pv-rot.multVec(pv),rot);ts[stage]=T
        for c in curves:
            for name,t in targets.items():
                if not t.Solids:continue
                member=stages.get(name.removeprefix('P0_'))
                stage=member[1] if member and member[0]==code else None
                if stage:
                    key=(name,angles[:('Hip','Knee','Ankle').index(stage)+1])
                    if key not in shape_cache:
                        s=t.copy();s.Placement=ts[stage]*s.Placement;shape_cache[key]=s
                    t=shape_cache[key]
                if collision(c,3,t):return 'material/'+name
            for name,(t,rr) in old.items():
                if collision(c,3,t,rr):return 'fixed-wire/'+name
        for i,c in enumerate(curves):
            for t in curves[i+1:]:
                if collision(c,3,t,3):return 'within-family'
            for q in kp['loops']:
                active=q['cad_code']==code
                key=('knee',q['section'],h if active else 0,k if active else 0)
                if key not in shape_cache:
                    shape_cache[key]=wire(scene_parts(q,h if active else 0,k if active else 0,axes))
                if collision(c,3,shape_cache[key],3):return 'Knee/'+q['section']
            for q in placed:
                key=('placed',q['section'])
                if key not in shape_cache:shape_cache[key]=wire(curve_at(q,0))
                if collision(c,3,shape_cache[key],3):return 'other-leg/'+q['section']
        return None
    # Whole family planes ordered by root displacement, not witness nudges.
    # No unsupported change of motor, axis, purchased case or existing wire.
    candidates=list(itertools.product((40,48,56,64,72,80,88,96),(65,73,81,89,97),('Y','Z'),('UP','OUT')))
    candidates.sort(key=lambda q:abs(q[0]-45)+abs(q[1]-65)+(8 if q[2]=='Z' else 0)+(4 if q[3]=='UP' else 0))
    for leg in ('FrontLeft','FrontRight','RearLeft','RearRight'):
        initial=[r for r in hp['loops'] if r['physical_leg']==leg]
        receipt=dict(leg=leg,candidates_tested=0,rejections={},accepted=False)
        for y,z,pitch,bow in candidates:
            if time.monotonic()-tick>budget_seconds:receipt['budget_reached']=True;break
            family=copy.deepcopy(initial)
            for i,r in enumerate(family):
                for key in ('fixed_anchor_world_mm','moving_anchor_rest_world_mm'):
                    r[key][1]=r['side']*(y+(8*i if pitch=='Y' else 0))
                    r[key][2]=z+(8*i if pitch=='Z' else 0)
                r['midpoint_direction']=[0,0,1] if bow=='UP' else [0,r['side'],0]
                r.pop('poses',None)
            receipt['candidates_tested']+=1
            candidate_cache={}
            if receipt['candidates_tested']%10==0:
                print('Allocation progress',leg,receipt['candidates_tested'],'pairs',result['pair_tests'],
                    'seconds',round(time.monotonic()-tick,1),flush=True)
            reason=None
            try:
                if any(curve_at(r,h) is None for r in family for h in (0,-15,15)):reason='fixed-length/R31'
                if reason is None:reason=test(family,(0,0,0))
                if reason is None:
                    for angles in itertools.product((-15,0,15),repeat=3):
                        if angles==(0,0,0):continue
                        if any(curve_at(r,angles[0]) is None for r in family):reason='fixed-length/R31';break
                        reason=test(family,angles)
                        if reason:break
                if reason is None:
                    # Only the selected candidate gets the full31angle math;
                    # no expensive31copies of all primitives in the receipt.
                    for r in family:
                        r['poses']=[]
                        for angle in range(-15,16):
                            q=curve_at(r,angle)
                            if q is None:reason='fixed-length/R31';break
                            r['poses'].append(dict(angle=angle,guide_mm=sum(p['length_mm'] for p in q),
                                minimum_R_mm=min(p.get('radius_mm',float('inf')) for p in q)))
                        if reason:break
                if reason is None:
                    placed.extend(family);result['accepted_families'].extend(family)
                    receipt.update(accepted=True,allocation=dict(absY_mm=y,Z_mm=z,pitch_axis=pitch,bow=bow),sampled_poses=27)
                    break
            except Exception as exc:
                result['errors'].append(dict(leg=leg,cause=repr(exc)));reason='geometry-error'
            receipt['rejections'][reason]=receipt['rejections'].get(reason,0)+1
            if result['errors']:break
        result['leg_results'].append(receipt)
        print('Common-space allocation',json.dumps(receipt),flush=True)
        if receipt.get('budget_reached') or result['errors']:break
    complete=len(result['accepted_families'])==12 and not result['errors']
    result.update(status='TWELVE_HIP_FAMILIES_SAMPLED_SPACE_ONLY_ROOTS_OPEN' if complete else 'BOUNDED_HIP_SPACE_INCOMPLETE',
        worker_seconds=round(time.monotonic()-tick,3),budget_seconds=budget_seconds,
        source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in pins}})
    (OUT/'hip-common-space.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],families=len(result['accepted_families']),
        seconds=result['worker_seconds'],errors=result['errors'])),flush=True)
    return result


if __name__=='__main__':run()
