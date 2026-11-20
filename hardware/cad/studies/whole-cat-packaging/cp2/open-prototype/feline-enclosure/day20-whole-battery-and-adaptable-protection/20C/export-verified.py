"""Export changed 20C BReps. Use 19I's reopened manifold method for seams."""
from pathlib import Path
from runpy import run_path
import hashlib
import json
import os
import struct

import manifold3d as mf
import numpy as np
import trimesh
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

here=Path(__file__).resolve().parent
study=here.parent.parent
Saved=run_path(str(study/'day18-front-insert-correction'/'saved-front.py'))['Saved']
native=Saved(here/'whole-cat20C.FCStd')
desktop_dir=here/'parts'
desktop_dir.mkdir(exist_ok=True)

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f,'sha256').hexdigest()

def info(shape):
    props=GProp_GProps()
    BRepGProp.VolumeProperties_s(shape,props,1e-8)
    ex=TopExp_Explorer(shape,TopAbs_SOLID)
    count=0
    while ex.More():count+=1;ex.Next()
    return props.Mass(),count,BRepCheck_Analyzer(shape).IsValid()

def read_mesh(file):
    mesh=trimesh.load_mesh(file, file_type='stl')
    return mesh

def compact(source,vol,rigid):
    for digits in (7,6,5,4,3):
        m=source.copy()
        m.merge_vertices(digits_vertex=digits)
        m.update_faces(m.unique_faces()&m.nondegenerate_faces(height=1e-9))
        m.remove_unreferenced_vertices()
        if not m.is_watertight:trimesh.repair.fill_holes(m)
        if not m.is_watertight:
            raw=mf.Mesh(m.vertices.astype('f'),m.faces.astype('uint32'))
            raw.merge(); manifold=mf.Manifold(raw)
            if manifold.status()==mf.Error.NoError and manifold.num_tri()>0:
                out=manifold.to_mesh()
                m=trimesh.Trimesh(vertices=out.vert_properties[:,:3],faces=out.tri_verts,process=False)
        if m.is_watertight and m.is_volume and abs(m.volume-vol)/vol<rigid:
            return m
    return None

def final_mesh(m,path,vol,tolerance):
    m.export(path)
    ready=read_mesh(path)
    if ready.is_watertight and ready.is_volume and abs(ready.volume-vol)/vol<tolerance:
        return ready,0.,0
    body=mf.Manifold(mf.Mesh(m.vertices.astype('f'),m.faces.astype('uint32')))
    assert body.status()==mf.Error.NoError,path
    for tol in (.002,.006,.012,.023):
        out=body.simplify(tol).to_mesh()
        v=np.array(out.vert_properties[:,:3],dtype=float)
        f=np.array(out.tri_verts)
        part=trimesh.Trimesh(vertices=v,faces=f,process=False)
        _,inverse,count=np.unique(v.astype('f'),axis=0,return_inverse=True,return_counts=True)
        dup=count[inverse]>1
        v[dup]+=part.vertex_normals[dup]*tol
        trimesh.Trimesh(vertices=v,faces=f,process=False).export(path)
        m=read_mesh(path)
        if m.is_watertight and m.is_volume and abs(m.volume-vol)/vol<tolerance:
            return m,tol,int(dup.sum())
    raise RuntimeError(f"{path}: STL failed reopen")

specs=[
 ("C20_FrontFrame","H19_FrontFrame",(0,0,-1),"bazą w dół","H19_FrontFrame"),
 ("C20_RearBase","E19_RearBase",(0,0,-1),"bazą w dół","E19_RearBase"),
 ("C20_BatteryUpperBridge","C20_BatteryUpperBridge",(0,1,0),"zewnętrzną powierzchnią +Y do stołu",""),
 ("C20_F0_OpenMount","C20_F0_OpenMount",(1,0,0),"długim bokiem +X do stołu",""),
 ("C20_Post_OpenSlottedMount","C20_Post_OpenSlottedMount",(0,0,1),"platformą do stołu",""),
]
specs.extend((f'C20_MTA_{place}',f'C20_MTA_{place}',(0,1,0),"długim bokiem +Y do stołu","") for place in ("FL","FR","RL","RR"))
results=[]
for part,obj,direction,pose,old in specs:
    solid=native.shape(obj)
    volume,count,valid=info(solid)
    assert count==1 and valid,(part,count,valid)
    close_tol=.001 if part=="C20_FrontFrame" else .004
    levels=[(.018,.085),(.04,.13),(.008,.05)] if part=="C20_FrontFrame" else [(.025,.11),(.014,.08)]
    raw=desktop_dir/(part+".temporary.stl")
    choice=None
    for lin,ang in levels:
        BRepTools.Clean_s(solid)
        BRepMesh_IncrementalMesh(solid,lin,False,ang,True)
        writer=StlAPI_Writer()
        writer.ASCIIMode=False
        assert writer.Write(solid,str(raw)),part
        choice=compact(read_mesh(raw),volume,close_tol)
        if choice is not None:break
    if choice is None:raise RuntimeError(f"{part} STL topology")
    transform=trimesh.geometry.align_vectors(direction,[0,0,-1])
    choice.apply_transform(transform)
    shift=-choice.bounds[0]
    choice.apply_translation(shift);transform[:3,3]+=shift
    stl=desktop_dir/(part+".stl")
    final,simplify,split_count=final_mesh(choice,stl,volume,close_tol)
    raw.unlink()
    step=desktop_dir/(part+".step")
    # A separate STEP in assembly coordinates retains the reassembly datum.
    sw=STEPControl_Writer()
    assert sw.Transfer(solid,STEPControl_AsIs)==IFSelect_RetDone and sw.Write(str(step))==IFSelect_RetDone
    rd=STEPControl_Reader()
    assert rd.ReadFile(str(step))==IFSelect_RetDone and rd.TransferRoots()>0
    recovered,count,valid=info(rd.OneShape())
    assert count==1 and valid and abs(recovered-volume)/volume<.001,(part,recovered,volume)
    envelope=(final.extents+np.array([16,16,8])).round(2).tolist()
    assert max(envelope)<=256,envelope
    results.append({"part":part,"qty":1,"native_object":obj,"replaces":old,
                    "print_pose":pose,"step_datum":"assembly coordinates",
                    "assembly_to_stl":transform.tolist(),"with_8mm_brim_each_side_8mm_support_z":envelope,
                    "stl":stl.relative_to(here).as_posix(),"stl_sha256":sha(stl),"stl_facets":len(final.faces),
                    "stl_reopened_watertight":True,"stl_simplification_mm":simplify,"stl_separated_fans_vertices":split_count,
                    "step":step.relative_to(here).as_posix(),"step_sha256":sha(step),
                    "volume_mm3":round(volume,3),"stl_volume_rel_error":abs(final.volume-volume)/volume,
                    "step_volume_rel_error":abs(recovered-volume)/volume})
    print(part,len(final.faces),envelope,"solid",flush=True)
out=here/'20C-print-index.json'
tmp=out.with_suffix('.tmp')
with tmp.open('x',encoding='utf-8',newline='\n') as f:
    json.dump(results,f,ensure_ascii=False,indent=2);f.write('\n')
os.replace(tmp,out)