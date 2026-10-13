"""Measure actual candidate attachment faces, before planning support arms.

This is not a collision/retention certificate or a hole in a purchased case.
Keep several actual faces in ONE shared layout record. Provisional adhesive
case roots need compatibility/load trials. Frame roots extend the existing
owner and must not duplicate or silently cut the chassis.
"""
import json
import math
import time
import zipfile
from pathlib import Path
import FreeCAD as A
import Part
import build_complete_source_carriers as B

P = B.P


def patch_faces(shape, goal, neighbours, owner, fixed_frame=False):
    candidates = []
    rejected = []
    width,height=(6,4) if fixed_frame else (10,8)
    for index, face in enumerate(shape.Faces):
        if not isinstance(face.Surface, Part.Plane) or face.Area < width*height:
            continue
        centre = face.CenterOfMass
        u, v = face.Surface.parameter(centre)
        normal = face.normalAt(u, v)
        normal.normalize()
        if shape.isInside(centre+normal*.1, 1e-6, False):
            normal = -normal
        tangent = A.Vector(1, 0, 0)
        tangent -= normal*tangent.dot(normal)
        if tangent.Length < .1:
            tangent = A.Vector(0, 1, 0)-normal*normal.y
        tangent.normalize()
        other = normal.cross(tangent)
        corners = [centre+tangent*x+other*y for x, y in
                   ((-width/2,-height/2),(width/2,-height/2),
                    (width/2,height/2),(-width/2,height/2),(-width/2,-height/2))]
        patch = Part.Face(Part.makePolygon(corners))
        contact = face.common(patch)
        if abs(contact.Area-width*height) > 1e-5:
            continue
        # A housing-only face can be buried under its real same-stage end
        # cover. Qualify the WHOLE proposed root stub against nearby material
        # before spending minutes assembling mesh/path reservations.
        stub=patch.extrude(normal*(3 if fixed_frame else 6.2))
        blockers=[]
        for name,s in neighbours.items():
            if name==owner:continue
            if not stub.BoundBox.intersect(s.BoundBox):continue
            if stub.distToShape(s)[0]>1e-5:continue
            common=stub.common(s)
            assert common.isNull() or common.isValid(),(owner,name,'Invalid contact result')
            if common.Volume>1e-5:blockers.append(dict(target=name,volume_mm3=common.Volume))
        if blockers:
            rejected.append(dict(owner=owner,face_index=index+1,blockers=blockers))
            continue
        # Merely having distance0 to a solid does not prove a useful area.
        # The exact face-face intersection above establishes this plane.
        candidates.append(dict(face_index=index+1, plane_centre_world_mm=list(centre),
                               outward_normal=list(normal), in_plane_axis=list(tangent),
                               patch_bounds_plane_mm=[width,height], actual_patch_area_mm2=contact.Area,
                               root_stub_nominal_clear_vs_retained_rest=True,
                               root_stub_depth_mm=3 if fixed_frame else 6.2,
                               outer_arm_root_world_mm=list(centre+normal*(3 if fixed_frame else 6.2)),
                               distance_to_group_centre_mm=(centre-A.Vector(*goal)).Length))
    return sorted(candidates, key=lambda r:r['distance_to_group_centre_mm'])[:4],rejected


def run():
    tick=time.monotonic()
    fp=P.OUT/'remaining-loom-roots-plan.json'
    plan=json.loads(fp.read_text())
    for n, digest in plan['source_sha256'].items():
        assert P.SHA(P.ROOT/n)==digest, n
    reader=B.H.P.SavedShapes()
    targets, _, archive, sf, ff=B.current_scene(reader)
    zf=P.ROOT/'hardware/simulation/v35/inputs.zip'
    with zipfile.ZipFile(zf) as z:
        members=json.loads(z.read('geometry.json'))['components']
    groups=[]
    for group in plan['groups']:
        goal=[sum(r['centre_world_mm'][i] for r in group['lands'])/len(group['lands']) for i in range(3)]
        if group['id'].endswith('HipExtension'):
            groups.append(dict(id=group['id'], owner_stage=group['owner_stage'],
                               preserved_owner=group['preserved_owner'], root_world_mm=group['root_world_mm'],
                               basis='Inside retained cap from pinned carrier recipe; full changed branches still OPEN'))
            continue
        names=group.get('root_case_candidates',[group.get('preserved_owner')])
        if group['owner_stage'].endswith('_Knee'):
            # ZK plus the actual SG/XG end covers are one bought casing.
            # No shaft, PCB, mounting ear or inferred drilled hole becomes
            # an adhesive root merely because its face is locally planar.
            names=['P0_'+r['name'] for r in members
                   if r['stage']==group['owner_stage']
                   and r['label'].startswith(('ZK_','SG-ZIJI_','XG-ZIJI_'))]
        faces=[]
        rejected=[]
        for name in names:
            assert name in targets, name
            shape=targets[name]
            assert shape.isValid(), (name,'Invalid root shape')
            patches,blocked=patch_faces(shape,goal,targets,name,group['owner_stage']=='Body')
            faces += [dict(owner=name, **f) for f in patches]
            rejected += blocked
        faces.sort(key=lambda f:f['distance_to_group_centre_mm'])
        groups.append(dict(id=group['id'], owner_stage=group['owner_stage'],
                           candidate_faces=faces,
                           rejected_covered_faces=rejected,
                           basis='Actual planar patches plus full root-stub/rest material screening. Shared arms/ties/sleeves/full motion/access and strength NOT checked.'))
        print('root faces',group['id'],len(faces),flush=True)
    files=[fp,archive,sf,B.H.HEAD,ff,zf,Path(__file__),Path(B.__file__)]
    result=dict(status='EXPOSED_ASSEMBLED_CASE_ROOT_FACES_REST_CLEAR_LAYOUT_OPEN',
                groups=groups, selected=False,W5_complete=False,physical_pass=False,
                errors=[g['id'] for g in groups if 'candidate_faces' in g and not g['candidate_faces']],
                source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files},
                worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'remaining-loom-root-faces.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','errors','worker_seconds')}),flush=True)


if __name__=='__main__':
    run()
