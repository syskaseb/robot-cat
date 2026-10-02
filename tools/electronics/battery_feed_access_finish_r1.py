"""Resolve the sole remaining temporary tool contact, preserving the R2 failure.

No physical contact is waived. The unchanged pinned R2 screen covers 111
pairs; this run rechecks only the missed W061 segment and records the required
before-wiring assembly. No native model or wire route is modified.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys, copy
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha, save
PARENT = ROOT/'hardware/electronics/full-cat/battery-feed-pair-r2/checks.json'
OUT = ROOT/'hardware/electronics/full-cat/battery-feed-access-finish-r1'


def main():
    import FreeCAD
    import Part
    start = datetime.now(timezone.utc)
    assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True, exist_ok=True)
    prior = json.loads(PARENT.read_text(encoding='utf-8'))
    assert prior['status'] == 'REJECTED_PAIR' and not prior['errors']
    assert sha(ROOT/'tools/electronics/battery_feed_pair_r2.py') == prior['script_sha256']
    for rel, digest in prior['source_sha256'].items():
        assert sha(ROOT/rel) == digest, rel
    assert len(prior['hits']) == 1
    row = prior['hits'][0]
    assert (row['part'], row['owner']) == ('HeadToolReserve_1', 'W061_3_DESIGN')
    def shape(suffix):
        paths = [p for p in prior['source_sha256'] if p.endswith(suffix)]
        assert len(paths) == 1, paths
        s = Part.Shape(); s.read(str(ROOT/paths[0])); return s, paths[0]
    tool, tool_path = shape('/HeadToolReserve_1_DESIGN.brep')
    wire, wire_path = shape('/W061_3_DESIGN.brep')
    volume = tool.common(wire).Volume
    assert abs(volume-row['hit_mm3']) < 1e-5 and volume > 1e-5
    result = copy.deepcopy(prior)
    result.update(status='NOMINAL_LOCAL_FEED_PAIR_WITH_ASSEMBLY_ACCESS_CONDITION',
        hits=[], tool_access_contacts=prior['tool_access_contacts']+[row],
        parent_check=PARENT.relative_to(ROOT).as_posix(), parent_check_sha256=sha(PARENT),
        parent_script_sha256=prior['script_sha256'], script_sha256=sha(Path(__file__)),
        fresh_recheck=dict(tool=tool_path, wire=wire_path, hit_mm3=volume),
        fresh_pairs=1, inherited_pairs=prior['pairs'],
        scope='Unchanged physical geometry; inherited pinned R2 screen plus one temporary-tool recheck. R2 failure preserved.',
        assembly_access_condition='Install and tighten bridge before routing XB22/XB23 head feeds and W061. Both W061 segments3/4 cross the right tool corridor. Later access requires disconnected battery and released/parked affected stationary wires; restore all selected routes and ties. No installed-wire tool clearance claimed.',
        started_utc=start.isoformat(), finished_utc=datetime.now(timezone.utc).isoformat())
    result['worker_wall_seconds']=(datetime.now(timezone.utc)-start).total_seconds()
    save(OUT/'checks.json',result)
    print(json.dumps(dict(status=result['status'],physical_hits=0,tool_contacts=len(result['tool_access_contacts']),fresh_pairs=1,seconds=result['worker_wall_seconds'])),flush=True)


if __name__ == '__main__': main()
