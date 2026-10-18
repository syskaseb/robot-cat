from pathlib import Path
import sys
import math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from plan_feline_current_port_contracts import compose


def test_current_kicad_cavities_not_historical_aliases():
    p=compose();e={r['id']:r for r in p['endpoints']}
    assert e['W062/retained0/end']['role']=='RL_G.4'
    assert e['W071/body/end']['role']=='RL_G.3'
    assert e['W063/retained0/end']['role']=='RR_G.4'
    assert e['W074/body/end']['role']=='RR_G.3'
    assert len({r['role'] for r in e.values() if r['group'].startswith('WAGO:')})==sum(r['group'].startswith('WAGO:') for r in e.values())
    assert not p['ecad_file_changed'] and not p['selected_parts_changed']


def test_complete_whole_junction_and_parallel_pair_contracts():
    p=compose();e={r['id']:r for r in p['endpoints']}
    for key in ('W076/retained0/end','W076/retained1/start'):
        assert math.dist(e[key]['departure_axis'],[0,-1,0])<1e-6
    a,b=e['W079/retained0/end'],e['W080/retained0/end']
    assert a['point_mm'][1:]==b['point_mm'][1:]
    assert math.isclose(b['point_mm'][0]-a['point_mm'][0],3.5)
    assert all(r['departure_axis']==[0,1,0] for r in e.values() if r['group']=='WAGO:G1_CP2')
    assert len(e)==178 and len(p['physical_segment_lower_bounds'])==89
    assert not p['N01_complete'] and not p['geometry_gate_complete'] and not p['selected']
