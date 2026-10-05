"""One joint space allocation, BEFORE any new route CAD is constructed.

Conservative bounds can identify a reservation to inspect, not prove an
intersection. This contract cannot select parts or close a milestone.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import re
from servo_fuse_inputs_r1 import save, sha
from w5_ground_joint_layout_r1 import BLOCKS as RECEIVED
from w5_ground_joint_layout_r2 import rotate_xy

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/electronics/full-cat/w5-space-plan-inputs-r1'
SHARED = {'W001','W003','W060','W061','XA05','W025','W036','W062','W063',
          'W064','W065','W066','W067','W068','W043','XA01',
          'W004','W005','W006','W008','W009','W010','W013','W014','W015','W016','W017','W018',
          'W019','W020','W021','W022','W023','W024','W030','W031','W032','W033','W034','W035',
          'W047','W049','W051','W055','W057','W059','W069','W070','W071','W072','W073','W074'}


def planned_ports():
    result = {}
    for name, row in RECEIVED.items():
        cx, cy = ([84, 0] if name == 'G1' else [124, 0] if name == 'G2' else row['centre'])
        floor = 132 if name == 'G2' else 124
        angle = 0 if name in ('G1','G2') else 180
        side = 1 if row['mouth_y'] > row['centre'][1] else -1
        for i, label in enumerate(row['labels']):
            dx, dy = rotate_xy((i-2)*row['pitch'],row['mouth_y']-row['centre'][1],angle)
            u,v = rotate_xy(0,side,angle)
            result[f'{name}.{label}'] = dict(point_mm=[cx+dx,cy+dy,floor+4.5],
                outward_axis=[u,v,0], provisional_cage_registration=True)
    return result


def overlaps(a,b):
    return all(a[i] < b[i+3] and b[i] < a[i+3] for i in range(3))


def main():
    begin = datetime.now(timezone.utc)
    target = OUT / 'allocation.json'
    assert not target.exists(), 'Preserve planning contract'
    space_path = OUT / 'space.json'; space = json.loads(space_path.read_text(encoding='utf-8'))
    p = planned_ports()
    bodies = {
        'G1':[65.5,-11,124,102.5,11,135], 'G2':[109,-9.5,132,139,9.5,141],
        **{n:[r['centre'][0]-15,r['centre'][1]-9.5,124,
              r['centre'][0]+15,r['centre'][1]+9.5,133]
           for n,r in RECEIVED.items() if n not in ('G1','G2')}}
    reservations = []
    deferred = []
    for name,bounds in bodies.items():
        for row in space['rows']:
            family = row['family']; key = row['owner']
            if not overlaps(bounds,row['bounds_mm']): continue
            net = re.search(r'(?<![A-Za-z0-9])(W\d+|XA\d+|XL\d+)',key)
            if family in ('ground_block_placement_may_change','unselected_leg_route_coupled_scope',
                'printed_owner_change_allowed_not_automatically_free_space',
                'mount_requires_compatible_replacement_if_its_wire_changes') or (net and net[1] in SHARED):
                deferred.append(dict(block=name,owner=key,reason='joint change; must replace or prove compatible'))
            else:
                reservations.append(dict(block=name,owner=key,bounds_mm=row['bounds_mm'],
                    bound_overlap_is_NOT_exact_contact=True))
    finish = datetime.now(timezone.utc)
    save(target, dict(status='JOINT_SPACE_ALLOCATION_REQUIRES_RESERVATION_REVIEW',
        planned_cages=p, planned_bodies_mm=bodies,
        preserve_bank_R47=True, preserve_electrical_P0_nets=True,
        coupled_conductors=sorted(SHARED),
        primary_changes=['Keep all six ground blocks below Carrier, above DATA.',
            'G1 original orientation, centre84/0 and underside124; G2 centre124/0, underside132.',
            'Four leg ground blocks original outward exits, underside124.',
            'Ground branches leave ABOVE existing factory feeds; thick returns fan sideways BEFORE rising.',
            'Reserve four return lanes with separation and a separate W061 bridge, not crossing polylines.',
            'D/V/G trunks planned as12 complete looms, not36 unrelated cables.',
            'W003 short diagonal approach above Pi cooling reservation, no Y65 detour.',
            'Retain BAT.minus, MAIN and BUS plug; adapt native Deck/Carrier/Cover only after paths fit.'],
        why_not_previous_R1=['Old G1 thick departures crossed DATA and Pi leads.',
            'Old RL return rose through purchased F_RL3.',
            'Old whole ground family crossed itself13times and fixed routes73times.',
            'Old W003332.387+30mm exceeded300mm.'],
        bounds_reservations_to_review=reservations, compatible_replacements_pending=deferred,
        limits=dict(BAT_minus_nominal_max_mm=150, BUS_factory_nominal_mm=300,
            leg_cable_nominal_mm=900, cable_stock_requires_max_D_V_G_length=True,
            fixed_TKD_radius_mm=21, fixed_LAPP_radius_mm=12.4, fixed_HELU_XA05_radius_mm=15),
        analytical_checks_pending=['Six bodies against fixed bought/structural reservations.',
            'All26 ground cage approaches have straight insulated grips before bends.',
            'Every full route fits the chosen radius without overlapping corner offsets.',
            'W001 and W003 satisfy their length limits including terminations.',
            '12 shared cable breakouts and full moving/service reservations are maintained.'],
        route_CAD_started=False, selected=False, W5_complete=False, physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in (space_path,Path(__file__),
            ROOT/'tools/electronics/w5_ground_joint_layout_r1.py',ROOT/'tools/electronics/w5_ground_joint_layout_r2.py')},
        started_utc=begin.isoformat(), finished_utc=finish.isoformat(),
        worker_wall_seconds=(finish-begin).total_seconds()))
    print('ALLOCATION',len(bodies),'bodies',len(reservations),'fixed reservations',len(deferred),'deferred',flush=True)
    for row in reservations: print(row['block'],row['owner'],flush=True)


if __name__ == '__main__': main()
