"""Read the saved assembly once for stage-1 planning; no recompute or save.

The legacy layout inventory predates the MAIN move. Read current reference
geometry, rather than applying its world placement a second time. Commercial
reservations remain reservations, not measured delivered parts.
"""
from pathlib import Path
import hashlib
import json
import time

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'


def main():
    import FreeCAD as A
    native = PACKAGE / 'OpenPrototype.FCStd'
    before = hashlib.sha256(native.read_bytes()).hexdigest()
    mount_path = PACKAGE.parent / 'neck-support/main-mount-sequence/checks.json'
    mount = json.loads(mount_path.read_text(encoding='utf-8'))
    tick = time.monotonic()
    d = A.openDocument(str(native))
    try:
        rows = []
        for ob in d.Objects:
            if not (ob.Name.endswith('_CP2') or ob.Name in
                    ['MainSupplierFamily', 'LeftRiserWithMain', 'RightRiser']):
                continue
            if ob.Name.startswith(('Access_', 'W0', 'XA')) or ob.Name == 'MAIN4853_CP2':
                continue
            if 'Shape' not in ob.PropertiesList or ob.Shape.isNull():
                continue
            bb = ob.Shape.BoundBox
            rows.append(dict(name=ob.Name, bounds_mm=[bb.XMin, bb.YMin, bb.ZMin,
                bb.XMax, bb.YMax, bb.ZMax], origin_mm=list(ob.Placement.Base),
                rotation_xyzw=list(ob.Placement.Rotation.Q),
                basis='Saved current geometry; commercial shape may be a reservation'))
        current = d.getObject('MainSupplierFamily')
        assert current and current.Shape.isValid()
        # Independent records agree on the intended PCB support plane. The
        # earlier builder overwrote its world Z using MainGap-4 on Placement.
        # Diagnose the reference, not a new physical bracket/route variant.
        pcb_thickness = 1.5748  # retained supplier-family prototype, not delivery measurement
        expected_from_bolt = mount['hardware'][0]['underhead_z_mm'] - pcb_thickness - .3
        expected_from_pads = min(row['point_mm'][2] for row in mount['affected_main_ends']) - pcb_thickness
        assert abs(expected_from_bolt - expected_from_pads) < 1e-7
        dz = expected_from_bolt - current.Shape.BoundBox.ZMin
        normalized = current.Shape.copy()
        normalized.translate(A.Vector(0, 0, dz))
        assert normalized.isValid()
        bb = normalized.BoundBox
        normalized_bounds = [bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax]
        assert all(bb.XMin <= e['point_mm'][0] <= bb.XMax and
                   bb.YMin <= e['point_mm'][1] <= bb.YMax and
                   bb.ZMin <= e['point_mm'][2] <= bb.ZMax for e in mount['affected_main_ends'])
        result = dict(native_sha256=before, inventory=rows,
            legacy_MAIN4853_CP2_excluded=True,
            main_geometry_source='MainSupplierFamily; world-space snapshot, do not transform twice',
            main_reference_issue=dict(saved_board_z_min_mm=current.Shape.BoundBox.ZMin,
                expected_board_z_min_from_bolt_mm=expected_from_bolt,
                expected_board_z_min_from_pad_mm=expected_from_pads,
                required_reference_translation_mm=[0, 0, dz],
                intended_reference_bounds_mm=normalized_bounds,
                transformed_reference_valid=True, four_nominal_pads_inside_bounds=True,
                source='whole_cat_neck_main_mount.py: Placement.Base.z=MainGap-4 resets the world base, while contact report tested separate ref',
                next='Correct only the reference placement in the working copy and test the MAIN gap roundtrip; preserve all mount parts and source checkpoints',
                saved_reference_not_qualified=True),
            no_geometry_recomputed_or_saved=True,
            worker_wall_seconds=round(time.monotonic()-tick, 3))
    finally:
        A.closeDocument(d.Name)
    assert hashlib.sha256(native.read_bytes()).hexdigest() == before
    print(json.dumps(result, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
