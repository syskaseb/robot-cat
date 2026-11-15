import FreeCAD as A,FreeCADGui as G,Part,MeshPart,json,math
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-mta-panel-fit')
def bb(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def run():
 S=next(d for d in A.listDocuments().values() if d.FileName.replace('\\','/').endswith('/day15-carrier-capture-first-fit/carrier-capture.FCStd'))
 unit=S.getObject('Motor_ATO4A__1_0').Shape;housing=unit.Solids[0];h=housing.BoundBox
 assert len(unit.Solids)==4 and len(housing.Faces)==6 and abs(h.ZLength-28.5)<1e-5
 # FIRST frozen source-derived assembly hypothesis; all CAD detail follows this.
 plan=dict(utc=datetime.now(timezone.utc).isoformat(),scope='ONE FREE BENCH MTA0300330 panel-interface coupon; not a bank mount/root or new installed layout',source_native=S.FileName,source_carrier_commit='4f9ce00a634651811c109ed245f917846b59c957',actual_source='Motor_ATO4A__1_0, builder factors Housing/ATO/IN/OUT; four source solids are dimensional boxes, not detailed delivered shapes',source_housing_bounds=bb(housing),source_housing_faces=6,primary='MTA B0-100.E10A ONLY FOR REFERENCE, 0300330.pdf SHAeb12686beb22918b9b48fed3bf7806d3d0eac2a28a807880fb45a66f500206fc',nominal_flange=[28,15,2],body_total_height_from_flange_top=28.5,nominal_shank_crosssection=[21.7,11],reference_panel_d=2,window_a=22.2,window_b=11.3,b_tolerance=[0,.3],coupon_manufacturing_clearance='No hidden added clearance. Print22.2x11.3 nominal; measure actual opening/clip/stock before asserting fit.',flange_plane_binding=dict(source_allocation_top=h.ZMax,primary_reference_flange_underside=h.ZMax-2,panel_top=h.ZMax-2,panel_bottom=h.ZMax-4,not_actual_flange_geometry=True,manufactured_pose_binding='FIT physical part, not source six-face box proof'),initial_sequence=['Keep both already-crimped complete femaleTE4-520448-2 andTE2-520184-2 leads intact and outside housing during INITIAL mounting, not virtual unplug of a completed factory module','Push MTA0300330 with its two supplied internal contacts through panel from flange side; no internal contact depinning. Check both springclips from open underside','After housing latched, mate whole TE female ends onto the two MTA tabs from fully open underside. Currente=0sourcebox is not measured insertion depth. Preserve actual IN/OUT mapping and full wire ends','Install complete ATO4A from top last. On free bench coupon, no surroundingbank/frame blocks releaseclip/terminal access. Real delivered mating/insulator interference/stock and latch force are physicalFIT','If actual prewiredunit cannot be assembled this way, stop with measurement dependency. Do not force whole rigid assembledunit through window or invent second split family'],source_order_basis='Local primary-pinned README/ENVELOPE: MTA0300330 includes internal contacts; both selectedTE are separate fully insulated FEMALE6.35x0.81 slip-on ends. Initial external mating after panel does not cut wire or unplug solderedE1.',installed_bank_root=False,fullunit_geometry_or_reach_pass=False,no_new_hardware=True,physical_pass=False,actual_fit_cut_slack=None)
 (P/'source-interface-and-initial-order.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
 D=A.newDocument('DAY15_MTA_PANEL_TRIAL');groups={}
 for o in S.Objects:
  if o.TypeId=='App::DocumentObjectGroup':groups[o.Name]=D.addObject('App::DocumentObjectGroup',o.Name)
 for o in S.Objects:
  if not hasattr(o,'Shape') or not hasattr(o.ViewObject,'ShapeColor') or o.Name.startswith('COUPON_'):continue
  q=D.addObject('PartDesign::Feature',o.Name);q.Shape=o.Shape.copy();q.Label=o.Label;q.ViewObject.ShapeColor=o.ViewObject.ShapeColor;q.ViewObject.Transparency=o.ViewObject.Transparency;q.ViewObject.Visibility=o.ViewObject.Visibility
  for g in S.Objects:
   if g.TypeId=='App::DocumentObjectGroup' and o in g.Group:groups[g.Name].addObject(q)
 gr=D.addObject('App::DocumentObjectGroup','ONE_BENCH_COUPON_AND_DUPLICATED_UNIT_DISPLAY_REFERENCE_NOT_EXTRA_BOM')
 def add(n,s,color=(.65,.65,.7),show=True):
  o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=color;o.ViewObject.Visibility=show;gr.addObject(o);return o
 # Display-only proper rigid mapping: currentY(long)->bench-X; currentX(short)->bench+Y.
 # Same source four whole parts, no shrink/reorientation of their relative assembly.
 cx=(h.XMin+h.XMax)/2;cy=(h.YMin+h.YMax)/2;dz=104-h.ZMax
 transform=A.Placement(V(225+cy,-cx,dz),A.Rotation(V(0,0,1),90))
 r=dict(primary_reference_geometry_not_delivery=True,source_unit_bounds=bb(unit),source_member_rows=[],display_transform=dict(Q=list(transform.Rotation.Q),translation=list(transform.Base)),nominal_panel_world=[203,-15,100,247,15,102],springclip_geometry_not_in_CAD=True)
 for i,(role,col) in enumerate([('HOUSING_ALLOCATED_NOT_EXACT_FLANGE',(.22,.3,.34)),('ATO4A_complete',(.65,.25,.15)),('TE_IN_4_520448_2_full',(.9,.7,.1)),('TE_OUT_2_520184_2_full',(.7,.2,.2))]):
  s=unit.Solids[i].copy();s.Placement=transform.multiply(s.Placement);o=add('BENCH_REFERENCE_'+role,s,col);o.ViewObject.Transparency=65 if i==0 else 0
  r['source_member_rows'].append(dict(role=role,source_bounds=bb(unit.Solids[i]),display_bounds=bb(s),source_volume=unit.Solids[i].Volume,display_volume=s.Volume,valid=s.isValid(),clone_not_additional_BOM=True))
 # FIRST actual whole source context/planes are persisted BEFORE printable geometry.
 (P/'whole-unit-datums-before-coupon.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 D.Label='DAY15 MTA / WHOLE UNIT + SOURCE PLAN BEFORE COUPON';D.recompute();D.saveAs(str(P/'mta-panel-trial.FCStd'))
 outer=Part.makeBox(44,30,2,V(203,-15,100));window=Part.makeBox(22.2,11.3,4,V(225-11.1,-5.65,99));coupon=outer.cut(window)
 assert coupon.isValid() and len(coupon.Solids)==1
 add('COUPON_MTA_PANEL2mm_REFERENCE_WINDOW',coupon,(.24,.65,.75))
 # Primary flange rectangles are wireframe datums ONLY: not invented purchased solids/clip shapes.
 for z,n in [(104,'NOMINAL_FLANGE_TOP_NOT_SOURCE_SOLID'),(102,'NOMINAL_FLANGE_UNDERSIDE_PANEL_BEARING')]:
  vs=[V(211,-7.5,z),V(239,-7.5,z),V(239,7.5,z),V(211,7.5,z)];o=add(n,Part.makePolygon(vs+[vs[0]]),(.8,.2,.7));o.ViewObject.LineWidth=3
 # Fullsource AUX is carried only as explicit OPEN occupied scope, not a newly accepted mount.
 aux=D.getObject('AUX_Pololu4092');b=aux.Shape.BoundBox;o=add('AUX_FULL9p5_OCCUPIED_CONTEXT_OPEN',Part.makeBox(25.4,25.4,9.5,V(b.XMin,b.YMin,b.ZMin-1.8)),(.95,.6,.2),False);o.Label='OPEN currentAUX fullpopulation, not PCB-only approval'
 D.recompute();D.save() # checkpoint BEFORE local geometry reads/export.
 r['nominal_bearing']=dict(flange_area=28*15,window_area=22.2*11.3,nominal_continuous_land_area=28*15-22.2*11.3,long_end_lands_each=(28-22.2)/2,short_side_lands_each=(15-11.3)/2,not_actual_contact_or_clampforce=True)
 r['nominal_shank_window_clearance']=dict(long_total=22.2-21.7,short_total=11.3-11,clip_compression_and_spring_free_state_unknown=True,source_bodybox_not_shank=True)
 r['depth_below_panel_bottom']=28.5-2-2
 r['whole_rigid_TE_projection']=dict(short_projected_size=unit.BoundBox.XLength,window_short=11.3,rigid_straight_fullymated_drop_in_NOTqualified=True,not_all_manual_paths_impossible=True)
 r['individual_TE_nominal_projections']=[dict(role=t,across_window_long=unit.Solids[i].BoundBox.YLength,across_window_short=unit.Solids[i].BoundBox.XLength,not_measured_mouth_or_matingdepth=True) for i,t in [(2,'IN'),(3,'OUT')]]
 for i,t in [(2,'IN'),(3,'OUT')]:assert unit.Solids[i].BoundBox.XLength<11.3 and unit.Solids[i].BoundBox.YLength<22.2
 # Explicit guard against treating coarse box as physical flange/shank.
 c=D.getObject('BENCH_REFERENCE_HOUSING_ALLOCATED_NOT_EXACT_FLANGE').Shape.common(coupon)
 r['full_housing_allocation_box_common_panel']=dict(volume=c.Volume,valid=c.isValid(),meaning='Expected whole-box cover overlap, NOT purchased-plastic collision or panel-fit verdict; source lacks actual flange/clip geometry.')
 local=coupon.copy();local.translate(V(-203,15,-100));mesh=MeshPart.meshFromShape(Shape=local,LinearDeflection=.05,AngularDeflection=.2,Relative=False);assert mesh.isSolid() and mesh.Volume>0 and abs(local.BoundBox.ZMin)<1e-6
 mesh.write(str(P/'MTA0300330_PANEL2_REFERENCE_COUPON.stl'));coupon.exportBrep(str(P/'MTA0300330_PANEL2_REFERENCE_COUPON_world.brep'))
 r['coupon']=dict(qty=1,closed_positive=True,mesh_volume=mesh.Volume,localXYZ=[44,30,2],Zmin=0,window=[22.2,11.3],panel2=True,release='CONDITIONAL_FREE_BENCH_SOURCE_INTERFACE_TRIAL_NOT_INSTALLED_BANK',additional_fasteners=0)
 r['physical_pass']=False;r['whole_kit_ready']=False;r['actual_fit_cut_slack']=None
 # Actual source section for datum proof; coarse housing clearly labelled as allocation.
 vs=[V(225,-18,45),V(225,18,45),V(225,18,128),V(225,-18,128)];plane=Part.Face(Part.makePolygon(vs+[vs[0]]));lines=[]
 for n in ['COUPON_MTA_PANEL2mm_REFERENCE_WINDOW','BENCH_REFERENCE_HOUSING_ALLOCATED_NOT_EXACT_FLANGE','BENCH_REFERENCE_ATO4A_complete','BENCH_REFERENCE_TE_IN_4_520448_2_full','BENCH_REFERENCE_TE_OUT_2_520184_2_full']:
  s=D.getObject(n).Shape;sec=s.section(plane);lines.append(dict(name=n,curves=[[[v.y,v.z] for v in e.discretize(Deflection=.03)] for e in sec.Edges]))
 (P/'actual-unit-panel-section.json').write_text(json.dumps(lines)+'\n',encoding='utf-8')
 (P/'coupon-and-whole-unit-result.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
 for o in D.Objects:
  if not hasattr(o.ViewObject,'ShapeColor'):continue
  if o.Name.startswith(('FEED_','KEY_','CAPTURE_','DIRECT_','P12_FULL_OD6','P12_UNCHANGED_R24')) or 'section' in o.Name.lower():o.ViewObject.Visibility=False
 D.Label='DAY15 MTA PANEL / ONE BENCH COUPON / NO INSTALLED BANK PASS';D.recompute();D.save();A.setActiveDocument(D.Name)
 print(json.dumps(dict(status='ONE_MTA_SOURCE_INTERFACE_COUPON_AND_LEGITIMATE_INITIAL_MATING_PLAN_SAVED',objects=len(D.Objects),coupon=r['coupon'],nominal_bearing=r['nominal_bearing'],source_box=c.Volume,rigid_projection=r['whole_rigid_TE_projection'])))
run()
