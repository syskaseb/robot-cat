"""Export only the FIT_S0 witness and its conditional rear-base parent."""
from pathlib import Path
from hashlib import sha256
import ast
import json
import os

import manifold3d as mf
import numpy as np
import trimesh
from OCP.BRep import BRep_Builder
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools
from OCP.GProp import GProp_GProps
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Reader, STEPControl_Writer
from OCP.StlAPI import StlAPI_Writer
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS_Shape

here = Path(__file__).resolve().parent
# Reuse the two mesh-verification routines and solid info from the
# accepted local 20C export. Their stand-alone names do not run 20C.
library = here.parent/'20C/export-verified.py'
module = ast.parse(library.read_text(encoding='utf-8'))
names = {'info','read_mesh','compact','final_mesh'}
functions = [f for f in module.body if isinstance(f,ast.FunctionDef) and f.name in names]
assert len(functions)==4
exec(compile(ast.Module(body=functions,type_ignores=[]),str(library),'exec'))

proof = json.loads((here/'FIT_S0-gate.json').read_bytes())
parts = [
    ('FIT_S0_coupon','coupon',(0,-1,0),'inside face Y99 down; supports as needed on the perimeter'),
    ('20H_RearBase_CONDITIONAL_AFTER_FIT_S0','rear_base',(0,0,-1),'same floor-down orientation as C20_RearBase'),
]
records = {}
for name, reference, down, pose in parts:
    brep = here/(reference+'.brep')
    shape = TopoDS_Shape()
    assert BRepTools.Read_s(shape,str(brep),BRep_Builder())
    volume,count,valid = info(shape)
    assert count==1 and valid and abs(proof[reference+'_volume_mm3']-volume)<.01
    raw = here/(name+'.raw.stl')
    selected = None
    for deflection, angle in [(0.025,.11),(.014,.08),(.008,.05)]:
        BRepTools.Clean_s(shape)
        BRepMesh_IncrementalMesh(shape,deflection,False,angle,True)
        writer=StlAPI_Writer()
        writer.ASCIIMode=False
        assert writer.Write(shape,str(raw))
        mesh=compact(read_mesh(raw),volume,.004)
        if mesh is not None:
            selected = mesh
            break
    assert selected is not None, name
    transform=trimesh.geometry.align_vectors(down,[0,0,-1])
    selected.apply_transform(transform)
    offset=-selected.bounds[0]
    selected.apply_translation(offset)
    transform[:3,3]+=offset
    stl=here/(name+'.stl')
    mesh,change,split=final_mesh(selected,stl,volume,.004)
    raw.unlink()
    step=here/(name+'.step')
    writer=STEPControl_Writer()
    assert writer.Transfer(shape,STEPControl_AsIs)==IFSelect_RetDone
    assert writer.Write(str(step))==IFSelect_RetDone
    rd=STEPControl_Reader()
    assert rd.ReadFile(str(step))==IFSelect_RetDone and rd.TransferRoots()>0
    recovered,n,valid=info(rd.OneShape())
    assert n==1 and valid and abs(recovered-volume)/volume<.001
    envelope=(mesh.extents+np.array([16.,16.,8.])).round(3).tolist()
    assert max(envelope)<=256
    records[name]={'print_pose':pose,'assembly_to_stl':transform.tolist(),
        'raw_size_mm':mesh.extents.round(3).tolist(),
        'with_8mm_brim_each_side_8mm_support_z':envelope,
        'solid_count':1,'stl_watertight':mesh.is_watertight,
        'stl_facets':len(mesh.faces),'stl_simp_mm':change,'stl_split_vertices':split,
        'stl_volume_rel_error':abs(mesh.volume-volume)/volume,
        'step_volume_rel_error':abs(recovered-volume)/volume,
        'stl':stl.name,'stl_sha256':sha256(stl.read_bytes()).hexdigest(),
        'step':step.name,'step_sha256':sha256(step.read_bytes()).hexdigest()}
    print(name,records[name]['raw_size_mm'],envelope,flush=True)
out=here/'FIT_S0-exports.json'
tmp=out.with_suffix('.tmp')
with tmp.open('x',encoding='utf-8',newline='\n') as f:
    json.dump(records,f,ensure_ascii=False,indent=2)
    f.write('\n')
os.replace(tmp,out)
