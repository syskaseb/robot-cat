"""Data-only final source-occurrence correction; run after frame builder, not a new design."""
import FreeCAD as A,MeshPart,json
from pathlib import Path
D=A.getDocument('DAY15_ESSENTIAL_SHARED_FRAME');P=Path(r'C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-essential-shared-frame')
s=D.getObject('CL_Rp_lower').Shape
o=D.getObject('P18_rear_positive_lower_jaw')
if o is None:o=D.addObject('PartDesign::Feature','P18_rear_positive_lower_jaw');o.Shape=s;D.getObject('ESSENTIAL_REAL_PRINT_PARTS').addObject(o)
local=s.copy();b=local.BoundBox;local.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin));MeshPart.meshFromShape(Shape=local,LinearDeflection=.15,AngularDeflection=.2,Relative=False).write(str(P/'P18_rear_positive_lower_jaw.stl'));s.exportBrep(str(P/'P18_rear_positive_lower_jaw.brep'))
D.getObject('CL_Fp_lower').ViewObject.Visibility=True;D.getObject('CL_Fp_lower').Label='P16 second occurrence — source frontjaw flipped, exact0/0'
plan=json.loads((P/'parting.json').read_bytes());next(x for x in plan['parts'] if x['name']=='P17_rear_lower_jaw')['quantity']=1
if not any(x['name']=='P18_rear_positive_lower_jaw' for x in plan['parts']):
 b=s.BoundBox;plan['parts'].append(dict(name='P18_rear_positive_lower_jaw',quantity=1,world_bounds_mm=[[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]],print_size_mm=[b.XLength,b.YLength,b.ZLength],valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume,print_orientation='sourcepositivejaw bottomZ0',support_note='Do not mirror source negativejaw',retention_scope='Actual unchanged source positivejaw'))
plan['quantity_disposition']='Front2 exactflip0/0; rearnegative1/rearpositive1 because mirror source difference15.5/30.725mm3';(P/'parting.json').write_bytes((json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode());D.recompute();D.save()
