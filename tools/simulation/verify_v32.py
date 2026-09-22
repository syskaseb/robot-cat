"""Verify v32 local ToF mechanics / optics and CAD physics provenance.

This deliberately retains the inherited head clashes as OPEN, not passed.
"""
import hashlib,json,zipfile
from cad_model import ROOT,OUT,REVISION,actuator_envelope

def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert REVISION=='v32','Set ROBOT_CAT_CAD_REVISION=v32'
    cad=ROOT/'hardware/skorupa/v32';digest=sha(cad/'Kot_v32_NOS_TOF.FCStd');master=sha(cad/'OpticsDesign32.FCStd')
    plan,native,fit,inheritance=[read(cad/n) for n in ['assembly-plan.json','assembly-validation.json','fit-audit.json','inheritance-check.json']]
    assert all(r['source_sha256']==digest for r in [plan,native,fit,inheritance])
    assert all(r['master_sha256']==master for r in [plan,native,fit])
    assert len(plan['components'])==286
    assert (native['fixed'],native['revolute'],native['temporary'])==(272,13,32)
    assert native['solver_result']==0 and native['restored']
    test=native['tests'][0];assert len(test['frames'])==22 and len(test['peak_angles_deg'])==13
    for name,value in test['peak_angles_deg'].items():assert abs(value-(30 if name=='Rev_TailYaw29' else 3))<1e-5
    for frame in test['frames']:
        assert all(frame[k] for k in ['imu_fixed_to_chassis','power_fixed_to_chassis','tof_and_nose_fixed_to_muzzle'])
        assert max(frame[k] for k in ['max_joint_gap_mm','max_fixed_error_rad','max_axis_error_rad'])<1e-5
    assert fit['new_components']==6 and fit['rest_pairs']>0 and not fit['new_rest_interferences']
    assert not fit['full_head_collision_clearance'] and not fit['print_release']
    assert fit['inherited_head_interferences']
    assert all(r['added_material_interference_mm3']<.01 for r in fit['inherited_head_interferences'])
    proof=fit['headfront_subtractive_proof']
    assert len(proof['checks'])==4 and proof['equality_tolerance_mm']==1e-5
    assert all(r['valid'] and not r['solids'] and abs(r['residual_volume_mm3'])<1e-8 for r in proof['checks'])
    assert proof['feature']=='ToFCablePassage32' and proof['depth_mm']==14
    assert len(fit['native_sketches'])==7 and all(r['fully_constrained'] for r in fit['native_sketches'])
    assert all(r['valid'] and r['solids']==1 and r['fits_256_cube'] for r in fit['printable_master_parts'])
    assert len(fit['keepouts'])==2 and all(not r['hits'] for r in fit['keepouts'])
    assert len(fit['contacts'])==2
    for r in fit['contacts']:
        assert min(r[k] for k in ['muzzle_to_PCB_support_mm2','PCB_front_annulus_mm2','PCB_rear_annulus_mm2','rear_spacer_PCB_contact_mm2','nose_to_muzzle_contact_mm2','nose_support_annulus_mm2'])>10
        assert r['shaft_interference_mm3']<1e-6 and abs(r['protrusion_mm']-.9)<1e-9
    assert len(fit['tool_access'])==2 and all(not r['blockers'] for r in fit['tool_access'])
    assert inheritance['verified'] and inheritance['inherited_parts']==276 and inheritance['max_absolute_delta']<1e-9
    assert inheritance['inherited_from_sha256']==sha(ROOT/'hardware/skorupa/v31/Kot_v31_ZASILANIE.FCStd')
    archives={}
    for stem in ['inputs','meshes','telemetry']:
        p=OUT/(stem+'.zip');archives[p.name]=sha(p)
        assert p.with_suffix('.sha256').read_text().split()[0]==archives[p.name]
        with zipfile.ZipFile(p) as z:assert z.testzip() is None
    with zipfile.ZipFile(OUT/'inputs.zip') as z:geometry,model=[json.loads(z.read(n)) for n in ['geometry.json','model.json']]
    assert geometry['source_sha256']==model['source_sha256']==digest
    assert len(geometry['components'])==286 and all(r['valid'] for r in geometry['components'])
    assert len(model['links'])==13 and len(model['joints'])==12
    assert abs(sum(r['mass_kg'] for r in model['links'])-model['total']['mass_kg'])<1e-10
    assert geometry['frozen_native_joints']==['Rev_TailYaw29']
    aux=read(OUT/'auxiliary-budget.json');tail=read(ROOT/'hardware/skorupa/v29/tail-budget.json')
    assert aux['source_sha256']==digest
    assert abs(aux['tail_yaw_actual_cad_axis']['mass_kg']-tail['moving_mass_kg'])<1e-12
    assert abs(aux['tail_yaw_actual_cad_axis']['inertia_about_axis_kg_m2']-tail['yaw_inertia_kg_m2'])<1e-12
    assert {n for n in [p['name'] for p in plan['components']] if n.startswith(('ToFSpacer32_','ToFBolt32_','ToFNut32_'))} <= set(aux['head_pitch_placeholder_centre']['parts'])
    trials=[]
    with zipfile.ZipFile(OUT/'telemetry.zip') as z:
        for n in z.namelist():
            if not n.endswith('-summary.json'):continue
            r=json.loads(z.read(n));assert r['source_sha256']==digest
            assert not r['hard_joint_velocity_limit']
            assert all(j['torque_speed_violations']==0 for j in r.get('joints',{}).values())
            raw=json.loads(z.read(n.replace('-summary.json','.json')))
            assert raw['summary']==r and len(raw['records'])==r['samples'] and r['samples']>0
            fresh=[frame for frame in raw['records'] if frame['motor_fresh']]
            assert fresh,'No trustworthy motor telemetry, including early failed trials'
            # An early fall has no post-settle joint statistics. Check the
            # archived SAME-tick motor data instead of silently passing an
            # empty dictionary. Also covers startup for successful trials.
            for frame in fresh:
                assert len(frame['motor_joints'])==12
                assert all(abs(v[2])<=actuator_envelope(speed=v[1])['moving_limit_nm']+1e-8
                           for v in frame['motor_joints'].values())
            if r['screening_completed']:assert r.get('joints')
            c=r['configuration']
            baseline=abs(c['step_seconds']-1)<1e-9 and abs(c['friction']-.4)<1e-9 and abs(c['torque_cap']-1)<1e-9
            trials.append(dict(file=n,mode=r['mode'],mass_case=c['mass'],baseline=baseline,
                screening_completed=r['screening_completed'],result=r['result'],cycle_seconds=4*c['step_seconds'] if r['mode']=='crawl' else None,
                friction=c['friction'],torque_cap_nm=c['torque_cap'],
                observed_end_seconds=raw['records'][-1]['t'],raw_fresh_samples_checked=len(fresh)))
    assert {(r['mode'],r['mass_case']) for r in trials if r['baseline'] and r['screening_completed']}>={('stand','nominal'),('crawl','nominal'),('crawl','upper')}
    report=dict(provenance_verified=True,mechanical_release=False,continuous_torque_certified=False,full_gait_collision_test=False,
        tail_support_verified=False,head_mount_verified=False,full_head_clearance=False,optical_performance_certified=False,
        inherited_head_interferences=fit['inherited_head_interferences'],geometric_optical_reserve_clear=True,
        source_sha256=digest,master_sha256=master,archives_sha256=archives,components=286,native_revolute=13,native_fixed=272,
        temporary_locks=32,native_frames=22,new_part_rest_interferences=0,inherited_parts_checked=276,
        dynamic_links=13,dynamic_leg_axes=12,head_and_tail_frozen_in_Gazebo=True,trials=trials,scope=__doc__)
    (OUT/'checkpoint-integrity.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
