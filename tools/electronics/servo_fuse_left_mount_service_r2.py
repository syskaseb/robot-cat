"""Exact foot boundary restores the0.1mm post join, same proven footprint.

R1 has0changed contacts/full bearing/continuous foot100mm, but2solids due
to overcut at113.1. Reuse only its unchanged foot/hardware/envelope checks;
check restored actual post sliver against both tools and final strict BOP.
Whole-module release remains OPEN, not inherited from this delta proof.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_left_mount_service_r1.py')
code=parent.read_text(encoding='utf-8').replace('servo-fuse-left-mount-service-r1','servo-fuse-left-mount-service-r2')
code=code.replace('108.9,-47.9,97.1,113.1','108.9,-47.9,97.1,113.0')
begin=code.index('    # Small hardware is checked')
end=code.index('    state=dict(',begin)
code=code[:begin]+"""    priorpath=ROOT/'hardware/electronics/full-cat/servo-fuse-left-mount-service-r1/checks.json'
    pins[priorpath.relative_to(ROOT).as_posix()]=sha(priorpath);prior=json.loads(priorpath.read_text(encoding='utf-8'))
    assert not prior['hits'] and not prior['errors'] and prior['washer_bearing_missing_mm3']<1e-5
    assert prior['state']['solids']==2 and prior['new_foot_mm']==footbox and prior['new_axis_mm']==axis
    for rel,h in prior['source_sha256'].items():assert pins.get(rel,h)==h,rel
    oldcandidate=Part.read(str(priorpath.parent/'BankLeft_CANDIDATE.brep'))
    pins[(priorpath.parent/'BankLeft_CANDIDATE.brep').relative_to(ROOT).as_posix()]=sha(priorpath.parent/'BankLeft_CANDIDATE.brep')
    restored=candidate.cut(oldcandidate);assert restored.Volume>0
    assert restored.cut(bank).Volume<1e-5
    assert abs(restored.BoundBox.ZMin-113)<1e-5 and abs(restored.BoundBox.ZMax-113.1)<1e-5
    for k,t in tools.items():check('restored_original_post_join_tool_access','PostJoin',restored,k,t)
    reused=prior['pairs']
"""+code[end:]
code=code.replace('hits=hits,errors=errors,pairs=pairs,','hits=hits,errors=errors,pairs=pairs,unchanged_delta_pairs_reused=reused,restored_original_post_mm3=restored.Volume,')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
