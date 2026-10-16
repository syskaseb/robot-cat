"""Changed source hardware and explicit bench tool sequence, not live service."""
import json,time,math
from pathlib import Path
import FreeCAD as A
import Part
from phase1_source_protection import ROOT,BASE,BODY,OUT,scene,check,sha,cyl,hexnut
from check_source_contact_insulation import bounded_distance

def run():
 check();tick=time.monotonic();reader,targets,wires=scene()
 targets.pop('UpperFrame8Screw/0/0');targets.pop('UpperFrame8TopWasher/0/0')
 for key,name in [('S0MountFoundation','S0MountFoundation'),('S1MountCurrent','S1MountCurrent')]:
  s=Part.Shape();s.read(str(OUT/(name+'.brep')));targets[key]=s
 new={'S1SharedFrameScrew':cyl(138,30,33.5,1.5,48.7).fuse(Part.makeCone(1.5,2.8,1.3,A.Vector(138,30,82.2)))}
 for x in (-96,-58):
  suffix=str(abs(x));new['S0M6_'+suffix]=cyl(x,16,89,3,20).fuse(cyl(x,16,109,5,6))
  for n,z in [('top',107.4),('lower',99.4)]:new['S0Washer_'+suffix+n]=cyl(x,16,z,6,1.6).cut(cyl(x,16,z,3.2,1.6))
  new['S0Nut_'+suffix]=hexnut(x,16,94.4,10,5).cut(cyl(x,16,94.3,3,5.2))
 report=dict(status='PENDING',selected=False,physical_pass=False,contacts=[],supplier_interface_gates=[],pairs=0,
  S1_stack=dict(head_top_mm=83.5,tip_mm=33.5,nut_bottom_mm=36.82,nut_top_mm=39.22,protrusion_mm=3.32,
   product='Wurth0048350 DIN965M3x50 PH1 partialthread',delivered_tip_thread_min_mm=6,
   remove=['UpperFrame8Screw/0/0','UpperFrame8TopWasher/0/0']),
  S0_stack=dict(M6x20=2,washer_OD12_ID6p4_t1p6=4,nut_AF10_h5=2,project_flange_mm=4,flange_max_for_one_pitch_protrusion_mm=8.4,
   gate='Actual flange thickness/key/stud clock unknown. Published mount pattern only; delivered body/hardware fit must be verified unplugged, do not infer a hollow bolt bay from filled reservation.'),
  tool_sequence=[dict(tool='Project PH1 OD5x60',from_xyz=[138,30,83.7],stage='Frame joint before S1 case and before fixing the loose wires. Not assembled hot service.'),
    dict(tool='M6 AF5 and AF10',stage='Source S0 mounted on static Foundation on bench before head/looms; support key OFF/remove key. Actual delivered flange recess access gate.')])
 for n,s in new.items():
  assert s.isValid() and len(s.Solids)==1 and not s.check(True)
  for m,t in [*targets.items(),*[(m,t) for m,t in new.items() if m<n]]:
   if not s.BoundBox.intersect(t.BoundBox):continue
   check();report['pairs']+=1;q=s.copy().common(t.copy());assert q.isNull() or q.isValid(),(n,m)
   if q.Volume>1e-5:
    row=dict(a=n,b=m,volume_mm3=q.Volume)
    if n.startswith('S0') and m.startswith(('S0_body_CP2/','S0_neck_CP2/','S0_key_CP2/')):report['supplier_interface_gates'].append(row)
    else:report['contacts'].append(row)
  for m,(c,r) in wires.items():
   b=s.BoundBox;b.enlarge(r)
   if not b.intersect(c.BoundBox):continue
   check();report['pairs']+=1;d=bounded_distance(s,c,r)
   if d<r-1e-6:report['contacts'].append(dict(a=n,b=m,distance_mm=d,required_mm=r))
  s.exportBrep(str(OUT/(n+'.brep')))
 # Assembly driver excludes only the explicitly NOT YET installed S1 case,
 # its own screw, and loose conductors. All remaining material stays present.
 driver=cyl(138,30,83.7,2.5,60)
 for m,t in targets.items():
  if m.startswith(('current/S1_body_CP2/','current/S1_control_CP2/')) or not driver.BoundBox.intersect(t.BoundBox):continue
  check();report['pairs']+=1;q=driver.copy().common(t.copy());assert q.isNull() or q.isValid(),m
  if q.Volume>1e-5:report['contacts'].append(dict(a='PH1BenchDriver',b=m,volume_mm3=q.Volume))
 report['status']='SOURCE_HARDWARE_BENCH_SEQUENCE_NOMINAL_CLEAR' if not report['contacts'] else 'SOURCE_HARDWARE_REJECTED'
 report['source_sha256']={**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))}
 report['worker_seconds']=round(time.monotonic()-tick,3)
 (OUT/'source-hardware-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
if __name__=='__main__':run()
