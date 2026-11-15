import FreeCAD as A,Part,json,math,time
from pathlib import Path
V=A.Vector;D=A.getDocument('DAY15_P12_INTEGRATED');P=Path(D.FileName).parent;OLD=P.parent/'day15-frame-fastening';T=time.perf_counter();r=dict(status='RUNNING_ONLY_CHANGED_FOREIGN_GATE',bounds=0,checks=[],first_falsifier=None)
def hx(af,z,h):
 rr=af/math.sqrt(3);pp=[V(rr*math.cos(i*math.pi/3),rr*math.sin(i*math.pi/3),z) for i in range(7)];return Part.Face(Part.Wire(Part.makePolygon(pp).Edges)).extrude(V(0,0,h))
steel=[];gr=D.addObject('App::DocumentObjectGroup','CARRIER_TWO_COMPLETE_M3_NEEDED_UNCONFIRMED')
for tag,origin,direction,stack,L in [('front',[-104.5,-35,70],[1,0,0],10.5,16),('rear',[107.5,-35,70],[-1,0,0],16.5,25)]:
 bolt=Part.makeCylinder(1.5,L).fuse(Part.makeCylinder(2.75,3,V(0,0,-3))).cut(hx(2.5,-3,1.3));w1=Part.makeCylinder(3.5,.5).cut(Part.makeCylinder(1.6,.5));w2=Part.makeCylinder(3.5,.5,V(0,0,stack)).cut(Part.makeCylinder(1.6,.5,V(0,0,stack)));nut=hx(5.5,stack+.5,2.4).cut(Part.makeCylinder(1.5,2.4,V(0,0,stack+.5)))
 for role,s in [('bolt',bolt),('headwasher',w1),('nutwasher',w2),('fullnut',nut)]:
  s.Placement=A.Placement(V(*origin),A.Rotation(V(0,0,1),V(*direction)));n='CARRIER_'+tag+'_'+role;o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.7,.72,.75);gr.addObject(o);steel.append((n,s))
D.recompute();D.save()
def save():r['seconds']=time.perf_counter()-T;(P/'changed-foreign-first-gate.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
def gate(n,s,m,q,limit=1.25):
 a=s.BoundBox;b=q.BoundBox;lb=math.sqrt(sum(max(0,getattr(a,t+'Min')-getattr(b,t+'Max'),getattr(b,t+'Min')-getattr(a,t+'Max'))**2 for t in 'XYZ'))
 if lb>=limit+1e-5:r['bounds']+=1;return True
 gap=s.distToShape(q)[0];c=s.common(q) if gap<1e-6 or limit==0 else None;row=dict(a=n,b=m,gap=gap,limit=limit,common=None if c is None else c.Volume,valid=True if c is None else c.isValid());r['checks'].append(row);ok=(c.isValid() and c.Volume<1e-5) if limit==0 else gap>=limit-1e-6
 if not ok:r['first_falsifier']=row;r['status']='FIRST_CHANGED_FOREIGN_HOLD_ONE_HYPOTHESIS_STOP';s.exportBrep(str(P/'foreign-witness-a.brep'));q.exportBrep(str(P/'foreign-witness-b.brep'));save()
 return ok
targets=[]
for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
 if not hasattr(o,'Shape') or o.Shape.isNull() or o.Name.startswith(('Ola_','Battery_crossarm_','Battery_edgepost_')) or o.Name in ['Battery_tray_shared','Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits'] or 'bracket_space' in o.Name:continue
 targets.append((o.Name,o.Shape))
for n in ['BNO_FULL_SOURCE_INSTALLATION_COVER','RS_USB_FULL_SOURCE_COVER']:targets.append((n,D.getObject(n).Shape))
for gn in ['USED_FASTENERS_nominal_fit','NEW_CLAMP_HARDWARE_NEEDED_UNCONFIRMED','NEW_CSUNK_STANDARD_STEEL_PROPOSED','OCCUPIED_PROFILE_PLUS_OUTER04_MARGIN']:targets.extend((o.Name,o.Shape) for o in D.getObject(gn).Group if hasattr(o,'Shape'))
def run():
 for pn in ['P10_front_gate','P12_common_deck_speaker']:
  old=Part.Shape();old.read(str(OLD/(pn+'.brep')));s=D.getObject(pn).Shape.cut(old)
  if s.Volume<1e-5:continue
  for n,q in targets:
   if not gate(pn+'_positive_delta',s,n,q,0 if n=='Pi4B_actual_PCB' else 1.25):return
 r['Pi_new_positive_foreign_clear']=True;save()
 # Complete newM3 stock vs sourceactualcases before carrierrelease, no whole126 exact.
 for m,s in steel:
  for n,q in targets:
   if not gate(m,s,n,q):return
  for n in ['P10_front_gate','P11_rear_gate','P19_shared_lower_carrier']:
   if not gate(m,s,n,D.getObject(n).Shape,0):return
 r['new_carrier_full8steel_clear']=True;save()
 s=D.getObject('P19_shared_lower_carrier').Shape
 for n,q in targets:
  matched=(n=='Battery_GEA223S30X6GT' or n.startswith('Leg_protected_MTA0100335_'))
  if not gate('P19',s,n,q,0 if matched else 1.25):return
 for n in ['P02_front_deck','P03_rear_deck_integrated_load_yoke']:
  if not gate('P19',s,n,D.getObject(n).Shape,0):return
 r['carrier_actual_foreign_and_deck_disjoint_clear']=True;save()
 for o in D.Objects:
  if not o.Name.startswith('STRAP'):continue
  for n,q in targets:
   if n=='Battery_GEA223S30X6GT':limit=0
   else:limit=1.25
   if not gate(o.Name,o.Shape,n,q,limit):return
 r['status']='ONLY_CHANGED_FOREIGN_STEEL_CARRIER_STOCK_FIELDS_CLEAR_SCOPED';save()
run();print(json.dumps(dict(status=r['status'],bounds=r['bounds'],checks=len(r['checks']),first=r['first_falsifier'],Pi_positive=r.get('Pi_new_positive_foreign_clear'),steel=r.get('new_carrier_full8steel_clear'),seconds=r['seconds'])))
