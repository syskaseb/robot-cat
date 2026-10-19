"""Keep measured distances; recheck complete pairs affected by tie/tie rule.

This never turns a failed pair into PASS. Its first failing witness is retained
in history and the WHOLE pair goes back to exact checking. Rigid/bare margins
and actual distance algorithm stay unchanged.
"""
import ast
import json
import subprocess
from pathlib import Path
import FreeCAD
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json
from feline_fore_power_pair import pair_spacing


def requires_recheck(rec):
    if rec['ok'] or not rec.get('pairs'):return False
    last=rec['pairs'][-1];a,b=last['part'],last['other']
    if not all('band_budget' in n or 'head_budget' in n or 'Tie' in n for n in (a,b)):return False
    minimum=pair_spacing('Current:'+a,dict(kind='project_stock_reservation'),'Current:'+b,dict(kind='project_stock_reservation'))
    return minimum<last['minimum_mm'] and minimum-1e-6<=last['gap_mm']<last['minimum_mm']-1e-6


def main():
    path=ROOT/'tools/cad/feline_fore_power_pair.py'
    old=subprocess.run(['git','show','68c104d7:tools/cad/feline_fore_power_pair.py'],cwd=ROOT,check=True,capture_output=True).stdout
    get=lambda text,name:next(n for n in ast.walk(ast.parse(text)) if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name==name)
    assert ast.dump(get(old,'SolidQueries'))==ast.dump(get(path.read_text(),'SolidQueries'))
    for name,field in (('n01-shared54-whole.json','mutual_cache'),('n01-bank-whole-preflight.json','pairs')):
        p=OUT/name;doc=json.loads(p.read_text());cache=doc[field]
        changed={code:rec for code,rec in cache.items() if requires_recheck(rec)}
        if not changed:continue
        history=doc.setdefault('soft_stock_policy_rechecks',[])
        history.append(dict(old_measured_negative_pairs=changed,
            reason='Documented soft nylon .2mm reserve now includes tie/tie; rigid/bare remain1.25. COMPLETE pairs must be rechecked, not auto-passed',
            classifier_sha256=sha(path),distance_class_AST_unchanged=True))
        for code in changed:del cache[code]
        doc['cuts']=[pair for pair in doc['cuts'] if '|'.join(sorted(pair)) not in changed]
        save_json(p,doc);print(name,'complete pairs queued for recheck',len(changed))


if __name__=='__main__':main()
