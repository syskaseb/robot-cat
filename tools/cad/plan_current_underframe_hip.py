"""One underside Hip cable family, not another ATO-gallery offset search.

All twelve cables pass below the rigid electronics platform, with no cuts to
P0 or bankR47. Root mounts and full body/member joins remain a separate gate.
Only one layout is tried. A rejected layout is not retried automatically.
"""
import copy,itertools,json,time,zipfile
from pathlib import Path
from allocate_current_hip_space import curve_at as symmetric_curve, four_arcs
from plan_current_moving_looms import add,sub,mul,rotation,norm
from plan_current_mta_interfaces import line
from current_prototype_harness_scene import context,wire,W
from plan_current_main_sources import ROOT,OUT,SHA
from plan_current_joint_local_looms import scene_parts


def hip_curve(r,angle):
    if not r.get('asymmetric'):return symmetric_curve(r,angle)
    fixed=r['fixed_anchor_world_mm'];t=r['axial_tangent'];pivot=r['pivot_mm']
    end=add(pivot,rotation(sub(r['moving_anchor_rest_world_mm'],pivot),r['joint_axis'],angle))
    a,b=add(fixed,mul(t,9)),sub(end,mul(t,9));delta=sub(b,a)
    d=[t[1]*delta[2]-t[2]*delta[1],t[2]*delta[0]-t[0]*delta[2],t[0]*delta[1]-t[1]*delta[0]]
    d=mul(d,1/norm(d))
    if d[1]*r['side']<0:d=mul(d,-1)
    # Free midpoint bows normal to the changing endpoint displacement.
    # Equal half-offsets keep both R31 arcs feasible without a tall moving mast.
    q=four_arcs(a,b,t,d,length=172)
    return [line(fixed,a)]+q+[line(b,end)] if q else None


def family(layout):
    hp=json.loads((OUT/'hip-axial-loom-plan.json').read_text());rows=copy.deepcopy(hp['loops'])
    assert layout in ('underframe','inward-corridor','fixed-high-moving-low')
    for r in rows:
        r.pop('poses',None)
        for key in ('fixed_anchor_world_mm','moving_anchor_rest_world_mm'):
            r[key][2]=-50 if layout=='underframe' else 60 if r['physical_leg'].startswith('Front') else 65
        r['midpoint_direction']=[0,r['side']*(1 if layout=='underframe' else -1),0]
        if layout=='fixed-high-moving-low':
            r['fixed_anchor_world_mm'][0]-=20*r['axial_tangent'][0]
            r['fixed_anchor_world_mm'][2]=150;r['moving_anchor_rest_world_mm'][2]=65
            r['asymmetric']=True;r['guide_mm']=190;r['flex_length_mm']=172
            r['support_status']='OPEN: high FIXED comb on electronics carrier; original low MOVING root needs short case mount. No tall moving mast.'
    return rows


def run(layout='underframe'):
    tick=time.monotonic();reader,pins,targets,old=context()
    hf=OUT/'hip-axial-loom-plan.json';kf=OUT/'joint-local-knee-plan.json'
    hp=json.loads(hf.read_text());kp=json.loads(kf.read_text())
    af=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    axes=json.loads(af.read_text())['axes'];archive=ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(archive) as z:components=json.loads(z.read('geometry.json'))['components']
    stages={q['name']:q['stage'].split('_')[1:] for q in components if q['stage'].startswith('Motion_')}
    pins.update((hf,kf,af,archive,Path(__file__)))
    rows=family(layout)
    result=dict(status='PENDING',layout=layout,
        rationale=('Fixed carrier comb Z150, moving case root Z65, axial span140, flex172+two9mm lands=190. Free midpoint normal to endpoint displacement; no tall moving mast or native cut. All372 Hip angles passed R31 math before the material worker.' if layout=='fixed-high-moving-low' else 'Single underside gallery' if layout=='underframe' else
            'Whole family bows INWARD, away from rear data cases and their fixed approach lands; front plane below S0 family bottom65 and above retained motors. Bank/P0/source wires unchanged; native roots still open.'),
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
            lambda r=r:wire(hip_curve(r,h if r['cad_code']==code else 0))) for r in rows}
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
                q=hip_curve(r,h);assert q is not None,(r['section'],h,'length/R31')
                assert abs(sum(p['length_mm'] for p in q)-r['guide_mm'])<1e-5
        for code in dict.fromkeys(r['cad_code'] for r in rows):test(code,0,0,0)
        # A nominal failure rejects the architecture before motion/native work.
        if not result['contacts']:
            for code in dict.fromkeys(r['cad_code'] for r in rows):
                for angles in itertools.product((-15,0,15),repeat=3):
                    if angles!=(0,0,0):test(code,*angles)
                    if result['contacts']:break
                print(layout,code,'contacts',len(result['contacts']),flush=True)
                if result['contacts']:break
    except Exception as exc:result['errors'].append(repr(exc))
    label={'underframe':'UNDERFRAME_HIP','inward-corridor':'INWARD_HIP_CORRIDOR','fixed-high-moving-low':'ASYMMETRIC_HIP_CORRIDOR'}[layout]
    result.update(status='REJECTED_'+label if result['contacts'] or result['errors'] else label+'_SAMPLED_ONLY_ROOTS_AND_JOINS_OPEN',
        worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in pins}})
    filename='underframe-hip-plan.json' if layout=='underframe' else 'hip-corridor-current.json'
    (OUT/filename).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('status','pair_tests','sampled_cases','contacts','errors','worker_seconds')}),flush=True)
    return result


if __name__=='__main__':
    import sys
    # Explicit architecture only; a rejected default is never an automatic retry.
    assert len(sys.argv)==2 and sys.argv[1]=='fixed-high-moving-low','Specify the newly planned architecture; rejected layouts are not automatic retries'
    run(sys.argv[1])
