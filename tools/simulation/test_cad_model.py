import json
import math
from pathlib import Path
import numpy as np
import pytest
from cad_model import (OUT,R,REVISION,xyz,make_model,mass_budget,combine,reactions,
                       actuator_envelope,KGFCM_TO_NM,static_report,write_sdf)


@pytest.fixture(scope='module')
def geometry():
    return json.loads((OUT/'geometry.json').read_text(encoding='utf8'))


def test_right_handed_frame():
    assert np.linalg.det(R)==pytest.approx(1)
    assert xyz([21,0,18.51])==pytest.approx([0,0,0])
    assert xyz([-79,0,18.51])==pytest.approx([.1,0,0])


def test_part_mass_accounting(geometry):
    rows=mass_budget(geometry)
    assert len(rows)==239 and len({r['name'] for r in rows})==239
    servos=[r for r in rows if r['basis'].startswith('ST3215 body')]
    assert len(servos)==72
    assert sum(r['mass_kg'] for r in servos)==pytest.approx(12*.069)
    assert next(r for r in rows if r['name']=='Battery')['mass_kg']==pytest.approx(.174)
    assert next(r for r in rows if r['name']=='Pi')['mass_kg']==pytest.approx(.046)


def test_inverted_hip_mount_ownership(geometry):
    if REVISION=='v25':pytest.skip('v25 ownership is known wrong, retained as historical evidence')
    for axis in geometry['axes']:
        if axis['stage']!='Hip':continue
        number=int(axis['horn'].replace('Part__Feature',''))
        for i in range(number-6,number+2):
            part=next(p for p in geometry['components'] if p['name']=='Part__Feature%03d'%i)
            assert part['stage']==('Motion_'+axis['code']+'_Hip' if i<number else 'Chassis')


def test_parallel_axis_theorem():
    parts=[dict(mass_kg=1,com_m=[x,0,0],inertia_kg_m2=np.eye(3).tolist()) for x in [-1,1]]
    result=combine(parts)
    assert result['com_m']==pytest.approx([0,0,0])
    assert np.asarray(result['inertia_kg_m2'])==pytest.approx(np.diag([2,4,4]))


def test_link_inertias_and_topology(geometry):
    model=make_model(geometry)
    assert len(model['links'])==13 and len(model['joints'])==12
    assert sum(l['mass_kg'] for l in model['links'])==pytest.approx(model['total']['mass_kg'])
    for l in model['links']:
        I=np.asarray(l['inertia_kg_m2']);ev=np.linalg.eigvalsh(I)
        assert I==pytest.approx(I.T)
        assert ev.min()>0 and ev.max()<=sum(ev)/2+1e-12
    for j in model['joints']:assert np.linalg.norm(j['axis'])==pytest.approx(1)


def test_torque_speed_and_voltage():
    a=actuator_envelope(12)
    assert a['stall_nm']==pytest.approx(30*KGFCM_TO_NM)
    assert a['no_load_rad_s']==pytest.approx(math.pi/3/.222)
    assert actuator_envelope(12,a['no_load_rad_s'])['moving_limit_nm']==pytest.approx(0)
    assert actuator_envelope(10.5)['stall_nm']<a['stall_nm']
    assert actuator_envelope(12,a['no_load_rad_s']/2)['moving_limit_nm']==pytest.approx(a['stall_nm']/2)


def test_equilibrium_detects_tipping():
    f,ok=reactions([[-1,-1,0],[-1,1,0],[1,1,0],[1,-1,0]],4,[0,0,1])
    assert ok and f==pytest.approx([9.80665]*4)
    _,ok=reactions([[-1,-1,0],[-1,1,0],[1,1,0]],4,[.9,-.9,1])
    assert not ok


def test_current_model_static(geometry):
    model=make_model(geometry)
    feet=json.loads((OUT/'feet.json').read_text())
    report=static_report(model,feet)
    assert report['four_foot_equilibrium']
    assert sum(report['normal_forces_N'].values())==pytest.approx(model['total']['mass_kg']*9.80665)
    assert len(report['joint_torques'])==12
    assert max(abs(t['torque_nm']) for t in report['joint_torques'])<1


def test_no_free_velocity_braking_constraint(geometry,tmp_path):
    import xml.etree.ElementTree as ET
    path=tmp_path/'world.sdf'
    write_sdf(make_model(geometry),json.loads((OUT/'feet.json').read_text()),path=path)
    root=ET.parse(path).getroot()
    assert len(root.findall('.//joint'))==12
    assert not root.findall('.//joint/axis/limit/velocity')
