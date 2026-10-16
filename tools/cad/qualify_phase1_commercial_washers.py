"""One commercial DIN433 OD4.5 overlay; only newly added annuli checked.

Current accepted print/wire geometry is immutable. Saved valid supplier solids
are used, not the invalid historical BUS compound. No physical fit claim.
"""
import json,time,tempfile,shutil
from pathlib import Path
import FreeCAD as A, Part, Sketcher
from plan_current_harness_interfaces import ROOT,BASE,SHA
from check_main_p0_placement import SavedShapes,prop
from current_work_guard import check


def run():
    check();tick=time.monotonic();reader=SavedShapes()
    source=BASE/'body-harness-checkpoint/current-w5-assembly/CurrentW5AssemblyNeutral.FCStd'
    out=BASE/'commercial-hardware';out.mkdir(exist_ok=True)
    model=out/'CommercialWashers.FCStd';report=out/'washer-checks.json'
    assert not model.exists() and not report.exists(),'Receive existing worker, do not duplicate'
    objects=reader.doc(source);targets={};washers={};errors=[];contacts=[];pairs=0
    for name,obj in objects.items():
        if prop(obj,'Shape') is None and prop(obj,'LinkedObject') is None:continue
        s=reader.shape(source,name)
        if s.isNull():continue
        assert s.isValid(),('Invalid selected current shape',name)
        targets[name]=s
        b=s.BoundBox
        if 'Washer' in name and abs(b.XLength-4.3)<1e-5 and abs(b.YLength-4.3)<1e-5 and abs(b.ZLength-.3)<1e-5:
            washers[name]=s
    assert len(washers)==20,len(washers)
    print('Current saved shapes',len(targets),'commercial washers',len(washers),flush=True)
    d=A.newDocument('CommercialWashers');rows=[]
    try:
        body=d.addObject('PartDesign::Body','DIN433_M2')
        sk=d.addObject('Sketcher::SketchObject','WasherProfile');body.addObject(sk)
        for rad in (2.25,1.1):
            i=sk.addGeometry(Part.Circle(A.Vector(0,0,0),A.Vector(0,0,1),rad),False)
            sk.addConstraint(Sketcher.Constraint('Radius',i,rad))
            sk.addConstraint(Sketcher.Constraint('DistanceX',i,3,0.0));sk.addConstraint(Sketcher.Constraint('DistanceY',i,3,0.0))
        pad=body.newObject('PartDesign::Pad','WasherPad');pad.Profile=sk;pad.Length=.3
        d.recompute();assert body.Shape.isValid() and len(body.Shape.Solids)==1
        v=body.Shape.Volume;sk.setDatum(0,A.Units.Quantity('2.3 mm'));d.recompute();assert body.Shape.Volume>v
        sk.setDatum(0,A.Units.Quantity('2.25 mm'));d.recompute();assert abs(body.Shape.Volume-v)<1e-6
        for name,old in washers.items():
            check();b=old.BoundBox;pos=A.Vector((b.XMin+b.XMax)/2,(b.YMin+b.YMax)/2,b.ZMin)
            new=body.Shape.copy();new.translate(pos);extra=new.cut(old)
            assert extra.isValid() and extra.Volume>0
            for other,t in targets.items():
                if other==name or not extra.BoundBox.intersect(t.BoundBox):continue
                pairs+=1
                try:
                    common=extra.common(t);assert common.isValid()
                    if common.Volume>1e-5:contacts.append(dict(washer=name,other=other,added_contact_mm3=common.Volume))
                except Exception as exc:errors.append(dict(washer=name,other=other,error=str(exc)))
            link=d.addObject('App::Link','Installed_'+name);link.LinkedObject=body;link.LinkPlacement=A.Placement(pos,A.Rotation())
            rows.append(dict(replaces=name,object=link.Name,centre_xy_mm=[pos.x,pos.y],bottom_z_mm=pos.z,OD_mm=4.5,ID_mm=2.2,thickness_mm=.3))
        d.recompute();d.saveAs(str(model));A.closeDocument(d.Name);d=None
        with tempfile.TemporaryDirectory(prefix='cat-commercial-washers-') as temp:
            f=Path(temp)/model.name;shutil.copy2(model,f);r=A.openDocument(str(f));r.recompute()
            assert len([o for o in r.Objects if o.TypeId=='App::Link'])==20
            assert abs(r.DIN433_M2.Shape.Volume-v)<1e-6;A.closeDocument(r.Name)
        result=dict(status='COMMERCIAL_WASHERS_CHANGED_MATERIAL_CLEAR' if not errors+contacts else 'COMMERCIAL_WASHER_LAYOUT_CHANGE_REQUIRED',
            selected=False,physical_pass=False,rows=rows,contacts=contacts,errors=errors,changed_pairs=pairs,
            native=model.relative_to(ROOT).as_posix(),native_sha256=SHA(model),
            radial_parameter_roundtrip_mm=[2.25,2.3,2.25],relocated_reopen=True,
            source_sha256={source.relative_to(ROOT).as_posix():SHA(source),Path(__file__).relative_to(ROOT).as_posix():SHA(Path(__file__))},
            scope='Only20 board washers grow4.3to4.5. Accepted prints/wires unchanged. Exact added material contacts, not bbox collisions. No supplier tolerance/physical fit approval.',
            worker_seconds=round(time.monotonic()-tick,3))
        report.write_text(json.dumps(result,indent=2)+'\n',newline='\n')
        print(json.dumps({k:result[k] for k in ('status','changed_pairs','contacts','errors','worker_seconds')}),flush=True)
    finally:
        if d:A.closeDocument(d.Name)


if __name__=='__main__':run()
