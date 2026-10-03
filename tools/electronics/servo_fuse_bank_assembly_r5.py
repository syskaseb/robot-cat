"""Receive the completed rear stations into ONE conditional bank sequence.

No new geometry, selected quantities, or lever-motion claim. Keep the actual
RR station attached to the right bank in the removal dependencies; R4's old
recipe treated every output cage as fixed to Deck and is not applicable.
Run only after checkpoint R20 and its pinned native exports are complete.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/electronics'))
from servo_fuse_inputs_r1 import sha, save


def main():
    start = datetime.now(timezone.utc)
    pins = {}

    def read(rel):
        p = ROOT / rel
        pins[rel] = sha(p)
        return json.loads(p.read_text(encoding='utf-8'))

    checkpoint = read('hardware/electronics/full-cat/servo-fuse-construction-checkpoint-r20/manifest.json')
    native = read('hardware/electronics/full-cat/servo-fuse-rear-output-stations-parameter-r4/checks.json')
    rear = read('hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r3/checks.json')
    mapping = read('hardware/electronics/full-cat/servo-fuse-wago-map-r1/interface.json')
    service = read('hardware/electronics/full-cat/servo-fuse-bank-service-r3/checks.json')
    materials = read('hardware/electronics/full-cat/servo-fuse-main-feeds-materials-r1/materials.json')
    assert checkpoint['rear_output_stations']['contacts'] == 0
    assert len(native['exports']) == 4 and all(r['parameter_mm'] == [.2, .3, .2] for r in native['exports'])
    assert not rear['hits'] and not rear['errors'] and not rear['mount_failures']
    assert (mapping['all_ports'], mapping['connected_ports'], mapping['unused_ports']) == (20, 16, 4)
    assert service['parked_ends'] == 24 and not service['hits'] and not service['errors']
    assert len(materials['factory']) == 8 and len(materials['HELU23802']['extensions']) == 7
    assert {r['leg'] for r in rear['stations']} == {'RL', 'RR'}
    assert len(rear['ties']) == 6 and sum(r['installed'] for r in rear['ties']) == 6
    # Do not overwrite the retained R51 or merge an obsolete extension list.
    out = ROOT / 'hardware/electronics/full-cat/servo-fuse-bank-assembly-r5'
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / 'assembly.json').exists(), 'Preserve recorded construction'
    stages = [
        dict(id='bench', after=[], action='Battery absent. Label the 20 project slots of the four P blocks; prewire their 16 occupied cages on the bench, leaving the four port5 cages empty. Use the pinned map, not manufacturer cage numbers. Do not tin conductors.'),
        dict(id='main', after=['bench'], action='On removed Deck assemble the four fixed MTA bodies in main-joint-layout-r3 orientations, their integral saddles and recorded straps/clips. Build all eight factory feeds: seven HELU extensions, FL W041 direct, three insulated source laps, four output221-412 cages. Both exits of every holder must be present.'),
        dict(id='fixed', after=['main'], action='Install the prewired P blocks, front guard and fixed FL/FR/RL source/output insulation grips. RL output cage is integral with Deck. Do not re-use the old flat-Deck support or an older rear-output shell.'),
        dict(id='bank', after=['fixed'], action='Fit the twelve mini holders and twenty-four TE ends with their retained lower input loops and output axes. Install the matched left/right bank and current Cover. RR output cage and both insulation seats belong to RIGHT BANK, not Deck.'),
        dict(id='rear', after=['bank'], action='Place RL/RR output housings into their matched open trays. Restrain housing and each insulated lead separately using the six specified T18I. Keep the exact R8 wire paths and the existing W038/W039 passage; do not pull a bare end through a restraint.'),
        dict(id='close', after=['rear'], action='Complete fasteners and head JR last. The final seating/removal interface still requires the common check; this ordering is a conditional construction recipe, not an accepted assembled robot.'),
    ]
    seen = set()
    for row in stages:
        assert set(row['after']) <= seen
        assert row['id'] not in seen
        seen.add(row['id'])
    release = [
        dict(id='isolate', requires=[], action='Disconnect/remove battery and release the head JR. Do not separate Cover vertically from the bank; that independent motion was rejected.'),
        dict(id='rr_output', requires=['isolate'], action='Release the THREE RR output straps and BOTH RR output221-412 cages before moving the bank. Park the housing and freed insulated leads clear of its tray. Lever/finger/tool clearance and this parking motion are OPEN, so do not call this step qualified.'),
        dict(id='holders', requires=['rr_output'], action='Remove twelve ATOs, release the twenty-four nominal holder clip slots, raise each holder10mm and unmate the TE ends. Release/cut the twenty-four bank strain ties, not the fixed source insulation ties.'),
        dict(id='park', requires=['holders'], action='Move the twelve input TE ends5.5mm inward using retained connected loops; retain the twelve output TE axes. Never pull TE down through the bank backers. Existing loop/rigid-end evidence is inherited only, not proof against the new rear stations.'),
        dict(id='lift', requires=['park'], action='Release bank fasteners and raise bank+Cover as one module over the parked ends. The nominal100mm motion against the CURRENT fixed Deck/RL station/guard and freed RR cage needs a joint test. Four RR MTA clip tools also remain OPEN.'),
        dict(id='restore', requires=['lift'], action='Reassemble in reverse; replace each cut tie and restore all wire roles and isolation. All physical fit, latch/strap pull, PETG load and continuity/current trials belong to phase2.'),
    ]
    seen = set()
    for row in release:
        assert set(row['requires']) <= seen
        seen.add(row['id'])
    save(out / 'assembly.json', dict(
        status='ONE_CURRENT_CONDITIONAL_SEQUENCE_SHARED_RELEASE_OPEN',
        selected=False, physical_pass=False, W5_complete=False, assembly_complete=False,
        bench_P_ports=20, occupied_P_ports=16, empty_P_ports=4, terminal_ends=24,
        factory_feeds=8, HELU_extensions=7, rear_output_restraints=6,
        part_ownership={'RL_output_station': 'Deck', 'RR_output_station': 'BankRight'},
        assembly=stages, removal=release,
        invalidated_prior_claim='AssemblyR4 cannot establish common removal with the new RR cage/grips attached to BankRight.',
        actual_lever_motion_qualified=False, shared_release_qualified=False,
        replacement_ties={'bank_terminal_ties_if_cut':24, 'RR_output_ties_if_cut':3,
                          'rule':'Count once in final installed/spare stock; these are replacement consumables, not extra installed ties.'},
        source_sha256=pins, script_sha256=sha(Path(__file__)),
        started_utc=start.isoformat(), finished_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(dict(ports=20, ends=24, assembly_complete=False, shared_release_qualified=False)))


if __name__ == '__main__':
    main()
