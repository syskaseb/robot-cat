"""One current constructive MAIN proposal; whole-world gate is still separate."""
import json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_cuff_composed_context import compose as parent
from receive_feline_rrp_shared_height import load


def received():
    f=OUT/'n01-MAIN-hung-union-received.json';r=json.loads(f.read_text())
    assert r['status']=='MAIN_HUNG_LOCAL_CONSTRUCTIVE_PLAN_RECEIVED_WORLD_TOOLS_OPEN' and not r['failures']
    assert r['byte_identical_actor_count']==25 and r['original_Pi_PWM_carrier_unchanged']
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return f,r


def compose():
    world,parts,meta,pins,docs=parent();f,r=received();actors=load(r)
    for n in r['retired']:assert n in parts,n;parts.pop(n);meta.pop(n,None)
    for row in r['geometry']:
        n=row['name'];assert n not in parts,n;parts[n]=actors[n];meta[n]=dict(row,group='MAINUpper')
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (f,ROOT/r['bundle'],ROOT/r['pair_rows'],ROOT/'tools/cad/feline_main_hung_context.py')})
    docs.update(MAIN_local=r,MAIN_changed=set(actors),MAIN_retired=set(r['retired']),MAIN_world_qualified=False)
    return world,parts,meta,pins,docs
