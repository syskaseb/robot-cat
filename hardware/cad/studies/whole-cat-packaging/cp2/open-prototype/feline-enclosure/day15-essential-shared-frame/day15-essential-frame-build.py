import FreeCAD as A,FreeCADGui as G,Part,MeshPart,json,math,time
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;D=A.getDocument('DAY15_ESSENTIAL_SHARED_FRAME');P=Path(r'C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-essential-shared-frame');T=time.perf_counter();CPU=time.process_time()
def box(x,y,z,dx,dy,dz):return Part.makeBox(dx,dy,dz,V(x,y,z))
def fuse(a,b):return a.fuse(b)
def bb(s):
 b=s.BoundBox;return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
M=D.getObject('CF_COMMON_LOAD_ENVELOPE').Shape;C=D.getObject('AL_REMOVABLE_MIC_TOUCH_FRAME').Shape;BUS=D.getObject('CF_REMOVABLE_BUS_BRIDGE').Shape
frontmask=box(-200,-200,0,102,400,200);rearmask=box(95,-200,0,105,400,200)
for y in [-88,79.5]:
 frontmask=frontmask.fuse(box(-98,y,48.52,7,8.5,3));rearmask=rearmask.fuse(box(89,y,48.52,6,8.5,3))
fm=M.common(frontmask);rm=M.common(rearmask);mid=M.cut(fm).cut(rm)
fc=C.common(box(-200,-200,0,102,400,200));rc=C.common(box(95,-200,0,105,400,200));cm=C.cut(fc).cut(rc);touch=cm.common(box(-200,20,0,400,180,200));mic=cm.cut(touch)
front=fm.fuse(fc);rear=rm.fuse(rc)
# Whole actual root jaws belong to the corresponding gate, not to an arbitrary X slice.
parts={'P10_front_gate':front,'P11_rear_gate':rear,'P12_common_deck_speaker':mid,'P13_BUS_bridge':BUS,'P14_fixed_touch_rail':touch,'P15_removable_mic_rail':mic}
source_before={n:s for n,s in parts.items()};jointlog=[];allcuts=[];steels=[];tools=[]
# Integral rail fingers, two per gate, transfer their overlapping material out of middle deck.
for gn,x0,dx in [('P10_front_gate',-104,18),('P11_rear_gate',83,18)]:
 for y,w in [(-20,3),(16,2)]:
  # Entire front negative lap reaches the BNO-free receiver zone, derived from
  # coverXmax-72.2 +1.25foreign +3.5wholewasher = axis>=-67.45; choose-65.
  span=45 if gn=='P10_front_gate' and y==-20 else dx
  finger=box(x0,y,88,span,w,8);old=parts[gn];parts[gn]=old.fuse(finger);parts['P12_common_deck_speaker']=parts['P12_common_deck_speaker'].cut(finger)
  jointlog.append(dict(role='integral_half_lap_finger',gate=gn,contact_old_mm3=old.common(finger).Volume,member_missing_mm3=finger.cut(parts[gn]).Volume,section_mm=[w,8],no_strength_claim=True))
# Two separate upper rails: righttouch remains fixed and wired; leftmic rail/tray can lift.
for gn,x0,dx in [('P10_front_gate',-104,16),('P11_rear_gate',85,22)]:
 for pn,y in [('P14_fixed_touch_rail',16),('P15_removable_mic_rail',-26)]:
  tab=box(x0,y,135.5,dx,10,2.5);lip=box(x0,y,132.5,dx,10,3)
  old=parts[pn];parts[pn]=old.fuse(tab);parts[gn]=parts[gn].cut(tab).fuse(lip)
  jointlog.append(dict(role='upper_rail_bolted_bearing_lap',gate=gn,rail=pn,tab_missing_mm3=tab.cut(parts[pn]).Volume,lip_missing_mm3=lip.cut(parts[gn]).Volume,old_rail_overlap_mm3=old.common(tab).Volume,bearing_area_mm2=dx*10))
# BUS support stays removable; two fixed ears transfer its leg load to the retained inner rail.
for x in [8,66]:
 ear=box(x,-20,94,4,6,10);old=parts['P12_common_deck_speaker'];parts['P12_common_deck_speaker']=old.fuse(ear);jointlog.append(dict(role='BUS_integral_fixed_ear',old_overlap_mm3=old.common(ear).Volume,member_missing_mm3=ear.cut(parts['P12_common_deck_speaker']).Volume))
# The underlap must be a continuous transverse loadmember. Four isolated lips only
# shared an edge with the old topbeam after tab-transfer and were not printable.
for gn,x,w in [('P10_front_gate',-104,6),('P11_rear_gate',95,12)]:
 beam=box(x,-86,132.5,w,172,3);parts[gn]=parts[gn].fuse(beam);jointlog.append(dict(role='continuous_upper_underlap_crossmember',gate=gn,member_missing_mm3=beam.cut(parts[gn]).Volume,section_mm=[w,3],no_strength_claim=True))
intended={n:s for n,s in parts.items()}
def cylinder(r,h,p,axis):return Part.makeCylinder(r,h,V(*p),V(*axis))
def point(p,a,t):return [p[i]+a[i]*t for i in range(3)]
def hardware(tag,base,axis,L,thick,owners,access):
 # base=outer printed bearing face, positive axis points into the joint.
 # Complete two-sided standard stack: head + washer + shaft + washer + full nut.
 a=A.Vector(*axis);rot=A.Rotation(V(0,0,1),a)
 def locate(s,t):s=s.copy();s.Placement=A.Placement(V(*point(base,axis,t)),rot);return s
 sh=Part.makeCylinder(1.5,L).fuse(Part.makeCylinder(2.75,3,V(0,0,-3)))
 steel=[('bolt_M3x'+str(L),locate(sh,-.5))]
 washer=Part.makeCylinder(3.5,.5).cut(Part.makeCylinder(1.65,.5));steel += [('head_washer',locate(washer,-.5)),('nut_washer',locate(washer,thick))]
 R=5.5/math.sqrt(3);pts=[V(R*math.cos(j*math.pi/3),R*math.sin(j*math.pi/3),0) for j in range(7)];nut=Part.Face(Part.Wire(Part.makePolygon(pts).Edges)).extrude(V(0,0,2.4)).cut(Part.makeCylinder(1.5,2.4));steel.append(('nut_AF5p5x2p4',locate(nut,thick+.5)))
 for role,s in steel:steels.append((tag+'_'+role,s))
 bore=cylinder(1.65,thick+2,point(base,axis,-1),axis)
 # Counterbore continues to the open side of any wider shared plate, not only the nominal rail face.
 headclear=cylinder(3.65,40,point(base,axis,-40),axis);nutclear=cylinder(3.65,30,point(base,axis,thick),axis)
 cut=bore.fuse(headclear).fuse(nutclear)
 for pn in owners:parts[pn]=parts[pn].cut(cut)
 allcuts.append(cut);tool=cylinder(2.5,12,point(base,axis,-15.5),axis);tools.append((tag+'_driver_before_boards',tool,owners))
 jointlog.append(dict(role='complete_M3_joint',tag=tag,axis=axis,outer_bearing=base,printed_stack_mm=thick,bolt_length_mm=L,full_nut_end=thick+.5+2.4,tip_mm=L-.5,tip_beyond_nut_mm=L-.5-(thick+.5+2.4),washers=2,nuts=1,standard_demand_unconfirmed=True,printed_owners=owners,access_order=access,nominal_driver_R=2.5))
for gn,x in [('P10_front_gate',-92),('P11_rear_gate',89)]:
 hardware(gn+'_negative',[-65 if gn=='P10_front_gate' else x,-20,92],[0,1,0],12,6,[gn,'P12_common_deck_speaker'],'Bare frame from -Y before PCB/ends/bank closure; frontentirelapoutsideBNO axis>=-67.45')
 hardware(gn+'_positive',[x,20,92],[0,-1,0],10,4,[gn,'P12_common_deck_speaker'],'Bare frame from +Y before MAIN/PCB; never drive through installed MAIN')
for gn,x in [('P10_front_gate',-101),('P11_rear_gate',101)]:
 for pn,y in [('P14_fixed_touch_rail',21),('P15_removable_mic_rail',-21)]:hardware(gn+'_'+pn,[x,y,138],[0,0,-1],12,5.5,[gn,pn],'Open top driver; remove leftmic2bolts only for battery, righttouch stays wired')
hardware('BUS_front',[8,-17,100],[1,0,0],16,8,['P12_common_deck_speaker','P13_BUS_bridge'],'Side driver after leftmic rail removed; actual BUS USB/power disconnected')
hardware('BUS_rear',[70,-17,100],[-1,0,0],16,8,['P12_common_deck_speaker','P13_BUS_bridge'],'Side driver after leftmic rail removed; actual BUS USB/power disconnected')
# The open front driverchannel separates a small EXISTING traycorner. Transfer its
# material/load role to the touching frontgate; never export a loose unintended chip.
for s in list(parts['P12_common_deck_speaker'].Solids):
 b=s.BoundBox
 if b.XMax < -60 and b.YMax <= -20+1e-6 and b.ZMin > 92:
  parts['P10_front_gate']=parts['P10_front_gate'].fuse(s);parts['P12_common_deck_speaker']=parts['P12_common_deck_speaker'].cut(s)
  intended['P10_front_gate']=intended['P10_front_gate'].fuse(s);intended['P12_common_deck_speaker']=intended['P12_common_deck_speaker'].cut(s)
  jointlog.append(dict(role='actual_front_traywing_and_post_partition_transfer',to='P10_front_gate',volume_mm3=s.Volume,reason='Connected via actual frontcrossbeam face; samecombinedmaterial and actualPi holeframe, driverchannel remainsopen'))
# Structural parts, unchanged four lower jaws exported in two types; no boughtshape fused.
parts['P16_front_lower_jaw']=D.getObject('CL_Fm_lower').Shape;parts['P17_rear_lower_jaw']=D.getObject('CL_Rm_lower').Shape
grp=D.addObject('App::DocumentObjectGroup','ESSENTIAL_REAL_PRINT_PARTS');hw=D.addObject('App::DocumentObjectGroup','ESSENTIAL_NEW_STANDARD_STEEL');tg=D.addObject('App::DocumentObjectGroup','ESSENTIAL_DRIVER_BEFORE_MODULES_NOT_PARTS')
for o in D.Objects:
 if hasattr(o,'Shape') and (o.Name.startswith(('CF_','AL_added_','AL_cap_')) or o.Name in ['AL_REMOVABLE_MIC_TOUCH_FRAME'] or o.Name.startswith('CL_') and o.Name.endswith(('_upper','_lower'))):o.ViewObject.Visibility=False
rows=[]
for debugn,debugs in parts.items():debugs.exportBrep(str(P/(debugn+'-precheck.brep')))
for n,s in parts.items():
 assert s.isValid() and len(s.Solids)==1,(n,'construction',s.isValid(),len(s.Solids))
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=(.45,.68,.8);grp.addObject(o)
 # Export each print in a local positiveXYZ frame. Gates print flat on their broad YZ face.
 local=s.copy()
 if n in ['P10_front_gate','P11_rear_gate']:local.rotate(V(0,0,0),V(0,1,0),90)
 elif n=='P13_BUS_bridge':local.rotate(V(0,0,0),V(1,0,0),180)
 b=local.BoundBox;local.translate(V(-b.XMin,-b.YMin,-b.ZMin));b=local.BoundBox;size=[b.XLength,b.YLength,b.ZLength];assert max(size)<256
 mesh=MeshPart.meshFromShape(Shape=local,LinearDeflection=.15,AngularDeflection=.2,Relative=False);mesh.write(str(P/(n+'.stl')));s.exportBrep(str(P/(n+'.brep')))
 rows.append(dict(name=n,quantity=2 if n.startswith(('P16','P17')) else 1,world_bounds_mm=bb(s),print_size_mm=size,valid=True,solids=1,volume_mm3=s.Volume,print_orientation='Gate broadYZ flat; other naturalbase, BUS plateflat flipped',support_note='P12 speakerhang underside may need support; perform actual coupon/slicer preview later, no slicer run now' if n=='P12_common_deck_speaker' else 'flatbearing face onbed; actual printer fit trial',retention_scope='Structuralframe only; boardedge/audioholdingsurfaces and battery/bankkeepers remainNEXT'))
for n,s in steels:
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;hw.addObject(o);o.ViewObject.ShapeColor=(.6,.6,.62)
for n,s,owners in tools:
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;tg.addObject(o);o.ViewObject.Visibility=False
plan=dict(status='REAL_PARTS_SAVED_BEFORE_CHANGED_GATES',created_utc=datetime.now(timezone.utc).isoformat(),parts=rows,joints=jointlog,old_references_retired='CF_COMMON_LOAD_ENVELOPE +wholecap +CFbridge +CLupperlogicalmembers are referenceonly; P10..P17areONLYnewprintassembly. Oldfoundation unchanged.',touch_sequence='TTP223 wholeboard/pose fixed onP14rightbar; existingE1lead remainsconnected and unmoved. Remove2P15bolts+actualRSUSB ->leftmicbar out; then2BUSbolts+actualBUSends ->bridge out; unplugbattery and handlift/translate toleftopenarea. No touch parking or newconnector/slack assumed.',factory_unknowns='ActualRSUSB SKU/length, AMPheader/ends, speakerholdingrim/micports and allfactoryreach FIT. No wholekit/physical PASS.',physical_pass=False,structural_strength_pass=False,print_release='PENDING_CHANGED_INTERFACE_GATES',wall_seconds=time.perf_counter()-T,cpu_seconds=time.process_time()-CPU)
(P/'parting.json').write_bytes((json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode());D.Label='DAY15 essential shared frame — changed checks pending';D.recompute();A.setActiveDocument(D.Name);G.activeDocument().activeView().viewAxonometric();G.activeDocument().activeView().fitAll();D.save()
# Construction/coverage checkpoint before any exact neighboring-part test.
coverage=[]
for n,s in intended.items():
 allowed=s
 for c in allcuts:allowed=allowed.cut(c)
 missing=allowed.cut(parts[n]).Volume;coverage.append(dict(name=n,intended_missing_outside_named_bores_mm3=missing));assert missing<1e-5,(n,missing)
disjoint=[]
names=list(parts)[:6]
for i,n in enumerate(names):
 for m in names[i+1:]:
  v=parts[n].common(parts[m]).Volume;disjoint.append(dict(a=n,b=m,common_mm3=v));assert v<1e-5,(n,m,v)
plan['intended_material_coverage']=coverage;plan['separate_prints_disjoint']=disjoint;plan['status']='CONSTRUCTION_COVERAGE_DISJOINT_CLOSED_NEIGHBORS_PENDING';plan['wall_seconds']=time.perf_counter()-T;plan['cpu_seconds']=time.process_time()-CPU;(P/'parting.json').write_bytes((json.dumps(plan,ensure_ascii=False,indent=2)+'\n').encode());print(json.dumps({'status':plan['status'],'parts':len(rows),'pieces':sum(r['quantity'] for r in rows),'hardware_units':len(steels),'objects':len(D.Objects),'seconds':plan['wall_seconds']}))
