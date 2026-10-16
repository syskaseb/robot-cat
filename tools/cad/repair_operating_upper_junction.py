"""One causal positive1.6mm junction web, not a component/route offset.

Three four-face seams came from bank/MTA arms touching only along an edge.
Keep all original material and editable features. Check only added web against
the full current scene, then verify current native/parameter/reopen/closed STL.
"""
import json,shutil,tempfile,time
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
from bank_upper_retained_context import prepare,P
from check_main_p0_placement import SavedShapes
from current_source_retention_context import C
from current_native_receiver_primitives import Construction
from plan_axial_source_supports import arm_box
from loom_land_port import box
from current_bank_operating_native import equal
from build_remaining_loom_supports import print_orientation
from current_work_guard import check


def valid(s):assert s.isValid() and len(s.Solids)==1 and not s.check(True)


def run():
    check();tick=time.monotonic();folder=P.OUT/'operating-supports-native'
    location_file=folder/'upper-native-junction-location.json';location=json.loads(location_file.read_text())
    native=P.ROOT/location['native'];assert P.SHA(native)==location['native_sha256']
    v=location['candidate_integral_web_bounds_mm'];assert abs(v[4]-v[1]-1.6)<1e-6 and abs(v[5]-v[2]-1.6)<1e-6
    web=box(v);scene=prepare();targets=scene['targets'];wires=scene['wires']
    roots_file=P.OUT/'current-upper-operating-roots.json';roots=json.loads(roots_file.read_text());assert roots['accepted']==38
    for r in roots['groups']:
        if r['owner']=='UpperCarrier001':continue
        for i,(a,b) in enumerate(zip(r['path'],r['path'][1:])):targets['ForeignCurrentRoot/'+r['id']+'/'+str(i)]=arm_box(a,b,r['half_mm'])
    bounds=C.ImmutableBounds();cache=C.AtomicMaterial(folder/'junction-web-pairs.json',bounds.near)
    contacts=[];checks=0
    def hit(s,t,r=0):
        nonlocal checks
        if not bounds.near(s,t,r+.0001):return None
        if r and not t.Solids and len(t.Edges)>1:return next((v for e in t.Edges if (v:=hit(s,e,r))),None)
        check();checks+=1;gap,volume=cache.check(s,t,0,r)
        if volume>1e-5 or (r and gap<r-1e-6):return dict(volume_mm3=volume,gap_mm=gap,required_mm=r)
    for n,s in targets.items():
        if n in scene['owned']['UpperCarrier001'] or not s.Solids:continue
        if (h:=hit(web,s)):contacts.append(dict(obstacle=n,**h))
    for n,(s,r) in wires.items():
        if (h:=hit(web,s,r+.25)):contacts.append(dict(obstacle=n,**h))
    original=SavedShapes().shape(native,'UpperCarrier001OperatingCurrent')
    overlap=web.common(original.copy()).Volume;assert overlap>8
    source_pins=dict(scene['pins']);files=[location_file,roots_file,native,Path(__file__),Path(__file__).with_name('current_bank_operating_native.py')]
    source_pins.update({f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files})
    result=dict(status='CAUSAL_JUNCTION_WEB_MATERIAL_GATE',web_bounds_mm=v,contacts=contacts,checks=checks,
        overlap_with_original_mm3=overlap,source_sha256=source_pins,worker_seconds=round(time.monotonic()-tick,3),physical_pass=False)
    proof=folder/'upper-junction-native.json'
    def save(status):
        result.update(status=status,worker_seconds=round(time.monotonic()-tick,3))
        tmp=proof.with_suffix('.tmp');tmp.write_text(json.dumps(result,indent=2)+'\n');tmp.replace(proof);cache.save()
    save('JUNCTION_WEB_MATERIAL_CLEAR_NATIVE_OPEN' if not contacts else 'REJECTED_JUNCTION_WEB_CONTACT')
    assert not contacts,contacts
    final=folder/'UpperOperatingJunctionCurrent.FCStd';partial=folder/'UpperOperatingJunction.partial.FCStd'
    assert not final.exists() and not partial.exists(),'Receive existing junction native, no duplicate'
    print('junction web clear',checks,'pairs; preserve all existing geometry',flush=True)
    with tempfile.TemporaryDirectory(prefix='robot-cat-upper-junction-') as td:
        work=Path(td)/'Upper.FCStd';shutil.copy2(native,work);d=A.openDocument(str(work));ops=Construction(d)
        par=d.addObject('App::VarSet','JunctionParameters');par.addProperty('App::PropertyLength','WebThickness');par.WebThickness=1.6
        try:
            base=d.getObject('UpperCarrier001OperatingCurrent');assert base
            add=ops.box(v,'ManufacturingJunctionWeb');add.Tip.setExpression('Length','JunctionParameters.WebThickness');d.recompute();equal(add.Shape,web,'Native junction web')
            current=ops.fuse([base,add],'UpperCarrier001OperatingJunctionCurrent');valid(current.Shape)
            assert original.cut(current.Shape.copy()).Volume<1e-5,'Repair lost original material'
            baseline=current.Shape.copy();d.saveAs(str(partial));result['fully_constrained_new_sketches']=ops.sketches
            save('JUNCTION_NATIVE_SAVED_BEFORE_PARAMETER')
            par.WebThickness=1.8;d.recompute();valid(current.Shape);assert current.Shape.Volume>baseline.Volume
            par.WebThickness=1.6;d.recompute();equal(current.Shape,baseline,'Junction parameter restored')
            for o in d.Objects:
                if hasattr(o,'Visibility'):o.Visibility=False
            current.Visibility=True;d.saveAs(str(final));result.update(native=final.relative_to(P.ROOT).as_posix(),native_sha256=P.SHA(final),native_object=current.Name,
                one_solid_BOP0=True,junction_parameter_restore_mm=[1.6,1.8,1.6],original_material_preserved=True,volume_mm3=current.Shape.Volume)
            save('JUNCTION_NATIVE_PARAMETER_CLEAR_REOPEN_OPEN')
        finally:
            if par.WebThickness.Value!=1.6:par.WebThickness=1.6;d.recompute()
            A.closeDocument(d.Name)
        moved=Path(td)/'RelocatedUpper.FCStd';shutil.copy2(final,moved);d=A.openDocument(str(moved));d.recompute()
        try:
            s=d.getObject(result['native_object']).Shape;valid(s);equal(s,baseline,'Junction relocated reopen')
            orientation=print_orientation(s);assert orientation['fits_with_5mm_brim']
            shape=s.copy();shape.Placement=A.Placement(A.Vector(),A.Rotation(*orientation['rotation_quaternion']))*shape.Placement
            b=shape.BoundBox;shape.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin))
            mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.05,AngularDeflection=.15,Relative=False)
            result['mesh']=dict(closed=mesh.isSolid(),nonmanifolds=mesh.hasNonManifolds(),components=mesh.countComponents())
            save('JUNCTION_CURRENT_MESH_CHECKED')
            assert result['mesh']==dict(closed=True,nonmanifolds=False,components=1),result['mesh']
            f=folder/'UpperCarrier001_junction_operating_x1.stl';mesh.write(str(f));result.update(export=f.relative_to(P.ROOT).as_posix(),export_sha256=P.SHA(f),printing=orientation,relocated_reopen=True)
            save('CAUSAL_JUNCTION_NATIVE_AND_CLOSED_STL_COMPLETE')
        finally:A.closeDocument(d.Name)
    # Complete ONLY this actual verified Upper export. The unchanged builder
    # can now resume three Frames and skip this completed Upper job.
    manifest=folder/'manifest.json';p=json.loads(manifest.read_text());r=next(r for r in p['parts'] if r['part']=='UpperCarrier001')
    assert not any(e['part']=='UpperCarrier001' for e in p['exports'])
    supplement=dict(path=proof.relative_to(P.ROOT).as_posix(),sha256=P.SHA(proof))
    r.update(native=result['native'],object=result['native_object'],volume_mm3=result['volume_mm3'],relocated_reopen=True,
        junction_supplement=supplement,junction_parameter_restore_mm=result['junction_parameter_restore_mm'])
    p['models'].append(dict(path=result['native'],sha256=result['native_sha256']))
    p['exports'].append(dict(part='UpperCarrier001',path=result['export'],sha256=result['export_sha256'],quantity=1,printing=result['printing'],junction_supplement=supplement))
    p['status']='UPPER_CAUSAL_JUNCTION_EXPORT_COMPLETE_THREE_FRAMES_OPEN'
    tmp=manifest.with_suffix('.tmp');tmp.write_text(json.dumps(p,indent=2)+'\n');tmp.replace(manifest)
    print('causal Upper web native/mesh complete',result['worker_seconds'],flush=True)


if __name__=='__main__':run()
