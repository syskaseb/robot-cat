"""Receive the saved R2 result; diagnose its failed volume identity only.

No recompute or repeated full BOP. Preserve the failed run and do not infer
completion, selection or physical fit from a valid saved native shape.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/electronics'))
from servo_fuse_inputs_r1 import save, sha


def main():
    import FreeCAD as A
    import Part
    start = datetime.now(timezone.utc)
    target = ROOT / 'hardware/cad/studies/w5-g1-passage-native-r2/DeckG1Passage.FCStd'
    out = ROOT / 'hardware/electronics/full-cat/w5-g1-saved-volume-r1'
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / 'checks.json').exists()
    before = sha(target)
    doc = A.openDocument(str(target))
    original = doc.SelectedR52Deck.Shape.copy()
    final = doc.G1PassageFinished.Shape.copy()
    tool = doc.G1WholePassageTool.Shape.copy()
    print('SAVED_NATIVE_LOADED', original.Volume, final.Volume, flush=True)
    assert original.isValid() and final.isValid() and len(final.Solids) == 1
    witness = original.common(tool)
    residual = original.Volume - final.Volume - witness.Volume
    same_source = Part.read(str(ROOT / 'hardware/cad/studies/servo-fuse-left-mount-service-native-r7/Deck_WORLD.brep'))
    end = datetime.now(timezone.utc)
    save(out / 'checks.json', dict(status='FAILED_R2_VOLUME_IDENTITY_DIAGNOSIS_ONLY',
        original_volume_mm3=original.Volume, final_volume_mm3=final.Volume,
        removed_by_subtraction_mm3=original.Volume-final.Volume,
        tool_intersection_mm3=witness.Volume, signed_residual_mm3=residual,
        old_absolute_tolerance_mm3=1e-5,
        original_vs_selected_source_volume_delta_mm3=original.Volume-same_source.Volume,
        final_valid=True, final_solids=len(final.Solids), selected=False,
        physical_pass=False, W5_complete=False, source_unchanged=sha(target)==before,
        source_sha256={target.relative_to(ROOT).as_posix(): before,
            'tools/electronics/w5_g1_saved_volume_r1.py': sha(Path(__file__)),
            'hardware/cad/studies/servo-fuse-left-mount-service-native-r7/Deck_WORLD.brep': sha(ROOT/'hardware/cad/studies/servo-fuse-left-mount-service-native-r7/Deck_WORLD.brep')},
        started_utc=start.isoformat(), finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds()))
    print('SAVED_VOLUME_DIAGNOSIS', residual, witness.Volume, flush=True)
    for name in list(A.listDocuments()): A.closeDocument(name)


if __name__ == '__main__':
    main()
