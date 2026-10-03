"""Recover matched left-foot/Deck native pair before whole-module R15.

Retain rejected evidence; do not select an incomplete bank or count W5.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save

def main():
    prev=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r33/manifest.json'
    m=json.loads(prev.read_text(encoding='utf-8'));files={r['path']:r['sha256'] for r in m['files']}
    def add(p):
        rel=p.relative_to(ROOT).as_posix();h=sha(p)
        if rel in files:assert files[rel]==h,rel
        files[rel]=h
    add(prev)
    folders=['servo-fuse-bank-fixed-rr-lift-r14','servo-fuse-left-mount-service-r1',
      'servo-fuse-left-mount-service-r2','servo-fuse-left-mount-deck-cut-diagnosis-r1',
      'servo-fuse-left-mount-service-native-r7']
    for folder in folders:
        for p in (ROOT/'hardware/electronics/full-cat'/folder).iterdir():
            if p.suffix in ('.json','.brep'):add(p)
    for p in (ROOT/'hardware/cad/studies/servo-fuse-left-mount-service-native-r7').iterdir():
        if p.suffix in ('.FCStd','.brep','.stl'):add(p)
    for n in ('servo_fuse_left_mount_service_r1.py','servo_fuse_left_mount_service_r2.py',
      'servo_fuse_left_mount_service_native_r1.py','servo_fuse_left_mount_service_native_r2.py',
      'servo_fuse_left_mount_service_native_r3.py','servo_fuse_left_mount_service_native_r4.py',
      'servo_fuse_left_mount_service_native_r5.py','servo_fuse_left_mount_service_native_r6.py','servo_fuse_left_mount_service_native_r7.py',
      'servo_fuse_left_mount_deck_cut_diagnosis_r1.py','servo_fuse_bank_fixed_rr_lift_r15.py',
      'servo_fuse_bank_stock_budget_r11.py','servo_fuse_bank_assembly_r10.py','servo_fuse_bank_select_r6.py',
      'servo_fuse_construction_checkpoint_r36.py'):add(ROOT/'tools/electronics'/n)
    nativepath='hardware/electronics/full-cat/servo-fuse-left-mount-service-native-r7/checks.json'
    native=json.loads((ROOT/nativepath).read_text(encoding='utf-8'))
    assert len(native['exports'])==2 and all(q['single_solid'] and q['closed_STL'] and q['relocated_reopen'] for q in native['exports'])
    for p,h in native['source_sha256'].items():assert sha(ROOT/p)==h,p;add(ROOT/p)
    add(Path(__file__));now=datetime.now(timezone.utc)
    m.update(recorded_utc=now.isoformat(),elapsed_turn_seconds=(now-datetime(2026,10,3,19,17,4,tzinfo=timezone.utc)).total_seconds(),
      status='LEFT_NATIVE_MOUNT_PAIR_COMPLETE_WHOLE_R15_PENDING',local_bank_complete=False,selected=False,
      completed='Same four bank bolts; left foot narrowed and axis moved across retained post with matched Deck hole. Eight washers, unchanged wires/roofs; changed-foot100mm envelope clear. Native pair1solid/BOP0/closedSTL/parameter/reopen.',
      remaining=['Receive sole whole-moduleR15; after six clear poses run stockR11/assemblyR10/selectorR6/checkpointR36/integrity/commit.',
        'R51 remains selected; whole phase1 remains15/20=75%, W5/E3/K3/A2/A3 OPEN.'])
    m['left_service_mount']=dict(source=nativepath,exports=native['exports'],changed_axis_mm=native['changed_axis_mm'],bank_hardware=native['four_mount_hardware'])
    m['deck_cut_diagnosis']=dict(first_full_depth_result='valid/one solid/BOP0; recorded stdout and preserved Deck_drill_8.3.brep',
      short_depth_result='Not received; diagnostic worker stopped because unused short variant is unnecessary.',
      native_r1_failure='Null/uncomputed Deck; bank-first source load conflicts with historical Deck dependencies.',
      resolution='Deck-first source load, same geometry, substrate drill then retained fixture union; only unused historical BankRight link is not required.')
    m['whole_bank_release']=dict(status='R14_REJECTED_LEFT_FOOT_AT5MM_R15_PENDING',source='hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r14/checks.json',continuous_withdrawal_qualified=False)
    for rel,h in files.items():assert sha(ROOT/rel)==h,rel
    m['files']=[dict(path=p,sha256=h) for p,h in sorted(files.items())]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r35';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'manifest.json').exists();save(out/'manifest.json',m)
    print('RECOVERABLE_R35',len(files),flush=True)
if __name__=='__main__':main()
