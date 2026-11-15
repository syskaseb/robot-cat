import FreeCAD as A,FreeCADGui as G,Part,json,math,time,re
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-whole-rear-layer-proposal')
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cyl(x,y,z,r,h):return Part.makeCylinder(r,h,V(x,y,z))
def hx(x,y,z,af,h):
 r=af/math.sqrt(3);vs=[V(x+r*math.cos(i*math.pi/3),y+r*math.sin(i*math.pi/3),z) for i in range(6)];return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,h))
def lo(s,q):
 a=s.BoundBox;b=q.BoundBox;return sum(max(0,getattr(a,t+'Min')-getattr(b,t+'Max'),getattr(b,t+'Min')-getattr(a,t+'Max'))**2 for t in 'XYZ')**.5
def run():
 T=time.perf_counter();S=A.getDocument('DAY15_MTA_PANEL_TRIAL')
 read=json.loads((P/'available-layer-and-actual-root-read.json').read_bytes())
 rootread=[]
 for y in [35,49]:
  q=cyl(103,y,103,3.5,4);c=S.getObject('P11_rear_gate').Shape.common(q);rootread.append(dict(axis=[103,y],actual_volume=c.Volume,required=q.Volume,missing=q.cut(S.getObject('P11_rear_gate').Shape).Volume,valid=c.isValid()))
 assert all(x['missing']<1e-5 for x in rootread)
 plan=dict(utc=datetime.now(timezone.utc).isoformat(),status='ONE_WHOLE_FUNCTIONAL_STRATEGIC_PROPOSAL_BEFORE_GEOMETRY_NO_PRINTS',not_ce9_shoe_correction=True,load_topology='Existing P11 transverse top107 ->two ordinaryM3 spacers5 ->commonOPENmountplane112..115 ->ordinaryM2spacers4 ->manufacturer-hole PCBbottom119. Full accessible throughsets; no captive nut floor/pockets.',root_actual=rootread,root_zone_derivation='P11 beamX95..107/Y-86..86/Z103..107. North banks startY56; fullnutwasherR3.5+1.25 restrict secondaxisY<=51.25. Choose35/49, not prior preliminary74.5 read which would put lowerhardware in FHACYaw. Beam contacts actually measured before this ONE proposal.',allowed_PCB_Z=[118.3752,123.1752],height_basis=['M2x12 underhead+upperwasher+PCB: tip=PCBbottom-10.1252; above P11/P13 max107 +1.25 needsPCB>=118.3752','P14 lower134 minus1.25 minus1.5748+8 terminationallowance givesPCB<=123.1752','AUX monitor ceiling125 applies only overlappingXY. Actual north bayYmin>=45+1.25; P11 outerupright atY80 ->Ymin<=80-1.25-25.4=53.35'],AUX_north_Ymin_interval=[46.25,53.35],chosen_AUX_Ymin=47,PCB_bottom=119,plane=[112,115],ordinary_frame_spacer5=True,ordinary_PCB_spacer4=True,MAIN=dict(boundsXY=[61,22,91.48,44.86],source_STEP_frame='local x->+Y/y->-X/z->+Z, origin(91.48,22,119). Opposite toce9projectclock, not manufacturerworldpose.',ports='toward+X side, deliberate wholeboardorientation'),AUX=dict(boundsXY=[99,47,124.4,72.4],oldPCBdatum94=True,source_orientation180retained=True,fullfield=[99,47,117.2,124.4,72.4,126.7],ports='north Y67..74, clear of MonitorY20..45'),all_other_bought_poses_unchanged=True,P11_P13_functions_retained='Actual wholeP11 gate/rootjaws/crossbeams/upperrail bearing +P13 BUS31cooling/removablebridge remain geometrically identical. TWO future print boresØ3.4 in existing P11 beam are proposed interface contract only; no boughtframe drilling/cut.',support_parting='NEW open frame is one structural occupied-volume proposal, not a printable part. Separate from P11, real spacer contacts, two root axes antirotation. Manufacturing parting/seat tolerances intentionally not detailed.',complete_standard_sets=dict(boards='5M2x12socketD3.8h2 +2washersOD5t.3 each +fullM2nutAF4h1.6 +ordinaryspacerOD4L4',root='2ISO10642M3x16 LENGTHINCLUDESHEAD D6.72/h1.86 +lowerwasherOD7t.5 +fullnutAF5.5h2.4 +ordinaryspacerOD6L5'),hardware_demand='NEEDED_UNCONFIRMED, no purchase/inventory',print_contracts_NOT_acceptance=['Openplane3mm with5straightM2clearance passages; no captive pockets','2ordinary root CSheadbearing seat contracts in newplane and2P11printbores; wholehead envelopes modeled, no finished seat/part/STL','ActualsafePCBholeannulus/undersidecontact revision remains physicalcouponFIT3'],affected_interfaces=['MAIN all solder/voltagecontrol/powerends reoriented andZ+25','AUX all12solder/header positions movedY+25/Z+25 withfullunderside1.8; no freewire extension or old lengthcredit','New root wholetool before bank units/boards; P14/MIC/BUS latepanels retain assembly functions','Carrier/powerprotection/sourceclamps/57+extras/factoryplugs/four220/bothMTA unaffected; installedreach/slack/cutNULL'],assembly=['Loose currentframe/carrier assembly received4f9; P11 remains integral realprint, no virtualsplit','Fit newOPENplane ontwo5mmspacers; fullM3nut/washer fromunderside while all banks/boards absent, two people hold parts; no automatic nutcage','Preterminate wholeMAIN/AUX onbench; retain all oppositefactoryends/solderedE1kit; 4mmM2spacers+fullthroughsets, upper/lower washers andfullnuts accessible','Then latebank/monitor and P14/MIC/BUS closures; trimmer/tool slots accessible before closure. Service canpartialdemount, not rapidservice'],physical_pass=False,whole_kit_ready=False,actual_fit_cut_slack=None)
 (P/'whole-rear-layer-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
 D=A.newDocument('DAY15_WHOLE_REAR_LAYER');groups={}
 for o in S.Objects:
  if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
 for o in S.Objects:
  if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor') or o.Name.startswith(('COUPON_','BENCH_REFERENCE_','VIEW_ONLY_','NOMINAL_FLANGE_','AUX_FULL9p5_')):continue
  q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape.copy();q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
  for g in S.Objects:
   if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
 gr=D.addObject('App::DocumentObjectGroup','STRUCTURAL_PROPOSAL_ONLY_NO_PRINT_RELEASE')
 def add(n,s,c=(.72,.73,.77),show=True):
  o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=c;o.ViewObject.Visibility=show;gr.addObject(o);return o
 main=Part.read('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/reference/main-p0-2026-09-24/reg32c.step');main.Placement=A.Placement(V(91.48,22,119),A.Rotation(V(0,0,1),90)).multiply(main.Placement);D.getObject('MAIN_Pololu4853').Shape=main
 mc=box(61,22,119,30.48,22.86,7.6748);add('MAIN_UNSHRUNK_FAMILY_SCOPE',mc,(.7,.4,.2),False)
 aux=D.getObject('AUX_Pololu4092').Shape.copy();aux.translate(V(0,25,25));aux=aux.common(box(98,46,119,28,28,1.57));D.getObject('AUX_Pololu4092').Shape=aux
 ac=add('AUX_FULL9p5_POPULATED_SCOPE',box(99,47,117.2,25.4,25.4,9.5),(.95,.6,.18));ac.ViewObject.Transparency=65
 members=[('MAINopenrail',box(86.3,20.5,112,6,25,3)),('rootcrossbridge',box(86.3,32,112,20.7,6,3)),('rootspine',box(99,32,112,8,45.5,3)),('AUXlowercross',box(99,46.5,112,26,5.5,3)),('AUXouterrail',box(119.5,46.5,112,5.5,27,3)),('AUXuppercross',box(99,67.5,112,26,10,3))]
 mount=members[0][1]
 for n,s in members[1:]:mount=mount.fuse(s)
 add('PROPOSED_OPEN_MOUNT_PLANE_NOT_PRINT_PART',mount,(.3,.65,.7))
 holes=[(89.321,24.159),(89.321,42.701),(122.241,70.241),(101.159,70.241),(122.241,49.159)];steel=[];spacers=[];tools=[]
 for i,(x,y) in enumerate(holes):
  top=120.5748 if i<2 else 120.57;under=top+.3
  screw=cyl(x,y,under-12,1,12).fuse(cyl(x,y,under,1.9,2));uw=cyl(x,y,top,2.5,.3).cut(cyl(x,y,top,1.1,.3));lw=cyl(x,y,111.7,2.5,.3).cut(cyl(x,y,111.7,1.1,.3));nut=hx(x,y,110.1,4,1.6).cut(cyl(x,y,110.08,1.025,1.65));sp=cyl(x,y,115,2,4).cut(cyl(x,y,115,1.1,4))
  for tag,s in [('full_M2x12',screw),('upperwasher',uw),('lowerwasher',lw),('fullnut',nut)]:steel.append((f'OPEN_M2_{i}_{tag}',s));add(f'OPEN_M2_{i}_{tag}',s)
  spacers.append((f'OPEN_M2_{i}_ordinary_spacer4',sp));add(f'OPEN_M2_{i}_ordinary_spacer4',sp,(.55,.5,.8));tools.append((f'M2_{i}_driver_phase',cyl(x,y,under+2,2.2,25)))
 for i,y in enumerate([35,49]):
  x=103;sp=cyl(x,y,107,3,5).cut(cyl(x,y,107,1.6,5));spacers.append((f'ROOT_{i}_ordinary_spacer5',sp));add(f'ROOT_{i}_ordinary_spacer5',sp,(.55,.5,.8))
  screw=cyl(x,y,99,1.5,14.14).fuse(Part.makeCone(1.5,3.36,1.86,V(x,y,113.14)));wash=cyl(x,y,102.5,3.5,.5).cut(cyl(x,y,102.5,1.6,.5));nut=hx(x,y,100.1,5.5,2.4).cut(cyl(x,y,100.08,1.525,2.45))
  for tag,s in [('ISO10642M3x16_includeshead',screw),('lowerwasher',wash),('fullnut',nut)]:steel.append((f'OPEN_ROOT_{i}_{tag}',s));add(f'OPEN_ROOT_{i}_{tag}',s)
  tools.append((f'ROOT_{i}_HEX2_beforeboards',cyl(x,y,115,4.25,35)));tools.append((f'ROOT_{i}_nuttool_beforebanks',cyl(x,y,100.1,4.25,2.4).fuse(box(82,y-4.25,100.1,21,8.5,2.4))))
 ports=[('MAIN_all_terminal_field_FIT2',box(83,23,120.5748,11.5,21,8)),('AUX_all_terminal_field_FIT2',box(102,66,120.57,20,9,8))]
 for n,s in ports:o=add(n,s,(.9,.8,.25),False)
 D.Label='DAY15 WHOLE REAR LAYER / STRUCTURAL PROPOSAL ONLY';D.recompute();D.saveAs(str(P/'whole-rear-layer.FCStd'))
 r=dict(status='ONE_FINITE_COMPLETE_MODULE_AND_HARDWARE_FALSIFIER',bounds=0,checks=[],failures=[],tool_phase=[],own_print_realization_NOTclaimed=True,root=plan['root_actual'],all_unchanged_P11_P13_clamps_carrier_preserved=True)
 def ck(a,s,b,q,lim=1.25,phase=False):
  if lo(s,q)>lim+1e-6:r['bounds']+=1;return
  gap=s.distToShape(q)[0];c=s.common(q) if gap<1e-6 else None;row=dict(a=a,b=b,gap=gap,required=lim,common=None if c is None else c.Volume,valid=True if c is None else c.isValid(),clear=gap>=lim-1e-6)
  (r['tool_phase'] if phase else r['checks']).append(row)
  if not row['clear'] and not phase:r['failures'].append(row)
 targets=[]
 for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
  if not hasattr(o,'Shape') or not hasattr(o,'Placement') or o.Shape.isNull() or o.Name.startswith(('Ola_','Battery_crossarm_','Battery_edgepost_')) or o.Name in ['MAIN_Pololu4853','AUX_Pololu4092','Battery_tray_shared','Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits'] or 'bracket_space' in o.Name:continue
  targets.append((o.Name,o.Shape))
 for gn in ['USED_FASTENERS_nominal_fit','NEW_CLAMP_HARDWARE_NEEDED_UNCONFIRMED','NEW_CSUNK_STANDARD_STEEL_PROPOSED','PI_INTERNAL_M2p5x8_FULL_STANDARD_SETS']:
  g=D.getObject(gn)
  if g:targets.extend((o.Name,o.Shape) for o in g.Group if hasattr(o,'Shape') and hasattr(o.ViewObject,'ShapeColor'))
 targets.extend((o.Name,o.Shape) for o in D.Objects if re.match(r'^P(10|11|12|13|14|15|16|17|18|19)_',o.Name) and 'Shape' in o.PropertiesList and not re.match(r'^P12_(FULL|UNCHANGED|actual|ACTUAL)',o.Name))
 targets=list(dict(targets).items())
 for n,s in [('OPEN_MOUNT_PLANE',mount),('MAIN_family',mc),('AUX_full9p5',ac.Shape)]+steel+spacers+ports:
  for m,q in targets:
   # Root through P11 is a FUTURE printed-hole/bearing contract, not a passed common/Own exception.
   if m=='P11_rear_gate' and (n.startswith('OPEN_ROOT') or n.startswith('ROOT_')):continue
   ck(n,s,m,q)
 ck('MAINfamily',mc,'AUXfull',ac.Shape)
 for n,s in steel+spacers:
  if n.startswith(('OPEN_ROOT','ROOT_')):continue
  # Upper complete fasteners against opposite full module; own primary holezones requirephysicalannulus fit.
  idx=int(n.split('_')[2]);ck(n,s,'OTHER_MODULE',ac.Shape if idx<2 else mc)
 for n,s in tools:
  for m,q in targets:ck(n,s,m,q,phase=True)
 r['material_coverage']=[dict(member=n,missing=s.cut(mount).Volume,valid=s.cut(mount).isValid()) for n,s in members]
 r['connection_contracts']=dict(M2='Straight through holes2.4 in future plane, NO captive pockets; fullnuts freebelow. Plane is structural occupied volume, NOT own-clearance/printrelease.',root='Two future P11 printedbores3.4 and ordinary CShead seats in futureopenplane. Whole steel envelope present; actual P11root material read. No boughtdrill, no claim currentP11/STL modified. Netbeam section after3.4 bore proposed(12-3.4)*4=34.4mm2, notstrengthPASS.',spacer_contacts='Z107P11top->5spacer->112plane; plane115top->4spacer->119PCB. Fullusefulvolume contacts nominal, safePCBannulusFIT3.')
 r['status']='WHOLE_PROPOSAL_FOREIGN_SPACE_CLEAR_SCOPED_NOT_PRINT_OR_OWN_FIT_RELEASE' if not r['failures'] else 'WHOLE_PROPOSAL_HOLD_NO_SECOND_FAMILY'
 r['seconds']=time.perf_counter()-T;(P/'whole-module-space-and-hardware-falsifier.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 # Actual section evidence beforecostlyanyviews. No manufacturing print exported.
 rows=[]
 for z in [107,113,119,125.5]:
  for n in ['P11_rear_gate','P13_BUS_bridge','PROPOSED_OPEN_MOUNT_PLANE_NOT_PRINT_PART','MAIN_Pololu4853','AUX_FULL9p5_POPULATED_SCOPE','Monitor_MOD05015','S1_NKK_S821_installed']:
   s=D.getObject(n).Shape
   if s.BoundBox.ZMin>z+.001 or s.BoundBox.ZMax<z-.001:continue
   sec=s.section(Part.makePlane(90,72,V(48,15,z)));rows.append(dict(z=z,part=n,curves=[[[v.x,v.y] for v in e.discretize(Deflection=.05)] for e in sec.Edges]))
 (P/'actual-whole-layer-sections.json').write_text(json.dumps(rows)+'\n',encoding='utf-8');D.recompute();D.save();A.setActiveDocument(D.Name)
 print(json.dumps(dict(status=r['status'],objects=len(D.Objects),bounds=r['bounds'],checks=len(r['checks']),failures=r['failures'],tool_blocks=[x for x in r['tool_phase'] if not x['clear']],seconds=r['seconds'])))
run()
