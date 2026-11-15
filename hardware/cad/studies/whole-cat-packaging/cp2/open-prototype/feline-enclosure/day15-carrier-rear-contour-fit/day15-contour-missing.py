import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.getDocument('DAY15_CARRIER_CONTOUR');P=Path(D.FileName).parent;V=A.Vector;T=time.perf_counter();r=dict(status='RUNNING_ONLY_UNRECEIVED_CARRIER_AND_STOCK',bounds=0,checks=[],first_falsifier=None)
def save():(P/'missing-whole-carrier-gate.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
def lo(s,q):
 a=s.BoundBox;b=q.BoundBox;return math.sqrt(sum(max(0,getattr(a,t+'Min')-getattr(b,t+'Max'),getattr(b,t+'Min')-getattr(a,t+'Max'))**2 for t in 'XYZ'))
def gate(n,s,m,q,limit=1.25):
 lb=lo(s,q)
 if lb>=limit+1e-5:r['bounds']+=1;return True
 gap=s.distToShape(q)[0];c=s.common(q) if gap<1e-6 or limit==0 else None;row=dict(a=n,b=m,gap=gap,required=limit,common=None if c is None else c.Volume,valid=True if c is None else c.isValid());r['checks'].append(row)
 ok=(c.isValid() and c.Volume<1e-5) if limit==0 else gap>=limit-1e-6
 if not ok:
  r['status']='FIRST_MISSING_WHOLE_HOLD_STOP';r['first_falsifier']=row;s.exportBrep(str(P/'missing-witness-a.brep'));q.exportBrep(str(P/'missing-witness-b.brep'));save()
 return ok
targets=[]
for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
 if not hasattr(o,'Shape') or o.Shape.isNull() or o.Name.startswith(('Ola_','Battery_crossarm_','Battery_edgepost_')) or o.Name in ['Battery_tray_shared','Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits'] or 'bracket_space' in o.Name:continue
 targets.append((o.Name,o.Shape))
for gn in ['USED_FASTENERS_nominal_fit','NEW_CLAMP_HARDWARE_NEEDED_UNCONFIRMED','NEW_CSUNK_STANDARD_STEEL_PROPOSED','OCCUPIED_PROFILE_PLUS_OUTER04_MARGIN','PI_INTERNAL_M2p5x8_FULL_STANDARD_SETS']:
 g=D.getObject(gn)
 if g:targets.extend((o.Name,o.Shape) for o in g.Group if hasattr(o,'Shape') and hasattr(o.ViewObject,'ShapeColor'))
for n in ['BNO_FULL_SOURCE_INSTALLATION_COVER','RS_USB_FULL_SOURCE_COVER']:
 o=D.getObject(n)
 if o:targets.append((n,o.Shape))
def run():
 s=D.getObject('P19_shared_lower_carrier').Shape
 for n,q in targets:
  if n=='S0_body':continue # Newactual1.627gate alreadyreceived, not replay.
  own=n=='Battery_GEA223S30X6GT' or n.startswith('Leg_protected_MTA0100335_')
  if not gate('COMPLETE_P19',s,n,q,0 if own else 1.25):return
 r['carrier_remaining_foreign_clear']=True;save()
 # Whole2stock fields vsunreceivedforeign only; own/P13geometry proofs areunchanged andnotreplayed.
 for o in D.Objects:
  if not o.Name.startswith(('STRAP0_','STRAP1_')) or not hasattr(o,'Shape'):continue
  for n,q in targets:
   if not gate(o.Name,o.Shape,n,q,0 if n=='Battery_GEA223S30X6GT' else 1.25):return
 r['whole_two_stock_remaining_foreign_clear']=True;save()
 # Oldfrontcomplete4stock heldbysource32ac receipt; no newgeometry nearit, reuseforeign+ownscope.
 r['oldfront_stock']='Full4parts unchanged; prior32ac allfrontforeign+own rows precede oldrearSTOP. Notnewlycredited asframebearing/root.'
 r['newroot_reuse']='Direct89e3 unchangedexceptP19rearSUBSET:1815bounds/6newforeign+6ownsteel+membercoverage/disjoint remainidentity/subset.'
 r['status']='MISSING_WHOLE_CARRIER_AND_BOTH_WHOLE_STOCK_SCOPED_CLEAR';r['seconds']=time.perf_counter()-T;save()
run();print(json.dumps(dict(status=r['status'],bounds=r['bounds'],exact=len(r['checks']),first=r['first_falsifier'],seconds=time.perf_counter()-T)))
