"""One documented U1 adapter module at current attachment, not a new selection.

Plan complete PCB/support/retention together first. Carrier holes belong to PETG,
never invented holes in the supplied PCB. Electrical wire grips/local passives
are explicitly NOT finished by this mechanical module receipt.
"""
import json
import time
import tempfile
import shutil
from pathlib import Path
import FreeCAD as A
import Part
import Mesh
import MeshPart
from current_prototype_harness_scene import context
from plan_current_main_sources import ROOT, BASE, OUT, SHA
from open_deck_p0_supports import sketch, feature
from open_deck_p0_plate import rect, circle


def box(bounds):
    x,y,z,xx,yy,zz=bounds
    return Part.makeBox(xx-x,yy-y,zz-z,A.Vector(x,y,z))


def run():
    tick=time.monotonic()
    ref=OUT/'u1-documented-adapter.json';p=json.loads(ref.read_text())
    assert p['status']=='DOCUMENTED_U1_ADAPTER_CANDIDATE_NOT_SELECTED'
    for n,h in p['source_sha256'].items():assert SHA(ROOT/n)==h,n
    dest=OUT/'u1-documented-module-checks.json';native=OUT/'U1DocumentedModule.FCStd'
    assert not dest.exists() and not native.exists(),'Receive existing result; never duplicate'
    reader,pins,targets,old=context()
    # These are the exact explicitly replaced U1 project objects, not neighbors.
    replaced=[n for n in targets if n.startswith(('U1BoardAllowance','U1Spacer','U1Insulator','U1Mount','U1_unknown_height')) and not n.endswith('Nut')]
    for n in replaced:targets.pop(n)
    result=dict(status='PENDING',contacts=[],errors=[],pairs=0,selected=False,physical_pass=False,
                replaced_current_U1_objects=replaced,reference=ref.relative_to(ROOT).as_posix(),
                preserved_attachment_axes_mm=[[84.19,40.7],[91.81,15.3]],
                plan={'PCB_center_xy_mm':[88,28],'PCB_bottom_mm':96.02,'PCB_thickness_project_mm':1.6,
                      'floor_bounds_mm':[77,8.72,90.02,99,47.28,92.02],
                      'two_foam_pads_mm':[5,3,2],'foam_is_electrically_insulating_and_not_wire_relief':True,
                      'mount_screws':'2xM2x6 into retained captiveM2nuts; oldM2x10/spacers/top washers replaced',
                      'assembly':'Bench solder/continuity first; tray screws before foam/PCB, U1 before above MTA. Reverse for service.',
                      'local_electrical_and_independent_wire_grips':'OPEN; adhesive does NOT transfer cable loads',
                      'retention':'Two removable insulating foam pads plus loose lateral stops; no pressure on any pad row'})
    d=A.newDocument('U1DocumentedModule')
    try:
        params=d.addObject('App::FeaturePython','Parameters');params.addProperty('App::PropertyLength','FloorThickness');params.FloorThickness=2
        body=d.addObject('PartDesign::Body','U1AdapterTray')
        sk=sketch(body,'TrayFloor',90.02);rect(sk,77,8.72,22,38.56)
        body.Tip=feature(body,'Pad','Floor',sk,'Parameters.FloorThickness')
        sk=sketch(body,'TrayAttachmentAxes','90.02 mm+Parameters.FloorThickness')
        for x,y in result['preserved_attachment_axes_mm']:circle(sk,x,y,2.4)
        body.Tip=feature(body,'Pocket','MountClearance',sk,'Parameters.FloorThickness')
        sk=sketch(body,'FoamPedestals','90.02 mm+Parameters.FloorThickness')
        for y in (12.22,40.22):rect(sk,85.5,y,5,3)
        body.Tip=feature(body,'Pad','InsulatingPedestals',sk,2)
        sk=sketch(body,'LooseSideStops','90.02 mm+Parameters.FloorThickness')
        for x in (77.61,97.39):
            for y in (14,39):rect(sk,x,y,1,3)
        body.Tip=feature(body,'Pad','SideStops',sk,5.6)
        d.recompute()
        assert body.Shape.isValid() and len(body.Shape.Solids)==1 and not body.Shape.check(True)
        assert all(o.FullyConstrained and o.solve()==0 for o in body.Group if o.TypeId=='Sketcher::SketchObject')
        # Native editable exact manufacturer outline, physically unpopulated SOIC side.
        pcb=d.addObject('PartDesign::Body','Adafruit1208PCB')
        import Sketcher
        sk=sketch(pcb,'ManufacturerOutline',96.02)
        for seg in p['board_outline_segments_mm']:
            x,y,xx,yy=seg
            a=A.Vector(88+(17.78-x)-8.89,28+y-17.78,0)
            b=A.Vector(88+(17.78-xx)-8.89,28+yy-17.78,0)
            i=sk.addGeometry(Part.LineSegment(a,b),False);sk.addConstraint(Sketcher.Constraint('Block',i))
        pcb.Tip=feature(pcb,'Pad','ProjectBoardThickness',sk,1.6)
        sk=sketch(pcb,'Actual28Drills',97.62)
        for x in (80.38,95.62):
            for i in range(14):circle(sk,x,44.51-i*2.54,1.016)
        pcb.Tip=feature(pcb,'Pocket','SupplierDrills',sk,1.6)
        pcb.addProperty('App::PropertyString','Qualification');pcb.Qualification='Manufacturer outline/drills; project1.6mm thickness, not measured board'
        parts={'U1AdapterTray':body.Shape}
        d.recompute();parts['Adafruit1208PCB']=pcb.Shape
        chip=box([85.75,24.7,97.62,90.25,32.6,98.82])
        ob=d.addObject('Part::Feature','TI_PW_MaxBody');ob.Shape=chip
        ob.addProperty('App::PropertyString','Qualification');ob.Qualification='TI body max4.5x7.9x1.2 at+0.65 longitudinal chip shift; leads separate'
        parts[ob.Name]=chip
        for i,y in enumerate((12.22,40.22),1):
            foam=box([85.5,y,94.02,90.5,y+3,96.02]);parts['Foam'+str(i)]=foam
            ob=d.addObject('Part::Feature','Foam'+str(i));ob.Shape=foam
        # M2x6 reference geometry: standard nominal head4x2, shank2x6.
        for i,(x,y) in enumerate(result['preserved_attachment_axes_mm'],1):
            screw=Part.makeCylinder(2,2,A.Vector(x,y,92.02)).fuse(Part.makeCylinder(1,6,A.Vector(x,y,86.02)))
            ob=d.addObject('Part::Feature','M2x6_'+str(i));ob.Shape=screw;parts[ob.Name]=screw
        # Only changed interfaces. Shared context includes actual current MAIN/BUS.
        for a,s in parts.items():
            assert s.isValid(),a
            for b,t in targets.items():
                if a.startswith('M2x6_') and b.startswith('U1Mount') and b.endswith('Nut'):
                    continue  # Retained mating nut; intended threaded engagement.
                if not s.BoundBox.intersect(t.BoundBox):continue
                result['pairs']+=1
                try:
                    assert t.isValid(),b
                    v=sum(x.common(y).Volume for x in s.Solids for y in t.Solids)
                    if v>1e-5:result['contacts'].append(dict(a=a,b=b,volume_mm3=v))
                except Exception as e:result['errors'].append(dict(a=a,b=b,error=repr(e)))
            for b,(curve,rad) in old.items():
                expanded=s.BoundBox;expanded.enlarge(rad)
                if not expanded.intersect(curve.BoundBox):continue
                result['pairs']+=1
                dd=curve.distToShape(s)[0]
                if dd<rad-1e-5:result['contacts'].append(dict(a=a,b=b,distance_mm=dd,required_mm=rad))
        # Screw joints/foam bearings are intentional only within this new module.
        for a,b in [('U1AdapterTray','Adafruit1208PCB'),('U1AdapterTray','TI_PW_MaxBody'),('Adafruit1208PCB','TI_PW_MaxBody')]:
            v=parts[a].common(parts[b]).Volume
            assert v<1e-5,(a,b,v)
        if not result['contacts'] and not result['errors']:
            initial=body.Shape.Volume;params.FloorThickness=2.5;d.recompute();assert body.Shape.isValid() and body.Shape.Volume>initial
            params.FloorThickness=2;d.recompute();assert abs(body.Shape.Volume-initial)<1e-5
            d.saveAs(str(native));A.closeDocument(d.Name)
            with tempfile.TemporaryDirectory(prefix='robot-cat-u1-document-reopen-') as temp:
                copy=Path(temp)/native.name;shutil.copy2(native,copy);d=A.openDocument(str(copy));d.recompute()
                assert d.U1AdapterTray.Shape.isValid() and abs(d.U1AdapterTray.Shape.Volume-initial)<1e-5
            stl=OUT/'U1AdapterTray.stl';s=d.U1AdapterTray.Shape.copy();s.translate(A.Vector(-s.BoundBox.XMin,-s.BoundBox.YMin,-s.BoundBox.ZMin))
            MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False).write(str(stl))
            mesh=Mesh.Mesh(str(stl));assert mesh.isSolid() and mesh.countComponents()==1
            assert max(mesh.BoundBox.XLength+10,mesh.BoundBox.YLength+10,mesh.BoundBox.ZLength)<256
            result.update(native=native.relative_to(ROOT).as_posix(),native_sha256=SHA(native),export=stl.relative_to(ROOT).as_posix(),export_sha256=SHA(stl),
                          editable_parameter_cycle=[2,2.5,2],fresh_relocated_reopen=True)
        result['status']='REJECTED_DOCUMENTED_U1_MODULE' if result['contacts'] or result['errors'] else 'DOCUMENTED_U1_MECHANICAL_MODULE_ONLY_E1_OPEN'
    finally:
        if d.Name in A.listDocuments():A.closeDocument(d.Name)
    pins.update((Path(__file__),ref));result.update(source_sha256={**reader.hashes,**{p.relative_to(ROOT).as_posix():SHA(p) for p in pins}},worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','contacts','errors','pairs','worker_seconds')}),flush=True)


if __name__=='__main__':run()
