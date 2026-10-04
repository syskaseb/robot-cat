"""Native current-Deck G1.4 passage, no selected original overwritten.

The complete R3-R6 downwards departures share the same one witnessed
Deck intersection. Construct that whole passage once. Retain all closed
source/bank interfaces; the complete destination route remains OPEN.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/electronics'))
from servo_fuse_inputs_r1 import save, sha
OUT = ROOT / 'hardware/electronics/full-cat/w5-g1-passage-native-r1'
CAD = ROOT / 'hardware/cad/studies/w5-g1-passage-native-r1'


def main():
    import FreeCAD as A
    import Part
    import MeshPart
    start = datetime.now(timezone.utc)
    OUT.mkdir(parents=True, exist_ok=True); CAD.mkdir(parents=True, exist_ok=True)
    assert not (OUT / 'checks.json').exists(), 'Preserve completed source'
    source = ROOT / 'hardware/cad/studies/servo-fuse-left-mount-service-native-r7/LeftBankServiceMount.FCStd'
    target = CAD / 'DeckG1Passage.FCStd'
    assert not target.exists()
    digest = sha(source)
    fit = ROOT / 'hardware/electronics/full-cat/w5-front-return-r52-r6/checks.json'
    receipt = json.loads(fit.read_text(encoding='utf-8'))
    assert not receipt['errors']
    deck_hits = [r for r in receipt['hits'] if r['owner'] == 'CandidateDeck']
    assert len(deck_hits) == 1 and deck_hits[0]['segment'] == 1
    save(OUT / 'intent.json', dict(status='SAVED_BEFORE_NATIVE', selected=False,
        from_port='G1.4', cable_OD_mm=4.2, fixed_radius_mm=21,
        bounded_passage_mm=[70.6, 20.5, 102.5, 76.4, 37.5, 115.5],
        native=target.relative_to(ROOT).as_posix(), new_fasteners=0,
        condition='Complete W036 route, FR_G mount/orientation and underdeck restraints remain open',
        physical_pass=False, W5_complete=False))
    parent = A.openDocument(str(source))
    d = A.newDocument('DeckG1Passage')
    d.saveAs(str(target))
    p = d.addObject('App::VarSet', 'G1PassageParameters')
    for name, value in [('Width', 5.8), ('Length', 17), ('Height', 13)]:
        p.addProperty('App::PropertyLength', name); setattr(p, name, value)
    link = d.addObject('App::Link', 'SelectedR52Deck')
    link.setLink(parent.DeckLeftServiceMountFinished)
    link.LinkPlacement = parent.DeckLeftServiceMountFinished.Placement
    tool = d.addObject('Part::Box', 'G1WholePassageTool')
    tool.setExpression('Length', 'G1PassageParameters.Width')
    tool.setExpression('Width', 'G1PassageParameters.Length')
    tool.setExpression('Height', 'G1PassageParameters.Height')
    tool.setExpression('Placement.Base.x', '73.5 mm - G1PassageParameters.Width / 2')
    tool.Placement.Base.y = 20.5; tool.Placement.Base.z = 102.5
    final = d.addObject('Part::Cut', 'G1PassageFinished')
    final.Base = link; final.Tool = tool; final.Refine = False
    d.save()
    print('G1_NATIVE_SAVED_BEFORE_RECOMPUTE', flush=True)
    d.recompute(None, True, True)
    shape = final.Shape.copy()
    assert shape.isValid() and len(shape.Solids) == 1 and not shape.check(True)
    nominal = shape.Volume
    p.Width = 6; d.recompute(None, True, True); probe = final.Shape.Volume
    assert probe < nominal
    p.Width = 5.8; d.recompute(None, True, True)
    assert abs(final.Shape.Volume-nominal) < 1e-5
    # Check only the changed cable departure against this new Deck; unrelated
    # downstream contacts remain in R6, not silently suppressed by this result.
    routefile = ROOT / 'hardware/electronics/full-cat/w5-front-return-r52-r6/W036_DESIGN.brep'
    pieces = Part.read(str(routefile)).childShapes()
    intersections = [s.common(shape).Volume for s in pieces]
    assert all(v < 1e-5 for v in intersections), intersections
    original = link.Shape.copy()
    # Removal must be confined to the declared tool; no extra stock disappears.
    witness = original.common(tool.Shape)
    assert abs(original.Volume - nominal - witness.Volume) < 1e-5
    assert witness.Volume > 0
    external = list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values()
                                if q.FileName and Path(q.FileName) != target))
    d.save(); shape.exportBrep(str(CAD / 'Deck_WORLD.brep'))
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=.08, AngularDeflection=.15, Relative=False)
    assert mesh.isSolid() and mesh.countComponents() == 1
    bb = mesh.BoundBox; dims = [bb.XLength, bb.YLength, bb.ZLength]
    assert dims[0]+6 <= 256 and dims[1]+6 <= 256 and dims[2] <= 256
    mesh.translate(-bb.XMin, -bb.YMin, -bb.ZMin)
    mesh.write(str(CAD / 'DeckG1Passage_UNSELECTED_x1.stl'))
    for name in list(A.listDocuments()): A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-g1-passage-') as td:
        tmp = Path(td)
        for path in [target] + external:
            destination = tmp / path.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(path, destination)
        reopened = A.openDocument(str(tmp / target.relative_to(ROOT)))
        reopened.recompute(None, True, True)
        assert reopened.G1PassageFinished.Shape.isValid()
        assert abs(reopened.G1PassageFinished.Shape.Volume - nominal) < 1e-5
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
        for name in list(A.listDocuments()): A.closeDocument(name)
    assert sha(source) == digest
    end = datetime.now(timezone.utc)
    pins = {q.relative_to(ROOT).as_posix(): sha(q) for q in [source, fit, routefile, Path(__file__)] + external}
    save(OUT / 'checks.json', dict(status='G1_CURRENT_DECK_PASSAGE_NATIVE_COMPLETE_W036_OPEN',
        native=target.relative_to(ROOT).as_posix(), final='G1PassageFinished',
        single_solid=True, strict_BOP_errors=0, closed_STL=True,
        relocated_reopen=True, source_unchanged=True, native_tool='Parametric PartBox and PartCut of linked selected R52 native Deck',
        cable_departure_intersections_mm3=intersections, removed_stock_mm3=witness.Volume,
        removed_stock_confined_to_tool=True, parameter_width_mm=[5.8, 6, 5.8],
        parameter_volumes_mm3=[nominal, probe, nominal], dimensions_mm=dims,
        total_brim_allowance_mm=6, selected=False, physical_pass=False,
        W036_complete=False, W5_complete=False, new_fasteners=0,
        source_sha256=pins, started_utc=start.isoformat(), finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds()))
    print('G1_NATIVE_COMPLETE', json.dumps(dict(removed_mm3=witness.Volume, dimensions_mm=dims)), flush=True)


if __name__ == '__main__':
    main()
