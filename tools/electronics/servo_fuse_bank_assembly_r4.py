"""One bench-wiring/module-removal recipe; no in-place WAGO lever claim.

R4 connected loops supersede serviceR3's requirement to detach all input
pigtails at WAGO. This recipe stays conditional until new fixed main feeds,
restraints and native parts pass the common installed/removal interface.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    started=datetime.now(timezone.utc)
    sources={}
    def read(rel):
        p=ROOT/rel;sources[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    ports=read('hardware/electronics/full-cat/servo-fuse-wago-map-r1/interface.json')
    loops=read('hardware/electronics/full-cat/servo-fuse-bank-connected-release-r4/checks.json')
    service=read('hardware/electronics/full-cat/servo-fuse-bank-service-r3/checks.json')
    lift=read('hardware/electronics/full-cat/servo-fuse-bank-lower-loop-lift-r2/checks.json')
    materials=read('hardware/electronics/full-cat/servo-fuse-parent-extension-materials-r2/materials.json')
    assert (ports['all_ports'],ports['connected_ports'],ports['unused_ports'])==(20,16,4)
    assert not loops['hits'] and not loops['errors'] and not loops['continuous_deformation_qualified']
    assert service['parked_ends']==24 and not service['hits'] and not service['errors']
    assert materials['red_4mm2_additional_rough_blank_mm']==1080
    # Read the retained lift result, not another expensive geometry rerun.
    assert not lift['hits'] and not lift['errors']
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-assembly-r4'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'assembly.json').exists()
    save(out/'assembly.json',dict(selected=False,physical_pass=False,W5_complete=False,
        status='CONDITIONAL_ONE_BENCH_ASSEMBLY_AND_CONNECTED_MODULE_REMOVAL',
        installed_ports=16,empty_ports=4,terminal_ends=24,
        assembly=[
            'Battery absent. Work on removed Deck, before Pi/bridge/cover obstruct the source cages. Use the mapped world orientations of all four P blocks.',
            'Prepare the24 TE ends and12 lower pigtails to their saved routes/blank allowances. Fit labelled ends, not a guessed common100mm branch.',
            'Prewire all16 occupied P-WAGO cages on the bench; one unsoldered bare conductor per cage, retain the4 empty port5 cages. Close and pull-check before mounting the blocks. No claim of opening their levers in the assembled robot.',
            'Fit four fixed main holders on their integral Deck saddles. Install the eight body ties and complete both factory exits with the saved12 wire sections. Front extensions use two221412; rear supported lap joints use selected TE3/8 sleeve. Native joint and wire grips are still required.',
            'Mount the prewired blocks and fixed main feeds without stretching the wires. Secure each insulation grip. Preserve the R4 lower loops and their fixed P-WAGO mouths.',
            'Fit the12 mini holders into the native bank cutouts and mate their24 TE ends. Fit the24 input/output strain ties and ATOs; screws/brackets retain their recorded native axes.',
            'Mount bank+cover together after the new fixed-main-feed clearances are resolved. Reconnect the head JR only after the enclosure is seated. Do not power hardware in phase1.'
        ],
        removal=[
            'Disconnect/remove battery and release head JR/ties. Fixed P-WAGO ends and four main holders stay on Deck.',
            'Remove the12 ATOs. Use the24 nominal clip slots and0.8x3mm tool to release the depicted holder clips. Their actual latch action is a phase2 coupon check.',
            'Raise each mini holder10mm to unmate the fixed TE ends. Cut/release all24 bank insulation ties, not the fixed source/main-holder ties.',
            'Park the12 input TE ends5.5mm inward using connected lower-loopR4. Keep12 output ends on their axes. Do NOT pull a TE down through a backer and do NOT open the P-WAGO levers for this operation.',
            'Release module mounting fasteners and hold the24 parked ends stationary while raising bank+cover together100mm. The old lower-loop lift proof is retained; new fixed main-feed/connector/grip clearances still need the combined check.',
            'Refit in reverse, restore the nominal lower loops and replace cut strain ties. Physical continuity/pull/current/thermal trials belong to phase2.'
        ],
        supersedes='serviceR3 step requiring detached input pigtails; connected-loopR4 preserves fixed upstream mouths. Does NOT certify in-place WAGO lever travel.',
        still_open=['R7 strict native repair/result and actual installed contacts.',
                    'Native WAGO/lap/insulation restraints and cover/bank reliefs.',
                    'Combined100mm module removal against all new fixed main feeds and their supports.',
                    'One final selection/stock/24 replacement ties accounting/E3 contribution.'],
        evidence_limit='Five sampled connected-loop poses, not continuous wire deformation or physical latch/fit qualification.',
        source_sha256=sources,script_sha256=sha(Path(__file__)),
        started_utc=started.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(dict(ports=20,ends=24,selected=False,service_complete=False)))


if __name__=='__main__':main()
