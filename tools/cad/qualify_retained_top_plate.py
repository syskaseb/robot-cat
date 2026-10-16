"""Restore the retained CP2 structural top plate to the manufacturing set.

Not new CAD: geometry already present in the accepted W5 context and explicitly
used in retained tail root proof. Historical walking DeckR2 retired this print;
CP2 uses the original1.5mm plate beneath four19mm tail risers instead.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
from check_main_p0_placement import ROOT,SavedShapes,prop,sha
from current_work_guard import check
from phase1_stl_preflight import inspect,fit
from build_phase1_source_mounts import signature
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype';OUT=BASE/'functional-protection'
def run():
 check();tick=time.monotonic();r=SavedShapes();source=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd';x=r.doc(source)
 s=r.shape(source,'Part__Feature038');s.Placement=r.placement(x['Rigid_Part__Feature038'])*s.Placement
 assert s.isValid() and len(s.Solids)==1 and not s.check(True);plate=s.copy();contacts=[]
 tail=BASE/'tail-mount-checkpoint/TailAssemblyCurrent.FCStd'
 for i in range(1,5):
  n='TailRiser'+str(i);t=r.shape(tail,n);b=t.optimalBoundingBox();gap=t.distToShape(plate)[0]
  probe=Part.makeBox(b.XLength,b.YLength,.1,A.Vector(b.XMin,b.YMin,b.ZMin-.1));area=plate.common(probe).Volume/.1
  overlap=t.common(plate).Volume;assert gap<1e-6 and overlap<1e-5 and area>30,(n,gap,area,overlap)
  contacts.append(dict(instance=n,actual_bottom_z_mm=b.ZMin,gap_mm=gap,bearing_area_mm2=area,overlap_mm3=overlap))
 b=s.optimalBoundingBox();s.translate(A.Vector(-b.XMin,-b.YMin,-b.ZMin));file=OUT/'P0RetainedTopPlate_x1.stl'
 MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False).write(str(file))
 measured=inspect(file.read_bytes());assert measured['closed'] and measured['components']==1 and fit(measured['size_mm'])
 result=dict(status='RETAINED_TOP_PLATE_FOUR_TAIL_BEARINGS_EXPORT_COMPLETE',selected=False,physical_pass=False,
  part=dict(identity='P0-BASE-TOP-PLATE-CP2',part='P0-BASE-TOP-PLATE-CP2',quantity=1,native=source.relative_to(ROOT).as_posix(),native_object='Part__Feature038',
   world_wrapper='Rigid_Part__Feature038',native_editability='Inherited saved source snapshot, not claimed a newly migrated parametric plate',path=file.relative_to(ROOT).as_posix(),sha256=sha(file),
   printing=dict(**measured,rotation_quaternion=[0,0,0,1],brim_each_mm=5,fits_with_5mm_brim=True)),
  bearings=contacts,source_signature=signature(plate),
  source_sha256={**r.hashes,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
 (OUT/'retained-top-plate.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':run()
