"""One editable BUS H5 passage and independent paired-wire jaw.

Retain the complete W1 carrier history. Supplier plug/copper and leg motion
remain explicit gates; this scoped native result cannot select the whole W5.
"""
import json,math,time,shutil,tempfile
from pathlib import Path
import FreeCAD as A,Part,Sketcher,MeshPart
from plan_current_main_sources import ROOT,BASE,OUT,SHA
from open_deck_p0_supports import sketch
from open_deck_p0_plate import rect
from plan_current_tail_complete import tie_z

SOURCE=BASE/'aux-wiring-checkpoint/AUXPowerCurrent.FCStd'
MODEL=OUT/'BUSCarrierCurrent.FCStd'
WORK=OUT/'BUSCarrierNativeWork.FCStd'

def run():
    tick=time.monotonic()
    f=OUT/'BUS-routes-plan.json';p=json.loads(f.read_text())
    g=OUT/'BUS-routes-checks.json';gate=json.loads(g.read_text())
    assert gate['status']=='BUS_NOMINAL_MATERIAL_AND_JAW_CLEAR_NATIVE_OPEN'
    assert not gate['contacts'] and not gate['errors']
    for q in (p,gate):
        for n,h in q['source_sha256'].items():assert SHA(ROOT/n)==h,n
    assert not MODEL.exists() and not WORK.exists(),'Receive the existing native work; no duplicate build'
    src=A.openDocument(str(SOURCE));d=A.newDocument('BUSCarrierCurrent')
    body=d.copyObject(src.UpperCarrier001,True);d.recompute();original=body.Shape.copy()
    A.closeDocument(src.Name)
    params=d.addObject('App::VarSet','BUSParameters')
    params.addProperty('App::PropertyLength','PassageRadius');params.PassageRadius=1.6
    inverse=body.Placement.inverse()
    def pad_box(row):
        b=row['bounds_mm'];a=inverse.multVec(A.Vector(*b[:3]));c=inverse.multVec(A.Vector(*b[3:]))
        old=body.Tip;s=sketch(body,row['name']+'Plan',a.z)
        rect(s,a.x,a.y,c.x-a.x,c.y-a.y)
        ob=body.newObject('PartDesign::Pad',row['name']);ob.Profile=s;ob.BaseFeature=old;ob.Length=c.z-a.z
        body.Tip=ob;s.Visibility=False;return ob
    for row in gate['shared_grip_pads']:pad_box(row)
    d.recompute();print('BUS native jaw pads',flush=True)
    # A native circular profile and editable planar arc are sufficient:
    # only the first arc intersects the plate; no opaque Boolean replacement.
    for n,prefix in p['source_prefixes'].items():
        old=body.Tip
        q=prefix[0];a=A.Vector(*q['start']);end=A.Vector(*q['end']);mid=A.Vector(*q['mid'])
        direction=A.Vector(-2**-.5,-2**-.5,0);up=A.Vector(0,0,1)
        placement=A.Placement(a,A.Rotation(direction,up,direction.cross(up),'ZXY'))
        path=body.newObject('Sketcher::SketchObject',n+'PassagePath');path.Placement=inverse*placement
        transform=placement.inverse()
        i=path.addGeometry(Part.Arc(transform.multVec(a),transform.multVec(mid),transform.multVec(end)),False)
        path.addConstraint(Sketcher.Constraint('Block',i))
        profile=body.newObject('Sketcher::SketchObject',n+'PassageProfile')
        profile.Placement=inverse*A.Placement(a,A.Rotation())
        profile.addGeometry(Part.Circle(A.Vector(),up,1.6),False)
        profile.addConstraint(Sketcher.Constraint('Coincident',0,3,-1,1))
        c=profile.addConstraint(Sketcher.Constraint('Diameter',0,3.2))
        profile.renameConstraint(c,'PassageDiameter')
        profile.setExpression('Constraints.PassageDiameter','2 * BUSParameters.PassageRadius')
        ob=body.newObject('PartDesign::SubtractivePipe',n+'Passage')
        ob.BaseFeature=old;ob.Profile=profile;ob.Spine=(path,[]);ob.Transition=0;body.Tip=ob
        d.recompute();path.Visibility=False;profile.Visibility=False
        assert ob.Shape.isValid() and len(ob.Shape.Solids)==1,(n,list(ob.State))
        print('BUS native passage',n,flush=True)
    cols=[q[2]['start'] for q in p['source_prefixes'].values()]
    x=sum(c[0] for c in cols)/2;z=cols[0][2]+4.5
    x0=x-5.8;x1=x+2.3;y0=min(c[1] for c in cols)-2.2;y1=max(c[1] for c in cols)+2.2
    # A square-cornered, slightly larger native return slot is a SUBSET of
    # the qualified rounded-offset jaw. Its extra removal is measured below.
    old=body.Tip;clearance=.15;s=sketch(body,'BUSBandSlotPlan',z+1.25+clearance-body.Placement.Base.z)
    rect(s,x0-clearance-body.Placement.Base.x,y0-clearance-body.Placement.Base.y,x1-x0+2*clearance,y1-y0+2*clearance)
    rect(s,x0+1.2+clearance-body.Placement.Base.x,y0+1.2+clearance-body.Placement.Base.y,x1-x0-2.4-2*clearance,y1-y0-2.4-2*clearance)
    ob=body.newObject('PartDesign::Pocket','BUSBandReturn');ob.Profile=s;ob.BaseFeature=old;ob.Length=2.5+2*clearance
    body.Tip=ob;s.Visibility=False;d.recompute();d.saveAs(str(WORK))
    def validate():
        assert body.Shape.isValid() and len(body.Shape.Solids)==1 and not body.Shape.check(True)
        for o in body.Group:
            assert not any(t in ('Invalid','Error') for t in o.State),(o.Name,list(o.State))
            if o.TypeId=='Sketcher::SketchObject' and o.Name.startswith(('BUS','W002','W003')):
                assert o.FullyConstrained and o.solve()==0,o.Name
    validate()
    qualified=original.copy()
    for row in gate['shared_grip_pads']:
        b=row['bounds_mm'];qualified=qualified.fuse(Part.makeBox(*(b[i+3]-b[i] for i in range(3)),A.Vector(*b[:3])))
    for prefix in p['source_prefixes'].values():
        q=prefix[0];edge=Part.Arc(A.Vector(*q['start']),A.Vector(*q['mid']),A.Vector(*q['end'])).toShape();w=Part.Wire([edge])
        pipe=w.makePipeShell([Part.Wire([Part.makeCircle(1.6,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])],True,False)
        qualified=qualified.cut(pipe.common(Part.makeBox(30,40,3.4,A.Vector(45,-40,74.52))))
    band,head=tie_z(z,x0,x1,y0,y1);qualified=qualified.cut(band.makeOffsetShape(.15,.01)).removeSplitter()
    # Every retained plate/support change outside the planned passage/slot
    # would fail this comparison instead of silently inheriting a green gate.
    added=body.Shape.cut(qualified).Volume;extra_removed=qualified.cut(body.Shape)
    assert added<1e-5,added
    assert extra_removed.Volume<1,extra_removed.Volume
    retained_removed=original.cut(body.Shape)
    assert retained_removed.cut(Part.makeBox(30,40,3.4,A.Vector(45,-40,74.52))).Volume<1e-5
    baseline=body.Shape.Volume;params.PassageRadius=1.7;d.recompute();validate()
    assert baseline-body.Shape.Volume>.1
    params.PassageRadius=1.6;d.recompute();validate();assert abs(body.Shape.Volume-baseline)<1e-5
    mesh=MeshPart.meshFromShape(Shape=body.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
    assert mesh.isSolid() and not mesh.hasNonManifolds()
    b=mesh.BoundBox;size=[b.XLength,b.YLength,b.ZLength];assert max(size)+10<256,size
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);stl=OUT/'UpperCarrier_BUS_current_x1.stl';mesh.write(str(stl))
    d.recompute();d.saveAs(str(MODEL));name=body.Name;A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='cat-bus-native-') as td:
        relocated=Path(td)/MODEL.name;shutil.copy2(MODEL,relocated);d=A.openDocument(str(relocated));d.recompute();body=d.getObject(name)
        validate();assert abs(body.Shape.Volume-baseline)<1e-5;A.closeDocument(d.Name)
    result=dict(status='BUS_NATIVE_CARRIER_PREPARED_W5_OPEN',model=MODEL.relative_to(ROOT).as_posix(),model_sha256=SHA(MODEL),
        export=dict(path=stl.relative_to(ROOT).as_posix(),sha256=SHA(stl),size_mm=size,quantity=1,replaces='W1 UpperCarrier001; not another physical plate'),
        native_history_preserved=True,parameter_1p6_1p7_1p6_restore=True,fresh_relocated_reopen=True,
        volume_added_outside_qualified_material_mm3=added,extra_slot_corner_removal_mm3=extra_removed.Volume,
        retained_removal_outside_two_plate_passages_mm3=0,paired_backer_remaining_nominal_web_mm=3.4,
        T18I_installed=1,T18I_service_spares=1,selected=False,W5_complete=False,physical_pass=False,print_ready=False,
        delivery_gates=p['delivery_gates'],leg_motion_and_common_service_open=True,worker_seconds=time.monotonic()-tick,
        source_sha256={q.relative_to(ROOT).as_posix():SHA(q) for q in (SOURCE,f,g,Path(__file__))})
    (OUT/'BUS-native-checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:result[k] for k in ('status','worker_seconds','extra_slot_corner_removal_mm3')}),flush=True)
    return result

if __name__=='__main__':run()
