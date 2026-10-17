"""Receive actual evidence, keep nominal baseline separate, close only on time."""
import json,time,hashlib,subprocess,sys
from pathlib import Path
from datetime import datetime as DT,timezone as TZ

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure'
START=DT.fromisoformat('2026-10-17T00:06:33+00:00')
DEADLINE=DT.fromisoformat('2026-10-17T07:30:00+00:00')


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    tick=time.monotonic();now=DT.now(TZ.utc);close='--close-window' in sys.argv
    if close:assert now>=DEADLINE,'Do not close early just to finish the response'
    files=['layout-checkpoint.json','leg-body-path.json','belly-feet-native.json','belly-feet-bolted-path.json',
        'interior-native-checks.json','shared-skin-exact.json','motion-receivers-checks.json','receiver-straight-land-gate.json',
        'torso-candidate-exports.json','render-receivers-skin.json','grounded-spine-plan.json','grounded-spine-integrated-plan.json',
        'skin-base-wall-thickness.json','skin-end-correction.json','true-normal-wall-study.json',
        'endpoint-current-receivers.json','current-mount-axis-inventory.json','compact-rear-joint-topology-plan.json','whole-profile-wall-budget.json']
    reports={};pins={}
    for filename in files:
        p=OUT/filename;data=json.loads(p.read_text());pins[p.relative_to(ROOT).as_posix()]=sha(p)
        reports[filename]={k:v for k,v in data.items() if k in ('status','worker_seconds','native_receiver_seconds','native_seconds',
            'native_built','fresh_reopen','native','native_sha256','pairs','leg_poses','head_poses','changed_parts',
            'changed_native_parts_verified','unchanged_saved_node_placements_verified','full_wiring_complete',
            'contacts','clearance_failures','errors','exact_lateral_surface_minimum_mm','base_lateral_minimum_mm',
            'endpoint_records','mapped_identity_only','unallocated_roles','actual_saved_axis_count','known_wire_pieces_checked')}
        if data.get('native') and data.get('native_sha256'):
            native=ROOT/data['native'];assert sha(native)==data['native_sha256'],filename
            pins[data['native']]=data['native_sha256']
    scorefile=OUT.parent/'current-phase1-score.json';score=json.loads(scorefile.read_text());assert score['fixed_total']==20 and score['result_count']==20
    tag='phase1-open-prototype-100-2026-10-17';tagrev=subprocess.check_output(['git','rev-parse',tag+'^{commit}'],cwd=ROOT,text=True).strip();assert tagrev.startswith('9bf50a5')
    baseline=OUT.parent/'phase1-whole-assembly/RobotCatPhase1Current.FCStd'
    assert sha(baseline)=='aff0a45bfc4bb430179e80d8e9b4267dc4727a7bb93cadb9c9083911d3d6d4ee'
    pins[baseline.relative_to(ROOT).as_posix()]=sha(baseline);pins[scorefile.relative_to(ROOT).as_posix()]=sha(scorefile)
    result=dict(status='AUTHORIZED_WINDOW_CLOSED_INCOMPLETE' if close else 'AUTHORIZED_WINDOW_IN_PROGRESS_INCOMPLETE',
        window_id='appearance-lie-bundles-20261017-0930',started_utc=START.isoformat(),deadline_utc=DEADLINE.isoformat(),
        recorded_utc=now.isoformat(),closed=close,stage_completed=False,selected_new_layout=False,physical_pass=False,
        elapsed_window_seconds=round((now-START).total_seconds(),3),elapsed_is_not_continuous_CPU_or_active_work=True,
        baseline=dict(tag=tag,commit=tagrev,fixed_total=20,result_count=20,percent=100,change_pp=0,
            scope='Historical approved nominal OPEN prototype documentation only; no physical/electrical qualification or enclosure completion'),
        new_extension=dict(complete=False,percentage_awarded=False,baseline_points_not_transferred=True,
            accepted_scopes=['Sampled36pose leg trajectory and unchanged interfaces only',
                'Four editable belly feet and geometric bolted load path, not strength test',
                'Derived17part receiving layout native/reopen with original source preserved, not full wiring',
                'Four panel candidate36leg/9head contact screen ONLY, not3Dwall/print qualification'],
            invalidated_claims=['No print-ready or completed skin: original side surfaces intersect, aligned-end derivative too thin and has4contacts',
                'No grounded internal scaffold: both common plans rejected; builder intentionally not run',
                'No full wiring: two compulsory9mm lands hit full feet,38identity records unallocated',
                'No appearance completion: cowls, visible old interfaces, actual proportion evaluation and final assembly open']),
        findings=reports,source_sha256=pins,
        exports=dict(current_candidate_set_not_selected=True,print_ready=False,closed_manifold_STL_is_not_wall_or_assembly_approval=True,
            disqualified_by=['skin-base-wall-thickness.json','skin-end-correction.json']),
        reference_analysis=dict(reference='hardware/reference/appearance/ola-cat-reference.jpg',dimensions_inferred=False,
            preserve=['Round head/concave ears','Gentle arched back/waist','Visible mechanical legs','Continuous neck and curved segmented tail'],
            current_visual_concerns=['Boxlike faceted torso','Head/body proportions need a dimensioned side comparison, not a blind lift from perspective',
                'Exposed neck/tail roots and old head-interface elements']),
        next_checkpoint='One supported shared load/bank/4-tail/S1/tail-cowl/true-wall layout before detailed native modules. Reconcile known free-rail anchor strategy and current19PCB axes/178end records. No more new columns or serial wall notches.',
        estimate=dict(next_plan_hours=[1,2],confidence='LOW; planning checkpoint only, not complete extension ETA',
            full_extension_eta='Not reliable before common architecture acceptance; prior estimates not reaffirmed'),
        model_settings_changed=False,runtime_model_effort_independently_verified=False,
        resets_purchases_power_pushes_slicer_ROS_performed=False,receipt_seconds=round(time.monotonic()-tick,3))
    (OUT/'appearance-checkpoint.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','closed','stage_completed','elapsed_window_seconds','receipt_seconds')}),flush=True)


if __name__=='__main__':main()
