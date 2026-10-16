"""Actual retained topplate versus current CP2 neighbors before full assembly."""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,prop,sha
from check_source_contact_insulation import bounded_distance
from phase1_source_protection import scene,check,OUT,BASE
def run():
 check();tick=time.monotonic();r,targets,wires=scene();p0=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd';x=r.doc(p0)
 s=r.shape(p0,'Part__Feature038');s.Placement=r.placement(x['Rigid_Part__Feature038'])*s.Placement
 report=dict(status='PENDING',selected=False,physical_pass=False,contacts=[],pairs=0,errors=[])
 for n,t in targets.items():
  if n=='head/0/0/Foundation/0/0':continue # retired duplicate of current Foundation
  if not s.BoundBox.intersect(t.BoundBox):continue
  check();report['pairs']+=1;q=s.copy().common(t.copy());assert q.isNull() or q.isValid(),n
  if q.Volume>1e-5:report['contacts'].append(dict(part=n,volume_mm3=q.Volume))
 for n,(c,rad) in wires.items():
  if n.startswith('wire/head/local/') and n.split('/')[-1] in ('+15','-15'):continue
  b=s.BoundBox;b.enlarge(rad)
  if not b.intersect(c.BoundBox):continue
  check();report['pairs']+=1;gap=bounded_distance(s,c,rad)
  if gap<rad-1e-6:report['contacts'].append(dict(wire=n,distance_mm=gap,required_mm=rad))
 report.update(status='RETAINED_TOP_PLATE_CURRENT_SHARED_SPACE_CLEAR' if not report['contacts'] else 'RETAINED_TOP_PLATE_CURRENT_REJECTED',
  source_sha256={**r.hashes,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
 (OUT/'retained-top-plate-current-space.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':run()
