"""Receive three real tie/wire contacts using full two-lead envelopes."""
import json,time,sys,tempfile,shutil
from pathlib import Path
sys.path.insert(0,str(Path(sys.executable).resolve().parent.parent/'lib'))
import finish_current_pwm_fixture as F
A,Part,B,C,P=F.A,F.Part,F.B,F.C,F.P
OUT,ROOT,BASE=F.OUT,F.ROOT,F.BASE

def run():
    tick=time.monotonic();r=dict(status='PENDING',contacts=[],pairs=0,physical_pass=False)
    prior=json.loads((OUT/'current-checks.json').read_text())
    assert {(q['a'],q['b']) for q in prior['contacts']}=={('Band_SourceRed','XP03_source'),('Band_Module1','XP02_module'),('Band_Module2','XP02_module')}
    d=A.openDocument(str(OUT/'PWMBranchAssembly.FCStd'));reader=P.SavedShapes()
    targets,torso=C.I.E.context(reader)
    tp=json.loads((BASE/'tail-mount-checkpoint/tail-assembly-checks.json').read_text())
    for n in tp['tail_identities']:targets.pop('P0_'+n,None)
    src=A.openDocument(str(BASE/'mounting-checkpoint/CurrentBoardMounts.FCStd'))
    obsolete={o.Name for b in src.Objects if b.TypeId=='PartDesign::Body' for o in b.Group}
    for n in obsolete:targets.pop(n,None)
    targets.pop('UpperCarrier001',None)
    def check(n,s,m,t):
      if not C.near(s,t,0):return
      assert s.isValid() and t.isValid()
      v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids);r['pairs']+=1
      if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume=v))
    try:
      # Bundle envelope: two centresZ138/141, radius0.925, clearance0.2,
      # strap thickness1.2. Derive complete top/bottom instead of offsets.
      top=141+.925+.2+1.2;bottom=138-.925-.2-1.2
      specs=[('SourceRed',88.5,-10.7,-2.3,134.4,top),('Module1',126,-11.7,-4.375,bottom,top),('Module2',130,-11.7,-4.375,bottom,top)]
      for n,x,y0,y1,z0,z1 in specs:
        d.getObject('Band_'+n).Shape=C.box([x-1.25,y0,z0,x+1.25,y1,z1]).cut(C.box([x-1.4,y0+1.2,z0+1.2,x+1.4,y1-1.2,z1-1.2]))
        d.getObject('TieHead_'+n).Shape=C.box([x-2.25,y0-3.5,(z0+z1)/2-2.4,x+2.25,y0,(z0+z1)/2+2.4])
      d.E2ExitBandPassages.Length=137.4-(bottom-.2);d.recompute()
      F.validate(d,[d.UpperCarrier001,d.E2Fixture])
      paths=json.loads((OUT/'final-plan.json').read_text())['routes']
      scene={**targets,'UpperCarrier001':d.UpperCarrier001.Shape,'E2Fixture':d.E2Fixture.Shape,
        **{n:d.getObject(n).Shape for n in paths},'F_PWM_sleeve':d.F_PWM_sleeve.Shape,
        **{n:d.getObject(n).Shape for n in ('XP02_module_BoardInsulation','XP03_module_BoardInsulation')}}
      for n,_,_,_,_,_ in specs:
        for prefix in ('Band_','TieHead_'):
          ob=d.getObject(prefix+n)
          for m,t in scene.items():check(ob.Name,ob.Shape,m,t)
      # New band locations remain fixed; the nearest moving-tail test is
      # repeated only for these six changed shapes, using native TailYaw.
      tail=A.openDocument(str(BASE/'tail-mount-checkpoint/TailAssemblyCurrent.FCStd'))
      for angle in range(-30,31,5):
        tail.TailParameters.TailYaw=angle;tail.recompute()
        for o in tail.TailRotor.Group:
          if not hasattr(o,'Shape'):continue
          s=o.Shape.copy();s.Placement=tail.TailRotor.Placement*s.Placement
          for n,_,_,_,_,_ in specs:
            for pre in ('Band_','TieHead_'):check(pre+n,d.getObject(pre+n).Shape,'tail/'+o.Name+'@'+str(angle),s)
      r['tail_samples']=list(range(-30,31,5))
      d.recompute();baseline=d.E2Fixture.Shape.Volume;d.E2Parameters.FloorThickness=3;d.recompute();F.validate(d,[d.UpperCarrier001,d.E2Fixture])
      assert abs(d.E2Fixture.Shape.Volume-baseline)>1;d.E2Parameters.FloorThickness=2.8;d.recompute();assert abs(d.E2Fixture.Shape.Volume-baseline)<1e-5
      exports=[]
      for ob in (d.UpperCarrier001,d.E2Fixture):
        mesh=F.MeshPart.meshFromShape(Shape=ob.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
        assert mesh.isSolid() and not mesh.hasNonManifolds();bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
        dest=OUT/(ob.Name+'_final_x1.stl');mesh.write(str(dest));bb=mesh.BoundBox;size=[bb.XLength,bb.YLength,bb.ZLength]
        assert size[0]+10<256 and size[1]+10<256 and size[2]<256
        exports.append(dict(path=dest.relative_to(ROOT).as_posix(),sha256=P.sha(dest),object=ob.Name,quantity=1,size_mm=size,brim_mm=5,print_ready=False))
      model=OUT/'PWMBranchCurrentFinal.FCStd';assert not model.exists();d.saveAs(str(model));A.closeDocument(d.Name)
      with tempfile.TemporaryDirectory(prefix='cat-e2-bands-') as td:
        dest=Path(td)/model.name;shutil.copy2(model,dest);d=A.openDocument(str(dest));F.validate(d,[d.UpperCarrier001,d.E2Fixture]);assert all(o.getLinkedObject().Document==d for o in d.Objects if o.TypeId=='App::Link')
      r.update(status='E2_CURRENT_BANDS_REJECTED' if r['contacts'] else 'E2_CURRENT_COMPLETE_NATIVE_PREPARED',worker_seconds=round(time.monotonic()-tick,3),
        model_sha256=P.sha(model),exports=exports,native_parameter_restore=True,fresh_relocated_reopen=True,
        source_sha256={**reader.hashes,**{(OUT/n).relative_to(ROOT).as_posix():P.sha(OUT/n) for n in ('PWMBranchAssembly.FCStd','current-checks.json','received-checks.json','final-plan.json')},Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__))},
        prior_failures_resolved='Three exact positive tie/insulation intersections. Bundle top/bottom derived together; lower module channels resized for full1.2mm strap plus0.2mm clearance. No wire move. Prior unchanged service/torso/PCB/tail gates retained.',nominal_clearance_mm=.2)
      (OUT/'complete-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:r[k] for k in ('status','contacts','pairs','worker_seconds')}),flush=True)
    finally:
      for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
if __name__=='__main__':run()
