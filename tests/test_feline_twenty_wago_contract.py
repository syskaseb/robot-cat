from pathlib import Path
import sys
import math
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/cad'))
from compose_feline_twenty_wago_contract import compose


def test_all_twenty_and_unique_cavities():
    p=compose();assert p['station_count']==20
    ports=[r['endpoint'] for s in p['stations'] for r in s['occupied_ports']]
    assert len(set(ports))==len(ports)==p['occupied_cavities']
    assert len(p['three_extra_face_transfers'])==3
    assert not p['N01_complete'] and not p['selected']
    assert p['untouched_selected_parts_and_ECAD']


def test_current_aux_faces_and_ground_cavities():
    p=compose();stations={s['ref']:s for s in p['stations']}
    for ref in ('P_AUX','G_AUX','G_TAIL'):
        for r in stations[ref]['occupied_ports']:
            assert math.isclose(r['point_mm'][1],-76.5,abs_tol=1e-4)
            assert math.isclose(r['point_mm'][2],40,abs_tol=1e-4)
            assert r['departure_axis']==[0,-1,0]
    assert next(r for r in stations['RL_G']['occupied_ports'] if r['wire']=='W071')['physical_port']==3
    assert next(r for r in stations['RL_G']['occupied_ports'] if r['wire']=='W062')['physical_port']==4
    assert stations['RL_P']['schematic_to_physical_common_rail_map']=={'1':5,'2':2,'3':3,'4':4,'5':1}
    feed=next(r for r in stations['RL_P']['occupied_ports'] if r['wire']=='W045/custom')
    assert feed['schematic_port']==1 and feed['physical_port']==5
    assert math.dist(feed['point_mm'],[-33.5,-24.5,-19.75])<1e-4
