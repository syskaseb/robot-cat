import importlib.util
from pathlib import Path
import sys
import math

TOOLS=Path(__file__).resolve().parents[1]/'tools/cad'
sys.path.insert(0,str(TOOLS))
from compose_feline_current_endpoint_packet import branch_point,branch_direction,compose


def test_rigid_branch_transform():
    d=dict(old_centre_mm=[-95,0,-34],new_centre_mm=[17.5,-14,-34])
    assert branch_point([-95,-56,-34],d)==[-38.5,-14,-34]
    assert branch_direction([0,-1,0])==[-1,0,0]
    assert math.dist(branch_point([-95,-17.5,-34],d),branch_point([-95,-38.25,-34],d))==20.75


def test_packet_all_identity_pairs_and_no_route_inheritance():
    p=compose()
    assert len(p['endpoints'])==178 and len(p['changed_endpoint_ids'])==62
    assert len(p['physical_segment_lower_bounds'])==89 and p['logical_nets']==80
    assert not any(e['complete_route_verified'] or e['stock_selected'] for e in p['endpoints'])
    assert not p['N01_complete'] and not p['selected']


def test_full_factory_lands_and_no_stock_waiver():
    p=compose()
    for row in p['factory_lengths'].values():
        assert row['grip_length_mm']==9 and row['between_grips_mm']>2.24
        assert row['grip_offsets_from_start_mm'][0]==.25
        assert row['factory100mm_is_project_assumption']
    e={r['id']:r for r in p['endpoints']}
    assert e['W043/single/start']['point_mm']==[-27.45,0,41.1]
    assert math.dist(e['W078/retained0/start']['point_mm'],[-71.55,-24.0,48.1])<1e-8


def test_full_scene_lower_bay_replaces_all_rejected_case_endpoints():
    p=compose(lower_bay=True)
    assert len(p['endpoints'])==178 and len(p['changed_endpoint_ids'])==62
    assert len(p['physical_segment_lower_bounds'])==89 and p['logical_nets']==80
    assert not p['rejected_central_cassette_MTA_endpoints_used']
    ends={r['id']:r for r in p['endpoints']}
    for w in ('W026','W037','W041','W042','W044','W045','W052','W053'):
        a,b,c=[ends[w+suffix] for suffix in ('/factory/start','/factory/end','/custom/start')]
        assert 'lower bay' in a['current_update'] and 'lower bay' in c['current_update']
        assert math.isclose(b['point_mm'][2],-34,abs_tol=1e-4)
        assert math.isclose(math.dist(b['point_mm'],c['point_mm']),35.5,abs_tol=1e-4)
        assert math.dist(b['departure_axis'],[-v for v in c['departure_axis']])<1e-5
        assert p['factory_lengths'][w]['guide_mm']<=100
    assert 88<p['factory_lengths']['W041']['guide_mm']<89
    assert math.isclose(ends['W041/factory/end']['point_mm'][1],33.25,abs_tol=1e-4)
    assert math.isclose(ends['W052/factory/end']['point_mm'][1],-33.25,abs_tol=1e-4)
    assert not any(e['complete_route_verified'] or e['stock_selected'] for e in p['endpoints'])
    assert not p['N01_complete'] and not p['selected']
