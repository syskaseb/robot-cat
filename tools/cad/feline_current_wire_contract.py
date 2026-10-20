"""The working whole-wire contract: pinned profile table + typed bend delta.

Existing generic12.4mm is not a manufacturer requirement. Explicit retained
HELU25.2 and fixed-logic .5/6/10mm recipes govern their own selected wires.
No existing CAD evidence or immutable source contract is overwritten.
"""
import json,time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT,BASE
from feline_atomic_save import save_json


def load():
    source=OUT/'n01-whole-wire-profile-contract.json';delta=OUT/'n01-selected-wire-bend-delta.json'
    result=json.loads(source.read_text());d=json.loads(delta.read_text())
    for p,h in d['source_sha256'].items():assert sha(ROOT/p)==h,p
    for name,change in d['updates'].items():result['portions'][name]=dict(result['portions'][name],**change)
    return result,source,delta


def main():
    tick=time.monotonic();pf=OUT/'n01-whole-wire-profile-contract.json';profiles=json.loads(pf.read_text())
    hf=ROOT/'hardware/reference/parent-fuse-extensions-2026-10-03/facts.json';helu=json.loads(hf.read_text())['HELU23802']
    uf=BASE/'body-harness-checkpoint/u1-common-wiring-plan.json';common=json.loads(uf.read_text())['routes'];updates={}
    for name,r in profiles['portions'].items():
        if 'project_radius_mm' not in r:continue
        R=None;basis=None
        if (r.get('selected_material') or '').startswith('HELU23802'):
            R=helu['routing_radius_mm'];basis='Existing selected HELU project routing radius; same bought conductor'
        elif r['wire'] in common:
            R=common[r['wire']]['source']['project_radius_mm'];basis='Existing selected whole fixed logic recipe; not generic12.4 fallback'
        if R is not None:
            updates[name]=dict(minimum_project_R_mm=R,typed_bend_basis=basis,diameter_contract_unchanged=True)
    assert updates['W066/retained0']['minimum_project_R_mm']==25.2
    assert updates['XS11/extra']['minimum_project_R_mm']==.5
    result=dict(status='EXPLICIT_SELECTED_BENDS_OVERLAY_GENERIC_DEFAULTS_NOT_NEW_SKUS',updates=updates,
        supplier_minimum_bend_not_claimed=True,N01_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (pf,hf,uf,Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-selected-wire-bend-delta.json',result)
    print(json.dumps(dict(changed_rows=len(updates),HELU_R=25.2,fixed_logic_source_R=[.5,6,10],seconds=result['worker_seconds'])))


if __name__=='__main__':main()
