"""One profile per physical portion, selected material before local CAD caps.

Caps are observations of the current CAD, not authority to thin selected
wire. Keep factory portions intact and unresolved dimensions provisional.
"""
import csv,gzip,json,time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT,BASE
from feline_atomic_save import save_json


def governing_radius(budget,actual,selected=None):
    values=([budget] if selected is None else [selected])+list(actual)
    return max(v for v in values if v is not None)


def main():
    tick=time.monotonic();ef=OUT/'n01-shared-routing-boundaries.json';reg=json.loads(ef.read_text());ends={e['id']:e for e in reg['endpoints']}
    nf=OUT/'n01-current-corridor-topology.json';network=json.loads(nf.read_text());af=ROOT/network['assignments']
    assert sha(af)==network['assignments_sha256'];assignments=json.loads(gzip.decompress(af.read_bytes()))
    cf=OUT/'n01-current-source-cap-profiles.json';caps=json.loads(cf.read_text())['rows']
    mf=ROOT/'hardware/electronics/full-cat/body-harness-w5-r2/wire-cuts.csv'
    materials={r['id']:r for r in csv.DictReader(mf.open(encoding='utf-8-sig',newline=''))}
    hf=ROOT/'hardware/reference/parent-fuse-extensions-2026-10-03/facts.json';helu=json.loads(hf.read_text())['HELU23802']
    uf=BASE/'body-harness-checkpoint/u1-common-wiring-plan.json';common=json.loads(uf.read_text())['routes']
    rows={};mismatches=[]
    for name,ids in reg['portions'].items():
        wire=ends[ids[0]]['wire'];basewire=wire.split('/')[0];a=assignments[name]
        if a['status']=='RECEIVED_COMPLETE_UNCHANGED_CURVE':
            rows[name]=dict(status='RETAINED_WHOLE_FACTORY_OR_SELECTED_CURVE_NOT_REPROFILED',wire=wire);continue
        budget=a['radius_mm'];actual=[caps[e]['actual_project_radius_mm'] for e in ids if e in caps and caps[e]['actual_project_radius_mm'] is not None]
        material=materials.get(basewire,{}).get('material');selected=None;basis='Conservative existing portion envelope plus actual source caps'
        if material and material.startswith('HELU23802'):
            selected=helu['routing_OD_mm']/2;basis='Retained selected HELU23802 project material OD; not smaller local CAD cap'
        elif wire in common:
            s=common[wire]['source'];selected=s['OD_project_upper_mm']/2
            assert all(abs(e['radius']-selected)<1e-6 for e in common[wire]['ends'].values())
            basis='Existing same whole fixed conductor recipe; OD remains project fit gate, not supplier guarantee'
        radius=governing_radius(budget,actual,selected)
        conflicts=[dict(end=e,cap_radius_mm=caps[e]['actual_project_radius_mm'],governing_radius_mm=radius)
            for e in ids if e in caps and caps[e]['actual_project_radius_mm'] is not None and abs(caps[e]['actual_project_radius_mm']-radius)>1e-5]
        rows[name]=dict(status='ONE_CURRENT_PORTION_PROFILE_WITH_SOURCE_CONFLICTS_OPEN' if conflicts else 'ONE_CURRENT_PORTION_PROFILE',
            wire=wire,selected_material=material,project_radius_mm=radius,minimum_project_R_mm=a['minimum_R_mm'],
            previous_independent_budget_mm=budget,basis=basis,source_cap_conflicts=conflicts,
            bought_wire_or_total_length_changed=False,supplier_OD_guaranteed=False)
        mismatches.extend(dict(portion=name,**r) for r in conflicts)
    assert len(rows)==123 and rows['W066/retained0']['project_radius_mm']>=2.1-1e-6
    result=dict(status='WHOLE123_CURRENT_WIRE_PROFILES_SOURCE_GEOMETRY_CONFLICTS_OPEN',portions=rows,conflicts=mismatches,
        never_shrink_selected_wire_to_match_local_cap=True,N01_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (ef,nf,af,cf,mf,hf,uf,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-whole-wire-profile-contract.json',result)
    print(json.dumps(dict(status=result['status'],portions=len(rows),source_conflicts=len(mismatches),seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
