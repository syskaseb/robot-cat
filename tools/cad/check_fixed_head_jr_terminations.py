"""Only added fixed splice material/bands/sleeves against the shared scene."""
import json,time,re,itertools,zipfile
from pathlib import Path
import FreeCAD as A
import Part
import plan_fixed_head_jr_terminations as J
from exact_pair_receipts import PairReceipts
from immutable_bounds import ImmutableBounds
H,S,C,I=J.H,J.S,J.C,J.I

def run():
    tick=time.monotonic();pf=H.OUT/'fixed-head-jr-terminations-plan.json';plan=H.read(pf)
    assert plan['status']=='FIXED_JR_JOINS_SHARED_PLAN_MATERIAL_NATIVE_OPEN'
    for n,h in plan['source_sha256'].items():assert S.SHA(H.ROOT/n)==h,n
    parent=H.read(H.OUT/'fixed-head-interface-native.json')
    p,feeds,roots,meta,fork,reader,alloc,archive=I.prepare()
    pads,bands,sleeves,rows=J.allocation(feeds)
    assert pads==plan['pads'] and rows==plan['stock_rows']
    host=reader.shape(H.ROOT/parent['model'],'FixedYawCarrier')
    support=S.fuse([host]+[H.T.box(row) for row in pads.values()])
    for band in bands.values():support=support.cut(band)
    support=support.removeSplitter();assert support.isValid() and len(support.Solids)==1
    assert host.cut(support).Volume<1e-5
    added=support.cut(host);assert added.isValid()
    members={'NewSpliceSupport':added,**bands,**{n+'Sleeve':s for n,s in sleeves.items()}}
    targets,old,_=S.scene();station,hardware,bonds,_=C.D.allocate(targets)
    targets.pop('Foundation',None);targets.update({**station,**hardware,**bonds})
    retired={n for n in old if re.search(r'(?:^|/)(?:XB22|XB23|XS23)(?:/|_|$)',n)}
    bounds=ImmutableBounds();cache=PairReceipts(H.OUT/'fixed-head-jr-termination-pairs.json',bounds.near)
    report=dict(pairs=0,contacts=[],errors=[],selected=False,physical_pass=False,head_poses=0,leg_poses=0)
    def test(n,s,m,t,r=0,pose=None):
        if not bounds.near(s,t,r+.001):return
        report['pairs']+=1
        try:d,v=cache.check(s,t,0,r)
        except (AssertionError,ValueError) as exc:report['errors'].append([n,m,str(exc)]);return
        if d<r-1e-4 or v>1e-5:report['contacts'].append(dict(a=n,b=m,pose=pose,gap_mm=d,volume_mm3=v))
    for n,s in members.items():
        for m,t in targets.items():
            if t.Solids:test(n,s,m,t)
        for m,(t,r) in old.items():
            if m not in retired:test(n,s,m,t,r)
        for m,t in roots.items():test(n,s,m,t)
        for m,es in feeds.items():
            if n==m+'Sleeve':continue  # Exactly this conductor's OWN insulation envelope.
            test(n,s,m,Part.Wire(es),1.05)
        if n!='NewSpliceSupport':test(n,s,'ChangedFixedYawCarrier',support)
    for n,s in members.items():
        for m,t in members.items():
            if n<m:test(n,s,m,t)
    print('Added splice/static',report['pairs'],len(report['contacts']),len(report['errors']),flush=True)
    qualified,_=C.F.allocation(60)
    for yaw,pitch in itertools.product((-15,0,15),(-10,0,5)):
        head=H.head(reader,yaw,pitch);head['Fork']=H.moved(fork,yaw)
        report['head_poses']+=1
        for n,s in members.items():
            for m,t in head.items():test(n,s,'head/'+m,t,pose=[yaw,pitch])
            for m,t in roots.items():
                if m.startswith('Moving'):test(n,s,m,H.moved(t,yaw),pose=[yaw,pitch])
            if pitch==0:
                pose=next(row for row in p['poses'] if row['yaw']==yaw)
                test(n,s,'FactoryFreeUncut250',H.T.wire(pose['parts']),I.Q.RESERVE,pose=[yaw,pitch])
                for m,(t,r) in qualified.items():
                    if m.startswith('Qualified'):test(n,s,m,H.moved(t,yaw),r,pose=[yaw,pitch])
    af=H.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';zf=H.ROOT/'hardware/simulation/v35/inputs.zip'
    axes=H.read(af)['axes']
    with zipfile.ZipFile(zf) as z:membership=json.loads(z.read('geometry.json'))['components']
    groups={c:{stage:[] for stage in ('Hip','Knee','Ankle')} for c in ('FL','FR','RL','RR')}
    for row in membership:
        if row['stage'].startswith('Motion_'):
            _,code,stage=row['stage'].split('_');groups[code][stage].append('P0_'+row['name'])
    memo={}
    for code,stages in groups.items():
        for angles in itertools.product((-15,0,15),repeat=3):
            tr=A.Placement();report['leg_poses']+=1
            for idx,(stage,angle) in enumerate(zip(('Hip','Knee','Ankle'),angles)):
                ax=next(a for a in axes if a['code']==code and a['stage']==stage)
                pivot=A.Vector(*ax['pivot_mm']);rot=A.Rotation(A.Vector(*ax['axis']),angle)
                tr=tr*A.Placement(pivot-rot.multVec(pivot),rot)
                for name in stages[stage]:
                    key=(name,angles[:idx+1])
                    if key not in memo:
                        s=targets[name].copy();s.Placement=tr*s.Placement;memo[key]=s
                    for n,s in members.items():test(n,s,name,memo[key],pose=[code,*angles])
    report.update(status='FIXED_JR_JOINS_SHARED_MATERIAL_CLEAR_NATIVE_OPEN' if not report['contacts'] and not report['errors'] else 'REJECTED_FIXED_JR_JOINS_MATERIAL',
        unchanged_parent_material_retained=True,continuous_sweep_verified=False,
        source_sha256={**plan['source_sha256'],pf.relative_to(H.ROOT).as_posix():S.SHA(pf),
            **{f.relative_to(H.ROOT).as_posix():S.SHA(f) for f in (Path(__file__),af,zf)}},
        worker_seconds=round(time.monotonic()-tick,3))
    H.save('fixed-head-jr-terminations-material.json',report);cache.save()
    print(json.dumps({k:report[k] for k in ('status','head_poses','leg_poses','pairs','contacts','errors','worker_seconds')}),flush=True)

if __name__=='__main__':run()
