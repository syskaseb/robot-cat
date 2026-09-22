"""Reproducible CAD mass budget and articulated Gazebo model.

No ROS/FreeCAD dependency. CAD axes are not replaced by the generic cat IK.
Masses are estimates with an explicit provenance, not scale measurements.
"""
from pathlib import Path
import json
import math
import os
import xml.etree.ElementTree as ET
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
REVISION = os.environ.get('ROBOT_CAT_CAD_REVISION','v28')
assert REVISION in ('v25','v27','v28'), REVISION
OUT = ROOT / 'hardware/simulation' / REVISION
WORLD = 'cad_'+REVISION
R = np.diag([-1., -1., 1.])  # proper rotation: CAD head -X -> REP103 +X
ORIGIN_MM = np.array([21., 0., 18.51])
STAGES = ('Hip', 'Knee', 'Ankle')
KGFCM_TO_NM = 0.0980665
SERVO_SOURCE = 'https://www.waveshare.com/st3215-servo.htm?sku=22414'
# Explicit engineering assumptions pending scales and final electronics.
BOUGHT_G = dict(Battery=174, Pi=46, PiHatCooling=65, Pololu=12, AuxBuck=12,
                BusAdapter=15, PowerDistribution=35, IMU=4, Touch=3, AudioAmp=4,
                Speaker=65, NeckYawServo=13.8, HeadPitchServo=13.8,
                TailYawServo=13.8, TailLiftServo=13.8, Camera=6, ToF=2,
                Microphones=20, PWMControllerUnplaced=15, IrIlluminator=10,
                ChargeSocketXT60=8, MainSwitch=8, BalancerPort=3,
                BatteryLiner23=2, BatteryStrap123=3, BatteryStrap223=3)
SERVO_PREFIXES = ('ZK_', 'SG-ZIJI_', 'XG-ZIJI_', 'MOTOR-', 'PCB-CHAZUO_', 'GE_')


def xyz(mm):
    return R @ (np.asarray(mm) - ORIGIN_MM) * .001


def stage_name(stage):
    return 'base_link' if stage == 'Chassis' else stage.lower()


def combine(parts):
    mass = sum(p['mass_kg'] for p in parts)
    com = sum(p['mass_kg']*np.array(p['com_m']) for p in parts)/mass
    inertia = np.zeros((3,3))
    for p in parts:
        d = np.array(p['com_m'])-com
        inertia += np.array(p['inertia_kg_m2']) + p['mass_kg']*(d@d*np.eye(3)-np.outer(d,d))
    assert np.linalg.eigvalsh(inertia).min() > 0
    assert max(np.linalg.eigvalsh(inertia)) <= np.trace(inertia)/2 + 1e-10
    return dict(mass_kg=mass, com_m=com.tolist(), inertia_kg_m2=inertia.tolist())


def mass_budget(geometry, petg_density=1.27, servo_g=69., bought_factor=1., reserve_g=120.):
    rows = []
    servo_parts = [p for p in geometry['components'] if p['label'].startswith(SERVO_PREFIXES)]
    assert len(servo_parts) == 72, '12 servo bodies, six components each'
    # Allocate each complete servo's estimated mass across its CAD subparts.
    # Equal density within each servo is an inertia approximation, not material data.
    assert all(servo_parts[i]['label'].startswith('ZK_') for i in range(0,72,6))
    servo_vol = {p['name']:sum(q['volume_mm3'] for q in servo_parts[i:i+6])
                 for i in range(0,72,6) for p in servo_parts[i:i+6]}
    for p in geometry['components']:
        n, label, vol = p['name'], p['label'], p['volume_mm3']
        if n in servo_vol:
            mass = servo_g*.001*vol/servo_vol[n]
            basis = 'ST3215 body: 69 g assumption; 60..89 g sensitivity; horns counted separately'
        elif n in BOUGHT_G:
            mass = BOUGHT_G[n]*.001*bought_factor
            basis = 'bought mass allowance, not CAD envelope density; verify by weighing'
            if n == 'Battery':
                basis += '; candidate GEA223S30X6GT manufacturer nominal 174 g, geometry still old'
        elif 'Screw' in n or ('Nut' in n and not n.startswith('NutShoe')):
            mass, basis = vol*7.85e-6, 'steel fastener envelope, density assumption 7.85 g/cm3'
        elif label.startswith('HornDisc'):
            mass, basis = vol*2.70e-6, 'aluminium horn density assumption 2.70 g/cm3'
        else:
            mass, basis = vol*petg_density*1e-6, 'solid CAD PETG volume; 1.27 g/cm3 assumption; not infill percentage'
        I = R @ np.array(p['inertia_volume_mm5'])*(mass/vol)*1e-6 @ R.T
        rows.append(dict(name=n, stage=p['stage'], mass_kg=mass, com_m=xyz(p['com_mm']).tolist(),
                         inertia_kg_m2=I.tolist(), basis=basis))
    # Wiring, missing little fasteners and brackets: explicit chassis allowance.
    rows.append(dict(name='UnmodelledHarnessAndMounts', stage='Chassis', mass_kg=reserve_g*.001,
                     com_m=[0,0,.03], inertia_kg_m2=(np.diag([.10**2+.07**2,.20**2+.07**2,.20**2+.10**2])*reserve_g*.001/12).tolist(),
                     basis='120 g design allowance; COM/inertia box assumption, no visual CAD part'))
    return rows


def make_model(geometry,**mass_options):
    rows = mass_budget(geometry,**mass_options)
    poses = {'Chassis':np.zeros(3)}
    axes = []
    for a in geometry['axes']:
        key = 'Motion_'+a['code']+'_'+a['stage']
        poses[key] = xyz(a['pivot_mm'])
        i = STAGES.index(a['stage'])
        parent = 'Chassis' if i == 0 else 'Motion_'+a['code']+'_'+STAGES[i-1]
        axis = R @ np.asarray(a['axis']); axis /= np.linalg.norm(axis)
        axes.append(dict(name=key.lower()+'_joint', stage=key, parent=parent,
                         origin_m=poses[key].tolist(), axis=axis.tolist(),
                         cad_code=a['code'], cad_stage=a['stage']))
    links = []
    for key, origin in poses.items():
        group = [p for p in rows if p['stage']==key]
        inertia = combine(group)
        inertia['com_m'] = (np.array(inertia['com_m'])-origin).tolist()
        links.append(dict(name=stage_name(key), stage=key, origin_m=origin.tolist(), **inertia))
    return dict(source_sha256=geometry['source_sha256'], components=rows, links=links, joints=axes,
                total=combine(rows), warnings=[
                    REVISION+' snapshot: head/tail fixed, 4 auxiliary placeholders, 64 temporary locks.',
                    'Bought masses and PETG density are assumptions; weigh actual build and slicer results.',
                    'No measured continuous ST3215 torque; stall is not a safe continuous rating.',
                    '10.5 V linear torque/speed scaling is an estimate for the 12 V winding, NOT the 7.4 V variant.',
                    'Foot friction, collisions and joint ranges are provisional; not print release.'])


def actuator_envelope(voltage=10.5, speed=0.):
    stall = 30 * KGFCM_TO_NM * min(voltage,12.)/12.
    no_load = math.pi/3/.222 * min(voltage,12.)/12.
    # Preliminary brushed-DC torque-speed line, not a measured gearbox curve.
    return dict(stall_nm=stall, no_load_rad_s=no_load,
                moving_limit_nm=stall*max(0.,1-abs(speed)/no_load),
                screening_25pct_nm=stall*.25)


def pd_damping(model,joint,kp=30.):
    """0.7 critical damping estimated from downstream inertia, not servo ID.

    A single 0.5 Nms/rad gain destabilises the tiny distal link at 1 ms.
    This gain avoids that numerical artefact; actual servo gains remain unknown.
    """
    inertia=np.zeros((3,3));i=STAGES.index(joint['cad_stage'])
    stages=['Motion_'+joint['cad_code']+'_'+s for s in STAGES[i:]]
    for p in model['components']:
        if p['stage'] not in stages:continue
        d=np.array(p['com_m'])-joint['origin_m']
        inertia+=np.array(p['inertia_kg_m2'])+p['mass_kg']*(d@d*np.eye(3)-np.outer(d,d))
    a=np.array(joint['axis']);equivalent=float(a@inertia@a)
    return .7*2*math.sqrt(kp*equivalent)


def reactions(points, mass, com):
    A = np.vstack([np.ones(len(points)),np.asarray(points)[:,:2].T])
    b = mass*9.80665*np.array([1,com[0],com[1]])
    f = np.linalg.lstsq(A,b,rcond=None)[0]
    return f, bool(f.min()>=-1e-8 and np.linalg.norm(A@f-b)<1e-7)


def static_report(model, feet):
    codes = list(feet)
    points = np.array([feet[c] for c in codes])
    f, stable = reactions(points,model['total']['mass_kg'],model['total']['com_m'])
    torques = []
    for j in model['joints']:
        code = j['cad_code']; i = STAGES.index(j['cad_stage'])
        downstream = ['Motion_'+code+'_'+s for s in STAGES[i:]]
        pivot, axis = np.array(j['origin_m']),np.array(j['axis'])
        moment = np.cross(np.array(feet[code])-pivot,[0,0,f[codes.index(code)]])
        for p in model['components']:
            if p['stage'] in downstream:
                moment += np.cross(np.array(p['com_m'])-pivot,[0,0,-p['mass_kg']*9.80665])
        torques.append(dict(joint=j['name'],torque_nm=float(-axis@moment)))
    tripods = {}
    for code in codes:
        idx=[i for i,c in enumerate(codes) if c!=code]
        forces,ok=reactions(points[idx],model['total']['mass_kg'],model['total']['com_m'])
        tripods[code]=dict(static_feasible_without_body_shift=ok, normal_forces_N=forces.tolist())
    return dict(four_foot_equilibrium=stable,normal_forces_N=dict(zip(codes,f.tolist())),
                joint_torques=torques,tripods=tripods, actuator=actuator_envelope(),
                scope='Quasi-static, flat plane, vertical point reactions; no acceleration/impact/thermal model.')


def text(parent,tag,value):
    e=ET.SubElement(parent,tag);e.text=str(value);return e


def vec(v):
    return ' '.join(f'{x:.10g}' for x in v)


def write_sdf(model, feet, effort=1.0,friction=.4,path=None):
    """Standalone effort-limited screening model; does not alter legacy ROS cat."""
    path=OUT/'cat.sdf' if path is None else Path(path)
    import os
    mesh_root=Path(os.path.relpath(OUT/'meshes',path.parent)).as_posix()
    sdf=ET.Element('sdf',version='1.9');world=ET.SubElement(sdf,'world',name=WORLD)
    physics=ET.SubElement(world,'physics',name='1ms',type='ignored')
    text(physics,'max_step_size',.001);text(physics,'real_time_factor',1)
    for filename,name in [('physics','Physics'),('user-commands','UserCommands'),('scene-broadcaster','SceneBroadcaster')]:
        ET.SubElement(world,'plugin',filename='gz-sim-'+filename+'-system',name='gz::sim::systems::'+name)
    text(world,'gravity','0 0 -9.80665')
    ground=ET.SubElement(world,'model',name='ground');text(ground,'static','true')
    gl=ET.SubElement(ground,'link',name='ground')
    for kind in ['collision','visual']:
        g=ET.SubElement(ET.SubElement(gl,kind,name='plane_'+kind),'geometry')
        plane=ET.SubElement(g,'plane');text(plane,'normal','0 0 1');text(plane,'size','20 20')
    light=ET.SubElement(world,'light',name='sun',type='directional')
    text(light,'pose','0 0 10 0 0 0');text(light,'diffuse','0.8 0.8 0.8 1');text(light,'direction','-0.3 0.2 -1')
    cat=ET.SubElement(world,'model',name='robot_cat_cad')
    # Drop 2 mm, not 20 cm; CAD rest pose already includes bent legs.
    text(cat,'pose',f'0 0 {-min(p[2] for p in feet.values())+.002:.9f} 0 0 0')
    text(cat,'self_collide','false')
    for link in model['links']:
        l=ET.SubElement(cat,'link',name=link['name']);text(l,'pose',vec(link['origin_m'])+' 0 0 0')
        inertial=ET.SubElement(l,'inertial');text(inertial,'mass',link['mass_kg'])
        text(inertial,'pose',vec(link['com_m'])+' 0 0 0')
        inertia=ET.SubElement(inertial,'inertia');I=link['inertia_kg_m2']
        for name,i,j in [('ixx',0,0),('iyy',1,1),('izz',2,2),('ixy',0,1),('ixz',0,2),('iyz',1,2)]:text(inertia,name,I[i][j])
        visual=ET.SubElement(l,'visual',name='cad_mesh')
        mesh=ET.SubElement(ET.SubElement(visual,'geometry'),'mesh')
        text(mesh,'uri',mesh_root+'/'+link['name']+'.stl')
        material=ET.SubElement(visual,'material');text(material,'diffuse','0.08 0.085 0.095 1');text(material,'ambient','0.1 0.1 0.1 1')
        if link['stage'].endswith('Ankle'):
            code=link['stage'].split('_')[1];foot=np.array(feet[code])-np.array(link['origin_m'])
            foot[2]+=.006
            col=ET.SubElement(l,'collision',name='provisional_petg_foot')
            text(col,'pose',vec(foot)+' 0 0 0')
            text(ET.SubElement(ET.SubElement(col,'geometry'),'sphere'),'radius',.006)
            ode=ET.SubElement(ET.SubElement(ET.SubElement(col,'surface'),'friction'),'ode')
            text(ode,'mu',friction);text(ode,'mu2',friction)
        if link['name']=='base_link':
            col=ET.SubElement(l,'collision',name='fall_stop_proxy')
            text(col,'pose','0 0 .025 0 0 0')
            text(ET.SubElement(ET.SubElement(col,'geometry'),'box'),'size','0.25 0.09 0.08')
    for j in model['joints']:
        joint=ET.SubElement(cat,'joint',name=j['name'],type='revolute')
        text(joint,'parent',stage_name(j['parent']));text(joint,'child',stage_name(j['stage']))
        axis=ET.SubElement(joint,'axis');text(axis,'xyz',vec(j['axis']))
        limit=ET.SubElement(axis,'limit')
        # No hard velocity constraint: no-load speed is NOT an absolute
        # mechanical speed limit. A physics clamp would supply unlogged braking
        # impulse during impact and bias the inferred motor effort downwards.
        for key,val in [('lower',-.5),('upper',.5),('effort',effort)]:text(limit,key,val)
        dynamics=ET.SubElement(axis,'dynamics');text(dynamics,'damping',.015)
    motor=ET.SubElement(cat,'plugin',filename='robot_cat_cad_actuator',name='robot_cat::Actuator')
    for j in model['joints']:text(motor,'joint_name',j['name'])
    for j in model['joints']:text(motor,j['name']+'_d_gain',pd_damping(model,j))
    for key,val in [('effort_cap',effort),('stall_torque',actuator_envelope()['stall_nm']),
                    ('no_load_speed',actuator_envelope()['no_load_rad_s']),('p_gain',30),('d_gain',.5)]:text(motor,key,val)
    publisher=ET.SubElement(cat,'plugin',filename='gz-sim-joint-state-publisher-system',name='gz::sim::systems::JointStatePublisher')
    text(publisher,'update_rate',100)
    ET.indent(sdf)
    ET.ElementTree(sdf).write(path,encoding='utf-8',xml_declaration=True)


def main():
    geometry=json.loads((OUT/'geometry.json').read_text(encoding='utf8'))
    model=make_model(geometry)
    model['mass_scenarios_kg']={
        'lower':combine(mass_budget(geometry,1.20,60,.85,80))['mass_kg'],
        'nominal':model['total']['mass_kg'],
        'upper':combine(mass_budget(geometry,1.30,89,1.25,180))['mass_kg']}
    (OUT/'model.json').write_text(json.dumps(model,indent=2,ensure_ascii=False),encoding='utf8')
    feetfile=OUT/'feet.json'
    if feetfile.exists():
        feet=json.loads(feetfile.read_text())
        report=static_report(model,feet)
        (OUT/'static.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        write_sdf(model,feet)
        print(json.dumps(report,indent=2))
    print('Mass scenarios kg:',model['mass_scenarios_kg'])
    print('COM m:',model['total']['com_m'])


if __name__=='__main__':main()
