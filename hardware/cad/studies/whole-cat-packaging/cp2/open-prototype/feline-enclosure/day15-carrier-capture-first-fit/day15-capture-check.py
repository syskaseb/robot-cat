import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.getDocument('DAY15_CARRIER_CAPTURE');P=Path(D.FileName).parent;V=A.Vector;T=time.perf_counter();r=dict(status='RUNNING_ONLY_CHANGED_POSITIVE_AND_COMPLETE_KNOWN_CONSTRAINTS',bounds=0,checks=[],failures=[])
def lo(s,q):
 a=s.BoundBox;b=q.BoundBox;return math.sqrt(sum(max(0,getattr(a,t+'Min')-getattr(b,t+'Max'),getattr(b,t+'Min')-getattr(a,t+'Max'))**2 for t in 'XYZ'))
def check(a,s,b,q,lim=1.25):
 if lo(s,q)>lim+1e-5:r['bounds']+=1;return
 gap=s.distToShape(q)[0];c=s.common(q) if gap<1e-6 or lim==0 else None;row=dict(a=a,b=b,gap=gap,required=lim,common=None if c is None else c.Volume,valid=True if c is None else c.isValid());r['checks'].append(row)
 ok=(c.isValid() and c.Volume<1e-5) if lim==0 else gap>=lim-1e-6
 if not ok:r['failures'].append(row)
targets=[]
for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
 if not hasattr(o,'Shape') or o.Shape.isNull() or o.Name.startswith(('Ola_','Battery_crossarm_','Battery_edgepost_')) or o.Name in ['Battery_tray_shared','Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits'] or 'bracket_space' in o.Name:continue
 targets.append((o.Name,o.Shape))
for gn in ['USED_FASTENERS_nominal_fit','NEW_CLAMP_HARDWARE_NEEDED_UNCONFIRMED','NEW_CSUNK_STANDARD_STEEL_PROPOSED','OCCUPIED_PROFILE_PLUS_OUTER04_MARGIN','PI_INTERNAL_M2p5x8_FULL_STANDARD_SETS','PRINT_PARTS_world_assembly']:
 g=D.getObject(gn)
 if g:targets.extend((o.Name,o.Shape) for o in g.Group if hasattr(o,'Shape') and hasattr(o.ViewObject,'ShapeColor'))
targets=list(dict(targets).items())
for o in D.getObject('CAPTURE_CONSTRUCTION_OPERANDS_NOT_EXTRA_PARTS').Group:
 s=o.Shape
 if 'FRONT_RECEIVER' in o.Name:s=s.cut(Part.makeCylinder(1.65,12,V(-106,-35,70),V(1,0,0)))
 for n,q in targets:check(o.Name,s,n,q,1.25)
 for n in ['P10_front_gate','P11_rear_gate','P12_common_deck_speaker']:
  if 'FRONT_RECEIVER' in o.Name and n=='P10_front_gate':continue
  check(o.Name,s,n,D.getObject(n).Shape,0 if 'FRONT_RECEIVER' in o.Name and n=='P12_common_deck_speaker' else 1.25)
 for st in D.Objects:
  if st.Name.startswith(('STRAP0_','STRAP1_')) and hasattr(st,'Shape'):check(o.Name,s,st.Name,st.Shape,0) # actualmodeledlinkedfixture, noforeignwaiver.
# Resolveallknownrear sourceconstraints together, notiteratorreplay.
for n in ['S0_body','H03_panel_M3x55_1','P05_spacer_instance2']:
 check('COMPLETE_NEW_P19',D.getObject('P19_shared_lower_carrier').Shape,n,D.getObject(n).Shape)
# NewP10receivingear withWHOLEunchangedfrontsteel andfrontframe facebearing.
for o in D.getObject('CARRIER_TWO_COMPLETE_M3_NEEDED_UNCONFIRMED').Group:
 if o.Name.startswith('CARRIER_front_'):check(o.Name,o.Shape,'P10_REAL_FRONT_RECEIVER',D.getObject('P10_front_gate').Shape,0)
r['actual_front_headwasher_gap']=D.getObject('CARRIER_front_headwasher').Shape.distToShape(D.getObject('P10_front_gate').Shape)[0]
# Newanchorpositive cannotinterferepreviouslyclear driver/negativeXnutfeed: exactnewdelta/ownonly.
tool=Part.makeCylinder(4.25,2.4,V(76,30,81.62)).fuse(Part.makeBox(21,8.5,2.4,V(55,25.75,81.62)))
for o in D.getObject('CAPTURE_CONSTRUCTION_OPERANDS_NOT_EXTRA_PARTS').Group:check('NUT_TOOL',tool,o.Name,o.Shape,0)
# Actualcell+6unchangedstockfields vsP12 alongpositiveZapproach usingactualmaterialXYcolumns.
p12=D.getObject('P12_common_deck_speaker').Shape;r['closure_columns']=[]
for n in ['Battery_GEA223S30X6GT']+[o.Name for o in D.Objects if o.Name.startswith(('STRAP0_','STRAP1_')) and hasattr(o,'Shape')]:
 s=D.getObject(n).Shape;b=s.BoundBox;c=p12.common(Part.makeBox(b.XLength,b.YLength,250,V(b.XMin,b.YMin,-20)));empty=c.isNull() or c.Volume<1e-5;gap=None if empty else c.BoundBox.ZMin-b.ZMax;row=dict(part=n,valid=c.isValid(),emptyXYcolumn=empty,minP12Z=None if empty else c.BoundBox.ZMin,partZmax=b.ZMax,gap=gap,continuous_positiveZ_clear=empty or gap>=(1.25 if n.startswith('Battery') else 0)-1e-6);r['closure_columns'].append(row)
 if not row['continuous_positiveZ_clear']:r['failures'].append(dict(assembly='P12_POSITIVE_Z_APPROACH_COLUMN_INCONCLUSIVE_NOT_COLLISION',**row))
r['seconds']=time.perf_counter()-T;r['status']='CHANGED_CAPTURE_GEOMETRY_AND_KNOWN_COMPLETE_CONSTRAINTS_CLEAR_SCOPED' if not r['failures'] else 'CAPTURE_BOUNDED_FAILURES_NO_GEOMETRY_RETRY';(P/'capture-changed-gate.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(dict(status=r['status'],bounds=r['bounds'],checks=len(r['checks']),failures=r['failures'],headwasher=r['actual_front_headwasher_gap'],closure=r['closure_columns'],seconds=r['seconds'])))
