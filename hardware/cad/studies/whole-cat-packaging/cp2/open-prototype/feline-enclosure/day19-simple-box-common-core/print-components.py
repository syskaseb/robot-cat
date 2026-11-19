"""Build the single effective inventory and reopen individual conditional exports."""
from pathlib import Path
import os,runpy,json,hashlib
import numpy as np,trimesh
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepTools import BRepTools
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.STEPControl import STEPControl_Reader,STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
P=Path(__file__).parent;D=P.parent/'day19-whole-appearance-and-moving-neck-correction'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return Path(os.path.relpath(p,P)).as_posix()
native=P/'whole-cat19E.FCStd'; src=D/'whole-cat19D.FCStd'
Saved=runpy.run_path(str(P.parent/'day18-front-insert-correction/saved-front.py'))['Saved']
S=Saved(native);oldS=Saved(src)
base=json.loads((D/'material-index.json').read_bytes())
ret=['B19_RearFloor','D19D_FrontFloor','D19D_Shoulder','D19D_RearShell','D19D_YawHood','TAIL_ROTATING_HOLLOW_REAL_ROOT']
rows=[];steps=[]
identity={}
def props(shape):
    g=GProp_GProps();BRepGProp.VolumeProperties_s(shape,g);m=g.MatrixOfInertia()
    return np.array([g.Mass(),*g.CentreOfMass().Coord(),*[m.Value(i,j) for i in (1,2,3) for j in (1,2,3)]])
def bound(n):
    if n in identity:return
    same=S.zip.read(S.members[n])==oldS.zip.read(oldS.members[n])
    if not same:
        aa,bb=(TopExp_Explorer(doc.shape(n),TopAbs_SOLID) for doc in (S,oldS));nsol=0
        while aa.More() and bb.More():
            assert np.allclose(props(aa.Current()),props(bb.Current()),atol=.00002,rtol=1e-8),(n,nsol)
            aa.Next();bb.Next();nsol+=1
        assert not aa.More() and not bb.More() and nsol
        assert np.allclose(S.bounds(n),oldS.bounds(n),atol=.00002,rtol=0)
    identity[n]='identical BRep bytes' if same else 'retained source, corresponding solids have same volume, centroid, inertia and whole bounds after native reserialization'
for q in base['parts']:
    n=q['part']
    if n in ret:continue
    if n in S.members:bound(n)
    elif n.startswith('Leg'):bound('WAVEGO_complete_126_source_solids')
    r=dict(q)
    if q.get('stl'):
        f=(D/q['stl']).resolve();assert h(f)==q['sha256'];r.update(stl=rel(f),effectivity='source retained by identity')
    rows.append(r)
new=['E19_KeyedTail','E19_UpperYawCover','E19_FrontShroud','E19_ForeLid','E19_RearLid','E19_WagoForeNeg','E19_WagoForePos','E19_WagoRearNeg','E19_WagoRearPos','E19_ForeBase','E19_RearBase']
coupon={'part':'E19_MTA_sample_land','qty':0,'use':'one optional off-robot physical slot sample'}
purpose=['source crosspin and horn/race assembly','attach with yaw saddle tongue','retain in fore wall at two side tongues','front removable cap, mic and touch','rear service cap, speaker / BNO / monitor / JPWM','four fixed lever housings','four lever housings','four lever housings','three lever housings','four source front countersunk anchors / Pi / fuse and keyed stations','four source rear anchors / bearing / converter and operator stations']
new.append('E19_BatteryDoor');purpose.append('RR W052 and W053 removable seats, snap buttons and lower door hooks')
for n,fn in zip(new,purpose):rows.append(dict(part=n,qty=1,hardware_use=fn))
folder=P/'components';folder.mkdir(exist_ok=True)
def save():
    mass=sum(q['volume_total_mm3'] for q in rows if 'volume_total_mm3' in q)*.00127
    data=dict(native_sha256=h(native),source_19D_sha256=h(src),retired=ret,parts=rows,off_robot=coupon,steps=steps,geometric_P_g=mass,known_robot_scenario_g=[1853.4+mass,2593.4+mass],physical_PASS=False,actual_cut_fit_slack=None,whole_print_kit=False)
    data['retained_geometry']=identity
    (P/'material-index.json').write_text(json.dumps(data,indent=1)+'\n')
for q in [r for r in rows if not r.get('stl')]+[coupon]:
    n=q['part'];s=S.shape(n);p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p,1e-8);vol=p.Mass()
    if q is not coupon:q['volume_total_mm3']=vol*q['qty']
    ex=TopExp_Explorer(s,TopAbs_SOLID);count=0
    while ex.More():count+=1;ex.Next()
    q.update(solids=count,valid=BRepCheck_Analyzer(s).IsValid(),stl=None)
    if count!=1 or not q['valid']:q['export_state']='hold geometry';continue
    path=folder/(n+'.stl')
    BRepTools.Clean_s(s);BRepMesh_IncrementalMesh(s,.025,False,.11,True);writer=StlAPI_Writer();writer.ASCIIMode=False
    assert writer.Write(s,str(path));original=trimesh.load_mesh(path,process=True)
    for digits in [6,5,4,3]:
        m=original.copy();m.merge_vertices(digits_vertex=digits);m.update_faces(m.unique_faces() & m.nondegenerate_faces());m.remove_unreferenced_vertices()
        if m.is_watertight and m.is_volume:break
    if not (m.is_watertight and m.is_volume):
        q['export_state']='hold mesh topology';path.unlink();continue
    normal=[0,0,1] if n.endswith('Lid') else [0,0,-1]
    if n in ['E19_KeyedTail','D19D_OpticsCarrier','D19D_PitchBack','E19_UpperYawCover','E19_FrontShroud']:
        normal=m.facets_normal[np.argmax(m.facets_area)]
    mat=trimesh.geometry.align_vectors(normal,[0,0,-1]);m.apply_transform(mat);shift=-m.bounds[0];m.apply_translation(shift);mat[:3,3]+=shift
    m.export(path);g=trimesh.load_mesh(path);env=g.extents+[16,16,4];err=abs(g.volume-vol)/vol
    if not g.is_watertight or not g.is_volume or max(env)>256 or err>.012:q['export_state']='hold reopened mesh';path.unlink();continue
    q.update(stl=rel(path),sha256=h(path),envelope_with_allowance=env.tolist(),native_to_mesh=mat.tolist(),print_pose='supplied orientation with 8 mm around every side and 4 mm Z support allowance',mesh_volume_error=err,reopened_watertight=True,export_state='individual component dry-fit only')
    if n in ['E19_ForeBase','E19_RearBase','E19_KeyedTail']:
        f=folder/(n+'.step');w=STEPControl_Writer();assert w.Transfer(s,STEPControl_AsIs)==IFSelect_RetDone and w.Write(str(f))==IFSelect_RetDone
        reader=STEPControl_Reader();assert reader.ReadFile(str(f))==IFSelect_RetDone and reader.TransferRoots()>0
        ss=reader.OneShape();ex=TopExp_Explorer(ss,TopAbs_SOLID);assert ex.More();ex.Next();assert not ex.More();assert BRepCheck_Analyzer(ss).IsValid()
        p=GProp_GProps();BRepGProp.VolumeProperties_s(ss,p,1e-8);assert abs(p.Mass()-vol)/vol<.001;steps.append(dict(part=n,step=rel(f),sha256=h(f)))
    save()
save();print(len(rows),sum(q['qty'] for q in rows),sum(bool(q.get('stl')) for q in rows),[(q['part'],q.get('export_state')) for q in rows if not q.get('stl')])
