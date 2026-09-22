"""Verify saved CAD / native / fit / dynamics provenance, not print approval."""
import hashlib,json,zipfile
from pathlib import Path
from cad_model import ROOT,OUT,REVISION

def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert REVISION=='v29','Set ROBOT_CAT_CAD_REVISION=v29'
    cad=ROOT/'hardware/skorupa/v29';target=cad/'Kot_v29_OGON_PROTOTYP.FCStd'
    digest=sha(target);master=sha(cad/'TailDesign29.FCStd')
    plan=read(cad/'assembly-plan.json');native=read(cad/'assembly-validation.json')
    fit=read(cad/'fit-audit.json');tail=read(cad/'tail-budget.json')
    assert all(r['source_sha256']==digest for r in [plan,native,fit,tail])
    assert all(r['master_sha256']==master for r in [plan,native,fit])
    assert len(plan['components'])==252 and (native['fixed'],native['revolute'],native['temporary'])==(238,13,36)
    assert native['solver_result']==0 and native['restored']
    test=native['tests'][0];assert len(test['frames'])==22
    assert len(test['peak_angles_deg'])==13
    for name,value in test['peak_angles_deg'].items():
        assert abs(value-(30 if name=='Rev_TailYaw29' else 3))<1e-5
    for r in test['frames']:
        assert max(r[k] for k in ['max_joint_gap_mm','max_fixed_error_rad','max_axis_error_rad'])<1e-5
    assert fit['new_components']==43 and not fit['rest_interferences']
    assert len(fit['yaw_samples'])==13 and all(not r['interferences'] for r in fit['yaw_samples'])
    assert len(fit['native_sketches'])==56 and all(r['fully_constrained'] for r in fit['native_sketches'])
    assert all(r['valid'] and r['solids']==1 and r['fits_256_cube'] for r in fit['printable_master_parts'])
    assert all(max(r['interference_frame_mm3'],r['interference_cover_mm3'])<1e-5 for r in fit['frame_hole_checks'])
    archives={}
    for stem in ['inputs','meshes','telemetry']:
        p=OUT/(stem+'.zip');digest_archive=sha(p)
        assert p.with_suffix('.sha256').read_text().split()[0]==digest_archive
        with zipfile.ZipFile(p) as z:assert z.testzip() is None
        archives[p.name]=digest_archive
    with zipfile.ZipFile(OUT/'inputs.zip') as z:
        geometry=json.loads(z.read('geometry.json'));model=json.loads(z.read('model.json'))
    assert geometry['source_sha256']==model['source_sha256']==digest
    assert len(geometry['components'])==252 and all(r['valid'] for r in geometry['components'])
    assert len(model['links'])==13 and len(model['joints'])==12
    assert abs(sum(r['mass_kg'] for r in model['links'])-model['total']['mass_kg'])<1e-10
    assert geometry['frozen_native_joints']==['Rev_TailYaw29']
    aux=read(OUT/'auxiliary-budget.json')['tail_yaw_actual_cad_axis']
    assert abs(aux['mass_kg']-tail['moving_mass_kg'])<1e-12
    assert abs(aux['inertia_about_axis_kg_m2']-tail['yaw_inertia_kg_m2'])<1e-12
    trials=[]
    with zipfile.ZipFile(OUT/'telemetry.zip') as z:
        for n in z.namelist():
            if not n.endswith('-summary.json'):continue
            r=json.loads(z.read(n))
            assert r['source_sha256']==digest and r['screening_completed']
            assert not r['hard_joint_velocity_limit']
            assert all(j['torque_speed_violations']==0 for j in r['joints'].values())
            trials.append(dict(file=n,mode=r['mode'],mass_case=r['configuration']['mass']))
    assert {(r['mode'],r['mass_case']) for r in trials}>={('stand','nominal'),('crawl','nominal'),('crawl','upper')}
    report=dict(provenance_verified=True,mechanical_release=False,continuous_torque_certified=False,
                full_gait_collision_test=False,tail_support_verified=False,
                source_sha256=digest,master_sha256=master,archives_sha256=archives,
                components=252,native_revolute=13,native_fixed=238,temporary_locks=36,
                native_frames=22,new_part_rest_interferences=0,sampled_tail_interferences=0,
                dynamic_links=13,dynamic_leg_axes=12,tail_frozen_in_Gazebo=True,trials=trials,
                scope=__doc__)
    (OUT/'checkpoint-integrity.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
