"""Finish the saved native passage after the separate volume diagnosis.

Do not repeat the successful nominal BOP or native parameter round trip.
Those assertions executed in R2 before its later volume-identity failure.
Receive the unchanged saved result, export it, and check relocated links.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/electronics'))
from servo_fuse_inputs_r1 import save, sha


def main():
    import FreeCAD as A
    import MeshPart
    start = datetime.now(timezone.utc)
    diagnosis = ROOT / 'hardware/electronics/full-cat/w5-g1-saved-volume-r1/checks.json'
    data = json.loads(diagnosis.read_text(encoding='utf-8'))
    # Volume integration over the same trimmed curved faces is not exact.
    # Explicit relative bound, not a changed physical-fit tolerance.
    tolerance = max(1e-5, 1e-8*abs(data['original_volume_mm3']))
    assert abs(data['signed_residual_mm3']) <= tolerance, data
    assert abs(data['original_vs_selected_source_volume_delta_mm3']) <= tolerance
    assert data['source_unchanged'] and data['tool_intersection_mm3'] > 0
    target = ROOT / 'hardware/cad/studies/w5-g1-passage-native-r2/DeckG1Passage.FCStd'
    assert sha(target) == data['source_sha256'][target.relative_to(ROOT).as_posix()]
    out = ROOT / 'hardware/electronics/full-cat/w5-g1-saved-export-r1'
    out.mkdir(parents=True, exist_ok=True)
    assert not (out/'checks.json').exists()
    doc = A.openDocument(str(target))
    final = doc.G1PassageFinished.Shape.copy()
    assert final.isValid() and len(final.Solids) == 1
    assert abs(doc.G1PassageParameters.Width.Value-5.8) < 1e-8
    nominal = final.Volume
    geometry = target.parent/'Deck_WORLD.brep'
    stl = target.parent/'DeckG1Passage_UNSELECTED_x1.stl'
    assert not geometry.exists() and not stl.exists()
    final.exportBrep(str(geometry))
    mesh = MeshPart.meshFromShape(Shape=final, LinearDeflection=.08, AngularDeflection=.15, Relative=False)
    assert mesh.isSolid() and mesh.countComponents() == 1
    bb = mesh.BoundBox
    dims = [bb.XLength, bb.YLength, bb.ZLength]
    assert dims[0]+6 <= 256 and dims[1]+6 <= 256 and dims[2] <= 256
    mesh.translate(-bb.XMin, -bb.YMin, -bb.ZMin); mesh.write(str(stl))
    external = list(dict.fromkeys(Path(q.FileName) for q in A.listDocuments().values()
                                 if q.FileName and Path(q.FileName) != target))
    pins = {p.relative_to(ROOT).as_posix():sha(p) for p in [target, diagnosis, Path(__file__)]+external}
    for name in list(A.listDocuments()): A.closeDocument(name)
    print('SAVED_G1_CLOSED_EXPORT_COMPLETE', flush=True)
    with tempfile.TemporaryDirectory(prefix='robot-cat-g1-saved-export-') as td:
        tmp = Path(td)
        for path in [target]+external:
            destination = tmp/path.relative_to(ROOT)
            destination.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(path, destination)
        reopened = A.openDocument(str(tmp/target.relative_to(ROOT)))
        reopened.recompute([reopened.G1WholePassageTool, reopened.G1PassageFinished])
        assert reopened.G1PassageFinished.Shape.isValid()
        assert abs(reopened.G1PassageFinished.Shape.Volume-nominal) <= tolerance
        assert all(Path(q.FileName).is_relative_to(tmp) for q in A.listDocuments().values())
        for name in list(A.listDocuments()): A.closeDocument(name)
    assert all(sha(ROOT/rel)==digest for rel,digest in pins.items())
    end = datetime.now(timezone.utc)
    save(out/'checks.json', dict(status='CURRENT_NATIVE_G1_PASSAGE_EXPORTED_W036_OPEN',
        final='G1PassageFinished', native=target.relative_to(ROOT).as_posix(),
        native_BOP_and_parameter_test='R2 assertions passed before later failed volume identity; console markers observed in session61942',
        BOP_repeat_performed=False, parameter_round_trip=[5.8,6,5.8],
        relative_volume_tolerance=1e-8, absolute_volume_tolerance_mm3=tolerance,
        volume_diagnosis=diagnosis.relative_to(ROOT).as_posix(),
        closed_STL=True, relocated_reopen=True, dimensions_mm=dims,
        total_brim_allowance_mm=6, selected=False, physical_pass=False,
        W036_complete=False, W5_complete=False, source_sha256=pins,
        files={p.relative_to(ROOT).as_posix():sha(p) for p in [geometry,stl]},
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    print('SAVED_G1_EXPORT_COMPLETE', dims, flush=True)


if __name__ == '__main__':
    main()
