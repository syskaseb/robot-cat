"""Same49 installed ties; replace12 output loops, cut2 FR source loops.

This supersedes the removal allowance, not the entire local selection.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_stock_budget_r3.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='stock_r3_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-stock-budget-r3','servo-fuse-bank-stock-budget-r4')
code=code.replace("    tie_groups = [", """    pins['tools/electronics/servo_fuse_bank_stock_budget_r3.py']=sha(ROOT/'tools/electronics/servo_fuse_bank_stock_budget_r3.py')
    clamps=read('hardware/electronics/full-cat/servo-fuse-output-clamps-fit-r1/checks.json')
    assert clamps['checked_clamps']==12 and not clamps['hits'] and not clamps['errors']
    tie_groups = [""")
code=code.replace("role='FR_RL_RR_source_insulation', installed=6, removal_replacements=0", "role='FR_RL_RR_source_insulation', installed=6, removal_replacements=2")
code=code.replace('local_removal_replacement_allowance=24','local_removal_replacement_allowance=26, output_loops_reoriented_not_added=12, FR_source_loops_cut=2')
exec(compile(code,str(Path(__file__).resolve()),'exec'))
