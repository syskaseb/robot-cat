"""Correct AUX footprint and register MAIN pads in the shared candidate.

Reservation correction, not a PCB mount or full harness qualification. MAIN
pads are inherited prototype datums aligned by the documented family footprint,
not by a box centre. Only the changed AUX envelope gets a new contact gate.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import math
import time
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2'
SOURCE = BASE / 'BranchSourceCandidate.FCStd'
NATIVE = BASE / 'BoardDatumCandidate.FCStd'
OUT = BASE / 'board-datums-checks.json'
GRAPH = BASE / 'whole-harness-board-plan.json'
MAIN = ROOT / 'hardware/cad/studies/main-p0-mount/r5/MainP0Mount.FCStd'
OLD_ORIGIN = [105.82, 8.16, 52]
OLD_PADS = {'MAIN.VIN': [114.869, 4.91, 62.5748],
            'MAIN.GND': [114.869, 8.41, 62.5748],
            'MAIN.VOUT': [114.869, 15.41, 62.5748],
            'MAIN.GND_OUT': [114.869, 11.91, 62.5748]}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def footprint_coordinates(old_world, family_min):
    return [v - origin - low for v, origin, low in zip(old_world, OLD_ORIGIN, family_min)]


def main():
    import FreeCAD as A
    started = datetime.now(timezone.utc)
    tick = time.monotonic()
    deadline = datetime.fromisoformat('2026-10-06T07:00:00+00:00')
    resume = '--resume-saved' in sys.argv
    assert started < deadline and not OUT.exists()
    assert NATIVE.exists() == resume, 'Preserve existing native; use explicit failed-receipt recovery'
    paths = [SOURCE, MAIN, BASE/'whole-harness-current-plan.json', Path(__file__),
             ROOT/'tools/electronics/main_input_return_r1.py',
             ROOT/'tools/electronics/main_positive_input_route_common_r2.py',
             ROOT/'tools/electronics/pi_power_usb_r1.py',
             ROOT/'hardware/electronics/full-cat/board-interfaces-r1/interfaces.json',
             ROOT/'hardware/reference/aux4092-2026-09-26/reg24d-drill.dxf']
    pins = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    original = json.loads(paths[2].read_text(encoding='utf-8'))
    assert sha(SOURCE) == original['branch_source_static_proof']['candidate_native_sha256']
    interface = json.loads(paths[-2].read_text(encoding='utf-8'))['pololu4092']
    assert interface['dimensions_mm'] == [25.4, 25.4]
    d = A.openDocument(str(NATIVE if resume else SOURCE))
    source_doc = None
    try:
        aux = d.getObject('AUX4092_CP2')
        assert abs(aux.Length.Value-(25.4 if resume else 18.8)) < 1e-7 and abs(aux.Width.Value-25.4) < 1e-7
        old_aux = dict(length_mm=18.8, volume_mm3=18.8*25.4*30,
                       placement=str(aux.Placement))
        if not resume:
            aux.Length = 25.4
            d.recompute()
        assert aux.Shape.isValid() and len(aux.Shape.Solids) == 1
        corrected_volume = aux.Shape.Volume
        # Useful native reservation parameter perturbation/restoration; no mount.
        if not resume:
            aux.Length = 24.4
            d.recompute()
            assert abs(aux.Shape.Volume-24.4*25.4*30) < 1e-5
            aux.Length = 25.4
            d.recompute()
            assert abs(aux.Shape.Volume-corrected_volume) < 1e-5
        contacts, errors, tested = [], [], 0
        shape = aux.Shape
        for ob in d.Objects:
            if ob == aux or 'Shape' not in ob.PropertiesList or ob.Shape.isNull():
                continue
            if ob.Name in ['TorsoEnvelope', 'BatteryNominal']:
                continue
            relevant = any(p.Name in ['InteriorReservations', 'HarnessCandidate',
                'S0TerminalCandidates', 'S1TerminalCandidates', 'ServiceReservations',
                'ATOStackCandidates'] for p in ob.InList) or (
                'Category' in ob.PropertiesList and ob.Category != 'electronics')
            if not relevant or not shape.BoundBox.intersect(ob.Shape.BoundBox):
                continue
            tested += 1
            try:
                assert ob.Shape.isValid(), 'Invalid input BRep'
                common = shape.common(ob.Shape)
                assert common.isValid(), 'Invalid common BRep'
                if common.Volume > 1e-5:
                    contacts.append(dict(pair=[aux.Name, ob.Name], volume_mm3=common.Volume,
                        basis='Changed supplier footprint reservation vs named current geometry; not material fit'))
            except Exception as error:
                errors.append(dict(pair=[aux.Name, ob.Name], error=str(error)))
            assert datetime.now(timezone.utc) < deadline
        remaining = shape.cut(d.getObject('TorsoEnvelope').Shape)
        assert remaining.isValid()
        outside = remaining.Volume > 1e-5
        source_doc = A.openDocument(str(MAIN))
        family = source_doc.getObject('SupplierFamilyReference')
        assert family.Shape.isValid()
        bb = family.Shape.BoundBox
        low = [bb.XMin, bb.YMin, bb.ZMin]
        size = [bb.XLength, bb.YLength, bb.ZLength]
        assert math.dist(size, [30.48, 22.86, 7.6748]) < 1e-5
        target = d.getObject('MAIN4853_CP2')
        datums = {}
        for role, old_world in OLD_PADS.items():
            local = footprint_coordinates(old_world, low)
            assert all(-1e-7 <= x <= extent+1e-7 for x, extent in zip(local, size))
            point = target.Placement.multVec(A.Vector(*local))
            assert (target.Placement.inverse().multVec(point)-A.Vector(*local)).Length < 1e-7
            datums[role] = dict(native=target.Name, point_mm=list(point),
                departure=list(target.Placement.Rotation.multVec(A.Vector(0,0,1))),
                source_world_mm=old_world, local_family_footprint_mm=local,
                basis='Inherited R53 prototype pad, normalized mounted R5 family footprint then current CP2 placement; NOT exact delivered4853 pad',
                route_restraint_and_lever_qualified=False)
        datums['MAIN.GND_IN'] = dict(datums['MAIN.GND'])
        datums['MAIN.VIN_SW'] = dict(datums['MAIN.VIN'])
        source_holes = [[11.081, y+2, 9] for y in [-9.271, 9.271]]
        holes = [list(target.Placement.multVec(A.Vector(*[v-m for v,m in zip(h,low)]))) for h in source_holes]
        assert abs(math.dist(*holes)-18.542) < 1e-6
        if not resume: d.saveAs(str(NATIVE))
        A.closeDocument(d.Name)
        d = A.openDocument(str(NATIVE))
        reopened = d.getObject('AUX4092_CP2')
        assert reopened.Shape.isValid() and abs(reopened.Shape.Volume-corrected_volume) < 1e-5
        result = dict(status='AUX_FOOTPRINT_CORRECTED_MAIN_DATUMS_BOUND' if not(contacts or errors or outside) else 'CORRECTED_FOOTPRINT_REQUIRES_SHARED_CHANGE',
            selected=False, physical_pass=False, W1_complete=False, W5_complete=False,
            source_sha256=pins, candidate_native_sha256=sha(NATIVE),
            AUX=dict(old=old_aux, corrected_board_XY_mm=[25.4,25.4],
                retained_height_reserve_mm=30, source='https://www.pololu.com/product/4092',
                electrical_pad_orientation_OPEN=True, native_mount_OPEN=True),
            exact_changed_pairs_tested=tested, contacts=contacts, errors=errors, outside=outside,
            MAIN_frame=dict(source_native=str(MAIN.relative_to(ROOT)),
                mounted_family_bbox_min_mm=low, size_mm=size,
                transformation='old_world - old_mount_origin - mounted_family_min, then CP2 local placement',
                source_copper_pads_provisional=True, target_holes_mm=holes,
                supports_not_created=True), MAIN_datums=datums,
            saved_reopen=True, parameter_restored=True,
            receipt_recovery_from_saved_native=resume,
            recovery_reason='First run saved native after parameter restore, but dereferenced deleted aux object after close; changed AUX gate recovered, no native rewrite' if resume else None,
            retained_F_PI_service_conflict_NOT_waived=True,
            old_CP2_AUX18p8_envelope_evidence_invalid_for_AUX_neighbours=True,
            unchanged_pairs_not_rerun=True,
            started_utc=started.isoformat(), finished_utc=datetime.now(timezone.utc).isoformat(),
            worker_wall_seconds=round(time.monotonic()-tick,3))
        OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        # Rebind graph without repeating unchanged native inventory/contact gates.
        graph = original
        for row in graph['body_conductors']:
            row['ends'] = [dict(role=e['role'], **datums[e['role']]) if e['role'] in datums else e for e in row['ends']]
            row['bound_end_count'] = sum('point_mm' in e for e in row['ends'])
            if row['bound_end_count'] == 2:
                row['straight_distance_only_mm'] = math.dist(*[e['point_mm'] for e in row['ends']])
                row['distance_not_routed_length'] = True
        for row in graph['distribution_boundary']:
            row['resolved_datums'].update({role: datums[role] for role in row['ends'] if role in datums})
            row['ends_bound'] = len(row['resolved_datums'])
        graph['source_sha256'].update(pins)
        graph['source_sha256'][OUT.relative_to(ROOT).as_posix()] = sha(OUT)
        graph['current_candidate_native'] = NATIVE.relative_to(ROOT).as_posix()
        graph['current_candidate_native_sha256'] = sha(NATIVE)
        graph['board_datum_proof'] = result
        graph['scope']['bound_body_ends'] = sum(r['bound_end_count'] for r in graph['body_conductors'])
        graph['scope']['fully_bound_body_pairs'] = sum(r['bound_end_count']==2 for r in graph['body_conductors'])
        graph['missing_endpoint_roles'] = [e for e in graph['missing_endpoint_roles'] if e not in datums]
        graph['next_gate'] = 'Resolve F_PI service sequence and exact/provisional AUX/head/tail/leg/USB endpoints, then one complete wiring corridor plan. AUX footprint25.4 replaces18.8; old neighbour fit invalid. No more scalar offsets or blind route searches.'
        GRAPH.write_text(json.dumps(graph,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        assert all(sha(ROOT/p)==h for p,h in pins.items())
        print(result['status'], 'contacts', contacts, 'errors', errors, 'bodyends', graph['scope']['bound_body_ends'], flush=True)
    finally:
        A.closeDocument(d.Name)
        if source_doc: A.closeDocument(source_doc.Name)


if __name__ == '__main__':
    main()
