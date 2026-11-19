"""Weld coincident STL seams of the small inlays at sub-nozzle resolution."""
from pathlib import Path
import runpy,json,hashlib
import numpy as np,trimesh
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools
from OCP.StlAPI import StlAPI_Writer
P=Path(__file__).parent
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"whole-cat19C.FCStd")
dst=P/"material-index.json";index=json.loads(dst.read_bytes())
for row in index["parts"]:
    if "export_rejection" not in row:continue
    s=D.shape(row["part"]);BRepTools.Clean_s(s)
    BRepMesh_IncrementalMesh(s,.012,False,.09,True);path=P/"individual-parts"/(row["part"]+".stl")
    assert StlAPI_Writer().Write(s,str(path));mesh=trimesh.load_mesh(path,process=True)
    for digits in [5,4,3]:
        m=mesh.copy();m.merge_vertices(digits_vertex=digits)
        m.update_faces(m.unique_faces() & m.nondegenerate_faces());m.remove_unreferenced_vertices()
        if m.is_watertight and m.is_volume:break
    if not m.is_volume or not m.is_watertight:
        path.unlink();continue
    matrix=trimesh.geometry.align_vectors(m.facets_normal[np.argmax(m.facets_area)],[0,0,-1]);m.apply_transform(matrix);shift=-m.bounds[0];m.apply_translation(shift);matrix[:3,3]+=shift;m.export(path)
    got=trimesh.load_mesh(path,process=True);err=abs(abs(got.volume)-row["volume_total_mm3"])/row["volume_total_mm3"]
    if not got.is_volume or not got.is_watertight or err>=.012:
        path.unlink();continue
    row.update(stl=path.relative_to(P).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),envelope_with_allowance=(got.extents+[16,16,4]).tolist(),native_to_mesh=matrix.tolist(),print_pose="STL on largest planar facet",reopened_watertight=True,mesh_volume_difference_fraction=err,initial_rejection=row.pop("export_rejection"),seam_weld_decimal_places=digits)
dst.write_bytes((json.dumps(index,indent=1)+"\n").encode())
print([(r["part"],bool(r["stl"])) for r in index["parts"] if r["part"].startswith("C19_")])

