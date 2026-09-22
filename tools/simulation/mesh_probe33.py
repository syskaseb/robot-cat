"""Independent Manifold triangle-solid diagnostics of the v33 head. No repair."""
from pathlib import Path
import hashlib,json
import trimesh
import numpy as np
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'hardware/skorupa/v33/shape-cache/mesh-proof'
index=json.loads((BASE/'index.json').read_text())
assert hashlib.sha256((ROOT/'hardware/skorupa/v33/HeadDesign33.FCStd').read_bytes()).hexdigest()==index['master_sha256']
meshes={};rows=[];intersections=[]
for r in index['meshes']:
    path=BASE/(r['name']+'.stl');assert hashlib.sha256(path.read_bytes()).hexdigest()==r['sha256']
    m=trimesh.load_mesh(path,process=True);meshes[r['name']]=m
    counts=np.bincount(m.edges_unique_inverse,minlength=len(m.edges_unique))
    edges=m.edges_unique[counts!=2]
    print(r['name'],dict(volume=m.volume,watertight=m.is_watertight,winding=m.is_winding_consistent,is_volume=m.is_volume,
                            nonmanifold_edges=len(edges)),flush=True)
    rows.append(dict(name=r['name'],sha256=r['sha256'],volume_mm3=float(m.volume),
        watertight=bool(m.is_watertight),consistent_winding=bool(m.is_winding_consistent),
        is_volume=bool(m.is_volume),nonmanifold_edges=len(edges)))
    if len(edges):
        print(' boundary extent',m.vertices[edges].reshape(-1,3).min(axis=0),m.vertices[edges].reshape(-1,3).max(axis=0),flush=True)
        for digits in [5,4,3]:
            candidate=m.copy();candidate.merge_vertices(digits_vertex=digits)
            candidate.update_faces(candidate.nondegenerate_faces());candidate.remove_unreferenced_vertices()
            print(' weld diagnostic only',digits,candidate.is_volume,candidate.is_watertight,candidate.volume,flush=True)
for a,b in [('HeadFront','OpticalReserve32'),('HeadFace33','OpticalReserve32'),('HeadFace33','ToFWireReserve32'),
            ('HeadFace33','NoseAccess0'),('HeadFace33','NoseAccess1'),('HeadFace33','RightAngle0'),('HeadFace33','RightAngle1'),
            ('EarR','RightAngle0'),('EarL','RightAngle1')]+[(n,p+str(i)) for n in ['HeadFace33','EarL','EarR'] for p in ['BottomDriver','TopWrench'] for i in range(2)]:
    try:
        result=trimesh.boolean.intersection([meshes[a],meshes[b]],engine='manifold',check_volume=True)
        print('INTERSECTION',a,b,result.volume,flush=True)
        intersections.append(dict(parts=[a,b],volume_mm3=float(result.volume)))
    except Exception as exc:
        print('UNRESOLVED',a,b,repr(exc),flush=True)
        intersections.append(dict(parts=[a,b],error=str(exc)))
required=[r for r in intersections if r['parts'][0]=='HeadFace33' and r['parts'][1].startswith(('Optical','ToFWire','NoseAccess','BottomDriver','TopWrench'))]
report=dict(master_sha256=index['master_sha256'],linear_deflection_mm=index['linear_deflection_mm'],
    angular_deflection_rad=index['angular_deflection_rad'],engine='trimesh5.1 + manifold3d3.5; no hole filling or mesh repair',
    head_manifold=next(r['is_volume'] and r['nonmanifold_edges']==0 for r in rows if r['name']=='HeadFace33'),
    required_clearance_passed=len(required)==8 and all('error' not in r and r['volume_mm3']<.01 for r in required),
    meshes=rows,intersections=intersections,mechanical_release=False,
    limitations='Old head is non-manifold. Old downward tool route rejected. Upward screw assembly requires EarL absent for nut wrench; full service not approved. Tessellation is not exact BRep proof.')
(BASE.parent.parent/'mesh-proof.json').write_text(json.dumps(report,indent=2),encoding='utf8',newline='\n')
assert report['head_manifold'] and report['required_clearance_passed']
