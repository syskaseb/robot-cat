"""Intrinsic four purchased-ring fit before any more complete fan allocation.

Clock choices are independent of whole-source rigid pose. Cloud proposals
receive exact whole-ring distance before acceptance of this limited fit.
"""
import itertools
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


def main():
    tick = time.monotonic()
    rows, pins = candidates()
    choices = {}
    for ref, candidates_ in rows.items():
        choices[ref] = list({m['clock_target_degrees']: m for m in reversed(candidates_)}.values())
    memo = {}
    def pair(a, i, b, j):
        k = (a, i, b, j) if a < b else (b, j, a, i)
        if k not in memo:
            aa, bb = choices[a][i], choices[b][j]
            p, q = aa['points'][aa['types'] == 9], bb['points'][bb['types'] == 9]
            memo[k] = float(cKDTree(q).query(p, workers=1)[0].min())
        return memo[k]
    names = list(choices)
    proposals = []
    for ids in itertools.product(range(12), repeat=4):
        score = min(pair(a, ids[i], b, ids[j]) for i,a in enumerate(names) for j,b in enumerate(names) if i < j)
        if score >= 1.25:
            proposals.append((score, ids))
    proposals.sort(reverse=True)
    result = dict(selected=False, N01_complete=False, physical_pass=False,
                  rigid_whole_source_pose_invariant=True, required_project_gap_mm=1.25,
                  clock_options_each=12, cloud_pair_cache_count=len(memo),
                  cloud_proposals=len(proposals), exact_receipts=[], chosen=None,
                  no_changed_world_or_wire_checks=True, source_sha256=pins)
    scene, *_ = current()
    tf = rigid_tf(scene['Ref_Material_current_S1_body_CP2_0_0'].BoundBox.Center,[15,0,0],180)
    for score, ids in proposals[:12]:
        shapes = {}
        for i, name in enumerate(names):
            m = choices[name][ids[i]]
            clock = A.Placement(A.Vector(*m['clock_tf_translation_mm']), A.Rotation(*m['clock_tf_rotation_quaternion']))
            s = scene[m['ring_name']].copy()
            s.Placement = tf * clock * s.Placement
            shapes[name] = s
        pairs = [dict(a=a,b=b,exact_gap_mm=distance(shapes[a],shapes[b])) for a,b in itertools.combinations(names,2)]
        receipt = dict(clocks={name:choices[name][ids[i]]['clock_target_degrees'] for i,name in enumerate(names)},
                       cloud_min_gap_mm=score,pairs=pairs)
        result['exact_receipts'].append(receipt)
        if min(r['exact_gap_mm'] for r in pairs) >= 1.25-1e-6:
            result['chosen'] = receipt
            break
    result.update(worker_seconds=round(time.monotonic()-tick,3),
                  status='INTRINSIC_RING_FIT_RECEIVED_NOT_WHOLE_SOURCE_APPROVAL' if result['chosen'] else 'NO_RECEIVED_INTRINSIC_RING_FIT_IN_BOUNDED_CLOCK_FAMILY')
    result['source_sha256'][Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    dest = OUT/'n01-s1-intrinsic-ring-joint.json'
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(seconds=result['worker_seconds'],cloud_proposals=len(proposals),chosen=result['chosen'],status=result['status'])),flush=True)


if __name__ == '__main__':
    main()
