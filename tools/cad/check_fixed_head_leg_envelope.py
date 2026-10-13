"""Changed whole neck interface vs all retained P0 leg sample combinations.

Only changed interfaces: retained mechanics are not needlessly re-audited.
All three head-yaw positions are combined with each of108leg samples. Exact
valid geometry, no bbox contact claim or transfer of a rejected cable family.
"""
import itertools,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import Part
import plan_fixed_head_feed_interface as I
from exact_pair_receipts import PairReceipts
from immutable_bounds import ImmutableBounds
H,S,C,Q=I.H,I.S,I.C,I.Q

def run():
    tick=time.monotonic();gatefile=H.OUT/'fixed-head-interface-material.json';gate=H.read(gatefile)
    assert gate['status']=='SHARED_FIXED_HEAD_INTERFACE_SAMPLED_CLEAR_NATIVE_OPEN'
    for n,h in gate['source_sha256'].items():assert S.SHA(H.ROOT/n)==h,n
    p,feeds,roots,meta,fork,reader,allocation,archive=I.prepare()
    targets,_,_=S.scene();x,z=p['fixed_receiver_XZ_mm'];y=p['fixed_receiver_Y_mm']
    fixed={n:(s,0) for n,s in roots.items() if not n.startswith('Moving')}
    fixed.update({n:(Part.Wire(es),1.05) for n,es in feeds.items()})
    fixed['FixedJR']=(H.T.box([x-6,y-30,z-5,x+6,y,z+5]),0)
    moving={}
    for yaw in (-15,0,15):
        row=next(q for q in p['poses'] if q['yaw']==yaw)
        moving['FactoryYaw'+str(yaw)]=(H.T.wire(row['parts']),Q.RESERVE)
        moving.update({n+'Yaw'+str(yaw):(H.moved(s,yaw),0) for n,s in roots.items() if n.startswith('Moving')})
    candidates={**fixed,**moving}
    af=H.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    zf=H.ROOT/'hardware/simulation/v35/inputs.zip'
    axes=H.read(af)['axes'];groups={c:{s:[] for s in ('Hip','Knee','Ankle')} for c in ('FL','FR','RL','RR')}
    with zipfile.ZipFile(zf) as zfile:members=json.loads(zfile.read('geometry.json'))['components']
    for r in members:
        if r['stage'].startswith('Motion_'):
            _,code,stage=r['stage'].split('_');groups[code][stage].append('P0_'+r['name'])
    bounds=ImmutableBounds();cache=PairReceipts(H.OUT/'fixed-head-leg-pairs.json',bounds.near)
    memo={};seen=set();report=dict(poses=0,pairs=0,contacts=[],errors=[],selected=False,physical_pass=False)
    for code,stages in groups.items():
        axis={a['stage']:a for a in axes if a['code']==code}
        for angles in itertools.product((-15,0,15),repeat=3):
            transform=A.Placement();report['poses']+=1
            for idx,(stage,angle) in enumerate(zip(('Hip','Knee','Ankle'),angles)):
                a=axis[stage];v=A.Vector(*a['pivot_mm']);rotation=A.Rotation(A.Vector(*a['axis']),angle)
                transform=transform*A.Placement(v-rotation.multVec(v),rotation)
                for name in stages[stage]:
                    key=(name,angles[:idx+1])
                    if key not in memo:
                        s=targets[name].copy();s.Placement=transform*s.Placement;memo[key]=s
                    s=memo[key]
                    for n,(t,r) in candidates.items():
                        pair=(key,n)
                        if pair in seen or not bounds.near(s,t,r+.001):continue
                        seen.add(pair);report['pairs']+=1
                        try:gap,vol=cache.check(s,t,0,r)
                        except (AssertionError,ValueError) as exc:report['errors'].append([name,n,str(exc)]);continue
                        if gap<r-1e-4 or vol>1e-5:
                            report['contacts'].append(dict(leg=code,angles=angles,a=name,b=n,gap_mm=gap,volume_mm3=vol))
            if report['contacts'] or report['errors']:break
        cache.save();print(code,report['poses'],report['pairs'],len(report['contacts']),flush=True)
        if report['contacts'] or report['errors']:break
    report.update(status='REJECTED_CHANGED_HEAD_LEG_INTERFACE' if report['contacts'] or report['errors'] else 'CHANGED_HEAD_LEG_INTERFACE_SAMPLED_CLEAR',
        head_yaw_cases=3,continuous_sweep_verified=False,W5_complete=False,
        source_sha256={**gate['source_sha256'],gatefile.relative_to(H.ROOT).as_posix():S.SHA(gatefile),
            **{f.relative_to(H.ROOT).as_posix():S.SHA(f) for f in (Path(__file__),af,zf)}},
        worker_seconds=round(time.monotonic()-tick,3))
    H.save('fixed-head-leg-material.json',report)
    print(json.dumps({k:report[k] for k in ('status','poses','pairs','contacts','errors','worker_seconds')}),flush=True)

if __name__=='__main__':run()
