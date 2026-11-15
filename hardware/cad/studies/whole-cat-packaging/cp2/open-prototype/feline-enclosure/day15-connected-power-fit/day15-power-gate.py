import FreeCAD as A, Part,json,time,math
from pathlib import Path
D=A.getDocument('DAY15_CONNECTED_POWER_FIT');P=Path(D.FileName).parent;T=time.perf_counter();r=dict(status='RUNNING',bounds=0,checks=[],first_falsifier=None)
def save():
 r['seconds']=time.perf_counter()-T;(P/'power-region-result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
def lb(s,q):
 a=s.BoundBox;b=q.BoundBox;return math.sqrt(sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in 'XYZ'))
targets=[]
skip={'XT60H_mated_with_boots','Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits'}
for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
 if not hasattr(o,'Shape') or o.Shape.isNull() or o.Name in skip or o.Name.startswith('Ola_'):continue
 if o.Name=='WAVEGO_complete_126_source_solids':targets.extend(('WAVEGOsolid'+str(i),s) for i,s in enumerate(o.Shape.Solids))
 else:targets.append((o.Name,o.Shape))
for group in ['FASTENING_REAL_PRINT_PARTS','OCCUPIED_PROFILE_PLUS_OUTER04_MARGIN']:
 targets.extend((o.Name,o.Shape) for o in D.getObject(group).Group if hasattr(o,'Shape'))
for o in D.Objects:
 if o.Name.startswith(('METAL_','HARD_','BNO_FULL_SOURCE','RS_USB_FULL_SOURCE')) and hasattr(o,'Shape'):targets.append((o.Name,o.Shape))
def run():
 fields=[D.getObject('XT60H_mated_with_boots')]+list(D.getObject('CONNECTED_POWER_CAPACITY_NOT_RIGID_WIRES').Group)
 for o in fields:
  for n,s in targets:
   b=lb(o.Shape,s)
   if b>=1.25001:r['bounds']+=1;continue
   gap=o.Shape.distToShape(s)[0];row=dict(field=o.Name,neighbor=n,gap=gap,limit=1.25)
   r['checks'].append(row)
   if gap<1.25-1e-6:
    c=o.Shape.common(s);row.update(common_mm3=c.Volume,valid=c.isValid());r['first_falsifier']=row;r['status']='ALLOCATED_REGION_HOLD_NOT_DELIVERED_CONTACT';o.Shape.exportBrep(str(P/'region-witness-a.brep'));s.exportBrep(str(P/'region-witness-b.brep'));save();return
  save()
 r['status']='CONNECTED_NOMINAL_POWER_REGIONS_CLEAR_SCOPED';save()
run();print(json.dumps(r))
