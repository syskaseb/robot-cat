import FreeCAD as A,FreeCADGui as G,Part,json,math,time
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector;t0=time.perf_counter()
def bx(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def bb(s):
 b=s.BoundBox;return[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def wr(n,d):(P/n).write_bytes((json.dumps(d,indent=2)+'\n').encode())
def add(n,s,col=(.4,.59,.63)):
 o=D.getObject(n) or D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;o.ViewObject.Visibility=True;return o
def ring(x,y,z,ro,ri,h):return Part.makeCylinder(ro,h,V(x,y,z)).cut(Part.makeCylinder(ri,h+.2,V(x,y,z-.1)))
def hexnut(x,y,z):
 pts=[V(x+3.175*math.cos(i*math.pi/3),y+3.175*math.sin(i*math.pi/3),z) for i in range(6)]
 return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,2.4)).cut(Part.makeCylinder(1.3,2.6,V(x,y,z-.1)))
def run():
 # Finite source-read BEFORE implementation: two complete lapjoint steel sets
 # outside actual source P01 and the current drives. No source-compound BOP.
 src=D.getObject('WAVEGO_complete_126_source_solids');hits=[]
 for i,s in enumerate(src.Shape.Solids):
  b=s.BoundBox
  for y in [-65,65]:
   if b.XMax>=-2.75 and b.XMin<=6.75 and b.YMax>=y-4.75 and b.YMin<=y+4.75 and b.ZMax>=35.77 and b.ZMin<=53.27:hits.append({'i':i,'y':y,'bounds':bb(s)})
 wr('current-two-joint-preflight.json',{'locations':[[2,-65],[2,65]],'expanded_completehardware125':True,'source_cached_candidates':hits,'source_solids_read':126,'no_global_exact':True,'body':{'P_FRONT_maxX':-13,'bridge_minX':-10,'MTAfront_rail_y':[28.25,30.75],'MTArear_rail_y':[73,83],'newhead_y':[61.5,68.5],'sourceP01_y':[-27.5,27.5]},'initialorder':'gridsplicesteel and driver BEFORE MTA/Pi/bodykit; no leg/bankvirtualdetach'})
 if hits:
  print('HOLD actualsource jointcandidates requireboundedread beforeimplementation');return
 oldgrid=D.getObject('NIGHT_SHARED_LOAD_GRID').Shape;oldroot=D.getObject('NIGHT_HEAD_FIXED_SADDLE_ROOT').Shape
 # One integral fixed member, useful actual washer bearing pads with 0.5 mm
 # material beyond full OD5 washers. No moved head/bolt/Pi or reduced cooling.
 root=bx(-86,15,45.52,12,8,21).fuse(bx(-127,15,66.5,53,8,7)).fuse(bx(-127,-13,66.5,28,36,3))
 pads=[]
 for y in [-11.5,11.5]:
  pad=bx(-114,y-3,66.5,8,6,3);pads.append(pad);root=root.fuse(pad).cut(Part.makeCylinder(1.1,6,V(-110,y,65)))
 # Grid/root are now ACTUAL one printed part before the planned grid split.
 whole=oldgrid.fuse(root)
 cross=bx(-10,-85,45.52,24,169,3);whole=whole.fuse(cross)
 bridges=[]
 for y in [-65,65]:
  q=bx(-18,y-6,41.52,40,12,7);bridges.append(q);whole=whole.fuse(q).cut(Part.makeCylinder(1.7,10,V(2,y,40.5)))
 # Real half-lap parting across this crossmember: lower-front/upper-rear.
 # Both halves retain four existing source-anchor axes, never cut bought base.
 zone=bx(-10,-85,40,24,169,14);inside=whole.common(zone);outside=whole.cut(zone)
 front=outside.common(bx(-200,-100,35,202,200,70)).fuse(inside.common(bx(-10,-85,40,24,169,5.02)))
 rear=outside.common(bx(2,-100,35,160,200,70)).fuse(inside.common(bx(-10,-85,45.02,24,169,8.98)))
 # Matched tongue/edge restraint supplied by full stepped crossmember and
 # two separated bolts, not friction-only or an invisible screw thread.
 add('RG_FRONT_GRID_WITH_INTEGRAL_HEAD_RECEIVER',front)
 add('RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER',rear)
 for n in ['NIGHT_SHARED_LOAD_GRID','NIGHT_HEAD_FIXED_SADDLE_ROOT']:D.getObject(n).ViewObject.Visibility=False
 for y in [-65,65]:
  pre='RG_SPLICE_'+str(y);add(pre+'_M3x12_fullscrew',Part.makeCylinder(1.5,12,V(2,y,37.02)).fuse(Part.makeCylinder(2.75,3,V(2,y,49.02))),(.68,.69,.7))
  add(pre+'_upperwasher',ring(2,y,48.52,3.5,1.6,.5),(.68,.69,.7));add(pre+'_lowerwasher',ring(2,y,41.02,3.5,1.6,.5),(.68,.69,.7));add(pre+'_fullnut',hexnut(2,y,38.62),(.68,.69,.7))
 D.recompute();D.save()
 # Save checkpoint first. Only actual changed integration, coverage and source
 # seating/foreign relations follow; old8FFC/forepairs are not replayed.
 total=front.fuse(rear);common=front.common(rear)
 coverage={'old_grid_missing':oldgrid.cut(total).Volume,'new_root_missing':root.cut(total).Volume,'planned_crossmember_missing':cross.cut(total).Volume,'two_fullbridge_members_missing':[q.cut(total).Volume for q in bridges],'union_missing':whole.cut(total).Volume,'union_added':total.cut(whole).Volume,'separate_common':common.Volume,'separate_common_valid':common.isValid(),'front_solids':len(front.Solids),'rear_solids':len(rear.Solids),'front_valid':front.isValid(),'rear_valid':rear.isValid()}
 wr('actual-integral-parting-and-member-coverage.json',coverage)
 cool=D.getObject('Pi_components_and_cooling').Shape;saddle=D.getObject('YAW_REAL_REMOVABLE_SERVO_SADDLE').Shape
 # Full source8holes retained by subset (oldgrid missing0), standard2M2x10
 # unchanged, receiver face69.5 proved again ONLY because pad material changed.
 fa=[f for f in root.Faces if abs(f.BoundBox.ZMin-69.5)<1e-7 and abs(f.BoundBox.ZMax-69.5)<1e-7];fb=[f for f in saddle.Faces if abs(f.BoundBox.ZMin-69.5)<1e-7 and abs(f.BoundBox.ZMax-69.5)<1e-7]
 bearing=Part.makeCompound(fa).common(Part.makeCompound(fb)).Area
 wr('root-cooling-and-actual-bearing.json',{'new_root_cooling_gap':root.distToShape(cool)[0],'new_front_cooling_gap':front.distToShape(cool)[0],'required':1.25,'root_saddle_common':root.common(saddle).Volume,'contact_Z69p5_area':bearing,'root_new_material_vs_old':root.cut(oldroot).Volume,'old_unbuilt_root_retired_volume':oldroot.cut(root).Volume,'fullM2x10_rootsets':'samefullsource83b steel/centres/no shaft/head offset','actual_defined_pad':[8,6,3],'washer_OD':5,'beyondwasher_edge':.5,'bore_wall_min':1.9,'no_strengthPASS':True})
 contacts=[]
 for n in ['P01_load_rail','P01_load_rail_instance2']:
  o=D.getObject(n)
  if o:
   # New front is an integrated grid identity; actual contactarea at45.52.
   faces=[f for f in o.Shape.Faces if abs(f.BoundBox.ZMin-45.52)<1e-6 and abs(f.BoundBox.ZMax-45.52)<1e-6]
   bottoms=[f for f in front.Faces if abs(f.BoundBox.ZMin-45.52)<1e-6 and abs(f.BoundBox.ZMax-45.52)<1e-6]
   area=Part.makeCompound(faces).common(Part.makeCompound(bottoms)).Area if faces and bottoms else 0
   contacts.append({'source':n,'front_Z45p52_area':area,'common':front.common(o.Shape).Volume})
 wr('P01-real-source-seats-and-print-envelope.json',{'contacts':contacts,'front_sourceaxes':[-80,-70],'rear_sourceaxes':[112,122],'both_y':[-22.5,22.5],'source8holes':'originalgrid retained subset/coverage, no boughtdrill/tap/sourcecut','newprints':[{'n':n,'bounds':bb(sh),'XYZ':[sh.BoundBox.XLength,sh.BoundBox.YLength,sh.BoundBox.ZLength],'orientation':'worldZ base down; root underside support/coupon, no slicerclaim','brim_allowance_each_side':4,'under256_including_brim':max(sh.BoundBox.XLength+8,sh.BoundBox.YLength+8,sh.BoundBox.ZLength+8)<256} for n,sh in [('FRONT',front),('REAR',rear)]],'lap_planeZ':45.02,'lap_quantity':2,'completeM3x12':{'qty':2,'upperhead_underZ':49.02,'tip':37.02,'fullnut':[38.62,41.02],'lowerwasher':[41.02,41.52],'upperwasher':[48.52,49.02],'nutengagement':2.4,'tipbeyondnut':1.6,'source':'NEEDED_UNCONFIRMED_NOTPURCHASE'},'assembly':'emptybase/P01source8sets; lapnuts/washers frombottom+R4.25driverfromtop beforePi/MTA/connectedE1kit; thenhead2M2/saddle; masks/coverslate','physicalP00threads_and_payload':'OPEN physical only, not fabricatedsupplierthread'})
 print(json.dumps({'coverage':coverage,'cool_gap':root.distToShape(cool)[0],'seat_area':bearing,'seconds':time.perf_counter()-t0}))
run()
