"""Read-only material gate for the two local Knee flex sections, not W5."""
import json,time,zipfile
from pathlib import Path
from plan_current_main_sources import ROOT,OUT,SHA


def run():
    tick=time.monotonic();source=OUT/'joint-local-loom-plan.json';p=json.loads(source.read_text())
    assert p['status']=='JOINT_LOCAL_PILOT_MATH_ONLY'
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    from current_complete_harness_context import context,W,Part
    reader,pins,targets,old=context();pins.update((source,Path(__file__)))
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';archive=ROOT/'hardware/simulation/v35/inputs.zip'
    pins.update((af,archive));axes=json.loads(af.read_text())['axes']
    with zipfile.ZipFile(archive) as z:components=json.loads(z.read('geometry.json'))['components']
    code=p['loops'][0]['cad_code'];aa={a['stage']:a for a in axes if a['code']==code}
    stages={q['name']:q['stage'].split('_')[-1] for q in components if q['stage'].startswith('Motion_'+code+'_')}
    result=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,W5_complete=False,
        physical_pass=False,native_changed=False,full_cable_routes_complete=False,
        continuous_motion_verified=False,scope='Two local Knee sections only; actual retained material and body wires',tested_poses=[])
    def transforms(angles):
        T=W.A.Placement();ts={}
        for stage,angle in zip(('Hip','Knee','Ankle'),angles):
            a=aa[stage];pv=W.A.Vector(*a['pivot_mm']);rot=W.A.Rotation(W.A.Vector(*a['axis']),angle)
            T=T*W.A.Placement(pv-rot.multVec(pv),rot);ts[stage]=T
        return ts
    def curve(row,hip,knee):
        pose=next(q for q in row['poses'] if q['angle']==knee);edges=[]
        for q in pose['parts']:
            if q['kind']=='bezier':
                c=Part.BezierCurve();c.setPoles([W.A.Vector(*v) for v in q['poles_mm']]);edges.append(c.toShape())
            else:edges.extend(W.makewire([q]).Edges)
        shape=Part.Wire(edges)
        shape.Placement=transforms((hip,knee,0))['Hip']*shape.Placement
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
            result['contacts'].append(hit);print('Local Knee actual contact',json.dumps(hit),flush=True)
    def save():
        result.update(status='REJECTED_JOINT_LOCAL_PILOT_MATERIAL' if result['contacts'] or result['errors'] else 'TWO_KNEE_SECTIONS_SAMPLED_MATERIAL_ONLY_FULL_CABLE_OPEN',
            worker_seconds=time.monotonic()-tick,source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in pins}})
        (OUT/'joint-local-loom-material.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:result[k] for k in ('status','pairs','contacts','errors','worker_seconds')}),flush=True)
    import itertools
    poses=[(0,0,0)]+[q for q in itertools.product((-15,0,15),repeat=3) if q!=(0,0,0)]
    tested=set()
    for hip,knee,ankle in poses:
        pose=dict(hip=hip,knee=knee,ankle=ankle);ts=transforms((hip,knee,ankle))
        curves={r['loom']:curve(r,hip,knee) for r in p['loops']}
        for n,c in curves.items():
            for m,t in targets.items():
                if not t.Solids:continue
                stage=stages.get(m.removeprefix('P0_'))
                ma=() if not stage else (hip,) if stage=='Hip' else (hip,knee) if stage=='Knee' else (hip,knee,ankle)
                key=(n,hip,knee,m,ma)
                if key in tested:continue
                tested.add(key)
                if stage:t=t.copy();t.Placement=ts[stage]*t.Placement
                pair(n,c,m,t,pose=pose)
            for m,(t,rr) in old.items():
                key=(n,hip,knee,m)
                if key not in tested:tested.add(key);pair(n,c,m,t,rr,pose)
            for m,t in curves.items():
                key=(n,hip,knee,m)
                if m>n and key not in tested:tested.add(key);pair(n,c,m,t,3,pose)
        result['tested_poses'].append(pose)
        print('Local Knee material pose',hip,knee,ankle,'pairs',result['pairs'],flush=True)
        if result['contacts'] or result['errors']:break
    save();return result


if __name__=='__main__':run()
