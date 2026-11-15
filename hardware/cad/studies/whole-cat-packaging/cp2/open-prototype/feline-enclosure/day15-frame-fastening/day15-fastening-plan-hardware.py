import FreeCAD as A,FreeCADGui as G,Part,json,math,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;D=A.getDocument('DAY15_FRAME_FASTENING');P=Path(r'C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-frame-fastening');OLD=P.parent/'day15-essential-shared-frame';old=json.loads((OLD/'parting.json').read_bytes());T=time.perf_counter();CPU=time.process_time()
def point(p,a,t):return [p[i]+a[i]*t for i in range(3)]
def locate(s,p,a,t=0):s=s.copy();s.Placement=A.Placement(V(*point(p,a,t)),A.Rotation(V(0,0,1),V(*a)));return s
def hexshape(af,h):
 R=af/math.sqrt(3);pts=[V(R*math.cos(i*math.pi/3),R*math.sin(i*math.pi/3),0) for i in range(7)];return Part.Face(Part.Wire(Part.makePolygon(pts).Edges)).extrude(V(0,0,h))
grp=D.addObject('App::DocumentObjectGroup','NEW_CSUNK_STANDARD_STEEL_PROPOSED');rows=[]
for j in old['joints']:
 if j['role']!='complete_M3_joint':continue
 base=j['outer_bearing'];axis=j['axis'];tag=j['tag'];bus=tag.startswith('BUS_');upper='P14_' in tag or 'P15_' in tag;thick=8 if bus else 6;L=12 if bus else 10
 head=Part.makeCone(3.36,1.5,1.86);shaft=Part.makeCylinder(1.5,L-1.86,V(0,0,1.86));bolt=head.fuse(shaft).cut(hexshape(2,1.1));washer=Part.makeCylinder(3.5,.5).cut(Part.makeCylinder(1.65,.5));nut=hexshape(5.5,2.4).cut(Part.makeCylinder(1.5,2.4))
 names=[]
 for suffix,s,t in [('ISO10642_M3x'+str(L),bolt,0),('nutwasher',washer,thick),('fullnut',nut,thick+.5)]:
  n='CS_'+tag+'_'+suffix;o=D.addObject('PartDesign::Feature',n);o.Shape=locate(s,base,axis,t);grp.addObject(o);o.ViewObject.ShapeColor=(.65,.65,.67);o.ViewObject.Visibility=False;names.append(n);assert o.Shape.isValid()
 rows.append(dict(tag=tag,base=base,axis=axis,length_including_head_mm=L,printed_stack_mm=thick,head_nominal_diameter_mm=6.72,head_height_mm=1.86,head_angle_deg=90,hex_AF_mm=2,hex_depth_mm=1.1,head_bearing_part_thickness_mm=4,remaining_axial_seatweb_mm=2.14,nutwasher_mm=.5,nut_AF_mm=5.5,nut_thickness_mm=2.4,full_nut_end_from_top_mm=thick+2.9,tip_beyond_fullnut_mm=L-thick-2.9,head_top_flush=True,head_flatwasher=False,objects=names,print_owners=j['printed_owners'],assembly_order=j['access_order'],routine_service='UppermicandBUSaccess fromopentop/side; lowerframejoint onlybeforeboards, rarePCBdemount permitted',source_demand='NEW nominal ISO10642 demand, not stock claim or purchasedgeometry reselection'))
plan=dict(status='ONE_WHOLE_TEN_JOINT_ARCHITECTURE_BEFORE_PRINT_DELTA',created_utc=datetime.now(timezone.utc).isoformat(),source_manifest_sha256=hashlib.sha256((OLD/'manifest.json').read_bytes()).hexdigest(),manufacturer_primary='BossardBN2104 ISO10642 PDF https://www.tme.eu/Document/8ccf0396b9d8180afe969e47af892318/BN_2104_1_Bossard_1.pdf p1; M3 dkmax6.72/kmax1.86/90deg/socket2/depth1.1/L10and12. Lengthincludeshead as drawing.',old_two_negatives_retained=['C0sockethead/BNO1.6539166','C1sockethead/MAIN2.9186763'],whole_decision='Allten NEWsocketheadsets replaced by completeflushcountersunk nominalsets. Fourqualifieddeckclamps unchanged. Printedheadbearing4mm and2.14mmweb; lowerparting4+2mm, upper4+2mm; BUS4+4mm. No module/axis move, no headshrink/cutrod.',joints=rows,necessary_material_delta=['Lowerfour laps reassigned to4mmouterheadbearing/2mminner; positiveinnerbossY14..16 only','Upperfourtabs4mmZ134..138 +gate2mmZ132..134/full12wide/leftfrontX-107; all continuousbeamfunctions retained','BUSfixedears12x12 transverse/4mmaxial +legY-23 extension; 4+4mm stack'],first_gate='All30fullpermanentmetalobjects vsactualnearbyretainedboards/ports/base/cases/nominalcooling, numericcull first. No support changes untilthatgate.',physical_pass=False,inventory_confirmed=False,new_purchase=False)
(P/'whole-fastening-plan.json').write_bytes((json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode());D.recompute();D.save()
def lower(a,b):
 a=a.BoundBox;b=b.BoundBox;return math.sqrt(sum(max(0,getattr(a,k+'Min')-getattr(b,k+'Max'),getattr(b,k+'Min')-getattr(a,k+'Max'))**2 for k in 'XYZ'))
r=dict(status='NEW_WHOLE_HARDWARE_RUNNING',rows=[],bounds=[],first_falsifier=None,unchanged_oldchecks_replayed=False)
def save():r.update(wall_seconds=time.perf_counter()-T,cpu_seconds=time.process_time()-CPU);(P/'hardware-gate.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
def run():
 targets=[]
 for o in D.getObject('Retained_whole_layout_REFERENCE').Group:
  if not hasattr(o,'Shape') or o.Shape.isNull():continue
  if o.Name.startswith('Ola_') or 'bracket_space' in o.Name or o.Name in ['Right_logic_open','Left_power_open','Rear_aux_open','USB500_loose_loop','Four_220_joint_exits','Neck_shared_root','Battery_tray_shared']:continue
  if o.Name=='WAVEGO_complete_126_source_solids':targets.extend([('WAVEGOsolid'+str(i),s) for i,s in enumerate(o.Shape.Solids)])
  else:targets.append((o.Name,o.Shape))
 targets.extend([(n,D.getObject(n).Shape) for n in ['BNO_FULL_SOURCE_INSTALLATION_COVER','RS_USB_FULL_SOURCE_COVER']]);save()
 for o in grp.Group:
  for n,q in targets:
   lb=lower(o.Shape,q)
   if lb>=1.25001:r['bounds'].append(dict(a=o.Name,b=n,lower_mm=lb));continue
   assert q.isValid();gap=o.Shape.distToShape(q)[0];row=dict(a=o.Name,b=n,gap_mm=gap,required_mm=1.25,valid=True,pass_scoped=gap>=1.25-1e-6);r['rows'].append(row)
   if not row['pass_scoped']:
    c=o.Shape.common(q);row.update(common_mm3=c.Volume,common_valid=c.isValid());r['first_falsifier']=row;r['status']='WHOLE_HARDWARE_HOLD';o.Shape.exportBrep(str(P/'hardware-falsifier-a.brep'));q.exportBrep(str(P/'hardware-falsifier-b.brep'));save();return
  save()
 r['status']='ALL_TEN_FULL_METAL_SETS_CLEAR_SCOPED';r['metal_objects']=len(grp.Group);r['targets']=len(targets);save()
run();print(json.dumps({'status':r['status'],'joints':len(rows),'metal':len(grp.Group),'exact':len(r['rows']),'bounds':len(r['bounds']),'first_falsifier':r['first_falsifier'],'seconds':r['wall_seconds']}))
