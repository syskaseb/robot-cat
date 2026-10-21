"""Check saved pair against hash-recovered current actors; never award partial coverage.

An actual intersection can reject a proposal before all sources are recovered.
Absence of intersections in this subset cannot receive a route or N01.
"""
import json
import time
import hashlib
import zipfile
from pathlib import Path
import FreeCAD as A
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from receive_feline_W024_shared_body import solid
from receive_feline_jpwm_whole_pose import solid_profile_target
from feline_solid_distance import bbox_lower_bound
from feline_fore_power_pair import SolidQueries
from feline_atomic_save import save_json


def check(scene, metadata, expected, source_records, boundaries):
    tick = time.monotonic()
    path = OUT/'joint-corridor-space-20261021/current-exact-linked-body-preflight.json'
    plan = json.loads(path.read_text())
    actors = {}
    for wire in ('W009', 'W069'):
        recipe = plan['paths'][wire+'/body']
        assert recipe['status'] == 'SELF_SEPARATION_PROPOSAL_POSITIVE'
        for side, part, key in [('start', recipe['parts'][0], 'start'),
                                ('end', recipe['parts'][-1], 'end')]:
            row = next(e for e in boundaries if e['id'] == wire+'/body/'+side)
            assert (A.Vector(*part[key])-A.Vector(*row['routing_exit_mm'])).Length < 1e-6
        actors['CurrentMiddle:'+wire] = solid(recipe['parts'], recipe['radius_mm'])
    checks = {}; errors = {}; query = SolidQueries()
    own = {'CurrentMiddle:W009': {'VerticalCuff:W009/body/start', 'Station:D_FR:wire:D_FR.3'},
           'CurrentMiddle:W069': {'RLArc:W069/body/start', 'Station:RL_G:wire:RL_G.1'}}
    for name, actor in actors.items():
        for target, shape in {**scene, **actors}.items():
            if target == name: continue
            r = metadata.get(target, {}).get('nominal_profile_radius_mm', 0) if not shape.Solids else 0
            if bbox_lower_bound(actor.BoundBox, shape.BoundBox) >= 1.25+r+1e-6: continue
            key = name+'|'+target
            try:
                other = solid_profile_target(shape, metadata.get(target, {}))
                gap = query.distance(actor, other)
                row = dict(gap_mm=gap, diagnostic_only=True)
                if gap < 1e-6:
                    # Isolate serialized sources before Boolean work.
                    import Part
                    a = Part.Shape(); a.importBrepFromString(actor.exportBrepToString())
                    b = Part.Shape(); b.importBrepFromString(other.exportBrepToString())
                    row['common_mm3'] = a.common(b).Volume
                    row['intended_cap'] = target in own[name]
                    row['hard_intersection'] = row['common_mm3'] > 1e-5
                checks[key] = row
            except Exception as error:
                errors[key] = str(error)
        print('PAIR_SUBSET', name, len(checks), len(errors), flush=True)
    failures = [k for k, r in checks.items() if r.get('hard_intersection')]
    result = dict(status='SAVED_PAIR_ACTUAL_INTERSECTION_HOLD' if failures else 'SAVED_PAIR_SUBSET_ONLY_NOT_RECEIVED',
        failures=failures, checks=checks, errors=errors,
        scene_actors=len(scene), expected_actors=len(expected),
        unrecovered_current_actors=sorted(set(expected)-set(scene)),
        source_records=source_records, source_sha256={str(path.relative_to(ROOT)):sha(path)},
        boundary_ids=[e['id'] for e in boundaries if e['portion_id'] in ('W009/body','W069/body')],
        whole_scene_received=False, N01_complete=False, physical_pass=False,
        worker_seconds=round(time.monotonic()-tick, 3))
    save_json(OUT/'n01-W009-W069-recovered-subset-check.json', result)
    print(result['status'], failures, result['worker_seconds'], flush=True)
    return result, actors


def save_blocker(actors, scene, expected, source_records, result, witnesses, field_rejection):
    """Small replayable counterexample, not a claim of whole-scene recovery."""
    dest=OUT/'n01-W009-W069-joint-blocker.json'
    archive=dest.with_suffix('.breps.zip')
    assert not dest.exists() and not archive.exists()
    names=sorted({k.split('|')[1] for k in result['failures']})
    assert len(names)==5 and len(witnesses)==5
    records=[]; provenance={}
    for n in names:
        raw=scene[n].exportBrepToString().encode()
        current_hash=hashlib.sha256(raw).hexdigest()
        source=source_records.get(n)
        assert current_hash==expected[n] or source and source[2]==expected[n],n
        provenance[n]=dict(manifest_geometry_sha256=expected[n],
                           saved_geometry_sha256=current_hash,archive_source=source)
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for n,s in {**actors,**{n:scene[n] for n in names}}.items():
            assert s.isValid() and len(s.Solids)==1
            raw=s.exportBrepToString().encode();entry=str(len(records))+'.brep'
            z.writestr(entry,raw)
            records.append(dict(name=n,entry=entry,sha256=hashlib.sha256(raw).hexdigest()))
    inputs=[OUT/'joint-corridor-space-20261021/current-exact-linked-body-preflight.json',
            OUT/'joint-corridor-space-20261021/owner-source-cache-bridge.json',
            OUT/'joint-corridor-space-20261021/n01-integrated-signed-space.json',
            Path(__file__),ROOT/'tools/cad/plan_feline_current_joint_tangent_space.py']
    packet=dict(status='W009_W069_SAVED_ROUTES_REJECTED_FIVE_ACTUAL_INTERSECTIONS',
        geometry=records,bundle=archive.relative_to(ROOT).as_posix(),bundle_sha256=sha(archive),
        witnesses=witnesses,provenance=provenance,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in inputs},
        root_cause='Current shared tangent graph omitted harness_signed_distance; only rigid, motion and outer were constrained.',
        correction='Include existing harness distance with unchanged1.2mm sampling allowance plus0.2mm jacket spacing. Missing harness fails closed.',
        fixed_field_rejection=field_rejection,
        intentional_endpoint_contacts_require_exact_named_cap_checks_not_global_harness_erasure=True,
        previous_graph_and_saved_pair_are_not_accepted_routes=True,
        exact_subset_queries=len(result['checks']),query_seconds=result['worker_seconds'],
        unrecovered_scene_actors=result['unrecovered_current_actors'],
        whole_scene_received=False,N01_complete=False,physical_pass=False,
        next='Recover current whole scene, include accepted W020/W022/W024 as obstacles, and plan both central corridors with harness-aware gates. Preserve endpoints and selected parts; do not retry rejected middle recipes.')
    save_json(dest,packet)
    return packet
