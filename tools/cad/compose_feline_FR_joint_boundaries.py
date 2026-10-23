"""Current three complete FR bodies; W035 source geometry remains original."""
import json
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from compose_feline_current_body_routes import current as parent
from compose_feline_integrated_boundaries import apply_updates


def current():
    base,rows,files=parent();path=OUT/'n01-FR-W031-W033-common-body-plan.json'
    r=json.loads(path.read_text())
    assert r['status']=='FR_TWO_COMPLETE_BODY_CURVES_CURRENT_BOUNDARIES_RECEIVED_NOT_N01'
    assert r['W035_original_source_retained'] and all(c['ok'] for c in r['checks'].values())
    assert sha(ROOT/r['bundle'])==r['bundle_sha256']
    for name,h in r['source_sha256'].items():assert sha(ROOT/name)==h,name
    assert set(r['updates'])=={w+'/body/'+side for w in ('W031','W033') for side in ('start','end')}
    extra_path=OUT/'n01-current-W035-retained-source-body-plan.json'
    extra=json.loads(extra_path.read_text())
    assert extra['status']=='RETAINED_SOURCE_CHANGED_BANK_COMPLETE_BODY_RECEIVED_NOT_N01'
    assert extra['wire']=='W035' and extra['source_geometry_unchanged']
    assert all(c['ok'] for c in extra['checks'].values()) and extra['outer']['ok']
    assert sha(ROOT/extra['bundle'])==extra['bundle_sha256']
    for name,h in extra['source_sha256'].items():assert sha(ROOT/name)==h,name
    updates={**r['updates'],**extra['updates']}
    resolved=apply_updates(rows,updates)
    assert len(resolved)==246 and [e['id'] for e in resolved]==[e['id'] for e in rows]
    for old,new in zip(rows,resolved):
        assert old['point_mm']==new['point_mm']
        if old['id'] not in updates:assert old==new
        if old['id']=='W035/body/start':
            for key in ('routing_exit_mm','routing_exit_axis','source_prefix_length_mm','prefix_geometry_owner'):
                assert old.get(key)==new.get(key),key
    return base,resolved,(*files,path,extra_path)
