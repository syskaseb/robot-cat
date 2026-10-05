"""Integrate received central retention into ONE editable linked Deck.

Run only after the complete R3 actual-material receipt is clear. Supplier
ties remain nominal envelopes. This does not close whole W1/W5 or physical fit.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import tempfile
import w5_central_retention_layout_r3 as R
from servo_fuse_inputs_r1 import sha, save

ROOT = R.N.ROOT
OUT = R.N.BASE/'w5-central-retention-native-r1'
CAD = ROOT/'hardware/cad/studies/w5-central-retention-native-r1'
PARENT = ROOT/'hardware/cad/studies/w5-harness-passages-qualified-r1/WholeHarnessPassages.FCStd'
QUALIFIED = R.N.BASE/'w5-harness-passages-qualified-r1/checks.json'


def main():
    import FreeCAD as A, Part, MeshPart
    begin = datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    proof_path = R.OUT/'checks.json'
    proof = json.loads(proof_path.read_text(encoding='utf-8'))
    assert proof['status'] == 'CENTRAL_RETENTION_LAYOUT_STATIC_CLEAR_NATIVE_PENDING'
    assert not proof['hits'] and not proof['errors']
    assert all(v > 0 for v in proof['stop_bearing_join_mm3'].values())
    qualified = json.loads(QUALIFIED.read_text(encoding='utf-8'))
    pins = [Path(__file__), Path(R.__file__), proof_path, QUALIFIED]
    for receipt in (proof, qualified):
        for rel, digest in {**receipt['source_sha256'], **receipt['files']}.items():
            p = ROOT/rel
            assert sha(p) == digest, rel
            pins.append(p)
    OUT.mkdir(parents=True, exist_ok=True)
    CAD.mkdir(parents=True, exist_ok=True)
    parent = A.openDocument(str(PARENT))
    source = parent.getObject('SourceDeckHarnessFinished')
    assert source is not None and source.Shape.isValid()
    d = A.newDocument('WholeHarnessCentralRetention')
    target = CAD/'WholeHarnessCentralRetention.FCStd'
    d.saveAs(str(target))
    param = d.addObject('App::VarSet', 'RetentionParameters')
    param.addProperty('App::PropertyLength', 'GrooveAllowance')
    param.GrooveAllowance = .2
    param.addProperty('App::PropertyString', 'InterfaceStatus')
    param.InterfaceStatus = 'Prototype candidate; physical tie/lever/pullout tests phase2'
    link = d.addObject('App::Link', 'ReceivedHarnessDeck')
    link.setLink(source)
    link.LinkPlacement = source.Placement
    roots, cutters = [], []

    def box(name, bounds, placement=None):
        q = d.addObject('Part::Box', name)
        q.Length, q.Width, q.Height = [bounds[i+3]-bounds[i] for i in range(3)]
        q.Placement.Base = A.Vector(*bounds[:3])
        if placement is not None:
            q.Placement = placement.multiply(q.Placement)
        return q

    for name, bounds in proof['specification']['stops']:
        roots.append(box(name, bounds))
    for row in proof['endpoint_recipes']:
        key = row['key']
        point = row['point_mm']
        placement = A.Placement(A.Vector(point[0], point[1], 0),
                                A.Rotation(A.Vector(0, 0, 1), row['angle_deg']))
        bounds = row['raw_seat_local_mm']
        roots.append(box(key+'InsulationSeatRaw', bounds, placement))
        bore = d.addObject('Part::Cylinder', key+'InsulationGroove')
        bore.setExpression('Radius', str(row['OD_mm']/2)+' mm + RetentionParameters.GrooveAllowance')
        bore.Height = bounds[4]-bounds[1]
        local = A.Placement(A.Vector(0, bounds[1], point[2]),
                            A.Rotation(A.Vector(0, 0, 1), A.Vector(0, 1, 0)))
        bore.Placement = placement.multiply(local)
        cutters.append(bore)
    for name, bounds in proof['slots_mm'].items():
        cutters.append(box(name+'NativeBandPassage', bounds))
    union = d.addObject('Part::MultiFuse', 'DeckAndIntegralRetentionRoots')
    union.Shapes = [link, *roots]
    union.Refine = False
    tool = d.addObject('Part::Compound', 'InsulationAndTieTools')
    tool.Links = cutters
    final = d.addObject('Part::Cut', 'CentralRetentionDeckFinished')
    final.Base, final.Tool = union, tool
    final.Refine = False
    d.save()
    state = dict(status='NATIVE_CENTRAL_RETENTION_PENDING',
                 started_utc=begin.isoformat(), selected=False,
                 W1_complete=False, W5_complete=False, physical_pass=False)

    def checkpoint(stage, **extra):
        state.update(stage=stage, updated_utc=datetime.now(timezone.utc).isoformat(), **extra)
        save(OUT/'progress.json', state)
        print('CENTRAL_RETENTION_NATIVE', stage, flush=True)

    checkpoint('editable_tree_saved', integral_roots=len(roots), native_tools=len(cutters))
    d.recompute()
    s = final.Shape
    assert s.isValid() and len(s.Solids) == 1, ('Native nominal Deck', len(s.Solids))
    nominal = s.Volume
    nominal_errors = s.check(True) or []
    assert not nominal_errors, nominal_errors
    checkpoint('nominal_valid', volume_mm3=nominal)
    param.GrooveAllowance = .3
    checkpoint('parameter_probe_started')
    d.recompute()
    s = final.Shape
    assert s.isValid() and len(s.Solids) == 1
    probe = s.Volume
    assert probe < nominal
    param.GrooveAllowance = .2
    checkpoint('nominal_restore_started', probe_mm3=probe)
    d.recompute()
    s = final.Shape
    assert s.isValid() and len(s.Solids) == 1
    assert abs(s.Volume-nominal) < max(1e-5, nominal*1e-8)
    assert not (s.check(True) or [])
    for q in d.Objects:
        if q != final and hasattr(q, 'ViewObject') and q.ViewObject:
            q.ViewObject.Visibility = False
    d.save()
    brep = CAD/'CentralRetentionDeck_CANDIDATE_WORLD.brep'
    s.exportBrep(str(brep))
    mesh = MeshPart.meshFromShape(Shape=s, LinearDeflection=.08,
                                 AngularDeflection=.15, Relative=False)
    assert mesh.isSolid() and mesh.countComponents() == 1
    bb = mesh.BoundBox
    dims = [bb.XLength, bb.YLength, bb.ZLength]
    assert max(dims)+6 <= 256, dims
    mesh.translate(-bb.XMin, -bb.YMin, -bb.ZMin)
    mesh.write(str(CAD/'CentralRetentionDeck_UNSELECTED_x1.stl'))
    checkpoint('closed_export_saved', dimensions_mm=dims)
    deps = list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values()
                             if q.FileName and Path(q.FileName) != target))
    assert all(p.is_relative_to(ROOT) for p in deps)
    for name in list(A.listDocuments()):
        A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-central-retention-') as td:
        tmp = Path(td)
        for p in [target, *deps]:
            dest = tmp/p.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
        relocated = A.openDocument(str(tmp/target.relative_to(ROOT)))
        relocated.recompute()
        shape = relocated.getObject('CentralRetentionDeckFinished').Shape
        assert shape.isValid() and len(shape.Solids) == 1
        assert abs(shape.Volume-nominal) < max(1e-5, nominal*1e-8)
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
        for name in list(A.listDocuments()):
            A.closeDocument(name)
    finish = datetime.now(timezone.utc)
    pins += deps
    state.update(status='CENTRAL_RETENTION_NATIVE_PARAMETER_EXPORT_REOPEN_COMPLETE',
                 solids=1, BOP_errors=0, closed_STL=True, relocated_reopen=True,
                 parameter_probe_mm=[.2, .3, .2], restored=True,
                 nominal_mm3=nominal, probe_mm3=probe,
                 integral_roots=len(roots), native_tools=len(cutters),
                 new_body_ties=2, new_insulation_ties=10, new_screws=0,
                 new_separate_prints=0, dimensions_mm=dims,
                 assembly=proof['assembly'],
                 physical_tie_pullout_creep_and_lever_tests_pending=True,
                 whole_restraints_motion_assembly_stock_selection_pending=True,
                 finished_utc=finish.isoformat(),
                 worker_wall_seconds=(finish-begin).total_seconds(),
                 source_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in dict.fromkeys(pins)},
                 files={p.relative_to(ROOT).as_posix(): sha(p) for p in CAD.iterdir()
                        if p.suffix.lower() in ('.fcstd', '.brep', '.stl')})
    save(OUT/'checks.json', state)
    checkpoint('complete')


if __name__ == '__main__':
    main()
