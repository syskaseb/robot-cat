"""Four editable frame-anchored belly supports, candidate until shared fit gate.

Reuse original8 frame holes/nuts/washers; replace M2x6 with nominalM2x10.
No historical document saved, structural/electrical/physical PASS not inferred.
"""
import json,math,time
from pathlib import Path
import FreeCAD as A
import Part
import Sketcher
import MeshPart
from check_main_p0_placement import SavedShapes,ROOT,sha
from plan_feline_layout import MODEL,OUT


def run():
    tick=time.monotonic();reader=SavedShapes()
    old=OUT/'FelineLayoutEnvelope.FCStd';tip=reader.shape(old,'BellyPadReservation1').BoundBox.ZMin
    path=OUT/'FelineBellyFeet.FCStd';assert not path.exists(),'Receive saved native feet before any rebuild'
    partial=OUT/'FelineBellyFeet.partial.FCStd'
    doc=A.openDocument(str(partial)) if partial.exists() else A.newDocument('FelineBellyFeet')
    live_doc_name=doc.Name;reused_sketches=set()
    report=dict(status='BUILDING_NATIVE_FEET',selected=False,physical_pass=False,
        external_fit_complete=False,load_test_complete=False,parts=[],hardware=[],
        load_path='Ground annular foot -> hollow18mm stem ->18x30x3 bridge -> P0 underside contact and two existingM2 frame holes per support',
        stock_delta={'M2x6':-8,'M2x10':8,'M2washers':0,'M2nuts':0},
        assembly=['Disconnect/remove battery before assembly; no energized work authorized',
            'Replace one original frame bolt pair at a time; preserve captive upper nuts/washers',
            'Seat bridge at frameZ-2, two0.5mm bosses at battery-plateZ-1.5',
            'Bottom driver along original axes; actual tool/retention/load fit remains a gate'],
        print_gate='Candidate PETG, no slicer run. Root-down print needs local support for0.5mm bosses; orientation/support and first physical fit still open.')
    def save_report():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        (OUT/'belly-feet-native.json').write_text(json.dumps(report,indent=2)+'\n')
    def sketch(body,name,z):
        if doc.getObject(name):
            s=doc.getObject(name);reused_sketches.add(name);assert s.FullyConstrained
            assert abs(s.Placement.Base.z-z)<1e-6;return s
        s=doc.addObject('Sketcher::SketchObject',name);body.addObject(s);s.Placement.Base.z=z
        return s
    def circle(s,x,y,r,expression):
        if s.Name in reused_sketches:return
        i=s.addGeometry(Part.Circle(A.Vector(x,y,0),A.Vector(0,0,1),r),False)
        s.addConstraint(Sketcher.Constraint('DistanceX',i,3,x));s.addConstraint(Sketcher.Constraint('DistanceY',i,3,y))
        k=s.addConstraint(Sketcher.Constraint('Radius',i,r));s.setExpression(f'Constraints[{k}]',expression)
    def rectangle(s,x0,y0,x1,y1):
        if s.Name in reused_sketches:return
        pts=[A.Vector(x0,y0,0),A.Vector(x1,y0,0),A.Vector(x1,y1,0),A.Vector(x0,y1,0)]
        for i in range(4):s.addGeometry(Part.LineSegment(pts[i],pts[(i+1)%4]),False)
        for i in range(4):s.addConstraint(Sketcher.Constraint('Coincident',i,2,(i+1)%4,1))
        for i,p in enumerate(pts):
            s.addConstraint(Sketcher.Constraint('DistanceX',i,1,p.x));s.addConstraint(Sketcher.Constraint('DistanceY',i,1,p.y))
    def pad(body,name,s,length,expression=None,reversed=False):
        doc.recompute();o=doc.getObject(name) or body.newObject('PartDesign::Pad',name)
        o.setExpression('Length',None);o.Profile=s;o.Length=length;o.Reversed=reversed
        if expression:o.setExpression('Length',expression)
        doc.recompute()
        if o.Shape.isNull():
            report['native_feature_error']=dict(name=name,state=list(o.State),status=o.getStatusString(),
                length_mm=o.Length.Value,reversed=o.Reversed,sketch_constrained=s.FullyConstrained,
                sketch_state=list(s.State),sketch_status=s.getStatusString(),expression=list(o.ExpressionEngine))
            raise ValueError('Null native feature: '+name)
        assert o.Shape.isValid() and len(o.Shape.Solids)==1,name
        return o
    try:
        p=doc.getObject('Parameters') or doc.addObject('Spreadsheet::Sheet','Parameters')
        # Negative quantity text is stored as a string by this Spreadsheet
        # version. Store the positive drop and negate in a typed expression.
        values=[('PadDrop',-tip),('StemRadius',9),('StemInnerRadius',4),('BossRadius',3.2),('HoleRadius',1.1)]
        for row,(name,value) in enumerate(values,1):p.set(f'A{row}',name);p.set(f'B{row}',f'{value} mm');p.setAlias(f'B{row}',name)
        bodies=[];sketches=[]
        for index,(x,y) in enumerate(((-75.5,-40),(-75.5,40),(117.5,-40),(117.5,40)),1):
            b=doc.getObject(f'BellyFoot{index}') or doc.addObject('PartDesign::Body',f'BellyFoot{index}');b.Label=f'Podpora brzucha {index}, kandydat'
            holes=(-80,-70) if x<0 else (112,122);hy=math.copysign(22.5,y)
            s=sketch(b,f'RootProfile{index}',-5);rectangle(s,x-9,min(math.copysign(19,y),math.copysign(49,y)),x+9,max(math.copysign(19,y),math.copysign(49,y)))
            pad(b,f'RootBridge{index}',s,3);sketches.append(s)
            s=sketch(b,f'BossProfile{index}',-2.1)
            for hx in holes:
                circle(s,hx,hy,3.2,'Parameters.BossRadius');circle(s,hx,hy,1.1,'Parameters.HoleRadius')
            pad(b,f'SeatBosses{index}',s,.6);sketches.append(s)
            s=sketch(b,f'StemProfile{index}',-3)
            circle(s,x,y,9,'Parameters.StemRadius');circle(s,x,y,4,'Parameters.StemInnerRadius')
            pad(b,f'HollowStem{index}',s,-3-tip,'Parameters.PadDrop - 3 mm',True);sketches.append(s)
            s=sketch(b,f'HoleProfile{index}',-1.5)
            for hx in holes:circle(s,hx,hy,1.1,'Parameters.HoleRadius')
            doc.recompute();cut=b.newObject('PartDesign::Pocket',f'FrameHoles{index}');cut.Profile=s;cut.Type=1
            doc.recompute();assert b.Shape.isValid() and len(b.Shape.Solids)==1
            assert not b.Shape.check(True)
            sketches.append(s);bodies.append(b)
            report['parts'].append(dict(object=b.Name,axes_mm=[[hx,hy] for hx in holes],
                pad_center_mm=[x,y,tip],root_top_mm=-2,boss_top_mm=-1.5,
                volume_mm3=b.Shape.Volume,fully_editable=True,external_fit_complete=False))
            save_report();print('Native foot',index,'saved in memory',flush=True)
        assert all(s.FullyConstrained for s in sketches)
        for i,x in enumerate((-80,-70,112,122)):
            for j,y in enumerate((-22.5,22.5)):
                source=reader.shape(MODEL,'BatteryFrameHardware'+str(i*2+j))
                upper=[s for s in source.Solids if s.BoundBox.ZMin>=1.49];assert len(upper)==2
                lower=[s for s in source.Solids if -1.81<s.BoundBox.ZMin<-1.79 and s.BoundBox.ZMax<-1.49];assert len(lower)==1
                washer=lower[0].copy();washer.translate(A.Vector(0,0,-3.5))
                bolt=Part.makeCylinder(1.9,2,A.Vector(x,y,-7.3)).fuse(Part.makeCylinder(1,10,A.Vector(x,y,-5.3)))
                ob=doc.addObject('Part::Feature',f'FrameHardwareNew{i*2+j}');ob.Shape=Part.makeCompound([bolt,washer,*upper])
                ob.addProperty('App::PropertyString','Provenance');ob.Provenance='Original exact upper nut/washer + original lower washer translated3.5mm; nominal M2x10 replacement, not supplier thread/torque geometry'
                report['hardware'].append(dict(object=ob.Name,replaces='BatteryFrameHardware'+str(i*2+j),axis_mm=[x,y],underhead_mm=-5.3,tip_mm=4.7))
        original=[b.Shape.Volume for b in bodies]
        p.set('B1',f'{-tip+1} mm');doc.recompute()
        assert all(b.Shape.isValid() and abs(b.Shape.BoundBox.ZMin-(tip-1))<1e-5 for b in bodies)
        p.set('B1',f'{-tip} mm');doc.recompute()
        assert all(abs(b.Shape.Volume-v)<1e-4 for b,v in zip(bodies,original))
        doc.saveAs(str(path));saved_names=[b.Name for b in bodies];doc_name=doc.Name;A.closeDocument(doc_name);live_doc_name=None
        doc=A.openDocument(str(path));live_doc_name=doc.Name;assert all(doc.getObject(n).Shape.isValid() for n in saved_names)
        for n,r in zip(saved_names,report['parts']):
            s=doc.getObject(n).Shape;mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.1,AngularDeflection=.3,Relative=False)
            assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
            bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
            assert max(bb.XLength,bb.YLength,bb.ZLength)<=252
            target=OUT/(n+'_candidate_x1.stl');mesh.write(str(target))
            r.update(stl=target.relative_to(ROOT).as_posix(),stl_sha256=sha(target),closed_stl=True,
                print_extents_mm=[bb.XLength,bb.YLength,bb.ZLength])
        report.update(status='FOUR_EDITABLE_FEET_NATIVE_SHARED_FIT_OPEN',native=path.relative_to(ROOT).as_posix(),native_sha256=sha(path),
            fully_constrained_sketches=len(sketches),parameter_tip_test_mm=[tip,tip-1,tip],fresh_reopen=True,
            resumed_unchanged_partial_sketches=sorted(reused_sketches),
            source_sha256={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))})
        save_report();print(json.dumps({k:report[k] for k in ('status','fully_constrained_sketches','worker_seconds')}),flush=True)
    except Exception as e:
        report.update(status='NATIVE_FEET_INCOMPLETE',error=str(e))
        if live_doc_name:
            partial=OUT/'FelineBellyFeet.partial.FCStd';doc.saveAs(str(partial));report['partial_native']=partial.relative_to(ROOT).as_posix()
        if path.exists():report.update(native=path.relative_to(ROOT).as_posix(),native_sha256=sha(path))
        save_report();raise
    finally:
        if live_doc_name and live_doc_name in A.listDocuments():A.closeDocument(live_doc_name)


if __name__=='__main__':run()
