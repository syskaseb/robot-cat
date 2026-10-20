"""Single working boundary input after receiving the existing cuff outlets.

The selected native and historical registers remain unchanged. This updates
only nine routing exits, never the fixed/moving electrical seam or wire OD.
"""
import json
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from compose_feline_output_boundaries import current as parent
from compose_feline_integrated_boundaries import apply_updates


def current():
    base, rows, files = parent()
    f = OUT/'n01-current-prefix-atlas.json'; atlas = json.loads(f.read_text())
    for p,h in atlas['source_sha256'].items(): assert sha(ROOT/p) == h,p
    result = apply_updates(rows, atlas['updates'])
    for old,new in zip(rows,result):
        for k in ('id','wire','portion_id','endpoint','group','point_mm','departure_axis'):
            assert old.get(k) == new.get(k), (old['id'], k)
    return base, result, (*files, f)
