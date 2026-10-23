"""Recover only exact old hashes linked by the existing mesh-only receipt.

No archive search, approximate geometry match, new pose, or acceptance.
"""
import hashlib
import json
import time
import zipfile
from pathlib import Path
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def eligible(name, digest, missing, expected, receipt):
    return (name in missing
            and receipt['previous_bridge']['source_geometry_sha256'].get(name) == digest
            and receipt['current_source_geometry_sha256'].get(name) == expected[name])


def recover(parts, metadata):
    tick = time.monotonic()
    folder = OUT/'W009-W069-harness-corridor'
    source = OUT/'power-space-current/mesh-only-resume.json'
    bridge = OUT/'joint-corridor-space-20261021/owner-source-cache-bridge.json'
    context = folder/'recovered-context.json'
    receipt = json.loads(source.read_text())
    expected = json.loads(bridge.read_text())['source_geometry_sha256']
    missing = set(json.loads(context.read_text())['unrecovered'])
    assert receipt['status'] == 'MESH_ONLY_SERIALIZATION_RECOVERY_NOT_GEOMETRY_ACCEPTANCE'
    assert receipt['full_cleaned_BRep_tokens_match_replayed_pinned_sources']
    for p, h in receipt['replayed_source_sha256'].items():
        assert sha(ROOT/p) == h, ('Changed provider', p)
    dest = folder/'receipted-serialization-recovery.json'
    archive = dest.with_suffix('.breps.zip')
    assert not dest.exists() and not archive.exists(), 'Receive saved recovery instead'
    shapes, rows = {}, []
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(missing & parts.keys()):
            raw = parts[name].exportBrepToString().encode()
            digest = hashlib.sha256(raw).hexdigest()
            if not eligible(name, digest, missing, expected, receipt):
                continue
            entry = str(len(rows))+'.brep'
            z.writestr(entry, raw)
            shapes[name] = parts[name]
            rows.append(dict(name=name, entry=entry, sha256=digest,
                             expected_scene_hash=expected[name],
                             metadata=metadata.get(name, {})))
    assert rows, 'No exact previous serialization recovered'
    packet = dict(status='EXISTING_MESH_ONLY_RECEIPT_CHAIN_PARTIAL_RECOVERY',
                  geometry=rows, bundle=archive.relative_to(ROOT).as_posix(),
                  bundle_sha256=sha(archive), unrecovered=sorted(missing-shapes.keys()),
                  source_sha256={p.relative_to(ROOT).as_posix(): sha(p)
                                 for p in (source, bridge, context, Path(__file__))},
                  whole_scene_received=False, N01_complete=False, physical_pass=False,
                  worker_seconds=round(time.monotonic()-tick, 3))
    save_json(dest, packet)
    print(packet['status'], len(rows), 'remaining', len(packet['unrecovered']), flush=True)
    return shapes, packet
