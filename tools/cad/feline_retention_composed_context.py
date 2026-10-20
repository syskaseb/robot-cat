"""One working layout overlay from the received node; no native selection."""
import json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT


def received():
    cf=OUT/'n01-psys-flp-joint-retention-r2.json';gf=OUT/'n01-psys-flp-frame-load-paths.json'
    core=json.loads(cf.read_text());graph=json.loads(gf.read_text())
    assert not core['failures'] and not core['errors']
    assert graph['status']=='ALL_CHANGED_FRAME_SOLIDS_REACH_EXISTING_CLAMP_SEATS' and not graph['floating_solids']
    assert graph['source_sha256'][cf.relative_to(ROOT).as_posix()]==sha(cf)
    for p,h in core['source_sha256'].items():assert sha(ROOT/p)==h,p
    for p,h in graph['source_sha256'].items():assert sha(ROOT/p)==h,p
    return cf,gf,core,graph


def compose():
    from feline_integrated_space_context import integrated
    from receive_feline_psys_frame_load_paths import load
    world,parts,meta,pins,docs=integrated();cf,gf,core,graph=received();actors=load(core,'geometry')
    retired=core['retired_only_own_custom_prefix_actors']+[core['retired_printed_support']]
    for n in retired:assert n in parts,n;parts.pop(n);meta.pop(n,None)
    for r in core['geometry']:
        n=r['name'];parts[n]=actors[n];meta[n]=dict(meta.get(n,{}),**r)
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (cf,gf,ROOT/core['bundle'],ROOT/'tools/cad/feline_retention_composed_context.py')})
    docs.update(retention_core=core,retention_retired=retired,retention_changed=set(actors),retention_frame_graph=graph)
    return world,parts,meta,pins,docs
