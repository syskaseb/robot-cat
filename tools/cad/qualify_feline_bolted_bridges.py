"""Verify the actual bolted load path, not an unnecessary new direct seat.

Unchanged four brackets already clear common material/known wires/36poses.
Two actual axial contact interfaces per bolt connect them through the R4
mounting plate to the frame. No strength/torque/physical or closed-skin claim.
"""
import copy,json,time,math
from pathlib import Path
import FreeCAD as A
import Part
import MeshPart
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import MODEL,OUT


def flat_faces(shape,z):
    return [f for f in shape.Faces if f.BoundBox.ZLength<1e-7 and abs(f.BoundBox.ZMin-z)<1e-6]


def common_faces(a,faces):
    result=[]
    for f in faces:
        c=a.common(f);assert c.isNull() or c.isValid()
        if c.Area>1e-5:result.extend(c.Faces)
    return result


def main():
    tick=time.monotonic();reader=SavedShapes();mf=OUT/'belly-feet-native.json';ff=OUT/'belly-feet-fit.json'
    m=json.loads(mf.read_text());old=json.loads(ff.read_text());native=ROOT/m['native'];native_before=sha(native)
    assert native_before==m['native_sha256']
    assert old['status']=='FEET_SHARED_FIT_REJECTED' and not old['contacts'] and not old['wire_clearance']
    assert len(old['poses'])==36 and len(old['errors'])==4
    assert all(e['error']=='No actual frame seat material witnessed' for e in old['errors'])
    for n,h in old['source_sha256'].items():assert sha(ROOT/n)==h,n
    plate=reader.shape(MODEL,'Print_P0_BATTERY_PLATE_R4')
    bottom,top=flat_faces(plate,-1.5),flat_faces(plate,0);assert bottom and top
    report=copy.deepcopy(old)
    report.update(status='BOLTED_BRIDGE_LOAD_PATH_CHECK_RUNNING',errors=[],seat_contacts=[],
        supersedes_local_criterion='Unrequired direct Side22bearing atZ-2; original rejected receipt preserved at76604ec',
        load_path_criterion='BOLTED_FRAME_BRIDGE_VIA_RETAINED_R4_PLATE_20261017',
        retained_native_exactly_unchanged=True,reused_previous_new_interface_pairs=old['pairs'],
        reused_previous36poses=True,old_errors_not_declared_passed=True,
        new_bearing_face_checks=[],load_qualified=False,physical_pass=False,
        assembly_service_open=['Whole closed-skin tool access not yet qualified',
            'R4plate removal requires chassis propped/unloaded and feet detached first; do not drop plate through attached bridges',
            'Actual PETG stiffness, fastener torque, delivered fit and static load test remain phase2 gates'])
    destination=OUT/'belly-feet-bolted-path.json'
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3)
        destination.write_text(json.dumps(report,indent=2)+'\n')
    save()
    for row in m['parts']:
        foot=reader.shape(native,row['object']);bosses=flat_faces(foot,-1.5);assert len(bosses)==2
        frame_name='Ref_Material_P0_Frame'+('Front' if row['pad_center_mm'][0]<0 else 'Rear')+'20_0_0'
        frame=reader.shape(MODEL,frame_name);frame_faces=flat_faces(frame,0);assert frame_faces
        contacts=[]
        for x,y in row['axes_mm']:
            face=min(bosses,key=lambda f:(f.CenterOfMass.x-x)**2+(f.CenterOfMass.y-y)**2)
            assert math.hypot(face.CenterOfMass.x-x,face.CenterOfMass.y-y)<.01
            foot_plate_area=sum(c.Area for c in common_faces(face,bottom))
            projected=face.copy();projected.translate(A.Vector(0,0,1.5))
            plate_patch=common_faces(projected,top)
            plate_frame_area=sum(c.Area for p in plate_patch for c in common_faces(p,frame_faces))
            assert foot_plate_area>1 and plate_frame_area>1,(row['object'],x,y,foot_plate_area,plate_frame_area)
            contacts.append(dict(axis_mm=[x,y],foot_to_R4plate_face_z_mm=-1.5,
                foot_to_plate_actual_area_mm2=foot_plate_area,plate_to_frame_face_z_mm=0,
                plate_to_frame_actual_area_mm2=plate_frame_area,frame=frame_name,
                area_is_geometric_contact_not_load_capacity=True))
        report['seat_contacts'].append(dict(foot=row['object'],load_via_R4plate=True,contacts=contacts))
        report['new_bearing_face_checks'].extend(contacts)
    assert sha(native)==native_before
    # Export the current four originals root-down. A small support under the
    #0.5mm boss/bridge step is required; no slicer/print approval is claimed.
    for row in m['parts']:
        s=reader.shape(native,row['object'])
        mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.1,AngularDeflection=.3,Relative=False)
        mesh.transform(A.Rotation(A.Vector(1,0,0),180).toMatrix())
        assert mesh.isSolid() and not mesh.hasNonManifolds() and mesh.countComponents()==1
        b=mesh.BoundBox;mesh.translate(-b.XMin,-b.YMin,-b.ZMin)
        assert max(b.XLength,b.YLength,b.ZLength)<=252
        target=ROOT/row['stl'];mesh.write(str(target));row['stl_sha256']=sha(target)
        row.update(print_extents_mm=[b.XLength,b.YLength,b.ZLength],external_fit_complete=True,
            print_orientation='Root-seat-down,180degX; support the0.5mm bridge/boss step')
    report.update(status='FOUR_BOLTED_BELLY_BRIDGES_GEOMETRIC_LOAD_PATH_CLEAR',
        native_sha256=native_before,printed_bodies=4,constrained_sketches=16,
        same_known61approaches_and8factory_paths=True,
        source_sha256={**old['source_sha256'],**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))})
    m.update(status='FOUR_BOLTED_BELLY_BRIDGES_GEOMETRY_CLEAR_LOAD_TEST_OPEN',
        external_fit_complete=True,accepted_for_geometry_continuation=True,selected_for_print=False,
        load_path='Annular ground foot -> hollow stem ->3mm bridge -> two boss seats -> retained R4mountingplate -> actual FrameFront20/Rear20 face at same twoM2axes',
        actual_clamp_contacts=report['seat_contacts'],
        print_gate='Root-seat-down export; support0.5mm boss/bridge step. Slicer/printed fit/torque/load test phase2; not print-ready.',
        bolted_path_receiver_seconds=round(time.monotonic()-tick,3),
        source_sha256={**m['source_sha256'],Path(__file__).with_name('build_feline_belly_feet.py').relative_to(ROOT).as_posix():sha(Path(__file__).with_name('build_feline_belly_feet.py')),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))})
    mf.write_text(json.dumps(m,indent=2)+'\n')
    report['source_sha256'][mf.relative_to(ROOT).as_posix()]=sha(mf)
    save();ff.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],bearing_face_interfaces=16,native_unchanged=True,
        total_frame_bearing_mm2=sum(r['plate_to_frame_actual_area_mm2'] for r in report['new_bearing_face_checks']),seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()
