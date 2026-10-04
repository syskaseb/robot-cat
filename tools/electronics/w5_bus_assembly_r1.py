"""Receive the completed BUS pilot; qualify changed bank-service interfaces.

No inherited full-body audit. The selected three-body removal sequence is
retained, with seven poses tested only against the added fixed BUS geometry.
This receipt is a candidate until one explicit print-set selection adopts it.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/electronics'))
from servo_fuse_inputs_r1 import save, sha
import w5_bus_restraints_r3 as layout
OUT = ROOT / 'hardware/electronics/full-cat/w5-bus-assembly-r1'
NATIVE = ROOT / 'hardware/electronics/full-cat/w5-bus-native-grips-r3/checks.json'
CAD = ROOT / 'hardware/cad/studies/w5-bus-native-grips-r3/BusSharedGrips.FCStd'
ROUTES = ROOT / 'hardware/electronics/full-cat/w5-bus-pair-r52-r4'


def main():
    import FreeCAD as A
    import Part
    from w5_selected_owners_r52 import cached
    begin = datetime.now(timezone.utc)
    proof = json.loads(NATIVE.read_text(encoding='utf-8'))
    assert proof['status'] == 'SHARED_BUS_NATIVE_STATIC_COMPLETE_UNSELECTED'
    assert not proof['hits'] and not proof['errors']
    assert proof['closed_STL'] and proof['relocated_reopen']
    assert all(sha(ROOT / rel) == value for rel, value in proof['files'].items())
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT / 'assembly.json').exists(), 'Preserve completed receipt'
    owners, cache = cached()
    service_path = ROOT / 'hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r22/checks.json'
    service = json.loads(service_path.read_text(encoding='utf-8'))
    assert not service['hits'] and not service['errors']
    assert service['module'] == ['BankRight', 'BankLeft', 'Cover']
    intent = json.loads((ROUTES / 'intent.json').read_text(encoding='utf-8'))
    sx = intent['source_lead_datums']['W003'][0]
    # Open saved cached native geometry without forcing inherited recompute.
    doc = A.openDocument(str(CAD))
    fixed = {name: Part.makeBox(b[3]-b[0], b[4]-b[1], b[5]-b[2], A.Vector(*b[:3])).cut(doc.BusClearanceTools.Shape)
             for name, b in layout.supports(sx)}
    fixed.update(layout.restraints(A, Part, sx))
    fixed.update({wire: Part.read(str(ROUTES / (wire + '_DESIGN.brep'))) for wire in ('W002', 'W003')})
    assert all(s.isValid() for s in fixed.values())
    hits, errors, pairs = [], [], 0
    lifts = [0, 2, 5, 10, 30, 60, 100]
    for lift in lifts:
        for name in service['module']:
            moving = owners[name].copy()
            moving.translate(A.Vector(0, 0, lift))
            for key, shape in fixed.items():
                if not moving.BoundBox.intersect(shape.BoundBox):
                    continue
                pairs += 1
                try:
                    v = moving.common(shape).Volume
                    if v > 1e-5:
                        hits.append(dict(lift_mm=lift, moving=name, fixed=key, mm3=v))
                except Exception as exc:
                    errors.append(dict(lift_mm=lift, moving=name, fixed=key, error=str(exc)))
        print('BUS_SERVICE_POSE', lift, 'hits', len(hits), flush=True)
    lengths = json.loads((ROUTES / 'checks.json').read_text(encoding='utf-8'))['lengths']
    assert {r['wire']: r['nominal_trim_bound_mm'] for r in lengths} == {'W002': 170, 'W003': 300}
    paths = [Path(__file__), Path(layout.__file__), NATIVE, CAD, service_path,
             ROUTES / 'checks.json', ROUTES / 'intent.json',
             ROOT / 'hardware/electronics/power-platform/ADAPTER-PIGTAIL-P0.md',
             ROOT / 'hardware/electronics/full-cat/w5-installed-r52/owners.json',
             ROOT / 'hardware/electronics/full-cat/w5-installed-r52/installed.brep']
    end = datetime.now(timezone.utc)
    result = dict(status='BUS_LOCAL_READY_FOR_SELECTION' if not hits and not errors else 'BUS_SERVICE_REJECTED',
        selected=False, W5_complete=False, physical_pass=False,
        sampled_service_lifts_mm=lifts, continuous_service_verified=False,
        hits=hits, errors=errors, changed_pairs=pairs,
        retained_bank_sequence=service['sequence'],
        changed_fixed_geometry='Four native seats, three new straps, one reused shared W061 strap, complete D/G paths',
        wiring=[dict(wire='W002', source='H3.1 D schematic role', end='D_FL.1', nominal_trim_mm=170),
                dict(wire='W003', source='H3.3 G schematic role', end='G2.4', nominal_trim_mm=300)],
        no_physical_cavity_order_inferred=True, V_contact_removed=True,
        stock=dict(factory34171=dict(pack_count=1, factory_cables_installed=1, pack_spares=5,
                    replaces_existing_BUS_cable_role=True, extra_packs=0),
                   tie11102370=dict(new_installed=3, new_service_replacements=3,
                    reused_W061_installed=1, W061_replacement_already_existing_role=True,
                    whole_robot_census_pending=True), new_screws=0, new_separate_prints=0),
        deck_replacement=dict(identity='electronics:DeckP10-cover-mount', quantity=1,
            native=CAD.relative_to(ROOT).as_posix(), final_object='BusDeckFinished',
            stl='hardware/cad/studies/w5-bus-native-grips-r3/BusSharedGrips_UNSELECTED_x1.stl'),
        assembly=[
            'With battery/USB/all sources absent, prepare Deck before mounting purchased blocks. Retain bank mounts, the G1 passage and all unchanged parts.',
            'Identify factory cable D/V/G by schematic and unpowered continuity. Retain one factory plug, remove V contact/lead without damaging D/G. Never use colours as pin identification.',
            'With W061 free at G2, thread its reused strap through retained left105.5/11 and new right120.2/11 slot. Retain its head and unused old right slot; do not add a second overlapping strap.',
            'Lay complete D and G routes in open channels; source seat supports the insulation above H3. Fit three new straps: source, D with west-facing head, G middle atX98.',
            'Fit one BUS plug without force. Dry-fit entire cable before any cut: nominal D170/G300 are independent core trim bounds, NOT two cables and NOT usable-length measurements.',
            'Remove far plug only after confirming adequate delivered G length. Mark D/G, strip11mm or delivered221-415 marking, one untinned Cu strand per port; verify actual copper .14..4mm2. If not compatible do not insert.',
            'Connect D_FL.1 and G2.4, then tension open-seat straps gently against insulation, with slack at plug and bare ends. The shared G2 strap supports W061 and BUS G without pulling either clamp.',
            'Retain R52 bank assembly/removal order. For BUS removal disconnect D/G and H3 with power absent, support cable, cut three BUS straps and shared W061 strap before lifting its bracket; renew only affected roles.',
        ],
        phase2_conditions=['Delivered factory copper area, connector revision, usable G length and lead exit remain unmeasured. If G is shorter than needed revise route/material before assembly, never stretch it.',
            'OD2mm/R10/plugprojection8mm are replaceable prototype assumptions. Confirm grip fit, actual bend limits, pull relief and insulation damage.',
            'Local nominal channel skin .8mm requires PETG/profile/strength review in phase2; no physical or full-final strictBOP PASS.',
            'Verify D continuity, G continuity, absence of V and D/G short with devices unplugged before hardware power.'],
        source_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in paths},
        started_utc=begin.isoformat(), finished_utc=end.isoformat(), worker_wall_seconds=(end-begin).total_seconds())
    save(OUT / 'assembly.json', result)
    print('BUS_ASSEMBLY', result['status'], pairs, len(hits), flush=True)


if __name__ == '__main__':
    main()
