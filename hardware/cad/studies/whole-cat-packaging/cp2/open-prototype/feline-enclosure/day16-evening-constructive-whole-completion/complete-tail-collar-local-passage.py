import FreeCAD as A,FreeCADGui as G,Part,json,math
from pathlib import Path
D=A.ActiveDocument;V=A.Vector;P=Path(__file__).parent;C=V(185,0,154)
def sector(r,lo,hi,y0,y1):
 def q(a):return V(185+r*math.cos(math.radians(a)),y0,154+r*math.sin(math.radians(a)))
 c=V(185,y0,154)
 w=Part.Wire([Part.makeLine(c,q(lo)),Part.Arc(q(lo),q((lo+hi)/2),q(hi)).toShape(),Part.makeLine(q(hi),c)])
 return Part.Face(w).extrude(V(0,y1-y0,0))
def bounds(s):
 b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
# Functional open C-collar integrated into the already removable outer-race cap; no extra layer under screw head.
cap=D.getObject('TAIL_FIXED_OUTER_RACE_CAP').Shape.copy()
collar=sector(13.5,105,290,-4,19.5).cut(Part.makeCylinder(9.5,23.5,V(185,-4,154),V(0,1,0)))
newcap=cap.fuse(collar)
D.getObject('TAIL_FIXED_OUTER_RACE_CAP').Shape=newcap
# Continuous occupied cover of retained rotating material: hub cylinder + angular interval covers of neck and upper tube.
root=D.getObject('TAIL_ROTATING_HOLLOW_REAL_ROOT').Shape
hub=Part.makeCylinder(7,6,V(185,0,154),V(0,1,0))
# Polar intervals from constructive neck polygon and actual retained tube bounds. 15deg prototype pitch chosen once.
neckpts=[(190,150),(197,152),(211,160),(214,168),(201,175),(190,160)]
phis=[math.degrees(math.atan2(z-154,x-185)) for x,z in neckpts];rmax=max(math.hypot(x-185,z-154) for x,z in neckpts)
neckcover=sector(rmax,min(phis)-15,max(phis)+15,0,16)
# Tail upper bound contains all retained tube points in XZ; +Y side plane preserved. This is conservative, not delivered material.
b=root.BoundBox;upperr=math.hypot(b.XMax-185,b.ZMax-154)
uppercover=sector(upperr,math.degrees(math.atan2(6,b.XMax-185))-15,math.degrees(math.atan2(b.ZMax-154,10.6177))+15,2.86,17.15)
cover=Part.makeCompound([hub,neckcover,uppercover]);o=D.addObject('PartDesign::Feature','YTAIL_CONTINUOUS_LOCAL_MOTION_COVER_NOT_PRINT');o.Shape=cover;o.ViewObject.Transparency=75;o.ViewObject.ShapeColor=(0.9,0.5,0.1)
# Clearance passage around actual moving tube at the body seam Y10. Only new rear skin material changed.
clear_hub=Part.makeCylinder(8.25,8.5,V(185,-1.25,154),V(0,1,0))
clear_neck=sector(rmax+1.25,min(phis)-15-11.3,max(phis)+15+11.3,-1.25,17.25)
clear_upper=sector(upperr+1.25,math.degrees(math.atan2(6,b.XMax-185))-15-6.3,math.degrees(math.atan2(b.ZMax-154,10.6177))+15+6.3,1.61,18.4)
# Gap cuts are explicit local clearance operands, not whole outer-BBox air cuts; foundation/root region below90 protected.
changes=[]
for n in ['CLOSED_BODY_rear_negative','CLOSED_BODY_rear_positive']:
 obj=D.getObject(n);old=obj.Shape.copy();new=old
 for clearance in [clear_hub,clear_neck,clear_upper]:
  if new.BoundBox.intersect(clearance.BoundBox):new=new.cut(clearance)
 obj.Shape=new;protect=old.common(Part.makeBox(500,300,90,V(-250,-150,0)))
 changes.append(dict(name=n,removed_clearance_mm3=old.Volume-new.Volume,protected_under90_missing_mm3=protect.cut(new).Volume,valid=new.isValid(),solids=len(new.Solids)))
D.recompute();D.save()
# Nominal assembly and motion; no global poses or new fixed wire axes.
rows=[]
for angle in [-15,0,15]:
 s=root.copy();s.rotate(C,V(0,1,0),angle)
 tip=C+A.Rotation(V(0,1,0),angle).multVec(V(233,10,214)-C)
 row={'pitch_deg':angle,'tail_tip_xyz':[tip.x,tip.y,tip.z],'delta_z':tip.z-214,'fixed_frame_common':s.common(D.getObject('P07_open_tail_root_U').Shape).Volume,'cap_guard_common':s.common(newcap).Volume,'skin_common':sum(s.common(D.getObject(n).Shape).Volume for n in ['CLOSED_BODY_rear_negative','CLOSED_BODY_rear_positive'])}
 rows.append(row)
r={'range_deg':[-15,15],'authority':'one provisional useful prototype range from Y-separated fixed/moving layer and local continuous passage; not supplier travel or calibration','axis':[0,1,0],'axis_point':[185,0,154],'tip_rest':[233,10,214],'poses':rows,'cap_collar':{'valid':newcap.isValid(),'solids':len(newcap.Solids),'source_cap_missing':cap.cut(newcap).Volume,'positive_join_mm3':cap.common(collar).Volume,'open_sector_deg':[-70,105],'existing_full_cap_sets_unchanged':True},'skin_changes':changes,'continuous_cover':'hub exact; angular polar bounds neck/tube include all points and full ±15; slot cut adds1.25 clearance; no all-world motion claim','assembly':['P07 seated source base4M3 first; full servo in saddle with original ears and complete twoM2 sets','outer bearing608 and retained original axial shoulder, fit removable C-cap+two existingM2 before moving root','factory horn + original center screw before formkey halves and journal; no spline claim','install real root on journal through C-slot, retain full crosspin/nut/2washers; no extra thickness under source screw','rear skin halves close around Y10 moving tail plane after whole flexible lead handlay; no virtual tail detach'],'OPEN':['actual MG/horn/bearing FIT3 and servo calibration','whole complete key/horn hardware continuous motion check not inferred from curved tube cover','C-collar/body edge attachment and all closure fasteners not final print release','source servo lead actual length and exit; planned fixed route stays on nonrotating saddle']}
(P/'tail-pitch-collar-passage-and-assembly.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
print(json.dumps(r))
