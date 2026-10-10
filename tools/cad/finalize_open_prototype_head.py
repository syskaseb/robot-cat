"""Add the retained current neck mount and independently reopen the CP2 head."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,time,math,tempfile,shutil
sys.path.insert(0,str(Path(sys.executable).resolve().parent.parent/'lib'))
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from open_prototype_head_assembly import OUT,BASE,FIXED,PITCH
from open_prototype_tail_assembly import solid_centre

def run():
    tick=time.monotonic();model=OUT/'HeadNeckCurrent.FCStd';proof=OUT/'head-neck-checks.json'
    assert not model.exists() and not proof.exists()
    report=json.loads((OUT/'native-assembly-checks.json').read_text())
    assert report['status']=='CURRENT_HEAD_LOCAL_NATIVE_PREPARED_FRESH_REOPEN_REQUIRED'
    head=OUT/'HeadAssemblyCurrent.FCStd';assert sha(head)==report['model_sha256']
    neckpath=BASE/'mounting-checkpoint/Mounts.FCStd';r=SavedShapes()
    doc=A.openDocument(str(head));neck=A.openDocument(str(neckpath));support=[]
    try:
      old={o.Name for o in doc.Objects}
      for n in ('LeftRiser','RightRiser'):
        ob=doc.copyObject(neck.getObject(n),True);doc.recompute()
        s=r.shape(neckpath,n)
        assert abs(s.Volume-ob.Shape.Volume)<1e-5,n
        assert s.cut(ob.Shape).Volume<1e-5 and ob.Shape.cut(s).Volume<1e-5,n
        ob.Visibility=True;support.append(ob.Name)
      left=doc.getObject(support[0])
      candidates=[o for o in left.OutListRecursive if 'MainGap' in o.PropertiesList]
      assert len(candidates)==1,[o.Name for o in candidates]
      parameter=candidates[0];parameter_name=parameter.Name
      main=doc.addObject('Part::Feature','CurrentMainSupplierReference');main.Shape=r.shape(neckpath,'MainSupplierFamily')
      main.addProperty('App::PropertyString','RetainedSource');main.RetainedSource=neckpath.relative_to(ROOT).as_posix()+'#MainSupplierFamily'
      main.setExpression('Placement.Base.z',f'46.52 mm + {parameter.Name}.MainGap - 4 mm')
      doc.recompute();assert abs(main.Placement.Base.z-46.52)<1e-6
      volume=left.Shape.Volume
      parameter.MainGap=5;doc.recompute()
      assert abs(main.Placement.Base.z-47.52)<1e-6 and abs(left.Shape.Volume-volume)>1e-5
      parameter.MainGap=4;doc.recompute()
      assert abs(main.Placement.Base.z-46.52)<1e-6 and abs(left.Shape.Volume-volume)<1e-5
      # Full eight-stack neck hardware is retained, not a second stock kit.
      hardware=[];head_washers=[]
      for y in (22.5,-22.5):
       for ax in (-80,-70):
        for role,x,z,L,nz,wz in [('lower',ax,35.22,10,42.82,42.52),('upper',ax-42,71.82,12,61.62,63.22)]:
          sign=1 if role=='lower' else -1
          shapes={'Bolt':Part.makeCylinder(1,L,A.Vector(x,y,z),A.Vector(0,0,sign)).fuse(Part.makeCylinder(1.9,2,A.Vector(x,y,z),A.Vector(0,0,-sign))),
            'Washer':Part.makeCylinder(2.5,.3,A.Vector(x,y,wz)).cut(Part.makeCylinder(1.1,.3,A.Vector(x,y,wz))),
            'HeadWasher':Part.makeCylinder(2.5,.3,A.Vector(x,y,z if role=='lower' else z-.3)).cut(Part.makeCylinder(1.1,.3,A.Vector(x,y,z if role=='lower' else z-.3))),
            'Nut':Part.makeCylinder(4/math.sqrt(3),1.6,A.Vector(x,y,nz)).cut(Part.makeCylinder(1,1.6,A.Vector(x,y,nz)))}
          for kind,s in shapes.items():
            ob=doc.addObject('Part::Feature','Neck'+kind+str(len(hardware)));ob.Shape=s
            hardware.append(dict(name=ob.Name,role=role,kind=kind,axis=[x,y],length=L if kind=='Bolt' else None))
            if kind=='HeadWasher':head_washers.append(ob.Shape.copy())
      # Only the eight omitted head-side washers are a new interface. Existing
      # head/neck clearance evidence is retained, not rerun in full.
      context=BASE/'OpenPrototypePlan.FCStd';obstacles={}
      from check_main_p0_placement import prop
      for n,o in r.doc(context).items():
        if n.startswith('P0_') and not any(t in n for t in ('Tail','MG92B','Power','Battery')) and prop(o,'Shape') is not None:
          obstacles[n]=r.shape(context,n)
      for n in support:obstacles[n]=doc.getObject(n).Shape.copy()
      pairs=0;contacts=[]
      root=doc.CP2Head;yaw=doc.YawMotion;pitch=doc.PitchMotion
      for p in (-10,0,5):
       for y in (-15,0,15):
        doc.HeadParameters.Pitch=p;doc.HeadParameters.Yaw=y;doc.recompute()
        current=dict(obstacles)
        for row in report['parts']:
          n=row['name'];s=doc.getObject('Head_'+n).Shape.copy();pose=root.Placement
          if n not in FIXED:pose=pose*yaw.Placement
          if n in PITCH:pose=pose*pitch.Placement
          s.Placement=pose*s.Placement;current[n]=s
        for i,w in enumerate(head_washers):
         for n,s in current.items():
          if not w.BoundBox.intersect(s.BoundBox):continue
          pairs+=1;assert s.isValid() and w.isValid(),n
          v=sum(a.common(b).Volume for a in w.Solids for b in s.Solids)
          if v>1e-5:contacts.append(dict(washer=i,other=n,pitch=p,yaw=y,volume=v))
      assert not contacts,contacts
      doc.HeadParameters.Pitch=0;doc.HeadParameters.Yaw=0
      # Local printed targets and purchased references remain self-contained.
      assert all(o.getLinkedObject().Document==doc for o in doc.Objects if o.TypeId=='App::Link')
      doc.recompute();doc.saveAs(str(model))
    finally:
      for d in list(A.listDocuments().values()):A.closeDocument(d.Name)
    # A genuinely new document in a relocated file, not an already open cache.
    with tempfile.TemporaryDirectory(prefix='robot-cat-head-neck-fresh-') as td:
      relocated=Path(td)/model.name;shutil.copy2(model,relocated)
      doc=A.openDocument(str(relocated));doc.recompute()
      try:
        links=[o for o in doc.Objects if o.TypeId=='App::Link']
        assert links and all(o.getLinkedObject().Document==doc for o in links)
        objects={row['name']:doc.getObject('Head_'+row['name']) for row in report['parts']}
        assert len(objects)==52 and all(o is not None and o.Shape.isValid() for o in objects.values())
        initial={n:o.Shape.copy() for n,o in objects.items()}
        root=doc.CP2Head;yaw=doc.YawMotion;pitch=doc.PitchMotion
        def world(name):
          s=objects[name].Shape.copy()
          pose=root.Placement
          if name not in FIXED:pose=pose*yaw.Placement
          if name in PITCH:pose=pose*pitch.Placement
          s.Placement=pose*s.Placement;return s
        baseline={n:world(n) for n in objects}
        doc.HeadParameters.HeadRise=26;doc.recompute()
        assert all(abs(solid_centre(world(n)).z-solid_centre(s).z-1)<1e-5 for n,s in baseline.items())
        doc.HeadParameters.HeadRise=25;doc.recompute()
        for p,y in [(-10,-15),(-10,15),(5,-15),(5,15),(0,0)]:
          doc.HeadParameters.Pitch=p;doc.HeadParameters.Yaw=y;doc.recompute()
          for n,s in initial.items():
            expected=s.copy()
            if n in PITCH:expected.rotate(A.Vector(-152,0,136),A.Vector(0,1,0),p)
            if n not in FIXED:expected.rotate(A.Vector(-110,-5.25,0),A.Vector(0,0,1),y)
            expected.translate(A.Vector(-42,0,25))
            assert (solid_centre(world(n))-solid_centre(expected)).Length<1e-5,(n,p,y)
        gap=doc.getObject(parameter_name);gap.MainGap=5;doc.recompute()
        assert abs(doc.CurrentMainSupplierReference.Placement.Base.z-47.52)<1e-6
        gap.MainGap=4;doc.recompute()
        assert abs(doc.CurrentMainSupplierReference.Placement.Base.z-46.52)<1e-6
        assert all(abs(solid_centre(world(n)).z-solid_centre(s).z)<1e-5 for n,s in baseline.items())
        result=dict(status='CURRENT_HEAD_NECK_FRESH_RELOCATED_NATIVE_PREPARED',complete_M2=False,
          physical_pass=False,selected=False,head_modeled_identities=52,neck_hardware=hardware,
          neck_supports=support,local_links=len(links),external_links=0,
          head_washer_changed_interface=dict(washers=8,pose_samples=9,pairs=pairs,contacts=contacts),
          motion_parameters_checked=True,all_52_rise_restore=True,pose_samples=[[-10,-15],[-10,15],[5,-15],[5,15],[0,0]],
          MAIN_absolute_4_5_4=True,MAIN_world_z_mm=46.52,
          inherited_neck_assembly_proof='hardware/cad/studies/whole-cat-packaging/cp2/neck-support/mount-check-corrected.json',
          source_sha256={**r.hashes,head.relative_to(ROOT).as_posix():sha(head),(OUT/'native-assembly-checks.json').relative_to(ROOT).as_posix():sha(OUT/'native-assembly-checks.json'),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
          model_sha256=sha(model),worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        proof.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('status','head_modeled_identities','local_links','worker_seconds')}),flush=True)
      finally:A.closeDocument(doc.Name)

if __name__=='__main__':run()
