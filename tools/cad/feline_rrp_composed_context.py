"""One received curved-source layout over the unchanged current scene."""
import json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_output_composed_context import compose as parent
from receive_feline_rrp_shared_height import load


def received():
    f=OUT/'n01-RRP-shared-height.json';r=json.loads(f.read_text())
    assert r['status']=='RRP_SHARED_HEIGHT_STATIC36_RECEIVED_ROOTS_AND_ASSEMBLY_OPEN'
    assert not r['failures'] and len(r['completed_static'])==len(r['completed_motion'])==8
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return f,r


def compose():
    world,parts,meta,pins,docs=parent();f,r=received();actors=load(r)
    for n in r['retired']:assert n in parts;parts.pop(n);meta.pop(n)
    for row in r['geometry']:
        n=row['name'];parts[n]=actors[n];meta[n]=dict(row)
        if n.endswith((':band_budget',':head_budget')):meta[n]['material_role']='selected_T18I_nylon_budget'
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (f,ROOT/r['bundle'],ROOT/r['pair_rows'],ROOT/'tools/cad/feline_rrp_composed_context.py')})
    docs.update(RRP_received=r,RRP_changed=set(actors),RRP_retired=r['retired'])
    return world,parts,meta,pins,docs
