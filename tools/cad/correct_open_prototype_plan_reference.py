"""Correct one saved reference datum, not physical mount geometry.

The retained source is never saved. This creates one stage-1 planning copy
and verifies every other stored shape/placement after reopening it.
"""
from pathlib import Path
import hashlib
import json
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
SOURCE_HASH = '19bf2ea51e2d2c6deb6c0416c1290fd9e04c29453ce58be38edcd63663bbd6c1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprint(ob):
    shape = ob.Shape
    return (shape.exportBrepToString(),
            tuple(ob.Placement.Base), tuple(ob.Placement.Rotation.Q))


NUMBER = re.compile(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')


def compare_saved_shape(before, after):
    """OCC save/reload may round the BRep text; never waive topology changes.

    Compare complete records, not bounding boxes or volume alone. Non-numeric
    structure and every entity index must match. Allow only <=1e-10 absolute
    numeric roundoff, and require exactly unchanged object placement.
    """
    assert before[1:] == after[1:], 'Placement changed'
    left, right = before[0], after[0]
    if left == right:
        return 0.0
    assert NUMBER.sub('#', left) == NUMBER.sub('#', right), 'BRep structure changed'
    a, b = NUMBER.findall(left), NUMBER.findall(right)
    assert len(a) == len(b)
    error = max((abs(float(x)-float(y)) for x,y in zip(a,b)), default=0.0)
    assert error <= 1e-10, f'BRep numeric change exceeds save/reload roundoff: {error}'
    return error


def bounds(shape):
    b = shape.BoundBox
    return [b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax]


def main():
    import FreeCAD as A
    tick = time.monotonic()
    source = PACKAGE / 'OpenPrototype.FCStd'
    target = PACKAGE / 'OpenPrototypePlan.FCStd'
    proof = PACKAGE / 'reference-frame-correction.json'
    assert sha(source) == SOURCE_HASH, 'Source changed; do not apply a stale correction'
    recover = sys.argv[1:] == ['--verify-existing']
    assert recover or not sys.argv[1:], 'Unknown argument'
    assert not proof.exists(), 'Result already exists; do not repeat the operation'
    assert target.exists() if recover else not target.exists(), 'Use --verify-existing to recover a saved result'
    mount = json.loads((PACKAGE.parent / 'neck-support/main-mount-sequence/checks.json').read_text(encoding='utf-8'))
    expected_z = mount['hardware'][0]['underhead_z_mm'] - 1.5748 - .3
    assert abs(expected_z - (min(e['point_mm'][2] for e in mount['affected_main_ends']) - 1.5748)) < 1e-8
    doc = A.openDocument(str(source))
    try:
        main_ref = doc.getObject('MainSupplierFamily')
        assert main_ref and main_ref.Shape.isValid()
        assert not main_ref.ExpressionEngine, 'Inspect unexpected live expressions before changing the snapshot'
        unchanged = {o.Name: fingerprint(o) for o in doc.Objects
                     if o.Name != main_ref.Name and 'Shape' in o.PropertiesList}
        old_bounds = bounds(main_ref.Shape)
        delta_z = expected_z - old_bounds[2]
        expected = main_ref.Shape.copy()
        expected.translate(A.Vector(0, 0, delta_z))
        placement = main_ref.Placement
        placement.Base.z += delta_z
        main_ref.Placement = placement
        assert main_ref.Shape.isValid()
        assert all(abs(a-b) < 1e-8 for a, b in zip(bounds(main_ref.Shape), bounds(expected)))
        assert len(main_ref.Shape.Vertexes) == len(expected.Vertexes)
        assert max((a.Point-b.Point).Length for a,b in zip(main_ref.Shape.Vertexes, expected.Vertexes)) < 1e-8
        if not recover:
            doc.Label = 'Open prototype stage-1 plan, corrected MAIN reference'
            doc.saveAs(str(target))
    finally:
        A.closeDocument(doc.Name)
    reopened = A.openDocument(str(target))
    try:
        ref = reopened.getObject('MainSupplierFamily')
        assert ref.Shape.isValid()
        assert all(abs(a-b) < 1e-8 for a, b in zip(bounds(ref.Shape), bounds(expected)))
        after = {o.Name: fingerprint(o) for o in reopened.Objects
                 if o.Name != ref.Name and 'Shape' in o.PropertiesList}
        assert after.keys() == unchanged.keys(), 'Unrelated shape added or removed'
        errors = {name: compare_saved_shape(unchanged[name], after[name]) for name in unchanged}
        changed_text = sum(unchanged[name][0] != after[name][0] for name in unchanged)
        assert abs(ref.Shape.Volume-expected.Volume) < 1e-8
        bb = ref.Shape.BoundBox
        assert all(bb.isInside(A.Vector(*e['point_mm'])) for e in mount['affected_main_ends'])
        final_bounds = bounds(ref.Shape)
    finally:
        A.closeDocument(reopened.Name)
    assert sha(source) == SOURCE_HASH
    result = dict(status='REFERENCE_SNAPSHOT_CORRECTED_NOT_HARDWARE_QUALIFIED',
        source_sha256=SOURCE_HASH, target_sha256=sha(target), target=str(target.relative_to(ROOT)),
        script_sha256=sha(Path(__file__)), corrected_object='MainSupplierFamily',
        translation_mm=[0,0,delta_z], previous_bounds_mm=old_bounds,
        corrected_bounds_mm=final_bounds, independent_support_plane_mm=expected_z,
        four_nominal_pads_inside_reference=True, corrected_shape_valid=True,
        unchanged_shape_and_placement_count=len(unchanged),
        unaffected_BRep_structure_and_placements_preserved=True,
        BRep_text_roundtrip_difference_count=changed_text,
        maximum_BRep_numeric_roundtrip_error=max(errors.values(),default=0.0),
        allowed_BRep_numeric_roundtrip_error=1e-10,
        source_unchanged=True, save_reopen_verified=True,
        no_mount_or_wire_geometry_changed=True, supplier_family_not_delivered_SKU=True,
        no_full_assembly_collision_claim=True, no_physical_pass=True,
        worker_wall_seconds=round(time.monotonic()-tick,3))
    proof.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False),flush=True)


if __name__ == '__main__':
    main()
