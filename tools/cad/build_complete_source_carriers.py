"""Four actual rooted Hip carriers after whole source-space planning.

Only changed carriers/bonds/12ties are checked. Cable, fixed roots, Knee
restraints, extensions, stock and whole W5 remain unselected/open.
"""
import itertools,json,re,time,zipfile,shutil,tempfile
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
import check_low_hip_loom_layout as P
import plan_current_head_wiring as H
from plan_continuous_joint_family import parts_for_loom
from plan_current_rigid_factory_joins import moved_parts
from immutable_bounds import ImmutableBounds
from exact_pair_receipts import PairReceipts
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect
from build_u1_grouped_grips import validate


def current_scene(reader):
    targets,wires,archive=P.scene()
    for n in list(wires):
        if re.search(r'(?:^|/)(?:XB22|XB23|XS23)(?:/|_|$)',n):wires.pop(n)
    sf=P.OUT/'StationFramesCurrent.FCStd';targets.pop('Foundation')
    for n in ('FLStationFrame','FRStationFrame','RLStationFrame','RRStationFrame','FoundationStationSupports'):targets[n]=reader.shape(sf,n)
    for n in reader.doc(sf):
        if n.startswith('Ref_'):targets[n[4:]]=reader.shape(sf,n)
    H.HEAD=H.OUT/'HeadNeckFixedJoined.FCStd'
    for n,s in H.head(reader,0,0).items():
        for y,p in {(y if n not in H.FIXED else 0,p if n in H.PITCH else 0) for y,p in itertools.product((-15,0,15),(-10,0,5))}:targets[f'head/{y}/{p}/{n}']=H.moved(s,y,p)
    for n in reader.doc(H.HEAD):
        if not n.startswith('Interface_') or n=='Interface_FactoryFreeUncut250':continue
        s=reader.shape(H.HEAD,n);s.translate(H.SHIFT)
        for y in ((-15,0,15) if n.startswith(('Interface_Moving','Interface_Qualified')) else (0,)):
            if n in ('Interface_XB22','Interface_XB23','Interface_XS23'):wires[f'headwire/{y}/{n}']=(H.moved(s,y),1.05)
            else:targets[f'headref/{y}/{n}']=H.moved(s,y)
    ff=H.OUT/'fixed-underneck-rounds-plan.json'
    from plan_fixed_underneck_rounds import RESERVE
    for r in json.loads(ff.read_text())['poses']:
        if r['yaw'] in (-15,0,15):wires['factory/'+str(r['yaw'])]=(P.wire(r['parts']),RESERVE)
    return targets,wires,archive,sf,ff


def allocation(plan,family,targets,members):
    shapes={};codes={};recipes={};bond_contacts=[]
    for root in plan['roots']:
        leg=root['leg'];code=root['cad_code'];side=1 if leg.endswith('Left') else -1;sign=-1 if leg.startswith('Front') else 1
        name=leg+'SourceCarrier';bounds=root['bond_bounds_world_mm'];x,y,z,X,Y,Z=bounds
        pads=[dict(name='CaseCap',bounds_mm=[x,y,Z,X,Y,Z+4])];cuts=[]
        for path in root['paths']:
            for i,(a,b) in enumerate(zip(path['points_mm'],path['points_mm'][1:])):
                v=[min(a[j],b[j])-h for j,h in enumerate((2,3,2))]+[max(a[j],b[j])+h for j,h in enumerate((2,3,2))]
                if v not in [r['bounds_mm'] for r in pads]:pads.append(dict(name=path['loom']+'Branch'+str(i),bounds_mm=v))
        for r in (r for r in family['hips'] if r['physical_leg']==leg):
            xx,yy,zz=r['moving_anchor_rest_world_mm'];cz=zz-4.5
            def B(a,b,c,d,e,f):
                lo,hi=sorted((xx+sign*a,xx+sign*d));return [lo,yy+b,c,hi,yy+e,f]
            pads.append(dict(name=r['loom']+'NineMmLand',bounds_mm=B(4,-3,zz-9,8,3,zz)))
            # Seat one cuttable purchased band in the back of the post;
            # post still has3mm of depth. No wire bore through the jacket.
            cuts.append(B(7,-3.1,cz-1.4,8.3,3.1,cz+1.4))
            outer=P.box(B(-4.2,-4.2,cz-1.25,8.2,4.2,cz+1.25))
            inner=P.box(B(-3,-3,cz-1.4,7,3,cz+1.4))
            band=outer.cut(inner);head=P.box(B(8.2,-3,cz-2.5,14.2,3,cz+2.5))
            tie=band.fuse(head).removeSplitter();assert tie.isValid() and len(tie.Solids)==1
            shapes[r['loom']+'IndependentBand']=tie;codes[r['loom']+'IndependentBand']=code
        # Refine EACH additive union, just as native Pad.Refine does. Keeping
        # all intermediate seams until the last operation made the unchanged
        # RearLeft union unorientable. Per-union refine preserves its volume
        # to2e-11mm3 and produces one valid solid through all three cuts.
        body=P.box(pads[0]['bounds_mm'])
        for row in pads[1:]:body=body.fuse(P.box(row['bounds_mm'])).removeSplitter()
        for cut in cuts:body=body.cut(P.box(cut))
        body=body.removeSplitter()
        valid=body.isValid()
        try:bop=[str(e) for e in (body.check(True) or [])]
        except ValueError as e:bop=[str(e)]
        if not valid or len(body.Solids)!=1 or bop:
            diagnostic=dict(status='REJECTED_SOURCE_CARRIER_ALLOCATION',part=name,valid=valid,
                solid_count=len(body.Solids),bop=bop,pads=pads,cuts=cuts,
                components=[dict(volume_mm3=s.Volume,bounds_mm=[s.BoundBox.XMin,s.BoundBox.YMin,s.BoundBox.ZMin,s.BoundBox.XMax,s.BoundBox.YMax,s.BoundBox.ZMax]) for s in body.Solids],
                selected=False,W5_complete=False,physical_pass=False)
            (P.OUT/'complete-source-carriers-allocation.json').write_text(json.dumps(diagnostic,indent=2)+'\n',encoding='utf-8')
            raise AssertionError((name,valid,len(body.Solids),bop))
        bond=P.box(bounds)
        for m in members:
            if m['stage']=='Motion_'+code+'_Hip' and m['label'].startswith(('ZK_','SG-ZIJI_','XG-ZIJI_')):bond=bond.cut(targets['P0_'+m['name']])
        bond=bond.removeSplitter();assert bond.isValid() and len(bond.Solids)==1
        cap=P.box(pads[0]['bounds_mm']);assert cap.distToShape(bond)[0]<1e-6
        case=targets['P0_'+root['case']];assert bond.distToShape(case)[0]<1e-6 and bond.common(case).Volume<1e-6
        bond_contacts.append(dict(leg=leg,case=root['case'],cap_bond_gap_mm=cap.distToShape(bond)[0],bond_case_gap_mm=bond.distToShape(case)[0]))
        shapes[name]=body;codes[name]=code;shapes[leg+'SourceCaseBond']=bond;codes[leg+'SourceCaseBond']=code
        recipes[name]=dict(pads=pads,cuts=cuts)
    return shapes,codes,recipes,bond_contacts


def run():
    tick=time.monotonic();fp=P.OUT/'leg-source-near-member-plan.json';pf=P.OUT/'complete-source-carriers-plan.json'
    family=json.loads(fp.read_text());plan=json.loads(pf.read_text())
    assert plan['status']=='COMPLETE_SOURCE_CARRIERS_RESERVED_ACTUAL_NATIVE_OPEN'
    for n,h in plan['source_sha256'].items():assert P.SHA(P.ROOT/n)==h,n
    assert len(plan['roots'])==4 and all(p['points_mm'] for r in plan['roots'] for p in r['paths'])
    af=P.ROOT/'hardware/simulation/p0/e6-leg-compatibility.json';zf=P.ROOT/'hardware/simulation/v35/inputs.zip';axes=json.loads(af.read_text())['axes']
    with zipfile.ZipFile(zf) as z:members=json.loads(z.read('geometry.json'))['components']
    membership={r['name']:r['stage'].split('_')[1:] for r in members if r['stage'].startswith('Motion_')}
    reader=H.P.SavedShapes();targets,wires,archive,sf,ff=current_scene(reader)
    shapes,codes,recipe,contacts=allocation(plan,family,targets,members)
    transforms={}
    for code in ('FL','FR','RL','RR'):
        for h,k,a in itertools.product((-15,0,15),repeat=3):
            T=A.Placement()
            for stage,angle in zip(('Hip','Knee','Ankle'),(h,k,a)):
                ax=next(r for r in axes if r['code']==code and r['stage']==stage);pv=A.Vector(*ax['pivot_mm']);rot=A.Rotation(A.Vector(*ax['axis']),angle)
                T=T*A.Placement(pv-rot.multVec(pv),rot);transforms[code,h,k,a,stage]=T
    def moved(s,T):q=s.copy();q.Placement=T*q.Placement;return q
    actual=[];memo={}
    for n,s in targets.items():
        mem=membership.get(n.removeprefix('P0_')) if n.startswith('P0_') else None
        if not mem:actual.append((n,s,None,None));continue
        stage=mem[1]
        for h,k,a in itertools.product((-15,0,15),repeat=3):
            key=(n,h,k if stage!='Hip' else 0,a if stage=='Ankle' else 0)
            if key in memo:continue
            memo[key]=moved(s,transforms[mem[0],h,k,a,stage]);actual.append((n+str(key[1:]),memo[key],mem[0],h))
    actual_wires=[(n,s,r,None,None) for n,(s,r) in wires.items()]
    for route in family['routes']:
        code=route['source']['cad_code']
        for h,k in itertools.product((-15,0,15),repeat=2):
            q=P.wire(parts_for_loom(family,route['loom'],h,k,axes)+moved_parts(route['source_parts'],route['source'],h,k,axes))
            actual_wires.append((route['loom']+str((h,k)),q,3,code,h))
    new=[]
    for n,s in shapes.items():
        for h in (-15,0,15):new.append((n,moved(s,transforms[codes[n],h,0,0,'Hip']),codes[n],h))
    bounds=ImmutableBounds();cache=PairReceipts(P.OUT/'complete-source-carriers-pair-cache.json',bounds.near);report=dict(pairs=0,contacts=[],errors=[])
    inputs=(fp,pf,af,zf,archive,sf,H.HEAD,ff,Path(__file__),
        Path(P.__file__),Path(H.__file__),
        Path(__file__).with_name('exact_pair_receipts.py'),
        Path(__file__).with_name('immutable_bounds.py'))
    pins={p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in inputs}
    gf=P.OUT/'complete-source-carriers-material.json'
    def test(n,s,m,t,rad=0):
        if not bounds.near(s,t,rad+.001):return
        report['pairs']+=1
        try:gap,vol=cache.check(s,t,0,rad)
        except Exception as e:report['errors'].append([n,m,str(e)]);return
        if vol>1e-5 or gap<rad-1e-4:report['contacts'].append(dict(a=n,b=m,gap_mm=gap,required_mm=rad,volume_mm3=vol))
    for n,s,code,h in new:
        for m,t,other,oh in actual:
            if other==code and oh!=h:continue
            test(n+str(h),s,m,t)
        for m,t,r,other,oh in actual_wires:
            if other==code and oh!=h:continue
            test(n+str(h),s,m,t,r)
        print('actual carrier',n,h,'pairs',report['pairs'],'contacts',len(report['contacts']),flush=True)
        cache.save()
        gf.write_text(json.dumps(dict(**report,status='PARTIAL_COMPLETE_SOURCE_CARRIERS_ACTUAL_MATERIAL',
            last_item=n,last_Hip_deg=h,selected=False,W5_complete=False,physical_pass=False,
            source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3)),indent=2)+'\n',encoding='utf-8')
        if report['contacts'] or report['errors']:break
    if not report['contacts'] and not report['errors']:
        for i,(n,s,code,h) in enumerate(new):
            for m,t,other,oh in new[i+1:]:
                if n==m or (code==other and h!=oh):continue
                test(n+str(h),s,m+str(oh),t)
    cache.save()
    gate=dict(**report,status='REJECTED_COMPLETE_SOURCE_CARRIERS_ACTUAL_MATERIAL' if report['contacts'] or report['errors'] else 'FOUR_SOURCE_CARRIERS_ACTUAL_CLEAR_NATIVE_PENDING',
        scope='Changed4Hipcarriers/4casebonds/12independentties vs all retained body/currenthead/stations/wires and complete12sourcefamilies. OwnHip coupled; other legs sampled independently. No continuous sweep/strength/W5 claim.',
        rooted_contacts=contacts,beam_depth_project_mm=4,tie_heads_project_mm=[6,6,5],
        selected=False,W5_complete=False,physical_pass=False,source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3))
    gf.write_text(json.dumps(gate,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:gate[k] for k in ('status','pairs','contacts','errors','worker_seconds')}),flush=True)
    if report['contacts'] or report['errors']:return
    # Only the actual positive material gate permits native history/export.
    native(recipe,shapes,codes,gate,gf,tick)


def native(recipe,shapes,codes,gate,gf,tick):
    model=P.OUT/'CompleteSourceCarriers.FCStd';assert not model.exists(),'Receive existing native instead of overwrite'
    d=A.newDocument('CompleteSourceCarriers');par=d.addObject('App::VarSet','CarrierParameters')
    par.addProperty('App::PropertyLength','BackboneDepth');par.BackboneDepth=4
    bodies=[];volumes={};sketches=0
    for name,r in recipe.items():
        b=d.addObject('PartDesign::Body',name);bodies.append(b)
        for i,row in enumerate(r['pads']):
            x,y,z,X,Y,Z=row['bounds_mm'];old=b.Tip;sk=sketch(b,name+'PadPlan'+str(i),z);rect(sk,x,y,X-x,Y-y);sketches+=1
            pad=b.newObject('PartDesign::Pad',name+'Pad'+str(i));pad.Profile=sk
            if old:pad.BaseFeature=old
            if row['name'].endswith('NineMmLand'):pad.Length=Z-z
            else:pad.setExpression('Length',f'{Z-z-4} mm + CarrierParameters.BackboneDepth')
            pad.Refine=True;b.Tip=pad;d.recompute();sk.Visibility=False
            if old:old.Visibility=False
        for i,v in enumerate(r['cuts']):
            x,y,z,X,Y,Z=v;old=b.Tip;sk=sketch(b,name+'BandPlan'+str(i),Z);rect(sk,x,y,X-x,Y-y);sketches+=1
            cut=b.newObject('PartDesign::Pocket',name+'BandSeat'+str(i));cut.Profile=sk;cut.BaseFeature=old;cut.Length=Z-z;cut.Refine=True;b.Tip=cut;d.recompute();old.Visibility=False;sk.Visibility=False
        validate(b);expected=shapes[name];assert b.Shape.cut(expected).Volume<1e-5 and expected.cut(b.Shape).Volume<1e-5,name
        volumes[name]=b.Shape.Volume;print('native source carrier',name,flush=True)
    for n,s in shapes.items():
        if n in recipe:continue
        o=d.addObject('Part::Feature','Ref_'+n);o.Shape=s;o.addProperty('App::PropertyString','Readiness');o.Readiness='Provisional physical bond/tie; not printed and not manufacturer dimensions'
    par.BackboneDepth=4.2;d.recompute()
    for b in bodies:validate(b);assert b.Shape.Volume>volumes[b.Name],b.Name
    par.BackboneDepth=4;d.recompute()
    for b in bodies:validate(b);assert abs(b.Shape.Volume-volumes[b.Name])<1e-5
    d.saveAs(str(model));A.closeDocument(d.Name);exports=[]
    with tempfile.TemporaryDirectory(prefix='robot-cat-source-carriers-') as td:
        f=Path(td)/model.name;shutil.copy2(model,f);d=A.openDocument(str(f));d.recompute()
        for name,v in volumes.items():
            b=d.getObject(name);validate(b);assert abs(b.Shape.Volume-v)<1e-5
            s=b.Shape.copy();bb=s.BoundBox;s.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
            bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength];assert max(size)+10<256
            f=P.OUT/(name+'_x1.stl');mesh.write(str(f));exports.append(dict(part=name,path=f.relative_to(P.ROOT).as_posix(),sha256=P.SHA(f),quantity=1,size_mm=size,brim_each_mm=5))
        A.closeDocument(d.Name)
    receipt=dict(status='FOUR_HIP_SOURCE_CARRIERS_NATIVE_PREPARED_W5_OPEN',selected=False,W5_complete=False,physical_pass=False,
        native=model.relative_to(P.ROOT).as_posix(),native_sha256=P.SHA(model),exports=exports,fully_constrained_sketches=sketches,
        parameter_restore_mm=[4,4.2,4],relocated_reopen=True,hardware_candidate={'T18I_independent_bands':12,'provisional_case_bonds':4},
        assembly=['No energy sources. Bench-fit existing case patch; do not drill motor or use shaft/PCB/seam as root.',
            'Bond prototype cap to exposed case patch only after compatible adhesive trial and cure in supported jig.',
            'Fit all three9mm insulated lands and independent cuttable ties. No cable force through electrical terminal.',
            'For deep repair support wires first, cut dedicated ties, remove cap/bond without prying on PCB; no quick-release or physical strength approval.'],
        gates=['Case/PETG bond peel/load/creep and long-carrier stiffness/coupon remain phase2 gates',
            'Source-owned splices, Knee/fixed roots/body fans and complete stock/selection still OPEN',
            'Print orientation/support and slicer approval not performed'],
        source_sha256={gf.relative_to(P.ROOT).as_posix():P.SHA(gf),Path(__file__).relative_to(P.ROOT).as_posix():P.SHA(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'complete-source-carriers-native.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('status','fully_constrained_sketches','worker_seconds')}),flush=True)


if __name__=='__main__':run()
