import FreeCAD as A,Part,json,math,time
from pathlib import Path
D=A.getDocument('DAY15_CARRIER_CONTOUR');P=Path(D.FileName).parent.parent/'day15-carrier-capture-first-fit';P.mkdir(exist_ok=True);V=A.Vector;T=time.perf_counter();base=Path(D.FileName).parent
old=json.loads((base/'missing-whole-carrier-gate.json').read_bytes());received={(x['a'],x['b']) for x in old['checks'] if x['gap']>=x['required']-1e-6 or (x['required']==0 and (x.get('common') or 0)<1e-5)}
r=dict(status='FINITE_MISSING_SCREEN_BEFORE_NEW_GEOMETRY',utc=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),received33_exact_not_replayed=len(received),bounds=0,checks=[],blocks=[],tool_phase=[],source_diagnostics=[],elapsed=None)
def lo(s,q):
 a=s.BoundBox;b=q.BoundBox;return math.sqrt(sum(max(0,getattr(a,t+'Min')-getattr(b,t+'Max'),getattr(b,t+'Min')-getattr(a,t+'Max'))**2 for t in 'XYZ'))
def check(a,s,b,q,lim=1.25,phase=None):
 if lo(s,q)>lim+1e-5:r['bounds']+=1;return
 gap=s.distToShape(q)[0];c=s.common(q) if gap<1e-6 or lim==0 else None;row=dict(a=a,b=b,gap=gap,required=lim,common=None if c is None else c.Volume,valid=True if c is None else c.isValid());r['checks'].append(row)
 ok=(c.isValid() and c.Volume<1e-5) if lim==0 else gap>=lim-1e-6
 if not ok:
  if phase:row['phase']=phase;r['tool_phase'].append(row)
  else:r['blocks'].append(row)
targets=[]
for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
 if not hasattr(o,'Shape') or o.Shape.isNull() or o.Name.startswith(('Ola_','Battery_crossarm_','Battery_edgepost_')) or o.Name in ['Battery_tray_shared','Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits'] or 'bracket_space' in o.Name:continue
 targets.append((o.Name,o.Shape))
for gn in ['USED_FASTENERS_nominal_fit','NEW_CLAMP_HARDWARE_NEEDED_UNCONFIRMED','NEW_CSUNK_STANDARD_STEEL_PROPOSED','OCCUPIED_PROFILE_PLUS_OUTER04_MARGIN','PI_INTERNAL_M2p5x8_FULL_STANDARD_SETS','PRINT_PARTS_world_assembly']:
 g=D.getObject(gn)
 if g:targets.extend((o.Name,o.Shape) for o in g.Group if hasattr(o,'Shape') and hasattr(o.ViewObject,'ShapeColor'))
targets=list(dict(targets).items())
carrier=D.getObject('P19_shared_lower_carrier').Shape
for n,q in targets:
 if ('COMPLETE_P19',n) in received or n=='S0_body':continue
 if n.startswith(('P01','P02','P03')):lim=0 # Receivedactualdeck/feetfixture nonpenetration; no foreigncasewaiver.
 else:lim=0 if n=='Battery_GEA223S30X6GT' or n.startswith('Leg_protected_MTA0100335_') else 1.25
 check('COMPLETE_P19',carrier,n,q,lim)
for o in D.Objects:
 if not o.Name.startswith(('STRAP0_','STRAP1_')) or not hasattr(o,'Shape'):continue
 for n,q in targets:check(o.Name,o.Shape,n,q,0 if n=='Battery_GEA223S30X6GT' else 1.25)
# Complete driver/spanner sourceair fields. MAIN/latepanels mayphase-share only asnamedinitialorder.
driver=Part.makeCylinder(4.25,70,V(76,30,92.52));spanner=Part.makeCylinder(4.25,2.4,V(76,30,81.62)).fuse(Part.makeBox(21,8.5,2.4,V(55,25.75,81.62)))
for tag,s in [('HEX2_R4p25',driver),('NUT_TOOL_R4p25_FROM_NEGX',spanner)]:
 for n,q in targets:check(tag,s,n,q,1.25,phase='BEFORE THIS MODULE/BANK/PANEL only if actualdiscreteinitialassembly; nooperatingclearanceclaim')
 for n in ['P10_front_gate','P11_rear_gate','P12_common_deck_speaker','P19_shared_lower_carrier']:
  check(tag,s,n,D.getObject(n).Shape,0,phase='OWNPRINT_TOOLACCESS_mustcommon0_notlabelwaiver')
gap=D.getObject('CARRIER_front_headwasher').Shape.distToShape(D.getObject('P10_front_gate').Shape)[0]
r['source_diagnostics'].append(dict(interface='OLD_FRONT_HEADWASHER_TO_P10',actual_gap=gap,interpretation='Ifnonzero thisoldUNBUILTdemandcannotbecreditedasframeclamp; newdirectkeyedjoint+4feetmustcarrycompletefunction, keeporretireexplicitly NOT purchasedpartdelete.'))
# ActualP12material projected overcell: continuouspositiveZclosingbound, not endpointonly.
p12=D.getObject('P12_common_deck_speaker').Shape;c=p12.common(Part.makeBox(106.5,35,250,V(-2,-17.5,-20)))
r['source_diagnostics'].append(dict(interface='P12_OVER_ACTUAL_CELL_XY_COLUMN',valid=c.isValid(),volume=c.Volume,minZ=None if c.isNull() or c.Volume<1e-5 else c.BoundBox.ZMin,celltop86p5=True,interpretation='ForP12atallhigherZ, thisactualcolumnbound provescellclearonly if minZ>=87.75. Otherkitclosurestillseparate.'))
r['elapsed']=time.perf_counter()-T;r['status']='FINITE_SCREEN_RECEIVED_NO_NEW_GEOMETRY';(P/'finite-missing-screen.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps(dict(status=r['status'],bounds=r['bounds'],exact=len(r['checks']),blocks=r['blocks'],tool_phase=r['tool_phase'],diagnostics=r['source_diagnostics'],seconds=r['elapsed'])))
