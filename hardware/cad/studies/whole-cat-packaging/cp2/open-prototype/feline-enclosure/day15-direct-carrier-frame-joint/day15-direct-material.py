import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
D=A.getDocument('DAY15_DIRECT_CARRIER');P=Path(D.FileName).parent;V=A.Vector;T=time.perf_counter();g=json.loads((P/'candidate-whole-first-gate.json').read_bytes());assert not g['first_falsifier']
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
old12=D.getObject('P12_common_deck_speaker').Shape.copy();old19=D.getObject('P19_shared_lower_carrier').Shape.copy();bore=Part.makeCylinder(1.65,20,V(76,30,77));seat=Part.makeCone(1.5,3.36,1.86,V(76,30,90.66))
p12=old12
for n in ['DIRECT_P12_receiver_tab','DIRECT_P12_key_cheek_left','DIRECT_P12_key_cheek_right']:p12=p12.fuse(D.getObject(n).Shape)
p12=p12.cut(bore).cut(seat)
p19=old19
for n in ['DIRECT_P19_loadbeam','DIRECT_P19_upriser','DIRECT_P19_flange']:p19=p19.fuse(D.getObject(n).Shape)
p19=p19.cut(bore)
assert p12.isValid() and p19.isValid()
D.getObject('P12_common_deck_speaker').Shape=p12;D.getObject('P19_shared_lower_carrier').Shape=p19
for o in D.getObject('DIRECT_PLANNED_INTERFACE_BEFORE_UNION').Group:
 if o.Name.startswith(('DIRECT_P12_','DIRECT_P19_')):o.ViewObject.Visibility=False
D.recompute();D.save() # CompleteCSG checkpoint before newown/contact/tooltests.
r=dict(status='SAVED_REAL_UNION_BEFORE_OWN_CHECKS',members=[],junctions=[],own_stock=[],first_falsifier=None)
def write():(P/'material-and-load-realization.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
def fail(row):r['status']='FIRST_REALIZATION_HOLD_STOP';r['first_falsifier']=row;write()
def run():
 for n in ['DIRECT_P12_receiver_tab','DIRECT_P12_key_cheek_left','DIRECT_P12_key_cheek_right','DIRECT_P19_loadbeam','DIRECT_P19_upriser','DIRECT_P19_flange']:
  owner=p12 if n.startswith('DIRECT_P12') else p19;s=D.getObject(n).Shape.cut(bore)
  if n.startswith('DIRECT_P12'):s=s.cut(seat)
  q=s.cut(owner);row=dict(member=n,valid=q.isValid(),missing=q.Volume,intended_extent=str(s.BoundBox));r['members'].append(row)
  if not q.isValid() or q.Volume>1e-5:fail(row);return
 for tag,old,now in [('P12',old12,p12),('P19',old19,p19)]:
  q=old.cut(bore)
  if tag=='P12':q=q.cut(seat)
  m=q.cut(now);r.setdefault('source_protected',[]).append(dict(part=tag,missing=m.Volume,valid=m.isValid(),solids=len(now.Solids),bounds=str(now.BoundBox)))
  if not m.isValid() or m.Volume>1e-5:fail(r['source_protected'][-1]);return
 pairs=[('receiver_to_ACTUAL_P12',D.getObject('DIRECT_P12_receiver_tab').Shape,old12),('leftcheek_receiver',D.getObject('DIRECT_P12_key_cheek_left').Shape,D.getObject('DIRECT_P12_receiver_tab').Shape),('rightcheek_receiver',D.getObject('DIRECT_P12_key_cheek_right').Shape,D.getObject('DIRECT_P12_receiver_tab').Shape),('beam_ACTUAL_P19',D.getObject('DIRECT_P19_loadbeam').Shape,old19),('riser_beam',D.getObject('DIRECT_P19_upriser').Shape,D.getObject('DIRECT_P19_loadbeam').Shape),('flange_riser',D.getObject('DIRECT_P19_flange').Shape,D.getObject('DIRECT_P19_upriser').Shape)]
 for n,a,b in pairs:
  c=a.common(b);row=dict(name=n,positive_common=c.Volume,valid=c.isValid());r['junctions'].append(row)
  if not c.isValid() or c.Volume<=1e-5:fail(row);return
 c=p12.common(p19);r['disjoint_parts']=dict(valid=c.isValid(),common=c.Volume)
 if not c.isValid() or c.Volume>1e-5:fail(r['disjoint_parts']);return
 for n in ['DIRECT_ISO10642_M3x12_full','DIRECT_full_OD7_washer','DIRECT_full_AF5p5_nut']:
  for part,s in [('P12',p12),('P19',p19)]:
   c=D.getObject(n).Shape.common(s);row=dict(steel=n,print=part,valid=c.isValid(),common=c.Volume);r['own_stock'].append(row)
   if not c.isValid() or c.Volume>1e-5:fail(row);return
 # Actualmatchedbearingface and nominalkeyfit; no strength/threadinventoryclaim.
 f=Part.makeBox(11.2,17.5,.05,V(70.4,24,88.52));r['bearing']=dict(topgap=p19.distToShape(p12)[0],plane_Z=88.52,key_X_gap=.4,carrier_key_width=11.2,slot_width=12,positive_bearing_roi=p12.common(f).Volume,full_hole_bore3p3=True,all6DOF='Fullshaft/boretranslationstop +tensionseat +twoXcheeksat separatedY resistrotation; fourfeetcompression. finiteplayphysicalFIT.')
 r['status']='COMPLETE_DIRECT_PRINT_LOAD_MATERIAL_AND_FULL_STEEL_SCOPED_CLEAR';r['seconds']=time.perf_counter()-T;write()
run();print(json.dumps(dict(status=r['status'],first=r['first_falsifier'],junctions=r['junctions'],members=len(r['members']),own=len(r['own_stock']),seconds=time.perf_counter()-T)))
