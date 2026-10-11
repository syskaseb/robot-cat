"""One underside Hip cable family, not another ATO-gallery offset search.

All twelve cables pass below the rigid electronics platform, with no cuts to
P0 or bankR47. Root mounts and full body/member joins remain a separate gate.
Only one layout is tried. A rejected layout is not retried automatically.
"""
import copy,itertools,json,time,zipfile
from pathlib import Path
from allocate_current_hip_space import curve_at
from current_prototype_harness_scene import context,wire,W
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_joint_local_looms import scene_parts


def run():
    tick=time.monotonic();reader,pins,targets,old=context()
    hf=OUT/'hip-axial-loom-plan.json';kf=OUT/'joint-local-knee-plan.json'
    hp=json.loads(hf.read_text());kp=json.loads(kf.read_text())
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    axes=json.loads(af.read_text())['axes'];archive=ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(archive) as z:components=json.loads(z.read('geometry.json'))['components']
    stages={q['name']:q['stage'].split('_')[1:] for q in components if q['stage'].startswith('Motion_')}
    pins.update((hf,kf,af,archive,Path(__file__)))
    rows=copy.deepcopy(hp['loops'])
    for r in rows:
        r.pop('poses',None)
        for key in ('fixed_anchor_world_mm','moving_anchor_rest_world_mm'):
            r[key][2]=-50
        r['midpoint_direction']=[0,r['side'],0]
    result=dict(status='PENDING',layout='Single underside axial gallery Z-50, Y45/53/61; electronics and ATO bank unchanged',
        loops=rows,contacts=[],errors=[],pair_tests=0,sampled_cases=0,
        native_changed=False,selected=False,W5_complete=False,physical_pass=False,
        roots_and_full_joins_open=True,continuous_sweep_verified=False)
    cache={}
    def cached(key,make):
        if key not in cache:cache[key]=make()
        return cache[key]
    def hit(c,rr,t,rad=0):
        if not W.near(c,t,rr+rad):return False
        result['pair_tests']+=1;assert c.isValid() and t.isValid()
        return c.distToShape(t)[0]<rr+rad-1e-4
    def test(code,h,k,a):
        result['sampled_cases']+=1
        T=W.A.Placement();transforms={}
        for stage,angle in zip(('Hip','Knee','Ankle'),(h,k,a)):
            ax=next(v for v in axes if v['code']==code and v['stage']==stage)
            pv=W.A.Vector(*ax['pivot_mm']);rot=W.A.Rotation(W.A.Vector(*ax['axis']),angle)
            T=T*W.A.Placement(pv-rot.multVec(pv),rot);transforms[stage]=T
        curves={r['section']:cached(('hip',r['section'],h if r['cad_code']==code else 0),
            lambda r=r:wire(curve_at(r,h if r['cad_code']==code else 0))) for r in rows}
        knees={r['section']:cached(('knee',r['section'],h if r['cad_code']==code else 0,k if r['cad_code']==code else 0),
            lambda r=r:wire(scene_parts(r,h if r['cad_code']==code else 0,k if r['cad_code']==code else 0,axes))) for r in kp['loops']}
        active=[r for r in rows if r['cad_code']==code]
        for r in active:
            name=r['section'];c=curves[name];reason=None
            for n,t in targets.items():
                if not t.Solids:continue
                member=stages.get(n.removeprefix('P0_'))
                if member and member[0]==code:
                    stage=member[1];key=('part',n,(h,k,a)[:('Hip','Knee','Ankle').index(stage)+1])
                    def moved(t=t,stage=stage):
                        s=t.copy();s.Placement=transforms[stage]*s.Placement;return s
                    t=cached(key,moved)
                if hit(c,3,t):reason='material/'+n;break
            if reason is None:
                for n,(t,rr) in old.items():
                    if hit(c,3,t,rr):reason='fixed-wire/'+n;break
            if reason is None:
                for n,t in {**curves,**knees}.items():
                    if n!=name and hit(c,3,t,3):reason='moving-guide/'+n;break
            if reason:result['contacts'].append(dict(section=name,angles=[h,k,a],other=reason))
    try:
        for r in rows:
            for h in range(-15,16):
                q=curve_at(r,h);assert q is not None,(r['section'],h,'length/R31')
                assert abs(sum(p['length_mm'] for p in q)-126)<1e-5
        for code in dict.fromkeys(r['cad_code'] for r in rows):test(code,0,0,0)
        # A nominal failure rejects the architecture before motion/native work.
        if not result['contacts']:
            for code in dict.fromkeys(r['cad_code'] for r in rows):
                for angles in itertools.product((-15,0,15),repeat=3):
                    if angles!=(0,0,0):test(code,*angles)
                    if result['contacts']:break
                print('Underframe',code,'contacts',len(result['contacts']),flush=True)
                if result['contacts']:break
    except Exception as exc:result['errors'].append(repr(exc))
    result.update(status='REJECTED_UNDERFRAME_HIP' if result['contacts'] or result['errors'] else 'UNDERFRAME_HIP_SAMPLED_ONLY_ROOTS_AND_JOINS_OPEN',
        worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in pins}})
    (OUT/'underframe-hip-plan.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('status','pair_tests','sampled_cases','contacts','errors','worker_seconds')}),flush=True)
    return result


if __name__=='__main__':run()
