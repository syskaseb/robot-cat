"""Independent reopen: geometry, placements, topology and native static solve.

Run with the bundled FreeCAD Python, not the ROS/pixi runtime.
Animation validation is performed by Simulation24.FCMacro in GUI FreeCAD.
"""
from pathlib import Path
import hashlib,json,sys,zipfile,xml.etree.ElementTree as ET
import FreeCAD as A
import Part
sys.path.insert(0,A.getHomePath()+'Mod/Assembly')
import JointObject
from probe21 import world,visible_names

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'hardware/skorupa/v24'
SOURCE=ROOT/'hardware/skorupa/v23/Kot_v23_AKUMULATOR_PETG.FCStd'
DEST=OUT/'Kot_v24_ASSEMBLY.FCStd'
plan=json.loads((OUT/'assembly-plan.json').read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(SOURCE)==plan['source_sha256']
dest_sha=sha(DEST)
with zipfile.ZipFile(SOURCE) as sz,zipfile.ZipFile(DEST) as dz:
    sv={v.get('name'):v for v in ET.fromstring(sz.read('GuiDocument.xml')).iter('ViewProvider')}
    dv={v.get('name'):v for v in ET.fromstring(dz.read('GuiDocument.xml')).iter('ViewProvider')}
    for row in plan['components']:
        n=row['name']
        sf=sv[n].find("Properties/Property[@name='ShapeAppearance']/MaterialList").get('file')
        df=dv[n].find("Properties/Property[@name='ShapeAppearance']/MaterialList").get('file')
        assert sz.read(sf)==dz.read(df),('saved per-face materials',n)
print('Saved per-face materials verified for all components',flush=True)
source=A.openDocument(str(SOURCE)); d=A.openDocument(str(DEST))
asm=d.getObject('RobotCatAssembly24')
assert asm and asm.TypeId=='Assembly::AssemblyObject'
vis=visible_names(DEST)
max_delta=0.; max_area_delta=0.; max_volume_delta=0.; count=0; samples=0; degenerate_edges=0
for row in plan['components']:
    n=row['name']; original=source.getObject(n); part=d.getObject(n)
    assert n in vis,n
    assert part.getParentGeoFeatureGroup().Name=='Rigid_'+n,n
    assert part.getGlobalPlacement().isSame(original.getGlobalPlacement(),1e-6),n
    a=world(original); b=world(part)
    # Saving world-space copies can canonicalize nested OCC locations.
    # Raw BRep text is therefore not an invariant. Check the actual global
    # topology, vertices, edge samples and surface samples instead.
    for attr in ['Solids','Faces','Edges','Vertexes']:
        assert len(getattr(a,attr))==len(getattr(b,attr)),(n,attr)
    volume_delta=abs(a.Volume-b.Volume)
    max_volume_delta=max(max_volume_delta,volume_delta)
    assert volume_delta<1e-5,n
    def point_check(p,q):
        global max_delta,samples
        delta=(p-q).Length
        assert delta<1e-6,(n,delta)
        max_delta=max(max_delta,delta); samples+=1
    for p,q in zip(a.Vertexes,b.Vertexes): point_check(p.Point,q.Point)
    for p,q in zip(a.Edges,b.Edges):
        assert abs(p.Length-q.Length)<1e-6,n
        if p.Length<1e-8 and q.Length<1e-8:
            # Seam poles have no discretizable curve; vertices were checked.
            degenerate_edges+=1
            continue
        assert abs(p.FirstParameter-q.FirstParameter)<1e-6,n
        assert abs(p.LastParameter-q.LastParameter)<1e-6,n
        for frac in [.1,.3,.5,.7,.9]:
            u=p.FirstParameter+frac*(p.LastParameter-p.FirstParameter)
            point_check(p.valueAt(u),q.valueAt(u))
    for p,q in zip(a.Faces,b.Faces):
        delta=abs(p.Area-q.Area); max_area_delta=max(max_area_delta,delta)
        assert delta<1e-5,n
        point_check(p.CenterOfMass,q.CenterOfMass)
        uv=p.ParameterRange
        assert max(abs(x-y) for x,y in zip(uv,q.ParameterRange))<1e-6,n
        for ufrac in [.1,.5,.9]:
            for vfrac in [.1,.5,.9]:
                u=uv[0]+ufrac*(uv[1]-uv[0]); v=uv[2]+vfrac*(uv[3]-uv[2])
                point_check(p.valueAt(u,v),q.valueAt(u,v))
    count+=1
    if count%25==0: print('Checked geometry',count,'/',len(plan['components']),flush=True)
g=next(o for o in asm.Group if o.TypeId=='Assembly::JointGroup')
assert len(g.Group)==238
for row in plan['joints']:
    j=d.getObject(row['name'])
    assert j in g.Group and j.JointType==row['type'],row['name']
    assert j.Reference1[0].Name=='Rigid_'+row['parent']
    assert j.Reference2[0].Name=='Rigid_'+row['child']
    assert j.Detach1 and j.Detach2
    assert j.DesignStatus==row['status']
sim=d.getObject('LegConnectionTest24')
assert sim and len(sim.Group)==12
assert all(m.Joint[0].JointType=='Revolute' for m in sim.Group)
print('Reopened geometry and native graph verified; solving...',flush=True)
result=asm.solve(); assert result==0,result
max_gap=0.
for row in plan['joints']:
    j=d.getObject(row['name'])
    a=j.Reference1[0].Placement*j.Placement1
    b=j.Reference2[0].Placement*j.Placement2
    max_gap=max(max_gap,(a.Base-b.Base).Length)
    assert a.isSame(b,1e-6),row['name']
assert sha(DEST)==dest_sha,'Checkpoint changed during verification; run again'
report=dict(file=DEST.name,sha256=dest_sha,reopened=True,source_sha256=sha(SOURCE),
    preserved_visible_shapes=count,geometry_sample_count=samples,degenerate_edges_checked_as_vertices=degenerate_edges,
    maximum_geometry_sample_delta_mm=max_delta,
    maximum_face_area_delta_mm2=max_area_delta,maximum_volume_delta_mm3=max_volume_delta,
    fixed_joints=225,revolute_joints=12,grounded_parts=1,temporary_locks=len(plan['temporary_locks']),
    saved_per_face_materials_preserved=True,
    solver_result=result,max_joint_gap_mm=max_gap,native_simulation_motions=len(sim.Group),
    whole_cat_visible=True,scope='Native geometry/constraint persistence, not mechanical print release or collision validation')
(OUT/'saved-document-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report),flush=True)
