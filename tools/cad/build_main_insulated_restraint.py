"""Editable replacement MAINGrip only; no copy of the whole power module."""
import json,time,tempfile,shutil
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
from phase1_source_protection import ROOT,BASE,BODY,OUT,check,sha
from plan_main_insulated_restraint import grip_recipe,grip_shape
from plan_u1_power_grips import AXES
from build_phase1_source_mounts import rectangle,disk,bores,qualified
from phase1_stl_preflight import inspect,fit

MODEL=OUT/'MAINInsulatedGripCurrent.FCStd'
def run():
 check();tick=time.monotonic();file=OUT/'MAIN-insulated-restraint-plan.json';p=json.loads(file.read_text())
 assert p['status']=='MAIN_INSULATED_RESTRAINT_NOMINAL_SPACE_CLEAR_NATIVE_PENDING' and not p['contacts']
 for n,h in p['source_sha256'].items():assert sha(ROOT/n)==h,n
 assert not MODEL.exists(),'Receive existing native before rebuild'
 d=A.newDocument('MAINInsulatedGripCurrent');par=d.addObject('App::VarSet','GripParameters')
 par.addProperty('App::PropertyLength','MainRailThickness');par.MainRailThickness=2
 b=d.addObject('PartDesign::Body','MAINGripInsulatedCurrent');rows,band,head=grip_recipe()
 priority=['Foot0','FootRoot0','Post0','Rail','FootRoot1','Foot1','Post1','TopReturn','InsulationSeat']
 rows.sort(key=lambda r:priority.index(r['name']))
 for r in rows:
  if r.get('kind')=='disc':
   x,y,z=r['centre_mm'];disk(b,r['name'],z,x,y,2*r['radius_mm'],r['height_mm'])
  else:
   x,y,z,X,Y,Z=r['bounds_mm'];rectangle(b,r['name'],z,x,y,X-x,Y-y,'GripParameters.MainRailThickness' if r['name']=='Rail' else Z-z)
 bores(b,'RetainedBoardAxes',65,AXES,2.4,20)
 expected,_,_=grip_shape();delta=b.Shape.copy().cut(expected.copy()).Volume+expected.copy().cut(b.Shape.copy()).Volume;assert delta<1e-5,delta
 for n,s in [('MAINBandInsulated',band),('MAINLockRetained',head)]:
  o=d.addObject('Part::Feature',n);o.Shape=s;o.addProperty('App::PropertyString','Scope');o.Scope='Nominal T18R envelope, hand tension/unpowered retention gate; not a print'
 for n in ('W079','W080','W060','W078'):
  s=Part.Shape();s.read(str(OUT/('Sleeve_'+n+'.brep')));o=d.addObject('Part::Feature','MAINNeckSleeve_'+n);o.Shape=s
  o.addProperty('App::PropertyString','FitGate');o.FitGate=p['fit_gate']
 baseline=qualified(d,[b.Name]);d.saveAs(str(MODEL));print('MAIN grip saved before parameter',flush=True)
 par.MainRailThickness=2.2;changed=qualified(d,[b.Name]);assert changed[b.Name][0]>baseline[b.Name][0]
 par.MainRailThickness=2;restored=qualified(d,[b.Name]);assert max(abs(a-z) for a,z in zip(baseline[b.Name],restored[b.Name]))<1e-5
 d.save();s=b.Shape.copy();bb=s.optimalBoundingBox();s.translate(A.Vector(-bb.XMin,-bb.YMin,-bb.ZMin))
 export=OUT/'MAINGripInsulatedCurrent_x1.stl';MeshPart.meshFromShape(Shape=s,LinearDeflection=.04,AngularDeflection=.15,Relative=False).write(str(export))
 measured=inspect(export.read_bytes());assert measured['closed'] and measured['components']==1 and fit(measured['size_mm'])
 A.closeDocument(d.Name)
 with tempfile.TemporaryDirectory(prefix='cat-main-insulated-') as td:
  moved=Path(td)/MODEL.name;shutil.copy2(MODEL,moved);d=A.openDocument(str(moved));again=qualified(d,['MAINGripInsulatedCurrent'])
  assert max(abs(a-z) for a,z in zip(again['MAINGripInsulatedCurrent'],baseline['MAINGripInsulatedCurrent']))<1e-5
  A.closeDocument(d.Name)
 result=dict(status='MAIN_INSULATED_GRIP_NATIVE_PARAMETER_REOPEN_STL_COMPLETE',selected=False,physical_pass=False,
  native=MODEL.relative_to(ROOT).as_posix(),native_sha256=sha(MODEL),
  part=dict(identity='MAINGrip',part='MAINGrip',native=MODEL.relative_to(ROOT).as_posix(),native_object='MAINGripInsulatedCurrent',
   path=export.relative_to(ROOT).as_posix(),sha256=sha(export),quantity=1,printing=dict(**measured,rotation_quaternion=[0,0,0,1],brim_each_mm=5,fits_with_5mm_brim=True)),
  parameter_mm=[2,2.2,2],relocated_reopen=True,all_sketches_fully_constrained=True,material_symmetric_difference_mm3=delta,
  no_new_ties_or_metal=True,source_sha256={file.relative_to(ROOT).as_posix():sha(file),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
  worker_seconds=round(time.monotonic()-tick,3))
 (OUT/'MAIN-insulated-grip-native.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':run()
