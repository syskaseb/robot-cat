"""Correct the saved native pilot as ONE shared G2/D/middle restraint layout.

Reuse its cached sweeps; do not repeat whole legacy imports/strict full BOP.
The changed native boxes, slots and final result remain editable. Probe one
seat height, not both full passage sweeps, then restore and verify contacts.
"""
from datetime import datetime,timezone
from pathlib import Path
import json,shutil,sys,tempfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save,sha
import w5_bus_restraints_r3 as layout
OUT=ROOT/'hardware/electronics/full-cat/w5-bus-native-grips-r3'
CAD=ROOT/'hardware/cad/studies/w5-bus-native-grips-r3'
ROUTES=ROOT/'hardware/electronics/full-cat/w5-bus-pair-r52-r4'

def main():
    import FreeCAD as A
    import Part
    import MeshPart
    from w5_selected_owners_r52 import cached
    start=datetime.now(timezone.utc)
    OUT.mkdir(parents=True,exist_ok=True);CAD.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'checks.json').exists()
    fit=ROOT/'hardware/electronics/full-cat/w5-bus-band-preflight-r3/checks.json'
    check=json.loads(fit.read_text(encoding='utf-8'));assert not check['hits'] and not check['errors']
    source=ROOT/'hardware/cad/studies/w5-bus-native-grips-r2/BusCompleteDeck.FCStd'
    oldsha=sha(source)
    source_observation=ROOT/'hardware/electronics/full-cat/w5-bus-native-grips-r2/execution-observation.json'
    save(OUT/'intent.json',dict(status='SAVED_BEFORE_SHARED_NATIVE_CORRECTION',
        source=source.relative_to(ROOT).as_posix(),source_sha256=oldsha,
        inherited='R2 computed native pilot, valid1solid/newsupport BOP observed; rejected strap layout, no completed full-BOP/reopen claim',
        new_ties=3,reused_shared_W061_tie=1,new_fasteners=0,new_separate_prints=0,
        source_grips='Dwesthead/G2sharedtwoUgrooves/middleX98/sourcehanging',
        nominal_trim_mm={'W002':170,'W003':300},one_factory34171_cable=True,
        selected=False,W5_complete=False,physical_pass=False,
        material_note='Nominal G channel R1.2 atZ107 in inherited4mm plate leaves locally0.8mm skin, not a qualified PETG strength/profile. Check actual profile/support and coupon in phase2.'))
    d=A.openDocument(str(source));assert abs(d.BusGripParameters.GrooveRadius.Value-1.2)<1e-9
    target=CAD/'BusSharedGrips.FCStd';d.saveAs(str(target))
    olddeck=d.CurrentG1Deck.Shape.copy()
    sx=sum(json.loads((ROUTES/'intent.json').read_text(encoding='utf-8'))['source_lead_datums'][w][0] for w in ('W002','W003'))/2
    boxes=[]
    for name,b in layout.supports(sx):
        o=d.getObject(name+'InsulationSeat');assert o
        o.Length=b[3]-b[0];o.Width=b[4]-b[1];o.Height=b[5]-b[2];o.Placement.Base=A.Vector(*b[:3]);boxes.append(o)
    d.MiddleOpenGrip.Placement.Base.x=96.75
    # Existing W061 left slot retained; discard the redundant G left candidate.
    tools=list(d.BusClearanceTools.Shapes);tools.remove(d.GTieSlotL)
    d.BusClearanceTools.Shapes=tools
    d.GTieSlotR.Placement.Base=A.Vector(119.2,9.4,100)
    for side,n in [(-1,'GmidTieSlotL'),(1,'GmidTieSlotR')]:
        d.getObject(n).Placement.Base=A.Vector(96.4,61+side*3-1,100)
    p=d.BusGripParameters;p.addProperty('App::PropertyLength','DSeatHeight');p.DSeatHeight=5.2
    d.DendInsulationSeat.setExpression('Height','BusGripParameters.DSeatHeight')
    d.save();d.recompute();f=d.BusDeckFinished
    assert f.Shape.isValid() and len(f.Shape.Solids)==1
    nominal=f.Shape.Volume;d.save();print('BUS_SHARED_NATIVE_NOMINAL_SAVED',flush=True)
    assert all(o.Shape.isValid() and not o.Shape.check(True) for o in boxes)
    p.DSeatHeight=5.3;d.recompute();probe=f.Shape.Volume;assert probe>nominal
    print('BUS_SHARED_SEAT_PARAMETER_PROBE',probe,flush=True)
    p.DSeatHeight=5.2;d.recompute();shape=f.Shape.copy()
    assert shape.isValid() and len(shape.Solids)==1 and abs(shape.Volume-nominal)<max(1e-5,nominal*1e-8)
    d.save();shape.exportBrep(str(CAD/'Deck_WORLD.brep'))
    print('BUS_SHARED_PARAMETER_RESTORED',flush=True)
    owners,cache=cached()
    for n in layout.removed_owners():owners.pop(n)
    ties=layout.restraints(A,Part,sx);hits=[];errors=[];pairs=0
    def test(name,s,refs):
        nonlocal pairs
        for key,o in refs.items():
            if not s.BoundBox.intersect(o.BoundBox):continue
            for j,q in enumerate(o.Solids):
                if not s.BoundBox.intersect(q.BoundBox):continue
                pairs+=1
                try:
                    v=s.common(q).Volume
                    if v>1e-5:hits.append(dict(part=name,owner=key,solid=j,mm3=v))
                except Exception as e:errors.append(dict(part=name,owner=key,error=str(e)))
    for wire in ('W002','W003'):
        test(wire,Part.read(str(ROUTES/(wire+'_DESIGN.brep'))),{'newDeck':shape,**ties})
    # Only added support geometry against other installed owners. Subtracting
    # the whole inherited multi-MB Deck just to recover4boxes is unnecessary.
    for o in boxes:test(o.Name,o.Shape.cut(d.BusClearanceTools.Shape),owners)
    for name,s in ties.items():
        test(name,s,{'newDeck':shape})
        s.exportBrep(str(OUT/(name.replace('/','_')+'.brep')))
    dependencies=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    paths=[Path(__file__),Path(layout.__file__),source,source_observation,fit,ROUTES/'checks.json',ROUTES/'intent.json',*dependencies,
           ROOT/'hardware/electronics/full-cat/w5-installed-r52/owners.json',ROOT/'hardware/electronics/full-cat/w5-installed-r52/installed.brep']
    assert sha(source)==oldsha
    result=dict(status='SHARED_BUS_NATIVE_REJECTED' if hits or errors else 'SHARED_BUS_NATIVE_CLEAR_EXPORT_PENDING',
        hits=hits,errors=errors,changed_pairs=pairs,single_solid=True,new_support_strict_BOP_errors=0,
        full_final_strict_BOP_verified=False,parameter_DSeatHeight_mm=[5.2,5.3,5.2],parameter_volumes=[nominal,probe,shape.Volume],
        new_ties=3,reused_shared_W061_tie=1,new_fasteners=0,new_separate_prints=0,
        selected=False,W5_complete=False,physical_pass=False,closed_STL=False,relocated_reopen=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in paths},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in list(CAD.glob('*.FCStd'))+list(CAD.glob('*.brep'))+list(OUT.glob('*.brep'))},
        started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds())
    save(OUT/'checks.json',result);print('BUS_SHARED_CONTACTS',json.dumps(dict(hits=hits,errors=errors)),flush=True)
    if hits or errors:return
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    b=mesh.BoundBox;dims=[b.XLength,b.YLength,b.ZLength]
    assert dims[0]+6<=256 and dims[1]+6<=256 and dims[2]<=256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin);mesh.write(str(CAD/'BusSharedGrips_UNSELECTED_x1.stl'))
    for n in list(A.listDocuments()):A.closeDocument(n)
    with tempfile.TemporaryDirectory(prefix='robot-cat-shared-bus-') as td:
        tmp=Path(td)
        for p in [target]+dependencies:
            q=tmp/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        restored=A.openDocument(str(tmp/target.relative_to(ROOT)));restored.recompute()
        assert restored.BusDeckFinished.Shape.isValid() and len(restored.BusDeckFinished.Shape.Solids)==1
        assert abs(restored.BusDeckFinished.Shape.Volume-nominal)<max(1e-5,nominal*1e-8)
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
    result.update(status='SHARED_BUS_NATIVE_STATIC_COMPLETE_UNSELECTED',closed_STL=True,relocated_reopen=True,dimensions_mm=dims,
        files={p.relative_to(ROOT).as_posix():sha(p) for p in list(CAD.glob('*.FCStd'))+list(CAD.glob('*.brep'))+list(CAD.glob('*.stl'))+list(OUT.glob('*.brep'))},
        finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds())
    save(OUT/'checks.json',result)

if __name__=='__main__':main()
