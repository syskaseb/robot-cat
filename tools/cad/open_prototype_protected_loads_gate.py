"""Read-only positive material witnesses for the two newly planned feeds.

No tube acceptance is inferred from an empty point screen. Existing S1 and
tail receiving blockers stay open; native sources are never saved here.
"""
from pathlib import Path
import open_prototype_protected_loads as L
import open_prototype_rr_receiving_branch as R
import open_prototype_source_distance_gate as D

ROOT=L.ROOT;OUT=L.OUT;PLAN=L.PLAN
PROOF=OUT/'protected-loads-point-screen.json'
CAPACITY=OUT/'rear-gallery-height-capacity.json'
REUSE_CASES_FROM=OUT/'source-group-capacity-plan.json'
read=R.read;sha=R.sha;build=L.expanded_gate_plan
geometry_digest=R.geometry_digest

if __name__=='__main__':
    # Compact gate input is independently derived, not the original trial.
    p=read(PLAN)
    assert p['status']=='TWO_PROTECTED_BODY_FEEDS_PLANNED_TAIL_RECEIVING_STATION_BLOCKED'
    for n,h in p['source_sha256'].items():assert sha(ROOT/n)==h,n
    original_read=read
    def read(path):
        data=original_read(path)
        if Path(path)==PLAN:
            data=dict(data,recipe_compact=True,materialized_geometry_digest=geometry_digest(build()))
        return data
    import sys
    D.G=sys.modules[__name__];D.POINT_SCREEN=True;D.run()
