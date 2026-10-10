"""Current CP2 head: local editable targets, two motion frames, no physical PASS."""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,time,shutil,tempfile
sys.path.insert(0,str(Path(sys.executable).resolve().parent.parent/'lib'))
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from open_prototype_head_preflight import BASE,OUT,HEAD,SHIFT,PITCH,flatten,bbox

# The horn -> jaws -> fork path co-rotates. T210 explicitly cancels their
# shared yaw. Bridge and servo carrier remain on the fixed bearing support.
FIXED={'Foundation','YawCarrier','YawServoReference','Bridge'}
PRINTED={'FrontLeft','FrontRightPorted','Rear','Nose','EarL','EarR','PassiveJournal',
 'CageBase','CageRetainerLeft','CageRetainerRight','Carrier','PitchRetainer',
 'Fork','Retainer','ClampPositiveX','ClampNegativeX','Bridge','Foundation',
 'YawCarrier','HornProvisional','YawPrintedHorn'}
REPLACEMENTS={
 'FrontRightPorted':('hardware/cad/studies/head-external-wire-support-r1/FrontRightWirePassage.FCStd','WireInterface0'),
 'Fork':('hardware/cad/studies/head-yaw-end-restraints-r2/ForkYawEndSeatSplices.FCStd','Interface0'),
 'YawCarrier':('hardware/cad/studies/head-fixed-yaw-feed-r3/YawCarrierJRSeat.FCStd',None),
 'Carrier':('hardware/cad/studies/head-jr-support-r5/PitchCarrierThroughLeadExit.FCStd','Interface0')}
NATIVE_SOURCE_OVERRIDES={'PitchRetainer':('hardware/cad/studies/head-p8/pitch-support-r3/PitchBearingFork.FCStd','PitchRetainer')}

def same_geometry(actual,expected,name):
    # Native features/parameters are copied from the pinned source unchanged.
    # Material/face/edge/vertex signatures verify that copy without repeating
    # multi-minute Boolean subtraction of an unchanged detailed shell.
    reference_signature(actual,expected,name)

def servo_smoke():
    r=SavedShapes();path=HEAD.parent/'YawDrivePrintedHornR2.FCStd';name='YawServoReference'
    expected=r.shape(path,name);source=A.openDocument(str(path))
    ob=source.getObject(name)
    if ob.TypeId=='App::Link':ob=ob.getLinkedObject(True)
    with tempfile.TemporaryDirectory(prefix='robot-cat-head-servo-smoke-') as td:
      d=A.newDocument('ServoCopySmoke');d.saveAs(str(Path(td)/'smoke.FCStd'))
      target=d.copyObject(ob,True);d.recompute()
      actual=target.Shape.copy();actual.Placement=expected.Placement*target.Shape.Placement.inverse()*actual.Placement
      values=dict(compound_difference_mm3=[actual.cut(expected).Volume,expected.cut(actual).Volume],solids=len(actual.Solids))
      values['per_solid']=[dict(index=i,actual_valid=a.isValid(),expected_valid=b.isValid(),actual_volume=a.Volume,expected_volume=b.Volume,difference=[a.cut(b).Volume,b.cut(a).Volume],vertices=[len(a.Vertexes),len(b.Vertexes)],vertex_distance=max([(x.Point-y.Point).Length for x,y in zip(a.Vertexes,b.Vertexes)],default=0)) for i,(a,b) in enumerate(zip(actual.Solids,expected.Solids))]
      values['exact_serialized_brep_identity']=actual.exportBrepToString()==expected.exportBrepToString()
      values['self_difference_mm3']=[a.cut(a).Volume for a in actual.Solids]
      sa=actual.exportBrepToString().splitlines();sb=expected.exportBrepToString().splitlines()
      values['brep_line_counts']=[len(sa),len(sb)]
      values['brep_differences']=[dict(line=i,actual=a,expected=b) for i,(a,b) in enumerate(zip(sa,sb)) if a!=b][:12]
      (OUT/'servo-copy-diagnostic.json').write_text(json.dumps(values,indent=2)+'\n',encoding='utf-8')
      print(json.dumps(values),flush=True)
      same_geometry(actual,expected,'YawServoReference');values['per_solid_identity']=True
      (OUT/'servo-copy-diagnostic.json').write_text(json.dumps(values,indent=2)+'\n',encoding='utf-8')
      print(json.dumps(values),flush=True)
      for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)

def reference_smoke():
    tick=time.monotonic();r=SavedShapes()
    parts=flatten(r,HEAD,'HeadNoseInsertUnit')
    with tempfile.TemporaryDirectory(prefix='robot-cat-ref-smoke-') as td:
      d=A.newDocument('ReferenceSmoke')
      names=[n for n in parts if n not in PRINTED]
      for name in names:
        expected=parts[name][0];ob=d.addObject('Part::Feature',name);ob.Shape=expected;d.recompute()
        reference_signature(ob.Shape,expected,name)
      p=Path(td)/'reference.FCStd';d.saveAs(str(p));A.closeDocument(d.Name)
      d=A.openDocument(str(p));d.recompute()
      for name in names:
        restored=d.getObject(name).Shape;expected=parts[name][0]
        # FCStd serialization may normalize periodic pcurves. The input was
        # byte-identical before saving; compare material/face/edge signatures
        # after the native serializer, not pointer identity or Compound Cut.
        reference_signature(restored,expected,name)
      A.closeDocument(d.Name)
    print('EXACT_REFERENCE_ASSIGNMENT_AND_FRESH_REOPEN',round(time.monotonic()-tick,3),flush=True)

def part_smoke(name):
    r=SavedShapes();expected,path,objname=flatten(r,HEAD,'HeadNoseInsertUnit')[name]
    if name in NATIVE_SOURCE_OVERRIDES:
      rel,objname=NATIVE_SOURCE_OVERRIDES[name];path=ROOT/rel
    with tempfile.TemporaryDirectory(prefix='robot-cat-head-part-') as td:
      source=A.openDocument(str(path));ob=source.getObject(objname)
      if ob.TypeId=='App::Link':ob=ob.getLinkedObject(True)
      d=A.newDocument('PartCopySmoke');d.saveAs(str(Path(td)/'smoke.FCStd'))
      target=d.copyObject(ob,True);d.recompute();actual=target.Shape.copy()
      actual.Placement=expected.Placement
      print(json.dumps(dict(name=name,path=str(path.relative_to(ROOT)),object=objname,target=ob.Name,
        expected_volume=expected.Volume,actual_volume=actual.Volume,
        solids=[len(expected.Solids),len(actual.Solids)],faces=[len(expected.Faces),len(actual.Faces)],
        bounds=[bbox(expected),bbox(actual)],
        vertices=[len(expected.Vertexes),len(actual.Vertexes)],
        vertex_distance=max([(a.Point-b.Point).Length for a,b in zip(expected.Vertexes,actual.Vertexes)],default=0))),flush=True)
      for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)

def reference_signature(actual,expected,name):
    assert len(actual.Solids)==len(expected.Solids),name
    for a,b in zip(actual.Solids,expected.Solids):
      assert a.isValid() and b.isValid(),name
      assert len(a.Faces)==len(b.Faces) and len(a.Edges)==len(b.Edges) and len(a.Vertexes)==len(b.Vertexes),name
      assert abs(a.Volume-b.Volume)<max(1e-5,abs(b.Volume)*1e-8),name
      assert abs(a.Area-b.Area)<max(1e-5,abs(b.Area)*1e-8),name
      assert (a.CenterOfMass-b.CenterOfMass).Length<1e-5,name
      assert max(abs(x-y) for x,y in zip(bbox(a),bbox(b)))<1e-5,name
      for x,y in zip(a.Vertexes,b.Vertexes):assert (x.Point-y.Point).Length<1e-5,name
      for x,y in zip(a.Edges,b.Edges):
        assert abs(x.Length-y.Length)<1e-5 and (x.CenterOfMass-y.CenterOfMass).Length<1e-5,name
      for x,y in zip(a.Faces,b.Faces):
        assert abs(x.Area-y.Area)<max(1e-5,abs(y.Area)*1e-8) and (x.CenterOfMass-y.CenterOfMass).Length<1e-5,name
        assert type(x.Surface)==type(y.Surface),name

def motion_frame(doc,name,parameter,axis,centre):
    part=doc.addObject('App::Part',name)
    part.Placement=A.Placement(A.Vector(),A.Rotation(A.Vector(*axis),0))
    part.setExpression('Placement.Rotation.Angle','HeadParameters.'+parameter)
    cx,cy,cz=centre;p='HeadParameters.'+parameter
    if axis==[0,0,1]:
      part.setExpression('Placement.Base.x',f'{cx} mm * (1-cos({p})) + {cy} mm * sin({p})')
      part.setExpression('Placement.Base.y',f'{cy} mm * (1-cos({p})) - {cx} mm * sin({p})')
    else:
      part.setExpression('Placement.Base.x',f'{cx} mm * (1-cos({p})) - {cz} mm * sin({p})')
      part.setExpression('Placement.Base.z',f'{cz} mm * (1-cos({p})) + {cx} mm * sin({p})')
    return part

def run():
    model=OUT/'HeadAssemblyCurrent.FCStd';proof=OUT/'native-assembly-checks.json'
    assert not model.exists() and not proof.exists(),'Preserve previous qualified attempt'
    pre=json.loads((OUT/'preflight.json').read_text())
    assert pre['status']=='CURRENT_HEAD_EXTERNAL_INTERFACES_CLEAR' and not pre['contacts']
    assert all(sha(ROOT/n)==h for n,h in pre['source_sha256'].items())
    tick=time.monotonic();reader=SavedShapes();parts=flatten(reader,HEAD,'HeadNoseInsertUnit')
    docs={};d=A.newDocument('HeadAssemblyCurrent');targets={};rows=[]
    scratch=tempfile.TemporaryDirectory(prefix='robot-cat-head-native-')
    d.saveAs(str(Path(scratch.name)/'HeadAssemblyBuild.FCStd'))
    def opened(path):
      if path not in docs:docs[path]=A.openDocument(str(path))
      return docs[path]
    try:
      params=d.addObject('App::VarSet','HeadParameters')
      for n,v,kind in [('HeadForward',42,'Length'),('HeadRise',25,'Length'),('Yaw',0,'Angle'),('Pitch',0,'Angle')]:
        params.addProperty('App::Property'+kind,n);setattr(params,n,v)
      root=d.addObject('App::Part','CP2Head')
      root.setExpression('Placement.Base.x','-HeadParameters.HeadForward')
      root.setExpression('Placement.Base.z','HeadParameters.HeadRise')
      yaw=motion_frame(d,'YawMotion','Yaw',[0,0,1],[-110,-5.25,0]);root.addObject(yaw)
      pitch=motion_frame(d,'PitchMotion','Pitch',[0,1,0],[-152,0,136]);yaw.addObject(pitch)
      instances={};corrected=[]
      for name,(expected,path,objname) in parts.items():
        reference_only=name not in PRINTED
        if reference_only:
          # Purchased references need no native redesign. Keep the exact
          # saved BRep; opening/rebuilding its supplier primitive changes
          # periodic pcurves and invalidates a cross-representation Boolean.
          source_ob=None
        elif name in REPLACEMENTS:
          rel,objname=REPLACEMENTS[name];path=ROOT/rel
          source=opened(path)
          if objname is None:
            # Generated final feature is selected by exact saved BRep volume,
            # not by a guessed feature number or the first box/sketch.
            expected=Part.read(str(path.with_suffix('.brep')))
            candidates=[o for o in source.Objects if hasattr(o,'Shape') and not o.Shape.isNull() and o.TypeId.startswith('Part::') and not o.InList and abs(o.Shape.Volume-expected.Volume)<1e-5]
            assert len(candidates)==1,(name,[o.Name for o in candidates]);objname=candidates[0].Name
          source_ob=source.getObject(objname);assert source_ob is not None,(name,objname)
          expected=reader.shape(path,objname)
        else:
          if name in NATIVE_SOURCE_OVERRIDES:
            rel,objname=NATIVE_SOURCE_OVERRIDES[name];path=ROOT/rel
          source=opened(path);source_ob=source.getObject(objname)
          if source_ob.TypeId=='App::Link':source_ob=source_ob.getLinkedObject(True)
        key=(str(path),objname) if reference_only else (source_ob.Document.FileName,source_ob.Name)
        if reference_only:
          link=d.addObject('Part::Feature','Head_'+name);link.Shape=expected
          reference_signature(link.Shape,expected,name)
          link.addProperty('App::PropertyString','RetainedSource');link.RetainedSource=path.relative_to(ROOT).as_posix()+'#'+objname
          target=link
        if key not in targets:
          if reference_only:
            copied=link
          else:
            assert hasattr(source_ob,'Shape'),(name,source_ob.TypeId,source_ob.Name)
            copied=d.copyObject(source_ob,True)
          d.recompute();copied.Visibility=False
          targets[key]=copied
        target=targets[key]
        assert target.Shape.isValid() and expected.isValid(),name
        # A link placement maps the original native target into the saved
        # physical leaf pose without destroying any editable source feature.
        if not reference_only:
          link=d.addObject('App::Link','Head_'+name);link.setLink(target);link.LinkTransform=True
          link.LinkPlacement=expected.Placement*target.Shape.Placement.inverse()
        if name in PITCH:pitch.addObject(link)
        elif name not in FIXED:yaw.addObject(link)
        else:root.addObject(link)
        d.recompute();actual=link.Shape.copy()
        assert max(abs(a-b) for a,b in zip(bbox(actual),bbox(expected)))<1e-5,name
        assert abs(actual.Volume-expected.Volume)<max(1e-5,abs(expected.Volume)*1e-8),name
        if reference_only:
          reference_signature(actual,expected,name)
        else:same_geometry(actual,expected,name)
        instances[name]=link
        rows.append(dict(name=name,source=path.relative_to(ROOT).as_posix(),source_object=objname,
            local_target=target.Name,type=target.TypeId,volume_mm3=actual.Volume,
            reference_only=reference_only,frame='pitch' if name in PITCH else 'fixed' if name in FIXED else 'yaw'))
        if name in pre['parts'] and pre['parts'][name]['yaw']!=(name not in FIXED):corrected.append(name)
        print('local head',name,len(rows),flush=True)
      # Only the eight jaw/hardware identities changed motion classification.
      # At every qualified pose their geometry is separated from all changed
      # external obstacles. The frozen broad screen remains a parent receipt.
      external={}
      from open_prototype_head_preflight import MOUNT
      neck=BASE/'mounting-checkpoint/Mounts.FCStd'
      for n in ('LeftRiser','RightRiser','MainSupplierFamily'):external[n]=reader.shape(neck,n)
      for n in ('LowerCarrier','UpperCarrier','Spacer1','Spacer2','Spacer3','Spacer4'):external[n]=reader.shape(MOUNT,n)
      corrections=[]
      for y in (-15,0,15):
        params.Yaw=y;d.recompute()
        for name in corrected:
          s=instances[name].Shape.copy();s.Placement=root.Placement*yaw.Placement*s.Placement
          for n,t in external.items():
            if s.BoundBox.intersect(t.BoundBox):
              v=sum(a.common(b).Volume for a in s.Solids for b in t.Solids)
              assert v<1e-5,(name,n,y,v)
            corrections.append(dict(name=name,obstacle=n,yaw=y,clear=True))
      params.Yaw=0;d.recompute()
      baseline={n:bbox(o.Shape) for n,o in instances.items()}
      params.HeadRise=26;d.recompute()
      assert abs(root.Placement.Base.z-26)<1e-6
      params.HeadRise=25;params.Pitch=-10;params.Yaw=15;d.recompute()
      assert yaw.Placement.Rotation.isSame(A.Rotation(A.Vector(0,0,1),15),1e-7)
      assert pitch.Placement.Rotation.isSame(A.Rotation(A.Vector(0,1,0),-10),1e-7)
      params.Pitch=0;params.Yaw=0;d.recompute()
      assert all(max(abs(a-b) for a,b in zip(bbox(o.Shape),baseline[n]))<1e-5 for n,o in instances.items())
      # Native copy dependencies may include links; explicitly localize actual
      # linked targets until no external references remain.
      while True:
        links=[o for o in d.Objects if o.TypeId=='App::Link' and o.getLinkedObject().Document!=d]
        if not links:break
        for ob in links:
          old=ob.getLinkedObject();pose=ob.LinkPlacement;native=d.copyObject(old,True)
          native.Visibility=False;ob.setLink(native);ob.LinkPlacement=pose
        d.recompute()
      for o in d.Objects:
        if hasattr(o,'Visibility') and o not in instances.values():o.Visibility=False
      root.Visibility=True;yaw.Visibility=True;pitch.Visibility=True
      for o in instances.values():o.Visibility=True
      d.recompute();d.saveAs(str(model))
      pins={**reader.hashes,**{p.relative_to(ROOT).as_posix():sha(p) for p in docs}}
      pins[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
      pins[(OUT/'preflight.json').relative_to(ROOT).as_posix()]=sha(OUT/'preflight.json')
      result=dict(status='CURRENT_HEAD_LOCAL_NATIVE_PREPARED_FRESH_REOPEN_REQUIRED',selected=False,
        physical_pass=False,complete_M2=False,parts=rows,local_native_targets=len(targets),
        corrected_yaw_classification=corrected,changed_motion_checks=corrections,
        nominal_pitch_deg=[-10,5],nominal_yaw_deg=[-15,15],native_parameter_restore=True,
        head_shift_mm=list(SHIFT),model_sha256=sha(model),source_sha256=pins,
        copy_verification='Unchanged copied native feature definitions; corresponding solid/face/edge/vertex material signatures, not a new Boolean material qualification',
        worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
      proof.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
      print(result['status'],len(rows),result['worker_seconds'],flush=True)
    finally:
      for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
      scratch.cleanup()

if __name__=='__main__':
    if '--reference-smoke' in sys.argv:reference_smoke()
    elif '--part-smoke' in sys.argv:part_smoke(sys.argv[-1])
    elif '--servo-smoke' in sys.argv:servo_smoke()
    else:run()
