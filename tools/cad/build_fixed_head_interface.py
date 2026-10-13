"""One editable head interface, only after the complete shared material gate.

Retained mechanical bases are explicitly inherited, self-contained shapes.
Every new support/passage is a constrained native Pad/Pocket, not a mesh.
This candidate does not select or silently replace the approved prototype.
"""
import json,time,tempfile,shutil
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
import plan_fixed_head_feed_interface as I
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect
from build_u1_grouped_grips import validate
H,S,C=I.H,I.S,I.C
V=A.Vector
MODEL=H.OUT/'FixedHeadInterface.FCStd'

def strap_boxes(x,y,bottom,top,halfwidth,head_side=1):
    a,b=x-halfwidth,x+halfwidth;lo,hi=a-1.2,b+1.2
    return [[lo,y-1.25,bottom-1.2,a,y+1.25,top+1.2],
            [b,y-1.25,bottom-1.2,hi,y+1.25,top+1.2],
            [a,y-1.25,bottom-1.2,b,y+1.25,bottom],
            [a,y-1.25,top,b,y+1.25,top+1.2],
            [x-3,y+head_side*3-3,top+1.2,x+3,y+head_side*3+3,top+6.2]]

def band_boxes(x,y):
    boxes={
      'MovingFactoryBand':[
        [-180.2,50,151.4,-179,52.5,155.6],[-173,50,151.4,-171.8,52.5,155.6],
        [-179,50,151.4,-173,52.5,152.6],[-179,50,154.4,-173,52.5,155.6],
        [-185.2,48.25,150.5,-180.2,54.25,156.5]],
      'FixedJRBand':[
        [x-6.25,y-31.2,70.8,x-3.75,y-30,86.2],
        [x-6.25,y,70.8,x-3.75,y+1.2,86.2],
        [x-6.25,y-30,70.8,x-3.75,y,72],
        [x-6.25,y-30,85,x-3.75,y,86.2],
        [x-8,y-18,86.2,x-2,y-12,91.2]]}
    for n,yy,z,xx,sx in [('XB23',68,51,-247,-216),('XB22',78,48,-227,-169),('XS23',88,45,-237,-187)]:
        north=[]
        for row in strap_boxes(0,0,40,z+1.25,1.25):
            s=H.T.box(row);s.rotate(V(),V(0,0,1),90);s.translate(V(sx,yy,0));north.append(H.bb(s))
        boxes[n+'NorthBand']=north
        boxes[n+'FrontBand']=strap_boxes(xx,0,37,z+1.25,1.25)
    boxes['SourceLandBand']=strap_boxes(x,y-34.5,75,81.25,3.85,head_side=-1)
    boxes['FactoryLandBand']=strap_boxes(x,y+4.5,75,81.1,1.95)
    return boxes

def add_box(d,b,n,row,pocket=False,expression=None):
    x,y,z,X,Y,Z=row;old=b.Tip
    sk=sketch(b,n+'Plan',Z if pocket else z);rect(sk,x,y,X-x,Y-y)
    f=b.newObject('PartDesign::Pocket' if pocket else 'PartDesign::Pad',n)
    f.Profile=sk
    if old:f.BaseFeature=old
    if expression:f.setExpression('Length',expression)
    else:f.Length=Z-z
    f.Refine=True;b.Tip=f;d.recompute();sk.Visibility=False
    if old:old.Visibility=False
    assert not f.State or 'Invalid' not in f.State,(n,f.State)
    return f

def run():
    tick=time.monotonic();gatefile=H.OUT/'fixed-head-interface-material.json';gate=H.read(gatefile)
    assert gate['status']=='SHARED_FIXED_HEAD_INTERFACE_SAMPLED_CLEAR_NATIVE_OPEN'
    assert gate['poses']==9 and not gate['contacts'] and not gate['errors']
    for n,h in gate['source_sha256'].items():assert S.SHA(H.ROOT/n)==h,n
    legfile=H.OUT/'fixed-head-leg-material.json';leg=H.read(legfile)
    assert leg['status']=='CHANGED_HEAD_LEG_INTERFACE_SAMPLED_CLEAR' and leg['poses']==108
    assert not leg['contacts'] and not leg['errors']
    for n,h in leg['source_sha256'].items():assert S.SHA(H.ROOT/n)==h,n
    assert not MODEL.exists(),'Receive existing candidate, do not overwrite/duplicate'
    p,feeds,roots,meta,fork,reader,allocation,archive=I.prepare()
    assert meta==gate['rooted_support'] and allocation==gate['allocation']
    assert all(abs(sum(e.Length for e in es)-gate['lengths_mm'][n])<1e-6 for n,es in feeds.items())
    x,z=p['fixed_receiver_XZ_mm'];y=p['fixed_receiver_Y_mm']
    cuts=band_boxes(x,y)
    for n,rows in cuts.items():
        s=S.fuse([H.T.box(b) for b in rows]);target=roots[n]
        assert s.cut(target).Volume<1e-6 and target.cut(s).Volume<1e-6,(n,'Band recipe mismatch')
    head=H.head(reader);d=A.newDocument('FixedHeadInterface')
    par=d.addObject('App::VarSet','HeadInterfaceParameters')
    par.addProperty('App::PropertyLength','NorthRailThickness');par.NorthRailThickness=3
    bodies={};volumes={};expected={}
    for owner,host,pads,bandnames in [
      ('FixedYawCarrier',head['YawCarrier'],{**meta['fixed_pads'],**meta['shared_feed_pads']},[n for n in cuts if not n.startswith('Moving')]),
      ('MovingFork',fork,meta['moving_pads'],['MovingFactoryBand'])]:
        b=d.addObject('PartDesign::Body',owner);base=b.newObject('PartDesign::Feature',owner+'InheritedBase');base.Shape=host
        base.addProperty('App::PropertyString','Provenance');base.Provenance='Immutable inherited mechanical source, world placement applied exactly once. All new supports/passages editable; this base is not claimed fully migrated.'
        b.Tip=base;d.recompute()
        for name,row in pads.items():
            add_box(d,b,owner+name,row,expression='HeadInterfaceParameters.NorthRailThickness' if name=='NorthBranch' else None)
        for name in bandnames:
            for i,row in enumerate(cuts[name]):
                if b.Shape.common(H.T.box(row)).Volume>1e-6:add_box(d,b,owner+name+'Passage'+str(i),row,pocket=True)
        validate(b)
        ref=host.fuse(roots['FixedJRSeat' if owner=='FixedYawCarrier' else 'MovingFactoryGrip']).removeSplitter()
        assert b.Shape.cut(ref).Volume<1e-5 and ref.cut(b.Shape).Volume<1e-5,(owner,'Native material differs from complete gate')
        bodies[owner]=b;volumes[owner]=b.Shape.Volume;expected[owner]=ref
        print('Editable whole head part',owner,flush=True)
    for n,s in roots.items():
        if n in ('FixedJRSeat','MovingFactoryGrip'):continue
        ob=d.addObject('Part::Feature','Ref_'+n);ob.Label='Purchased nominal '+n;ob.Shape=s
    jr=d.addObject('Part::Feature','Ref_FixedJR');jr.Shape=H.T.box([x-6,y-30,z-5,x+6,y,z+5])
    for n,es in feeds.items():
        ob=d.addObject('Part::Feature','Feed_'+n);ob.Shape=Part.Wire(es)
        ob.addProperty('App::PropertyString','Scope');ob.Scope='One whole fixed source-to-JR nominal path; no splice at planning boundaries. Delivered connector polarity/fit and final trim remain phase2 gates.'
    rest=next(q for q in p['poses'] if q['yaw']==0)
    ob=d.addObject('Part::Feature','FactoryUncut250FreePath');ob.Shape=H.T.wire(rest['parts'])
    ob.addProperty('App::PropertyString','Scope');ob.Scope='Plus retained43.814903mm S-prefix = uncut250mm; R31.5 prototype requirement, not supplier data.'
    # Parameter/recompute/restore is functional, not a property-only test.
    par.NorthRailThickness=3.2;d.recompute()
    for b in bodies.values():validate(b)
    assert bodies['FixedYawCarrier'].Shape.Volume>volumes['FixedYawCarrier']
    par.NorthRailThickness=3;d.recompute()
    for n,b in bodies.items():validate(b);assert abs(b.Shape.Volume-volumes[n])<1e-5
    sketches=sum(o.TypeId=='Sketcher::SketchObject' for o in d.Objects)
    d.saveAs(str(MODEL));A.closeDocument(d.Name);exports=[]
    with tempfile.TemporaryDirectory(prefix='robot-cat-fixed-head-') as td:
        copy=Path(td)/MODEL.name;shutil.copy2(MODEL,copy);d=A.openDocument(str(copy));d.recompute()
        assert not any(o.TypeId=='App::Link' for o in d.Objects),'Unexpected external/internal link dependence'
        for name,v in volumes.items():
            b=d.getObject(name);validate(b);assert abs(b.Shape.Volume-v)<1e-5
            s=b.Shape.copy();bb=s.BoundBox;s.translate(V(-bb.XMin,-bb.YMin,-bb.ZMin))
            mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
            bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength];assert max(size)+10<256
            file=H.OUT/(name+'_FixedInterface_x1.stl');mesh.write(str(file))
            exports.append(dict(part=name,path=file.relative_to(H.ROOT).as_posix(),sha256=S.SHA(file),size_mm=size,quantity=1,brim_each_mm=5))
        A.closeDocument(d.Name)
    report=dict(status='FIXED_HEAD_INTERFACE_NATIVE_CANDIDATE_ASSEMBLY_STOCK_OPEN',selected=False,physical_pass=False,
        model=MODEL.relative_to(H.ROOT).as_posix(),model_sha256=S.SHA(MODEL),exports=exports,
        editable_parts=2,fully_constrained_sketches=sketches,parameter_restore_mm=[3,3.2,3],relocated_reopen=True,
        exact_material_matches_shared_gate=True,purchased_nominal_bands=len(cuts),new_M3=0,
        inherited_mechanical_bases_explicit=True,whole_phase1_complete=False,W2_complete=False,W3_complete=False,
        source_sha256={**leg['source_sha256'],legfile.relative_to(H.ROOT).as_posix():S.SHA(legfile),Path(__file__).relative_to(H.ROOT).as_posix():S.SHA(Path(__file__))},
        remaining=['Whole assembly/disconnection/ATO access/current length-stock and native master selection','Remaining full leg/body wiring and E3, not claimed by this interface'],
        worker_seconds=round(time.monotonic()-tick,3))
    H.save('fixed-head-interface-native.json',report)
    print(json.dumps({k:report[k] for k in ('status','editable_parts','fully_constrained_sketches','worker_seconds')}),flush=True)

if __name__=='__main__':run()
