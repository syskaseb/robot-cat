"""One nominal local assembly/removal order for fixed Deck cages/channel.

Require actual shared six-pose result. Lever motion on the crowded fitted
Deck is not assumed: prewire purchased WAGO blocks on the bench and remove
their straps before later opening. Prototype physical checks are phase2.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
def main():
    t=datetime.now(timezone.utc);pins={}
    def read(rel):p=ROOT/rel;pins[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    lift=read('hardware/electronics/full-cat/servo-fuse-bank-fixed-rr-lift-r11/checks.json')
    stock=read('hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r7/stock.json')
    mapping=read('hardware/electronics/full-cat/servo-fuse-wago-map-r1/interface.json')
    ends=read('hardware/electronics/full-cat/servo-fuse-bank-electrical-r2/interface.json')
    guard=read('hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-native-r1/checks.json')
    clips=read('hardware/electronics/full-cat/servo-fuse-rr-clip-approach-r2/checks.json')
    assert not lift['hits'] and not lift['errors'] and lift['completed_clear_lifts_mm']==[2,5,10,30,60,100]
    assert lift['FR_guard_owner']=='FIXED_DECK_WITH_2SCREWS_2NUTS' and len(ends['ends'])==24
    assert (mapping['all_ports'],mapping['connected_ports'],mapping['unused_ports'])==(20,16,4)
    assert not clips['hits'] and not clips['errors']
    stages=[
      ('bench','Battery absent. Label20project ports and24TE ends. Cut the12input blanks and7HELU extensions once from current electrical/materials receipts. FourP-WAGO port5 remain empty. Crimp the exact TE terminal/one lead with pinned die and strip; do not tin WAGO conductors.'),
      ('fixed_guard','On bare removed Deck mount the fixed side channel/output cage using the two horizontal M3x8 and2M3nuts, heads inside its open cavity. Do this BEFORE routing wires; retain the original Cover brackets and mounts.'),
      ('main','Prewire the four MAIN MTA holders/source laps and output splices on the bench with both factory exits. Lay the exact8routes, mount bodies at native seats, install6MTA body straps and4RR clips; source/output insulation grips and cages remain on Deck, including FRGuard and RRoutput.'),
      ('p_wago','Prewire the four P-WAGO blocks on the bench using the pinned20port/16lead map; close levers before positioning. Fit bodies into existing Deck seats, install four recorded body straps through8native slots, then dress the crossing wires. No lever motion on a strapped crowded board is assumed.'),
      ('bank_cover','Bring left/right bank and Cover down together over the parked24ends, as the reverse of the shared removal path. Do not independently drop the Cover around a fully seated bank. Seat the four native mounts/brackets and install4M2x12/4M2nuts/4washers; retain all Cover mount hardware.'),
      ('terminals','Reverse the5.5mm input-end release, reconnect keyed24TE ends, restore24terminal restraints with the recorded bottom-open upperkeepers. Fit12mini holders and12ATOs last; headJR last. This is a nominal prototype order, not power authorization or whole-robotA2 closure.')]
    remove=[
      ('isolate','Disconnect and remove battery, disconnect headJR. Keep bank and Cover together; do not independently raise Cover.'),
      ('holders','Remove12ATOs. Use the recorded24clip-slot tools to release12holders, unplug24TE ends, cut their24insulation straps.'),
      ('free_loops','Cut9output,6source,6MTA-body and4P-WAGO-body straps:49in total includingTE. Keep the four lower input feed straps. Closed WAGO bodies and all insulation/wires stay at recorded Deck-supported positions; no cage opening or wire parking required.'),
      ('park','Move12input TE ends5.5mm inward along recorded connected loops;12output TE axes stay fixed. Do not push TE terminals through backers.'),
      ('lift','Undo4bank and4Cover screws. Lift bank+Cover together100mm nominally, leaving Deck, channel,2GuardM3fasteners, source/output cages and all wires stationary. Shared verification is sampled at2/5/10/30/60/100mm, NOT a claimed continuous sweep or physical test.'),
      ('main_service','Once bank+Cover are removed, the four RR body clip tools have the recorded clearance. No P-WAGO cage opening is necessary for this module removal. Optional whole-Deck rewiring is outside the qualified local removal sequence; do not infer clear wired-block translation or in-situ lever motion from bench prewiring.'),
      ('restore','Reverse sequence; replace all49cut loops, preserving exact wire/terminal labels and isolation. Perform phase2 fit/latch/strap-pull/PETG stiffness/polarity/continuity/current/thermal trials before power.')]
    def chain(rows):return [dict(id=n,after=[] if i==0 else [rows[i-1][0]],action=s) for i,(n,s) in enumerate(rows)]
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-assembly-r6';out.mkdir(parents=True,exist_ok=True);assert not (out/'assembly.json').exists()
    save(out/'assembly.json',dict(status='ONE_NOMINAL_LOCAL_SEQUENCE_SAMPLED_RELEASE_COMPLETE',selected=False,physical_pass=False,W5_complete=False,
      assembly_complete=True,whole_robot_A2_complete=False,bench_P_ports=20,occupied_P_ports=16,empty_P_ports=4,terminal_ends=24,factory_feeds=8,
      part_ownership=dict(Guard='Deck',FR_output='Deck/Guard',RL_output='Deck',RR_output='Deck'),assembly=chain(stages),removal=chain(remove),
      replacement_ties=49,actual_lever_motion_qualified=False,in_situ_lever_motion_required=False,
      sampled_shared_release_clear=True,continuous_withdrawal_qualified=False,nominal_clip_deflection_requires_phase2=True,
      source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=t.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat()))
    print('ONE_LOCAL_ASSEMBLY_AND_REMOVAL_RECORDED',20,24,49,flush=True)
if __name__=='__main__':main()
