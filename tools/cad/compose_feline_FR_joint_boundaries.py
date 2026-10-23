"""Current four changed boundaries; original W035 remains byte-for-byte data."""
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
    resolved=apply_updates(rows,r['updates'])
    assert len(resolved)==246 and [e['id'] for e in resolved]==[e['id'] for e in rows]
    for old,new in zip(rows,resolved):
        assert old['point_mm']==new['point_mm']
        if old['id'] not in r['updates']:assert old==new
    return base,resolved,(*files,path)
