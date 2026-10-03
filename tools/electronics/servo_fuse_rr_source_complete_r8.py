"""RR R7 unchanged against the lower RL R3 construction candidate.

Old inherited RL extension crosses R7 RR. R3 is one whole matched RL
factory/lap/source candidate, not a mix of endpoints; it still has fixed
contacts and is NOT selected. Qualify changed RR interfaces against it,
record both statuses separately. No whole-pair/W5 completion is inferred.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rr_source_complete_r7.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'))
code=code.replace("servo-fuse-rr-source-complete-r7'","servo-fuse-rr-source-complete-r8'")
code=code.replace("if not p.stem.startswith(affected):owners['OtherFeed/'+p.stem]=load(p)",
    "if not p.stem.startswith(('W044','W052')):owners['OtherFeed/'+p.stem]=load(p)")
code=code.replace('    fixed={n:bounds(s)', '''    rl_folder=ROOT/'hardware/electronics/full-cat/servo-fuse-rear-source-pair-r3'
    p=rl_folder/'checks.json';pin(p);rl_candidate=json.loads(p.read_text(encoding='utf-8'))
    for p in rl_folder.glob('W044*_DESIGN.brep'):owners['RL_R3_CANDIDATE/'+p.stem]=load(p)
    save(OUT/'RL-status.json',dict(selected=False,physical_pass=False,
        candidate='servo-fuse-rear-source-pair-r3',accepted=False,
        fixed_contacts=[h for h in rl_candidate['hits'] if h['part'].startswith('W044') and not h['owner'].startswith('W052')],
        reason='Self-consistent lower RL candidate only; native RR fit does NOT qualify these known RL contacts.'))
    fixed={n:bounds(s)''')
code=code.replace("    pin(parent);pin(src);", "    pin(parent);pin(src);pin(ROOT/'hardware/electronics/full-cat/servo-fuse-rr-source-complete-r7/checks.json');")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
