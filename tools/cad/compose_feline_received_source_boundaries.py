"""Eight received local-source outlets over the pinned246-end register.

Reference the received geometry and unchanged identities, not a copied ledger
or an implicit completion claim. No original sources or selected CAD change.
"""
import copy,json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from compose_feline_source_mta_boundaries import current as parent
from compose_feline_integrated_boundaries import apply_updates


def current():
    base,rows,files=parent();updates={}
    paths=[OUT/n for n in ('n01-U1-frontband-common-plan.json','n01-U1-frontband-common-received.json','n01-existing-HP-current-delta.json')]
    plan,u1,hp=[json.loads(p.read_text()) for p in paths]
    assert u1['status']=='U1_FIVE_COMMON_RESTRAINTS_STATIC36_RECEIVED_FULL123_ASSEMBLY_OPEN' and not u1['failures']
    assert len(u1['completed_static'])==len(u1['completed_motion'])==29
    assert hp['status']=='EXISTING_HP_SIX_KIT_CURRENT_DELTA_RECEIVED_HEAD_MOTION_SKIN_OPEN' and not hp['failures']
    assert u1['source_sha256'][paths[0].relative_to(ROOT).as_posix()]==sha(paths[0])
    assert sha(ROOT/plan['bundle'])==plan['bundle_sha256']
    updates.update(copy.deepcopy(plan['updates']));assert len(updates)==5
    for eid,r in updates.items():
        r.update(routing_boundary_status='CURRENT_RECEIVED_U1_FIVE_SOURCE_GRIP_ROOT_OUTLET',
            grip_length_mm=9,current_restraint_receipt=paths[1].relative_to(ROOT).as_posix(),
            independent_grip_root_and_sampled_leg_motion_received=True,full_middle_route_accepted=False)
    updates.update(copy.deepcopy(hp['updates']));assert len(updates)==8
    resolved=apply_updates(rows,updates)
    assert len(base['portions'])==123 and len(resolved)==246
    assert all(a['point_mm'] is not None or b['point_mm'] is None for a,b in zip(rows,resolved))
    return base,resolved,(*files,*paths)
