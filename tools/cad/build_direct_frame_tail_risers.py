"""One editable direct-frame riser and4installed links; no copied chassis."""
import json,time,tempfile,shutil
from pathlib import Path
import FreeCAD as A
import Part,MeshPart
from phase1_source_protection import ROOT,BASE,OUT,check,sha
from open_deck_p0_supports import sketch,feature
from open_deck_p0_plate import circle
from phase1_stl_preflight import inspect,fit

MODEL=OUT/'DirectFrameTailRisers.FCStd'
def qualify(d):
 d.recompute();b=d.DirectFrameRiser
 assert b.Shape.isValid() and len(b.Shape.Solids)==1 and not b.Shape.check(True)
 assert d.RiserPlan.solve()==0 and d.RiserPlan.FullyConstrained
 z=37.02+d.RiserParameters.Height.Value
 assert abs(d.TailTopDatum.Placement.Base.z-z)<1e-6
 for i in range(1,5):assert abs(d.getObject('TailRiser'+str(i)).Shape.optimalBoundingBox().ZMax-z)<1e-6
 return b.Shape.Volume
def run():
 check();tick=time.monotonic();file=OUT/'direct-frame-tail-risers-plan.json';p=json.loads(file.read_text())
 assert p['status']=='FOUR_DIRECT_FRAME_TAIL_RISERS_SPACE_CLEAR_NATIVE_PENDING' and not p['contacts']
 for n,h in p['source_sha256'].items():assert sha(ROOT/n)==h,n
 assert not MODEL.exists(),'Receive existing result before rebuild'
 d=A.newDocument('DirectFrameTailRisers');par=d.addObject('App::VarSet','RiserParameters')
 par.addProperty('App::PropertyLength','Height');par.Height=20.5
 b=d.addObject('PartDesign::Body','DirectFrameRiser');s=sketch(b,'RiserPlan',0);circle(s,0,0,7);circle(s,0,0,2.6)
 b.Tip=feature(b,'Pad','RiserHeight',s,'RiserParameters.Height')
 for i,(x,y) in enumerate(p['axes_xy_mm'],1):
  o=d.addObject('App::Link','TailRiser'+str(i));o.LinkedObject=b;o.LinkPlacement=A.Placement(A.Vector(x,y,37.02),A.Rotation())
 datum=d.addObject('PartDesign::Plane','TailTopDatum');datum.setExpression('Placement.Base.z','37.02 mm + RiserParameters.Height')
 datum.addProperty('App::PropertyString','MatingSource');datum.MatingSource='Same upper tail/bottom-carrier57.52datum. Four frameside bolt axes unchanged; Part__Feature038 NOT required.'
 original=qualify(d);d.saveAs(str(MODEL));par.Height=20.7;changed=qualify(d);assert changed>original
 par.Height=20.5;assert abs(qualify(d)-original)<1e-5;d.save()
 exp=OUT/'DirectFrameTailRiser_x4.stl';MeshPart.meshFromShape(Shape=b.Shape,LinearDeflection=.04,AngularDeflection=.15,Relative=False).write(str(exp))
 q=inspect(exp.read_bytes());assert q['closed'] and q['components']==1 and fit(q['size_mm']);A.closeDocument(d.Name)
 with tempfile.TemporaryDirectory(prefix='cat-direct-risers-') as td:
  f=Path(td)/MODEL.name;shutil.copy2(MODEL,f);d=A.openDocument(str(f));assert abs(qualify(d)-original)<1e-5;A.closeDocument(d.Name)
 result=dict(status='DIRECT_FRAME_TAIL_RISERS_NATIVE_PARAMETER_REOPEN_STL_COMPLETE',selected=False,physical_pass=False,
  native=MODEL.relative_to(ROOT).as_posix(),native_sha256=sha(MODEL),
  part=dict(identity='CP2:TailRiser',part='CP2:TailRiser',quantity=4,native=MODEL.relative_to(ROOT).as_posix(),native_object='DirectFrameRiser',
   installed_objects=['TailRiser'+str(i) for i in range(1,5)],path=exp.relative_to(ROOT).as_posix(),sha256=sha(exp),
   printing=dict(**q,rotation_quaternion=[0,0,0,1],brim_each_mm=5,fits_with_5mm_brim=True)),
  parameter_mm=[20.5,20.7,20.5],linked_instances_update=True,mating_top_datum_updates=True,relocated_reopen=True,
  no_new_hardware=True,existing_M2x30_stack_total_unchanged='20.5mm riser replaces19mm riser plus missing1.5mm obsoleteplate; same top57.52, same underhead/shaft/nut datums',
  source_sha256={**p['source_sha256'],file.relative_to(ROOT).as_posix():sha(file),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
 (OUT/'direct-frame-tail-risers-native.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':run()
