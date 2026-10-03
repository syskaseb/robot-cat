"""Close local checkpoint only after actual R17 and one selected R52."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_construction_checkpoint_r36.py')
code=parent.read_text(encoding='utf-8')
for a,b in [('servo-fuse-construction-checkpoint-r35','servo-fuse-construction-checkpoint-r37'),
            ('servo-fuse-construction-checkpoint-r36','servo-fuse-construction-checkpoint-r38'),
            ('servo-fuse-bank-fixed-rr-lift-r15','servo-fuse-bank-fixed-rr-lift-r17'),
            ('servo-fuse-bank-stock-budget-r11','servo-fuse-bank-stock-budget-r12'),
            ('servo-fuse-bank-assembly-r10','servo-fuse-bank-assembly-r11'),
            ('servo_fuse_bank_stock_budget_r11.py','servo_fuse_bank_stock_budget_r12.py'),
            ('servo_fuse_bank_assembly_r10.py','servo_fuse_bank_assembly_r11.py'),
            ('servo_fuse_bank_select_r6.py','servo_fuse_bank_select_r7.py'),
            ('servo_fuse_bank_fixed_rr_lift_r15.py','servo_fuse_bank_fixed_rr_lift_r17.py')]:
    assert a in code,a
    code=code.replace(a,b)
exec(compile(code,str(Path(__file__).resolve()),'exec'))
