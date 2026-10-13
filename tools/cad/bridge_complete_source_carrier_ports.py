"""One shared below-band load path; exact changed-material gate, not a waiver.

Old carriers cleared every retained target/wire; their ONLY contacts were the
36 coupled own-band pairs. Reuse that clearance only for material contained
in the old solids. Test every added solid against the same full scene, then
all revised complete physical parts against each other. No native approval.
"""
import itertools,json,time,zipfile
from pathlib import Path
import FreeCAD as A
import build_complete_source_carriers as B
P=B.P


def run():
    tick=time.monotonic();pf=P.OUT/'complete-source-carriers-material.json'
    parent=json.loads(pf.read_text());assert not parent['errors']
    for n,h in parent['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    fp=P.OUT/'leg-source-near-member-plan.json';family=json.loads(fp.read_text())
    allowed={(r['loom']+'IndependentBand'+str(h),r['physical_leg']+'SourceCarrier'+str(h))
        for r in family['hips'] for h in (-15,0,15)}
    assert len(parent['contacts'])==36 and {(q['a'],q['b']) for q in parent['contacts']}==allowed
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';axes=json.loads(af.read_text())['axes']
    with zipfile.ZipFile(P.ROOT/'hardware/simulation/v35/inputs.zip') as z:members=json.loads(z.read('geometry.json'))['components']
    reader=B.H.P.SavedShapes();targets,wires,_,_,_=B.current_scene(reader)
    cp=json.loads((P.OUT/'complete-source-carriers-plan.json').read_text())
    old,codes,recipes,roots=B.allocation(cp,family,targets,members)
    revised=dict(old);added={};newrecipes={}
    for name,r in recipes.items():
        s=old[name];pads=list(r['pads']);cuts=list(r['cuts']);rings=[]
        leg=name.removesuffix('SourceCarrier');sign=-1 if leg.startswith('Front') else 1
        for row in (v for v in family['hips'] if v['physical_leg']==leg):
            x,y,z=row['moving_anchor_rest_world_mm'];cz=z-4.5
            def V(a,b,c,d,e,f):
                lo,hi=sorted((x+sign*a,x+sign*d));return [lo,y+b,z+c,hi,y+e,z+f]
            # Lower slab overlaps the9mm post by1mm; three arrival columns
            # sit beyond the band/head, not through them. Same12land datums.
            spans=(V(4,-6.2,-12,16,6.2,-8),V(14.9,-3,-12,18.9,3,-2.5),
                V(4,4.9,-12,8,8.9,-2.5),V(4,-8.9,-12,8,-4.9,-2.5))
            for i,v in enumerate(spans):
                pads.append(dict(name=row['loom']+'BelowBandBridge'+str(i),bounds_mm=v))
                s=s.fuse(P.box(v)).removeSplitter()
            outer=V(-4.4,-4.4,-5.95,8.4,4.4,-3.05)
            inner=V(-2.8,-2.8,-6.1,6.8,2.8,-2.9)
            rings.append(dict(outer=outer,inner=inner))
            s=s.cut(P.box(outer).cut(P.box(inner))).removeSplitter()
            head=V(8,-3.2,-7.2,14.4,3.2,-1.8);cuts.append(head)
            s=s.cut(P.box(head)).removeSplitter()
        assert s.isValid() and len(s.Solids)==1 and not s.check(True),(name,'invalid/disconnected port bridge')
        delta=s.cut(old[name]).removeSplitter()
        assert delta.isNull() or delta.isValid()
        revised[name]=s;added[name]=delta;newrecipes[name]=dict(pads=pads,cuts=cuts,ring_cuts=rings)
        print('below-band bridge',name,'added mm3',round(delta.Volume,3),flush=True)
    membership={r['name']:r['stage'].split('_')[1:] for r in members if r['stage'].startswith('Motion_')}
    transforms={}
    for code in ('FL','FR','RL','RR'):
        for h,k,a in itertools.product((-15,0,15),repeat=3):
            T=A.Placement()
            for stage,angle in zip(('Hip','Knee','Ankle'),(h,k,a)):
                ax=next(r for r in axes if r['code']==code and r['stage']==stage)
                pv=A.Vector(*ax['pivot_mm']);rot=A.Rotation(A.Vector(*ax['axis']),angle)
                T=T*A.Placement(pv-rot.multVec(pv),rot);transforms[code,h,k,a,stage]=T
    def move(s,code,h,k=0,a=0,stage='Hip'):
        q=s.copy();q.Placement=transforms[code,h,k,a,stage]*q.Placement;return q
    actual=[];seen=set()
    for n,s in targets.items():
        mem=membership.get(n.removeprefix('P0_')) if n.startswith('P0_') else None
        if not mem:actual.append((n,s,0,None,None));continue
        stage=mem[1]
        for h,k,a in itertools.product((-15,0,15),repeat=3):
            key=(n,h,k if stage!='Hip' else 0,a if stage=='Ankle' else 0)
            if key in seen:continue
            seen.add(key);actual.append((str(key),move(s,mem[0],h,k,a,stage),0,mem[0],h))
    actual += [(n,s,r,None,None) for n,(s,r) in wires.items()]
    for route in family['routes']:
        code=route['source']['cad_code']
        for h,k in itertools.product((-15,0,15),repeat=2):
            s=P.wire(B.parts_for_loom(family,route['loom'],h,k,axes)+B.moved_parts(route['source_parts'],route['source'],h,k,axes))
            actual.append((route['loom']+str((h,k)),s,3,code,h))
    bounds=B.ImmutableBounds();cache=B.PairReceipts(P.OUT/'source-carrier-port-bridge-pairs.json',bounds.near)
    report=dict(pairs=0,contacts=[],errors=[])
    def test(n,s,m,t,rad=0):
        if not bounds.near(s,t,rad+.001):return
        report['pairs']+=1
        try:gap,vol=cache.check(s,t,0,rad)
        except Exception as e:report['errors'].append([n,m,str(e)]);return
        if vol>1e-5 or gap<rad-1e-4:report['contacts'].append(dict(a=n,b=m,gap_mm=gap,required_mm=rad,volume_mm3=vol))
    for n,s in added.items():
        if s.isNull():continue
        code=codes[n]
        for h in (-15,0,15):
            q=move(s,code,h)
            for m,t,rad,other,oh in actual:
                if other==code and oh!=h:continue
                test(n+str(h)+'/added',q,m,t,rad)
            print('port added material',n,h,'pairs',report['pairs'],'contacts',len(report['contacts']),flush=True)
        if report['contacts'] or report['errors']:break
    if not report['contacts'] and not report['errors']:
        whole=[(n,move(s,codes[n],h),codes[n],h) for n,s in revised.items() for h in (-15,0,15)]
        for i,(n,s,code,h) in enumerate(whole):
            for m,t,other,oh in whole[i+1:]:
                if n==m or (code==other and h!=oh):continue
                test(n+str(h),s,m+str(oh),t)
    cache.save()
    receipt=dict(**report,status='REJECTED_SOURCE_CARRIER_PORT_BRIDGES' if report['contacts'] or report['errors'] else 'SOURCE_CARRIER_PORT_BRIDGES_ACTUAL_CLEAR_NATIVE_OPEN',
        selected=False,W5_complete=False,physical_pass=False,recipes=newrecipes,
        inherited_scope='Only old carrier material vs unchanged retained scene/wires. Exact new-minus-old solids checked, complete new physical pairs checked. No old own-band contacts waived.',
        parent=pf.relative_to(P.ROOT).as_posix(),source_sha256={p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (pf,fp,Path(B.__file__),Path(__file__))},
        added_volumes_mm3={n:s.Volume for n,s in added.items()},unchanged_land_count=12,
        open=['Native histories/exports and assembly/retention trials','Knee/source and fixed roots/bodyfanouts/stock; not wholeW5'],
        worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'source-carrier-port-bridges-material.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('status','pairs','contacts','errors','worker_seconds')}),flush=True)


if __name__=='__main__':run()
