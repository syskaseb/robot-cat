"""Three native strap pockets from the exact R3 intersection witnesses.

Subtractive correction only: preserve every clear foreign interface from R3.
New Cut operates on the saved pilot, not repeated historical sweeps/imports.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, shutil, sys, tempfile
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import save, sha
import w5_bus_restraints_r3 as layout
OUT = ROOT/'hardware/electronics/full-cat/w5-bus-native-grips-r4'
CAD = ROOT/'hardware/cad/studies/w5-bus-native-grips-r4'
SOURCE = ROOT/'hardware/cad/studies/w5-bus-native-grips-r3/BusSharedGrips.FCStd'
PARENT = ROOT/'hardware/electronics/full-cat/w5-bus-native-grips-r3/checks.json'


def main():
    import FreeCAD as A
    import Part, MeshPart
    begin = datetime.now(timezone.utc)
    previous = json.loads(PARENT.read_text(encoding='utf-8'))
    assert previous['status'] == 'SHARED_BUS_NATIVE_REJECTED' and not previous['errors']
    keys = ['Plug/0', 'Plug/1', 'G2shared/top']
    assert {r['part'] for r in previous['hits']} == set(keys)
    assert all(r['owner']=='newDeck' for r in previous['hits'])
    assert sha(SOURCE) == previous['files'][SOURCE.relative_to(ROOT).as_posix()]
    OUT.mkdir(parents=True, exist_ok=True); CAD.mkdir(parents=True, exist_ok=True)
    assert not (OUT/'checks.json').exists()
    parent = A.openDocument(str(SOURCE))
    d = A.newDocument('BusStrapSlots')
    target = CAD/'BusStrapSlots.FCStd'; d.saveAs(str(target))
    link = d.addObject('App::Link','BusR3Deck'); link.setLink(parent.BusDeckFinished)
    link.LinkPlacement = parent.BusDeckFinished.Placement
    p = d.addObject('App::VarSet','StrapParameters')
    p.addProperty('App::PropertyLength','Allowance'); p.Allowance=.15
    cuttools=[]; witnesses=[]
    for i,key in enumerate(keys):
        tie = Part.read(str(PARENT.parent/(key.replace('/','_')+'.brep')))
        contact = parent.BusDeckFinished.Shape.common(tie)
        assert contact.Volume > 1e-5
        b = contact.BoundBox
        bounds = [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
        o = d.addObject('Part::Box','StrapPocket'+str(i))
        # Grow only the witnessed contact; no arbitrary whole-body notch.
        for prop, val in zip(('Length','Width','Height'),(b.XLength,b.YLength,b.ZLength)):
            o.setExpression(prop, str(val)+' mm + 2 * StrapParameters.Allowance')
        for axis, val in zip(('x','y','z'),bounds[:3]):
            o.setExpression('Placement.Base.'+axis, str(val)+' mm - StrapParameters.Allowance')
        cuttools.append(o)
        witnesses.append(dict(tie=key, mm3=contact.Volume, bounds_mm=bounds))
    tools=d.addObject('Part::Compound','StrapPocketTools'); tools.Links=cuttools
    f=d.addObject('Part::Cut','BusStrapSlotsFinished'); f.Base=link; f.Tool=tools
    d.save(); print('BUS_SLOTS_SOURCE_SAVED',json.dumps(witnesses),flush=True)
    d.recompute(); nominal=f.Shape.Volume
    assert f.Shape.isValid() and len(f.Shape.Solids)==1
    assert all(o.Shape.isValid() and not o.Shape.check(True) for o in cuttools)
    d.save(); print('BUS_SLOTS_NOMINAL_SAVED',flush=True)
    p.Allowance=.2;d.recompute();probe=f.Shape.Volume; assert probe < nominal
    p.Allowance=.15;d.recompute(); shape=f.Shape.copy()
    assert shape.isValid() and len(shape.Solids)==1 and abs(shape.Volume-nominal)<max(1e-5,nominal*1e-8)
    d.save(); shape.exportBrep(str(CAD/'Deck_WORLD.brep'))
    tools.Shape.exportBrep(str(CAD/'StrapPocketTools_WORLD.brep'))
    hits=[]
    for key in keys:
        tie=Part.read(str(PARENT.parent/(key.replace('/','_')+'.brep')))
        v=shape.common(tie).Volume
        if v>1e-5:hits.append(dict(part=key,owner='newDeck',mm3=v))
    dependencies=list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target))
    paths=[Path(__file__),Path(layout.__file__),SOURCE,PARENT,*dependencies]
    assert sha(SOURCE)==previous['files'][SOURCE.relative_to(ROOT).as_posix()]
    result=dict(status='BUS_SLOTS_REJECTED' if hits else 'BUS_SLOTS_CLEAR_EXPORT_PENDING',
        hits=hits,errors=[],single_solid=True,new_slot_strict_BOP_errors=0,
        full_final_strict_BOP_verified=False,closed_STL=False,relocated_reopen=False,
        inherited_clear_static_interfaces=PARENT.relative_to(ROOT).as_posix(),
        inherited_basis='New PartCut only subtracts three tools from identical R3 Deck; all already-clear foreign objects, whole wires and other straps retain clearance.',
        witnesses=witnesses,slot_allowance_mm=[.15,.2,.15],parameter_volumes=[nominal,probe,shape.Volume],
        new_ties=3,reused_shared_W061_tie=1,new_fasteners=0,new_separate_prints=0,
        selected=False,W5_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in paths},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in list(CAD.glob('*.FCStd'))+list(CAD.glob('*.brep'))},
        started_utc=begin.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=(datetime.now(timezone.utc)-begin).total_seconds())
    save(OUT/'checks.json',result); print('BUS_SLOTS_CONTACTS',json.dumps(hits),flush=True)
    if hits:return
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    b=mesh.BoundBox; dims=[b.XLength,b.YLength,b.ZLength]
    assert dims[0]+6<=256 and dims[1]+6<=256 and dims[2]<=256
    mesh.translate(-b.XMin,-b.YMin,-b.ZMin); mesh.write(str(CAD/'BusStrapSlots_UNSELECTED_x1.stl'))
    for name in list(A.listDocuments()):A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-bus-slots-') as td:
        tmp=Path(td)
        for q in [target]+dependencies:
            dest=tmp/q.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
        restored=A.openDocument(str(tmp/target.relative_to(ROOT)));restored.recompute()
        final=restored.BusStrapSlotsFinished.Shape
        assert final.isValid() and len(final.Solids)==1 and abs(final.Volume-nominal)<max(1e-5,nominal*1e-8)
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
    result.update(status='BUS_SLOTS_STATIC_COMPLETE_UNSELECTED',closed_STL=True,relocated_reopen=True,dimensions_mm=dims,
        files={q.relative_to(ROOT).as_posix():sha(q) for q in list(CAD.glob('*.FCStd'))+list(CAD.glob('*.brep'))+list(CAD.glob('*.stl'))},
        finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=(datetime.now(timezone.utc)-begin).total_seconds())
    save(OUT/'checks.json',result); print('BUS_SLOTS_EXPORT_COMPLETE',flush=True)


if __name__=='__main__':main()
