"""Adopt received whole body curves without awarding whole900 or N01."""
import json
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from compose_feline_rr_two_tier_boundaries import current as parent
from compose_feline_integrated_boundaries import apply_updates


def current():
    base,rows,files=parent();byid={e['id']:e for e in rows};updates={}
    for filename,status in (
        ('n01-current-W022-complete-body-plan.json','CURRENT_W022_COMPLETE_STATIC_BODY_CURVE_AND_SAMPLE36_RECEIVED_NOT_N01'),
        ('n01-current-W024-shared-complete-body-plan.json','CURRENT_W024_SHARED_TRUNK_COMPLETE_BODY_AND_SAMPLE36_RECEIVED_NOT_N01'),
        ('n01-current-W020-complete-body-plan.json','CURRENT_W020_COMPLETE_BODY_AND_SAMPLE36_RECEIVED_NOT_N01'),
        ('n01-current-W009-complete-body-plan.json','CURRENT_BODY_CANONICAL_SOURCES_AND_SAMPLE36_RECEIVED_NOT_N01'),
        ('n01-current-W069-complete-body-plan.json','CURRENT_BODY_CANONICAL_SOURCES_AND_SAMPLE36_RECEIVED_NOT_N01')):
        path=OUT/filename;p=json.loads(path.read_text())
        assert p['status']==status and sha(ROOT/p['bundle'])==p['bundle_sha256']
        assert all(r['ok'] for r in p['checks'].values()) and p['outer']['ok']
        if p['portion']=='W020/body':
            assert p['motion_actors_covered']==3888 and p['sampled_poses']==36
            assert p['motion_vertical_lower_bound_mm']>=1.25-1e-6
        if p['portion'] in ('W009/body','W069/body'):
            assert p['motion_actors_covered']==3888 and p['sampled_poses']==36
            motion=json.loads((ROOT/p['motion_receipt']).read_text())
            assert motion['status']=='SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED'
            assert all(r['ok'] for r in motion['checks'].values())
            assert p['current_named_sources_covered']==1527
        assert not p['N01_complete'] and not p['physical_pass']
        for name,h in p['source_sha256'].items():assert sha(ROOT/name)==h,name
        for r in p['current_boundaries']:
            old=byid[r['id']];assert old['portion_id']==p['portion']
            assert np.allclose(old['routing_exit_mm'],r['point_mm'],atol=1e-7,rtol=0)
            assert np.allclose(old['routing_exit_axis'],r['axis'],atol=1e-7,rtol=0)
            updates[r['id']]=dict(full_middle_route_accepted=True,whole_portion_received=True,
                whole_portion_receipt=path.relative_to(ROOT).as_posix(),
                whole_body_length_mm=p['complete_body_length_mm'],
                current_complete_middle_owner='CurrentMiddle:'+p['portion'].split('/')[0],
                whole_factory900_and_moving_portion_NOT_received=True)
        files=(*files,path)
    resolved=apply_updates(rows,updates)
    # The old cap overlay predates the static36 and fastener receipts. Attach
    # their precise scopes, without promoting them to whole-current service.
    main_world=OUT/'n01-MAIN-hung-world.json'
    main_tools=OUT/'n01-MAIN-fastener-sequence-received.json'
    mw=json.loads(main_world.read_text());mt=json.loads(main_tools.read_text())
    assert mw['status']=='MAIN_WHOLE_STATIC36_RECEIVED_TOOLS_ASSEMBLY_OPEN'
    assert not mw['failures'] and len(mw['completed_static'])==25 and len(mw['completed_motion'])==25
    assert sha(ROOT/mw['pair_rows'])==mw['pair_rows_sha256']
    assert mt['status']=='MAIN_TWO_AXIS_FASTENER_ACCESS_RECEIVED_HARNESS_RELEASE_OPEN'
    assert mt['completed_axes']==[0,1]
    for source,h in mw['source_sha256'].items():
        if 'n01-MAIN-hung-union-received' in source:assert sha(ROOT/source)==h,source
    main_updates={}
    for e in resolved:
        if e.get('routing_boundary_status')!='CURRENT_MAIN_HUNG_ACTUAL_NOMINAL_CAP_LOCAL_RECEIVED_WORLD_OPEN':continue
        main_updates[e['id']]=dict(
            routing_boundary_status='CURRENT_MAIN_CAP_STATIC36_AND_FASTENER_RECEIPTS_AVAILABLE_COMMON_SERVICE_OPEN',
            static36_receipt=main_world.relative_to(ROOT).as_posix(),
            fastener_sequence_receipt=main_tools.relative_to(ROOT).as_posix(),
            world_and_tools_assembly_NOT_received=True,
            whole_current_scene_delta_and_harness_release_OPEN=True,
            whole_service_sequence_received=False)
    assert len(main_updates)==4
    resolved=apply_updates(resolved,main_updates)
    files=(*files,main_world,main_tools)
    assert len(resolved)==246 and [e['id'] for e in resolved]==[e['id'] for e in rows]
    return base,resolved,files
