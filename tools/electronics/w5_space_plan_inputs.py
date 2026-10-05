"""Receive one current space inventory BEFORE designing another harness.

Read cached BReps only, never rebuild E6. Bounds are planning reservations,
not exact collision evidence. Keep unselected D/V candidates distinct from
fixed selected conductors. No new route, print selection or physical PASS.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import re
from servo_fuse_inputs_r1 import save, sha

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/electronics/full-cat/w5-space-plan-inputs-r1'


def family(owner):
    if owner.startswith(('ReceivedD/', 'ReceivedV/')):
        return 'unselected_leg_route_coupled_scope'
    if owner.endswith('_NEW_BODY'):
        return 'ground_block_placement_may_change'
    if owner in ('SourceDeck', 'SourcePlatform', 'SourceCarrier', 'SourceCover',
                 'SourceBankLeft', 'BankRight', 'SourceWestHood', 'SourceEastHood'):
        return 'printed_owner_change_allowed_not_automatically_free_space'
    if any(x in owner.lower() for x in ('_tie', 'tiehead', 'tieband', '_band', '_seat', 'shared/')):
        return 'mount_requires_compatible_replacement_if_its_wire_changes'
    if re.search(r'(?<!\w)(W\d+|XA\d+|XL\d+)', owner):
        return 'received_conductor_fixed_unless_whole_interface_is_replanned'
    return 'received_bought_or_structural_reservation'


def main():
    import FreeCAD as A, Part
    from w5_ground_entries_r1 import owners, RECEIVED
    from w5_ground_network_plan import profile
    begin = datetime.now(timezone.utc)
    assert not (OUT / 'space.json').exists(), 'Preserve received planning inputs'
    OUT.mkdir(parents=True, exist_ok=True)
    proof_path = ROOT / 'hardware/electronics/full-cat/w5-ground-network-r1/checks.json'
    proof = json.loads(proof_path.read_text(encoding='utf-8'))
    assert proof['route_count'] == 21 and not proof['errors']
    # The failed complete network is an input, NEVER selected space.
    old = json.loads(RECEIVED.read_text(encoding='utf-8'))
    installed, pins = owners(A, Part, old)
    rows = []
    for owner, shape in installed.items():
        bb = shape.BoundBox
        # Per-solid reservations avoid treating a hollow printed body as
        # a completely occupied bounding box. Cavities STILL require proof.
        solids = []
        for s in shape.Solids:
            b = s.BoundBox
            solids.append([getattr(b,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')])
        rows.append(dict(owner=owner, family=family(owner),
            bounds_mm=[getattr(bb,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')],
            per_solid_reservations_mm=solids, bound_is_material_occupancy=False))
    finish = datetime.now(timezone.utc)
    pins += [Path(__file__), RECEIVED, proof_path,
        ROOT / 'tools/electronics/w5_ground_entries_r1.py',
        ROOT / 'tools/electronics/w5_source_grips_native_r1.py',
        ROOT / 'tools/electronics/w5_r53_owners.py',
        ROOT / 'hardware/manufacturing/one-batch-prototype-r53/selection.json']
    save(OUT / 'space.json', dict(status='PLANNING_INPUTS_ONLY_NO_ROUTE_SELECTED',
        base_selection='R53', base_completed_count=14, phase1_total=20,
        frame='received WORLD millimetres; not ROS primitive geometry', rows=rows,
        owner_scope='R53 cache with explicitly unselected source-family and ground-R4 replacements',
        source_family_selected=False, ground_R4_selected=False,
        preserved_bank='R47', rejected_network='w5-ground-network-r1',
        rejected_contact_count=len(proof['hits']),
        constraints=dict(battery_negative_nominal_max_mm=150, BUS_factory_nominal_mm=300,
            one_continuous_3_conductor_cable_per_leg_servo=12,
            nominal_leg_cable_mm=900, all_36_leg_conductors_must_close_together=True,
            individual_G_fits_do_not_qualify_whole_cable=True,
            radii_mm={w:profile(w)['radius_mm'] for w in ('W001','W003','W060','W025','XA05')},
            W060_retained_tail_unqualified_radius_bound_mm=6,
            ground_cage_datums_provisional=True),
        next_design_order=[
            'Freeze selected bought parts, bank and required moving/service reservations.',
            'Allocate complete12 D/V/G looms and central positive/ground/logic paths together.',
            'Choose block orientations plus straight insulated grip lengths BEFORE bends.',
            'Reject insufficient length or bend room analytically before building CAD.',
            'Make one coherent native mount/cover change after route space is agreed.',
            'Check only changed interfaces, assembly, quantities and current-source hashes.'],
        no_route_cad_until_space_allocation=True,
        selected=False, W5_complete=False, physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        started_utc=begin.isoformat(), finished_utc=finish.isoformat(),
        worker_wall_seconds=(finish-begin).total_seconds()))
    print('SPACE_PLAN_INPUTS_RECEIVED', len(rows), (finish-begin).total_seconds(), flush=True)


if __name__ == '__main__': main()
