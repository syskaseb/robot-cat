import FreeCAD as A,Part,json,math,time
from pathlib import Path
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit/fit-kit-final');OLD=P.parent/'foundation-fit-kit'
D=A.getDocument('DAY14_FIT_KIT_FINAL');S=A.getDocument('DAY14_FOUNDATION_FIT_KIT');r=json.loads((P/'checkpoint.json').read_bytes());V=A.Vector;T=time.perf_counter()
def sh(n):return D.getObject(n).Shape
def bbox(s):
 b=s.BoundBox;return [[b.XMin,b.YMin,b.ZMin],[b.XMax,b.YMax,b.ZMax]]
def lower(a,b):
 return math.sqrt(sum(max(l1-h2,l2-h1,0)**2 for l1,h1,l2,h2 in [(a.XMin,a.XMax,b.XMin,b.XMax),(a.YMin,a.YMax,b.YMin,b.YMax),(a.ZMin,a.ZMax,b.ZMin,b.ZMax)]))
def facearea(sa,sb,z):
 def fs(s):return [f for f in s.Faces if isinstance(f.Surface,Part.Plane) and f.BoundBox.ZLength<1e-6 and abs(f.BoundBox.ZMin-z)<1e-6]
 a=0
 for f in fs(sa):
  q=f.copy();q.translate(V(0,0,z-q.BoundBox.ZMin))
  for g in fs(sb):
   p=g.copy();p.translate(V(0,0,z-p.BoundBox.ZMin));a+=q.common(p).Area
 return a
def witness(a,b,kind='foreign'):
 x=sh(a);y=sh(b);gap=x.distToShape(y)[0];common=x.common(y).Volume
 row=dict(a=a,b=b,kind=kind,gap_mm=gap,common_mm3=common,a_valid=x.isValid(),b_valid=y.isValid())
 if kind=='foreign':assert gap>=1.25-1e-6 and common<1e-5,row
 else:assert common<1e-5,row
 return row
out=[]
cover=sh('WAVEGO_complete_126_source_solids').Solids[38]
for i,pocket in enumerate(r['pocket_plan']):
 n='H03_panel_M3x55_'+str(i);s=sh(n);g=s.distToShape(cover)[0];c=s.common(cover).Volume;assert g>=1.25 and c<1e-5
 out.append(dict(a=n,b='ACTUAL_TopCoverSolid38_36faces',gap_mm=g,common_mm3=c,valid=s.isValid() and cover.isValid(),fullnut_engagement=2.4,shaft_beyond_nut=1.1))
 # Fullproper nut andwasher are in realprintedvoids, no penetrationwaiver.
 for k in ['_nut','_washer']:
  c=sh(n+k).common(sh('P03_rear_deck_integrated_load_yoke')).Volume;assert c<1e-5,(n+k,c)
 area=facearea(sh(n+'_washer'),sh('P03_rear_deck_integrated_load_yoke'),46.52);assert area>0
 out.append(dict(a=n+'_washer',b='P03actualroof',seat_area_mm2=area,roof_mm=2,nut_pocket_closed_material_common0=True))
r['joint_checks']=out
(P/'partial-checks.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
# One bounded continuous occupied feed per actualnut+washer profile, not an empty channel.
def hull(pts):
 pts=sorted(set(pts))
 def cross(o,a,b):return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
 lo=[]
 for p in pts:
  while len(lo)>1 and cross(lo[-2],lo[-1],p)<=0:lo.pop()
  lo.append(p)
 hi=[]
 for p in reversed(pts):
  while len(hi)>1 and cross(hi[-2],hi[-1],p)<=0:hi.pop()
  hi.append(p)
 return lo[:-1]+hi[:-1]
feed=[]
for i,p in enumerate(r['pocket_plan']):
 x,y=p['centre'];ex,ey=p['entry'];ang=0 if p['feed_axis']=='X' else math.pi/6;R=5.5/math.sqrt(3)
 pts=hull([(cx+R*math.cos(ang+j*math.pi/3),cy+R*math.sin(ang+j*math.pi/3)) for cx,cy in [(x,y),(ex,ey)] for j in range(6)])
 v=[V(a,b,43.42) for a,b in pts];v.append(v[0]);nut=Part.Face(Part.Wire(Part.makePolygon(v).Edges)).extrude(V(0,0,2.4))
 dx=x-ex;dy=y-ey;L=math.hypot(dx,dy);ux=dx/L;uy=dy/L;px=-uy*3.5;py=ux*3.5
 q=[V(ex+px,ey+py,45.82),V(x+px,y+py,45.82),V(x-px,y-py,45.82),V(ex-px,ey-py,45.82)];q.append(q[0])
 wash=Part.Face(Part.Wire(Part.makePolygon(q).Edges)).extrude(V(0,0,.5))
 for cx,cy in [(x,y),(ex,ey)]:wash=wash.fuse(Part.makeCylinder(3.5,.5,V(cx,cy,45.82)))
 occupied=nut.fuse(wash);c=occupied.common(sh('P03_rear_deck_integrated_load_yoke')).Volume
 
 if not occupied.isValid() or c>=1e-5:
  intersection=occupied.common(sh('P03_rear_deck_integrated_load_yoke'))
  r['status']='HOLD_ONE_PURPOSEFUL_JOINT_FRONT_POSITIVE_LOADING_ENTRY'
  r['first_falsifier']=dict(pocket=i,volume_mm3=c,occupied_valid=occupied.isValid(),common_valid=intersection.isValid(),bounds_mm=bbox(intersection),cause='Full nut/washer loading-profile entrycaps are obstructed by existing thin deck material at entryX99; endseat is not enough. No newgeometry family attempted afterfalsifier.')
  r['received_feed_checks']=feed;r['not_received_after_falsifier']=['logicclosed-socket material/retention tests','changednearbyretainedparttests','wholeconditionalrelease'];r['native_pid']=8920
  intersection.exportBrep(str(P/'feed-entry-blocker.brep'))
  (P/'result.json').write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
  print(json.dumps({'status':r['status'],'joint_checks':out,'first_falsifier':r['first_falsifier'],'feeds_received':feed}))
  break

 feed.append(dict(pocket=i,actual_nut_washer_continuous_loading_cover_common_mm3=c,feed_length_mm=L,phase='PRELOAD ON BENCH before frame/electronics; no rigid operatingpart omitted',valid=True))

