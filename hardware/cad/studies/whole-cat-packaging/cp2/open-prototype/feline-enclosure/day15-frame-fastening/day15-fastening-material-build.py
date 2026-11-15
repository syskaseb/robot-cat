import FreeCAD as A,FreeCADGui as G,Part,MeshPart,json,math,time
from pathlib import Path
from datetime import datetime,timezone
V=A.Vector;D=A.getDocument('DAY15_FRAME_FASTENING');P=Path(r'C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-frame-fastening');T=time.perf_counter();CPU=time.process_time()
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
 for y,w in [(-20,4),(14,2)]:
  # Entire front negative lap reaches the BNO-free receiver zone, derived from
  # coverXmax-72.2 +1.25foreign +3.5wholewasher = axis>=-67.45; choose-65.
  span=45 if gn=='P10_front_gate' and y==-20 else dx
  finger=box(x0,y,88,span,w,8);old=parts[gn];parts[gn]=old.fuse(finger);parts['P12_common_deck_speaker']=parts['P12_common_deck_speaker'].cut(finger)
  jointlog.append(dict(role='integral_half_lap_finger',gate=gn,contact_old_mm3=old.common(finger).Volume,member_missing_mm3=finger.cut(parts[gn]).Volume,section_mm=[w,8],no_strength_claim=True))
uppertabs=[]
# Two separate upper rails: righttouch remains fixed and wired; leftmic rail/tray can lift.
for gn,x0,dx in [('P10_front_gate',-107,19),('P11_rear_gate',85,22)]:
 for pn,y in [('P14_fixed_touch_rail',15),('P15_removable_mic_rail',-27)]:
  tab=box(x0,y,134,dx,12,4);lip=box(x0,y,132,dx,12,2);uppertabs.append(tab)
  old=parts[pn];parts[pn]=old.fuse(tab);parts[gn]=parts[gn].cut(tab).fuse(lip)
  jointlog.append(dict(role='upper_rail_bolted_bearing_lap',gate=gn,rail=pn,tab_missing_mm3=tab.cut(parts[pn]).Volume,lip_missing_mm3=lip.cut(parts[gn]).Volume,old_rail_overlap_mm3=old.common(tab).Volume,bearing_area_mm2=dx*10))
# BUS support stays removable; two fixed ears transfer its leg load to the retained inner rail.
for x in [8,66]:
 ear=box(x,-23,94,4,12,12);old=parts['P12_common_deck_speaker'];parts['P12_common_deck_speaker']=old.fuse(ear);jointlog.append(dict(role='BUS_integral_fixed_ear',old_overlap_mm3=old.common(ear).Volume,member_missing_mm3=ear.cut(parts['P12_common_deck_speaker']).Volume))
# The underlap must be a continuous transverse loadmember. Four isolated lips only
# shared an edge with the old topbeam after tab-transfer and were not printable.
for gn,x,w in [('P10_front_gate',-104,6),('P11_rear_gate',95,12)]:
 beam=box(x,-86,132.5,w,172,3);parts[gn]=parts[gn].fuse(beam);jointlog.append(dict(role='continuous_upper_underlap_crossmember',gate=gn,member_missing_mm3=beam.cut(parts[gn]).Volume,section_mm=[w,3],no_strength_claim=True))
for gn in ['P10_front_gate','P11_rear_gate']:
 for tab in uppertabs:parts[gn]=parts[gn].cut(tab)
for x in [12,62]:parts['P13_BUS_bridge']=parts['P13_BUS_bridge'].fuse(box(x,-23,96,4,3,8))
intended={n:s for n,s in parts.items()}

# Appended to the explicit source-parting prefix. All source/bought poses unchanged.
plan=json.loads((P/'whole-fastening-plan.json').read_bytes());rowsby={j['tag']:j for j in plan['joints']};feeds=[];seats=[];tools=[];cuts=[];cage_allocations=[]
def place(s,j):s=s.copy();s.Placement=A.Placement(V(*j['base']),A.Rotation(V(0,0,1),V(*j['axis'])));return s
def polyhex(af,z,h):
 r=af/math.sqrt(3);pts=[V(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3),z) for i in range(7)];return Part.Face(Part.Wire(Part.makePolygon(pts).Edges)).extrude(V(0,0,h))
def hull(points):
 q=sorted(set(points));cross=lambda o,a,b:(a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0]);low=[];high=[]
 for p in q:
  while len(low)>1 and cross(low[-2],low[-1],p)<=0:low.pop()
  low.append(p)
 for p in reversed(q):
  while len(high)>1 and cross(high[-2],high[-1],p)<=0:high.pop()
  high.append(p)
 return low[:-1]+high[:-1]
def sweep_nut(af,z,h):
 r=af/math.sqrt(3);points=[(r*math.cos(i*math.pi/3),r*math.sin(i*math.pi/3)+y) for i in range(6) for y in [0,8]];pp=hull(points);wire=Part.makePolygon([V(x,y,z) for x,y in pp+[pp[0]]]);return Part.Face(Part.Wire(wire.Edges)).extrude(V(0,0,h))
def sweep_washer(r,z,h):return Part.makeCylinder(r,h,V(0,0,z)).fuse(box(-r,0,z,2*r,8,h)).fuse(Part.makeCylinder(r,h,V(0,8,z)))
for j in plan['joints']:
 tag=j['tag'];t=j['printed_stack_mm'];upper='P14_' in tag or 'P15_' in tag;bus=tag.startswith('BUS_');owners=j['print_owners']
 headowner='P12_common_deck_speaker' if bus else ('P14_fixed_touch_rail' if 'P14_' in tag else 'P15_removable_mic_rail') if upper else 'P12_common_deck_speaker' if tag.endswith('positive') else owners[0]
 backowner='P13_BUS_bridge' if bus else owners[0] if upper else owners[0] if tag.endswith('positive') else 'P12_common_deck_speaker'
 cage=place(box(-5,-4,t,10,8,4.5),j);old=parts[backowner];parts[backowner]=old.fuse(cage);cage_allocations.append((tag,cage,backowner));jointlog.append(dict(role='integral_anti_rotation_nut_and_washer_cage',tag=tag,owner=backowner,member_missing_mm3=cage.cut(parts[backowner]).Volume,source_contact_area_mm2=old.common(cage).Area,loadseat_protected_before_plane=t))
 bore=place(Part.makeCylinder(1.65,t+5),j);cone=place(Part.makeCone(3.36,1.5,1.86),j);headentry=place(Part.makeCylinder(3.65,40,V(0,0,-40)),j);feedcut=place(sweep_washer(3.6,t,.6).fuse(sweep_nut(5.7,t+.4,2.6)),j)
 for pn in owners:parts[pn]=parts[pn].cut(bore.fuse(cone).fuse(headentry).fuse(feedcut))
 # Cage backowner is among the same two joint owners. No unqualified print is detached.
 nominalfeed=place(sweep_washer(3.5,t,.5).fuse(sweep_nut(5.5,t+.5,2.4)),j);feeds.append((tag,nominalfeed,backowner));seats.append(dict(tag=tag,headowner=headowner,backowner=backowner,axial_web_mm=4-1.86,actual_stock_feed_mm=8,feed_world_direction=list(A.Rotation(V(0,0,1),V(*j['axis'])).multVec(V(0,1,0))),full_nut_mm=2.4,washer_mm=.5,nominal_length_includes_head=True))
 key=polyhex(2,-12,13.1).fuse(Part.makeCylinder(2.5,8,V(0,0,-20)));tools.append((tag,place(key,j)))
# Real parting assigns remaining cage MATERIAL to its backpart, never to both prints.
# Feed voids were already cut above. Local transfer proves no lost combined material.
for tag,cage,backowner in cage_allocations:
 material=parts[backowner].common(cage)
 for pn in list(parts):
  if pn==backowner:continue
  before=parts[pn];overlap=before.common(material).Volume
  if overlap>1e-6:
   parts[pn]=before.cut(material);removed=before.cut(parts[pn]);lost=removed.cut(parts[backowner]).Volume;assert lost<1e-5
   jointlog.append(dict(role='explicit_cage_material_partition_same_union',tag=tag,from_print=pn,to_print=backowner,transferred_mm3=overlap,combined_material_lost_mm3=lost,head_bearing_before_plane4_unchanged=True))
parts['P16_front_lower_jaw']=D.getObject('CL_Fm_lower').Shape;parts['P17_rear_lower_jaw']=D.getObject('CL_Rm_lower').Shape;parts['P18_rear_positive_lower_jaw']=D.getObject('CL_Rp_lower').Shape
# Reassign only actually detached existing tray fragments to their touching frontgate.
for s in list(parts['P12_common_deck_speaker'].Solids):
 b=s.BoundBox
 if b.XMax < -60 and b.YMax <= -20+1e-6 and b.ZMin > 92:
  parts['P10_front_gate']=parts['P10_front_gate'].fuse(s);parts['P12_common_deck_speaker']=parts['P12_common_deck_speaker'].cut(s);jointlog.append(dict(role='same_material_front_tray_partition',volume=s.Volume))
group=D.addObject('App::DocumentObjectGroup','FASTENING_REAL_PRINT_PARTS');ref=D.addObject('App::DocumentObjectGroup','NUT_FEED_AND_KEY_ASSEMBLY_NOT_PARTS');materialrows=[]
for n,s in parts.items():
 s.exportBrep(str(P/(n+'.brep')))
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;group.addObject(o);o.ViewObject.ShapeColor=(.55,.7,.8)
 materialrows.append(dict(name=n,valid=s.isValid(),solids=len(s.Solids),volume_mm3=s.Volume,bounds_mm=bb(s),quantity=2 if n=='P16_front_lower_jaw' else 1))
for o in D.getObject('NEW_CSUNK_STANDARD_STEEL_PROPOSED').Group:o.ViewObject.Visibility=True
for tag,s,owner in feeds:
 o=D.addObject('PartDesign::Feature','FEED_'+tag);o.Shape=s;ref.addObject(o);o.ViewObject.Visibility=False
for tag,s in tools:
 o=D.addObject('PartDesign::Feature','KEY_'+tag);o.Shape=s;ref.addObject(o);o.ViewObject.Visibility=False
for o in D.Objects:
 if hasattr(o,'Shape') and (o.Name.startswith(('CF_','AL_added_','AL_cap_')) or o.Name=='AL_REMOVABLE_MIC_TOUCH_FRAME' or o.Name.startswith('CL_') and o.Name.endswith(('_upper','_lower'))):o.ViewObject.Visibility=False
D.getObject('CL_Fp_lower').ViewObject.Visibility=True
result=dict(status='MATERIAL_SAVED_BEFORE_ASSEMBLY_CHECKS',parts=materialrows,seat_and_feed=seats,junctions=jointlog,one_whole_family=True,new_parts=9,total_pieces=10,print_release=False,first_falsifier=None);(P/'material-result.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode());D.recompute();D.Label='DAY15 full flush fastenings — material checks pending';D.save()
def save():result.update(wall_seconds=time.perf_counter()-T,cpu_seconds=time.process_time()-CPU);(P/'material-result.json').write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
def run():
 for r in materialrows:
  if not r['valid'] or r['solids']!=1:result['first_falsifier']=dict(kind='CONSTRUCTION_DISCONNECTED_OR_INVALID',part=r);result['status']='MATERIAL_CONSTRUCTION_HOLD';save();return
 result['disjoint']=[];names=list(parts)[:6]
 for i,n in enumerate(names):
  for m in names[i+1:]:
   c=parts[n].common(parts[m]);v=c.Volume;result['disjoint'].append(dict(a=n,b=m,common_mm3=v))
   if not c.isValid() or v>1e-5:result['first_falsifier']=dict(kind='PARTS_OVERLAP',a=n,b=m,common_mm3=v);result['status']='PARTING_HOLD';save();return
 result['feed_checks']=[]
 for tag,s,owner in feeds:
  c=s.common(parts[owner]);result['feed_checks'].append(dict(tag=tag,owner=owner,valid=c.isValid(),continuous_8mm_stock_common_mm3=c.Volume))
  if not c.isValid() or c.Volume>1e-5:result['first_falsifier']=dict(kind='ACTUAL_NUT_WASHER_CONTINUOUS_LOADING',tag=tag,owner=owner,common_mm3=c.Volume);result['status']='FEED_HOLD';save();return
 result['permanent_own_metal']=[]
 for o in D.getObject('NEW_CSUNK_STANDARD_STEEL_PROPOSED').Group:
  j=next(j for j in plan['joints'] if o.Name in j['objects'])
  for owner in j['print_owners']:
   c=o.Shape.common(parts[owner]);result['permanent_own_metal'].append(dict(metal=o.Name,owner=owner,common_mm3=c.Volume,matched_bearing_area_mm2=c.Area if c.Volume<1e-5 else None,valid=c.isValid()))
   if not c.isValid() or c.Volume>1e-5:result['first_falsifier']=dict(kind='PERMANENT_METAL_OWN_PRINT',metal=o.Name,owner=owner,common_mm3=c.Volume);result['status']='OWN_METAL_HOLD';save();return
 result['status']='OWN_PARTING_FULL_STOCK_FEEDS_AND_METAL_CLEAR_SCOPED';save()
run();print(json.dumps({'status':result['status'],'parts':materialrows,'first_falsifier':result['first_falsifier'],'seconds':result.get('wall_seconds')}))
