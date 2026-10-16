"""Read just missing retained instance datums, no whole-robot recompute."""
import json,time
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,prop,sha
from build_phase1_source_mounts import signature
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype';OUT=BASE/'functional-protection'
def run():
 r=SavedShapes();tail=BASE/'tail-mount-checkpoint/TailAssemblyCurrent.FCStd';x=r.doc(tail)
 f=ROOT/'hardware/cad/assembly/RobotCatNarrowRimEars.FCStd';p=r.doc(f);frame=r.shape(f,'FrameRear20');frame.Placement=r.placement(p['Rigid_FrameRear20'])*frame.Placement
 rows=[]
 for n in ['TailRiser'+str(i) for i in range(1,5)]:
  s=r.shape(tail,n);assert s.isValid();b=s.optimalBoundingBox();contact=s.distToShape(frame)[0]
  plane=Part.makeBox(b.XLength,b.YLength,.1,A.Vector(b.XMin,b.YMin,b.ZMin-.1));bearing=frame.common(plane).Volume/.1
  rows.append(dict(identity='CP2:TailRiser',native=tail.relative_to(ROOT).as_posix(),object=n,signature=signature(s),frame_distance_mm=contact,frame_bearing_area_mm2=bearing))
 print('Tailrisers',json.dumps(rows),flush=True)
 files={'battery_carrier':ROOT/'hardware/cad/studies/battery-p0/r4/electronics/BatteryCarrierP0.FCStd',
  'battery_plate':ROOT/'hardware/cad/studies/battery-p0/r4/chassis/BottomPlateP0.FCStd',
  'retainer':ROOT/'hardware/cad/studies/battery-p0/r6/BatteryNutRetainerP0.FCStd'}
 parts=[]
 for key,file in files.items():
  objs=r.doc(file)
  for n,o in objs.items():
   if n not in ('Carrier','Plate','Retainer') and not n.lower().startswith(('pack','battery','strap','liner')):continue
   try:s=r.shape(file,n)
   except ValueError:continue
   parts.append(dict(role=key,name=n,label=prop(o,'Label')[0].get('value'),source=file.relative_to(ROOT).as_posix(),signature=signature(s)))
 result=dict(status='READ_RETAINED_ADDITION_DATUMS',tail_risers=rows,battery_parts=parts,source_sha256=r.hashes)
 (OUT/'full-addition-datums.json').write_text(json.dumps(result,indent=2)+'\n');print('Batteryparts',json.dumps(parts),flush=True)
if __name__=='__main__':run()
