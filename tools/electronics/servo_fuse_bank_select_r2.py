"""Validate quantities at the same granularity as inherited offer bindings.

Parent supplier:Kamami:1188363 aggregates16pieces from several roles; one
product_binding describes its4piece role, not an erroneous whole-row16.
Only compare a binding's quantity to a row when their identity is equal.
No unrelated inherited quantities or SKU evidence are silently rewritten.
"""
from pathlib import Path
parent=Path(__file__).with_name('servo_fuse_bank_select_r1.py')
code=parent.read_text(encoding='utf-8')
old="if 'product_binding' in r:assert r['planning_quantity']==r['product_binding']['planning_quantity'],r['id']"
assert old in code
code=code.replace(old,"if 'product_binding' in r and r['id']==r['product_binding']['quantity_id']:assert r['planning_quantity']==r['product_binding']['planning_quantity'],r['id']")
exec(compile(code,str(Path(__file__).resolve()),'exec'))
