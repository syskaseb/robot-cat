import FreeCAD as A,Part,json,math,time
from pathlib import Path
V=A.Vector;T=time.perf_counter();P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit/fit-kit-ready');OLD=P.parent/'fit-kit-final';D=A.getDocument('DAY14_FIT_KIT_READY');r=json.loads((P/'checkpoint.json').read_bytes());r['checks']=[]
def sh(n):return D.getObject(n).Shape
def box(p,s):return Part.makeBox(*s,V(*p))
def bb(s):
 b=s.BoundBox;return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
def write():
 r['checks_wall_seconds']=time.perf_counter()-T;(P/'result.json').write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
def receive(row,ok=True):
 r['checks'].append(row);write()
 if not ok:r['status']='HOLD_FIRST_ACTUAL_FALSIFIER';r['first_falsifier']=row;write();raise RuntimeError(json.dumps(row))
def hull(pts):
 pts=sorted(set(pts))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[];hi=[]
 for p in pts:
  while len(lo)>1 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 for p in reversed(pts):
  while len(hi)>1 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
  hi.append(p)
 return lo[:-1]+hi[:-1]
def prism(pts,z,h):
 vs=[V(x,y,z) for x,y in pts];vs.append(vs[0]);return Part.Face(Part.Wire(Part.makePolygon(vs).Edges)).extrude(V(0,0,h))
# Exact continuous full nut and washer occupied field, preloaded0.2 lower, no rods or centreline proxy.
for i,p in enumerate(r['pocket_plan']):
 x,y=p['centre'];ex,ey=p['entry'];ey=-87 if i in [0,2] else ey;ang=0 if p['feed_axis']=='X' else math.pi/6;R=5.5/math.sqrt(3)
 pts=hull([(cx+R*math.cos(ang+j*math.pi/3),cy+R*math.sin(ang+j*math.pi/3)) for cx,cy in [(x,y),(ex,ey)] for j in range(6)])
 nut=prism(pts,43.42,2.4);dx=x-ex;dy=y-ey;L=math.hypot(dx,dy);px=-dy/L*3.5;py=dx/L*3.5
 wash=prism([(ex+px,ey+py),(x+px,y+py),(x-px,y-py),(ex-px,ey-py)],45.82,.5)
 for cx,cy in [(x,y),(ex,ey)]:wash=wash.fuse(Part.makeCylinder(3.5,.5,V(cx,cy,45.82)))
 field=nut.fuse(wash);common=field.common(sh('P03_rear_deck_integrated_load_yoke'));receive(dict(kind='FULL_CONTINUOUS_HORIZONTAL_FEED',pocket=i,length_mm=L,common_mm3=common.Volume,valid=field.isValid() and common.isValid()),field.isValid() and common.isValid() and common.Volume<1e-5)
 # Start below actual part minimum41.52. Convex XY profile extruded continuously to loading height is a conservative full unit entry, not just an endcap.
 npts=[(ex+R*math.cos(ang+j*math.pi/3),ey+R*math.sin(ang+j*math.pi/3)) for j in range(6)]
 rise=prism(npts,39,6.82).fuse(Part.makeCylinder(3.5,7.32,V(ex,ey,39)))
 common=rise.common(sh('P03_rear_deck_integrated_load_yoke'));receive(dict(kind='FULL_CONTINUOUS_BELOW_TO_FEED_ENTRY',pocket=i,from_z=39,to_washer_top=46.32,common_mm3=common.Volume,valid=rise.isValid() and common.isValid()),rise.isValid() and common.isValid() and common.Volume<1e-5)
 # Tightening lift0.2 into final roof is separately occupied, all intermediate vertical positions contained.
 n='H03_panel_M3x55_'+str(i);final=sh(n+'_nut').fuse(sh(n+'_washer'));low=final.copy();low.translate(V(0,0,-.2));vol=final.common(sh('P03_rear_deck_integrated_load_yoke')).Volume+low.common(sh('P03_rear_deck_integrated_load_yoke')).Volume
 receive(dict(kind='FINAL_FULL_STACK_SEAT_IDENTITY_AND_PRELOAD',pocket=i,common_mm3=vol,roof_web_mm=2,source='prior fullwasher29.931524seat/completeM3x50 engagement inherited unchanged'),vol<1e-5)
def facearea(sa,sb,z):
 def fs(s):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.BoundBox.ZLength<1e-6 and abs(f.BoundBox.ZMin-z)<1e-6]
 return sum(f.common(g).Area for f in fs(sa) for g in fs(sb))
panel=sh('P06_S0_shared_panel')
for rail,cy,post in [('Upper_frame_rail__49',-47.5,'Upper_frame_post_101__49'),('Upper_frame_rail_44',45.5,'Upper_frame_post_101_44')]:
 s=sh(rail);common=s.common(panel).Volume;area=facearea(s,panel,90)
 receive(dict(kind='REAL_RAIL_SOCKET_BEARING',rail=rail,common_mm3=common,bearing_mm2=area,roof_mm=.8,nominal_side_gap=.15,nominal_roof_gap=.2,nominal_end_gap=.2),common<1e-5 and area>0)
 # Continuous tongue alone through mouth; rail/mainframe preassembled before frontposts/PCB, separateparts not virtually detached.
 tongue=box((90,cy-3,90),(19.8,6,1.5));c=tongue.common(panel).Volume;receive(dict(kind='FULL_TONGUE_CONTINUOUS_10MM_INSERTION',rail=rail,common_mm3=c,sequence='rear socket/panel + two loose rails on bench; front crossframe/posts and PCB late'),c<1e-5)
 a=facearea(sh(post),panel,88.52);c=sh(post).common(panel).Volume;receive(dict(kind='POST_TO_SOCKET_FLOOR',post=post,bearing_mm2=a,common_mm3=c),a>0 and c<1e-5)
# Required useful rail capture: actualroof above full tongue, continuity material to panel/bridge preserved by immutable prior P06 member coverage.
for n in ['S0_body','S0_neck','S0_key']:
 c=panel.common(sh(n)).Volume;receive(dict(kind='S0_FULL_FUNCTIONAL_NONPENETRATION',part=n,common_mm3=c),c<1e-5)
def lower(a,b):
 return math.sqrt(sum(max(l1-h2,l2-h1,0)**2 for l1,h1,l2,h2 in [(a.XMin,a.XMax,b.XMin,b.XMax),(a.YMin,a.YMax,b.YMin,b.YMax),(a.ZMin,a.ZMax,b.ZMin,b.ZMax)]))
# Added P06/socket and changed rail/post vs only nearby retained parts; all other actor geometry kept. No global compound Boolean.
own={'Upper_frame_rail__49','Upper_frame_rail_44','Upper_frame_post_101__49','Upper_frame_post_101_44','P06_S0_shared_panel','P05_S0_panel_spacer40','P05_spacer_instance2','P05_spacer_instance3','P05_spacer_instance4','S0_body','S0_neck','S0_key'}
own|={o.Name for o in D.Objects if o.Name.startswith('H03')}
actors=[o for o in D.Objects if hasattr(o,'Shape') and not o.Shape.isNull() and hasattr(o.ViewObject,'ShapeColor')]
targets=['P06_S0_shared_panel','Upper_frame_rail__49','Upper_frame_rail_44','Upper_frame_post_101__49','Upper_frame_post_101_44']
for name in targets:
 s=sh(name)
 for o in actors:
  if o.Name in own or o.Name==name:continue
  if o.Name=='WAVEGO_complete_126_source_solids':
   items=[(o.Name+':solid'+str(i),q) for i,q in enumerate(o.Shape.Solids)]
  else:items=[(o.Name,o.Shape)]
  for other,q in items:
   lb=lower(s.BoundBox,q.BoundBox)
   if lb>=1.25-1e-6:continue
   # Nominal unbuiltlogic interpart contacts are classified actual function before using fit0; foreign parts remain1.25.
   if other.startswith('Upper_frame_'):
    c=s.common(q).Volume;receive(dict(kind='UNBUILT_LOGIC_FRAME_MATCHED_CONTACT',a=name,b=other,common_mm3=c),c<1e-5);continue
   if len(q.Faces)>100:receive(dict(kind='UNKNOWN_COMPLEX_NEARBY_SOURCE_NOT_GUI_EXACT',a=name,b=other,faces=len(q.Faces),lower_mm=lb),False)
   gap=s.distToShape(q)[0];c=s.common(q).Volume;receive(dict(kind='CHANGED_NEARBY_RETAINED_PART',a=name,b=other,gap_mm=gap,common_mm3=c,valid=s.isValid() and q.isValid()),gap>=1.25-1e-6 and c<1e-5 and s.isValid() and q.isValid())
r['reused']=dict(M3x50fullnut_tip_cover='all12steel bytegeometry equal to frozen44d7b4ec; gaps min4.0, fullnut2.4 tip1.1 seats29.931524 unchanged',P06membercoverage='frozen8members0missing; no P06geometry change',source8holes_and_boughtposes='unchanged; no source scans',P03foreign='materialsubset of frozen previouspart; no addedforeignmaterial')
r['status']='CONDITIONAL_UNPOWERED_FIRST_FIT_LOCAL_FEED_AND_SHARED_LOGIC_FUNCTION_CLOSED';write();D.Label='WAVEGO fit kit — conditional unpowered first fit';D.recompute();D.save();print(json.dumps({'status':r['status'],'checks':len(r['checks']),'seconds':r['checks_wall_seconds']}))
