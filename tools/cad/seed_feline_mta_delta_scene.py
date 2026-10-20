"""Reuse received pairs for the explicit one-ForePanel material-only delta.

Old foreign holds touching the changed floor are excluded. Exact newly
constructed own nylon slots are imported separately with their provenance.
The receiver still visits every missing pair and all sampled motion.
"""
import gzip,json
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def main():
    sf=OUT/'n01-MTA-full-band-slots.json';r=json.loads(sf.read_text())
    assert r['status']=='COMPLETE_MTA_KIT_REST_RECEIVED_STATIC_MOTION_ACCESS_OPEN'
    assert len(r['completed_rest'])==64 and not r['failures']
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    of=ROOT/r['reuse_scene']['path'];assert sha(of)==r['reuse_scene']['sha256'];old=json.loads(of.read_text())
    for p,h in old['source_sha256'].items():assert sha(ROOT/p)==h,p
    before={p['name']:p for p in old['geometry']};after={p['name']:p for p in r['geometry']}
    assert set(before)==set(after) and len(before)==64
    changed={n for n in before if before[n]['sha256']!=after[n]['sha256']}
    assert changed=={'LowerBay:ForePanel'} and r['changed_actors']==sorted(changed)
    for n in set(before)-changed:assert before[n]==after[n],n
    for p,h in old['source_sha256'].items():
        if p in r['source_sha256']:assert r['source_sha256'][p]==h,p
    pf0=ROOT/old['pair_rows'];assert sha(pf0)==old['pair_rows_sha256']
    previous=json.loads(gzip.decompress(pf0.read_bytes()))
    checks={k:v for k,v in previous.items() if not changed.intersection(k.split('|'))}
    assert checks and all(v['ok'] for v in checks.values())
    for key,value in r['named_interface_pairs'].items():
        a,b=key.split('|');assert a.startswith('ArcGrip:') and b=='LowerBay:ForePanel'
        assert value['exact_own_nylon_slot_pair']==[a,b] and value['whole_common_mm3']<1e-5
        assert value['minimum_mm']==.2 and value['foreign_margin_NOT_changed_mm']==1.25
    inherited=len(checks);checks.update(r['named_interface_pairs'])
    dest=sf.with_name(sf.stem+'-scene.json');pf=dest.with_suffix('.pairs.json.gz');assert not dest.exists() and not pf.exists()
    receiver=ROOT/'tools/cad/receive_feline_mta_family_scene.py';pins=dict(r['source_sha256'])
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/r['bundle'],receiver)})
    pf.write_bytes(gzip.compress(json.dumps(checks,separators=(',',':')).encode(),mtime=0))
    result=dict(r,status='RUNNING_WHOLE_MTA_SCENE',source_sha256=pins,completed_static=[],completed_motion=[],
        inherited_rest_actor_count=64,inherited_rest_worker_seconds=r['worker_seconds'],
        pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),checks=len(checks),failures=[],
        assembly_tools_and_common123_capacity_still_OPEN=True,
        unchanged_pair_cache=dict(source=of.relative_to(ROOT).as_posix(),source_sha256=sha(of),pair_rows_sha256=sha(pf0),
            writer=Path(__file__).relative_to(ROOT).as_posix(),writer_sha256=sha(Path(__file__)),
            byte_identical_actors=63,changed_actors=sorted(changed),reused_pair_count=inherited,
            exact_new_own_slot_pair_count=len(r['named_interface_pairs']),no_completed_static_actor_inherited=True,
            rejected_changed_pairs_EXCLUDED_not_passed=[k for k in old['failures'] if changed.intersection(k.split('|'))]))
    save_json(dest,result);print('Reused',inherited,'pairs; received',len(r['named_interface_pairs']),'exact own band/head slots',flush=True)


if __name__=='__main__':main()
