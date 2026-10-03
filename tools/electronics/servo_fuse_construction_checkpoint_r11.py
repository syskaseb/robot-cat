"""Pin four clear rolled bodies and the actual native cover alteration.

R10 installed99 contacts remain failures. Conservative curved-face BBox
containment is NOT a witness-validity test; the tessellation correction
supersedes the erroneous earlier diagnostic without deleting its evidence.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    parent=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r10/manifest.json'
    m=json.loads(parent.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    files[parent.relative_to(ROOT).as_posix()]=sha(parent)
    rel='hardware/electronics/full-cat/'
    joint=json.loads((ROOT/rel/'servo-fuse-main-joint-layout-r3/checks.json').read_text(encoding='utf-8'))
    cover=json.loads((ROOT/rel/'servo-fuse-main-reliefs-native-r1/checks.json').read_text(encoding='utf-8'))
    correction=json.loads((ROOT/rel/'servo-fuse-witness-tessellation-r1/checks.json').read_text(encoding='utf-8'))
    assert len(joint['holders'])==4 and not joint['hits'] and not joint['errors'] and joint['pairs']==19
    c=next(r for r in cover['parts'] if r['tag']=='Cover')
    assert c['single_solid'] and c['strict_BOP_errors']==0 and c['closed_STL'] and c['relocated_reopen']
    assert c['removed_mm3']>0 and not next(r for r in cover['parts'] if r['tag']=='Bank')['new_geometry']
    for r in (joint,cover):
        for path,h in r['source_sha256'].items():
            assert sha(ROOT/path)==h,path
            if path in files:assert files[path]==h,path
            files[path]=h
    dirs=['servo-fuse-main-space-plan-r2','servo-fuse-main-joint-layout-r1','servo-fuse-main-joint-layout-r2',
          'servo-fuse-main-joint-layout-r3','servo-fuse-contact-witness-sanity-r1','servo-fuse-rr-witness-sources-r1',
          'servo-fuse-witness-tessellation-r1','servo-fuse-main-reliefs-native-r1']
    for folder in [ROOT/rel/q for q in dirs]+[ROOT/'hardware/cad/studies/servo-fuse-main-reliefs-native-r1']:
        for q in folder.iterdir():
            if q.suffix in ('.json','.brep','.FCStd','.stl'):files[q.relative_to(ROOT).as_posix()]=sha(q)
    for name in ['servo_fuse_main_joint_layout_r1','servo_fuse_main_joint_layout_r2','servo_fuse_contact_witness_sanity_r1',
                 'servo_fuse_rr_witness_sources_r1','servo_fuse_witness_tessellation_r1','servo_fuse_main_reliefs_native_r1',
                 'servo_fuse_construction_checkpoint_r11']:
        q=ROOT/f'tools/electronics/{name}.py';files[q.relative_to(ROOT).as_posix()]=sha(q)
    now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),
        completed='One coherent rolled four-MTA body layout R3:19 pairs,0contacts/0errors. Actual native open-bottom RR cover relief: strict BOP, parameter restore, one closed STL, relocated reopen. Bank unchanged. Body-only fit, NOT full mounted/wired selection.',
        remaining=['Native integral cradles/8straps worker, full8actual feeds/joints/insulation grips.',
                   'Shared bank removal with new fixed feeds; one selected export/stock/E3 contribution/commit.'],
        diagnostic_correction='contact-witness-sanity-r1 BBox-containment inference is superseded by witness-tessellation-r1. Conservative curved-face BBoxes do not invalidate99 R8 contacts. Do not reuse wrong validity claim.')
    m['gates']['geometry']=dict(status='open',reason='Four bodies and altered cover clear; full cradles/straps/feed fit and service not yet closed. R8 installed contacts remain rejected.')
    m['service_summary'].update(rolled_four_body_pairs=19,rolled_four_body_contacts=0,new_native_cover_valid=True,
        bank_unchanged=True,bbox_validity_inference_superseded=True)
    for path,h in files.items():assert sha(ROOT/path)==h,path
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/rel/'servo-fuse-construction-checkpoint-r11';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print(json.dumps(dict(files=len(files),phase1_percent=75,selected=False,body_contacts=0,cover_native=True)))


if __name__=='__main__':main()
