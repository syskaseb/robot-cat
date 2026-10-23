"""Bind queried shapes to named immutable received plans, not voxel-cache hashes.

The old proposal cache is not a mechanical certificate. Its identity mismatch
is retained; fresh route queries may instead use explicit authoritative BReps.
No source search, pose change, Boolean healing, or collision-query repetition.
"""
import hashlib
import json
import time
import zipfile
from pathlib import Path
import Part
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from refresh_feline_power_space import same_geometry
from feline_atomic_save import save_json


def bind(query_shapes, assignments, allowed_source_pins):
    tick = time.monotonic()
    assert set(query_shapes) == set(assignments)
    grouped = {}
    for name, filename in assignments.items():
        grouped.setdefault(filename, []).append(name)
    bindings, pins = {}, {}
    for filename, names in grouped.items():
        path = OUT/filename
        relative = path.relative_to(ROOT).as_posix()
        assert allowed_source_pins.get(relative) == sha(path), ('Not a current source', relative)
        packet = json.loads(path.read_text())
        assert not packet.get('failures') and not packet.get('errors'), filename
        archive = ROOT/packet['bundle']
        assert sha(archive) == packet['bundle_sha256']
        records = packet.get('geometry', packet.get('parts'))
        if isinstance(records, list):
            records = {r['name']: r for r in records}
        pins.update({relative: sha(path), packet['bundle']: sha(archive)})
        with zipfile.ZipFile(archive) as z:
            for name in names:
                record = records[name]
                raw = z.read(record['entry'])
                assert hashlib.sha256(raw).hexdigest() == record['sha256']
                source = Part.Shape(); source.importBrepFromString(raw.decode())
                assert same_geometry(source, query_shapes[name]), ('Source geometry differs', name, filename)
                bindings[name] = dict(source=relative, entry=record['entry'],
                                      raw_source_sha256=record['sha256'],
                                      query_geometry_sha256=hashlib.sha256(query_shapes[name].exportBrepToString().encode()).hexdigest(),
                                      full_cleaned_BRep_tokens_match=True)
    dest = OUT/'W009-W069-harness-corridor/authoritative-source-bindings.json'
    assert not dest.exists()
    pins[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    dependency = ROOT/'tools/cad/refresh_feline_power_space.py'
    pins[dependency.relative_to(ROOT).as_posix()] = sha(dependency)
    packet = dict(status='AUTHORITATIVE_IMMUTABLE_SOURCES_MATCH_QUERY_GEOMETRY',
                  bindings=bindings, source_sha256=pins,
                  tolerance_abs_mm=1e-10, tolerance_relative=1e-12,
                  comparison_ignores_only_three_administrative_flags=True,
                  legacy_voxel_cache_hash_identity_recovered=False,
                  source_geometry_changed=False, old_voxel_cache_not_used_as_collision_proof=True,
                  BUS25_separate_valid_original_inverse_frame_receipt_required=True,
                  N01_complete=False, physical_pass=False,
                  worker_seconds=round(time.monotonic()-tick, 3))
    save_json(dest, packet)
    print(packet['status'], len(bindings), packet['worker_seconds'], flush=True)
    return packet
