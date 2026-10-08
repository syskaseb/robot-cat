"""One bounded inventory of ALL external circuit wires, not just80 body rows.

Aliases and reverse bus edges are grouped, local PCB links stay local. No route
or stock acceptance follows from logical connectivity or provisional datums.
"""
from collections import Counter
from pathlib import Path
import json
from open_prototype_wiring_endpoints import ROOT, BASE, OUT, read, sha


def build():
    net_path = ROOT / 'hardware/electronics/full-cat/connection-map-e4-r1/netlist.json'
    source_path = BASE / 'wiring-checkpoint/source-layout-plan.json'
    endpoint = read(OUT)
    net = read(net_path)
    allocation = read(source_path)
    source_meta_path = BASE.parent/'interfaces.json'
    historical = read(source_meta_path)['source_stock_contribution']
    s1_ids = {r['id']:r['legacy_nominal_mm'] for r in historical['S1_replacements']}
    assert set(s1_ids)=={'W064','W065','W067','W068'}
    assert sum(s1_ids.values())==historical['S1_legacy_subtotal_mm']==920
    body_by_pair = {tuple(sorted((r['a'],r['b']))):r for r in endpoint['body_conductors']}
    current = {e['role']:e for row in endpoint['body_conductors'] for e in row['ends']}
    for row in endpoint['distribution_boundary']:
        current.update(row['resolved_datums'])
    for row in allocation['source_plan']:
        for side in ('input','output'):
            role = row['holder'] + ('.in' if side == 'input' else '.out')
            current[role] = dict(role=role,point_mm=row[side+'_exit_mm'],
                status='UNSELECTED_FHAC_BODY_EXIT_RESERVATION_NOT_SUPPLIER_PIN',
                datum_is_not_manufacturer_pin=True)
    covered = {frozenset((r['a'],r['b'])) for r in endpoint['body_conductors']}
    aliases = {a for r in endpoint['distribution_boundary'] for a in r['graph_aliases']}
    groups = {}
    for edge in net['edges']:
        if edge['kind'] != 'wire':
            continue
        key = tuple(sorted((edge['a'],edge['b'])))
        group = groups.setdefault(key, dict(ends=list(key), graph_ids=[],
            source_files=[], current_datums={r:current[r] for r in key if r in current},
            missing_current_roles=[r for r in key if r not in current],
            current_route_selected=False))
        group['graph_ids'].append(edge['id'])
        if edge['source'] not in group['source_files']:
            group['source_files'].append(edge['source'])
        if edge['id'].startswith('BAT_'):
            group['scope'] = 'LEGACY_BATTERY_F0; LENGTH_AND_RESTRAINT_RECONCILIATION_OPEN'
        elif key in body_by_pair and body_by_pair[key]['id'] in s1_ids:
            wire=body_by_pair[key]
            group.update(scope='LEGACY_SOURCE_920MM; LENGTH_AND_RESTRAINT_RECONCILIATION_OPEN',
                body_id=wire['id'],historical_blank_mm=s1_ids[wire['id']],
                old_blank_not_current_flat_WAGO_route=True)
        elif frozenset(key) in covered or edge['id'] in aliases:
            group['scope'] = 'BODY_OR_DISTRIBUTION_PLAN; ROUTE_OPEN'
        elif edge['id'] == 'PI_VIN':
            group['scope'] = 'ONE_PHYSICAL_SPLIT_W077_W078_WITH_PROTECTED_SPLICE; NOT_EXTRA_PARALLEL_WIRE'
        elif edge['a'].startswith(('F_AUX.out','F_HY.out','F_HP.out','F_TY.out')):
            group['scope'] = 'FOUR_MOVED_FHAC_OUTPUTS; LOAD_ENDPOINT_AND_ROUTE_OPEN'
        else:
            group['scope'] = 'PCB_HEAD_TAIL_LOGIC_OR_PI_LOCAL_INTERCONNECT; CURRENT_BINDING_REVIEW_REQUIRED'
    rows = list(groups.values())
    pins = {p.relative_to(ROOT).as_posix():sha(p) for p in (net_path, OUT, source_path, source_meta_path, Path(__file__))}
    return dict(status='WHOLE_STAGE3_WIRE_SCOPE_PLAN_NOT_ROUTE_ACCEPTANCE',selected=False,
        stage_completed=False,physical_pass=False,source_sha256=pins,
        circuit_wire_edges=sum(len(r['graph_ids']) for r in rows),distinct_unordered_wire_pairs=len(rows),
        scopes=dict(Counter(r['scope'] for r in rows)),physical_pair_groups=rows,
        legacy_920mm=dict(wire_ids=sorted(s1_ids),historical_blanks_mm=s1_ids,
            total_mm=920,scope='Four S1 HELU23802 conductors, NOT BAT_0/BAT_1',
            historical_budget_not_current_routes_or_stock=True),
        graph_edge_count_not_wire_stock_quantity=True,
        internal_bus_module_local_links_not_added_to_wire_stock=True,
        open=['Unknown U1 delivered padmap; no invention',
            'AUX electrical orientation/pad positions not certified by mounting-hole drawing',
            'Both FHAC/MTA outputs, native independent load paths, current complete stock remain open'])


if __name__ == '__main__':
    result = build()
    dest = BASE / 'wiring-checkpoint/routing-scope-plan.json'
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('circuit_wire_edges','distinct_unordered_wire_pairs','scopes')}))
