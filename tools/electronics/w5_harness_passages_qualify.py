"""Qualify one saved native passage set without rebuilding its source tree.

Probe and restore a real clearance parameter on a separate document. This
does not qualify G1/G2 retention, restraint bands or whole W1/W5 assembly.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import tempfile
import w5_harness_passages_native as N
from servo_fuse_inputs_r1 import sha, save

OUT = N.BASE / 'w5-harness-passages-qualified-r1'
CAD = N.ROOT / 'hardware/cad/studies/w5-harness-passages-qualified-r1'
RECEIVED = N.OUT / 'checks.json'


def main():
    import FreeCAD as A, MeshPart
    begin = datetime.now(timezone.utc)
    assert not (OUT / 'checks.json').exists()
    receipt = json.loads(RECEIVED.read_text(encoding='utf-8'))
    assert receipt['geometry_valid']
    for rel, digest in {**receipt['source_sha256'], **receipt['files']}.items():
        assert sha(N.ROOT / rel) == digest, rel
    OUT.mkdir(parents=True, exist_ok=True)
    CAD.mkdir(parents=True, exist_ok=True)
    target = CAD / 'WholeHarnessPassages.FCStd'
    d = A.openDocument(str(N.CAD / 'WholeHarnessPassages.FCStd'))
    d.saveAs(str(target))
    owners = [r['owner'] for r in receipt['parts']]
    baseline = {r['owner']: r['remaining_mm3'] for r in receipt['parts']}
    state = dict(status='NATIVE_PASSAGE_QUALIFICATION_PENDING',
                 started_utc=begin.isoformat(), selected=False,
                 W1_complete=False, W5_complete=False, physical_pass=False)

    def checkpoint(stage, **values):
        state.update(stage=stage, **values)
        state['updated_utc'] = datetime.now(timezone.utc).isoformat()
        save(OUT / 'progress.json', state)
        print('PASSAGE_QUALIFICATION', stage, flush=True)

    checkpoint('cached_nominal_received')
    nominal = {o: d.getObject(o + 'HarnessFinished').Shape.Volume for o in owners}
    assert all(abs(nominal[o] - baseline[o]) < max(1e-5, baseline[o] * 1e-8) for o in owners)
    param = d.getObject('PassageParameters')
    param.RadialAllowance = .5
    checkpoint('parameter_0_5_recompute_started')
    d.recompute()
    probe = {}
    for owner in owners:
        s = d.getObject(owner + 'HarnessFinished').Shape
        assert s.isValid() and len(s.Solids) == 1, owner
        probe[owner] = s.Volume
        assert probe[owner] < nominal[owner], owner
    checkpoint('parameter_0_5_verified', probe_volumes_mm3=probe)
    param.RadialAllowance = .4
    checkpoint('nominal_restore_recompute_started')
    d.recompute()
    d.save()
    rows = []
    for owner in owners:
        s = d.getObject(owner + 'HarnessFinished').Shape
        assert s.isValid() and len(s.Solids) == 1, owner
        assert abs(s.Volume - baseline[owner]) < max(1e-5, baseline[owner] * 1e-8), owner
        s.check(True)
        p = CAD / (owner + '_CANDIDATE_WORLD.brep')
        s.exportBrep(str(p))
        mesh = MeshPart.meshFromShape(Shape=s, LinearDeflection=.08,
                                     AngularDeflection=.15, Relative=False)
        assert mesh.isSolid() and mesh.countComponents() == 1, owner
        bb = mesh.BoundBox
        dims = [bb.XLength, bb.YLength, bb.ZLength]
        assert max(dims) + 6 <= 256, (owner, dims)
        mesh.translate(-bb.XMin, -bb.YMin, -bb.ZMin)
        mesh.write(str(CAD / (owner + '_UNSELECTED_x1.stl')))
        rows.append(dict(owner=owner, nominal_mm3=s.Volume,
                         probe_mm3=probe[owner], restored=True, BOP_errors=0,
                         solids=1, closed_STL=True, dimensions_mm=dims))
        checkpoint('part_exported_' + owner, parts=rows)
    deps = list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values()
                             if q.FileName and Path(q.FileName) != target))
    assert all(p.is_relative_to(N.ROOT) for p in deps)
    for name in list(A.listDocuments()):
        A.closeDocument(name)
    with tempfile.TemporaryDirectory(prefix='robot-cat-whole-passages-') as td:
        tmp = Path(td)
        for p in [target, *deps]:
            dest = tmp / p.relative_to(N.ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
        relocated = A.openDocument(str(tmp / target.relative_to(N.ROOT)))
        relocated.recompute()
        for owner in owners:
            s = relocated.getObject(owner + 'HarnessFinished').Shape
            assert s.isValid() and len(s.Solids) == 1, owner
            assert abs(s.Volume - baseline[owner]) < max(1e-5, baseline[owner] * 1e-8), owner
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
        for name in list(A.listDocuments()):
            A.closeDocument(name)
    finish = datetime.now(timezone.utc)
    pins = [Path(__file__), Path(N.__file__), RECEIVED, *deps]
    state.update(status='NATIVE_PASSAGES_PARAMETER_EXPORT_REOPEN_COMPLETE',
                 parameter_probe_mm=[.4, .5, .4], parts=rows,
                 closed_STLs=True, relocated_reopen=True,
                 retained_wall_and_mount_review_pending=True,
                 registered_block_retention_pending=True,
                 restraints_complete=False,
                 finished_utc=finish.isoformat(),
                 worker_wall_seconds=(finish - begin).total_seconds(),
                 source_sha256={p.relative_to(N.ROOT).as_posix(): sha(p) for p in pins},
                 files={p.relative_to(N.ROOT).as_posix(): sha(p)
                        for p in CAD.iterdir() if p.suffix.lower() in ('.fcstd', '.brep', '.stl')})
    save(OUT / 'checks.json', state)
    checkpoint('complete')


if __name__ == '__main__':
    main()
