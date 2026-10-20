"""Received grounded RR_P planning module; other current interfaces unchanged."""
import json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_rrp_composed_context import compose as parent
from receive_feline_rrp_shared_height import load


def received():
    f=OUT/'n01-RRP-root-contract-received.json';r=json.loads(f.read_text())
    assert r['status']=='RRP_ROOT_CONTRACT_STATIC36_RECEIVED_ASSEMBLY_OPEN' and not r['failures']
    assert r['adopted_motion_pose_records']==3888 and r['recipe']['combined_bankbed_root_single_Solid']
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return f,r


def compose():
    world,parts,meta,pins,docs=parent();f,r=received();actors=load(r)
    assert list(actors)==['EarlyRR:comb:inner'];parts.update(actors)
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (f,ROOT/r['bundle'],ROOT/r['pair_rows'],ROOT/'tools/cad/feline_rrp_rooted_context.py')})
    docs.update(RRP_rooted=r,RRP_print_union=['CurrentFoundation:BankBedCurrent:1','EarlyRR:comb:inner'])
    return world,parts,meta,pins,docs
