import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
D=A.getDocument('DAY15_POWER_CAPACITY');P=Path(D.FileName).parent;plan=json.loads((P/'capacity-plan.json').read_bytes());old=A.getDocument('DAY15_CONNECTED_POWER_FIT')
if old:A.closeDocument(old.Name)
# Missing source steel check for local profiles only, not old fullmetal matrix.
joint=json.loads((P.parent/'day15-frame-fastening/whole-fastening-plan.json').read_bytes());checks=[]
for rec in plan['profiles']:
 s=D.getObject(rec['name']).Shape;a=s.BoundBox
 for j in joint['joints']:
  for n in j['objects']:
   q=D.getObject(n).Shape;b=q.BoundBox;lb=math.sqrt(sum(max(0,getattr(a,t+'Min')-getattr(b,t+'Max'),getattr(b,t+'Min')-getattr(a,t+'Max'))**2 for t in 'XYZ'));assert lb>=1.25,(n,lb);checks.append(dict(profile=rec['name'],metal=n,lower=lb))
(P/'local-steel-bounds.json').write_bytes((json.dumps(dict(status='SIXTY_NEW_PROFILE_TO_FULL_STEEL_BOUNDS_CLEAR',checks=checks),indent=2)+'\n').encode())
roi=Part.makeBox(25,18,.01,A.Vector(-14,-9,93.995));s=D.getObject('P12_common_deck_speaker').Shape.common(roi);assert s.isValid();o=D.addObject('PartDesign::Feature','P12_ACTUAL_SECTION_SLICE_Z94');o.Shape=s;o.ViewObject.ShapeColor=(.25,.3,.35);o.ViewObject.Transparency=0
theta=math.radians(plan['packing']['entry_roll_degrees']);out=dict(section_Z=94,actual_P12_boundary_X=-10,required_1p25_boundary_X=-8.75,circle_profiles=[],actual_section_edges=[])
for sign in [-1,1]:out['circle_profiles'].append(dict(centre=[-2+sign*3.5*math.cos(theta),sign*3.5*math.sin(theta)],nominal_radius=3,margin_radius=3.4))
sec=D.getObject('P12_actual_section').Shape
for e in sec.Edges:out['actual_section_edges'].append([[v.x,v.y] for v in e.discretize(20)])
(P/'local-section-data.json').write_bytes((json.dumps(out,indent=2)+'\n').encode())
D.Label='DAY15 power capacity — P12 clear / F0 allocation HOLD';D.recompute();D.save()
# Only local proof and source material for viewport; all retained context remains in native model.
for o in D.Objects:
 if hasattr(o,'Shape') and hasattr(o.ViewObject,'Visibility'):o.ViewObject.Visibility=o.Name in ['P12_ACTUAL_SECTION_SLICE_Z94','P12_FULL_OD6_MARGIN04_LEFT','P12_FULL_OD6_MARGIN04_RIGHT','P12_UNCHANGED_R24_UPPER_ARC_REGION','P12_common_deck_speaker']
D.getObject('P12_common_deck_speaker').ViewObject.Transparency=80
print(dict(objects=len(D.Objects),localsteel=len(checks),section='actualsourceZ94',saved_beforeview=True))
