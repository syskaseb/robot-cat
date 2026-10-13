"""Measure actual candidate attachment faces, before planning support arms.

This is not a collision/retention certificate or a hole in a purchased case.
Keep several actual faces in ONE shared layout record. Provisional adhesive
case roots need compatibility/load trials. Frame roots extend the existing
owner and must not duplicate or silently cut the chassis.
"""
import json
import math
import time
from pathlib import Path
import FreeCAD as A
import Part
import build_complete_source_carriers as B

P = B.P


def patch_faces(shape, goal):
    candidates = []
    for index, face in enumerate(shape.Faces):
        if not isinstance(face.Surface, Part.Plane) or face.Area < 80:
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
                   ((-5,-4),(5,-4),(5,4),(-5,4),(-5,-4))]
        patch = Part.Face(Part.makePolygon(corners))
        contact = face.common(patch)
        if abs(contact.Area-80) > 1e-5:
            continue
        # Merely having distance0 to a solid does not prove a useful area.
        # The exact face-face intersection above establishes this plane.
        candidates.append(dict(face_index=index+1, plane_centre_world_mm=list(centre),
                               outward_normal=list(normal), in_plane_axis=list(tangent),
                               patch_bounds_plane_mm=[10,8], actual_patch_area_mm2=contact.Area,
                               outer_arm_root_world_mm=list(centre+normal*6.2),
                               distance_to_group_centre_mm=(centre-A.Vector(*goal)).Length))
    return sorted(candidates, key=lambda r:r['distance_to_group_centre_mm'])[:4]


def run():
    tick=time.monotonic()
    fp=P.OUT/'remaining-loom-roots-plan.json'
    plan=json.loads(fp.read_text())
    for n, digest in plan['source_sha256'].items():
        assert P.SHA(P.ROOT/n)==digest, n
    reader=B.H.P.SavedShapes()
    targets, _, archive, sf, ff=B.current_scene(reader)
    groups=[]
    for group in plan['groups']:
        goal=[sum(r['centre_world_mm'][i] for r in group['lands'])/len(group['lands']) for i in range(3)]
        if group['id'].endswith('HipExtension'):
            groups.append(dict(id=group['id'], owner_stage=group['owner_stage'],
                               preserved_owner=group['preserved_owner'], root_world_mm=group['root_world_mm'],
                               basis='Inside retained cap from pinned carrier recipe; full changed branches still OPEN'))
            continue
        names=group.get('root_case_candidates',[group.get('preserved_owner')])
        faces=[]
        for name in names:
            assert name in targets, name
            shape=targets[name]
            assert shape.isValid(), (name,'Invalid root shape')
            faces += [dict(owner=name, **f) for f in patch_faces(shape,goal)]
        faces.sort(key=lambda f:f['distance_to_group_centre_mm'])
        groups.append(dict(id=group['id'], owner_stage=group['owner_stage'],
                           candidate_faces=faces,
                           basis='Measured planar patches only. Shared arms/ties/sleeves/full motion/access and strength NOT checked.'))
        print('root faces',group['id'],len(faces),flush=True)
    files=[fp,archive,sf,B.H.HEAD,ff,Path(__file__),Path(B.__file__)]
    result=dict(status='ACTUAL_REMAINING_ROOT_FACE_CANDIDATES_LAYOUT_OPEN',
                groups=groups, selected=False,W5_complete=False,physical_pass=False,
                errors=[g['id'] for g in groups if 'candidate_faces' in g and not g['candidate_faces']],
                source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files},
                worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'remaining-loom-root-faces.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','errors','worker_seconds')}),flush=True)


if __name__=='__main__':
    run()
