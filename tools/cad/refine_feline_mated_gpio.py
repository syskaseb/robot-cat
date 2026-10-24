"""Refine only unresolved necessary GPIO-prefix translation pairs; not full leads."""
import time
import json
from pathlib import Path
import FreeCAD as A
from check_feline_current_gpio_release import certify
from feline_fore_power_pair import pair_spacing
from feline_solid_distance import distance
from receive_feline_pi_split_service_space import independent
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT


def refine(probe, scene, metadata, movers):
    assert probe['delta_mm'] == [0, 0, 10]
    assert all(not s['errors'] for s in probe['samples'])
    tick = time.monotonic()
    keys = sorted({k for sample in probe['samples']
                   for k, row in sample['checks'].items() if not row['ok']})
    results = {}
    for key in keys:
        a, b = key.split('|')
        shapes = [movers[a], scene[b]]
        valid = all(s.isValid() and s.Solids and not s.check(True) for s in shapes)
        minimum = pair_spacing(a, metadata.get(a, {}), b, metadata.get(b, {}))
        if not valid:
            results[key] = dict(continuous_clear=False, strict_valid=False)
            continue
        known = {s['fraction'] * 10: s['checks'][key]['gap_mm']
                 for s in probe['samples'] if key in s['checks']}
        queries = 0
        def gap(z):
            nonlocal queries
            if z not in known:
                shape = independent(movers[a])
                shape.translate(A.Vector(0, 0, z))
                known[z] = distance(shape, scene[b])
                queries += 1
            return known[z]
        results[key] = certify(gap, stop=10, minimum=minimum)
        results[key].update(strict_valid=True, new_distance_queries=queries)
        print('MATED_REFINE', key, results[key]['continuous_clear'], flush=True)
    return dict(refined_pairs=results, necessary_prefix_clear=all(
        v['continuous_clear'] for v in results.values()),
        inherited_other_pairs='Original stricter1.25mm continuous bounds retained',
        full_five_leads_qualified=False, whole_service_qualified=False,
        N01_complete=False, worker_seconds=round(time.monotonic()-tick, 3))


def receive(probe, result, excluded):
    paths = [Path(__file__), ROOT/'tools/cad/feline_fore_power_pair.py',
             OUT/'W009-W069-harness-corridor/recovered-context.json']
    result.update(original_generic_probe=probe, excluded=sorted(excluded),
                  physical_pass=False, source_sha256={
                      p.relative_to(ROOT).as_posix(): sha(p) for p in paths},
                  open=['Five whole flexible leads and fixed remote ends',
                        'Whole moving Pi/carrier versus scene',
                        'USB/power/W009 parking and full assembly access',
                        'Missing276 scene actors'])
    dest = OUT/'n01-mated-GPIO-prefix-motion-20261024.json'
    # Compact nested checks: this is one receipt, not thousands of log lines.
    dest.write_text(json.dumps(result, separators=(',', ':'))+'\n',
                    encoding='utf-8', newline='\n')
    return dest
