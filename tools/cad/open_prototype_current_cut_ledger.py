"""One current nominal-length ledger, never an instruction to cut hardware.

Historical blanks remain history. Prefixes are not full conductors, factory
tails are not extra purchased stock, W076's physical split is one net edge.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,time
import open_prototype_rl_tail_group as T
from open_prototype_wiring_endpoints import BASE

OUT=T.OUT;DEST=OUT/'current-cut-ledger.json'

def build():
    tick=time.monotonic();current_source=None
    source_receipt=OUT/'source-current-receipt.json'
    if source_receipt.exists():
        import open_prototype_source_receipt as Current
        current_source=Current
        p=Current.verified_family()
    else:p=T.build()
    ep=T.B.read(OUT/'endpoint-plan.json')
    entries=[];tails={r['wire']:r for r in p['tails'] if r['leg'] in ('FL','FR','RL','RR')}
    assert len(tails)==8
    for row in ep['body_conductors']:
        ends=[r for r in p['body_ends'] if r['wire']==row['id']]
        assert len(ends)==2,row['id']
        item=dict(id=row['id'],net=row['net'],
            old_roles=[row['a'],row['b']],current_roles=[e['current_role'] for e in ends],
            datums=[e['datum'] for e in ends],material=row['material'],
            historical_R53_blank_mm=row.get('selected_R53_blank_mm'),
            current_nominal_blank_mm=None,stock_contribution_mm=None,
            status='FULL_ROUTE_AND_RESTRAINT_OPEN',ready_to_cut=False)
        if row['id'] in tails:
            r=tails[row['id']]
            assert r['target'] in item['current_roles']
            length=T.B.check_path(r['segments'],end=p['ports'][r['target']]['point_mm'],min_radius=r['min_radius_mm'])
            assert abs(length+r['strip_allowance_mm']-r['required_blank_mm'])<1e-7
            item.update(status='FACTORY_TAIL_NOMINAL_RECIPE_ONLY',
                current_nominal_blank_mm=math.ceil(r['required_blank_mm']),
                unrounded_required_mm=r['required_blank_mm'],route_mm=length,
                strip_allowance_mm=r['strip_allowance_mm'],
                factory_limit_assumption_mm=r['assumed_factory_limit_mm'],
                supplier_usable_lead_length_unverified=True,
                stock_contribution_mm=0,not_extra_purchased_wire=True,
                complete_current_native_grips_and_shared_gate_open=True)
        entries.append(item)
    assert len(entries)==80 and len({r['id'] for r in entries})==80
    ground_plan=OUT/'ground-upstream-grip-plan.json'
    ground_proof=OUT/'ground-upstream-grip-radius.json'
    g=T.B.read(ground_plan)['row'];proof=T.B.read(ground_proof)
    assert proof['status']=='CURRENT_GROUND_RADIUS_CLEAR_NATIVE_GRIPS_AND_SOURCE_BAY_OPEN'
    assert not any(proof[k] for k in ('conflicts','outside','errors'))
    assert all(T.B.sha(T.ROOT/n)==v for n,v in proof['source_sha256'].items())
    item=next(r for r in entries if r['id']=='W001')
    item.update(status='SCOPED_RADIUS_CLEAR_NATIVE_GRIPS_AND_ASSEMBLY_OPEN',
        current_nominal_blank_mm=g['nominal_fit_blank_mm'],
        unrounded_required_mm=g['centreline_mm']+g['termination_allowance_mm'],
        route_mm=g['centreline_mm'],strip_allowance_mm=g['termination_allowance_mm'],
        provisional_stock_contribution_mm=g['nominal_fit_blank_mm'],
        old150mm_blank_invalid=True,native_grips_and_assembly_access_open=True)
    if current_source:
        for r in p['s1_routes']:
            item=next(e for e in entries if e['id']==r['wire'])
            assert r['target'] in item['current_roles']
            item.update(status='CURRENT_SOURCE_RADIUS_RECIPE_NATIVE_RESTRAINT_AND_ASSEMBLY_OPEN',
                current_nominal_blank_mm=r['nominal_fit_blank_mm'],
                unrounded_required_mm=r['centreline_mm']+r['termination_allowance_mm'],
                route_mm=r['centreline_mm'],strip_allowance_mm=r['termination_allowance_mm'],
                provisional_stock_contribution_mm=r['nominal_fit_blank_mm'],
                source_radius_receipt=source_receipt.name,
                current_full_stock_selection_open=True)
    holder_inputs=[]
    for h in p['holders']:
        old=next(r for r in ep['distribution_boundary'] if h['role']+'.in' in r['ends'])
        current=p['permutation'].get(next(r for r in old['ends'] if r!=h['role']+'.in'),
                                     next(r for r in old['ends'] if r!=h['role']+'.in'))
        assert current==h['input_target'],(h['role'],current,h['input_target'])
        alias=old['body_id'] or old['graph_aliases'][0]
        holder_inputs.append(dict(id=alias,part=h['role'],from_role=h['role']+'.in',
            target=h['input_target'],nominal_mm=math.ceil(h['input_blank_mm']),
            unrounded_mm=h['input_blank_mm'],factory_minimum_mm=h['factory_minimum_mm'],
            factory_datum_OD_and_bend_provisional=True,stock_contribution_mm=0,
            output_prefix_mm=h['output_prefix_mm'],
            output_prefix_not_complete_blank=True,ready_to_cut=False))
        if old['body_id']:
            item=next(r for r in entries if r['id']==old['body_id'])
            item.update(status='FHAC_FACTORY_INPUT_NOMINAL_RECIPE_ONLY',
                current_nominal_blank_mm=math.ceil(h['input_blank_mm']),
                unrounded_required_mm=h['input_blank_mm'],stock_contribution_mm=0,
                not_extra_purchased_wire=True,complete_current_native_grips_and_shared_gate_open=True)
    legacy=[dict(id=r['id'],historical_cp2_nominal_mm=r['nominal_blank_mm'],
        current_nominal_mm=None,status='CURRENT_RECONCILIATION_OPEN_NOT_STOCK',
        reason='W001 landing changed; W076 extension/S0 reserve unresolved; W066 current SYS approach open')
        for r in T.B.read(BASE.parent/'interfaces.json')['nominal_source_wires']
        if r['id'] in ('W075','W076_FACTORY','W076_EXTENSION','W001','W066')]
    for r in legacy:
        if r['id']=='W001':
            r.update(current_nominal_mm=g['nominal_fit_blank_mm'],status='SCOPED_RADIUS_CLEAR_GRIPS_OPEN',
                reason='Current G1.1 and upstream9.6mm grip; last3mm entry is not a grip land')
    pins=[Path(__file__),Path(T.__file__),T.PLAN,OUT/'endpoint-plan.json',BASE.parent/'interfaces.json',ground_plan,ground_proof]
    if current_source:pins.extend([source_receipt,Path(current_source.__file__),current_source.G.PLAN,current_source.NEW_PROOF])
    return dict(status='CURRENT_IDENTITIES_AND_NOMINAL_SUBSET_NOT_FULL_CUTLIST',
        body_conductors=entries,holder_factory_inputs=holder_inputs,legacy_source=legacy,
        body_conductor_count=80,current_body_nominal_count=sum(r['current_nominal_blank_mm'] is not None for r in entries),
        extra_factory_wire_purchase_mm=0,whole_stock_total_mm=None,
        source_current_receipt=source_receipt.name if current_source else None,
        W076_factory_extension_one_logical_conductor=True,
        historical920mm_not_current_source_stock=True,
        branch_output_prefixes_not_double_counted=True,
        material_selection_and_full_routes_open=True,ready_to_cut=False,
        selected=False,stage_completed=False,physical_pass=False,
        source_sha256={f.relative_to(T.ROOT).as_posix():T.B.sha(f) for f in pins},
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())

def main():
    result=build();DEST.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','body_conductor_count','current_body_nominal_count','extra_factory_wire_purchase_mm','whole_stock_total_mm','worker_seconds')}))

if __name__=='__main__':main()
