"""Cheap integrity gate for an already saved checkpoint; never rebuild CAD."""
from pathlib import Path
import json
import hashlib

ROOT=Path(__file__).resolve().parents[2]
PACKAGE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    plan=json.loads((PACKAGE/'layout.json').read_text(encoding='utf-8'))
    assert all(digest(ROOT/path)==expected for path,expected in plan['source_sha256'].items())
    assert digest(ROOT/plan['native'])==plan['native_sha256']
    assert plan['saved_reopen'] and plan['topology_unchanged']
    rows=plan['body_conductors']
    assert len(rows)==len({r['id'] for r in rows})==80
    assert sum(r['bound_end_count'] for r in rows)==plan['bound_body_ends']==122
    assert len(plan['distribution_boundary'])==80
    assert len(plan['missing_body_endpoint_roles'])==38
    assert plan['result_count']==3 and plan['result_denominator']==20
    assert not any(plan[key] for key in ['selected','physical_pass','W1_complete','W5_complete','print_selection_complete'])
    proof=plan['F_PI_output_proof']
    assert not proof['contacts'] and not proof['errors']
    assert proof['exact_pairs_tested']==2
    assert plan['F_PI_factory_splice_budget']['available_margin_mm']>0
    print('Integrity PASS: 13 source pins + native, 80 IDs, 122 ends, 38 open roles; no result inflation')
    print('Route helper at verification:',digest(ROOT/'tools/cad/whole_cat_source_bay_plan.py'))


if __name__=='__main__':main()
