"""Receive the four new frames against the retained shared bank withdrawal.

Only changed interfaces: four fixed frames versus the current bank and cover.
Use the already received six lift samples. This is not continuous sweep proof
or permission to withdraw a wired bank without its existing release recipe.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
from servo_fuse_inputs_r1 import sha, save
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'hardware/electronics/full-cat'
OUT=BASE/'w5-common-service-delta-r1'

def main():
    import FreeCAD as A, Part
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);pins=[Path(__file__)]
    def read(p):pins.append(p);return json.loads(p.read_text(encoding='utf-8'))
    fixed_receipt=read(BASE/'w5-loom-fixed-native-r1/checks.json')
    assert fixed_receipt['BOP_errors']==0 and fixed_receipt['closed_STLs']==6
    inherited=read(BASE/'servo-fuse-bank-fixed-rr-lift-r22/checks.json')
    assert not inherited['hits'] and not inherited['errors']
    lifts=inherited['sampled_lifts_mm'];assert lifts==[2,5,10,30,60,100]
    def load(p):
        pins.append(p);s=Part.read(str(p));assert s.isValid() and len(s.Solids)==1,p
        return s
    frames={leg:load(ROOT/'hardware/cad/studies/w5-loom-fixed-native-r1'/(leg+'FixedFrame_CANDIDATE_WORLD.brep')) for leg in ('FL','FR','RL','RR')}
    # Right retained unchanged; new left/cover are received subtractive
    # variants, not arbitrary earlier revisions picked for an easier result.
    bank_left_receipt=read(BASE/'w5-source-bank-passage-native-r1/checks.json')
    left_files=[ROOT/p for p in bank_left_receipt['files'] if p.endswith('.brep') and 'BankLeft' in p]
    assert len(left_files)==1,left_files
    cover_receipt=read(BASE/'w5-side-retention-native-r1/checks.json')
    module=dict(BankRight=load(ROOT/'hardware/cad/studies/servo-fuse-bank-inner-feed-service-r1/BankRight_WORLD.brep'),
        BankLeft=load(left_files[0]),Cover=load(ROOT/'hardware/cad/studies/w5-side-retention-native-r1/SourceCover_CANDIDATE_WORLD.brep'))
    for receipt in (fixed_receipt,bank_left_receipt,cover_receipt):
        for rel,h in receipt.get('files',{}).items():assert sha(ROOT/rel)==h,rel
    hits=[];errors=[];pairs=0
    for lift in [0,*lifts]:
        for name,s in module.items():
            moved=s.copy();moved.translate(A.Vector(0,0,lift))
            for frame,t in frames.items():
                if not moved.BoundBox.intersect(t.BoundBox):continue
                pairs+=1
                try:
                    witness=moved.common(t)
                    if witness.Volume>1e-5:
                        p=OUT/('HIT_'+str(len(hits)+1)+'.brep');witness.exportBrep(str(p))
                        hits.append(dict(lift_mm=lift,moving=name,fixed_frame=frame,mm3=witness.Volume,
                            witness=p.relative_to(ROOT).as_posix()))
                except Exception as e:errors.append(dict(lift_mm=lift,moving=name,fixed_frame=frame,error=str(e)))
        save(OUT/'progress.json',dict(lift_mm=lift,pairs=pairs,hits=len(hits),errors=len(errors),updated_utc=datetime.now(timezone.utc).isoformat()))
        print('COMMON_SERVICE_FRAMES',lift,len(hits),len(errors),flush=True)
    finish=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='NEW_FIXED_FRAMES_BANK_LIFT_SAMPLES_CONFLICT' if hits or errors else 'NEW_FIXED_FRAMES_BANK_LIFT_SAMPLES_CLEAR',
        new_frame_count=4,current_bank_parts=list(module),sampled_lifts_mm=[0,*lifts],hits=hits,errors=errors,pairs=pairs,
        reused_old_bank_sequence=inherited['sequence'],new_frames_remain_fixed_to_Deck=True,
        remaining_service_interfaces=['Current source/central insulation restraints and crossing wires.','Current Deck/hood changes and released-bank-end parking.'],
        continuous_sweep_verified=False,complete_shared_service=False,selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in OUT.glob('HIT_*.brep')},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))

if __name__=='__main__':main()
