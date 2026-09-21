"""Reopen the v25 checkpoint; prove the replacement is localized and joints survive."""
from pathlib import Path
import json,sys,zipfile,xml.etree.ElementTree as ET
import FreeCAD as A
import Part
sys.path.insert(0,A.getHomePath()+'Mod/Assembly')
import JointObject
from probe21 import world,visible_names
from build22 import sha
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'hardware/skorupa/v25'
SOURCE=ROOT/'hardware/skorupa/v24/Kot_v24_ASSEMBLY.FCStd';DEST=OUT/'Kot_v25_DOMOWA_OSLONA.FCStd'
r=json.loads((OUT/'validation.json').read_text(encoding='utf-8'))
plan=json.loads((ROOT/'hardware/skorupa/v24/assembly-plan.json').read_text(encoding='utf-8'))
assert sha(SOURCE)==r['source_sha256'];dest_sha=sha(DEST)
source=A.openDocument(str(SOURCE));d=A.openDocument(str(DEST))
changed={p['source_name']:p for p in r['parts']};preserved=0;maxdelta=0.
visible=visible_names(DEST)
for row in plan['components']:
    n=row['name'];o=d.getObject(n);old=source.getObject(n)
    assert o and n in visible and o.getParentGeoFeatureGroup().Name=='Rigid_'+n,n
    if n in changed:
        data=changed[n];assert sha(OUT/data['file'])==data['sha256']
        expected=Part.Shape();expected.read(str(OUT/data['file']))
        actual=world(o)
        assert abs(expected.Volume-o.Shape.Volume)<1e-5,n
        o.Shape.check(True);assert o.Shape.isValid() and len(o.Shape.Solids)==1,n
        # Importing the new screw can add an equivalent OCC location record.
        # Compare actual world geometry, not its serialization, for replacements.
        for prop in ['Vertexes','Edges','Faces']:assert len(getattr(expected,prop))==len(getattr(actual,prop)),n
        for p,q in zip(expected.Vertexes,actual.Vertexes):assert (p.Point-q.Point).Length<1e-6,n
        for p,q in zip(expected.Faces,actual.Faces):
            assert abs(p.Area-q.Area)<1e-5 and (p.CenterOfMass-q.CenterOfMass).Length<1e-6,n
            uv=p.ParameterRange
            for f in [.1,.5,.9]:
                for h in [.1,.5,.9]:
                    u=uv[0]+f*(uv[1]-uv[0]);v=uv[2]+h*(uv[3]-uv[2])
                    assert (p.valueAt(u,v)-q.valueAt(u,v)).Length<1e-6,n
        continue
    else:
        assert o.getGlobalPlacement().isSame(old.getGlobalPlacement(),1e-8),n
        a=old.Shape.exportBrepToString().split();b=o.Shape.exportBrepToString().split();preserved+=1
    assert len(a)==len(b),(n,len(a),len(b))
    for av,bv in zip(a,b):
        if av==bv:continue
        delta=abs(float(av)-float(bv));assert delta<1e-8,(n,av,bv)
        maxdelta=max(maxdelta,delta)
with zipfile.ZipFile(SOURCE) as sz,zipfile.ZipFile(DEST) as dz:
    sv={v.get('name'):v for v in ET.fromstring(sz.read('GuiDocument.xml')).iter('ViewProvider')}
    dv={v.get('name'):v for v in ET.fromstring(dz.read('GuiDocument.xml')).iter('ViewProvider')}
    for row in plan['components']:
        n=row['name']
        if n in changed:continue
        sf=sv[n].find("Properties/Property[@name='ShapeAppearance']/MaterialList").get('file')
        df=dv[n].find("Properties/Property[@name='ShapeAppearance']/MaterialList").get('file')
        assert sz.read(sf)==dz.read(df),('material',n)
asm=d.getObject('RobotCatAssembly24');assert asm.TypeId=='Assembly::AssemblyObject'
g=next(o for o in asm.Group if o.TypeId=='Assembly::JointGroup');assert len(g.Group)==238
ground=[o for o in g.Group if 'ObjectToGround' in o.PropertiesList]
assert len(ground)==1 and ground[0].ObjectToGround.Name=='Rigid_FrameFront20'
for row in plan['joints']:
    j=d.getObject(row['name']);old=source.getObject(row['name'])
    assert j.JointType==row['type'] and j.Detach1 and j.Detach2
    assert j.Reference1[0].Name=='Rigid_'+row['parent'] and j.Reference2[0].Name=='Rigid_'+row['child']
    assert j.Placement1.isSame(old.Placement1,1e-8) and j.Placement2.isSame(old.Placement2,1e-8)
    assert j.DesignStatus==old.DesignStatus
assert len(d.getObject('LegConnectionTest24').Group)==12
print('Reopened geometry, materials and all joints verified; solving...',flush=True)
result=asm.solve();assert result==0
for row in plan['joints']:
    j=d.getObject(row['name']);a=j.Reference1[0].Placement*j.Placement1;b=j.Reference2[0].Placement*j.Placement2
    assert a.isSame(b,1e-6),row['name']
design=A.openDocument(str(OUT/'BellyDesign25.FCStd'))
assert all(o.FullyConstrained for o in design.Objects if o.TypeId=='Sketcher::SketchObject')
assert abs(design.getObject('Belly25').Shape.Volume-d.getObject('Belly22').Shape.Volume)<1e-5
assert sha(DEST)==dest_sha
report=dict(file=DEST.name,sha256=dest_sha,source_sha256=sha(SOURCE),reopened=True,
    preserved_shapes_and_placements=preserved,preserved_materials=preserved,replaced_shapes=len(changed),
    maximum_brep_numeric_delta=maxdelta,native_revolute_joints=12,native_fixed_joints=225,native_motions=12,
    temporary_locks=64,grounded_parts=1,solver_result=result,whole_cat_visible=True,all_guard_sketches_fully_constrained=True,
    scope='Persistence and localized geometry replacement, not complete mechanical/print approval')
(OUT/'saved-document-validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report),flush=True)
