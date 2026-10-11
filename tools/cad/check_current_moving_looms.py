"""One common12loom material gate; cheap plan must be viable first.

Nominal all-looms test first. A rejected rest layout is not sent into the
expensive motion matrix. Distances use real valid BReps, not box contacts.
"""
import json,time,itertools,zipfile
from pathlib import Path
from plan_current_main_sources import ROOT,BASE,OUT,SHA

def run():
    tick=time.monotonic();f=OUT/'moving-looms-plan.json';p=json.loads(f.read_text())
    assert p['status']=='PROJECT_FLEX_ALLOCATION_ONLY'
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    from current_complete_harness_context import context,W,Part
    reader,pins,targets,old=context();pins.update((f,Path(__file__)))
    result=dict(status='PENDING',pairs=0,contacts=[],errors=[],selected=False,W5_complete=False,
        physical_pass=False,native_parts_changed=0,project_bundle_OD_mm=6,
        manufacturer_flex_data_verified=False,continuous_sweep_verified=False,sampled_poses=0)
    def shape(row,angles):
        v=next(v for v in row['poses'] if v['angles']==list(angles))
        poles=v.get('spans_mm',[v.get('poles_mm')]);edges=[]
        for q in poles:
            curve=Part.BezierCurve();curve.setPoles([W.A.Vector(*x) for x in q]);edges.append(curve.toShape())
        if v.get('return_parts_mm'):edges.extend(W.makewire(v['return_parts_mm']).Edges)
        curve=Part.Wire(edges);assert curve.isValid()
        # OCC aggregate Wire.Length uses a different coarse quadrature on
        # these Beziers:365.994142 vs precise edge365.799797. Sum the actual
        # edges, verified independently by adaptive integration/dense samples.
        exact_length=sum(e.Length for e in curve.Edges)
        assert abs(exact_length-row['constant_flex_budget_mm'])<.001,(row['loom'],exact_length,row['constant_flex_budget_mm'])
        return curve
    def pair(n,c,m,t,rad=0,pose=None):
        if not W.near(c,t,3+rad):return
        assert c.isValid() and t.isValid(),(n,m);result['pairs']+=1
        d,pts,_=c.distToShape(t)
        if d<3+rad-1e-4:result['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=3+rad,
            pose=pose,witness_mm=[list(v) for v in pts[0]] if pts else None))
    def save(status):
        result.update(status=status,worker_seconds=round(time.monotonic()-tick,3),source_sha256={
            **reader.hashes,**{q.relative_to(ROOT).as_posix():SHA(q) for q in pins}})
        (OUT/'moving-looms-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:result[k] for k in ('status','pairs','contacts','worker_seconds')}),flush=True)
    nominal={r['loom']:shape(r,(0,) if r['motion_stage'].endswith('_Hip') else (0,0)) for r in p['looms']}
    for n,c in nominal.items():
        for m,t in targets.items():
            if t.Solids:pair(n,c,m,t)
        for m,(t,rad) in old.items():pair(n,c,m,t,rad)
        for m,t in nominal.items():
            if m>n:pair(n,c,m,t,3)
        print('Nominal loom',n,'contacts',len(result['contacts']),flush=True)
    if result['contacts']:save('REJECTED_SHARED_LOOM_REST_MATERIAL');return
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';archive=ROOT/'hardware/simulation/v35/inputs.zip'
    pins.update((af,archive));axes=json.loads(af.read_text())['axes']
    with zipfile.ZipFile(archive) as z:geom=json.loads(z.read('geometry.json'))
    code_by_leg={r['loom'][:2]:r['motion_stage'].split('_')[1] for r in p['looms']}
    for leg,code in code_by_leg.items():
        aa={a['stage']:a for a in axes if a['code']==code};rows=[r for r in p['looms'] if r['loom'].startswith(leg)]
        moving_names={q['name']:q['stage'].split('_')[-1] for q in geom['components'] if q['stage'].startswith('Motion_'+code+'_')}
        for hip,knee,ankle in itertools.product((-15,0,15),repeat=3):
            if hip==knee==ankle==0:continue
            result['sampled_poses']+=1;pose=dict(leg=leg,hip=hip,knee=knee,ankle=ankle)
            new={r['loom']:shape(r,(hip,) if r['motion_stage'].endswith('_Hip') else (hip,knee)) for r in rows}
            transforms={};T=W.A.Placement()
            for st,angle in zip(('Hip','Knee','Ankle'),(hip,knee,ankle)):
                a=aa[st];pivot=W.A.Vector(*a['pivot_mm']);rot=W.A.Rotation(W.A.Vector(*a['axis']),angle)
                T=T*W.A.Placement(pivot-rot.multVec(pivot),rot);transforms[st]=T
            for n,c in new.items():
                for m,t in targets.items():
                    if not t.Solids:continue
                    part=m.removeprefix('P0_')
                    if part in moving_names:
                        t=t.copy();t.Placement=transforms[moving_names[part]]*t.Placement
                    pair(n,c,m,t,pose=pose)
                for m,(t,rad) in old.items():pair(n,c,m,t,rad,pose)
                for m,t in nominal.items():
                    if not m.startswith(leg):pair(n,c,m,t,3,pose)
                for m,t in new.items():
                    if m>n:pair(n,c,m,t,3,pose)
            if result['contacts']:save('REJECTED_SHARED_LOOM_SAMPLED_MATERIAL');return
        print('Moving loom family',leg,'clear sampled matrix',flush=True)
    save('TWELVE_LOOM_GUIDES_SAMPLED_CLEAR_FANOUT_NATIVE_OPEN')

if __name__=='__main__':run()
