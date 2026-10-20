"""Bind received31 HP pairs to the complete current planned owner graph.

Only identity checks here, not a second geometry/distance audit. Earlier
scoped receipt is immutable. Every queried obstacle is byte-identical in the
reproducible MTA/source/U1/HP composition, whose full input graph is pinned.
"""
import gzip,hashlib,json,time
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def save(checked_parts,composed):
    tick=time.monotonic();_,parts,meta,pins,info=composed
    src=OUT/'n01-HP-selected-R12p6-received.json';r=json.loads(src.read_text())
    assert r['status']=='HP_SELECTED_R12p6_STATIC36_RECEIVED_HEAD_SKIN_MOTION_OPEN' and not r['failures']
    rows=json.loads(gzip.decompress((ROOT/r['pair_rows']).read_bytes()))
    names={k.split('|',1)[1] for k in rows if '|motion:' not in k};identities={}
    for n in names:
        before=checked_parts[n].exportBrepToString();after=parts[n].exportBrepToString()
        assert before==after,('Changed checked obstacle needs new pair reception',n)
        identities[n]=dict(brep_sha256=hashlib.sha256(after.encode()).hexdigest(),
            owner=info['current_overlay_owners'].get(n,'Pinned main-hung parent'))
    result=dict(status='HP_RECEIVED_PAIRS_BOUND_TO_CURRENT1448_PLANNED_SCENE',
        source_sha256={**pins,src.relative_to(ROOT).as_posix():sha(src),
            'tools/cad/bind_feline_hp_current_context.py':sha(ROOT/'tools/cad/bind_feline_hp_current_context.py')},queried_obstacle_identities=identities,
        no_new_distance_queries=True,current_actor_count=len(parts),
        current_bounds_reconciled=True,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-HP-current-composed-context-binding.json',result)
    print(result['status'],len(identities),result['worker_seconds'],flush=True);return result
