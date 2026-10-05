"""One preparation ledger for the prototype, not another geometric variant.

Keep immutable receipts. Replace old length roles once, retain factory cables
as ONE purchased loom, and provide a bench-first assembly sequence. Explicit
open gates prevent this preparation sheet from silently claiming whole W5.
"""
from pathlib import Path
from datetime import datetime, timezone
import csv, json, math
from servo_fuse_inputs_r1 import sha, save

ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'hardware/electronics/full-cat'
OUT=BASE/'w5-prototype-preparation-r1'


def main():
    start=datetime.now(timezone.utc);assert not (OUT/'preparation.json').exists()
    pins=[]
    def read(p):
        pins.append(p);return json.loads(p.read_text(encoding='utf-8'))
    graph=read(ROOT/'hardware/electronics/power-platform/wiring-p0.json')
    connection=read(BASE/'w5-whole-connection-plan-r1/plan.json')
    central=read(BASE/'w5-central-received-joint-r2/received.json')
    branch=read(BASE/'w5-branch-joint-routes-r3/checks.json')
    leg=read(BASE/'w5-leg-length-ledger-r1/ledger.json')
    source=read(BASE/'w5-source-material-contribution-r1/stock.json')
    selected=read(ROOT/'hardware/manufacturing/one-batch-prototype-r53/selection.json')
    cuts=BASE/'battery-feed-selected-r1/wire-cuts.csv';pins.append(cuts)
    with cuts.open(encoding='utf-8',newline='') as f:old={r['id']:r for r in csv.DictReader(f)}
    assert len(old)==80 and len(graph['wires'])==80
    cores={c['wire']:(l,c) for l in leg['looms'] for c in l['cores']}
    accepted={r['wire']:r for r in branch['accepted']}
    rows=[]
    for w in graph['wires']:
        wire=w['id'];r=old[wire]
        row=dict(wire=wire,a=w['a'],b=w['b'],material=r['material'],
                 inherited_recipe=r['selected_recipe'] or None,
                 nominal_preparation_blank_mm=float(r['nominal_selected_blank_mm']) if r['nominal_selected_blank_mm'] else None,
                 stock_basis='inherited selected recipe; no second copy of same conductor',
                 route_or_recipe_changed=False)
        if wire in cores:
            loom,c=cores[wire]
            row.update(factory_loom=loom['loom'],factory_sku='Waveshare34172',
                nominal_core_blank_mm=c['provisional_core_blank_mm'],
                common_factory_blank_mm=loom['common_uncut_blank_mm'],
                nominal_preparation_blank_mm=None,route_or_recipe_changed=True,
                stock_basis='One shared factory three-core loom; do not buy three cables or introduce a splice.',
                preparation='Keep factory plug. Identify D/G/V by continuity unpowered, split only body fanout, trim individual cores after fitting.',
                basis=c['source'])
        elif wire in ('W002','W003'):
            row.update(factory_loom='BUS_D_G_SHARED',factory_sku='Waveshare34171',nominal_factory_length_mm=900,
                nominal_preparation_blank_mm=None,route_or_recipe_changed=True,
                stock_basis='ONE shared900mm cable for W002+W003, replacing stale300mm entry; V cavity unused/removed per BUS recipe.',
                basis='hardware/electronics/full-cat/w5-bus-assembly-r1/assembly.json')
        elif wire in central['routes'] or wire in accepted:
            basis=central['routes'].get(wire) or accepted[wire]
            nominal=basis.get('nominal_mm',basis.get('body_mm'))
            assert nominal is not None,wire
            row.update(received_nominal_reference_mm=nominal,nominal_preparation_blank_mm=math.ceil((nominal+60)/10)*10,
                declared_additional_preparation_allowance_mm=60,route_or_recipe_changed=True,
                stock_basis='Replace inherited blank, never add both. Extra60mm is a provisional termination/fitting allowance, not a measured route.',
                preparation='Route without power, then trim/strip to exact terminal recipe. Do not force all extra length into the CAD corridor.')
        elif wire in source['HELU23802']['unique_roles']:
            row.update(nominal_preparation_blank_mm=source['HELU23802']['unique_roles'][wire],route_or_recipe_changed=True,
                stock_basis='Received source contribution replaces legacy920mm source subtotal. Stock includes its declared fitting/retermination allowance.')
        rows.append(row)
    assert len({r['wire'] for r in rows})==80
    aux=read(BASE/'aux-power-r1/circuit.json');auxrows=[]
    for feed in aux['feeds']:
        row=dict(wire=feed['id'],a=feed['from'],b=feed['to'],basis='Retain existing exact AUX recipe except received XA05 route.')
        if feed['id']=='XA05':
            n=central['routes']['XA05']['nominal_mm']
            row.update(received_nominal_reference_mm=n,nominal_preparation_blank_mm=math.ceil((n+60)/10)*10,
                declared_additional_preparation_allowance_mm=60,retention='RemoteEndRetention.CompleteDeckFinished plus received central G2 seat')
        if feed['id']=='XA01':row.update(nominal_trial_blank_mm=40,holder_internal_length_requires_unpowered_fitting=True)
        auxrows.append(row)
    loom_purchase=[dict(loom=l['loom'],sku='Waveshare34172',quantity=1,
        nominal_length_mm=900,common_blank_mm=l['common_uncut_blank_mm'],remaining_nominal_mm=l['nominal900_margin_mm']) for l in leg['looms']]
    missing=[r['wire'] for r in rows if r['nominal_preparation_blank_mm'] is None and not r.get('factory_loom')]
    recipe_keys=('head_local_wiring_recipe','tail_wiring_recipe','Pi_interface','connection_map','BUS_wiring_recipe')
    recipes={k:selected[k] for k in recipe_keys}
    for rel in recipes.values():pins.append(ROOT/rel)
    steps=[
        'On the bench, clear strap slots and check owned PETG parts. No battery connection.',
        'Fit captive nuts, Deck supports and four fixed loom frames BEFORE bank inputs W027/W038 obstruct their mounting tools.',
        'Thread all under-Deck/BAT/AUX/BUS straps before filling Deck. Attach bridge/source carrier and MAIN/Pi trays through their existing specified hardware.',
        'Prepare bankR47 off the robot using its24-end recipe. Route source-switch/fuse/XT60 network from its received recipe, replacing old920mm subtotal.',
        'Fit the received central and four side WAGO insulation restraints, respecting logical pin labels rather than geometric port order.',
        'Fit12factory looms with existing plugs. Attach each link/hip grip ONLY to its received rigid servo carrier; never strap a moving carrier to the body cover.',
        'Place body D/G/V fanouts on four fixed frames. Do not add a connector or electrical junction at the virtual split.',
        'Connect body ends using the exact WAGO/TE terminal recipes. Keep stock/fitting allowance untrimmed until route and nominal movement are checked unpowered.',
        'Fit Pi/head/tail retained recipes and AUX. Keep MAIN/AUX5V outputs separate. Tighten BAT/AUX/BUS/MAIN straps on insulation only.',
        'Before final covers, manually check nominal motion without power and mark any wire pinch/tension. Physical fit remains phase2, not a phase1 PASS.',
        'Fit protective hoods and removable bank cover last. Service reverses applicable steps, disconnecting obstructing leads before undoing frame fasteners.'
    ]
    finish=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    save(OUT/'preparation.json',dict(status='ONE_PROTOTYPE_WIRING_PREPARATION_CONSOLIDATED_NOT_SELECTED',
        P0_wire_count=80,AUX_feed_count=len(auxrows),P0=rows,AUX=auxrows,
        continuous_factory_looms=loom_purchase,shared_BUS_cable=dict(sku='Waveshare34171',quantity=1,nominal_mm=900),
        source_HELU23802=source['HELU23802'],legacy920mm_replaced=True,
        inherited_head_tail_Pi_recipes=recipes,bench_first_assembly=steps,
        candidate_installed_hardware_delta=dict(M3x16=8,M3nuts=8,T18L=12,T18I_fixed_frames=12,T18I_link_hip=12,T18I_AUX=1),
        candidate_new_prints=dict(fixed_frames=4,link_grips=8,hip_grips=4),
        candidate_replaced_prints=['CompleteDeck','SourceEastHood','SourceCarrier','SourceCover','SourceWestHood','SourceBankLeft','SourceBridge'],
        individual_blank_unresolved_wire_ids=missing,
        open_gates=['Receive remote native export.','Retain or demonstrate nominal articulation envelope for12moving looms.','Receive common installation/removal with current hoods/bank/source leads.',
            'Resolve inherited unspecified blanks by existing recipes, sum unique material stock once, and choose one coherent export set.'],
        physical_tests_phase2=['Factory usable cable length/pinout/copper/insulation.','PETG slot fit and loaded creep.','Unpowered routing and full physical joint travel before energizing.'],
        selected=False,W1_complete=False,W5_complete=False,A2_complete=False,K3_complete=False,physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in [Path(__file__),*dict.fromkeys(pins)]},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print(json.dumps(dict(P0=80,AUX=len(auxrows),factory_looms=12,unresolved_blanks=missing)),flush=True)


if __name__=='__main__':main()
