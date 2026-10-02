"""R1 extra7mm³ contact: relieve only FL2's upper rib by0.8mm to head tongue."""
from pathlib import Path
base=Path(__file__).with_name('servo_fuse_bank_restraints_r1.py')
code=base.read_text(encoding='utf-8').replace('servo-fuse-bank-restraints-r1','servo-fuse-bank-restraints-r2')
code=code.replace('cutters.append(groove)', """cutters.append(groove)
                if n=='W022':
                    cutters.append(block('FL2HeadSeatClearance',[x+2.2,133,134,x+4.2,137,140]))""")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
