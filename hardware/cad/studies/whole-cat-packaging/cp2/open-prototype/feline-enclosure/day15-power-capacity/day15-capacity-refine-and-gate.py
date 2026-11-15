import FreeCAD as A,Part,json,math,time
from pathlib import Path
V=A.Vector;D=A.getDocument('DAY15_POWER_CAPACITY');P=Path(D.FileName).parent;plan=json.loads((P/'capacity-plan.json').read_bytes());T=time.perf_counter();z0=95.52;z1=106.;L=z1-z0;r=3.5;rho=3.4;theta=math.radians(plan['packing']['entry_roll_degrees']);vel=2*theta/L;k=plan['packing']['curvature_upper'];clip=Part.makeBox(40,40,18,V(-20,-20,88))
def angle(z):
 t=(z-z0)/L
 return theta if t<=0 else theta*(1-2*t*t) if t<.5 else 2*theta*(1-t)**2
def centre(z,s):
 t=angle(z);return V(-2+s*r*math.cos(t),s*r*math.sin(t),z)
for sign,rec in zip([-1,1],plan['profiles']):
 nodes=[88,z0]+[z0+L*i/48 for i in range(1,49)];pieces=[]
 for i,(za,zb) in enumerate(zip(nodes,nodes[1:])):
  ca=centre(za,sign);cb=centre(zb,sign);v=cb-ca;sag=0 if zb<=z0 else k*(zb-za)**2/8;rad=rho+sag+1e-6;tlo=max(0,(za-z0)/L);thi=max(0,(zb-z0)/L)
  tpmax=vel if za<=z0+L/2<=zb else max(4*theta/L*min(tlo,max(0,1-tlo)),4*theta/L*min(thi,max(0,1-thi)))
  nz=rho*r*tpmax/math.sqrt(1+(r*tpmax)**2)+sag+1e-6
  cellclip=Part.makeBox(40,40,(zb-za)+2*nz,V(-20,-20,za-nz)).common(clip)
  pieces.append(Part.makeCylinder(rad,v.Length,ca,v).common(cellclip))
  if i>0:pieces.append(Part.makeSphere(rad,ca).common(cellclip))
 s=Part.makeCompound(pieces);assert s.isValid();D.getObject(rec['name']).Shape=s
 rec['normalZ_cell_bound']='rho*r*maxabs(theta_prime)/sqrt(1+(r*theta_prime)^2)+sag; clips only irrelevant spherical-cap overcoverage, preserves every continuous normal disc'
plan['coverage']='Analytic C1 centrepaths; full normal discs radius3.4 are contained in each polyline capsule radius3.4+|c_second|max*dz^2/8, clipped ONLY by analytic normal-disc Z reach. WholeP12/currentneighbors gate; no sampled-only path claim.'
(P/'capacity-plan.json').write_bytes((json.dumps(plan,indent=2)+'\n').encode());D.recompute();D.save()
result=dict(status='RUNNING',bounds=0,checks=[],first_falsifier=None)
def save():
 result['seconds']=time.perf_counter()-T;(P/'capacity-result.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
def lower(s,q):
 a=s.BoundBox;b=q.BoundBox;return math.sqrt(sum(max(0,getattr(a,t+'Min')-getattr(b,t+'Max'),getattr(b,t+'Min')-getattr(a,t+'Max'))**2 for t in 'XYZ'))
targets=[('P12_common_deck_speaker',D.getObject('P12_common_deck_speaker').Shape)]
skip={'XT60H_mated_with_boots','Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits'}
for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
 if not hasattr(o,'Shape') or o.Shape.isNull() or o.Name in skip or o.Name.startswith('Ola_'):continue
 if o.Name=='WAVEGO_complete_126_source_solids':targets.extend(('WAVEGOsolid'+str(i),s) for i,s in enumerate(o.Shape.Solids))
 else:targets.append((o.Name,o.Shape))
for group in ['FASTENING_REAL_PRINT_PARTS','OCCUPIED_PROFILE_PLUS_OUTER04_MARGIN']:
 targets.extend((o.Name,o.Shape) for o in D.getObject(group).Group if hasattr(o,'Shape') and o.Name!='P12_common_deck_speaker')
for o in D.Objects:
 if o.Name.startswith(('METAL_','HARD_','BNO_FULL_SOURCE','RS_USB_FULL_SOURCE')) and hasattr(o,'Shape'):targets.append((o.Name,o.Shape))
def run():
 for rec in plan['profiles']:
  s=D.getObject(rec['name']).Shape
  for n,q in targets:
   lb=lower(s,q)
   if lb>=1.25001:result['bounds']+=1;continue
   gap=s.distToShape(q)[0];row=dict(profile=rec['name'],neighbor=n,gap=gap,limit=1.25);result['checks'].append(row)
   if gap<1.25-1e-6:
    c=s.common(q);row.update(common_mm3=c.Volume,valid=c.isValid());result['first_falsifier']=row;result['status']='CAPACITY_HOLD_NOT_DELIVERED_CONTACT';s.exportBrep(str(P/'capacity-witness-a.brep'));q.exportBrep(str(P/'capacity-witness-b.brep'));save();return
  save()
 result['status']='P12_TWO_FULL_PROFILES_CONTINUOUS_NORMAL_COVER_CLEAR_SCOPED';save()
run();print(json.dumps(result))
