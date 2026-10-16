"""One native integral BUS ground guide, no private copy of shared chassis.

Editable new pads/pocket/foot; accepted Upper is an external native link.
One nominal lacing reference and the selected rebuilt wire are NOT prints.
"""
import json,shutil,tempfile,time
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
from phase1_source_protection import ROOT,BASE,BODY,OUT,check,sha
from plan_bus_ground_mid_guide import material
from build_phase1_source_mounts import rectangle,signature,qualified,dependencies
from open_deck_p0_supports import sketch,feature
from open_deck_p0_plate import rect
from phase1_stl_preflight import inspect,fit
from check_main_p0_placement import SavedShapes

MODEL=OUT/'BUSGroundGuideCurrent.FCStd'

def world_box(v,m):
    points=[m.multVec(A.Vector(x,y,z)) for x in (v[0],v[3]) for y in (v[1],v[4]) for z in (v[2],v[5])]
    return [min(p.x for p in points),min(p.y for p in points),min(p.z for p in points),
            max(p.x for p in points),max(p.y for p in points),max(p.z for p in points)]

def run():
    check();tick=time.monotonic();file=OUT/'BUS-ground-guide-west-plan.json';plan=json.loads(file.read_text())
    assert plan['status']=='BUS_MID_GUIDE_COMMON_SPACE_CLEAR_NATIVE_PENDING' and not plan['contacts']
    for n,h in plan['source_sha256'].items():assert sha(ROOT/n)==h,n
    assert not MODEL.exists(),'Receive existing result first'
    selected=json.loads((BASE/'phase1-current-print-selection.json').read_text())
    row=next(r for r in selected['prints'] if r['identity']=='UpperCarrier001');source_file=ROOT/row['native']
    reader=SavedShapes();saved=reader.shape(source_file,row['native_object']);saved_signature=signature(saved)
    expected,band,recipe=material(True)
    doc=A.newDocument('BUSGroundGuideCurrent');doc.saveAs(str(OUT/'BUSGroundGuideCurrent.building.FCStd'))
    params=doc.addObject('App::VarSet','GuideParameters');params.addProperty('App::PropertyLength','FootWidth');params.FootWidth=4
    body=doc.addObject('PartDesign::Body','IntegralBUSMidGuide')
    foot=recipe['foot_xyz_size'];stem=recipe['stem_xyz_size']
    rectangle(body,'StructuralBeamFoot',foot[2],foot[0],foot[1],foot[3],foot[4],foot[5],'GuideParameters.FootWidth')
    rectangle(body,'ShortGuideStem',stem[2],stem[0],stem[1],stem[3],stem[4],stem[5])
    m=A.Matrix(*recipe['profile']['local_to_world'])
    for i,v in enumerate(recipe['profile']['pads']):
        x,y,z,X,Y,Z=world_box(v,m);rectangle(body,'GuidePad'+str(i),z,x,y,X-x,Y-y,Z-z)
    outer=world_box(recipe['profile']['ring_cut']['outer'],m);inner=world_box(recipe['profile']['ring_cut']['inner'],m)
    s=sketch(body,'IndependentLacingPassagePlan',outer[5])
    for v in (outer,inner):rect(s,v[0],v[1],v[3]-v[0],v[4]-v[1])
    body.Tip=feature(body,'Pocket','IndependentLacingPassage',s,outer[5]-outer[2]);doc.recompute()
    delta=body.Shape.copy().cut(expected.copy()).Volume+expected.copy().cut(body.Shape.copy()).Volume
    assert delta<1e-4,('Native differs from common checked guide',delta)
    source=A.openDocument(str(source_file));old=source.getObject(row['native_object']);assert old
    assert max(abs(a-b) for a,b in zip(signature(old.Shape),saved_signature))<1e-5,'Opening inherited native changed geometry'
    link=doc.addObject('App::Link','RetainedUpperCarrier');link.LinkedObject=old
    final=doc.addObject('Part::MultiFuse','UpperCarrierBUSMidGuideCurrent');final.Shapes=[link,body];final.Refine=True
    doc.recompute();assert saved.copy().cut(final.Shape.copy()).Volume<1e-5
    route_file=OUT/'W003RetainedUpperBypass.json';route=json.loads(route_file.read_text());assert sha(ROOT/route['path'])==route['sha256']
    route_shape=Part.Shape();route_shape.read(str(ROOT/route['path']));assert route_shape.isValid()
    wire=doc.addObject('Part::Feature','W003Current');wire.Shape=route_shape
    wire.addProperty('App::PropertyString','Identity');wire.Identity='W003 BUS.G -> G2.4; same SR900 physical cable'
    wire.addProperty('App::PropertyString','Definition');wire.Definition='Versioned plan_bus_ground_source_bypass.py; inherited endpoint shapes and rebuilt R10 arcs, not claimed a native Sketcher3D wire.'
    lace=doc.addObject('Part::Feature','BUSMidLacing');lace.Shape=band
    lace.addProperty('App::PropertyString','MaterialAndGate');lace.MaterialAndGate='AlphaWire802534B one150mm blank. Inherited nominal flat packing profile1.6764x0.381, knot adjustable in unpowered phase2; no retention-strength rating.'
    names=[final.Name];baseline=qualified(doc,names);doc.saveAs(str(MODEL))
    print('BUS guide saved before parameter test',flush=True)
    params.FootWidth=4.2;changed=qualified(doc,names);assert changed[final.Name][0]>baseline[final.Name][0]
    params.FootWidth=4;restored=qualified(doc,names)
    assert max(abs(a-b) for a,b in zip(restored[final.Name],baseline[final.Name]))<1e-5
    doc.save();shape=final.Shape.copy();rotation=A.Rotation(*row['printing']['rotation_quaternion'])
    shape.Placement=A.Placement(A.Vector(),rotation)*shape.Placement;b=shape.optimalBoundingBox();shape.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
    export=OUT/'UpperCarrierBUSMidGuideCurrent_x1.stl'
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.25,Relative=False);mesh.write(str(export))
    measured=inspect(export.read_bytes());assert measured['closed'] and measured['components']==1 and fit(measured['size_mm']),measured
    files=dependencies(MODEL)
    for d in list(A.listDocuments().values()):A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix='cat-bus-guide-relocated-') as td:
        root=Path(td)
        for f in files:
            dest=root/f.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
        moved=A.openDocument(str(root/MODEL.relative_to(ROOT)));again=qualified(moved,names)
        assert max(abs(a-b) for a,b in zip(again[names[0]],baseline[names[0]]))<1e-5
        assert Path(moved.RetainedUpperCarrier.LinkedObject.Document.FileName).resolve().is_relative_to(root.resolve())
        assert sha(source_file)==reader.hashes[source_file.relative_to(ROOT).as_posix()]
        for d in list(A.listDocuments().values()):A.closeDocument(d.Name)
    result=dict(status='NATIVE_BUS_MID_GUIDE_W003_PARAMETER_REOPEN_STL_COMPLETE',selected=False,W5_complete=False,M4_complete=False,physical_pass=False,
        native=MODEL.relative_to(ROOT).as_posix(),native_object=names[0],native_sha256=sha(MODEL),
        part=dict(identity='UpperCarrier001',part='UpperCarrier001',native=MODEL.relative_to(ROOT).as_posix(),native_object=names[0],
                  path=export.relative_to(ROOT).as_posix(),sha256=sha(export),quantity=1,printing=dict(**measured,rotation_quaternion=list(rotation.Q),brim_each_mm=5,fits_with_5mm_brim=True)),
        wire_object='W003Current',lacing_object='BUSMidLacing',additional_lacing_blanks=1,lacing_blank_mm=150,
        parameter_mm=[4,4.2,4],relocated_reopen=True,all_sketches_fully_constrained=True,original_upper_material_preserved=True,
        checked_material_symmetric_difference_mm3=delta,beam_joint_overlap_mm3=plan['beam_joint_overlap_mm3'],
        source_sha256={**{f.relative_to(ROOT).as_posix():sha(f) for f in files},file.relative_to(ROOT).as_posix():sha(file),route_file.relative_to(ROOT).as_posix():sha(route_file),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'BUS-ground-guide-native.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],seconds=result['worker_seconds'])),flush=True)

if __name__=='__main__':run()
