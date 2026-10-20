"""Current received body-side cuff capacity prefixes over rooted RR_P."""
import json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_rrp_rooted_context import compose as parent
from receive_feline_rrp_shared_height import load


def received():
    f=OUT/'n01-fixed-cuff-seam-prefixes.json';r=json.loads(f.read_text())
    assert r['status']=='CONSTRUCTIVE_LINKS_STATIC36MOTION_RECEIVED_REMAINING_N01_OPEN' and not r['failures']
    assert len(r['completed_static'])==len(r['completed_motion'])==27
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return f,r


def compose():
    world,parts,meta,pins,docs=parent();f,r=received();actors=load(r)
    for link in r['links']:
        n=link['name'];assert n not in parts
        parts[n]=actors[n];meta[n]=dict(kind='wire',wire_owner=link['wire'],
            geometry_is_cuff_MAX_OD_capacity_not_supplier_OD=True)
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (f,ROOT/r['bundle'],ROOT/r['pair_rows'],ROOT/'tools/cad/feline_cuff_composed_context.py')})
    docs.update(cuff_prefixes=r,cuff_changed=set(actors),current_routing_owner_field_needs_RRP_plus27_delta=True)
    return world,parts,meta,pins,docs
