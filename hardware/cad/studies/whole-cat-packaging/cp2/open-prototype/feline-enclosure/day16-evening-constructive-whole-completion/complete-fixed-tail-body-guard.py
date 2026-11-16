import FreeCAD as A,Part,json,math
from pathlib import Path
D=A.ActiveDocument;P=Path(__file__).parent;V=A.Vector
# Complete same tail/body interface: local fixed guard derived from all real stationary bounding surfaces.
# Source receiver material below90 remains untouched; no change to bought servo or frame.
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def sector(r,lo,hi,y0,y1):
 def q(a):return V(185+r*math.cos(math.radians(a)),y0,154+r*math.sin(math.radians(a)))
 c=V(185,y0,154);return Part.Face(Part.Wire([Part.makeLine(c,q(lo)),Part.Arc(q(lo),q((lo+hi)/2),q(hi)).toShape(),Part.makeLine(q(hi),c)])).extrude(V(0,y1-y0,0))
outer=box(192,-69,90,25,93,93);inner=box(189.5,-66.6,92.4,25.1,88.2,88.2)
pod=outer.cut(inner)
# Explicit ordinary local feed reliefs around actual retained lower beam/right rear web, not whole ring/air BBox.
reliefs=[box(165.75,-51.85,83.75,48.5,45.1,8.5),box(205.75,-51.85,88.75,8.5,5.6,82.5)]
for s in reliefs:pod=pod.cut(s)
root=D.getObject('TAIL_ROTATING_HOLLOW_REAL_ROOT').Shape;b=root.BoundBox
phis=[math.degrees(math.atan2(z-154,x-185)) for x,z in [(190,150),(197,152),(211,160),(214,168),(201,175),(190,160)]]
rmax=max(math.hypot(x-185,z-154) for x,z in [(190,150),(197,152),(211,160),(214,168),(201,175),(190,160)])
clear=[Part.makeCylinder(8.25,8.5,V(185,-1.25,154),V(0,1,0)),sector(rmax+1.25,min(phis)-26.3,max(phis)+26.3,-1.25,17.25),sector(math.hypot(b.XMax-185,b.ZMax-154)+1.25,math.degrees(math.atan2(6,b.XMax-185))-21.3,math.degrees(math.atan2(b.ZMax-154,10.6177))+21.3,1.61,18.4)]
res=[]
for n,y0,y1 in [('CLOSED_BODY_rear_negative',-150,10),('CLOSED_BODY_rear_positive',10,150)]:
 o=D.getObject(n);old=o.Shape.copy();patch=pod.common(box(180,y0,85,50,y1-y0,110));new=old.fuse(patch)
 # Replaces original rear wall inside fixed guard, keeps material below90 and all old base receiver functions.
 new=new.cut(inner)
 for s in clear:new=new.cut(s)
 o.Shape=new
 protected=old.common(box(-250,-150,0,500,300,90))
 res.append(dict(name=n,valid=new.isValid(),solids=len(new.Solids),protected_receiver_missing=protected.cut(new).Volume,old_volume=old.Volume,new_volume=new.Volume))
D.recompute();D.save()
checks=[]
for a in ['P07_open_tail_root_U','MG92B_Tail','TAIL_FIXED_OUTER_RACE_CAP']:
 s=D.getObject(a).Shape
 for n in ['CLOSED_BODY_rear_negative','CLOSED_BODY_rear_positive']:
  t=D.getObject(n).Shape
  if s.BoundBox.intersect(t.BoundBox):checks.append(dict(a=a,b=n,common=s.common(t).Volume,gap=s.distToShape(t)[0]))
report={'guard_outer':[192,-69,90,217,24,183],'derived_bounds':'X217 >=P07max213+1.25+2.4; Ymin-69 <=MGmin-64.8-1.25-2.4; Ymax24 >=capcollar19.5+1.25+2.4','two_real_prints':'pod integral in each respective body half; seamY10 retained; existing six receiver roots below90 retained','intentional_local_passages':'tail moving polar clearance and actual lowerbeam/rightweb relief, not purchased cuts','parts':res,'stationary_changed_pairs':checks,'print_release':False}
(P/'tail-fixed-guard-and-real-body-parting.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print(json.dumps(report))
