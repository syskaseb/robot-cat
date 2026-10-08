"""Read-only shared source allocation check; distinguish real material/reservations.

No master edits, route acceptance, measured commercial geometry or physical PASS.
Only five changed holder allocations are tested, not the retained whole robot.
"""
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from open_prototype_wiring_endpoints import ROOT, BASE, CURRENT, read, sha, bounds


def input_path(A, Part, row, radius):
    """Exact tangent planned centreline; commercial cable properties still open."""
    start, finish = A.Vector(*row['input_exit_mm']), A.Vector(*row['target_entry_mm'])
    departure = A.Vector(*row['input_departure'])
    recipe = row['input_recipe']
    edges = []
    if recipe['quarter_arc_count']:
        toward = A.Vector(0,1 if finish.y > start.y else -1,0)
        r = recipe['quarter_radius_mm']
        p1 = start + departure*recipe['exit_straight_mm']
        p2 = p1 + departure*r + toward*r
        centre = p1 + toward*r
        middle = centre + (departure-toward)*(r/math.sqrt(2))
        edges = [Part.makeLine(start,p1),Part.Arc(p1,middle,p2).toShape(),Part.makeLine(p2,finish)]
    else:
        edges = [Part.makeLine(start,finish)]
    path = Part.Wire(edges)
    profile = Part.Wire(Part.makeCircle(radius,start,departure))
    solid = path.makePipeShell([profile],True,False)
    assert solid.isValid() and len(solid.Solids)==1
    strip = row['nominal_input_blank_mm']-path.Length
    assert abs(strip-(14 if row['holder'] in ('F_PI','F_AUX') else 11)) < 1e-7
    return solid, dict(holder=row['holder'],outside_centreline_mm=path.Length,
        nominal_input_blank_mm=row['nominal_input_blank_mm'],strip_allowance_mm=strip,
        insulated_entry_grip_straight_mm=recipe['entry_straight_mm'],
        swept_solid_valid=True, factory_OD_and_R6_not_measured=True)


def main():
    import FreeCAD as A
    import Part
    tick = time.monotonic()
    plan_path = BASE / 'wiring-checkpoint/source-layout-plan.json'
    context_path = BASE / 'OpenPrototypePlan.FCStd'
    plan = read(plan_path)
    context = A.openDocument(str(context_path))
    mounts = A.openDocument(str(CURRENT))
    paths = [plan_path, CURRENT, context_path, Path(__file__)]
    pins = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    targets = {}
    input_rows = []
    for row in plan['source_plan']:
        b = row['proposed_body_bounds_mm']
        targets[row['holder']] = Part.makeBox(*(b[i+3]-b[i] for i in range(3)), A.Vector(*b[:3]))
        shape, data = input_path(A,Part,row,plan['input_wire_diameter_design_allowance_mm']/2)
        targets[row['holder']+'_input'] = shape
        input_rows.append(data)
    material, reservations = {}, {}
    for o in context.Objects:
        if 'Shape' not in o.PropertiesList or o.Shape.isNull():
            continue
        if o.Name.startswith(('P0_', 'S1_ring_', 'S1_screw_')) or o.Name in ('LeftRiserWithMain', 'RightRiser', 'MainSupplierFamily'):
            material['context/'+o.Name] = o.Shape
        elif o.Name.endswith('_CP2') and mounts.getObject(o.Name) is None and not o.Name.startswith(('W0', 'F_PI_', 'F_AUX_', 'F_HP_', 'F_HY_', 'F_TY_')):
            # These are budget envelopes, not the populated commercial material.
            reservations['context/'+o.Name] = o.Shape
    for o in mounts.Objects:
        if 'Shape' not in o.PropertiesList or o.Shape.isNull():
            continue
        if o.TypeId in ('PartDesign::Body', 'App::Link') or o.Name.startswith('BUSsupplier') or o.Name.endswith('NominalPCB'):
            material['mount/'+o.Name] = o.Shape
        elif o.Name.endswith('_CP2'):
            reservations['mount/'+o.Name] = o.Shape
    for group in (mounts.NominalMountHardware, mounts.SideMountHardware):
        for o in group.Group:
            material['hardware/'+o.Name] = o.Shape
    contacts, allowance_hits, errors, self_contacts = [], [], [], []
    tested = 0
    for name, candidate in targets.items():
        for other, shape in targets.items():
            if other <= name or not candidate.BoundBox.intersect(shape.BoundBox):
                continue
            hit = candidate.common(shape)
            assert hit.isValid()
            if hit.Volume > 1e-5:
                self_contacts.append(dict(a=name,b=other,volume_mm3=hit.Volume))
    for name, candidate in targets.items():
        for kind, collection, dest in [('material', material, contacts), ('reservation', reservations, allowance_hits)]:
            for other, shape in collection.items():
                if not candidate.BoundBox.intersect(shape.BoundBox):
                    continue
                tested += 1
                try:
                    if not shape.isValid():
                        raise ValueError('Invalid source shape: not usable as contact evidence')
                    hit = candidate.common(shape)
                    if not hit.isValid():
                        raise ValueError('Invalid intersection')
                    if hit.Volume > 1e-5:
                        dest.append(dict(holder=name, target=other, volume_mm3=hit.Volume,
                            witness_bounds_mm=bounds(hit), category=kind))
                except Exception as exc:
                    errors.append(dict(holder=name, target=other, error=str(exc)))
    pcb = mounts.getObject('PWM9685NominalPCB')
    result = dict(status='SHARED_SOURCE_ALLOCATION_CHECK_ONLY', selected=False, physical_pass=False,
        source_sha256=pins, tested_candidate_pairs=tested, material_intersections=contacts,
        reservation_intersections=allowance_hits, errors=errors, self_intersections=self_contacts,
        five_current_input_routes=input_rows,
        PWM9685_nominal_PCB_bounds_mm=bounds(pcb.Shape),
        candidate_holder_geometry='Nominal bought-body budget box, NOT measured manufacturer BRep',
        outputs_mounts_wire_load_paths_and_populated_PWM9685_not_qualified=True,
        started_utc=datetime.now(timezone.utc).isoformat(), wall_seconds=time.monotonic()-tick)
    dest = BASE / 'wiring-checkpoint/source-layout-fit.json'
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False), flush=True)
    A.closeDocument(mounts.Name)
    A.closeDocument(context.Name)


if __name__ == '__main__':
    main()
