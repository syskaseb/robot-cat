"""Restore only missing actors with explicit received source bindings.

No archive search or geometry regeneration. Never replace a newer overlay.
Unbound actors and invalid supplier geometry remain explicit open items.
"""
import json
from collections import defaultdict
from check_main_p0_placement import ROOT, sha
from plan_feline_layout import OUT
from receive_feline_rrp_shared_height import load


def restore(scene, missing):
    path=OUT/'W009-W069-harness-corridor/authoritative-source-bindings.json'
    binding=json.loads(path.read_text()); groups=defaultdict(list)
    for name in sorted(set(missing)-set(scene)):
        if name in binding['bindings']:
            groups[binding['bindings'][name]['source']].append(name)
    result={}; pins={path.relative_to(ROOT).as_posix():sha(path)}
    for filename,names in groups.items():
        source=ROOT/filename; digest=sha(source)
        assert binding['source_sha256'][filename]==digest
        doc=json.loads(source.read_text())
        rows=doc.get('geometry',doc.get('parts'))
        if isinstance(rows,dict):
            rows=[dict(v,name=k) for k,v in rows.items()]
        chosen=[r for r in rows if r['name'] in names]
        assert {r['name'] for r in chosen}==set(names)
        for row in chosen:
            assert row['sha256']==binding['bindings'][row['name']]['raw_source_sha256']
        result.update(load(dict(doc,geometry=chosen)))
        pins[filename]=digest
    return result,dict(status='BOUND_MISSING_ACTORS_RESTORED_NOT_VALIDATED',
        restored=sorted(result),unbound=sorted(set(missing)-set(scene)-set(result)),
        source_sha256=pins,whole_scene_received=False,N01_complete=False,
        physical_pass=False)
