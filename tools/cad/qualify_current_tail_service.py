"""Exact bare-rail30mm vertical removal and redundant sleeve cleanup.

For a body made only from vertical extrusions, upward horizontal boundary
faces extruded by30mm plus the original body cover its continuous translation.
No attached deformable-wire motion is inferred from this printed-part test.
"""
import json,time,shutil,tempfile
from pathlib import Path
import receive_current_tail_final as R
F,A,Part,P,B,C,Q,ROOT,BASE,OUT=R.F,R.A,R.Part,R.P,R.B,R.C,R.Q,R.ROOT,R.BASE,R.OUT
MODEL=OUT/'TailWiringRelease.FCStd'

def run():
 tick=time.monotonic();assert not MODEL.exists(),'Receive existing release first'
 old=B.read(OUT/'complete-checks.json');assert len(old['contacts'])==1 and old['contacts'][0]['b']=='W4_B3Insulation'
 assert P.sha(OUT/'TailWiringSelected.FCStd')==old['model_sha256']
 d=A.openDocument(str(OUT/'TailWiringSelected.FCStd'));reader=P.SavedShapes();targets,torso=F.E.scene(reader)
 try:
  # Straight sleeve protected already-intactHELU jacket and collided with
  # the formed-terminal wrap. It is redundant, not another wiring restraint.
  d.removeObject('W4_B3Insulation');d.recompute()
  proof=dict(status='PENDING',contacts=[],pairs=0,physical_pass=False,selected=False,reused_pairs=old['pairs']+old['reused_final_pairs'])
  shapes={n:d.getObject(n).Shape for n in ('UpperCarrier001','E2Fixture','FTYCradle','TailLocalRail')}
  targets.update(shapes)
  # Wires/connector/rail straps first freed on supported bench, as explicitly
  # required by final service recipe. Only the bare printed rail moves here.
  targets={n:s for n,s in targets.items() if not n.startswith('local/') and n!='TailLocalRail'}
  targets['FTA_case']=d.W4_F_TY_case.Shape
  rail=shapes['TailLocalRail'];prisms=[]
  for face in rail.Faces:
   z=face.normalAt(0,0).z
   assert abs(z)<1e-7 or abs(abs(z)-1)<1e-7,'Rail has unhandled nonvertical geometry'
   if z>.99:
    prism=face.extrude(A.Vector(0,0,30));assert prism.isValid() and len(prism.Solids)==1
    prisms.append(prism)
  assert prisms
  for i,s in enumerate(prisms):
   for name,t in targets.items():
    if not C.near(s,t,0):continue
    assert t.isValid() and t.Solids,name
    volume=sum(s.common(part).Volume for part in t.Solids);proof['pairs']+=1
    if volume>1e-5:proof['contacts'].append(dict(a=f'rail_continuous30/top{i}',b=name,volume_mm3=volume))
  proof['bare_rail_continuous_lift_mm']=30;proof['upward_face_prisms']=len(prisms)
  proof['service_limits']='Bare rail ONLY: factoryJR unplugged, G_TAIL5 and B3 freed with PCB supported, case/wire/guard bands cut and wires/connector removed. Existing two retention bands118/138 cut. Then continuous+Z30 removal; no attached-wire sweep or physical hand/latch acceptance. Reverse for installation, wires afterward.'
  proof['insulation']=old['insulation'];proof['insulation']['redundant_straight_RNF15_removed']=True
  proof['factory']=old['factory'];proof['local_lengths']=old['local_lengths'];proof['tail_motion_samples']=old['tail_motion_samples']
  proof['exports']=old['exports'];proof['native_validity']=F.N.validate(d,[d.getObject(n) for n in shapes])
  proof['native_parameter_restore']=old['native_parameter_restore'] and old['guard_parameter_restore']
  d.saveAs(str(MODEL));A.closeDocument(d.Name)
  with tempfile.TemporaryDirectory(prefix='cat-w4-release-') as td:
   path=Path(td)/MODEL.name;shutil.copy2(MODEL,path);d=A.openDocument(str(path));F.N.validate(d,[d.getObject(n) for n in shapes]);assert all(o.getLinkedObject().Document==d for o in d.Objects if o.TypeId=='App::Link')
  proof.update(status='CURRENT_W4_RELEASE_PREPARED' if not proof['contacts'] else 'CURRENT_W4_RELEASE_REJECTED',
   fresh_relocated_reopen=True,model_sha256=P.sha(MODEL),worker_seconds=round(time.monotonic()-tick,3),
   source_sha256={Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__)),(OUT/'complete-checks.json').relative_to(ROOT).as_posix():P.sha(OUT/'complete-checks.json'),(OUT/'TailWiringSelected.FCStd').relative_to(ROOT).as_posix():P.sha(OUT/'TailWiringSelected.FCStd')})
  B.save('release-checks.json',proof);print(json.dumps({k:proof[k] for k in ('status','contacts','pairs','upward_face_prisms','worker_seconds')}),flush=True)
 finally:
  for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
if __name__=='__main__':run()
