"""Receive whole outward four-corner fan against existing field, without waivers."""
import json
import time
from pathlib import Path
import numpy as np
from scipy.interpolate import RegularGridInterpolator
from scipy.spatial import cKDTree
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_flat_s1_templates import candidates
from feline_flat_station_templates import compact, shared_rail_bounds, to_box


def main():
    tick = time.monotonic()
    source = OUT / 'n01-flat20-field-modulejoint.json'
    proof = json.loads(source.read_text())
    assert proof['stage'] == 'complete' and not proof['errors']
    fieldpath = ROOT / proof['field']
    assert sha(fieldpath) == proof['field_sha256']
    field = np.load(fieldpath, allow_pickle=False)
    axes = [field[k] for k in ('x', 'y', 'z')]
    grid = np.stack(np.meshgrid(*axes, indexing='ij'), axis=-1)
    fields = {k: RegularGridInterpolator(axes, field[k + '_distance'], bounds_error=False, fill_value=0)
              for k in ('material', 'reservation', 'curve_hold', 'motion36', 'outer')}
    for k in ('P_SYS', 'W043', 'S1', 'BankTerm', 'P0Rail'):
        dd = cKDTree(field[k + '_context']).query(grid.reshape(-1, 3), workers=1)[0].reshape(grid.shape[:3])
        fields[k] = RegularGridInterpolator(axes, dd, bounds_error=False, fill_value=0)
    inside = RegularGridInterpolator(axes, field['inside'].astype(float), bounds_error=False, fill_value=0)
    service = RegularGridInterpolator(axes, field['service'].astype(float), method='nearest', bounds_error=False, fill_value=1)
    allrows, pins = candidates()
    angles = {'W064/single/end': (0, 30), 'W065/single/end': (150, 180),
              'W067/single/end': (0, 330), 'W068/single/end': (180, 210)}
    result = dict(selected=False, N01_complete=False, physical_pass=False, domains={},
                  design='All four tails outward from actual stud square; selected rings unchanged',
                  source_sha256={**pins, source.relative_to(ROOT).as_posix(): sha(source),
                                 fieldpath.relative_to(ROOT).as_posix(): sha(fieldpath),
                                 Path(__file__).relative_to(ROOT).as_posix(): sha(Path(__file__))},
                  exact_material_or_native_approval=False, unchanged51_world_domains_not_requeried=True)
    for name, rows in allrows.items():
        received = []
        for m in rows:
            if m['clock_target_degrees'] not in angles[name]:
                continue
            p, rr, tt = m['points'], m['radii'], m['types']
            holds = []
            if inside(p).min() < .999:
                k = int(np.argmin(inside(p)))
                holds.append(dict(label='outside', margin=-1e6, point=p[k].tolist(), type=int(tt[k])))
            for label, interp in fields.items():
                mask = tt != 9 if label == 'S1' else np.ones(len(p), bool)
                req = 1 if label == 'outer' else 3.35 if label == 'curve_hold' else .2
                values = interp(p[mask]) - rr[mask] - req
                k = int(np.argmin(values))
                if values[k] < 0:
                    holds.append(dict(label=label, margin=float(values[k]), point=p[mask][k].tolist(), type=int(tt[mask][k])))
            if service(p).max() > .5:
                holds.append(dict(label='ATO_access', margin=-.01))
            for rail in shared_rail_bounds():
                values = to_box(p, rail) - rr - .2
                if values.min() < 0:
                    holds.append(dict(label='common_low_rail', margin=float(values.min())))
            received.append(dict(template=compact(m), holds=holds, numeric_only_possible=not holds))
        result['domains'][name] = received
        print(name, 'corner family', len(received), 'numeric possible', sum(not r['holds'] for r in received), flush=True)
    result['worker_seconds'] = round(time.monotonic() - tick, 3)
    dest = OUT / 'n01-s1-corner-allocation.json'
    dest.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print('received', result['worker_seconds'], flush=True)


if __name__ == '__main__':
    main()
