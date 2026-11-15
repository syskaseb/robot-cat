import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-powerboard-common-shoe')
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def cyl(x,y,z,r,h):return Part.makeCylinder(r,h,V(x,y,z))
def hexagon(x,y,z,af,h):
 r=af/math.sqrt(3);vs=[V(x+r*math.cos(i*math.pi/3),y+r*math.sin(i*math.pi/3),z) for i in range(6)]
 return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,h))
def bb(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def lower(a,b):
 a=a.BoundBox;b=b.BoundBox;return math.sqrt(sum(max(0,getattr(a,t+'Min')-getattr(b,t+'Max'),getattr(b,t+'Min')-getattr(a,t+'Max'))**2 for t in 'XYZ'))
def run():
 T=time.perf_counter();S=A.getDocument('DAY15_CARRIER_CAPTURE')
 plan=dict(utc=datetime.now(timezone.utc).isoformat(),source_native=S.FileName,source_commit='4f9ce00a634651811c109ed245f917846b59c957',hypothesis='ONE removable open common M2 powerboard shoe, on actual P12 and P11 ledges; full module population + ports + two complete frame joints',PCB_bottom=103.52,old_bottom=94,own_project_pose_change=9.52,base=[55,20,92.52,126,49,97.52],post_height=6,source_MAIN_frame='STEP local x->world -Y, y->world +X, z->world +Z; origin(61,44.86,103.52), project in-plane orientation explicit; old source was bounding-box allocation not actual STEP',source_AUX_frame='Existing 180deg XY PCB orientation retained; holes DXF inches exact 2.159/21.082 within drawing rounding/tolerance',admissible_conservative_PCB_interval=[100.57,107.0752],interval_basis='After shoe top97.52, underside1.8+foreign1.25 gives100.57; conservative S1 bottom116 minus MAIN7.6748 minus1.25 gives107.0752 when XY-adjacent. Selected103.52 inside; actual finite geometry still required.',MAIN_localPCB=[0,0,0,22.86,30.48,1.5748],AUX_PCB_thickness=1.57,AUX_below=1.8,AUX_above=6.1,AUX_full_occupied_height=9.47,source_rounded_height=9.5,AUX_components_envelope_not_solid_case=True,frame_axes=[[57,34],[118,35]],frame_joint='2 full ISO10642 M3x14 incl head + lower washerOD7x0.5 + fullnutAF5.5x2.4, demandUNCONFIRMED; two printed bores only, no bought drill',board_joint='5 full M2x12 socket headsD3.8h2 + upper washerOD5x0.3 + nutAF4h1.6 in actual sidefeed; source mountØ2.18, notM2.5',safe_hole_annulus_components_FIT3=True,changed_interfaces=['MAIN9.52Z+realSTEPframe replacing old allocatedbox','AUX9.52Z+primary full population; PCBdatum not bbox resize','P11/P12 two print bores at actual frame contact','two frame screws before boards, M2 sidefeeds before mountedshoe','all MAIN/AUX solder/wire end heights and reach FIT2, no cut or old slack credit'],retained='All other boards, battery, carrier/root/stock/audio/Pi/57+extras/sourceframe unchanged',assembly=['Insert full M2 nuts from actual nearest open Yedge into shoe on bench','Fasten common shoe to actual P12/P11 using fullM3 lower nut/washer before boards/banks/MAIN','Preterminate actual MAIN/AUX outsidePETG; lower boards onto five hole-zone posts, fasten M2 through actual mounting holes','Lay actual solder/ports in open ends; adjust only after unpowered fit; install latepanels after driver/trimmer access'],scope='CONDITIONAL_UNPOWERED_BOARD_MOUNT_TRIAL not complete module kit',physical_pass=False,actual_fit_cut_slack=None)
 (P/'whole-module-premise.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
 D=A.newDocument('DAY15_POWERBOARD_SHOE');groups={}
 for o in S.Objects:
  if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
 for o in S.Objects:
  if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor') or o.Name.startswith('COUPON_'):continue
  q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape.copy();q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
  for g in S.Objects:
   if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
 gr=D.addObject('App::DocumentObjectGroup','POWER_SHOE_CURRENT_PRINT_HARDWARE_AND_SCOPED_FIELDS')
 def add(n,s,color=(.7,.72,.76),show=True):
  o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=color;o.ViewObject.Visibility=show;gr.addObject(o);return o
 z=103.52
 main=Part.read('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/reference/main-p0-2026-09-24/reg32c.step');main.Placement=A.Placement(V(61,44.86,z),A.Rotation(V(0,0,1),-90)).multiply(main.Placement)
 oldmain=D.getObject('MAIN_Pololu4853').Shape.copy();oldmain.translate(V(0,0,9.52));D.getObject('MAIN_Pololu4853').Shape=main
 mc=add('MAIN_FULL_FAMILY_UNSHRUNK_CONSERVATIVE_SCOPE',oldmain,(.8,.45,.2),False)
 aux=D.getObject('AUX_Pololu4092').Shape.copy();aux.translate(V(0,0,9.52));D.getObject('AUX_Pololu4092').Shape=aux
 # Primary 1.57 PCB representation; actual holes retained in same source XY.
 aux=aux.common(box(98,21,z,28,28,1.57));D.getObject('AUX_Pololu4092').Shape=aux
 ac=add('AUX_FULL_POPULATED_OCCUPIED_NOT_PLASTICCASE',box(99,22,z-1.8,25.4,25.4,9.47),(.9,.58,.2));ac.ViewObject.Transparency=65
 mh=[(63.159,24.159),(63.159,42.701)];ah=[(122.241,45.241),(101.159,45.241),(122.241,24.159)];holes=mh+ah
 base=box(55,20,92.52,71,29,5);shoe=base.copy();members=[('base',base)];feeds=[];steel=[];tools=[]
 for i,(x,y) in enumerate(holes):
  post=cyl(x,y,97.02,1.9,6.5);shoe=shoe.fuse(post);members.append(('post'+str(i),post))
  pocket=hexagon(x,y,94.42,4.3,1.8)
  ya=19.5 if y<34 else y;yb=y if y<34 else 49.5
  feed=box(x-2.45,ya,94.42,4.9,yb-ya,1.8);shoe=shoe.cut(pocket.fuse(feed)).cut(cyl(x,y,92,1.2,13))
  # Full standard steel dimensions, no head or tip truncation.
  top=z+(1.5748 if i<2 else 1.57);under=top+.3
  screw=cyl(x,y,under-12,1,12).fuse(cyl(x,y,under,1.9,2))
  washer=cyl(x,y,top,2.5,.3).cut(cyl(x,y,top,1.1,.3))
  nut=hexagon(x,y,94.52,4,1.6).cut(cyl(x,y,94.5,1.025,1.7))
  for role,s in [('M2x12_full',screw),('upperwasher',washer),('fullnut',nut)]:steel.append((f'PB{i}_{role}',s));add(f'PB{i}_{role}',s)
  # Full nut swept to open Y edge before module/shoe installation.
  travel=abs((19.5 if y<34 else 49.5)-y);q=hexagon(x,y,94.52,4,1.6)
  # Convex prismatic cover contains full hex at all intermediate Y positions.
  sweep=box(x-4/math.sqrt(3),min(y-2,19.5-2) if y<34 else y-2,94.52,8/math.sqrt(3),travel+4,1.6)
  feeds.append((f'PB{i}_full_nut_continuous_Yfeed',sweep))
  tools.append((f'PB{i}_driver_beforelateclosure',cyl(x,y,under+2,2.2,35)))
 frame=[];frameholes=[]
 for i,(x,y) in enumerate([(57,34),(118,35)]):
  # Complete 90deg ISO10642 nominalmax headD6.72; length14 INCLUDES head.
  head=Part.makeCone(1.5,3.36,1.86,V(x,y,95.66));screw=cyl(x,y,83.52,1.5,12.14).fuse(head)
  washer=cyl(x,y,88.02,3.5,.5).cut(cyl(x,y,88.02,1.6,.5));nut=hexagon(x,y,85.62,5.5,2.4).cut(cyl(x,y,85.6,1.525,2.5))
  clearance=cyl(x,y,83,1.7,15).fuse(Part.makeCone(1.7,3.56,1.86,V(x,y,95.66)))
  shoe=shoe.cut(clearance)
  owner='P12_common_deck_speaker' if i==0 else 'P11_rear_gate';old=D.getObject(owner).Shape.copy();D.getObject(owner).Shape=old.cut(cyl(x,y,83,1.7,15));frameholes.append(dict(owner=owner,axis=[x,y],contact_footprint_actual_volume=old.common(cyl(x,y,88.52,3.5,4)).Volume,removed=old.cut(D.getObject(owner).Shape).Volume))
  for role,s in [('ISO10642_M3x14_full',screw),('lowerwasher',washer),('fullnut',nut)]:frame.append((f'SHOE_FRAME{i}_{role}',s));add(f'SHOE_FRAME{i}_{role}',s)
  tools.append((f'FRAME{i}_HEX2_beforeboards',cyl(x,y,97.52,4.25,40)))
 assert shoe.isValid() and len(shoe.Solids)==1
 add('P20_COMMON_MAIN_AUX_M2_SHOE',shoe,(.22,.55,.68))
 ports=[('MAIN_WIRE_TERMINATION_ALLOWANCE_FIT2',box(59.5,23,105.0948,11,20.7,8)),('AUX_WIRE_TERMINATION_ALLOWANCE_FIT2',box(103.5,40.5,105.09,16,8.9,8))]
 for n,s in ports:o=add(n,s,(.4,.8,.8),False)
 D.recompute();D.Label='DAY15 COMMON POWER SHOE / SAVED BEFORE GATES';D.saveAs(str(P/'powerboard-shoe.FCStd'))
 # Finite CURRENT near-pass only. No old carrier, frame, Pi or audio matrices.
 r=dict(status='FINITE_CHANGED_MODULE_LAYER_AND_COMPLETE_HARDWARE',checks=[],failures=[],bounds=0,frame_roots=frameholes,primary_holes_MAIN=mh,primary_holes_AUX=ah,PCB_bottom=z,source_main_valid=main.isValid(),nut_feeds=[],own_material=[],physical_hole_annulus_FIT3=True)
 def ck(a,s,b,q,lim=1.25,phase=None):
  if lower(s,q)>lim+1e-6:r['bounds']+=1;return
  gap=s.distToShape(q)[0];c=s.common(q) if gap<1e-6 or lim==0 else None;ok=(c.isValid() and c.Volume<1e-5) if lim==0 else gap>=lim-1e-6
  row=dict(a=a,b=b,gap=gap,required=lim,common=None if c is None else c.Volume,valid=True if c is None else c.isValid(),phase=phase,clear=ok);r['checks'].append(row)
  if not ok and not phase:r['failures'].append(row)
 targets=[]
 for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
  if not hasattr(o,'Shape') or not hasattr(o,'Placement') or o.Shape.isNull() or o.Name.startswith(('Ola_','Battery_crossarm_','Battery_edgepost_')) or o.Name in ['MAIN_Pololu4853','AUX_Pololu4092','Battery_tray_shared','Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits'] or 'bracket_space' in o.Name:continue
  targets.append((o.Name,o.Shape))
 for gn in ['USED_FASTENERS_nominal_fit','NEW_CLAMP_HARDWARE_NEEDED_UNCONFIRMED','NEW_CSUNK_STANDARD_STEEL_PROPOSED','PRINT_PARTS_world_assembly','PI_INTERNAL_M2p5x8_FULL_STANDARD_SETS']:
  g=D.getObject(gn)
  if g:targets.extend((o.Name,o.Shape) for o in g.Group if hasattr(o,'Shape') and hasattr(o.ViewObject,'ShapeColor'))
 targets=list(dict(targets).items())
 for n,s in [('SHOE',shoe),('MAIN_full_family',oldmain),('AUX_full_population',ac.Shape)]+steel+frame+ports:
  for m,q in targets:ck(n,s,m,q,0 if m in ['P11_rear_gate','P12_common_deck_speaker'] and (n=='SHOE' or n.startswith('SHOE_FRAME')) else 1.25)
 ck('MAIN_full',oldmain,'AUX_full',ac.Shape)
 for n,s in steel+frame:
  ck(n,s,'OWN_SHOE_actual_void',shoe,0)
 for n,s in feeds:
  c=s.common(shoe);r['nut_feeds'].append(dict(name=n,common=c.Volume,valid=c.isValid()));
  if not c.isValid() or c.Volume>1e-5:r['failures'].append(dict(name=n,reason='actualwhole nut feed not open',common=c.Volume))
 for n,s in tools:
  for m,q in targets:ck(n,s,m,q,1.25,phase='INITIAL_BEFORE_BOARDS_OR_LATE_PANELS_ONLY_IF_RECORDED')
 for n,s in members:
  intended=s.common(shoe);r['own_material'].append(dict(member=n,retained_volume=intended.Volume,valid=intended.isValid(),extent=bb(s)))
 # Actual source PCB holes checked independently; broad module covers not called plastic material.
 r['MAIN_fullsteel_actualcomponent_checks']=[]
 for n,s in steel[:6]:
  c=s.common(main);r['MAIN_fullsteel_actualcomponent_checks'].append(dict(name=n,common=c.Volume,valid=c.isValid()))
  if not c.isValid() or c.Volume>1e-5:r['failures'].append(dict(name=n,reason='MAIN full steel vs actual populated STEP',common=c.Volume))
 r['status']='SCOPED_NOMINAL_LAYER_CLEAR_CONDITIONAL_HOLE_ZONE_FIT' if not r['failures'] else 'WHOLE_LAYER_HOLD_NO_SECOND_FAMILY'
 r['seconds']=time.perf_counter()-T;(P/'finite-layer-and-joint-gate.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 # Save all operands and forensic result even on HOLD, normal return only.
 D.Label='DAY15 COMMON POWER SHOE / '+r['status'];D.save();print(json.dumps(dict(status=r['status'],bounds=r['bounds'],checks=len(r['checks']),failures=r['failures'],seconds=r['seconds'])))
run()
