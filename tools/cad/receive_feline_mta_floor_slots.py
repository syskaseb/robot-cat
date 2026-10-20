"""Receive only four exact nylon-head/own-floor planned slot interfaces.

The constructor cuts full selected T18I head budget+.2mm in its OWN floor.
This is a declared provisional printed fit, not ordinary foreign clearance.
No geometry moves, no blanket floor/nylon waiver, original rows preserved.
"""
import gzip,json,time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load
from feline_fore_power_pair import SolidQueries
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();sf=OUT/'n01-MTA-S1-complete-bypass-scene.json';r=json.loads(sf.read_text())
    assert r['status']=='WHOLE_MTA_SCENE_STATIC_HOLD'
    assert r['failures']==['ArcGrip:W041:head|LowerBay:RearPanel']
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    actors=load(r);pf=ROOT/r['pair_rows'];assert sha(pf)==r['pair_rows_sha256']
    rows=json.loads(gzip.decompress(pf.read_bytes()));query=SolidQueries();receipts={};original={}
    metadata={p['name']:p for p in r['geometry']}
    for w,p in r['positive_roots'].items():
        head='ArcGrip:'+w+':head';floor=p['parent'];assert floor in r['print_groups']
        assert metadata[head]['material_role']=='selected_T18I_nylon_budget'
        assert abs(actors[head].Volume-5*4.3*5.3)<1e-5
        assert p['parent_actual_overlap_mm3']>1e-5
        common=actors[head].common(actors[floor]);assert common.isNull() or common.isValid()
        gap=query.distance(actors[head],actors[floor]);assert common.Volume<1e-5 and gap>=.2-1e-6,(w,gap,common.Volume)
        key='|'.join(sorted((head,floor)))
        if key in rows:original[key]=rows[key]
        receipts[key]=dict(ok=True,gap_mm=gap,minimum_mm=.2,whole_common_mm3=common.Volume,
            exact_own_head_slot_pair=[head,floor],selected_T18I_full_head_budget_mm=[5,4.3,5.3],
            declared_constructor_slot_clearance_mm=.2,foreign_margin_NOT_changed_mm=1.25,
            printed_fit_and_delivered_tie_measurement_phase2=True)
    assert len(receipts)==4 and set(r['failures'])<=set(receipts)
    layout=OUT/'n01-MTA-S1-complete-bypass.json';assert r['source_sha256'][layout.relative_to(ROOT).as_posix()]==sha(layout)
    record=dict(status='FOUR_EXACT_OWN_T18I_FLOOR_SLOTS_RECEIVED',source_sha256={
        p.relative_to(ROOT).as_posix():sha(p) for p in (layout,ROOT/r['bundle'],Path(__file__),ROOT/'tools/cad/receive_feline_mta_shoulder_layout.py')},
        original_source_snapshot=dict(commit='f31ba528',scene_path=sf.relative_to(ROOT).as_posix(),scene_sha256=sha(sf),
            pair_rows_path=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf)),
        original_scene_status=r['status'],original_observations=original,received_pairs=receipts,
        geometry_bundle_sha256=r['bundle_sha256'],native_changed=False,N01_complete=False,physical_pass=False,
        worker_seconds=round(time.monotonic()-tick,3))
    proof=OUT/'n01-MTA-own-floor-slots.json';assert not proof.exists(),'Receive already adopted slot contract, do not duplicate'
    save_json(proof,record)
    rows.update(receipts);assert all(v['ok'] for v in rows.values())
    r.setdefault('interface_receipts',[]).append(dict(path=proof.relative_to(ROOT).as_posix(),sha256=sha(proof),
        observed_scene_before_sha256=sha(sf),original_pair_rows_sha256=sha(pf),exact_received_pairs=sorted(receipts)))
    pf.write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0))
    r.update(status='RUNNING_WHOLE_MTA_SCENE',pair_rows_sha256=sha(pf),checks=len(rows),failures=[])
    save_json(sf,r);print(record['status'],len(receipts),record['worker_seconds'],flush=True)


if __name__=='__main__':main()
