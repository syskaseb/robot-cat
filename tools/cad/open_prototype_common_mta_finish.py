"""Qualify fresh native reopen and candidate exports, not full wiring.

Reuse received 87 changed-interface pairs. No unchanged collision rerun.
Preserve previous source/rail modules and the received combined native file.
"""
from datetime import datetime, timezone
from pathlib import Path
import json, shutil, tempfile, time
import FreeCAD as A
import Mesh, MeshPart
from open_prototype_common_mta_mounts import MODEL, PROOF, OUT
from open_prototype_shared_distribution_carriers import validate
from open_prototype_wiring_endpoints import ROOT, read, sha


def main():
    tick = time.monotonic()
    dest = OUT / 'common-mta-mount-package.json'
    assert not dest.exists(), 'Receive existing finish result before rerunning'
    prior = read(PROOF)
    assert prior['status'] == 'NATIVE_COMMON4MTA_MOUNTS_STATIC_CLEAR_FULL8TAILS_OPEN'
    assert not any(prior[k] for k in ('contacts', 'errors', 'outside_torso'))
    assert sha(MODEL) == prior['model_sha256']
    for name, digest in prior['source_sha256'].items():
        assert sha(ROOT / name) == digest, name
    names = ('UpperCarrier', 'CommonSourcePlatform',
             'LeftDistributionCarrier', 'RightDistributionCarrier')
    r = dict(schema_version=1, readiness='prototype', selected=False,
             stage_completed=False, physical_pass=False, status='PENDING',
             source_sha256=prior['source_sha256'], model_sha256=sha(MODEL),
             reused_changed_interface_proof=PROOF.relative_to(ROOT).as_posix(),
             tested_pairs=prior['tested_pairs'], contacts=prior['contacts'],
             errors=prior['errors'], outside_torso=prior['outside_torso'],
             native_geometry=prior['native_geometry'],
             assembly=prior['assembly'], load_path=prior['load_path'],
             new_hardware_candidate=prior['new_hardware_candidate'],
             physical_gates=prior['physical_gates'], remaining=prior['remaining'],
             gates={name:dict(status='open', reason=reason) for name,reason in dict(
                 assembly='Local mount sequence only; whole wired installation/removal open',
                 electrical='Full8tails/terminations/insulation/materials/E3 open',
                 fit='Delivered casing/ties/lead dimensions and no-crush/no-slip fit',
                 geometry='Changed static mount interfaces qualified; full routes not included',
                 loads='Retained bolt load path/cantilever/vibration trial open',
                 petg='Profile/support removal/bridges/layers/creep trial open',
                 service='Actual ATO lid motion and connected wiring service open').items()})
    doc = None
    try:
        with tempfile.TemporaryDirectory(prefix='robot-cat-mta-reopen-') as temp:
            moved = Path(temp) / MODEL.name
            shutil.copy2(MODEL, moved)
            doc = A.openDocument(str(moved))
            bodies = [doc.getObject(n) for n in names]
            baseline = validate(doc, bodies)
            for name, v in baseline.items():
                assert abs(v - prior['native_geometry']['volumes_mm3'][name]) < 1e-6
            doc.MTAParameters.RearPostDiameter = 9
            trial = validate(doc, bodies)
            for name in names[2:]:
                assert trial[name] > baseline[name]
            doc.MTAParameters.RearPostDiameter = 8
            restored = validate(doc, bodies)
            assert all(abs(v - restored[n]) < 1e-6 for n, v in baseline.items())
            r['fresh_relocated_reopen_parameter_restore'] = True
            r['parameter_test'] = dict(rear_post_diameter_mm=[8, 9, 8],
                                       restored=True, integral_root_width_follows=True)
            r['exports'] = []
            for b in bodies:
                shape = b.Shape.copy()
                box = shape.BoundBox
                dimensions = [box.XLength, box.YLength, box.ZLength]
                assert max(dimensions) < 246
                shape.translate(-A.Vector(box.XMin, box.YMin, box.ZMin))
                mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=.15,
                                              AngularDeflection=.2, Relative=False)
                assert mesh.isSolid(), b.Name
                path = OUT / (b.Name + 'MtaCurrent.stl')
                assert not path.exists(), 'Preserve earlier exports: ' + path.name
                mesh.write(str(path))
                assert Mesh.Mesh(str(path)).isSolid()
                r['exports'].append(dict(path=path.relative_to(ROOT).as_posix(),
                                          sha256=sha(path), dimensions_mm=dimensions,
                                          closed=True, selected=False))
        r['files'] = [dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p))
                      for p in (MODEL, PROOF, Path(__file__),
                                ROOT / 'tools/cad/open_prototype_common_mta_mounts.py')]
        r['files'] += [dict(path=q['path'], sha256=q['sha256']) for q in r['exports']]
        r['status'] = 'COMMON4MTA_NATIVE_MOUNTS_PREPARED_FULL8TAILS_AND_WIRING_OPEN'
    except Exception as error:
        r['status'] = 'MTA_REOPEN_EXPORT_GATE_ERROR'
        r['errors'].append(dict(error=repr(error)))
        raise
    finally:
        if doc and doc.Name in A.listDocuments():
            A.closeDocument(doc.Name)
        r.update(worker_seconds=time.monotonic()-tick,
                 finished_utc=datetime.now(timezone.utc).isoformat())
        dest.write_text(json.dumps(r, indent=2)+'\n', encoding='utf-8')
    assert sha(MODEL) == r['model_sha256']
    assert all(sha(ROOT/n) == v for n, v in r['source_sha256'].items())
    print(json.dumps(dict(status=r['status'], exports=len(r['exports']),
                          worker_seconds=r['worker_seconds'])), flush=True)


if __name__ == '__main__':
    main()
