"""Correct physical feed-tie count:20 BRep fragments represent FOUR ties.

Preserve R2 as superseded candidate, not a selected installed census.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_stock_budget_r2.py')
code=parent.read_text(encoding='utf-8')
assert "installed=20" in code and "== 65" in code
code=code.replace('servo-fuse-bank-stock-budget-r2','servo-fuse-bank-stock-budget-r3')
code=code.replace("    tie_groups = [", """    pins['tools/electronics/servo_fuse_bank_stock_budget_r2.py']=sha(ROOT/'tools/electronics/servo_fuse_bank_stock_budget_r2.py')
    grip=read('hardware/electronics/full-cat/servo-fuse-parent-feed-grips-native-r2/checks.json')
    assert grip['grips']==4 and grip['through_slots']==8
    tie_groups = [""")
code=code.replace("role='fixed_lower_input_feeds', installed=20", "role='fixed_lower_input_feeds', installed=4")
code=code.replace('== 65','== 49').replace('local_installed_known=65','local_installed_known=49').replace('local_ties=65','local_ties=49')
code=code.replace("replaces='servo-fuse-bank-stock-budget-r1; never add its1080mm/old splice count to this ledger.'", "replaces='stock-r2 superseded:20 geometric feed-tie pieces were incorrectly counted as20 ties; four complete physical loops. Replace stock-r1 old1080mm totals too, never add revisions.'")
code=code.replace("local_installed_known=49,", "local_installed_known=49, feed_tie_BRep_fragments=20, feed_tie_physical_loops=4,")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
