"""Final changed E2 gates, service allowances and current native exports."""
import json,time,sys,tempfile,shutil
from pathlib import Path
sys.path.insert(0,str(Path(sys.executable).resolve().parent.parent/'lib'))
import finish_current_pwm_fixture as F
A,Part,B,C,P=F.A,F.Part,F.B,F.C,F.P
ROOT,BASE,OUT=F.ROOT,F.BASE,F.OUT
MODEL=OUT/'PWMBranchAssembly.FCStd'

def run():
    assert not MODEL.exists(),'Receive existing current assembly first'
    tick=time.monotonic();receipt=json.loads((OUT/'received-checks.json').read_text())
    assert receipt['status']=='E2_RECEIPT_STATIC_PREPARED' and not receipt['contacts']
    assert P.sha(OUT/'PWMBranchReceived.FCStd')==receipt['model_sha256']
    r=dict(status='PENDING',contacts=[],pairs=0,physical_pass=False,selected=False)
    d=A.openDocument(str(OUT/'PWMBranchReceived.FCStd'));reader=P.SavedShapes()
    targets,torso=C.I.E.context(reader)
    for n in json.loads((BASE/'tail-mount-checkpoint/tail-assembly-checks.json').read_text())['tail_identities']:targets.pop('P0_'+n,None)
    source=A.openDocument(str(BASE/'mounting-checkpoint/CurrentBoardMounts.FCStd'))
    obsolete={o.Name for b in source.Objects if b.TypeId=='PartDesign::Body' for o in b.Group}
    for n in obsolete:targets.pop(n,None)
    targets.pop('UpperCarrier001',None)
    def check(n,s,m,t):
      if not C.near(s,t,0):return
      assert s.isValid() and t.isValid(),(n,m,'invalid shape')
      v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids);r['pairs']+=1
      if v>1e-5:r['contacts'].append(dict(a=n,b=m,volume=v))
    try:
      # Retention bands cannot consume insulation. Only sleeve bearing or
      # nominal boundary touch is allowed; positive overlap is a failure.
      names=list(json.loads((OUT/'final-plan.json').read_text())['routes'])+['F_PWM_sleeve','XP02_module_BoardInsulation','XP03_module_BoardInsulation']
      for o in d.Objects:
        if o.TypeId=='Part::Feature' and o.Name.startswith(('Band_','TieHead_')):
          for n in names:check(o.Name,o.Shape,n,d.getObject(n).Shape)
      # Only newly affected pairs with the moving tail; old M3 internal
      # checks are retained, not replayed.
      tp=json.loads((BASE/'tail-mount-checkpoint/tail-assembly-checks.json').read_text())
      tailpath=BASE/'tail-mount-checkpoint/TailAssemblyCurrent.FCStd';xml=reader.doc(tailpath)
      aliases={'TailRoot29':'SupportedRoot34','TailLowerRetainer':'LowerRetainerPETG','MG92BMount29':'RaisedTailSupport','TailBridge29':'RaisedTailBridge'}
      aliases.update({f'TailCartridge{k}{i}':f'Cartridge{k}{i}' for k in ('Bolt','Nut') for i in range(4)})
      tail={}
      for n in tp['tail_identities']:
        actual=aliases.get(n,n if n in xml else 'Current_'+n)
        assert actual in xml,(n,actual)
        tail[n]=reader.shape(tailpath,actual)
      for n in list(targets):
        if n.startswith('tail/'):targets.pop(n)
      targets.update({'tail/'+n:s for n,s in tail.items()})
      moving={n:tail[n] for n in tp['moving_identities']}
      changed={o.Name:o.Shape for o in d.Objects if o.TypeId=='Part::Feature' and not 'Driver' in o.Name}
      changed['E2Fixture']=d.E2Fixture.Shape
      changed['UpperCarrierAdded']=d.UpperCarrier001.Shape.cut(source.UpperCarrier001.Shape)
      for n,s in tail.items():
        if n not in moving:
          for m,t in changed.items():check('tail/'+n,s,m,t)
      r['tail_motion_samples']=list(range(-30,31,5))
      for angle in r['tail_motion_samples']:
        for n,sh in moving.items():
          s=sh.copy();s.rotate(A.Vector(171,-6,0),A.Vector(0,0,1),angle)
          for m,t in changed.items():check(f'tail/{n}@{angle}',s,m,t)
      # Source ends and relevant ties are freed first. Body-only allowance,
      # NOT a claimed continuous sweep of attached deformable cables.
      p=json.loads((OUT/'final-plan.json').read_text());h=p['housing_bounds_mm']
      service={
        'housing_lift10':C.box([h[0],h[1],h[2],h[3],h[4],h[5]+10]),
        'housing_north15_after_lift':C.box([h[0],h[1]-15,h[2]+10,h[3],h[4],h[5]+10]),
        'P_REAR4_nominal_finger':C.box([15,-10.5,143.5,27,-2.5,161.5]),
        'G_TAIL3_nominal_finger':C.box([24,-39,145.5,35,-31,163.5])}
      for n,s in service.items():
        for m,t in {**targets,'E2Fixture':d.E2Fixture.Shape,'UpperCarrier001':d.UpperCarrier001.Shape}.items():check(n,s,m,t)
      r['service_limits']='Project housing/finger allowances only. Free both source ends and ties first; support board and unstack upper module for bench unplugging if tension occurs. No connected wire sweep or manufacturer lever stroke claimed.'
      # Current body fit is tested on actual valid geometry, not bbox.
      r['outside_torso']=[]
      for n in ('E2Fixture','P_REAR','G_TAIL','JPWM','F_PWM_sleeve'):
        s=d.getObject(n).Shape;v=s.cut(torso).Volume
        if v>1e-5:r['outside_torso'].append(dict(name=n,volume=v))
      base={n:d.getObject(n).Shape.Volume for n in ('UpperCarrier001','E2Fixture')};z=d.P_REAR.Shape.BoundBox.ZMin
      d.E2Parameters.FloorThickness=3;d.recompute();F.validate(d,[d.UpperCarrier001,d.E2Fixture]);assert abs(d.P_REAR.Shape.BoundBox.ZMin-z-.2)<1e-6
      assert abs(d.E2Fixture.Shape.Volume-base['E2Fixture'])>1
      d.E2Parameters.FloorThickness=2.8;d.recompute();assert all(abs(d.getObject(n).Shape.Volume-v)<1e-5 for n,v in base.items())
      r['native_parameter_restore']=True;r['native_validity']=F.validate(d,[d.UpperCarrier001,d.E2Fixture])
      exports=[]
      for ob in (d.UpperCarrier001,d.E2Fixture):
        mesh=F.MeshPart.meshFromShape(Shape=ob.Shape,LinearDeflection=.08,AngularDeflection=.2,Relative=False)
        assert mesh.isSolid() and not mesh.hasNonManifolds()
        bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
        path=OUT/(ob.Name+'_current_x1.stl');mesh.write(str(path));b=mesh.BoundBox;size=[b.XLength,b.YLength,b.ZLength]
        assert size[0]+10<256 and size[1]+10<256 and size[2]<256
        exports.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=P.sha(path),object=ob.Name,quantity=1,size_mm=size,brim_mm=5,print_ready=False,
          orientation='Current axes, base down; long fixture posts/bridge and upper lands require phase2 support planning. Remove support from band channels/nut pockets, deburr. No slicer verification.'))
      d.saveAs(str(MODEL));A.closeDocument(d.Name)
      with tempfile.TemporaryDirectory(prefix='cat-e2-final-') as td:
        path=Path(td)/MODEL.name;shutil.copy2(MODEL,path);d=A.openDocument(str(path));F.validate(d,[d.UpperCarrier001,d.E2Fixture])
        assert all(o.getLinkedObject().Document==d for o in d.Objects if o.TypeId=='App::Link')
      r.update(status='E2_CURRENT_NATIVE_REJECTED' if r['contacts'] or r['outside_torso'] else 'E2_CURRENT_NATIVE_PREPARED',
        worker_seconds=round(time.monotonic()-tick,3),exports=exports,model_sha256=P.sha(MODEL),fresh_relocated_reopen=True,
        source_sha256={**reader.hashes,**{(OUT/n).relative_to(ROOT).as_posix():P.sha(OUT/n) for n in ('PWMBranchReceived.FCStd','received-checks.json','final-checks.json','final-plan.json')},Path(__file__).relative_to(ROOT).as_posix():P.sha(Path(__file__))})
      (OUT/'current-checks.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
      print(json.dumps({k:r[k] for k in ('status','contacts','pairs','outside_torso','worker_seconds')}),flush=True)
    finally:
      for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
if __name__=='__main__':run()
