"""Combine changed bank stock with existing reservations without false closure."""
from pathlib import Path
from datetime import datetime, timezone
import json, math, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    start=datetime.now(timezone.utc);pins={}
    def read(rel):
        p=ROOT/rel;pins[rel]=sha(p);return json.loads(p.read_text(encoding='utf-8'))
    q=read('hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json')
    harness=read('hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json')
    source=read('hardware/electronics/full-cat/servo-fuse-parent-extension-materials-r2/materials.json')
    inputs=read('hardware/electronics/full-cat/servo-fuse-lower-loop-materials-r1/materials.json')
    order={row['id']:row for row in q['lines']}
    wires={row['id']:row for row in harness['conductors']}
    assert wires['W066']['current_selected_route_checked'] and wires['W066']['nominal_selected_blank_mm']==330
    remaining=[wires[n] for n in ('W064','W065','W067','W068')]
    assert all(not row['current_selected_route_checked'] and row['nominal_selected_blank_mm'] is None for row in remaining)
    legacy=sum(row['legacy_nominal_mm'] for row in remaining);assert legacy==920
    new=source['red_4mm2_additional_rough_blank_mm'];assert new==1080
    confirmed_blank_plans=330+new;provisional_total=confirmed_blank_plans+legacy
    assert provisional_total==2330
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-stock-budget-r1'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'stock.json').exists()
    end=datetime.now(timezone.utc)
    save(out/'stock.json',dict(selected=False,physical_pass=False,K3_complete=False,E3_complete=False,
        scope='Changed bank materials only; unresolved source wires are not passed or selected.',
        HELU23802=dict(quantity_id='p0:WIRE-RED4-P0',selected_R51_m=order['p0:WIRE-RED4-P0']['planning_quantity'],
            retained_W066_blank_mm=330,new_four_extensions_blank_mm=new,known_blank_plans_mm=confirmed_blank_plans,
            legacy_unchecked_source_reserve_mm=legacy,provisional_total_mm=provisional_total,
            candidate_m=math.ceil(provisional_total/1000),
            unresolved=[dict(wire=row['id'],legacy_mm=row['legacy_nominal_mm'],checked=False) for row in remaining],
            rule='330 replaces legacyW066300;1080 is additional once.3m is a planning candidate, not approved stock until four source routes and full census close.'),
        LAPP0107001=dict(quantity_id='p0:WIRE-INLET-BLACK12-P0',selected_R51_m=order['p0:WIRE-INLET-BLACK12-P0']['planning_quantity'],
            twelve_inputs_mm=2880,W001_return_mm=140,total_mm=inputs['stock']['nominal_required_mm'],candidate_m=4),
        WAGO221412=dict(quantity_id='splice:WAGO221-412',selected_R51_order=order['splice:WAGO221-412']['planning_quantity'],
            retained_installed=1,new_front_installed=2,retained_spare=1,candidate_order=4,
            rule='Replace order2 by4; do not add another XB11 spare or a new duplicate SKU.'),
        TE5053142077=dict(quantity_id='insulation:Pi:RNF-100-3/8-0-STK',selected_stock_m=6,
            new_joint_blanks_mm=52,new_trial_spares_mm=52,new_package_required=False,
            rule='Use already selected TE3/8 sleeve, not unverified assortment13mm. Whole sleeve census remains open.'),
        ties=dict(quantity_id='tie:111-02370',selected_R51_order=order['tie:111-02370']['planning_quantity'],
            known_candidate_bank_input=12,known_candidate_bank_output=12,fixed_parent_feeds=4,fixed_main_bodies=8,
            bank_removal_replacement_allowance=24,
            open='Native front WAGO/rear joint/source insulation grips and old-holder replacement accounting still need exact census; do not announce final installed total.'),
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds()))
    print(json.dumps(dict(provisional_HELU_mm=provisional_total,HELU_candidate_m=3,LAPP_candidate_m=4,selected=False)))


if __name__=='__main__':main()
