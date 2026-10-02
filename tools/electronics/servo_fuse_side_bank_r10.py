"""R9 input route plus10mm straight insulated grip before each TE end.

Lower only the outside turnaround; keep holder datums/WAGO fan/mounts.
Current bank/output/cover/bracket geometry is included, not old prototypes.
"""
from pathlib import Path
base=Path(__file__).with_name('servo_fuse_side_bank_r8.py')
code=base.read_text(encoding='utf-8')
code=code.replace('servo-fuse-side-bank-r8','servo-fuse-side-bank-r10')
code=code.replace("if side==1 and base==-69 and i==1:cx-=3",
    "if side==1 and base==-69 and i==1:cx-=3\n                if side==1 and base==-69 and i==2:cx+=6")
code=code.replace("if leg=='FL' and index==2:cx-=3",
    "if leg=='FL' and index==2:cx-=3\n        if leg=='FL' and index==3:cx+=6")
code=code.replace('line(A.Vector(p.x,p.y,end[2]));arc(dz,u,math.pi/2)',
    'line(A.Vector(p.x,p.y,end[2]-10));arc(dz,u,math.pi/2)')
code=code.replace('line(A.Vector(p.x,side*stop,p.z));arc(u,up,math.pi/2)',
    'line(A.Vector(p.x,side*stop,p.z));arc(u,up,math.pi/2);line(A.Vector(*end))')
code=code.replace('return owners, hashes, removed', '''
    cover_key='hardware/cad/studies/head-yaw-end-restraints-r1/CoverYawEndSeat.brep'
    owners[cover_key]=load(ROOT/'hardware/cad/studies/servo-fuse-cover-native-r3/Cover_WORLD.brep')
    for folder,pattern in [('hardware/cad/studies/servo-fuse-bank-restraints-r2','*_WORLD.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-bank-outputs-r1','*_LOCAL_DESIGN.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-bank-restraints-r2','*_TIE_DESIGN.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-bank-restraints-fit-r2','*_TIE_HEAD_RESERVE.brep'),
                           ('hardware/electronics/full-cat/servo-fuse-cover-neighbors-r1','CoverBracket_*.brep')]:
        for p in (ROOT/folder).glob(pattern):owners[folder+'/'+p.stem]=load(p)
    return owners, hashes, removed''')
begin=code.index('    for side in (-1,1):\n        # Panel top')
end=code.index('    for row in rows:',begin)
code=code[:begin]+code[end:]
code=code.replace('for n,s in {**holders,**terminals,**mounts,**wires}.items():',
    'for n,s in {**terminals,**wires}.items():')
code=code.replace('planned_required_blank_mm=sum(', 'straight_grip_before_terminal_mm=10,planned_required_blank_mm=sum(')
code=code.replace("source_sha256={ledger.relative_to(ROOT).as_posix():sha(ledger)}",
    "source_sha256={ledger.relative_to(ROOT).as_posix():sha(ledger),'tools/electronics/servo_fuse_side_bank_r8.py':sha(ROOT/'tools/electronics/servo_fuse_side_bank_r8.py')}")
code=code.replace('R6/R7 located upper feeds, S0foot and PWM shelf.',
    'R9 position retained; lower only outside turnaround10mm and add10mm straight grip. Actual bank/cover/output/brackets included.')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
