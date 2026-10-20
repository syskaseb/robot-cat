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
    paths=[OUT/n for n in ('n01-U1-frontband-common-plan.json','n01-U1-frontband-common-received.json','n01-existing-HP-current-delta.json','n01-HP-selected-R12p6-received.json')]
    plan,u1,hp,hpr=[json.loads(p.read_text()) for p in paths]
    assert u1['status']=='U1_FIVE_COMMON_RESTRAINTS_STATIC36_RECEIVED_FULL123_ASSEMBLY_OPEN' and not u1['failures']
    assert len(u1['completed_static'])==len(u1['completed_motion'])==29
    assert hp['status']=='EXISTING_HP_SIX_KIT_CURRENT_DELTA_RECEIVED_HEAD_MOTION_SKIN_OPEN' and not hp['failures']
    assert hpr['status']=='HP_SELECTED_R12p6_STATIC36_RECEIVED_HEAD_SKIN_MOTION_OPEN' and not hpr['failures']
    assert len(hpr['geometry'])==3 and all(g['minimum_wire_R_mm']==12.6 for g in hpr['geometry'])
    assert sha(ROOT/hpr['bundle'])==hpr['bundle_sha256']
    assert u1['source_sha256'][paths[0].relative_to(ROOT).as_posix()]==sha(paths[0])
    assert sha(ROOT/plan['bundle'])==plan['bundle_sha256']
    updates.update(copy.deepcopy(plan['updates']));assert len(updates)==5
    for eid,r in updates.items():
        r.update(routing_boundary_status='CURRENT_RECEIVED_U1_FIVE_SOURCE_GRIP_ROOT_OUTLET',
            grip_length_mm=9,current_restraint_receipt=paths[1].relative_to(ROOT).as_posix(),
            independent_grip_root_and_sampled_leg_motion_received=True,full_middle_route_accepted=False)
    updates.update(copy.deepcopy(hp['updates']));assert len(updates)==8
    for g in hpr['geometry']:
        r=next(v for v in updates.values() if v.get('prefix_geometry_owner')==g['name'])
        assert r['routing_exit_mm']==g['end_mm'] and r['jacket_grip9_mm']==g['source_full9_mm']
        r.update(source_prefix_length_mm=g['path_length_mm'],received_prefix_R_mm=12.6,
            current_restraint_receipt=paths[-1].relative_to(ROOT).as_posix(),
            routing_boundary_status='CURRENT_HP_SELECTED_R12p6_SOURCE_GRIP_ROOT_OUTLET_HEAD_MOTION_SKIN_OPEN')
    earlyfile=OUT/'n01-U1-early-pair.json';early=json.loads(earlyfile.read_text())
    assert early['status']=='U1_EARLY_PAIR_STATIC36_RECEIVED_FULL123_OPEN' and not early['failures']
    assert sha(ROOT/early['bundle'])==early['bundle_sha256']
    for eid,r in early['updates'].items():
        assert eid in updates and eid.startswith(('XP02.module/','XP03.module/'))
        values={k:v for k,v in r.items() if k not in ('id','wire','portion_id','endpoint','group')}
        values.update(current_restraint_receipt=earlyfile.relative_to(ROOT).as_posix(),
            routing_boundary_status='CURRENT_U1_EARLY_PAIR_FULL9_CURVED_ROOT_STATIC36',
            independent_grip_root_and_sampled_leg_motion_received=True)
        updates[eid]=values
    paths.extend((earlyfile,ROOT/early['motion_receipt']))
    resolved=apply_updates(rows,updates)
    assert len(base['portions'])==123 and len(resolved)==246
    assert all(a['point_mm'] is not None or b['point_mm'] is None for a,b in zip(rows,resolved))
    return base,resolved,(*files,*paths)
