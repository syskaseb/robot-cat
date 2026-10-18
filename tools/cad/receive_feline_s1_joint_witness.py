"""Receive only the named four-S1 dead end; do not rescan fixed worlds."""
import json
import time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
import FreeCAD as A
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_flat_s1_templates import candidates
from feline_current_candidate_scene import current
from plan_feline_fore_service_macro import rigid_tf
from feline_solid_distance import distance


def key(m):
    return m['clock_target_degrees'], m['first_mm'], m['bend_degrees']


def main():
    tick = time.monotonic()
    source = OUT / 'n01-whole51-joint-proposal.json'
    received = json.loads(source.read_text())
    allrows, pins = candidates()
    domains = {}
    for name, rows in allrows.items():
        bykey = {key(m): m for m in rows}
        domains[name] = [bykey[key(m)] for m in received['domains'][name]]
    result = dict(selected=False, N01_complete=False, physical_pass=False,
                  source_sha256={**pins, source.relative_to(ROOT).as_posix(): sha(source),
                                 Path(__file__).relative_to(ROOT).as_posix(): sha(Path(__file__))},
                  unchanged_world_domains_not_requeried=True, pairs=[])
    for a, rows in domains.items():
        for b, others in domains.items():
            if a >= b:
                continue
            witnesses = []
            for i, aa in enumerate(rows):
                for j, bb in enumerate(others):
                    g, ix = cKDTree(bb['points']).query(aa['points'], workers=1)
                    req = np.where((aa['types'] == 1) & (bb['types'][ix] == 1), .2, 1.25)
                    values = g - aa['radii'] - bb['radii'][ix] - req
                    k = int(np.argmin(values))
                    witnesses.append(dict(a_index=i, b_index=j, a_key=key(aa), b_key=key(bb),
                                          margin_mm=float(values[k]),
                                          a_type=int(aa['types'][k]), b_type=int(bb['types'][ix[k]]),
                                          a_point=aa['points'][k].tolist(), b_point=bb['points'][ix[k]].tolist()))
            witnesses.sort(key=lambda w: -w['margin_mm'])
            result['pairs'].append(dict(a=a, b=b, compatible_count=sum(w['margin_mm'] >= -1e-5 for w in witnesses),
                                        total=len(witnesses), best=witnesses[:3]))
    # Exact rings for one best W067 pair per neighbour distinguish ring geometry
    # from provisional clamp/head/wire cloud rejections. No global acceptance.
    scene, *_ = current()
    tf = rigid_tf(scene['Ref_Material_current_S1_body_CP2_0_0'].BoundBox.Center, [15, 0, 0], 180)
    for p in result['pairs']:
        if 'W067/single/end' not in (p['a'], p['b']):
            continue
        w = p['best'][0]
        shapes = []
        for name, idx in ((p['a'], w['a_index']), (p['b'], w['b_index'])):
            m = domains[name][idx]
            clock = A.Placement(A.Vector(*m['clock_tf_translation_mm']), A.Rotation(*m['clock_tf_rotation_quaternion']))
            shape = scene[m['ring_name']].copy()
            shape.Placement = tf * clock * shape.Placement
            assert shape.isValid() and len(shape.Solids) == 1
            shapes.append(shape)
        p['best_exact_ring_gap_mm'] = distance(*shapes)
        common = shapes[0].common(shapes[1])
        p['best_exact_ring_common_mm3'] = common.Volume
        p['exact_common_valid'] = common.isValid()
    result['worker_seconds'] = round(time.monotonic() - tick, 3)
    dest = OUT / 'n01-s1-joint-witness.json'
    dest.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(worker_seconds=result['worker_seconds'], pairs=result['pairs'])), flush=True)


if __name__ == '__main__':
    main()
