"""Three replaceable PETG parts on actual PCB1 mounting axes.

No source/selected assembly is overwritten. Native candidate only; separate
shared-space receipt is required. Two foam pads bear on known bare PCB regions;
two T18I loops retain the module, never its wires or solder pads.
"""
import json, time, shutil, tempfile, sys
from pathlib import Path
import FreeCAD as A
import Part, Mesh, MeshPart
from open_deck_p0_supports import sketch, feature
from open_deck_p0_plate import rect, circle
from plan_current_main_sources import ROOT, OUT, SHA

MODEL=OUT/'U1SocketRetainer.FCStd'


def box(b):
    x,y,z,X,Y,Z=b
    return Part.makeBox(X-x,Y-y,Z-z,A.Vector(x,y,z))


def references(thickness=2):
    """Actual SKU band dimensions, nominal installed bend/head envelopes."""
    facts=ROOT/'hardware/reference/hellermann-11102370-2026-10-04/dimensions.json'
    p=json.loads(facts.read_text())
    assert (p['band_width_mm'],p['band_thickness_mm'])==(2.5,1.2)
    shapes={}
    for name,x0,x1,headx in [('Left',65.2,71.9,65.8),('Right',110.3,118.1,117.5)]:
        top=98.9602+thickness
        outer=box([x0,-4.45,86.3202,x1,-1.95,top+1.2])
        inner=box([x0+1.2,-4.5,87.5202,x1-1.2,-1.9,top])
        head=box([headx-2.4,-5.45,top,headx+2.4,-.95,top+3.5])
        shapes['Tie'+name]=outer.cut(inner).fuse(head)
    for x in (80,100):shapes['Foam'+str(x)]=box([x-2.5,-4.7,96.9602,x+2.5,-1.7,98.9602])
    return shapes,facts


def pad(body,name,z,loops,h):
    sk=sketch(body,name+'Plan',z)
    for q in loops:rect(sk,*q)
    body.Tip=feature(body,'Pad',name,sk,h)


def pocket(body,name,z,loops,h):
    sk=sketch(body,name+'Plan',z)
    for q in loops:rect(sk,*q)
    body.Tip=feature(body,'Pocket',name,sk,h)


def geometry(d):
    d.recompute();bodies=[d.getObject(n) for n in ('AnchorLeft','AnchorRight','RetainerBar')]
    for b in bodies:
        assert b.Shape.isValid() and len(b.Shape.Solids)==1 and not b.Shape.check(True),b.Name
        assert not any('Invalid' in o.State for o in b.Group),b.Name
        assert all(o.FullyConstrained and o.solve()==0 for o in b.Group if o.TypeId=='Sketcher::SketchObject')
    refs,_=references(d.Parameters.BarThickness.Value)
    for n,s in refs.items():
        actual=d.getObject(n).Shape
        assert actual.isValid() and abs(actual.Volume-s.Volume)<1e-5,n
        assert abs(actual.BoundBox.ZMax-s.BoundBox.ZMax)<1e-6,n
    return bodies


def run():
    tick=time.monotonic()
    if MODEL.exists():
        assert '--replace-candidate' in sys.argv,'Receive existing candidate, do not overwrite'
        previous=json.loads((OUT/'u1-socket-retainer-native.json').read_text())
        assert SHA(MODEL)==previous['native_sha256'] and not previous['selected']
    p=json.loads((OUT/'u1-socket-carrier-plan.json').read_text())
    d=A.newDocument('U1SocketRetainer')
    try:
        par=d.addObject('App::VarSet','Parameters')
        par.addProperty('App::PropertyLength','BarThickness');par.BarThickness=2
        for name,x,foot,eye in [
            ('Left',73.81,(66.5,-2.4,9.71,4.8),(66.5,-5.7,4.1,5)),
            ('Right',109.37,(106.97,-2.4,9.83,4.8),(111.6,-5.7,5.2,5))]:
            b=d.addObject('PartDesign::Body','Anchor'+name)
            # Flat replacement washer-foot: existing carrier owns the PCB
            # locating function. Do NOT add a second neck in its same hole.
            pad(b,name+'BearingFoot',84.3202,[foot],1)
            pad(b,name+'TieEye',84.3202,[eye],4.8)
            # Horizontal through-X slot: sketch's XY becomes world ZY.
            s=sketch(b,name+'EyeWindow',0)
            s.Placement=A.Placement(A.Vector(eye[0]+eye[2],0,0),A.Rotation(A.Vector(0,1,0),90))
            rect(s,-87.7202,-4.6,1.4,2.8)
            b.Tip=feature(b,'Pocket',name+'BandPassage',s,eye[2])
            s=sketch(b,name+'ActualMountAxis',89.1202);circle(s,x,0,2.4)
            b.Tip=feature(b,'Pocket',name+'M2Clearance',s,6.4002)
        bar=d.addObject('PartDesign::Body','RetainerBar')
        pad(bar,'FlatBar',98.9602,[(64.5,-5.4,54.5,4.4)],'Parameters.BarThickness')
        pad(bar,'AsymmetricKeyTongue',98.9602,[(105.83,-1.1,2,5.91)],'Parameters.BarThickness')
        s=sketch(bar,'KeyStemPlan',97.1602);circle(s,106.83,3.81,2)
        bar.Tip=feature(bar,'Pad','KeyStem',s,1.8)
        s=sketch(bar,'UnusedSupplierHoleKeyPlan',95.5602);circle(s,106.83,3.81,.7)
        bar.Tip=feature(bar,'Pad','OrientationKey',s,1.6)
        pocket(bar,'FourTieSlots','98.9602 mm+Parameters.BarThickness',
               [(x-.8,-4.6,1.6,2.8) for x in (65.8,71.3,110.9,117.5)],'Parameters.BarThickness')
        refs,facts=references()
        # Purchased tie references are native boxes/cuts/fuses. Their closing
        # height and locking heads follow the useful bar parameter as well.
        def block(n,x,y,z,dx,dy,dz):
            ob=d.addObject('Part::Box',n);ob.Length=dx;ob.Width=dy;ob.Height=dz
            ob.Placement.Base=A.Vector(x,y,z);return ob
        for name,x0,x1,headx in [('Left',65.2,71.9,65.8),('Right',110.3,118.1,117.5)]:
            outer=block(name+'BandOuter',x0,-4.45,86.3202,x1-x0,2.5,15.84)
            outer.setExpression('Height','13.84 mm+Parameters.BarThickness')
            inner=block(name+'BandInner',x0+1.2,-4.5,87.5202,x1-x0-2.4,2.6,13.44)
            inner.setExpression('Height','11.44 mm+Parameters.BarThickness')
            band=d.addObject('Part::Cut',name+'Band');band.Base=outer;band.Tool=inner
            head=block(name+'Lock',headx-2.4,-5.45,100.9602,4.8,4.5,3.5)
            head.setExpression('Placement.Base.z','98.9602 mm+Parameters.BarThickness')
            tie=d.addObject('Part::Fuse','Tie'+name);tie.Base=band;tie.Tool=head;tie.Refine=True
        for n,s in refs.items():
            if n.startswith('Tie'):continue
            o=d.addObject('Part::Feature',n);o.Shape=s
            o.addProperty('App::PropertyString','Qualification')
            o.Qualification='Project installed envelope / delivery dry fit OPEN; not rated cable strain relief'
        bodies=geometry(d);vol=[b.Shape.Volume for b in bodies]
        par.BarThickness=2.4;changed=geometry(d)
        assert changed[-1].Shape.Volume>vol[-1] and abs(changed[-1].Shape.BoundBox.ZMax-101.3602)<1e-6
        par.BarThickness=2;geometry(d)
        assert all(abs(b.Shape.Volume-v)<1e-5 for b,v in zip(bodies,vol))
        d.saveAs(str(MODEL));A.closeDocument(d.Name)
        with tempfile.TemporaryDirectory(prefix='robot-cat-socket-retainer-') as tmp:
            copy=Path(tmp)/MODEL.name;shutil.copy2(MODEL,copy)
            d=A.openDocument(str(copy));bodies=geometry(d)
            assert all(abs(b.Shape.Volume-v)<1e-5 for b,v in zip(bodies,vol))
        exports=[]
        for b in bodies:
            s=b.Shape.copy();bb=s.BoundBox
            s.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
            f=OUT/(b.Name+'.stl')
            MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False).write(str(f))
            m=Mesh.Mesh(str(f));assert m.isSolid() and m.countComponents()==1
            assert max(m.BoundBox.XLength+10,m.BoundBox.YLength+10,m.BoundBox.ZLength+10)<256
            exports.append(dict(part=b.Name,quantity=1,path=f.relative_to(ROOT).as_posix(),sha256=SHA(f),
                                print_orientation='As exported; support underside overhang/eye roof as needed, no slicer claim',brim_margin_mm_each=5))
        result=dict(status='NATIVE_SOCKET_RETENTION_CANDIDATE_SHARED_SPACE_OPEN',selected=False,E1_complete=False,physical_pass=False,
            native=MODEL.relative_to(ROOT).as_posix(),native_sha256=SHA(MODEL),exports=exports,
            valid_editable_parts=3,parameter_restore_mm=[2,2.4,2],fresh_relocated_reopen=True,
            replaces=['PWM160825TopInsulator','PWM160824TopInsulator'],
            retained_fasteners='Existing2xM2x14/nuts, same1mm under-head stack; no extra metal fasteners',
            load_path='Foam on known bare PCB zones -> bar ->2T18I ->2PETG eyes -> actual PCB mounting bolts/posts',
            assembly=['Install anchors with PCB1 before plugging1208; bench solder and unpowered continuity first',
                      'Insert orientation-marked1208 into24actual socket contacts',
                      'Two5x3x2 insulating foam pads atX80/100,Y-3.2; no adhesive as wire strain relief',
                      'Lower keyed bar into existing unused1208hole at106.83,3.81; route and snug2T18I',
                      'Reverse: cut only these2ties, lift bar then withdraw adapter12mm vertically; unstack upper module first if obstructed'],
            added_ties=2,foam_pads=2,extra_screws=0,
            supplier_stack_is_nominal_not_tolerance_qualified=True,
            superseded_retainer_geometry='0f80936 preserves rejected locator-necks and PCB-crossing left band; NOT selected',
            phase2_gates=['Actual header/board thickness and seating; trim male tails<=1.4mm above adapter',
                         'Key0.7mm and1.4x2.8slot print coupon/dry fit; deburr band windows',
                         'PETG1mm washer bearing/creep and wing support, no strength rating',
                         'Foam must be electrically insulating and suitable for temperature; no bare pad compression',
                         'Separate independent external lead grips and underside insulating cover remainOPEN'],
            source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (Path(__file__),facts,OUT/'u1-socket-carrier-plan.json')},
            worker_seconds=round(time.monotonic()-tick,3))
        (OUT/'u1-socket-retainer-native.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:result[k] for k in ('status','valid_editable_parts','parameter_restore_mm','fresh_relocated_reopen','worker_seconds')}),flush=True)
    finally:
        if d.Name in A.listDocuments():A.closeDocument(d.Name)


if __name__=='__main__':run()
