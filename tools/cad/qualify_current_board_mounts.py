"""One current board-only M5 master: retained axes plus matched CP2 plates.

Do not select stale WAGO/source placements or repeat unchanged board gates.
"""
from pathlib import Path
from datetime import datetime,timezone
import sys,json,time,tempfile,shutil
sys.path.insert(0,str(Path(sys.executable).resolve().parent.parent/'lib'))
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from open_prototype_head_assembly import reference_signature
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'mounting-checkpoint'

def run():
    tick=time.monotonic();model=OUT/'CurrentBoardMounts.FCStd';proof=OUT/'current-M5-checks.json'
    assert not model.exists() and not proof.exists(),'Receive current M5 result, do not duplicate'
    paths={'retained':OUT/'RetentionMountsAssembly.FCStd',
      'lower':BASE/'tail-mount-checkpoint/TailAssemblyCurrent.FCStd',
      'upper':BASE/'wiring-checkpoint/DataShelfCurrent.FCStd'}
    reader=SavedShapes();before={k:reader.shape(paths['retained'],n) for k,n in [('lower','LowerCarrier'),('upper','UpperCarrier')]}
    expected={k:reader.shape(paths[k],n) for k,n in [('lower','LowerCarrier'),('upper','UpperCarrier')]}
    # Existing complete nominal stages, not the earlier rejected axial nut tool.
    inherited=['shared-retention-mount-checks.json','board-rear-tool-checks.json','pwm-flat-insulator-checks.json']
    for name in inherited:
      r=json.loads((OUT/name).read_text())
      for n,h in r['source_sha256'].items():assert sha(ROOT/n)==h,(name,n)
    d=A.openDocument(str(paths['retained']));others=[];copied=[]
    result=dict(status='PENDING',result_id='M5',selected=False,physical_pass=False,
      M5_complete=False,contacts=[],pairs=0,copy_receipts=[],old_WAGO_source_geometry_not_selected=True)
    try:
      changed={}
      for key,name in [('lower','LowerCarrier'),('upper','UpperCarrier')]:
        source=A.openDocument(str(paths[key]));others.append(source)
        ob=d.copyObject(source.getObject(name),True);d.recompute()
        reference_signature(ob.Shape,expected[key],name)
        ob.Label='Current '+name;copied.append(ob.Name);changed[key]=ob
        result['copy_receipts'].append(dict(role=key,name=ob.Name,volume_mm3=ob.Shape.Volume,source=paths[key].relative_to(ROOT).as_posix()))
      # All nominal board and fastener BReps are valid retained material. BUS
      # uses117 individual supplier solids, never the invalid cached compound.
      target_prefixes=('BUSsupplier','Pi4NominalPCB','PWM9685NominalPCB','AUX4092NominalPCB','PWM1608NominalPCB',
        'U1BoardAllowance','Pi4','BUS','PWM9685','AUX4092','PWM1608','U1Mount','U1Spacer','U1Insulator')
      targets={}
      for o in d.Objects:
        if o.Name.startswith(target_prefixes) and hasattr(o,'Shape') and not o.Shape.isNull() and 'Driver' not in o.Name:
          if o.Name in ('U1InsulatingSpacer','U1TopInsulator'):continue # unplaced print definitions
          s=reader.shape(paths['retained'],o.Name) if o.Name in reader.doc(paths['retained']) else o.Shape
          assert s.isValid(),o.Name;targets[o.Name]=s
      assert len([n for n in targets if n.startswith('BUSsupplier')])==117
      for key,ob in changed.items():
        # Only newly added material is retested. Holes/removals cannot add
        # collisions, but their body copy is independently signature-checked.
        extra=ob.Shape.cut(before[key]);assert extra.isNull() or extra.isValid(),key
        for name,s in targets.items():
          if extra.isNull() or not extra.BoundBox.intersect(s.BoundBox):continue
          volume=sum(a.common(b).Volume for a in extra.Solids for b in s.Solids)
          result['pairs']+=1
          if volume>1e-5:result['contacts'].append(dict(carrier=key,other=name,volume_mm3=volume))
      # A lower change removes only tail clearance; PCB/clamp bearing remains
      # the inherited datum. Explicitly preserve every PCB support cylinder.
      plan=json.loads((OUT/'board-mount-plan.json').read_text())
      support_checks=[]
      for board,axes in plan['board_hole_axes_world_xy_mm'].items():
        key='lower' if board in ('Pi4','BUS') else 'upper'
        z=plan['pcb_bottom_planes_mm'][board]
        for x,y in axes:
          collar=Part.makeCylinder(2.15,.2,A.Vector(x,y,z-.2)).cut(Part.makeCylinder(1.2,.2,A.Vector(x,y,z-.2)))
          area_before=before[key].common(collar).Volume;area_after=changed[key].Shape.common(collar).Volume
          assert area_before>1e-5 and abs(area_before-area_after)<1e-5,(board,x,y,area_before,area_after)
          support_checks.append(dict(board=board,axis=[x,y],retained_bearing_mm3=area_after))
      result['supplier_axis_bearing_checks']=support_checks
      assert len(support_checks)==17 and not result['contacts'],result['contacts']
      # Show only the current board module, not historical source/WAGO cases.
      physical=set(targets)|set(copied)
      physical.update(n for n in reader.doc(paths['retained']) if n.startswith(('RailClamp','UpperFrame','Spacer','TopClampPad','LowerClampJaw')) and n not in ('TopClampPad','LowerClampJaw') and not any(t in n for t in ('Tool','Driver')))
      for o in d.Objects:
        if hasattr(o,'Visibility'):o.Visibility=o.Name in physical
      assert all(o.getLinkedObject().Document==d for o in d.Objects if o.TypeId=='App::Link')
      d.recompute();d.saveAs(str(model))
      result['physical_objects']=sorted(physical)
    finally:
      for doc in list(A.listDocuments().values()):A.closeDocument(doc.Name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-board-fresh-') as td:
      relocated=Path(td)/model.name;shutil.copy2(model,relocated);d=A.openDocument(str(relocated));d.recompute()
      try:
        for key,name in zip(('lower','upper'),copied):reference_signature(d.getObject(name).Shape,expected[key],name)
        assert all(o.getLinkedObject().Document==d for o in d.Objects if o.TypeId=='App::Link')
        upper=d.getObject(copied[1]);params=[o for o in upper.OutListRecursive if 'U1BoardThickness' in o.PropertiesList]
        assert len(params)==1,[o.Name for o in params]
        p=params[0];initial=p.U1HoleX.Value;oldvol=upper.Shape.Volume;oldpoints=[v.Point for v in upper.Shape.Vertexes]
        p.U1HoleX=initial+.1;d.recompute();assert upper.Shape.isValid()
        assert any(min((v.Point-q).Length for q in oldpoints)>.05 for v in upper.Shape.Vertexes),'U1 hole parameter must change geometry'
        p.U1HoleX=initial;d.recompute();assert abs(upper.Shape.Volume-oldvol)<1e-5
        result.update(status='CURRENT_BOARD_MOUNT_NATIVE_PREPARED',fresh_relocated_reopen=True,
          native_U1_hole_parameter_restore=True,model_sha256=sha(model),
          source_sha256={**reader.hashes,**{p.relative_to(ROOT).as_posix():sha(p) for p in paths.values()},
            **{(OUT/n).relative_to(ROOT).as_posix():sha(OUT/n) for n in inherited},
            (OUT/'current-M5-plan.json').relative_to(ROOT).as_posix():sha(OUT/'current-M5-plan.json'),
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
          worker_seconds=round(time.monotonic()-tick,3),finished_utc=datetime.now(timezone.utc).isoformat())
        proof.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('status','pairs','worker_seconds')}),flush=True)
      finally:A.closeDocument(d.Name)

if __name__=='__main__':run()
