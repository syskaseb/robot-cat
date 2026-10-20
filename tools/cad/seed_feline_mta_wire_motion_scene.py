"""Adopt exact four-wire motion into the one current kit scene, not tools.

Keep the receiver immutable: its hash is part of earlier saved observations.
No static actor is marked complete; the changed head still meets every neighbor.
"""
import gzip,json
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def checked(path):
    r=json.loads(path.read_text())
    for p,h in r['source_sha256'].items():assert sha(ROOT/p)==h,p
    return r


def main():
    sf=OUT/'n01-MTA-body-head-clock.json';r=checked(sf)
    assert len(r['completed_rest'])==len(r['geometry'])==72 and not r['failures']
    of=ROOT/r['reuse_scene']['path'];assert sha(of)==r['reuse_scene']['sha256'];old=checked(of)
    before={p['name']:p for p in old['geometry']};after={p['name']:p for p in r['geometry']}
    assert set(before)==set(after)
    changed={n for n in before if before[n]['sha256']!=after[n]['sha256']}
    assert changed==set(r['changed_actors'])=={'CaseTie:FLHead'}
    for n in set(before)-changed:assert before[n]==after[n],n
    op=ROOT/old['pair_rows'];assert sha(op)==old['pair_rows_sha256']
    original=json.loads(gzip.decompress(op.read_bytes()))
    rows={k:v for k,v in original.items() if not changed.intersection(k.split('|'))}
    assert all(v['ok'] for v in rows.values());reused=len(rows)
    for v in r['named_interface_pairs'].values():
        assert v['ok'] and v['minimum_mm'] in (0,.2) and v['whole_common_mm3']<1e-5
        assert v['foreign_margin_NOT_changed_mm']==1.25
    rows.update(r['named_interface_pairs'])
    mf=OUT/'n01-MTA-four-wires-motion.json';motion=checked(mf)
    assert motion['source_layout']==sf.relative_to(ROOT).as_posix()
    assert motion['status']=='FOUR_FULL_MTA_WIRES_STATIC_AND36MOTION_RECEIVED_KIT_TOOLS_OPEN'
    assert not motion['failures'] and set(motion['completed_motion'])==set(r['recipes'])
    assert motion['pose_indices']==list(range(36))
    for p,h in motion['world_source_sha256'].items():assert r['source_sha256'][p]==h,p
    for n,h in motion['source_wire_actor_sha256'].items():assert after[n]['sha256']==h,n
    mp=ROOT/motion['pair_rows'];assert sha(mp)==motion['pair_rows_sha256']
    mr=json.loads(gzip.decompress(mp.read_bytes()))
    assert mr and all(v['ok'] and v['minimum_mm']==1.25 for v in mr.values())
    assert all(k.split('|')[0] in r['recipes'] and '|motion:' in k for k in mr)
    for k,v in mr.items():
        if k in rows:assert rows[k]==v,k
        rows[k]=v
    # Earlier rear failures do not invalidate unchanged, fully received fore
    # actors. Reuse only those actors' motion with identical motion sources.
    ff=OUT/'n01-factory-inputs-current-received.json';fore=checked(ff)
    for p,h in motion['world_source_sha256'].items():assert fore['source_sha256'][p]==h,p
    fg={p['name']:p for p in fore['geometry']}
    received_fore={n for n in fore['completed_motion'] if n in after and fg[n]['sha256']==after[n]['sha256']}
    assert len(received_fore)==20
    fp=ROOT/fore['pair_rows'];assert sha(fp)==fore['pair_rows_sha256']
    frows=json.loads(gzip.decompress(fp.read_bytes()))
    adopted={k:v for k,v in frows.items() if '|motion:' in k and k.split('|')[0] in received_fore}
    assert all(v['ok'] for v in adopted.values())
    assert not any(k.split('|')[0] in received_fore for k in fore['failures'])
    for k,v in adopted.items():
        if k in rows:assert rows[k]==v,k
        rows[k]=v
    wf=OUT/'n01-MTA-prior-motion-witnesses.json';witness=checked(wf)
    assert witness['status']=='EIGHT_PRIOR_REJECTIONS_CLEAR_ON_CURRENT_SHOES_NOT_WHOLE_KIT'
    assert witness['checks']==8 and not witness['failures']
    for n,h in witness['current_actor_sha256'].items():assert after[n]['sha256']==h,n
    for p,h in motion['world_source_sha256'].items():assert witness['source_sha256'][p]==h,p
    wp=ROOT/witness['pair_rows'];assert sha(wp)==witness['pair_rows_sha256']
    wr=json.loads(gzip.decompress(wp.read_bytes()));assert all(v['ok'] for v in wr.values())
    for k,v in wr.items():
        if k in rows:assert rows[k]==v,k
        rows[k]=v
    dest=sf.with_name(sf.stem+'-scene.json');pf=dest.with_suffix('.pairs.json.gz')
    assert not dest.exists() and not pf.exists()
    receiver=ROOT/'tools/cad/receive_feline_mta_contract_scene.py';pins=dict(r['source_sha256'])
    pins.update({p.relative_to(ROOT).as_posix():sha(p) for p in (sf,ROOT/r['bundle'],receiver)})
    pf.write_bytes(gzip.compress(json.dumps(rows,separators=(',',':')).encode(),mtime=0))
    result=dict(r,status='RUNNING_WHOLE_MTA_SCENE',source_sha256=pins,completed_static=[],
        completed_motion=sorted(set(r['recipes'])|received_fore),inherited_rest_actor_count=72,inherited_rest_worker_seconds=r['worker_seconds'],
        pair_rows=pf.relative_to(ROOT).as_posix(),pair_rows_sha256=sha(pf),checks=len(rows),failures=[],
        assembly_tools_and_common123_capacity_still_OPEN=True,
        unchanged_pair_cache=dict(source=of.relative_to(ROOT).as_posix(),source_sha256=sha(of),pair_rows_sha256=sha(op),
            byte_identical_actors=71,changed_actors=sorted(changed),reused_pair_count=reused,
            exact_named_owner_contracts=len(r['named_interface_pairs']),no_completed_static_actor_inherited=True,
            original_failures_EXCLUDED_not_passed=old['failures']),
        received_wire_motion=dict(source=mf.relative_to(ROOT).as_posix(),sha256=sha(mf),pair_rows_sha256=sha(mp),
            received_names=sorted(r['recipes']),reused_pair_count=len(mr),kit_tools_NOT_received=True,
            writer=Path(__file__).relative_to(ROOT).as_posix(),writer_sha256=sha(Path(__file__))),
        received_unchanged_fore_motion=dict(source=ff.relative_to(ROOT).as_posix(),sha256=sha(ff),pair_rows_sha256=sha(fp),
            byte_identical_actors=sorted(received_fore),reused_motion_pairs=len(adopted),foreign_failures_NOT_adopted=fore['failures']),
        received_prior_motion_interfaces=dict(source=wf.relative_to(ROOT).as_posix(),sha256=sha(wf),pair_rows_sha256=sha(wp),
            received_pair_count=len(wr),whole_rear_motion_NOT_inferred=True))
    save_json(dest,result);print('Reused static',reused,'wire motion',len(mr),'fore motion',len(adopted),'changed head remains open',flush=True)


if __name__=='__main__':main()
