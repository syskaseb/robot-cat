"""Rebind retained STL sources and export changed individual print solids from the actual save."""
from pathlib import Path
import os,json,hashlib,runpy
import numpy as np,trimesh
from OCP.BRepTools import BRepTools
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.StlAPI import StlAPI_Writer
from OCP.STEPControl import STEPControl_Writer,STEPControl_Reader,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepCheck import BRepCheck_Analyzer
P=Path(__file__).parent;C=P.parent/"day19-closed-head-neck-and-module-interfaces";native=P/"whole-cat19D.FCStd"
D=runpy.run_path(str(P.parent/"day18-front-insert-correction/saved-front.py"))["Saved"](native)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((C/"material-index.json").read_bytes());members=json.loads((P/"form-members.json").read_bytes())
retired=[r["part"] for r in old["parts"] if r["part"].startswith("C19_") or r["part"]=="D19_ROUNDED_REAR_COWL" or (r["part"]=="BR_FINISHED_YAW_SADDLE" and "D19D_YawSaddle" in members)]
rows=[r for r in old["parts"] if r["part"] not in retired]
for r in rows:
    if r["stl"]:
        path=(C/r["stl"]).resolve();assert sha(path)==r["sha256"]
        r["stl"]=Path(os.path.relpath(path,P)).as_posix()
folder=P/"individual-parts";folder.mkdir(exist_ok=True);steps=[]
for n,m in members.items():
    s=D.shape(n);v=GProp_GProps();BRepGProp.VolumeProperties_s(s,v,1e-8);volume=v.Mass()
    row=dict(part=n,qty=1,volume_total_mm3=m["volume"],adaptive_volume_mm3=volume,hardware_use=m["role"],stl=None,print_pose="native XYZ",envelope_with_allowance=(np.array(m["extents"])+[16,16,4]).tolist());rows.append(row)
    if n in ("D19D_FrontFloor","D19D_OpticsCarrier","D19D_YawHood"):
        path=folder/(n+".step");w=STEPControl_Writer();assert w.Transfer(s,STEPControl_AsIs)==IFSelect_RetDone and w.Write(str(path))==IFSelect_RetDone
        rr=STEPControl_Reader();assert rr.ReadFile(str(path))==IFSelect_RetDone and rr.TransferRoots()>0;o=rr.OneShape()
        ex=TopExp_Explorer(o,TopAbs_SOLID);assert ex.More();ex.Next();assert not ex.More() and BRepCheck_Analyzer(o).IsValid()
        pv=GProp_GProps();BRepGProp.VolumeProperties_s(o,pv,1e-8);assert abs(pv.Mass()-volume)<.0002*volume
        bb=Bnd_Box();BRepBndLib.AddOptimal_s(o,bb,False,False);bbox_error=float(max(abs(np.r_[bb.CornerMin().Coord(),bb.CornerMax().Coord()]-D.bounds(n))));assert bbox_error<.01,bbox_error
        steps.append(dict(part=n,path=path.relative_to(P).as_posix(),sha256=sha(path),volume=pv.Mass(),source_volume_mm3=volume,bounds_delta_mm=bbox_error,purpose="engineering fit"))
    if n not in ("D19D_Face","D19D_Nose","D19D_Iris_L","D19D_Iris_R","D19D_Pupil_L","D19D_Pupil_R","D19D_Ear_L","D19D_Ear_R","D19D_YawSaddle"):continue
    path=folder/(n+".stl");BRepTools.Clean_s(s);BRepMesh_IncrementalMesh(s,.018,False,.11,True);assert StlAPI_Writer().Write(s,str(path))
    original=trimesh.load_mesh(path,process=True)
    for digits in [5,4,3]:
        mesh=original.copy();mesh.merge_vertices(digits_vertex=digits);mesh.update_faces(mesh.unique_faces() & mesh.nondegenerate_faces());mesh.remove_unreferenced_vertices()
        if mesh.is_volume and mesh.is_watertight:break
    if mesh.is_watertight and mesh.is_volume:
        # Stand the eye insert on its rear. On each other member select its largest planar seat.
        normal=(np.array([.96,-.28*(1 if n.endswith('_L') else -1),-.10]) if ("Iris" in n or "Pupil" in n) else mesh.facets_normal[np.argmax(mesh.facets_area)])
        mat=trimesh.geometry.align_vectors(normal/np.linalg.norm(normal),[0,0,-1]);mesh.apply_transform(mat);shift=-mesh.bounds[0];mesh.apply_translation(shift);mesh.export(path)
        got=trimesh.load_mesh(path,process=True);error=abs(got.volume-volume)/volume
        envelope=(got.extents+[16,16,4]).tolist()
        if got.is_volume and got.is_watertight and error<.012 and max(envelope)<=256:
            mat[:3,3]+=shift;row.update(stl=path.relative_to(P).as_posix(),sha256=sha(path),print_pose="supplied STL on bed",native_to_mesh=mat.tolist(),envelope_with_allowance=envelope,reopened_watertight=True,mesh_volume_difference_fraction=error);continue
    row["mesh_rejection"]="topology, volume or dimensional screen";path.unlink()
mass=sum(r["volume_total_mm3"] for r in rows)*.00127
out=dict(native_sha256=sha(native),source_19C_sha256=old["native_sha256"],retired=retired,parts=rows,steps=steps,geometric_P_g=mass,delta_19C_g=mass-old["geometric_P_g"],whole_robot_known_range_g=[1853.4+mass,2593.4+mass],allowance="8 mm each XY side and 4 mm Z; planning only",missing_printed_mass_g=None,physical_PASS=False,actual_fit_cut_slack=None,whole_print_kit=False)
(P/"material-index.json").write_bytes((json.dumps(out,indent=1)+"\n").encode());print(mass,len(rows),[r["part"] for r in rows if r.get("mesh_rejection")])

