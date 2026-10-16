"""One direct-frame root for all4tail risers, same upper tail world datums.

No whole historical topplate and no cutout series. The1.5mm missing obsolete
plate is absorbed in four complete20.5mm risers; top57.52 and bolt axes stay.
"""
import json,time,math
from pathlib import Path
import FreeCAD as A
import Part
from phase1_source_protection import ROOT,BASE,BODY,OUT,SCENE,scene,check,sha
from check_main_p0_placement import SavedShapes
from check_source_contact_insulation import bounded_distance
def riser(x,y):return Part.makeCylinder(3.5,20.5,A.Vector(x,y,37.02)).cut(Part.makeCylinder(1.3,20.5,A.Vector(x,y,37.02)))
def run():
 check();tick=time.monotonic();reader,targets,wires=scene();source=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd';p0=reader.doc(source)
 frame=reader.shape(source,'FrameRear20');frame.Placement=reader.placement(p0['Rigid_FrameRear20'])*frame.Placement
 report=dict(status='PENDING',selected=False,physical_pass=False,contacts=[],pairs=0,bearings=[],axes_xy_mm=[[x,y] for x in (112,122) for y in (-22.5,22.5)],height_mm=20.5,bottom_mm=37.02,top_mm=57.52)
 for i,(x,y) in enumerate(report['axes_xy_mm'],1):
  s=riser(x,y);assert s.isValid() and len(s.Solids)==1 and not s.check(True)
  gap=s.distToShape(frame)[0];area=frame.common(Part.makeCylinder(3.5,.1,A.Vector(x,y,36.92))).Volume/.1
  assert gap<1e-6 and s.common(frame).Volume<1e-5 and area>20,(i,gap,area)
  report['bearings'].append(dict(instance=i,frame_distance_mm=gap,bearing_area_mm2=area))
  for n,t in targets.items():
   if not s.BoundBox.intersect(t.BoundBox):continue
   check();report['pairs']+=1;q=s.copy().common(t.copy());assert q.isNull() or q.isValid(),n
   if q.Volume>1e-5:report['contacts'].append(dict(instance=i,part=n,volume_mm3=q.Volume))
  for n,(c,r) in wires.items():
   b=s.BoundBox;b.enlarge(r)
   if not b.intersect(c.BoundBox):continue
   check();report['pairs']+=1;gap=bounded_distance(s,c,r)
   if gap<r-1e-6:report['contacts'].append(dict(instance=i,wire=n,distance_mm=gap,required_mm=r))
  s.exportBrep(str(OUT/('DirectTailRiser'+str(i)+'.brep')))
 report.update(status='FOUR_DIRECT_FRAME_TAIL_RISERS_SPACE_CLEAR_NATIVE_PENDING' if not report['contacts'] else 'DIRECT_FRAME_TAIL_RISERS_REJECTED',
  source_sha256={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
 (OUT/'direct-frame-tail-risers-plan.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':run()
