"""One editable four-copy hip grip from the received current static interface.

Native primitives/rings/cuts, clearance parameter, one closed STL, relocation.
Do not infer motion, pullout strength, physical fit or final selection.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,shutil,tempfile
import w5_source_hip_grip_window as H
from servo_fuse_inputs_r1 import save,sha
ROOT=H.ROOT;BASE=H.BASE;OUT=BASE/'w5-source-hip-native-r1'
CAD=ROOT/'hardware/cad/studies/w5-source-hip-native-r1'
INTERFACE=BASE/'w5-source-hip-harness-interface-r1/checks.json'


def main():
    import FreeCAD as A,Part,MeshPart
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    proof=json.loads(INTERFACE.read_text(encoding='utf-8'))
    assert not proof['hits'] and not proof['errors'] and proof['current_body_wires']==49
    for rel,h in proof['source_sha256'].items():assert sha(ROOT/rel)==h,rel
    bpp=H.OUT/'blueprint.json';bp=json.loads(bpp.read_text(encoding='utf-8'));s=bp['specification'];assert bp['print_quantity']==4
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    d=A.newDocument('HipSourceGrip');target=CAD/'HipSourceGrip.FCStd';d.saveAs(str(target))
    p=d.addObject('App::VarSet','GripParameters')
    for name,value in [('CaseClearance',.2),('CarrierHalfHeight',14.85),('JawWall',1.5),('CableEntryWidth',6.1)]:
        p.addProperty('App::PropertyLength',name);setattr(p,name,value)
    p.addProperty('App::PropertyString','Readiness');p.Readiness='Four copies, static interface received; motion/mounting/stock open'
    zi='GripParameters.CarrierHalfHeight + GripParameters.CaseClearance';zo=zi+' + GripParameters.JawWall'
    def box(name,b):
        o=d.addObject('Part::Box',name);o.Length,o.Width,o.Height=[b[i+3]-b[i] for i in range(3)]
        o.Placement.Base=A.Vector(*b[:3]);return o
    def cylinder(name,c,r,h):
        o=d.addObject('Part::Cylinder',name);o.Radius=r;o.Height=h
        o.Placement=A.Placement(A.Vector(*c),A.Rotation(A.Vector(0,0,1),A.Vector(0,1,0)));return o
    def cut(name,b,t):
        o=d.addObject('Part::Cut',name);o.Base=b;o.Tool=t;o.Refine=False;return o
    def compound(name,objs):
        o=d.addObject('Part::Compound',name);o.Links=objs;return o
    def union(name,objs):
        o=d.addObject('Part::MultiFuse',name);o.Shapes=objs;o.Refine=False;return o
    roots=[]
    for name,b in s['root_boxes_mm'].items():
        o=box(name,b)
        if name=='TopJaw':o.setExpression('Placement.Base.z',zi)
        if name in ('BottomJaw','BackJaw'):o.setExpression('Placement.Base.z','-('+zo+')')
        if name=='BackJaw':o.setExpression('Height','2 * ('+zo+')')
        if name=='BridgeRiser':
            o.setExpression('Placement.Base.z',zi);o.setExpression('Height','22.5 mm - ('+zi+')')
        roots.append(o)
    cx,cy,cz=s['source_saddle_center_in_PCB_frame_mm'];roots.append(cylinder('InsulationSaddle',[cx,cy-3,cz],5.5,6))
    entry=box('TopCableEntry',[cx-3.05,cy-4,cz,cx+3.05,cy+4,cz+7])
    entry.setExpression('Length','GripParameters.CableEntryWidth')
    entry.setExpression('Placement.Base.x',str(cx)+' mm - GripParameters.CableEntryWidth / 2')
    tools=[cylinder('CableOpening',[cx,cy-4,cz],3.05,8),entry]
    def half_ring(name,ri,ro,upper):
        ann=cut(name+'Annulus',cylinder(name+'Outer',[cx,cy-1.5,cz],ro,3),
            cylinder(name+'Inner',[cx,cy-1.6,cz],ri,3.2))
        hb=[cx-ro-.1,cy-1.6,cz if upper else cz-ro-.1,cx+ro+.1,cy+1.6,cz+ro+.1 if upper else cz]
        o=d.addObject('Part::Common',name);o.Base=ann;o.Tool=box(name+'HalfPlane',hb);o.Refine=False;return o
    tools.extend([half_ring('BackTieChannel',5.25,6.95,False),half_ring('CableTieChannel',2.5,4.2,True)])
    tools.extend(box('TieCorner'+str(i),b) for i,b in enumerate(s['tie_corner_slots_mm']))
    rear=box('RearBodyTieWindow',s['rear_band_window_mm'])
    rear.setExpression('Placement.Base.z','-('+zo+') - 0.1 mm');rear.setExpression('Height','2 * ('+zo+') + 0.2 mm')
    top=box('TopBodyTieWindow',s['top_body_tie_window_mm']);top.setExpression('Placement.Base.z','('+zo+') - 0.1 mm')
    tools.extend([rear,top]);final=cut('SourceClipHipFinished',union('CarrierRootAndSaddle',roots),compound('GripChannels',tools))
    d.recompute();expected=H.proposed(A,Part)[0]['Clip'];actual=final.Shape
    assert actual.isValid() and len(actual.Solids)==1 and not (actual.check(True) or [])
    delta=actual.cut(expected).Volume+expected.cut(actual).Volume;assert delta<max(1e-5,actual.Volume*1e-8),delta
    nominal=actual.Volume;print('SOURCE_HIP_NATIVE','nominal_received',nominal,flush=True)
    p.CaseClearance=.3;d.recompute();assert final.Shape.isValid() and len(final.Shape.Solids)==1
    probe=final.Shape.Volume;assert abs(probe-nominal)>1e-5
    p.CaseClearance=.2;d.recompute();assert abs(final.Shape.Volume-nominal)<max(1e-5,nominal*1e-8)
    assert not (final.Shape.check(True) or [])
    for o in d.Objects:
        if hasattr(o,'ViewObject') and o.ViewObject:o.ViewObject.Visibility=o==final
    d.save();shape=final.Shape;shape.exportBrep(str(CAD/'SourceClipHip_CANDIDATE_LOCAL.brep'))
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    b=mesh.BoundBox;size=[b.XLength,b.YLength,b.ZLength];assert max(size)+6<=256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'SourceClipHip_UNSELECTED_x4.stl'))
    count=len(d.Objects);A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-source-hip-') as td:
        copy=Path(td)/target.name;shutil.copy2(target,copy);opened=A.openDocument(str(copy));opened.recompute()
        restored=opened.getObject('SourceClipHipFinished').Shape
        assert restored.isValid() and len(restored.Solids)==1 and abs(restored.Volume-nominal)<max(1e-5,nominal*1e-8)
        assert len(A.listDocuments())==1;A.closeDocument(opened.Name)
    finish=datetime.now(timezone.utc);pins=[Path(__file__),Path(H.__file__),Path(H.R2.__file__),INTERFACE,bpp,H.OUT/'checks.json']
    save(OUT/'checks.json',dict(status='ONE_EDITABLE_FOUR_COPY_HIP_SOURCE_GRIP_NATIVE_COMPLETE',objects=count,
        print_quantity=4,new_print_identity='SourceClipHip',solids=1,BOP_errors=0,dimensions_mm=size,
        nominal_mm3=nominal,probe_mm3=probe,parameter_probe_mm=[.2,.3,.2],restored=True,relocated_reopen=True,closed_STLs=1,
        minimum_bridge_side_web_mm=1.25,minimum_rear_side_web_mm=1.25,open_cable_entry_width_mm=6.1,
        static_interface_receipt=INTERFACE.relative_to(ROOT).as_posix(),body_T18L_count=4,insulation_T18I_count=4,
        root_capture=s['root_capture'],assembly=s['assembly'],whole_motion_mounting_and_stock_pending=True,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in pins},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in CAD.iterdir() if q.suffix.lower() in ('.fcstd','.brep','.stl')},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False))
    print('SOURCE_HIP_NATIVE','complete',flush=True)


if __name__=='__main__':main()
