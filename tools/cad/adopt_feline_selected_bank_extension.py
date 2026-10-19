"""Prove retained selected-head recipes before adding one shared bank plan."""
import hashlib
import json
import subprocess
from pathlib import Path
import FreeCAD
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_remaining_kits import candidates
from feline_atomic_save import save_json


def main():
    file=ROOT/'tools/cad/feline_bank_selected_t18i.py';rel=file.relative_to(ROOT).as_posix()
    oldtext=subprocess.run(['git','show','3fe59048:'+rel],cwd=ROOT,check=True,capture_output=True).stdout
    old={'__name__':'pinned_selected_bank'};new={'__name__':'extended_selected_bank'}
    exec(compile(oldtext,'pinned_selected_bank','exec'),old);exec(compile(file.read_text(),'extended_selected_bank','exec'),new)
    groups,_=candidates();before=old['candidates'](groups);after=new['candidates'](groups);count=0
    for group,rows in before.items():
        for r in rows:
            assert r in after[group]
            aa,ak=old['materialise'](group,r);bb,bk=new['materialise'](group,r);assert ak==bk
            for n,s in aa.items():
                t=bb[n]
                if s.exportBrepToString()!=t.exportBrepToString():
                    for difference in (s.copy().cut(t.copy()),t.copy().cut(s.copy())):
                        assert difference.isNull() or difference.isValid()
                        assert difference.Volume<1e-7,(group,n)
            count+=1
    dest=OUT/'n01-bank-whole-preflight.json';doc=json.loads(dest.read_text())
    assert doc['source_sha256'][rel]==hashlib.sha256(oldtext).hexdigest()
    doc.setdefault('additive_receipt_repairs',[]).append(dict(reason='Shared opposed return gallery BELOW bank; all prior complete selected-head recipes geometrically identical',preserved_complete_recipes=count,old_sha256=doc['source_sha256'][rel],new_sha256=sha(file)))
    doc['source_sha256'][rel]=sha(file);save_json(dest,doc)
    print('Preserved actual complete material of',count,'selected-head recipes')


if __name__=='__main__':main()
