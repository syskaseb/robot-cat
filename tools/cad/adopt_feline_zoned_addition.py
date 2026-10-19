"""Adopt ONE additional bank zone without invalidating unchanged receipts.

All old recipes must survive verbatim, their zone results stay identical,
and both geometry-constructor ASTs stay identical. Otherwise refuse.
No negative receipt is removed and no clearance threshold changes.
"""
import ast
import hashlib
import json
import subprocess
from pathlib import Path
import FreeCAD
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_remaining_kits import candidates as source_candidates
from feline_atomic_save import save_json


HELPER='tools/cad/feline_bank_zoned_layout.py'


def prove(old_text,new_text,groups):
    get=lambda t,n:next(v for v in ast.walk(ast.parse(t)) if isinstance(v,ast.FunctionDef) and v.name==n)
    for n in ('profile','materialise'):
        assert ast.dump(get(old_text,n))==ast.dump(get(new_text,n)),n
    old={'__name__':'pinned_old_zoned'};new={'__name__':'pinned_new_zoned'}
    exec(compile(old_text,'pinned_old_zoned','exec'),old)
    exec(compile(new_text,'pinned_new_zoned','exec'),new)
    before=old['candidates'](groups);after=new['candidates'](groups)
    assert set(after)-set(before)=={'Bank:W029/single/end'}
    for g,rows in before.items():
        assert rows==after[g],g
        for r in rows:assert old['zone'](g,r['base_recipe'])==new['zone'](g,r['base_recipe']),g
    return before,after


def main():
    old=subprocess.run(['git','show','c5f0bd35:'+HELPER],cwd=ROOT,check=True,capture_output=True).stdout
    oldsha=hashlib.sha256(old).hexdigest();newsha=sha(ROOT/HELPER)
    groups,_=source_candidates();before,after=prove(old,(ROOT/HELPER).read_text(),groups)
    files=[OUT/'n01-shared54-whole.json',OUT/'n01-bank-zoned-static.json']
    pending=[]
    for p in files:
        doc=json.loads(p.read_text());pins=doc['source_sha256']
        assert pins[HELPER]==oldsha,(p,pins[HELPER])
        assert all(sha(ROOT/n)==h for n,h in pins.items() if n!=HELPER)
        if 'units' in doc:
            assert all(r['recipe'] in before[r['group']] for r in doc['units'].values())
        doc.setdefault('additive_receipt_repairs',[]).append(dict(
            reason='Only W029 joins already planned upper gallery above FULL P_SYS grip',
            old_helper_sha256=oldsha,new_helper_sha256=newsha,
            preserved_recipe_groups=len(before),new_recipe_groups=len(after)-len(before),
            profile_and_materialise_AST_identical=True,all_prior_zone_outputs_identical=True,
            all_positive_and_negative_receipts_retained=True))
        doc['source_sha256'][HELPER]=newsha;pending.append((p,doc))
    for p,doc in pending:save_json(p,doc)
    print('Adopted exactly1 additional zone; all10 prior zone recipes/shapes/receipts preserved')


if __name__=='__main__':main()
