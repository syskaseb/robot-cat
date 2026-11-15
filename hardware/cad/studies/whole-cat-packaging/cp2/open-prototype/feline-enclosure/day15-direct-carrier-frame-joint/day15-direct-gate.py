import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.getDocument('DAY15_DIRECT_CARRIER');P=Path(D.FileName).parent;T=time.perf_counter();r=dict(status='RUNNING_ONE_WHOLE_CANDIDATE_FOREIGN_GATE',bounds=0,checks=[],first_falsifier=None)
def save():(P/'candidate-whole-first-gate.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
def lo(s,q):
 a=s.BoundBox;b=q.BoundBox;return math.sqrt(sum(max(0,getattr(a,t+'Min')-getattr(b,t+'Max'),getattr(b,t+'Min')-getattr(a,t+'Max'))**2 for t in 'XYZ'))
def gate(n,s,m,q,limit=1.25):
 lb=lo(s,q)
 if lb>=limit+1e-5:r['bounds']+=1;return True
 gap=s.distToShape(q)[0];c=s.common(q) if gap<1e-6 or limit==0 else None;row=dict(a=n,b=m,gap=gap,required=limit,common=c.Volume if c else None,valid=c.isValid() if c else True);r['checks'].append(row)
 ok=(c.isValid() and c.Volume<1e-5) if limit==0 else gap>=limit-1e-6
 if not ok:
  r['status']='FIRST_REAL_CANDIDATE_HOLD_STOP_ONE_FAMILY';r['first_falsifier']=row;s.exportBrep(str(P/'first-witness-a.brep'));q.exportBrep(str(P/'first-witness-b.brep'));save()
 return ok
targets=[]
for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
 if not hasattr(o,'Shape') or o.Shape.isNull() or o.Name.startswith(('Ola_','Battery_crossarm_','Battery_edgepost_')) or o.Name in ['Battery_tray_shared','Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits'] or 'bracket_space' in o.Name:continue
 targets.append((o.Name,o.Shape))
for gn in ['USED_FASTENERS_nominal_fit','NEW_CLAMP_HARDWARE_NEEDED_UNCONFIRMED','NEW_CSUNK_STANDARD_STEEL_PROPOSED','OCCUPIED_PROFILE_PLUS_OUTER04_MARGIN','PI_INTERNAL_M2p5x8_FULL_STANDARD_SETS']:
 g=D.getObject(gn)
 if g:targets.extend((o.Name,o.Shape) for o in g.Group if hasattr(o,'Shape') and hasattr(o.ViewObject,'ShapeColor'))
for n in ['P10_front_gate','P11_rear_gate','P13_BUS_bridge','P14_fixed_touch_rail','P15_removable_mic_rail','BNO_FULL_SOURCE_INSTALLATION_COVER','RS_USB_FULL_SOURCE_COVER']:
 o=D.getObject(n)
 if o:targets.append((n,o.Shape))
targets.extend((o.Name,o.Shape) for o in D.Objects if o.Name.startswith(('STRAP0_','STRAP1_')) and hasattr(o,'Shape'))
def run():
 # Entirecandidate steel and allnecessarynewprintmembers vsactualretainedcases/stock.
 for o in D.getObject('DIRECT_PLANNED_INTERFACE_BEFORE_UNION').Group:
  for n,q in targets:
   if not gate(o.Name,o.Shape,n,q):return
  if o.Name.startswith('DIRECT_P19_'):
   if not gate(o.Name,o.Shape,'existingP12',D.getObject('P12_common_deck_speaker').Shape,0 if o.Name=='DIRECT_P19_flange' else 1.25):return
 r['status']='CANDIDATE_ENTIRE_STEEL_AND_MEMBERS_FOREIGN_CLEAR_SCOPED';r['seconds']=time.perf_counter()-T;save()
run();print(json.dumps(dict(status=r['status'],bounds=r['bounds'],exact=len(r['checks']),first=r['first_falsifier'],seconds=time.perf_counter()-T)))
