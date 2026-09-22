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
    expected=len(geometry['components'])+1
    assert len(rows)==expected and len({r['name'] for r in rows})==expected
    servos=[r for r in rows if r['basis'].startswith('ST3215 body')]
    assert len(servos)==72
    assert sum(r['mass_kg'] for r in servos)==pytest.approx(12*.069)
    assert next(r for r in rows if r['name']=='Battery')['mass_kg']==pytest.approx(.174)
    assert next(r for r in rows if r['name']=='Pi')['mass_kg']==pytest.approx(.046)


def test_v29_auxiliary_and_fastener_mass_classification(geometry):
    if REVISION not in ('v29','v30','v31','v32','v33','v34'):pytest.skip('v29+ tail integration only')
    rows={r['name']:r for r in mass_budget(geometry)}
    assert rows['MG92BCase29']['mass_kg']+rows['MG92BOutput29']['mass_kg']==pytest.approx(.0138)
    assert not {'TailYawServo','TailLiftServo'} & set(rows)
    bolts=[r for n,r in rows.items() if n.startswith(('TailBolt29','TailFrameBolt29','TailMountBolt29','TailEarBolt29'))]
    assert len(bolts)==16 and all(r['basis'].startswith('steel') for r in bolts)
    assert all(r['stage']=='Chassis' for n,r in rows.items() if n.startswith('Tail'))
    assert geometry['frozen_native_joints']==['Rev_TailYaw29']


def test_v30_imu_parts_are_rigidly_accounted_for(geometry):
    if REVISION not in ('v30','v31','v32','v33','v34'):pytest.skip('v30+ IMU mounting only')
    rows={r['name']:r for r in mass_budget(geometry)}
    assert len(geometry['components'])=={'v30':264,'v31':280,'v32':286,'v33':289,'v34':306}[REVISION]
    assert rows['IMU']['mass_kg']==pytest.approx(.004)
    posts=[r for n,r in rows.items() if n.startswith('IMUPost30_')]
    screws=[r for n,r in rows.items() if n.startswith('IMUBolt30_')]
    nuts=[r for n,r in rows.items() if n.startswith('IMUNut30_')]
    assert len(posts)==len(screws)==len(nuts)==4
    assert all(r['stage']=='Chassis' for r in posts+screws+nuts)
    assert all(r['basis'].startswith('solid CAD PETG') for r in posts)
    assert all(r['basis'].startswith('steel') for r in screws+nuts)
    assert sum(r['mass_kg'] for r in posts)==pytest.approx(4*153.9028541881796*1.27e-6)


def test_v31_power_mount_mass_classification(geometry):
    if REVISION not in ('v31','v32','v33','v34'):pytest.skip('v31+ main regulator mounting only')
    rows={r['name']:r for r in mass_budget(geometry)}
    assert rows['Pololu']['mass_kg']==pytest.approx(.0048)
    terminals=[r for n,r in rows.items() if n.startswith('PowerTerminal31_')]
    assert len(terminals)==2 and all(r['mass_kg']==pytest.approx(.002) for r in terminals)
    posts=[r for n,r in rows.items() if n.startswith(('PowerPost31_','PowerGapSpacer31_'))]
    bolts=[r for n,r in rows.items() if n.startswith(('PowerBolt31_','PowerNut31_'))]
    assert len(posts)==6 and len(bolts)==8
    assert all(r['stage']=='Chassis' for r in terminals+posts+bolts)
    assert all(r['basis'].startswith('solid CAD PETG') for r in posts)
    assert all(r['basis'].startswith('steel') for r in bolts)


def test_v32_tof_hardware_and_head_budget(geometry):
    if REVISION not in ('v32','v33','v34'):pytest.skip('v32+ ToF mounting only')
    rows={r['name']:r for r in mass_budget(geometry)}
    assert rows['ToF']['mass_kg']==pytest.approx(.0005)
    assert 'manufacturer nominal' in rows['ToF']['basis']
    spacers=[r for n,r in rows.items() if n.startswith('ToFSpacer32_')]
    steel=[r for n,r in rows.items() if n.startswith(('ToFBolt32_','ToFNut32_'))]
    assert len(spacers)==2 and len(steel)==4
    assert all(r['stage']=='Chassis' for r in spacers+steel)
    assert all(r['basis'].startswith('solid CAD PETG') for r in spacers)
    assert all(r['basis'].startswith('steel') for r in steel)
    report=json.loads((OUT/'auxiliary-budget.json').read_text())
    assert {r['name'] for r in spacers+steel} <= set(report['head_pitch_placeholder_centre']['parts'])


def test_inverted_hip_mount_ownership(geometry):
    if REVISION=='v25':pytest.skip('v25 ownership is known wrong, retained as historical evidence')
    for axis in geometry['axes']:
        if axis['stage']!='Hip':continue
        number=int(axis['horn'].replace('Part__Feature',''))
        for i in range(number-6,number+2):
            part=next(p for p in geometry['components'] if p['name']=='Part__Feature%03d'%i)
            assert part['stage']==('Motion_'+axis['code']+'_Hip' if i<number else 'Chassis')


def test_v33_integral_face_and_purchased_microphone_accounting(geometry):
    if REVISION not in ('v33','v34'):pytest.skip('v33+ integral face and microphone mount only')
    rows={r['name']:r for r in mass_budget(geometry)}
    assert 'Muzzle' not in rows
    assert rows['Microphones']['mass_kg']==pytest.approx(.020)
    assert rows['Microphones']['basis'].startswith('bought mass allowance')
    assert rows['HeadFront']['basis'].startswith('solid CAD PETG')
    hardware={n:r for n,r in rows.items() if n.startswith(('MicBolt33_','MicNut33_'))}
    assert len(hardware)==4 and all(r['basis'].startswith('steel') for r in hardware.values())
    report=json.loads((OUT/'auxiliary-budget.json').read_text())
    assert set(hardware)|{'HeadFront','Microphones'} <= set(report['head_pitch_placeholder_centre']['parts'])


def test_v33_microphone_holes_follow_actual_supplier_pose():
    if REVISION not in ('v33','v34'):pytest.skip('v33+ mounting plan only')
    plan=json.loads((OUT.parents[1]/f'skorupa/{REVISION}/assembly-plan.json').read_text())
    mount=plan['microphone_mount']
    source=np.array([[100.44,-105.295,0],[42.73,-76.375,0]])
    rotation=np.array([[0,-1,0],[1,0,0],[0,0,1]])
    expected=source@rotation.T+mount['pcb_base_mm']
    np.testing.assert_allclose(mount['holes_xy_mm'],expected[:,:2],atol=1e-9,rtol=0)
    assert mount['screw_direction'].startswith('Upwards')
    assert mount['screw_length_mm']-mount['clamped_stack_mm']-mount['nut_height_mm']==pytest.approx(mount['protrusion_mm'])


def test_v33_head_mesh_proof_is_current_and_not_a_release():
    if REVISION not in ('v33','v34'):pytest.skip('v33+ inherited head recovery only')
    import hashlib
    cad=OUT.parents[1]/'skorupa/v33'
    report=json.loads((cad/'mesh-proof.json').read_text())
    assert report['master_sha256']==hashlib.sha256((cad/'HeadDesign33.FCStd').read_bytes()).hexdigest()
    assert report['head_manifold'] and report['required_clearance_passed']
    assert not report['mechanical_release']
    old=next(r for r in report['meshes'] if r['name']=='HeadFront')
    assert not old['is_volume'] and old['nonmanifold_edges']>0


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
