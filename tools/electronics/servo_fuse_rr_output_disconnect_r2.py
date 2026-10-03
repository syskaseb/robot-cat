"""RR disconnect after taking out mini holders, before raising the bank.

The family installation drawing shows an upright lever, so90deg is the
PROJECT open position. R1's110deg reserve collided with retained terminals;
do not call that larger reserve clear or assert a manufacturer's stop angle.
Keep terminal ends and all wire paths in the check. Remove only12holder
bodies/12ATOs, as required by the normal bank-removal sequence anyway.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_rr_output_disconnect_r1.py')
code=parent.read_text(encoding='utf-8').replace('servo-fuse-rr-output-disconnect-r1','servo-fuse-rr-output-disconnect-r2')
code=code.replace('import json, math, sys','import json, math, sys, re')
code=code.replace('    V=A.Vector','''    prior=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-disconnect-r1/checks.json'
    pins[prior.relative_to(ROOT).as_posix()]=sha(prior)
    pins['tools/electronics/servo_fuse_rr_output_disconnect_r1.py']=sha(ROOT/'tools/electronics/servo_fuse_rr_output_disconnect_r1.py')
    removed_holders=[]
    for key in list(owners):
        if re.fullmatch(r'R11/F_(FL|FR|RL|RR)[123]_(ATO_)?DESIGN',key):
            removed_holders.append(key);del owners[key]
    assert len(removed_holders)==24,removed_holders
    V=A.Vector''')
code=code.replace('opening_degrees=110','opening_degrees=90')
code=code.replace('a,m,b=point(0),point(55),point(110)','a,m,b=point(0),point(45),point(90)')
code=code.replace('fixture_change=False,','fixture_change=False,removed_holder_and_ATO_shapes=removed_holders,')
code=code.replace("sequence='Battery absent, cut/release", "sequence='Battery absent, unmate twelve mini holders after removing their ATOs; keep TE ends on current axes. Then cut/release")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
