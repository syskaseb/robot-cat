"""Receive the one omitted U1 Root0/ForePanel planned print interface.

No shape moves, cuts or foreign-margin relaxation. The original failed row
is retained. Only a valid complete one-solid print permits this ownership.
Native manufacturing/U1 delivered-board fit remain separate gates.
"""
import copy,gzip,json,time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_main_hung_context import compose
from receive_feline_rrp_shared_height import load
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();world,parts,meta,pins,docs=compose()
    sf=OUT/'n01-MTA-bonded-cradles.json';r=json.loads(sf.read_text());actors=load(r)
    of=sf.with_name(sf.stem+'-scene.json');old=json.loads(of.read_text())
    for record in (r,old):
        for p,h in record['source_sha256'].items():assert sha(ROOT/p)==h,p
    key='LowerBay:ForePanel|StructureReserve:U1CarrierRoot0';assert old['failures']==[key]
    panel,root=key.split('|');assert root not in r['print_groups'][panel]
    # The source's two central printed roots both terminate on their lower
    # deck at -42; do not incorporate a bought module or its arbitrary bbox.
    assert root.startswith('StructureReserve:U1CarrierRoot') and parts[root].isValid()
    assert abs(parts[root].BoundBox.ZMin+42)<1e-6
    groups=copy.deepcopy(r['print_groups']);groups[panel].append(root)
    unit=actors[panel].multiFuse([actors[n] if n in actors else parts[n] for n in groups[panel] if n!=panel])
    assert unit.isValid() and len(unit.Solids)==1
    b=unit.BoundBox;size=[b.XLength,b.YLength,b.ZLength];assert max(size)<250
    c=actors[panel].common(parts[root]);assert c.isNull() or c.isValid()
    op=ROOT/old['pair_rows'];assert sha(op)==old['pair_rows_sha256']
    rows=json.loads(gzip.decompress(op.read_bytes()));original=copy.deepcopy(rows[key])
    assert not original['ok'] and original['minimum_mm']==1.25
    rows[key]=dict(ok=True,named_features_of_actual_single_solid_print=True,complete_print_solids=1,
        print_envelope_mm=size,source_interface_common_mm3=c.Volume,original_foreign_policy_observation=original,
        no_geometric_movement=True,all_other_foreign_margins_unchanged=True)
    assert all(v['ok'] for v in rows.values())
    dest=OUT/'n01-MTA-bonded-root-unions.json';assert not dest.exists()
    files=(sf,ROOT/r['bundle'],of,op,ROOT/'tools/cad/plan_feline_n01_common_backbone.py',
        ROOT/'tools/cad/plan_feline_full_lower_bay.py',Path(__file__))
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in files})
    result=dict(r,source_sha256={**r['source_sha256'],**pins},print_groups=groups,changed_actors=[],removed_actor_aliases=[],
        byte_identical_actors_from_prior=len(actors),reuse_scene=dict(path=of.relative_to(ROOT).as_posix(),sha256=sha(of)),
        fore_root_print_union=dict(parent=panel,root=root,solids=1,valid=True,print_envelope_mm=size,
            source_interface_common_mm3=c.Volume,original_foreign_observation_preserved=True,no_native_change=True),
        N01_complete=False,physical_pass=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result)
    scene=dest.with_name(dest.stem+'-scene.json');pf=scene.with_suffix('.pairs.json.gz');assert not scene.exists() and not pf.exists()
    receiver=ROOT/'tools/cad/receive_feline_mta_material_scene.py';sp=dict(result['source_sha256'])
    sp.update({p.relative_to(ROOT).as_posix():sha(p) for p in (dest,ROOT/result['bundle'],receiver)})
    pf.write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0))
    seeded=dict(result,status='RUNNING_WHOLE_MTA_SCENE',source_sha256=sp,
        completed_static=old['completed_static'][:],completed_motion=old['completed_motion'][:],
        inherited_rest_actor_count=len(actors),inherited_rest_worker_seconds=r['worker_seconds'],
        pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),checks=len(rows),failures=[],
        assembly_tools_and_common123_capacity_still_OPEN=True,
        unchanged_pair_cache=dict(source=of.relative_to(ROOT).as_posix(),source_sha256=sha(of),pair_rows_sha256=sha(op),
            byte_identical_actors=len(actors),reused_pairs=len(rows)-1,exact_print_interface_received=key,
            completed_static_actors_reused_for_identical_geometry=len(old['completed_static']),
            no_added_actors_or_changed_foreign_geometry=True,original_failed_row=original,
            writer=Path(__file__).relative_to(ROOT).as_posix(),writer_sha256=sha(Path(__file__))))
    save_json(scene,seeded);print('ONE_REAL_FORE_PRINT_ROOT_UNION_RECEIVED',size,'reused',len(rows)-1,
        'static',len(old['completed_static']),result['worker_seconds'],flush=True)


if __name__=='__main__':main()
