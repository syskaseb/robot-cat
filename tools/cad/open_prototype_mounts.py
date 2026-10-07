"""Bounded stage-2 native mounting work; preserve retained historical sources.

First operation repairs MAIN's absolute expression in the editable neck master.
This does not redesign the mount, repeat its contact checks or qualify all W5.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import time

from correct_open_prototype_plan_reference import sha, fingerprint, compare_saved_shape

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2'
OUT = BASE / 'open-prototype/mounting-checkpoint'
SOURCE = BASE / 'neck-support/main-mount-sequence/NeckMainMount.FCStd'
SOURCE_SHA = '2e2a810418157f39f305a8869a784692597414f4c3ab6e0178f623be12e56988'


def validate(doc):
    doc.recompute()
    left = doc.LeftRiser
    assert left.Tip.Name == 'MainBoltClearance'
    for ob in left.Group:
        assert 'Invalid' not in ob.State and 'Touched' not in ob.State, (ob.Name, ob.State)
        if ob.TypeId == 'Sketcher::SketchObject':
            assert ob.FullyConstrained and ob.solve() == 0, ob.Name
    assert left.Tip.Shape.isValid() and len(left.Tip.Shape.Solids) == 1
    assert not left.Tip.Shape.check(True)
    expected = 46.52 + doc.Parameters.MainGap.Value - 4
    for name in ('MainSupplierFamily', 'MAIN4853_CP2'):
        ob = doc.getObject(name)
        assert ob.Shape.isValid(), name
        assert abs(ob.Placement.Base.z - expected) < 1e-8, (name, ob.Placement.Base.z)
        assert abs(ob.Shape.BoundBox.ZMin - expected) < 1e-8, (name, ob.Shape.BoundBox.ZMin)
    return dict(gap_mm=doc.Parameters.MainGap.Value, board_base_z_mm=expected,
                mount_volume_mm3=left.Tip.Shape.Volume,
                fully_constrained_sketches=sum(o.TypeId == 'Sketcher::SketchObject' for o in left.Group))


def main():
    import FreeCAD as A
    tick = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    assert sha(SOURCE) == SOURCE_SHA, 'Retained master changed: inspect, do not overwrite'
    target = OUT / 'Mounts.FCStd'
    proof = OUT / 'main-expression-checks.json'
    recover = sys.argv[1:] == ['--verify-existing']
    assert recover or not sys.argv[1:]
    assert not proof.exists(), 'Completed result exists; do not repeat'
    assert target.exists() if recover else not target.exists(), 'Recover existing result, never regenerate unchanged'
    prior = json.loads((SOURCE.parent / 'checks.json').read_text(encoding='utf-8'))
    assert prior['native_sha256'] == SOURCE_SHA
    assert sha(ROOT / prior['stl']['path']) == prior['stl']['sha256']
    doc = A.openDocument(str(SOURCE))
    try:
        before = {o.Name: fingerprint(o) for o in doc.Objects if 'Shape' in o.PropertiesList
                  and o.Name not in ('MainSupplierFamily', 'MAIN4853_CP2')}
        # Intermediate PartDesign caches may be rebuilt with different OCC
        # topology ordering after the parameter cycle. They are not independent
        # hardware parts: compare the final Body and all other parts/references,
        # and separately validate the entire editable feature tree.
        bodies = [o for o in doc.Objects if o.TypeId == 'PartDesign::Body']
        intermediate = {o.Name for body in bodies for o in body.Group}
        body_names = {o.Name for o in bodies}
        for name in intermediate:
            before.pop(name,None)
        old_z = {n: doc.getObject(n).Placement.Base.z for n in ('MainSupplierFamily', 'MAIN4853_CP2')}
        assert doc.Parameters.MainGap.Value == 4
        for name in old_z:
            doc.getObject(name).setExpression('Placement.Base.z', '46.52 mm + Parameters.MainGap - 4 mm')
        baseline = validate(doc)
        doc.Parameters.MainGap = 5
        changed = validate(doc)
        assert changed['mount_volume_mm3'] > baseline['mount_volume_mm3']
        doc.Parameters.MainGap = 4
        restored = validate(doc)
        assert abs(restored['mount_volume_mm3'] - baseline['mount_volume_mm3']) < 1e-6
        doc.Label = 'Open prototype common mounts - editable Stage 2'
        if not recover:
            doc.saveAs(str(target))
    finally:
        A.closeDocument(doc.Name)
    doc = A.openDocument(str(target))
    try:
        reopened = validate(doc)
        after = {o.Name: fingerprint(o) for o in doc.Objects if 'Shape' in o.PropertiesList
                 and o.Name not in ('MainSupplierFamily', 'MAIN4853_CP2') and o.Name not in intermediate}
        assert after.keys() == before.keys()
        errors = {}
        compound_metadata = []
        final_body_geometry = []
        for n in before:
            if n in body_names:
                import Part
                original = Part.Shape()
                original.importBrepFromString(before[n][0])
                current = doc.getObject(n).Shape
                assert before[n][1:] == after[n][1:], (n,'Placement changed')
                assert original.isValid() and current.isValid()
                assert len(original.Solids) == len(current.Solids) == 1
                assert len(original.Vertexes) == len(current.Vertexes)
                differences = [original.cut(current).Volume,current.cut(original).Volume]
                assert max(differences) < 1e-8, (n,differences)
                final_body_geometry.append(dict(object=n,symmetric_difference_mm3=differences,
                    vertices=len(current.Vertexes),placement_unchanged=True))
                continue
            try:
                errors[n] = compare_saved_shape(before[n], after[n])
            except AssertionError as exc:
                # The PartDesign Body wrapper becomes a free compound after
                # recompute. This exact wrapper-bit change is not a dimension:
                # keep every other full BRep record/placement comparison, and
                # independently require zero solid symmetric difference.
                old, new = before[n][0], after[n][0]
                marker = '\nCo\n\n0100000\n'
                replacement = '\nCo\n\n1100000\n'
                assert n == 'LeftRiser' and old.count(marker) == 1, (n, str(exc))
                normalized = (old.replace(marker,replacement), *before[n][1:])
                errors[n] = compare_saved_shape(normalized,after[n])
                import Part
                original = Part.Shape()
                original.importBrepFromString(old)
                current = doc.getObject(n).Shape
                assert original.isValid() and current.isValid()
                assert original.cut(current).Volume < 1e-8 and current.cut(original).Volume < 1e-8
                assert len(original.Vertexes) == len(current.Vertexes)
                compound_metadata.append(dict(object=n,old='0100000',new='1100000',
                    location='Outer Co wrapper only',solid_symmetric_difference_mm3=0))
        expressions = {n: doc.getObject(n).ExpressionEngine for n in old_z}
    finally:
        A.closeDocument(doc.Name)
    assert sha(SOURCE) == SOURCE_SHA
    result = dict(status='ABSOLUTE_MAIN_DATUM_AND_EDITABLE_MASTER_REPAIRED',
        selected=False, stage2_complete=False, W5_complete=False, physical_pass=False,
        started_utc=started, finished_utc=datetime.now(timezone.utc).isoformat(),
        worker_wall_seconds=round(time.monotonic()-tick,3),
        source=str(SOURCE.relative_to(ROOT)), source_sha256=SOURCE_SHA,
        native=str(target.relative_to(ROOT)), native_sha256=sha(target),
        script_sha256=sha(Path(__file__)), previous_base_z_mm=old_z,
        absolute_parameter_test=[baseline,changed,restored], reopened=reopened,
        expressions=expressions, unchanged_shapes_and_placements=len(before),
        maximum_BRep_roundtrip_error=max(errors.values(),default=0),
        compound_wrapper_metadata_changes=compound_metadata,
        final_physical_bodies_geometry_checks=final_body_geometry,
        intermediate_feature_caches_regenerated_not_independent_parts=sorted(intermediate),
        retained_export=prior['stl'], no_mount_geometry_change=True,
        no_repeated_contact_or_export_tests=True, source_unchanged=True,
        remaining=['Common PCB supports and distribution tie rails',
                   'Fasteners, tool/assembly access and required new printable exports'])
    proof.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__ == '__main__':
    main()
