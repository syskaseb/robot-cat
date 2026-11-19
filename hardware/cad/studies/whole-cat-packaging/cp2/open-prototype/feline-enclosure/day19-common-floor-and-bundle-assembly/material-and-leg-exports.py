"""Bind the installed material and original leg export geometries to this saved assembly."""
from pathlib import Path
import json,runpy,re,hashlib
import numpy as np
import trimesh
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.BRepTools import BRepTools
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
P=Path(__file__).parent;native=P/"whole-cat19B.FCStd"
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](native)
basis=json.loads((P.parent/"day16-whole-power-entry-and-full-CSI/rough-mass-readonly/rough-mass-and-leg-levers.json").read_bytes())
def solids(s):
    e=TopExp_Explorer(s,TopAbs_SOLID);a=[]
    while e.More():a.append(e.Current());e.Next()
    return a
def props(s):
    p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p);return p.Mass(),np.array(p.CentreOfMass().Coord())
def bounds(s):
    b=Bnd_Box();BRepBndLib.AddOptimal_s(s,b,False,False)
    return np.array(b.CornerMax().Coord())-np.array(b.CornerMin().Coord())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
full=solids(D.shape("WAVEGO_complete_126_source_solids"));by_index=[props(s) for s in full]
folder=P/"retained-legs";folder.mkdir(exist_ok=True)
groups={};rows=[]
for record in basis["original_source_leg_print_candidates"]:
    label=record["label"];family=next(k for k in ["LegSpacer","LegLink","WConnector","Bracket_v"] if label.startswith(k))
    matches=[i for i,(v,c) in enumerate(by_index) if abs(v-record["volume_mm3"])<.05 and np.linalg.norm(c-np.array(record["COM_mm"]))<.05]
    assert len(matches)==1,(label,matches)
    i=matches[0];groups.setdefault(family,[]).append(i)
for family,ids in groups.items():
    s=full[ids[0]];path=folder/(family+".stl")
    BRepMesh_IncrementalMesh(s,.035,False,.15,True)
    assert StlAPI_Writer().Write(s,str(path))
    m=trimesh.load_mesh(path,process=True)
    # Align the largest planar triangulated facet down and place the mesh on the bed.
    # This is a geometric print orientation; supports/infill remain the builder's setup.
    idx=int(np.argmax(m.facets_area));normal=m.facets_normal[idx]
    mat=trimesh.geometry.align_vectors(normal,[0,0,-1]);m.apply_transform(mat);m.apply_translation(-m.bounds[0])
    m.export(path)
    m=trimesh.load_mesh(path,process=True);vol=sum(by_index[i][0] for i in ids)
    assert m.is_watertight and abs(abs(m.volume)-vol/len(ids))<max(12,.009*vol/len(ids)),family
    rows.append(dict(part=family,qty=len(ids),native_solid_index_zero_based=ids,volume_total_mm3=vol,print_pose="supplied STL flat face down",envelope_with_allowance=(m.extents+[16,16,4]).tolist(),stl=str(path.relative_to(P)),sha256=sha(path)))
# The current head and tail mechanisms are identified by the previous selected
# print roles. The three source names below were superseded by 19A's fork/frame.
names={r["name"] for r in basis["selected_prints"] if r["category"]=="current_head_tail_mechanism"} & set(D.members)
names-= {"YAW_REAL_REMOVABLE_SERVO_SADDLE"} if (P/"seat-receipt.json").exists() else set()
names.update(("BR_FINISHED_YAW_SADDLE","D18C_TRUE_PITCH_OPTICAL_RECEIVER","BR_COMMON_OPTICAL_MASK","D19_BROAD_SKULL_BACK","D19_SKULL_EARS","D19_ROUNDED_FORE_COWL","D19_ROUNDED_REAR_COWL","B19_FrontFloor","B19_RearFloor"))
for n in sorted(names):
    for i,s in enumerate(solids(D.shape(n))):
        vol,c=props(s)
        rows.append(dict(part=n,solid=i+1,qty=1,volume_total_mm3=vol,envelope_with_allowance=(bounds(s)+[16,16,4]).tolist(),print_pose="native XYZ envelope screen",stl=None))
total=sum(r["volume_total_mm3"] for r in rows)*.00127
out=dict(native_sha256=sha(native),density_g_cm3=1.27,geometric_P_for_listed_material_g=total,
    known_robot_range_g=[1853.4+total,2593.4+total],parts=rows,unmodeled_mass=None,physical_mass=None,whole_print_release=False,
    allowance="8 mm brim each XY side and 4 mm Z planning allowance; only retained legs supplied as oriented spare meshes")
(P/"material-index.json").write_text(json.dumps(out,indent=1)+"\n",encoding="utf8")
print(len(rows),total)

