"""Full12 source-to-body-grip sections against the current retained assembly.

Current fixed-head selection and all five station supports are included.
This does not qualify new joint roots, body fans, stock or continuous motion.
"""
import itertools,json,re,time,zipfile,sys
from pathlib import Path
import FreeCAD as A
import check_low_hip_loom_layout as P
import plan_current_head_wiring as H
from plan_circular_source_leg_looms import parts_for_loom,moved_parts
from immutable_bounds import ImmutableBounds
from exact_pair_receipts import PairReceipts
from plan_fixed_underneck_rounds import RESERVE


def run():
    tick=time.monotonic();fp=P.OUT/(sys.argv[1] if len(sys.argv)>1 else 'leg-source-current-plan.json')
    family=json.loads(fp.read_text())
    assert family['status'] in ('LEG_SOURCE_CURRENT_MATH_CLEAR_MATERIAL_OPEN','LEG_SOURCE_FIRST_MATH_CLEAR_MATERIAL_OPEN')
    assert len(family['routes'])==12 and not family['errors']
    for n,h in family['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    zf=P.ROOT/'hardware/simulation/v35/inputs.zip'
    axes=json.loads(af.read_text())['axes']
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    membership={r['name']:r['stage'].split('_')[1:] for r in members if r['stage'].startswith('Motion_')}
    targets,old,archive=P.scene();reader=H.P.SavedShapes()
    retired=[n for n in old if re.search(r'(?:^|/)(?:XB22|XB23|XS23)(?:/|_|$)',n)]
    for n in retired:old.pop(n)
    H.HEAD=H.OUT/'HeadNeckFixedJoined.FCStd'
    heads={};rest=H.head(reader,0,0)
    for n,s in rest.items():
        poses={(y if n not in H.FIXED else 0,p if n in H.PITCH else 0) for y,p in itertools.product((-15,0,15),(-10,0,5))}
        for y,p in poses:heads[f'head/{y}/{p}/{n}']=H.moved(s,y,p)
    # These stored references are local to CP2Head. Apply its verified SHIFT
    # once, then only the appropriate yaw motion; none is pitch-owned.
    interfaces={}
    for n in reader.doc(H.HEAD):
        if not n.startswith('Interface_') or n=='Interface_FactoryFreeUncut250':continue
        s=reader.shape(H.HEAD,n);s.translate(H.SHIFT)
        rad=1.05 if n in ('Interface_XB22','Interface_XB23','Interface_XS23') else 0
        for yaw in ((-15,0,15) if n.startswith(('Interface_Moving','Interface_Qualified')) else (0,)):
            interfaces[f'current/{yaw}/{n}']=(H.moved(s,yaw),rad)
    ff=H.OUT/'fixed-underneck-rounds-plan.json';factory=json.loads(ff.read_text())
    for r in factory['poses']:
        if r['yaw'] in (-15,0,15):
            interfaces['factory/'+str(r['yaw'])]=(H.T.wire(r['parts']),RESERVE)
    sf=P.OUT/'station-frames-native.json';stations=json.loads(sf.read_text());sm=P.ROOT/stations['native']
    assert P.SHA(sm)==stations['native_sha256']
    assert stations['editable_parts']==5 and stations['relocated_reopen']
    targets.pop('Foundation')
    for n in ('FLStationFrame','FRStationFrame','RLStationFrame','RRStationFrame','FoundationStationSupports'):
        targets[n]=reader.shape(sm,n)
    for n in reader.doc(sm):
        if n.startswith('Ref_'):targets[n[4:]]=reader.shape(sm,n)
    targets.update(heads)
    for n,(s,r) in interfaces.items():
        if r:old[n]=(s,r)
        else:targets[n]=s
    bounds=ImmutableBounds();cache=PairReceipts(P.OUT/'current-leg-source-pair-cache.json',bounds.near)
    memo={};seen=set();report=dict(cases=0,pairs=0,contacts=[],errors=[],selected=False,native_changed=False,
        W5_complete=False,physical_pass=False,continuous_motion_verified=False,
        retired_pitch_wire_labels=retired,retained_body_solids=len(targets)-len(heads),
        current_head_members=len(heads),current_interfaces=len(interfaces),retained_wire_envelopes=len(old),
        scope='All12 complete source-to-fixed-body-grip sections. Actual retained material/current five stations/current selected52-part head in9poses and complete current fixed-head interfaces.108same-leg samples; other legs nominal. No new joint roots/fullbody fans/stock qualification.')
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
    sources={r['loom']:r for r in family['routes']}
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
                route=sources[r['loom']]
                curves[r['loom']]=get(('loom',r['loom'],h,k),lambda r=r,h=h,k=k,route=route:P.wire(
                    parts_for_loom(family,r['loom'],h,k,axes)+moved_parts(route['source_parts'],route['source'],h,k,axes)))
            report['cases']+=1
            for row in own:
                n=row['loom'];s=curves[n]
                for m,t in tt.items():
                    if t.Solids:test(n,s,m,t)
                for m,(t,rad) in old.items():test(n,s,m,t,3,rad)
                for m,t in curves.items():
                    if n!=m:test(n,s,m,t,3,3)
            if report['cases']%5==0 or report['contacts'] or report['errors']:
                cache.save();print('current leg source',leg,report['cases'],report['pairs'],'contacts',len(report['contacts']),'errors',len(report['errors']),flush=True)
                (P.OUT/'current-leg-source-progress.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
            if report['contacts'] or report['errors']:break
    cache.save();report.update(status='CURRENT_LEG_SOURCE_SAMPLED_MATERIAL_CLEAR_ROOTS_BODY_OPEN' if report['cases']==108 and not report['contacts'] and not report['errors'] else 'REJECTED_CURRENT_LEG_SOURCE_MATERIAL',
        exact_pair_receipts=dict(reused=cache.reused,computed=cache.computed),bounds_profile=bounds.profile(),worker_seconds=round(time.monotonic()-tick,3),
        source_sha256={**reader.hashes,**{p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (fp,af,zf,archive,ff,sf,Path(__file__),
            Path(__file__).with_name('plan_circular_source_leg_looms.py'),
            Path(__file__).with_name('exact_pair_receipts.py'),Path(__file__).with_name('immutable_bounds.py'))}})
    dest='current-leg-source-checks.json' if len(sys.argv)==1 else fp.stem+'-material.json'
    (P.OUT/dest).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('status','cases','pairs','contacts','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()
