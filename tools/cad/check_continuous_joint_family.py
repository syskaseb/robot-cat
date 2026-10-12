"""Check connected joint sections against actual retained material/wires/head.

No old disconnected flex or root proof is inherited for changed geometry.
New Hip/Knee native roots remain explicitly OPEN, as do servo/body joins.
"""
import itertools
import json
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import check_low_hip_loom_layout as P
import plan_current_head_wiring as H
from plan_low_power_station_mounts import allocate as station_supports
from plan_continuous_joint_family import parts_for_loom
from immutable_bounds import ImmutableBounds
from exact_pair_receipts import PairReceipts


def run():
    tick=time.monotonic();fp=P.OUT/'continuous-joint-family-plan.json'
    family=json.loads(fp.read_text())
    assert family['status']=='CONTINUOUS_JOINT_SECTIONS_MATH_SCREEN_ONLY'
    assert family['math_poses']==620 and not family['self_contacts']
    for n,h in family['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    zf=P.ROOT/'hardware/simulation/v35/inputs.zip'
    axes=json.loads(af.read_text())['axes']
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    membership={r['name']:r['stage'].split('_')[1:] for r in members if r['stage'].startswith('Motion_')}
    targets,old,archive=P.scene();reader=H.P.SavedShapes()
    heads={f'head/{y}/{p}/{n}':s for y,p in itertools.product((-15,0,15),(-10,0,5)) for n,s in H.head(reader,y,p).items()}
    pp,hw,_=station_supports(targets);targets.update(pp);targets.update(hw);targets.update(heads)
    bounds=ImmutableBounds();cache=PairReceipts(P.OUT/'continuous-joint-family-pair-cache.json',bounds.near)
    memo={};seen=set();report=dict(cases=0,pairs=0,contacts=[],errors=[],selected=False,native_changed=False,
        W5_complete=False,physical_pass=False,continuous_motion_verified=False,
        scope='12continuous Hip/Knee/interstage sections vs all891retained material/246wires, four P-station supports/hardware and52head members in9poses. 108same-leg samples; other legs nominal. New joint supports and whole servo/body joins are NOT included or qualified.')
    def get(key,fn):
        if key not in memo:memo[key]=fn()
        return memo[key]
    def tr(ax,angle):
        v=A.Vector(*ax['pivot_mm']);r=A.Rotation(A.Vector(*ax['axis']),angle)
        return A.Placement(v-r.multVec(v),r)
    def moved(s,t):
        q=s.copy();q.Placement=t*q.Placement;return q
    def test(n,s,m,t,rs=3,rt=0):
        if not bounds.near(s,t,rs+rt+.001):return
        key=(id(s),id(t),rs,rt)
        if key in seen:return
        seen.add(key);report['pairs']+=1
        try:gap,volume=cache.check(s,t,rs,rt)
        except (AssertionError,ValueError) as e:report['errors'].append([n,m,str(e)]);return
        if gap<rs+rt-1e-4 or volume>1e-5:
            report['contacts'].append(dict(a=n,b=m,pose=[leg,hip,knee,ankle],gap_mm=gap,volume_mm3=volume))
    legs=('FrontLeft','FrontRight','RearLeft','RearRight')
    schedule=[(leg,[(0,0,0)]) for leg in legs]
    priority=[(-15,0,0),(15,0,0),(0,-15,0),(0,15,0),(0,0,-15),(0,0,15)]
    schedule += [(leg,priority+[q for q in itertools.product((-15,0,15),repeat=3) if q!=(0,0,0) and q not in priority]) for leg in legs]
    for leg,poses in schedule:
        if len(poses)>1 and (report['contacts'] or report['errors']):break
        own=[r for r in family['hips'] if r['physical_leg']==leg];code=own[0]['cad_code']
        for hip,knee,ankle in poses:
            transforms={};t=A.Placement()
            for stage,angle in zip(('Hip','Knee','Ankle'),(hip,knee,ankle)):
                t=t*tr(next(a for a in axes if a['code']==code and a['stage']==stage),angle);transforms[stage]=t
            tt={}
            for n,s in targets.items():
                member=membership.get(n[3:]) if n.startswith('P0_') else None
                if member and member[0]==code:
                    stage=member[1];angles=(hip,knee,ankle)[:('Hip','Knee','Ankle').index(stage)+1]
                    s=get(('material',n,angles),lambda s=s,stage=stage:moved(s,transforms[stage]))
                tt[n]=s
            curves={}
            for r in family['hips']:
                h=hip if r['cad_code']==code else 0;k=knee if r['cad_code']==code else 0
                curves[r['loom']]=get(('loom',r['loom'],h,k),lambda r=r,h=h,k=k:P.wire(parts_for_loom(family,r['loom'],h,k,axes)))
            report['cases']+=1
            for row in own:
                n=row['loom'];s=curves[n]
                for m,t in tt.items():
                    if t.Solids:test(n,s,m,t)
                for m,(t,rad) in old.items():test(n,s,m,t,3,rad)
                for m,t in curves.items():
                    if n!=m:test(n,s,m,t,3,3)
            if report['cases']%5==0 or report['contacts'] or report['errors']:
                cache.save();print('continuous actual',leg,report['cases'],report['pairs'],'contacts',len(report['contacts']),'errors',len(report['errors']),flush=True)
            if report['contacts'] or report['errors']:break
    cache.save();report.update(status='CONTINUOUS_JOINT_SECTIONS_SAMPLED_MATERIAL_CLEAR_SUPPORTS_OPEN' if report['cases']==108 and not report['contacts'] and not report['errors'] else 'REJECTED_CONTINUOUS_JOINT_MATERIAL',
        exact_pair_receipts=dict(reused=cache.reused,computed=cache.computed),
        bounds_profile=bounds.profile(),worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={**reader.hashes,**{p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (fp,af,zf,archive,Path(__file__),
            Path(__file__).with_name('plan_continuous_joint_family.py'),Path(__file__).with_name('plan_low_power_station_mounts.py'),
            Path(__file__).with_name('exact_pair_receipts.py'),Path(__file__).with_name('immutable_bounds.py'))}})
    (P.OUT/'continuous-joint-family-checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','cases','pairs','contacts','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()
