"""One final local closure after matched service Guard and whole R14."""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_construction_checkpoint_r32.py')
raw=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
ns=dict(__file__=str(parent),__name__='r32_definition');exec(compile(raw.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-construction-checkpoint-r30/manifest.json','servo-fuse-construction-checkpoint-r33/manifest.json')
code=code.replace('servo-fuse-bank-fixed-rr-lift-r13','servo-fuse-bank-fixed-rr-lift-r14').replace('servo-fuse-bank-stock-budget-r9','servo-fuse-bank-stock-budget-r10').replace('servo-fuse-bank-assembly-r8','servo-fuse-bank-assembly-r9')
code=code.replace('servo-fuse-construction-checkpoint-r32','servo-fuse-construction-checkpoint-r34').replace('LOCAL_BANK_R32_COMPLETE','LOCAL_BANK_R34_COMPLETE')
code=code.replace('    add(Path(__file__))',"""    serviceguard=read('hardware/electronics/full-cat/servo-fuse-guard-fixed-service-r1/checks.json')
    for row in serviceguard['exports']:
        gp=ROOT/row['file'];add(gp);add(gp.parent/'Guard_WORLD.brep');add(gp.parent/'Guard_UNSELECTED.stl')
    m['Fixed_guard_service']=dict(source='hardware/electronics/full-cat/servo-fuse-guard-fixed-service-r1/checks.json',exports=serviceguard['exports'],preserved=serviceguard['preserved_zones'])
    for name in ('servo_fuse_bank_stock_budget_r10.py','servo_fuse_bank_assembly_r9.py','servo_fuse_bank_select_r5.py','servo_fuse_bank_fixed_rr_lift_r14.py'):add(ROOT/'tools/electronics'/name)
    add(Path(__file__))""")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
