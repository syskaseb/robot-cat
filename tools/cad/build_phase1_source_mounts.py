"""Native final minimal source mounts after one shared layout acceptance.

Accepted parents stay editable external links. New material has Sketch/Pad/
Pocket histories. No old source is saved or overwritten. This is not M4/E3
selection by itself; insulation/quantities and final integration remain gates.
"""
import json,math,shutil,tempfile,time,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
import FreeCAD as A
import Part,Sketcher,MeshPart
from phase1_source_protection import ROOT,BASE,BODY,OUT,SCENE,check,sha,capsule,box
from open_deck_p0_supports import sketch,feature
from open_deck_p0_plate import rect,circle
from phase1_stl_preflight import inspect,fit

MODEL=OUT/'FunctionalSourceMounts.FCStd'

def rectangle(body,name,z,x,y,w,h,length,width_expression=None):
    s=sketch(body,name+'Plan',z);rect(s,x,y,w,h,width_expression);body.Tip=feature(body,'Pad',name,s,length);return body.Tip
def disk(body,name,z,x,y,d,length):
    s=sketch(body,name+'Plan',z);circle(s,x,y,d);body.Tip=feature(body,'Pad',name,s,length);return body.Tip
def bores(body,name,z,centres,d,length):
    s=sketch(body,name+'Plan',z)
    for x,y in centres:circle(s,x,y,d)
    body.Tip=feature(body,'Pocket',name,s,length);return body.Tip
def outline(body,name,z,solid,length):
    # Only the shared 2D routing outline is fixed. Extrusion dimensions remain
    # native and editable, rather than embedding a finished opaque solid.
    face=next(f for f in solid.Faces if abs(f.CenterOfMass.z)<1e-7 and abs(abs(f.normalAt(0,0).z)-1)<1e-7)
    s=sketch(body,name+'Plan',z)
    for wire in face.Wires:
        for e in wire.Edges:
            a=e.valueAt(e.FirstParameter);b=e.valueAt(e.LastParameter);mid=e.valueAt((e.FirstParameter+e.LastParameter)/2)
            if isinstance(e.Curve,Part.Line):g=Part.LineSegment(a,b)
            elif len(e.Vertexes)==1:g=Part.Circle(e.Curve.Center,A.Vector(0,0,1),e.Curve.Radius)
            else:g=Part.Arc(a,mid,b)
            i=s.addGeometry(g,False);s.addConstraint(Sketcher.Constraint('Block',i))
    body.Tip=feature(body,'Pad',name,s,length);return body.Tip

def source_addition(doc):
    b=doc.addObject('PartDesign::Body','S0StaticFoundationMount')
    rectangle(b,'StaticColumn',71.32,-128,32,3,8,33.68)
    rectangle(b,'AboveYawBridge',105,-128,32,29,8,'ProtectionParameters.PanelThickness')
    rectangle(b,'PanelJoin',105,-103,24,4,16,'ProtectionParameters.PanelThickness')
    rectangle(b,'PublishedS0Panel',105,-103,2,52,28,'ProtectionParameters.PanelThickness')
    bores(b,'PublishedS0Neck','105 mm + ProtectionParameters.PanelThickness',[(-77,16)],24,'ProtectionParameters.PanelThickness')
    bores(b,'PublishedS0MountingHoles','105 mm + ProtectionParameters.PanelThickness',[(-96,16),(-58,16)],6.5,'ProtectionParameters.PanelThickness')
    return b

def dock(doc):
    b=doc.addObject('PartDesign::Body','PostF0Dock')
    rectangle(b,'DockRoot',18.7,47,-65.4,24.1,13.2,1.8)
    rectangle(b,'AdhesivePedestal',20.5,50,-65.4,21.1,13.2,.5)
    rectangle(b,'EastCurb',21,69.3,-65.4,1.8,13.2,3)
    rectangle(b,'SouthCurb',21,50,-65.4,19.3,1.8,3)
    rectangle(b,'NorthCurb',21,50,-54,19.3,1.8,3)
    return b

def s1_mount(doc):
    b=doc.addObject('PartDesign::Body','S1MountCurrent')
    disk(b,'SharedFrameBoltFoot',77.72,138,30,8,5.98)
    shape=capsule((126.2,40),(138,30),3,0,1).fuse(box(126.2,37,0,41.5,6,1)).removeSplitter()
    outline(b,'AboveWireArch',81.22,shape,2.48)
    disk(b,'LocatorFoot',77.72,126.2,40,8,5.98)
    disk(b,'AntirotationPeg',74.72,126.2,40,3.2,3)
    rectangle(b,'PublishedS1Panel',81.22,164.7,23.5,3,24,35.78)
    s=b.newObject('Sketcher::SketchObject','S1NeckAndKeyPlan')
    s.Placement=A.Placement(A.Vector(167.7,0,0),A.Rotation(A.Vector(0,1,0),A.Vector(0,0,1),A.Vector(1,0,0),'ZXY'))
    circle(s,35.5,105,12.5);circle(s,26.5,105,3)
    b.Tip=feature(b,'Pocket','PublishedS1NeckAndKey',s,3)
    bores(b,'SharedFrameBore',83.7,[(138,30)],3.4,6)
    top=sketch(b,'CountersunkHeadTop',83.7);circle(top,138,30,6)
    lower=sketch(b,'CountersunkHeadBottom',82.4);circle(lower,138,30,3.4)
    f=b.newObject('PartDesign::SubtractiveLoft','FlushFrameHead');f.Profile=top;f.Sections=[lower];f.Ruled=True
    doc.recompute();b.Tip=f
    return b

def signature(s):
    b=s.optimalBoundingBox();return [s.Volume,b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def qualified(doc,names):
    doc.recompute();result={}
    for n in names:
        s=doc.getObject(n).Shape
        assert s.isValid() and len(s.Solids)==1 and not s.check(True),(n,'shape/BOP')
        result[n]=signature(s)
    sketches=[o for o in doc.Objects if o.TypeId=='Sketcher::SketchObject']
    assert all(s.solve()==0 and s.FullyConstrained for s in sketches),[(s.Name,s.FullyConstrained) for s in sketches]
    return result
def dependencies(file,seen=None):
    seen=set() if seen is None else seen
    if file in seen:return seen
    assert file.resolve().is_relative_to(ROOT.resolve());seen.add(file)
    with zipfile.ZipFile(file) as z:x=ET.fromstring(z.read('Document.xml'))
    for p in x.findall('.//*[@file]'):
        name=p.get('file')
        if name and name.lower().endswith('.fcstd'):dependencies((file.parent/name).resolve(),seen)
    return seen

def run():
    check();tick=time.monotonic();p=json.loads((OUT/'foundation-space-check.json').read_text())
    assert p['status']=='COMMON_LAYOUT_CLEAR_NATIVE_DETAIL_PENDING',p['contacts']
    old=json.loads((OUT/'minimal-space-check.json').read_text())
    assert not any(r['new']!='S0MountCurrent' for r in old['contacts'])
    rows=json.loads((BASE/'phase1-current-print-selection.json').read_text())['prints']
    src={r['identity']:r for r in rows if r['identity'] in ('Foundation','FrontRightFixedCarrier')}
    for r in src.values():assert sha(ROOT/r['path'])==r['sha256']
    assert not MODEL.exists(),'Receive existing native result, do not duplicate'
    doc=A.newDocument('FunctionalSourceMounts');doc.saveAs(str(OUT/'FunctionalSourceMounts.building.FCStd'))
    params=doc.addObject('App::VarSet','ProtectionParameters');params.addProperty('App::PropertyLength','PanelThickness');params.PanelThickness=2.4
    additions={'Foundation':source_addition(doc),'FrontRightFixedCarrier':dock(doc)};s1=s1_mount(doc)
    equivalence=[]
    for label,obj in [('S0MountFoundation',additions['Foundation']),('PostF0Dock',additions['FrontRightFixedCarrier']),('S1MountCurrent',s1)]:
        doc.recompute();f=OUT/(label+'.brep');prior=Part.Shape();prior.read(str(f))
        delta=obj.Shape.copy().cut(prior.copy()).Volume+prior.copy().cut(obj.Shape.copy()).Volume
        assert delta<1e-4,(label,'Native differs from checked shared material',delta)
        equivalence.append(dict(part=label,checked_brep=f.relative_to(ROOT).as_posix(),sha256=sha(f),symmetric_difference_mm3=delta))
    names=[];sources=[];retained={}
    for ident,r in src.items():
        check();f=ROOT/r['native'];source=A.openDocument(str(f));obj=source.getObject(r['native_object']);assert obj
        link=doc.addObject('App::Link','Retained_'+ident);link.LinkedObject=obj;sources.append(source)
        final=doc.addObject('Part::MultiFuse',ident+'ProtectedCurrent');final.Shapes=[link,additions[ident]];final.Refine=True
        doc.recompute();assert obj.Shape.copy().cut(final.Shape.copy()).Volume<1e-5
        names.append(final.Name);retained[ident]=dict(native=r['native'],object=r['native_object'],sha256=sha(f),signature=signature(obj.Shape))
    names.append(s1.Name);baseline=qualified(doc,names)
    # Save a recoverable baseline BEFORE the parameter test.
    doc.saveAs(str(MODEL));print('native saved; parameter test next',flush=True)
    params.PanelThickness=2.6;changed=qualified(doc,names)
    assert changed['FoundationProtectedCurrent'][0]>baseline['FoundationProtectedCurrent'][0]
    params.PanelThickness=2.4;restored=qualified(doc,names)
    assert all(max(abs(x-y) for x,y in zip(baseline[n],restored[n]))<1e-5 for n in names)
    doc.save();exports=[]
    for n in names:
        check();s=doc.getObject(n).Shape.copy();rotation=A.Rotation(.5,.5,.5,.5) if n.startswith('FrontRight') else A.Rotation()
        s.Placement=A.Placement(A.Vector(),rotation)*s.Placement;b=s.optimalBoundingBox();s.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
        f=OUT/(n+'_x1.stl');mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.08,AngularDeflection=.25,Relative=False);mesh.write(str(f))
        q=inspect(f.read_bytes());assert q['closed'] and q['components']==1 and fit(q['size_mm']),(n,q)
        exports.append(dict(part=n,native=MODEL.relative_to(ROOT).as_posix(),native_object=n,path=f.relative_to(ROOT).as_posix(),sha256=sha(f),quantity=1,printing=dict(**q,rotation_quaternion=list(rotation.Q),brim_each_mm=5,fits_with_5mm_brim=True)))
    files=dependencies(MODEL)
    for d in list(A.listDocuments().values()):A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='cat-source-relocated-') as td:
        root=Path(td)
        for f in files:
            target=root/f.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,target)
        moved=A.openDocument(str(root/MODEL.relative_to(ROOT)));moved.recompute();again=qualified(moved,names)
        assert all(max(abs(x-y) for x,y in zip(baseline[n],again[n]))<1e-5 for n in names)
        for o in moved.Objects:
            if o.TypeId=='App::Link':assert Path(o.LinkedObject.Document.FileName).resolve().is_relative_to(root.resolve())
        for d in list(A.listDocuments().values()):A.closeDocument(d.Name)
    pins={f.relative_to(ROOT).as_posix():sha(f) for f in files}
    for r in retained.values():assert sha(ROOT/r['native'])==r['sha256'],'Old parent changed'
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    result=dict(status='THREE_NATIVE_SOURCE_MOUNTS_REOPEN_PARAMETER_STL_COMPLETE',selected=False,M4_complete=False,physical_pass=False,
        parts=exports,retained=retained,source_sha256=pins,shared_layout_equivalence=equivalence,parameter_mm=[2.4,2.6,2.4],relocated_reopen=True,
        new_sketches_fully_constrained=True,original_material_preserved=True,worker_seconds=round(time.monotonic()-tick,3),
        remaining='Source contact insulation/nominal fastener fit and final common ownership/stock/A2 refresh. No power approval.')
    (OUT/'native-mounts.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'])),flush=True)

if __name__=='__main__':run()
