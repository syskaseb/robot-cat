"""Bind v35 CAD, bounded prototype evidence and fresh Gazebo screening."""
import hashlib
import json
import zipfile
from cad_model import ROOT,OUT,REVISION,actuator_envelope

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf8'))

def main():
    assert REVISION=='v35'
    cad=ROOT/'hardware/skorupa/v35'
    plan,native,fit,inherit,scope,mesh=[read(cad/n) for n in
        ['assembly-plan.json','assembly-validation.json','fit-audit.json','inheritance-check.json','prototype-scope.json','mesh-proof.json']]
    digest=sha(cad/plan['cad_filename']);master=sha(cad/plan['master_filename'])
    assert all(r['source_sha256']==digest for r in [plan,native,inherit])
    assert all(r['master_sha256']==master for r in [plan,native,fit,inherit,scope,mesh])
    assert plan['prototype_integration_scope_sha256']==sha(cad/'prototype-scope.json')
    assert scope['prototype_integration_allowed'] and not scope['strict_BOP_passed']
    assert not scope['mechanical_release'] and not fit['geometric_checks_passed']
    assert not scope['shell_errors_repaired'] and not scope['identical_error_locations_proven']
    assert all(sha(cad/n)==h for n,h in scope['evidence_sha256'].items())
    assert mesh['required_clearance_passed'] and not fit['rest_interferences']
    assert len(plan['components'])==native['components']==320
    assert (native['fixed'],native['revolute'],native['temporary'])==(306,13,29)
    assert native['restored'] and native['solver_result']==0
    assert not native['head_actuation_tested'] and not native['physical_horn_verified']
    frames=native['tests'][0]['frames'];assert len(frames)==22
    assert all(r['aux_mount_retained'] and max(r[k] for k in ['max_joint_gap_mm','max_fixed_error_rad','max_axis_error_rad'])<1e-5 for r in frames)
    assert inherit['verified'] and inherit['inherited_parts']==302 and len(inherit['master_snapshot_checks'])==18
    assert inherit['max_absolute_delta']<1e-9
    previous=ROOT/'hardware/skorupa/v34';old=read(previous/'assembly-plan.json')
    assert sha(previous/old['cad_filename'])==fit['source_checkpoint_sha256']==inherit['inherited_from_sha256']
    archives={}
    for stem in ['inputs','meshes','telemetry']:
        p=OUT/(stem+'.zip');archives[p.name]=sha(p)
        assert p.with_suffix('.sha256').read_text().split()[0]==archives[p.name]
        with zipfile.ZipFile(p) as z:assert z.testzip() is None
    with zipfile.ZipFile(OUT/'inputs.zip') as z:
        geometry,model=[json.loads(z.read(n)) for n in ['geometry.json','model.json']]
    assert geometry['source_sha256']==model['source_sha256']==digest
    assert len(geometry['components'])==320 and all(r['valid'] for r in geometry['components'])
    assert len(model['links'])==13 and len(model['joints'])==12
    assert abs(sum(r['mass_kg'] for r in model['links'])-model['total']['mass_kg'])<1e-10
    assert geometry['frozen_native_joints']==['Rev_TailYaw29']
    masses={r['name']:r for r in model['components']}
    assert abs(masses['AuxBuck']['mass_kg']-.0048)<1e-12
    assert all(abs(masses['AuxTerminal35_'+str(i)]['mass_kg']-.002)<1e-12 for i in range(2))
    assert all(abs(masses[n]['mass_kg']-.013)<1e-12 for n in ['BearingLower34','BearingUpper34'])
    assert read(OUT/'auxiliary-budget.json')['source_sha256']==digest
    suite=read(OUT/'baseline-suite.json')
    assert suite['source_sha256']==digest and suite['completed_cases']==suite['planned_cases']==3
    trials=[]
    with zipfile.ZipFile(OUT/'telemetry.zip') as z:
        for row in suite['trials']:
            name='trials/'+row['summary'];summary=json.loads(z.read(name))
            raw=json.loads(z.read(name.replace('-summary.json','.json')))
            assert summary['source_sha256']==digest and not summary['hard_joint_velocity_limit']
            assert raw['summary']==summary and len(raw['records'])==summary['samples']>0
            fresh=[r for r in raw['records'] if r['motor_fresh']]
            assert fresh and all(len(r['motor_joints'])==12 for r in fresh)
            assert all(abs(v[2])<=actuator_envelope(speed=v[1])['moving_limit_nm']+1e-8 for r in fresh for v in r['motor_joints'].values())
            assert summary['screening_completed'] and summary.get('joints')
            assert all(j['torque_speed_violations']==0 for j in summary['joints'].values())
            trials.append(dict(file=name,mode=summary['mode'],mass_case=summary['configuration']['mass'],
                screening_completed=summary['screening_completed'],result=summary['result'],fresh_motor_samples=len(fresh)))
    assert {(r['mode'],r['mass_case']) for r in trials}=={('stand','nominal'),('crawl','nominal'),('crawl','upper')}
    report=dict(source_sha256=digest,master_sha256=master,archives_sha256=archives,provenance_verified=True,
        components=320,native_fixed=306,native_revolute=13,temporary_locks=29,native_frames=22,
        inherited_parts_checked=302,changed_rest_interferences=0,head_and_tail_frozen_in_Gazebo=True,
        strict_shell_BOP_passed=False,legacy_shell_repaired=False,thermal_validation=False,
        physical_horn_verified=False,mechanical_release=False,continuous_torque_certified=False,
        trials=trials,scope=__doc__)
    (OUT/'checkpoint-integrity.json').write_text(json.dumps(report,indent=2),encoding='utf8',newline='\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
