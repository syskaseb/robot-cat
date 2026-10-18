"""Whole N01 input map; never convert partial per-module gates into selection.

Keep source solids, planned material, occupied ends and accounting boundaries
distinct. This map prepares ONE coupled allocation, not another CAD variant.
"""
import json
import time
from pathlib import Path
from collections import Counter
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_current_scene import load
from plan_feline_central_pi_wedge import packed


def main():
    tick=time.monotonic();dest=OUT/'n01-whole-constraint-map.json';assert not dest.exists()
    scene,meta,templates,data,pins,_=load()
    files={k:OUT/n for k,n in dict(local='n01-selected-local-head-tail-sources.json',
        extra='n01-all-extra-interface-contract.json',pi='n01-pi-full-port-contract.json',
        modules='n01-module-plan-r5.json',motion='motion-layout.json',
        source_receipt='n01-front-service-split-static.json',
        wedge_receipt='n01-central-pi-wedge.json',portal_receipt='n01-pi-carrier-portal.json').items()}
    docs={k:json.loads(f.read_text()) for k,f in files.items()}
    _,locals_,localmeta=packed(files['local'])
    for n,s in locals_.items():
        assert n not in scene,n
        scene[n]=s;meta[n]=localmeta[n]
    object_owner={}
    for g in docs['modules']['groups']:
        for n in g['objects']:
            assert n not in object_owner,n
            object_owner[n]=g['role']
    parts=[]
    for n,s in scene.items():
        bb=s.BoundBox;r=meta[n]
        parts.append(dict(name=n,owner=object_owner.get(n,r.get('role',r.get('kind','UNASSIGNED'))),
            source_record=r,world_bounds_mm=[[bb.XMin,bb.YMin,bb.ZMin],[bb.XMax,bb.YMax,bb.ZMax]],
            valid=s.isValid(),solids=len(s.Solids),
            geometry_category='curve_NOT_full_jacket' if not s.Solids else
                ('planning_reservation_NOT_supplier_material' if 'reservation' in r.get('kind','') or r.get('role')=='ScaffoldPlanning' else 'saved_source_solid'),
            bounds_are_broadphase_only=True))
    body=data['packet']['endpoints'];extra=[e for r in docs['extra']['sections'] for e in r['ends']]
    assert len(body)==178 and len(extra)==68
    endpoints=[]
    for e in body:endpoints.append(dict(e,domain='body89',current_layout_selected=False))
    for e in extra:endpoints.append(dict(e,domain='extra34_external',current_layout_selected=False))
    assert len(endpoints)==246
    occupied=data['ports']['stations'];assert len(occupied)==20
    assert sum(len(r['occupied_ports']) for r in occupied)==86
    pending=[e for e in extra if e.get('point_mm') is None]
    assert len(pending)==8
    scope=dict(body_physical_sections=89,extra_external_sections=34,
        external_sections_total=123,accounting_ends_total=246,
        U1_internal_schematic_sections_retained=11,
        accounting_boundaries_are_not_automatically_new_wires_or_connectors=True)
    failures=[]
    for key in ('source_receipt','wedge_receipt','portal_receipt'):
        p=docs[key]
        for kind in ('exact_geometry_failures','actual_clearance_failures','reservation_holds'):
            for row in p.get(kind,[]):failures.append(dict(source=files[key].relative_to(ROOT).as_posix(),
                kind=kind,pair=row,rejected_hypothesis_not_current_base_failure=True))
    result=dict(status='WHOLE_N01_CONSTRAINT_INPUT_MAP_NOT_A_LAYOUT_SELECTION',
        selected=False,N01_complete=False,physical_pass=False,scope=scope,
        coordinate_frame='Canonical ordered R5+lowerR3+common+remaining sources; no double placement. Head+35 is a REJECTED proposal, not automatically applied here.',
        parts=parts,unplaced_templates=[dict(name=n,role=role,source_record=r) for role,(n,s,r) in templates.items()],
        endpoints=endpoints,unallocated_local_endpoints=pending,WAGO_all20=occupied,
        full_Pi_source_and_mating_contract=docs['pi'],
        all_selected_local_head_tail_source_parts=len(locals_),
        prior_rejected_hypotheses=failures,
        keep=["P0/E6/15drives/replaceableMG92B and325x200x160/max200width",
            "Lower118/fourMTA/eightfactorypaths/24seats, reuse exact unchanged scopes",
            "BankR47 functional purchased interfaces and24full prefixes",
            "W043/W077/W078 and cut MAIN portal; do not refill its saved channel"],
        coupled_decisions=[
            "Allocate Pi AND PWM/JPWM occupied connectors together, not another isolated Pi pose",
            "Allocate ALL20 WAGO and their86occupied ports/after-turn grip budgets, keep P_SYS source if possible",
            "Include all3FHAC six complete factory/splice/custom/grip budgets before placing support rails",
            "Shared routes/corridor capacity/anchor ownership/tools first, then one actual native layout",
            "Portal-post overlaps require a named physical merged-part or bolted interface; not arbitrary same-owner waiver",
            "Reverse fasteners require renewed STACK/contact/tool evidence, not merely a rigid transform",
            "Own mould-to-wire interfaces named; unrelated own connectors and wire pairs still checked"],
        N01_gate_vs_later=[
            "N01: whole feasible named layout/corridors/grips/tools/anchors and no known blockers",
            "N03: editable native complete mounts and hardware/parameter/reopen",
            "N04/N05: actual full constant/moving routes and lengths, no inheritance from coarse corridors",
            "N06-N10: actual walls/cowls/assembly/full shared motion/stock/release"],
        new_native_files=0,new_scope_score='0/10',
        source_sha256={**pins,**{f.relative_to(ROOT).as_posix():sha(f) for f in files.values()},
            Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=result['status'],parts=len(parts),unplaced_templates=len(templates),
        ends=len(endpoints),unplaced_ends=len(pending),WAGO=len(occupied),occupied=86,
        categories=dict(Counter(r['geometry_category'] for r in parts)),
        invalid_sources=[r['name'] for r in parts if not r['valid']],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
