"""Compose an explicitly verified unchanged-pair cache for one MTA actor delta.

No completed static actor inherited: the receiver still visits missing pairs
against changed neighbors. All geometry hashes, old policies and base-source
pins must match. A rejected changed pair is excluded, never relabelled green.
"""
import gzip,json,sys
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def main():
    name=sys.argv[1] if len(sys.argv)>1 else 'n01-MTA-S1-complete-bypass.json'
    assert Path(name).name==name and name.startswith('n01-MTA-') and name.endswith('.json')
    sf=OUT/name;current=json.loads(sf.read_text())
    assert current['status']=='COMPLETE_MTA_KIT_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN'
    assert len(current['completed_rest'])==64 and not current['failures']
    oldfile=OUT/'n01-MTA-rear-shoulders-scene.json';old=json.loads(oldfile.read_text())
    receiver=ROOT/'tools/cad/receive_feline_mta_family_scene.py'
    for record in (old,current):
        for p,h in record['source_sha256'].items():assert sha(ROOT/p)==h,p
    assert old['source_sha256'][receiver.relative_to(ROOT).as_posix()]==sha(receiver)
    before={r['name']:r for r in old['geometry']};after={r['name']:r for r in current['geometry']}
    assert set(before)==set(after) and len(before)==64
    changed={n for n in before if before[n]['sha256']!=after[n]['sha256']}
    assert changed=={'CustomPrefix:W052'} and current['changed_actors']==sorted(changed)
    for n in set(before)-changed:assert before[n]==after[n],n
    for p,h in old['source_sha256'].items():
        if p in current['source_sha256']:assert current['source_sha256'][p]==h,p
    pf0=ROOT/old['pair_rows'];assert sha(pf0)==old['pair_rows_sha256']
    rows=json.loads(gzip.decompress(pf0.read_bytes()))
    reused={k:v for k,v in rows.items() if not changed.intersection(k.split('|'))}
    assert reused and all(v['ok'] for v in reused.values())
    dest=sf.with_name(sf.stem+'-scene.json');pf=dest.with_suffix('.pairs.json.gz')
    assert not dest.exists() and not pf.exists(),'Receive existing scene cache; never overwrite its progress'
    pins=dict(current['source_sha256']);pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/current['bundle'],receiver)})
    pf.write_bytes(gzip.compress(json.dumps(reused,separators=(',',':')).encode(),mtime=0))
    result=dict(current,status='RUNNING_WHOLE_MTA_SCENE',source_sha256=pins,completed_static=[],completed_motion=[],
        inherited_rest_actor_count=64,inherited_rest_worker_seconds=current['worker_seconds'],
        pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),checks=len(reused),failures=[],
        assembly_tools_and_common123_capacity_still_OPEN=True,
        unchanged_pair_cache=dict(source=oldfile.relative_to(ROOT).as_posix(),source_sha256=sha(oldfile),
            pair_rows_sha256=sha(pf0),writer=Path(__file__).relative_to(ROOT).as_posix(),writer_sha256=sha(Path(__file__)),
            byte_identical_actors=63,changed_actors=sorted(changed),reused_pair_count=len(reused),
            old_receiver_policy_identical=True,no_completed_static_actor_inherited=True,
            rejected_changed_pairs_EXCLUDED_not_passed=[k for k in old['failures'] if changed.intersection(k.split('|'))]))
    save_json(dest,result);print('Seeded',len(reused),'unchanged pairs; changed',sorted(changed),flush=True)


if __name__=='__main__':main()
