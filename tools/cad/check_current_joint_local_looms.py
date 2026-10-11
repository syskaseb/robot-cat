"""Read-only20section material gate. Reuse immutable pilot, check new pairs."""
import json,time,zipfile,itertools,subprocess,hashlib,math
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_joint_local_looms import scene_parts,expanded_pose

def pilot_reuse(plan):
    commit='86f0754'
    def blob(path):return subprocess.check_output(['git','show',commit+':'+path.relative_to(ROOT).as_posix()],cwd=ROOT)
    source=OUT/'joint-local-loom-plan.json';checker=Path(__file__)
    raw=blob(source);prior=json.loads(raw);proof=json.loads(blob(OUT/'joint-local-loom-material.json'))
    assert proof['status']=='TWO_KNEE_SECTIONS_SAMPLED_MATERIAL_ONLY_FULL_CABLE_OPEN'
    assert not proof['contacts'] and not proof['errors'] and len(proof['tested_poses'])==27
    for n,h in proof['source_sha256'].items():
        f=ROOT/n
        actual=hashlib.sha256(raw if f==source else blob(checker)).hexdigest() if f in (source,checker) else SHA(f)
        assert actual==h,('PILOT_CONTEXT_CHANGED',n)
    reused=[]
    for old in prior['loops']:
        row=next(r for r in plan['loops'] if r['loom']==old['loom'] and r['joint']==old['joint'])
        for key in ('cad_code','parent_stage','child_stage','project_OD_mm','guide_mm'):assert row[key]==old[key],key
        for angle in range(-15,16):
            a=expanded_pose(row,angle)['parts'];b=expanded_pose(old,angle)['parts'];assert len(a)==len(b)
            for x,y in zip(a,b):
                assert x['kind']==y['kind']
                for key in ('start','end'):assert math.dist(x[key],y[key])<1e-8,(row['section'],angle,key)
                if 'poles_mm' in x:assert all(math.dist(u,v)<1e-8 for u,v in zip(x['poles_mm'],y['poles_mm']))
        reused.append(row['section'])
    return dict(commit=commit,sections=reused,retained_context_unchanged=True,
        expanded_geometry_matches_all31poses=True,new_mutual_pairs_not_waived=True,
        original_pairs=proof['pairs'],original_worker_seconds=proof['worker_seconds'])

def run(knees_only=False):
    tick=time.monotonic();stem='joint-local-knee' if knees_only else 'joint-local-loom'
    source=OUT/(stem+'-plan.json');screen=OUT/(stem+'-screen.json')
    p=json.loads(source.read_text());gate=json.loads(screen.read_text())
    assert p['status']==('JOINT_LOCAL_KNEE_MATH_ONLY' if knees_only else 'JOINT_LOCAL_SECTIONS_MATH_ONLY')
    assert len(p['loops'])==(8 if knees_only else 20)
    if knees_only:assert all(r['child_stage']=='Knee' for r in p['loops'])
    assert gate['status']=='JOINT_LOCAL_SHARED_SAMPLED_ONLY_MATERIAL_OPEN'
    for receipt in (p,gate):
        for n,h in receipt['source_sha256'].items():assert SHA(ROOT/n)==h,n
    reuse=pilot_reuse(p)
    from current_complete_harness_context import context,W,Part
    reader,pins,targets,old=context();pins.update((source,screen,Path(__file__)))
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';archive=ROOT/'hardware/simulation/v35/inputs.zip'
    pins.update((af,archive));axes=json.loads(af.read_text())['axes']
    with zipfile.ZipFile(archive) as z:components=json.loads(z.read('geometry.json'))['components']
    stages={q['name']:q['stage'].split('_')[1:] for q in components if q['stage'].startswith('Motion_')}
    result=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,W5_complete=False,
        physical_pass=False,native_changed=False,full_cable_routes_complete=False,
        continuous_motion_verified=False,simultaneous_all_leg_motion_verified=False,
        scope=f"{len(p['loops'])}local sections; all nominal then27joint samples perleg. Rigid/source/body guides and native supports OPEN.",
        pilot_reuse=reuse,tested_poses=[])
    def transforms(code,angles):
        T=W.A.Placement();ts={}
        for stage,angle in zip(('Hip','Knee','Ankle'),angles):
            a=next(v for v in axes if v['code']==code and v['stage']==stage)
            pv=W.A.Vector(*a['pivot_mm']);rot=W.A.Rotation(W.A.Vector(*a['axis']),angle)
            T=T*W.A.Placement(pv-rot.multVec(pv),rot);ts[stage]=T
        return ts
    def curve(row,hip,knee):
        edges=[]
        for q in scene_parts(row,hip,knee,axes):
            if q['kind']=='bezier':
                c=Part.BezierCurve();c.setPoles([W.A.Vector(*v) for v in q['poles_mm']]);edges.append(c.toShape())
            else:edges.extend(W.makewire([q]).Edges)
        shape=Part.Wire(edges)
        assert shape.isValid() and abs(sum(e.Length for e in shape.Edges)-row['guide_mm'])<.001
        return shape
    def pair(n,c,m,t,rr=0,pose=None):
        if not W.near(c,t,3+rr):return
        if not c.isValid() or not t.isValid():result['errors'].append(dict(a=n,b=m,cause='INVALID_BREP'));return
        result['pairs']+=1
        try:d,pts,_=c.distToShape(t)
        except Exception as e:result['errors'].append(dict(a=n,b=m,cause=repr(e)));return
        if d<3+rr-1e-4:
            hit=dict(a=n,b=m,distance_mm=d,required_mm=3+rr,pose=pose,
                witness_mm=[list(v) for v in pts[0]] if pts else None)
            result['contacts'].append(hit);print('Joint-local actual contact',json.dumps(hit),flush=True)
    rows={r['section']:r for r in p['loops']};nominal={n:curve(r,0,0) for n,r in rows.items()};tested=set()
    def case(code,angles):
        hip,knee,ankle=angles;pose=dict(code=code,hip=hip,knee=knee,ankle=ankle)
        ts=transforms(code,angles) if code else {}
        changing={n for n,r in rows.items() if code is None or r['cad_code']==code}
        curves={n:curve(rows[n],hip,knee) if code and n in changing else c for n,c in nominal.items()}
        for n in sorted(changing):
            c=curves[n];r=rows[n];ca=(hip,) if r['child_stage']=='Hip' else (hip,knee)
            if n not in reuse['sections']:
                for m,t in targets.items():
                    if not t.Solids:continue
                    member=stages.get(m.removeprefix('P0_'));stage=member[1] if member and member[0]==code else None
                    ma=() if not stage else (hip,) if stage=='Hip' else (hip,knee) if stage=='Knee' else angles
                    key=(n,ca,m,ma)
                    if key in tested:continue
                    tested.add(key)
                    if stage:t=t.copy();t.Placement=ts[stage]*t.Placement
                    pair(n,c,m,t,pose=pose)
                for m,(t,rr) in old.items():
                    key=(n,ca,m)
                    if key not in tested:tested.add(key);pair(n,c,m,t,rr,pose)
            for m,t in curves.items():
                if m==n or m in changing and m<n:continue
                other=rows[m];oa=((hip,) if other['child_stage']=='Hip' else (hip,knee)) if m in changing else (0,) if other['child_stage']=='Hip' else (0,0)
                key=('mutual',tuple(sorted(((n,ca),(m,oa)))))
                if key not in tested:tested.add(key);pair(n,c,m,t,3,pose)
        result['tested_poses'].append(pose)
        print('Joint-local material pose',code,angles,'pairs',result['pairs'],'contacts',len(result['contacts']),flush=True)
    case(None,(0,0,0))
    if not result['contacts'] and not result['errors']:
        for code in dict.fromkeys(r['cad_code'] for r in rows.values()):
            for angles in itertools.product((-15,0,15),repeat=3):
                if angles==(0,0,0):continue
                case(code,angles)
                if result['contacts'] or result['errors']:break
            if result['contacts'] or result['errors']:break
    result.update(status='REJECTED_JOINT_LOCAL_SHARED_MATERIAL' if result['contacts'] or result['errors'] else ('EIGHT_KNEE_SECTIONS_SAMPLED_MATERIAL_ONLY_FULL_CABLE_OPEN' if knees_only else 'TWENTY_LOCAL_SECTIONS_SAMPLED_MATERIAL_ONLY_FULL_CABLE_OPEN'),
        worker_seconds=time.monotonic()-tick,source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in pins}})
    (OUT/(stem+'-material.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('status','pairs','contacts','errors','worker_seconds')}),flush=True)
    return result

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--knees-only',action='store_true')
    run(parser.parse_args().knees_only)
