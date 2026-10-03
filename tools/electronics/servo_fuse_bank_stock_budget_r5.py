"""Both FR source ties now stay with fixed Deck; removal allowance returns24.

Do not add twelve replacement output loops to installed count or buy another
stock package. This remains a local candidate until bank selection.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_stock_budget_r4.py')
wrapper=parent.read_text(encoding='utf-8');tail="exec(compile(code,str(Path(__file__).resolve()),'exec'))"
assert wrapper.rstrip().endswith(tail)
ns=dict(__file__=str(parent),__name__='stock_r4_definition_only')
exec(compile(wrapper.rstrip()[:-len(tail)],str(parent),'exec'),ns)
code=ns['code'].replace('servo-fuse-bank-stock-budget-r4','servo-fuse-bank-stock-budget-r5')
code=code.replace("role='FR_RL_RR_source_insulation', installed=6, removal_replacements=2","role='FR_RL_RR_source_insulation', installed=6, removal_replacements=0")
code=code.replace('local_removal_replacement_allowance=26','local_removal_replacement_allowance=24').replace('FR_source_loops_cut=2','FR_source_loops_cut=0')
code=code.replace("    tie_groups = [", """    station=read('hardware/electronics/full-cat/servo-fuse-fr-source-fixed-deck-native-r2/checks.json')
    assert len(station['exports'])==3 and all(r['relocated_reopen'] for r in station['exports'])
    assert station['source_ties_owner']=='FIXED_DECK'
    pins['tools/electronics/servo_fuse_bank_stock_budget_r4.py']=sha(ROOT/'tools/electronics/servo_fuse_bank_stock_budget_r4.py')
    tie_groups = [""")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
