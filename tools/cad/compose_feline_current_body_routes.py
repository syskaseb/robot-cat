"""Adopt received whole body curves without awarding whole900 or N01."""
import json
import numpy as np
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from compose_feline_rr_two_tier_boundaries import current as parent
from compose_feline_integrated_boundaries import apply_updates


def current():
    base,rows,files=parent();byid={e['id']:e for e in rows};updates={}
    path=OUT/'n01-current-W022-complete-body-plan.json';p=json.loads(path.read_text())
    assert p['status']=='CURRENT_W022_COMPLETE_STATIC_BODY_CURVE_AND_SAMPLE36_RECEIVED_NOT_N01'
    assert sha(ROOT/p['bundle'])==p['bundle_sha256']
    assert all(r['ok'] for r in p['checks'].values()) and p['outer']['ok']
    assert not p['N01_complete'] and not p['physical_pass']
    for name,h in p['source_sha256'].items():assert sha(ROOT/name)==h,name
    for r in p['current_boundaries']:
        old=byid[r['id']];assert old['portion_id']==p['portion']
        assert np.allclose(old['routing_exit_mm'],r['point_mm'],atol=1e-7,rtol=0)
        assert np.allclose(old['routing_exit_axis'],r['axis'],atol=1e-7,rtol=0)
        updates[r['id']]=dict(full_middle_route_accepted=True,whole_portion_received=True,
            whole_portion_receipt=path.relative_to(ROOT).as_posix(),
            whole_body_length_mm=p['complete_body_length_mm'],
            current_complete_middle_owner='CurrentMiddle:W022',
            whole_factory900_and_moving_portion_NOT_received=True)
    resolved=apply_updates(rows,updates)
    assert len(resolved)==246 and [e['id'] for e in resolved]==[e['id'] for e in rows]
    return base,resolved,(*files,path)
