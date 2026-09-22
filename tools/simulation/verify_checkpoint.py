"""Verify v28 checkpoint provenance, not mechanical or thermal approval."""
import hashlib,json,zipfile
from cad_model import ROOT,OUT


def read(path):return json.loads(path.read_text(encoding='utf8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert OUT.name=='v28'
    cad=ROOT/'hardware/skorupa/v28/Kot_v28_BIODRA_PETG.FCStd'
    digest=sha(cad);native=read(cad.parent/'assembly-validation.json')
    assert native['source_sha256']==digest and native['solver_result']==0
    assert len(native['native_frames'])==22 and native['temporary_locks']==64
    assert all(r['max_gap_mm']<1e-5 and max(r['case_overlaps_mm3'].values())<1e-5 for r in native['native_frames'])
    archives={}
    for stem in ['inputs','meshes','telemetry']:
        path=OUT/(stem+'.zip');actual=sha(path)
        assert path.with_suffix('.sha256').read_text().split()[0]==actual
        with zipfile.ZipFile(path) as z:assert z.testzip() is None
        archives[stem+'.zip']=actual
    with zipfile.ZipFile(OUT/'inputs.zip') as z:
        geometry=json.loads(z.read('geometry.json'));model=json.loads(z.read('model.json'))
    assert geometry['source_sha256']==model['source_sha256']==digest
    assert len(geometry['components'])==238 and all(p['valid'] for p in geometry['components'])
    assert len(model['links'])==13 and len(model['joints'])==12
    clearance=read(OUT/'cover-clearance-regression.json')
    assert clearance['source_sha256']==digest and len(clearance['poses'])==6
    assert all(not p['hits'] for p in clearance['poses'])
    current=[]
    for path in (OUT/'trials').glob('*-summary.json'):
        trial=read(path)
        if trial.get('hard_joint_velocity_limit',True):continue
        assert trial['source_sha256']==digest and trial['screening_completed']
        assert all(j['torque_speed_violations']==0 for j in trial['joints'].values())
        current.append(path.name)
    assert len(current)==3
    report=dict(provenance_verified=True,mechanical_release=False,
                continuous_torque_certified=False,full_gait_collision_test=False,
                source_sha256=digest,archives_sha256=archives,
                current_no_hard_velocity_limit_trials=sorted(current),
                native_frames=22,geometry_components=238,dynamic_links=13,leg_joints=12,
                temporary_locks=64,scope=__doc__)
    (OUT/'checkpoint-integrity.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
