"""Compose existing positive evidence; never re-run the collision batches.

Canonical source receipts replace an unusable voxel-cache identity as authority.
This receives two fixed body portions, not factory leads, continuous motion or N01.
"""
import hashlib
import json
import math
import time
import zipfile
from pathlib import Path
import numpy as np
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_tangent_routes import length, min_radius
from feline_atomic_save import save_json

FOLDER = OUT/'W009-W069-harness-corridor'
STATUS = 'CURRENT_BODY_CANONICAL_SOURCES_AND_SAMPLE36_RECEIVED_NOT_N01'


def receive(wire, middle, prefixes, boundaries):
    tick = time.monotonic(); pins = {}
    def read(name):
        path = FOLDER/name; p = json.loads(path.read_text())
        for key, value in p.get('source_sha256', {}).items():
            assert sha(ROOT/key) == value, key
            assert key not in pins or pins[key] == value
            pins[key] = value
        if 'bundle' in p:
            assert sha(ROOT/p['bundle']) == p['bundle_sha256']
            pins[p['bundle']] = p['bundle_sha256']
        pins[path.relative_to(ROOT).as_posix()] = sha(path)
        return p
    bindings = read('authoritative-source-bindings.json')
    assert bindings['status'] == 'AUTHORITATIVE_IMMUTABLE_SOURCES_MATCH_QUERY_GEOMETRY'
    assert len(bindings['bindings']) == 174
    assert all(r['full_cleaned_BRep_tokens_match'] for r in bindings['bindings'].values())
    coverage = read('current-source-coverage-review.json')
    assert coverage['expected_actors'] == 1524 and coverage['covered_named_actors'] == 1527
    assert not coverage['missing_named_actors'] and coverage['new_queries_positive']
    read('receipted-serialization-recovery.json')
    caps = read('four-current-caps.json')
    bus = read('canonical-BUS117-source-query.json')
    assert bus['original25_valid'] and bus['core116_cleaned_geometry_matches_loaded_provider']
    assert bus['original25_gaps_mm'][wire] >= 1.25
    preflight = read('W009-east-loop-removed-preflight.json')
    assert preflight['W069_actual_gap_mm'] >= .2
    if wire == 'W009':
        packet = read('W009-east-loop-removed.json'); recipe = packet['recipe']
        outer = preflight['outer']; self_gap = preflight['self_lower_bound_mm']
        motion = read('W009-east-loop-removed-sampled36.json')
    else:
        assert wire == 'W069'
        packet = read('W069-subset-spacing.json')
        recipe = read('pair-preflight.json')['paths']['W069/body']
        outer = read('pair-outline.json')['checks']['W069']
        self_gap = recipe['nonlocal_self_gap_lower_bound_mm']
        motion = read('W069-sampled36.json')
    assert outer['ok'] and self_gap >= .2 and min_radius(recipe['parts']) >= 12.4
    assert abs(length(recipe['parts'])-recipe['length_mm']) < 1e-6
    checks = dict(packet['checks'])
    assert not packet.get('errors') and all(r['ok'] for r in checks.values())
    for suffix in ('receipted101', 'canonical-BUS116', 'canonical-AUX', 'canonical-remaining30'):
        batch = read(wire+'-'+suffix+'-subset.json')
        assert not batch['errors'] and not batch['failures']
        for name, row in batch['checks'].items():
            assert row['gap_mm'] >= 1.25-1e-6, (name,row)
            assert name not in checks, name
            checks[name] = dict(row, minimum_mm=1.25, ok=True)
    checks['BUS25:valid_original'] = dict(gap_mm=bus['original25_gaps_mm'][wire], minimum_mm=1.25, ok=True)
    assert motion['status'] == 'SOURCE_UNIT_SAMPLE36_MOTION_RECEIVED'
    assert motion['completed'] == ['CurrentMiddle:'+wire]
    assert all(r['ok'] for r in motion['checks'].values())
    assert middle.isValid() and len(middle.Solids) == 1
    # The passed solid must be exactly the saved tested middle, not another recipe.
    from receive_feline_rrp_shared_height import load
    if wire == 'W009': tested = load(packet)['CurrentMiddle:'+wire]
    else: tested = load(read('pair-outline.json'))[wire]
    from refresh_feline_power_space import same_geometry
    assert same_geometry(middle,tested)
    saved_prefixes = load(read('recovered-context.json'))
    retained = [r for r in caps['caps'] if r['wire'] == wire]
    assert len(retained) == 2 and {r['side'] for r in retained} == {'start','end'}
    payload = {'CurrentMiddle:'+wire:middle.exportBrepToString().encode()}; ends = []
    for row in retained:
        owner = row['owner']; s = prefixes[owner]
        assert same_geometry(s,saved_prefixes[owner])
        assert row['cap_count'] == 1 and abs(row['cap_areas'][0]-math.pi*1.55**2) < 1e-5
        assert s.isValid() and len(s.Solids) == 1
        check = checks[owner]
        assert check['gap_mm'] < 1e-6 and check['common_mm3'] < 1e-5
        eid = wire+'/body/'+row['side']; e = next(e for e in boundaries if e['id'] == eid)
        endpoint = recipe['parts'][0]['start'] if row['side'] == 'start' else recipe['parts'][-1]['end']
        assert np.allclose(endpoint,e['routing_exit_mm'],atol=1e-7,rtol=0)
        ends.append(dict(id=eid, point_mm=e['routing_exit_mm'], axis=e['routing_exit_axis'],
                         retained_prefix_length_mm=row['volume_length_mm']))
        payload[owner] = s.exportBrepToString().encode()
    complete = recipe['length_mm'] + sum(r['volume_length_mm'] for r in retained)
    assert abs(complete-caps['body_lengths_mm'][wire]) < 1e-6
    dest = OUT/('n01-current-'+wire+'-complete-body-plan.json'); archive = dest.with_suffix('.breps.zip')
    assert not dest.exists() and not archive.exists()
    geometry = []
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for name, raw in payload.items():
            entry = str(len(geometry))+'.brep'; z.writestr(entry,raw)
            geometry.append(dict(name=name,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    pins[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    result = dict(status=STATUS,portion=wire+'/body',middle_recipe=recipe,
        current_boundaries=ends,source_prefix_owners=[r['owner'] for r in retained],
        complete_body_length_mm=complete,middle_length_mm=recipe['length_mm'],checks=checks,outer=outer,
        sampled_poses=36,motion_actors_covered=3888,motion_receipt=next(k for k in pins if k.endswith(wire+'-sampled36.json') or k.endswith(wire+'-east-loop-removed-sampled36.json')),
        motion_proof='Pinned sampled36 receipt; not continuous or head/tail motion.',
        source_authority='Immutable canonical source geometry bindings plus original BUS25 in verified current inverse frame; old voxel cache is not collision authority.',
        legacy_cache_hash_identity_recovered=False,current_named_sources_covered=1527,
        geometry=geometry,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),source_sha256=pins,
        whole900_moving_side_head_tail_motion_stock_and_complete123_OPEN=True,
        N01_complete=False,physical_pass=False,native_changed=False,worker_seconds=round(time.monotonic()-tick,3))
    save_json(dest,result)
    print(wire,STATUS,complete,result['worker_seconds'],flush=True)
    return result
