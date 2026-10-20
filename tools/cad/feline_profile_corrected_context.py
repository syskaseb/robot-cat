"""Current profile-corrected working layout; immutable R2 parent retained."""
import json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_retention_composed_context import compose as parent
from receive_feline_psys_frame_load_paths import load


def compose():
    world,parts,meta,pins,docs=parent();f=OUT/'n01-psys-selected-wire-profile.json';r=json.loads(f.read_text())
    assert r['status']=='SELECTED_W066_PROFILE_AND_OWN_GROOVE_RECEIVED' and not r['failures'] and not r['errors']
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    corrected=load(r,'geometry')
    for n,s in corrected.items():parts[n]=s
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (f,ROOT/r['bundle'],ROOT/'tools/cad/feline_profile_corrected_context.py')})
    docs.update(selected_profile_correction=r,corrected_profile_actor_names=set(corrected),
        old_rigid_field_still_conservative_comb_subset=True,old_W066_harness_cells_not_current_clearance=True)
    return world,parts,meta,pins,docs
