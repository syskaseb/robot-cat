"""Correct R1's filled-gap probe and obey the existing removed-Deck sequence.

R1's union bounding box filled the empty volume underneath each lip, causing
eight spurious body/roof contacts. Sweep column and lip separately. Cover
actually obstructs three top approaches: access is AFTER removing bank+Cover
together, not an independent vertical Cover removal. Whole bank release still
requires its own proof. Preserve all R1 witnesses; change no physical part.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rr_clip_approach_r1.py')
code=parent.read_text(encoding='utf-8').replace('servo-fuse-rr-clip-approach-r1','servo-fuse-rr-clip-approach-r2')
code=code.replace("    pins = {}", "    pins = {}\n    pins['tools/electronics/servo_fuse_rr_clip_approach_r1.py']=sha(ROOT/'tools/electronics/servo_fuse_rr_clip_approach_r1.py')\n    p=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-clip-approach-r1/checks.json';pins[p.relative_to(ROOT).as_posix()]=sha(p)")
code=code.replace("    folder = ROOT / 'hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r3'", """    removed_module=[]
    for key in ('ModifiableCover','Bank/RightClipAccessFinished_WORLD','Bank/LeftClipAccessFinished_WORLD'):
        assert key in owners
        del owners[key];removed_module.append(key)
    folder = ROOT / 'hardware/electronics/full-cat/servo-fuse-rear-output-stations-native-r3'""")
a=code.index('            cb, lb =');b=code.index('            nominal_motion.exportBrep',a)
code=code[:a]+'''            # Keep the empty space between the column and top lip empty.
            # These are exact rigid translation sweeps of each separate box,
            # conservative for the stated nominal outward bend allowance.
            sweeps=[]
            for key in ('column_mm','lip_mm'):
                q=list(clip[key]);q[0 if side=='L' else 3] += -3.4 if side=='L' else 3.4
                sweeps.append(box(q))
            nominal_motion=sweeps[0].fuse(sweeps[1])
''' +code[b:]
code=code.replace("fixture_change=False, probes=probes", "fixture_change=False, removed_module_before_tool_access=removed_module,\n        sequence_scope='Build/release RR main holder on unpowered removed Deck, AFTER bank+Cover have been removed together. Does not establish that bank release itself is possible.',\n        prior_R1_false_contacts='Eight filled-gap bounds under lip, not actual native-part interference; three Cover approach contacts remain real for the assembled state.',\n        probes=probes")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
