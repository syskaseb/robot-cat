"""Rebind each retained print and export separately mountable solid members from 19C."""
from pathlib import Path
import hashlib,json,runpy
import numpy as np
import trimesh
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.STEPControl import STEPControl_Writer,STEPControl_Reader,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
P=Path(__file__).parent;prev=P.parent/"day19-common-floor-and-bundle-assembly";native=P/"whole-cat19C.FCStd"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](native)
retired={"B19_FrontFloor":"C19_ShoulderFloor","BR_COMMON_OPTICAL_MASK":"C19_FaceAndEars","D18C_TRUE_PITCH_OPTICAL_RECEIVER":"C19_MovingOpticsCarrier","D19_BROAD_SKULL_BACK":"C19_OpenRearHelmet","D19_SKULL_EARS":"C19_Ear_1/2","D19_ROUNDED_FORE_COWL":"C19_FixedShoulderShell"}
rows=[r for r in json.loads((prev/"material-index.json").read_bytes())["parts"] if r["part"] not in retired]
for r in rows:
    if r["stl"]:
        path=prev/r["stl"];assert sha(path)==r["sha256"];r["stl"]="../"+prev.name+"/"+Path(r["stl"]).as_posix()
for n,m in json.loads((P/"final-members.json").read_bytes()).items():
    assert m["valid"] and m["solids"]==1
    rows.append(dict(part=n,qty=1,solid=1,volume_total_mm3=m["volume"],envelope_with_allowance=(np.array(m["extents"])+[16,16,4]).tolist(),stl=None,print_pose="native XYZ"))
folder=P/"individual-parts";folder.mkdir(exist_ok=True)
for r in rows:
    if r["stl"]:continue
    n=r["part"]
    # The known blocked floor/shell/moving return stay in native/engineering STEP.
    if n in {"C19_FixedShoulderShell","C19_ShoulderFloor","C19_OpenRearHelmet","C19_MovingOpticsCarrier","C19_FaceAndEars","D19_ROUNDED_REAR_COWL","B19_RearFloor"}:continue
    s=D.shape(n);e=TopExp_Explorer(s,TopAbs_SOLID);assert e.More();ss=e.Current();e.Next();assert not e.More()
    path=folder/(n+".stl")
    try:
        BRepMesh_IncrementalMesh(ss,.025,False,.13,True)
        assert StlAPI_Writer().Write(ss,str(path))
        m=trimesh.load_mesh(path,process=True);normal=m.facets_normal[np.argmax(m.facets_area)]
        mat=trimesh.geometry.align_vectors(normal,[0,0,-1]);m.apply_transform(mat);shift=-m.bounds[0];m.apply_translation(shift);m.export(path)
        m=trimesh.load_mesh(path,process=True);err=abs(abs(m.volume)-r["volume_total_mm3"])/r["volume_total_mm3"]
        assert m.is_watertight and m.is_volume and err<.012,(m.is_watertight,m.volume,err)
        envelope=(m.extents+[16,16,4]).tolist();assert max(envelope)<=256
        mat[:3,3]+=shift
        r.update(stl=path.relative_to(P).as_posix(),sha256=sha(path),envelope_with_allowance=envelope,native_to_mesh=mat.tolist(),print_pose="STL on largest planar facet",reopened_watertight=True,mesh_volume_difference_fraction=err)
    except Exception as exc:
        if path.exists():path.unlink()
        r["export_rejection"]=str(exc)
steps=[]
for n in ["C19_ShoulderFloor","C19_MovingOpticsCarrier"]:
    s=D.shape(n);path=folder/(n+".step");w=STEPControl_Writer()
    assert w.Transfer(s,STEPControl_AsIs)==IFSelect_RetDone and w.Write(str(path))==IFSelect_RetDone
    reader=STEPControl_Reader();assert reader.ReadFile(str(path))==IFSelect_RetDone and reader.TransferRoots()>0
    obj=reader.OneShape();p=GProp_GProps();q=GProp_GProps();BRepGProp.VolumeProperties_s(s,p,1e-8);BRepGProp.VolumeProperties_s(obj,q,1e-8)
    e=TopExp_Explorer(obj,TopAbs_SOLID);assert e.More();e.Next();assert not e.More() and BRepCheck_Analyzer(obj).IsValid() and abs(p.Mass()-q.Mass())<.00005*p.Mass()
    steps.append(dict(name=n,path=path.relative_to(P).as_posix(),sha256=sha(path),volume_mm3=q.Mass(),single_solid=True,status="engineering reference"))
total=sum(r["volume_total_mm3"] for r in rows)*.00127
out=dict(native_sha256=sha(native),source_19B_sha256=sha(prev/"whole-cat19B.FCStd"),superseded=retired,parts=rows,steps=steps,density_g_cm3=1.27,geometric_P_g=total,delta_vs_19B_g=total-863.6858,whole_robot_known_range_g=[1853.4+total,2593.4+total],missing_mount_mass_g=None,actual_fit_cut_slack=None,physical_PASS=False,whole_kit=False,allowance="8 mm per side in XY and 4 mm in Z. Geometric support allowance. No slicing.")
(P/"material-index.json").write_bytes((json.dumps(out,indent=1)+"\n").encode())
print(total,len(rows),len([r for r in rows if r['stl']]),[(r['part'],r['export_rejection']) for r in rows if 'export_rejection' in r])

