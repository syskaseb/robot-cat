import FreeCAD as A, FreeCADGui as G, Part,json,math
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent
pivot=V(185,0,154);rot=A.Rotation(V(1,0,0),-90)
T=A.Placement(pivot-rot.multVec(pivot),rot)
def box(x,y,z,l,w,h):return Part.makeBox(l,w,h,V(x,y,z))
def shape(n):return D.getObject(n).Shape.copy()
def bb(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def add(n,s,col):
 o=D.addObject('PartDesign::Feature',n);o.Shape=s;o.ViewObject.ShapeColor=col;return o
rows=[];original_tail=shape('TAIL_ROTATING_HOLLOW_REAL_ROOT')
for o in D.Objects:
 if hasattr(o,'Shape') and (o.Name.startswith('TAIL_') or o.Name in ['MG92B_Tail','Tail608']):
  old=o.Shape.copy();o.Placement=T.multiply(o.Placement)
  rows.append({'name':o.Name,'before':bb(old),'after':bb(o.Shape),'volume_delta':o.Shape.Volume-old.Volume,'rigid_axis_mapping':[0,1,0]})
# Operating curved upper tail stays in the original XZ silhouette; only its journal shoe changes orientation.
rotated_lower=D.getObject('TAIL_ROTATING_HOLLOW_REAL_ROOT').Shape.common(Part.makeCylinder(8,6,V(185,0,154),V(0,1,0)))
upper=original_tail.common(box(165,-20,160,100,40,100))
hub=Part.makeCylinder(7,6,V(185,0,154),V(0,1,0)).cut(Part.makeCylinder(4.05,6,V(185,0,154),V(0,1,0)))
web=box(181,-4,155,12,10,14)
new=upper.fuse(hub).fuse(web)
# Crosspin clearance is copied from the already modelled complete full pin axis, not invented spline.
new=new.cut(Part.makeCylinder(1.1,25,V(185,3,140),V(0,0,1)))
o=D.getObject('TAIL_ROTATING_HOLLOW_REAL_ROOT');o.Placement=A.Placement();o.Shape=new
# P07 bottom remains at its real foundation interface; its old vertical towers are replaced by horizontal-axis support.
old=shape('P07_open_tail_root_U');base=old.common(box(150,-50,50,80,100,39.2))
members=[base,box(164,-35,85,6,7,63),box(203,-35,85,6,7,63),box(164,-35,137,45,19,6)]
frame=members[0]
for m in members[1:]:frame=frame.fuse(m)
o=D.getObject('P07_open_tail_root_U');o.Shape=frame
# Side cheek links receiver to retained cartridge on its fixed outer-race body, not rotating journal.
links=[box(164,-20,134,6,8,14),box(203,-20,134,6,8,14)]
for i,s in enumerate(links):add('YTAIL_FIXED_RECEIVER_LINK_'+str(i),s,(0.35,0.55,0.7))
# No body-cut is claimed: existing Z-opening remains a named changed-interface gate.
pts=[v.Point for v in upper.Vertexes];tip=max(pts,key=lambda q:q.z)
poses=[]
for a in [-12,0,12]:
 r=A.Rotation(V(0,1,0),a);q=pivot+r.multVec(tip-pivot)
 s=new.copy();s.rotate(pivot,V(0,1,0),a)
 poses.append(dict(angle_deg=a,tip_xyz=[q.x,q.y,q.z],delta_z=q.z-tip.z,bounds=bb(s)))
result={'axis':[0,1,0],'axis_point':[185,0,154],'prototype_range_deg':[-12,12],'range_status':'PROJECT_PROVISIONAL_NOT_SERVO_CALIBRATION','rest_tip_sample':[tip.x,tip.y,tip.z],'poses':poses,'rigid_transforms':rows,'rotating_root':{'valid':new.isValid(),'solids':len(new.Solids),'volume':new.Volume,'upper_retained_missing':upper.cut(new).Volume,'hub_web_join_mm3':hub.common(web).Volume,'upper_web_join_mm3':upper.common(web).Volume},'fixed_support':{'valid':frame.isValid(),'solids':len(frame.Solids),'members_missing':[m.cut(frame).Volume for m in members]},'OPEN':['receiver links actual cartridge contacts','complete source hardware and shell passage','factory horn/bearing FIT3','connected servo lead movement reserve']}
(P/'tail-Y-architecture-and-tip-motion.json').write_text(json.dumps(result,indent=2))
D.Label='DAY16 EVENING WHOLE RECOVERY - UNSELECTED - NOT PRINT RELEASE';D.recompute();D.save()
print(json.dumps({'tail_axis':result['axis'],'poses':poses,'root':result['rotating_root'],'support':result['fixed_support']}))
