"""Repair the four hip exits and four overlapping knee bends as one layout.

Retain the four clear ankle corridors from R1 byte-pinned saved geometry.
R1 hip hits are FrontRearCover001/003, not permission to modify bought servos.
The editable hip plug projection is10mm; actual connector fit stays phase2.
"""
from pathlib import Path
parent = Path(__file__).with_name('w5_leg_corridors_r1.py')
code = parent.read_text(encoding='utf-8')
code = code.replace("w5-leg-corridors-r1'", "w5-leg-corridors-r2'", 1)
code = code.replace('start=p+direction*8; lead=start+direction*40',
    "projection=10 if row['loom'].endswith('1') else 8\n        start=p+direction*projection; lead=start+direction*40")
code = code.replace("y=side*(108+12*int(row['loom'][2]))",
    "y=side*(108+12*int(row['loom'][2]))\n        if row['loom'].endswith('2'): y=side*max(side*y,side*lead.y+25)")
code = code.replace('cable_exit_projection_assumption_mm=8', 'cable_exit_projection_assumption_mm=projection')
marker='    owners,cache=cached()'
assert code.count(marker)==1
code=code.replace(marker,"""    previous_folder=ROOT/'hardware/electronics/full-cat/w5-leg-corridors-r1'
    previous=json.loads((previous_folder/'checks.json').read_text(encoding='utf-8'))
    assert previous['status']=='LEG_CORRIDORS_REJECTED'
    assert len(previous['hits'])==4 and all(h['loom'].endswith('1') for h in previous['hits'])
    assert len(previous['errors'])==4 and all(h['loom'].endswith('2') for h in previous['errors'])
    assert all(sha(ROOT/k)==v for k,v in previous['files'].items())
    previous_plans=json.loads((previous_folder/'intent.json').read_text(encoding='utf-8'))['routes']
    previous_paths=Part.read(str(previous_folder/'CENTERLINES_WORLD.brep')).childShapes()
    previous_bundles=Part.read(str(previous_folder/'CORRIDORS_WORLD.brep')).childShapes()
    assert len(previous_paths)==len(previous_bundles)==len(previous['routes'])==8
    previous_indices={r['loom']:i for i,r in enumerate(previous['routes'])}
    for r in planned:
        if r['loom'].endswith('3'):
            assert r['waypoints_mm']==next(p['waypoints_mm'] for p in previous_plans if p['loom']==r['loom'])
"""+marker)
marker="    for row in planned:\n        try:"
assert code.count(marker)==1
code=code.replace(marker,"""    for row in planned:
        if row['loom'].endswith('3'):
            index=previous_indices[row['loom']]
            paths.append(previous_paths[index]);bundles.append(previous_bundles[index])
            rows.append(previous['routes'][index])
            print('LEG_INHERITED_UNCHANGED',row['loom'],flush=True)
            continue
        try:""")
old="        for j,b in enumerate(bundles[i+1:],i+1):check(rows[i]['loom'],None,a,rows[j]['loom'],b)"
assert code.count(old)==1
code=code.replace(old,"""        for j,b in enumerate(bundles[i+1:],i+1):
            if rows[i]['loom'].endswith('3') and rows[j]['loom'].endswith('3'):continue
            check(rows[i]['loom'],None,a,rows[j]['loom'],b)""")
marker="    save(OUT/'checks.json',dict(status="
assert code.count(marker)==1
code=code.replace(marker,"""    pins += [ROOT/'tools/electronics/w5_leg_corridors_r1.py',previous_folder/'checks.json',previous_folder/'intent.json',previous_folder/'CENTERLINES_WORLD.brep',previous_folder/'CORRIDORS_WORLD.brep']
"""+marker)
code=code.replace('routes=rows,hits=hits,errors=errors,pairs=pairs,source_sha256=',
    "inherited_unchanged_looms=['FL3','FR3','RL3','RR3'],routes=rows,hits=hits,errors=errors,pairs=pairs,source_sha256=")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
