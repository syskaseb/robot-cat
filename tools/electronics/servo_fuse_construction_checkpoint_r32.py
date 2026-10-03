"""Final local closure using actual R13/R52 only, not withdrawn R12."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_construction_checkpoint_r31.py')
code=parent.read_text(encoding='utf-8')
code=code.replace('servo-fuse-bank-fixed-rr-lift-r12','servo-fuse-bank-fixed-rr-lift-r13').replace('servo-fuse-bank-stock-budget-r8','servo-fuse-bank-stock-budget-r9').replace('servo-fuse-bank-assembly-r7','servo-fuse-bank-assembly-r8')
code=code.replace('servo-fuse-construction-checkpoint-r31','servo-fuse-construction-checkpoint-r32').replace('LOCAL_BANK_R31_COMPLETE','LOCAL_BANK_R32_COMPLETE')
code=code.replace('    add(Path(__file__))',"    for name in ('servo_fuse_bank_stock_budget_r9.py','servo_fuse_bank_assembly_r8.py','servo_fuse_bank_select_r4.py','servo_fuse_bank_fixed_rr_lift_r13.py'):add(ROOT/'tools/electronics'/name)\n    add(Path(__file__))")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
