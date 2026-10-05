"""Recover only the failed receipt write after all geometry assertions ran.

The worker failed at source_sha256 evaluation AFTER saving its shape and
blueprint, and after asserting no hits and16fully supported bearing rings.
Do not re-run geometry or invent lost per-pair figures or worker timestamps.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
from servo_fuse_inputs_r1 import save, sha
import w5_loom_mount_receive as R


def main():
    root=R.ROOT;out=R.OUT
    observation=out/'execution-observation.json';w=json.loads(observation.read_text(encoding='utf-8'))
    script=Path(R.__file__)
    assert sha(script)==w['executed_source_sha256']
    assert w['exit_code']==1 and w['failure_stage']=='source_sha256_in_final_checks_writer'
    assert not (out/'checks.json').exists()
    bp_path=out/'native-blueprint.json';bp=json.loads(bp_path.read_text(encoding='utf-8'))
    geom=root/bp['geometry'];assert geom.is_file() and len(bp['current_roles'])==5
    assert len(bp['axes'])==8 and len(bp['correction_channels'])==12
    assert bp['fixed_mount_static_received'] and not bp['all_installed_service_access']
    # Source execution ordering: saved these two files only after every check,
    # no-hit assertion and bearing assertion. Capture original source AND error.
    source=script.read_text(encoding='utf-8')
    assert source.index('assert not hits,hits')<source.index("save(OUT/'native-blueprint.json',bp)")
    assert source.index("save(OUT/'native-blueprint.json',bp)")<source.index('source_sha256=')
    prior_path=R.M.OUT/'checks.json';prior=json.loads(prior_path.read_text(encoding='utf-8'))
    for rel,digest in {**prior['source_sha256'],**prior['files']}.items():assert sha(root/rel)==digest,rel
    pins=[Path(__file__),script,observation,bp_path,prior_path,R.M.OUT/'native-blueprint.json',
          root/'hardware/cad/studies/w5-central-retention-native-r1/CentralRetentionDeck_CANDIDATE_WORLD.brep']
    save(out/'checks.json',dict(status='FIXED_FRAME_MOUNT_RECEIVED_RECOVERED_AFTER_WRITER_ERROR',
        all_static_material_pairs_clear=True,hits=[],errors=[],
        numeric_pair_and_bearing_rows_not_recovered=True,
        geometry_validation_basis='Observed executed-source ordering: four single-solid/BOP assertions, complete Deck assertion, all contact/bearing assertions preceded saved geometry/blueprint and receipt writer exception.',
        frame_single_solids=4,Deck_single_solids=1,BOP_errors=0,
        head_and_nut_bearing_full_support_assertions=16,
        reused_external_clear_pairs_from_R1=True,removed_material_only=True,
        installed_key_obstructions=[h for h in prior['hits'] if 'LowerKeyAccess' in h['part']],
        qualified_key_state='BENCH_PRE_BANK_ONLY',all_installed_service_access=False,
        native_complete=False,selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        worker_wall_seconds=None,worker_time_note='Original worker start/finish fields were not saved. Do not infer them from file dates.',
        recovered_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256={p.relative_to(root).as_posix():sha(p) for p in pins},
        files={p.relative_to(root).as_posix():sha(p) for p in [geom,bp_path]}))


if __name__=='__main__':main()
