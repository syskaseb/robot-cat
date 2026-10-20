"""Received outward-output planning overlay, not selected native production CAD."""
import json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_profile_corrected_context import compose as parent
from receive_feline_psys_frame_load_paths import load


def received():
    f=OUT/'n01-rooted-end-bays-caps.json';r=json.loads(f.read_text())
    assert r['status']=='END_BAY_OUTPUTS_RECEIVED_ROOTS_OPEN' and not r['failures']
    assert r['full_changed_motion_received'] and len(r['completed_static'])==len(r['completed_motion'])==60
    assert r['reused_receipt']['fixed_source_pins_verified'] and len(r['reused_receipt']['byte_identical_actors'])==58
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    groups=r['revision']['planned_print_unions'];assert len(groups)==2 and all(g['union_solids']==1 for g in groups)
    return f,r


def compose():
    world,parts,meta,pins,docs=parent();f,r=received();actors=load(r,'geometry')
    assert len(r['retired_current_actors'])==72 and len(actors)==60
    for n in r['retired_current_actors']:assert n in parts,n;parts.pop(n);meta.pop(n,None)
    parts.update(actors)
    for n in actors:meta[n]=dict(r['actor_meta'][n],current_output_wire=r['actor_owner'][n])
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (f,ROOT/r['bundle'],ROOT/r['pair_rows'],ROOT/'tools/cad/feline_output_composed_context.py')})
    docs.update(output_receipt=r,output_retired=set(r['retired_current_actors']),output_changed=set(actors),output_load_paths=r['revision']['positive_load_paths'])
    return world,parts,meta,pins,docs
