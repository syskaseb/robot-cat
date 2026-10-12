"""Exact affected Knee curves gate; no native roots or whole cable claim."""
import itertools,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import check_low_hip_loom_layout as P
import plan_current_head_wiring as H
from exact_pair_receipts import PairReceipts


def run():
    tick=time.monotonic();fp=P.OUT/'outboard-knee-planes-plan.json';plan=json.loads(fp.read_text())
    assert plan['status']=='KNEE_PLANES_RESERVED_EXACT_MATERIAL_AND_NATIVE_ROOTS_OPEN'
    for n,h in plan['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    family=json.loads((P.OUT/'low-joint-family-plan.json').read_text());rows=plan['knees']
    axes=json.loads((P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    with zipfile.ZipFile(P.ROOT/'hardware/simulation/v35/inputs.zip') as z:members=json.loads(z.read('geometry.json'))['components']
    membership={r['name']:r['stage'].split('_')[1:] for r in members if r['stage'].startswith('Motion_')}
    targets,old,archive=P.scene();supports,assigned,_=P.allocate(family['hips'],targets);reader=H.P.SavedShapes()
    heads={f'head/{y}/{p}/{n}':s for y,p in itertools.product((-15,0,15),(-10,0,5)) for n,s in H.head(reader,y,p).items()}
    cache=PairReceipts(P.OUT/'outboard-knee-pair-cache.json',P.W.near);memo={};seen=set()
    report=dict(status='PENDING',cases=0,pairs=0,contacts=[],errors=[],selected=False,native_changed=False,W5_complete=False,physical_pass=False,
        scope='All8Knee bows vs current body/head9poses/retained wires/newHip curves and allocated Hip supports at108coupled leg samples. NEW Knee grip roots and complete cables are NOT covered.')
    def tr(ax,angle):
        v=A.Vector(*ax['pivot_mm']);r=A.Rotation(A.Vector(*ax['axis']),angle);return A.Placement(v-r.multVec(v),r)
    def moved(s,t):
        q=s.copy();q.Placement=t*q.Placement;return q
    def get(key,fn):
        if key not in memo:memo[key]=fn()
        return memo[key]
    def test(n,s,m,t,rs=3,rt=0):
        if not P.W.near(s,t,rs+rt+.001):return
        key=(id(s),id(t),rs,rt)
        if key in seen:return
        seen.add(key);report['pairs']+=1
        try:gap,volume=cache.check(s,t,rs,rt)
        except (AssertionError,ValueError) as e:report['errors'].append([n,m,str(e)]);return
        if gap<rs+rt-1e-4 or volume>1e-5:report['contacts'].append(dict(a=n,b=m,pose=[leg,hip,knee,ankle],gap_mm=gap,volume_mm3=volume))
    for leg in ('FrontRight','FrontLeft','RearRight','RearLeft'):
        own=[r for r in rows if r['physical_leg']==leg];code=own[0]['cad_code']
        priority=[(-15,0,0),(0,0,0),(15,0,0)]
        for hip,knee,ankle in priority+[v for v in itertools.product((-15,0,15),repeat=3) if v not in priority]:
            transforms={};t=A.Placement()
            for stage,angle in zip(('Hip','Knee','Ankle'),(hip,knee,ankle)):
                t=t*tr(next(a for a in axes if a['code']==code and a['stage']==stage),angle);transforms[stage]=t
            tt=dict(heads)
            for n,s in targets.items():
                member=membership.get(n[3:]) if n.startswith('P0_') else None
                if member and member[0]==code:
                    stage=member[1];angles=(hip,knee,ankle)[:('Hip','Knee','Ankle').index(stage)+1]
                    s=get(('material',n,angles),lambda s=s,stage=stage:moved(s,transforms[stage]))
                tt[n]=s
            for n,s in supports.items():
                tt[n]=get(('support',n,hip),lambda s=s:moved(s,transforms['Hip'])) if assigned[n]==code else s
            for r in family['hips']:
                h=hip if r['cad_code']==code else 0
                tt[r['section']]=get(('hip',r['section'],h),lambda r=r,h=h:P.wire(P.parts_at(r,h)))
            for r in own:
                s=get(('knee',r['section'],hip,knee),lambda r=r:P.wire(P.scene_parts(r,hip,knee,axes)))
                for n,t in tt.items():test(r['section'],s,n,t,3,3 if '/Hip' in n else 0)
                for n,(t,rad) in old.items():test(r['section'],s,n,t,3,rad)
            for r,q in itertools.combinations(own,2):
                test(r['section'],memo['knee',r['section'],hip,knee],q['section'],memo['knee',q['section'],hip,knee],3,3)
            report['cases']+=1
            if report['cases']%9==0 or report['contacts'] or report['errors']:
                cache.save();print('Knee actual',leg,report['cases'],report['pairs'],'contacts',len(report['contacts']),flush=True)
            if report['contacts'] or report['errors']:break
        if report['contacts'] or report['errors']:break
    cache.save();report.update(status='KNEE_PLANES_SAMPLED_MATERIAL_CLEAR_NATIVE_ROOTS_OPEN' if report['cases']==108 and not report['contacts'] and not report['errors'] else 'REJECTED_KNEE_PLANES_MATERIAL',
        source_sha256={**reader.hashes,**{p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (fp,archive,Path(__file__),Path(P.__file__),Path(__file__).with_name('exact_pair_receipts.py'))}},
        worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'outboard-knee-planes-checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','cases','pairs','contacts','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()
