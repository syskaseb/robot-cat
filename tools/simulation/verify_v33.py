"""Verify v33 evidence without promoting a development checkpoint to release."""
import hashlib,json,zipfile
from cad_model import ROOT,OUT,REVISION,actuator_envelope
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    assert REVISION=='v33','Set ROBOT_CAT_CAD_REVISION=v33'
    cad=ROOT/'hardware/skorupa/v33';plan=read(cad/'assembly-plan.json')
    digest=sha(cad/plan['cad_filename']);master=sha(cad/plan['master_filename'])
    native,fit,inheritance=[read(cad/n) for n in ['assembly-validation.json','fit-audit.json','inheritance-check.json']]
    assert all(r['source_sha256']==digest for r in [plan,native,fit,inheritance])
    assert all(r['master_sha256']==master for r in [plan,native,fit])
    assert len(plan['components'])==289 and 'Muzzle' not in {r['name'] for r in plan['components']}
    assert (native['fixed'],native['revolute'],native['temporary'])==(275,13,30)
    assert not native['head_actuation_tested'] and native['solver_result']==0 and native['restored']
    test=native['tests'][0];assert len(test['frames'])==22 and len(test['peak_angles_deg'])==13
    for name,value in test['peak_angles_deg'].items():assert abs(value-(30 if name=='Rev_TailYaw29' else 3))<1e-5
    for frame in test['frames']:
        assert frame['microphone_and_optics_fixed_to_front_head'] and frame['imu_and_main_regulator_fixed']
        assert max(frame[k] for k in ['max_joint_gap_mm','max_fixed_error_rad','max_axis_error_rad'])<1e-5
    assert not fit['print_release'] and fit['new_components']==4
    assert not fit['new_interferences'] and not fit['added_support_interferences']
    assert len(fit['pcb_head_clearance_bound']['sources'])==4 and fit['pcb_head_clearance_bound']['total_upper_bound_mm3']<.01
    assert fit['inherited_head_interferences'], 'Inherited unresolved interfaces must remain explicit'
    assert len(fit['native_sketches'])==3 and all(r['fully_constrained'] for r in fit['native_sketches'])
    assert len(fit['identity_checks'])==3
    for r in fit['identity_checks']:
        if r.get('serialization_equivalent',False):
            assert r['absolute_tolerance_mm']==1e-9 and r['relative_tolerance']==1e-12 and r['max_absolute_delta']<1e-9
        else:assert r['valid'] and abs(r['residual_volume_mm3'])<1e-8
    assert len(fit['support_contacts'])==2 and all(r['embedded_in_recovered_shell_mm3']>20 for r in fit['support_contacts'])
    for r in fit['pcb_contacts']:
        assert min(r['support_top_area_mm2'],r['pcb_bottom_area_mm2'])>8
        assert r['shaft_interference_mm3']<.01 and abs(r['protrusion_mm']-1.29)<1e-9
    assert len(fit['nose_access'])==len(fit['optical_reserves'])==2
    assert all(r['head_obstruction_mm3']<.01 for r in fit['nose_access']+fit['optical_reserves'])
    assert len(fit['tool_access'])==4 and not fit['assembly_service_validated']
    assert all(not r['before_ear_installation_blockers'] for r in fit['tool_access'])
    assert {n for r in fit['tool_access'] for n in r['required_absent_parts']}=={'EarL'}
    mesh=read(cad/'mesh-proof.json')
    assert sha(cad/'mesh-proof.json')==fit['mesh_proof_sha256']
    assert mesh['master_sha256']==master and mesh['head_manifold'] and mesh['required_clearance_passed']
    assert not mesh['mechanical_release']
    assert plan['microphone_mount']['holes_xy_mm'][1][0]<-162
    assert plan['microphone_mount']['screw_direction'].startswith('Upwards')
    assert fit['printable_face']['solids']==1 and fit['printable_face']['valid'] and fit['printable_face']['fits_256_cube']
    assert inheritance['verified'] and inheritance['inherited_parts']==283 and inheritance['max_absolute_delta']<1e-9
    assert inheritance['inherited_from_sha256']==sha(ROOT/'hardware/skorupa/v32/Kot_v32_NOS_TOF.FCStd')
    archives={}
    for stem in ['inputs','meshes','telemetry']:
        p=OUT/(stem+'.zip');archives[p.name]=sha(p)
        assert p.with_suffix('.sha256').read_text().split()[0]==archives[p.name]
        with zipfile.ZipFile(p) as z:assert z.testzip() is None
    with zipfile.ZipFile(OUT/'inputs.zip') as z:geometry,model=[json.loads(z.read(n)) for n in ['geometry.json','model.json']]
    assert geometry['source_sha256']==model['source_sha256']==digest
    assert len(geometry['components'])==289 and all(r['valid'] for r in geometry['components'])
    assert len(model['links'])==13 and len(model['joints'])==12
    assert abs(sum(r['mass_kg'] for r in model['links'])-model['total']['mass_kg'])<1e-10
    assert geometry['frozen_native_joints']==['Rev_TailYaw29']
    aux=read(OUT/'auxiliary-budget.json');assert aux['source_sha256']==digest
    assert {'MicBolt33_0','MicBolt33_1','MicNut33_0','MicNut33_1','Microphones','HeadFront'} <= set(aux['head_pitch_placeholder_centre']['parts'])
    assert 'Muzzle' not in aux['head_pitch_placeholder_centre']['parts']
    trials=[]
    with zipfile.ZipFile(OUT/'telemetry.zip') as z:
        for n in z.namelist():
            if not n.endswith('-summary.json'):continue
            r=json.loads(z.read(n));assert r['source_sha256']==digest and not r['hard_joint_velocity_limit']
            raw=json.loads(z.read(n.replace('-summary.json','.json')))
            assert raw['summary']==r and len(raw['records'])==r['samples'] and r['samples']>0
            fresh=[frame for frame in raw['records'] if frame['motor_fresh']];assert fresh
            for frame in fresh:
                assert len(frame['motor_joints'])==12
                assert all(abs(v[2])<=actuator_envelope(speed=v[1])['moving_limit_nm']+1e-8 for v in frame['motor_joints'].values())
            assert all(j['torque_speed_violations']==0 for j in r.get('joints',{}).values())
            if r['screening_completed']:assert r.get('joints')
            c=r['configuration']
            trials.append(dict(file=n,mode=r['mode'],mass_case=c['mass'],screening_completed=r['screening_completed'],result=r['result'],fresh_motor_samples=len(fresh)))
    assert {(r['mode'],r['mass_case']) for r in trials if r['screening_completed']}>={('stand','nominal'),('crawl','nominal'),('crawl','upper')}
    report=dict(source_sha256=digest,master_sha256=master,archives_sha256=archives,provenance_verified=True,
        mechanical_release=False,continuous_torque_certified=False,head_actuation_verified=False,tail_support_verified=False,
        components=289,native_fixed=275,native_revolute=13,temporary_locks=30,native_frames=22,
        inherited_parts_checked=283,new_part_rest_interferences=0,inherited_head_interferences=fit['inherited_head_interferences'],
        dynamic_links=13,dynamic_leg_axes=12,head_and_tail_frozen_in_Gazebo=True,trials=trials,
        microphone_reference_only=True,acoustics_and_cables_verified=False,scope=__doc__)
    report.update(head_mesh_manifold=True,assembly_service_validated=False,
        required_absent_parts_for_microphone_assembly=['EarL'],head_bop_check_messages=fit['bop_check_messages'])
    (OUT/'checkpoint-integrity.json').write_text(json.dumps(report,indent=2),encoding='utf8',newline='\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
