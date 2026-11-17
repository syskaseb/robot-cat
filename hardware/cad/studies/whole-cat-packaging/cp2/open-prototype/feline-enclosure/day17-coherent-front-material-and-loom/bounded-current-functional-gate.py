import FreeCAD as A,Part,json,math,time
from pathlib import Path
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector;rows=[];t0=time.perf_counter()
put=lambda n,j:(P/n).write_bytes((json.dumps(j,indent=2)+'\n').encode())
def bound(a,b):
 a=a.BoundBox;b=b.BoundBox;return sum(max(0,getattr(a,x+'Min')-getattr(b,x+'Max'),getattr(b,x+'Min')-getattr(a,x+'Max'))**2 for x in 'XYZ')**.5
def gate(n,s,m,b,req=1.25):
 l=bound(s,b);r={'part':n,'neighbor':m,'lower':l,'required':req}
 if l>=req:r['clear']=True
 else:
  r['gap']=s.distToShape(b)[0];r['clear']=r['gap']>=req-1e-7
  if not r['clear']:r['common']=s.common(b).Volume
 rows.append(r);put('current-affected-material-and-profile-gate.json',{'rows':rows,'cursor':n+' / '+m,'wholekit':False})
base=D.getObject('CF17_SHARED_FIXED_PI_BUS_POWER_CARRIER').Shape;src=D.getObject('A17_INTEGRAL_FRONT_DECK_AND_N1').Shape
c=base.common(src)
put('actual-root-intersection-and-parting.json',{'source':'A17 actual source unchanged','root_commonV':c.Volume,'intersections':[{'volume':s.Volume,'bounds':str(s.BoundBox)} for s in c.Solids],'three_separate_print_common':[D.getObject(a).Shape.common(D.getObject(b).Shape).Volume for a,b in [('CF17_SHARED_FIXED_PI_BUS_POWER_CARRIER','CF17_REMOVABLE_COMMON_E1_ROOT_KEEPER'),('CF17_SHARED_FIXED_PI_BUS_POWER_CARRIER','CF17_POWER_INDEPENDENT_BOOT_AND_ADAPTER_KEEPER'),('CF17_REMOVABLE_COMMON_E1_ROOT_KEEPER','CF17_POWER_INDEPENDENT_BOOT_AND_ADAPTER_KEEPER')]],'own_contact_NOT_waiver':True})
# Named local profile edges and actual newcomponent primaryfields. Only current recipe/delta.
for y,p,nn in [(0,0,'N17_FFC200_OCCUPIED_0_0'),(-20,10,'N17_FFC200_OCCUPIED_m20_10'),(20,10,'N17_FFC200_OCCUPIED_20_10')]:
 s=D.getObject(nn).Shape;f=D.getObject('HEAD_MOVING_SENSOR_FRAME_AND_COVER_SPINE').Shape.copy();f.rotate(V(-135,0,121),V(0,1,0),p);f.rotate(V(-106,0,127),V(0,0,1),y)
 gate(nn,s,'newcorrelated_sensor_frame',f)
for o in D.Objects:
 if o.Name.startswith('CF17_PI_PRIMARY_') and not o.Name.endswith('CSI'):
  gate('neutral_fullFFC',D.getObject('N17_FFC200_OCCUPIED_0_0').Shape,o.Name,o.Shape)
gate('neutral_fullFFC',D.getObject('N17_FFC200_OCCUPIED_0_0').Shape,'unlabelled4mm_top_budget',D.getObject('CF17_PI_SMALL_TOP_COMPONENT_BUDGET').Shape)
for n in ['CF17_SHARED_FIXED_PI_BUS_POWER_CARRIER','CF17_REMOVABLE_COMMON_E1_ROOT_KEEPER','CF17_POWER_INDEPENDENT_BOOT_AND_ADAPTER_KEEPER']:
 for m in ['PCA9685_Adafruit815_PCB','E1_populated_prototype_board','Pi_USB_DATA_Delock_mating','PBAY_F_PI','Battery_GEA223S30X6GT','N17_ALL117_BUS_PRIMARY_EXTENT_REFERENCE_NOT_MATERIAL','HEAD_YAW_FORK_FIXED_PITCH_HOUSING']:
  if n=='CF17_REMOVABLE_COMMON_E1_ROOT_KEEPER' and m=='E1_populated_prototype_board':continue # specifically intended FR4topland, notblanketOwn
  gate(n,D.getObject(n).Shape,m,D.getObject(m).Shape)
put('current-affected-material-and-profile-gate.json',{'rows':rows,'failures':[r for r in rows if not r['clear']],'wholekit':False,'scope':'new3receivers/currentFFC/sourceprimaryPiFootprints andnamedadjacentcases only; source180/169notreplayed','seconds':time.perf_counter()-t0})
print(json.dumps({'rootcommon':c.Volume,'rootregions':[(s.Volume,str(s.BoundBox)) for s in c.Solids],'fails':[r for r in rows if not r['clear']],'seconds':time.perf_counter()-t0}))
