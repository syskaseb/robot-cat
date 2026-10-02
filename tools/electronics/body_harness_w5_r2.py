"""Current R44 physical fabrication ledger; unknown cuts stay unknown.

The twelve-input failed candidate cannot silently enlarge the purchase list
or become selected fabrication data. Parallel K1474 colours share one cable.
"""
from pathlib import Path
from datetime import datetime,timezone
import copy,csv,json,hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/body-harness-w5-r2'
PARENT=ROOT/'hardware/manufacturing/one-batch-prototype-r44'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def build():
    files={
      'ledger':'hardware/electronics/full-cat/body-harness-w5-r1/interface.json',
      'DATA':'hardware/electronics/full-cat/body-data-bridges-r7/interface.json',
      'W061':'hardware/electronics/full-cat/body-ground-bridge-finish-r5/interface.json',
      'W060':'hardware/electronics/full-cat/main-input-return-finish-r3/interface.json',
      'positive':'hardware/electronics/full-cat/main-positive-wiring-card-r1/interface.json',
      'Pi':'hardware/electronics/full-cat/pi-interface-final-r2/wiring-card.json',
      'rejected_inputs':'hardware/electronics/full-cat/servo-fuse-inputs-r1/checks.json',
      'quantities':'hardware/manufacturing/one-batch-prototype-r44/one-order-quantities.json',
      'selection':'hardware/manufacturing/one-batch-prototype-r44/selection.json'}
    docs={k:read(ROOT/v) for k,v in files.items()}
    data=copy.deepcopy(docs['ledger']);data['parent']='one-batch-prototype-r44'
    data.update(schema_version=2,status='CURRENT_PARTIAL_W5_FABRICATION_LEDGER_NOT_ORDER_RELEASE',
                selected_route_scope='Only explicitly bound R44 inherited/overridden recipes, no failed candidate',
                W5_complete=False,K3_complete=False,physical_pass=False,new_STL=0)
    by_id={r['id']:r for r in data['conductors']};assert len(by_id)==80
    # Historical route flags were tied to R35. Preserve actual assembly ends,
    # but do not imply that later geometry approved an unbound body route.
    for row in by_id.values():
        row['historical_R35_route_checked']=row.pop('current_R35_route_checked')
        row['current_selected_route_checked']=False
        row['nominal_selected_blank_mm']=None
        row['selected_recipe']=None
        row['actual_cut_mm']=None
    def select(wire,blank,source):
        row=by_id[wire];row.update(current_selected_route_checked=True,
           nominal_selected_blank_mm=blank,selected_recipe=files[source],limit_mm=None)
        row['route_state']='SELECTED_NOMINAL_WITH_PHASE2_FIT'
    for w,r in docs['DATA']['lengths'].items():select(w,r['proposed_blank_mm'],'DATA')
    select('W061',docs['W061']['lengths']['W061']['provisional_blank_mm'],'W061')
    select('W060',docs['W060']['nominal_blank_mm'],'W060')
    for r in docs['positive']['rows']:select(r['wire'],r['nominal_blank_mm'],'positive')
    for w in ('W079','W080'):select(w,docs['Pi']['power']['nominal_cut_bound_mm'],'Pi')
    # MAIN R44 supersedes only its shared insulation and positive splice, not
    # the retained W060 route. Both sides refer to one common outer input boot.
    by_id['W060']['shared_outer_input_insulation']=docs['positive']['MAIN_input_insulation']
    by_id['W078']['shared_outer_input_insulation']=docs['positive']['MAIN_input_insulation']
    for row in docs['rejected_inputs']['lengths']:
        by_id[row['id']]['unselected_candidate_blank_mm']=row['nominal_blank_mm']
        by_id[row['id']]['rejected_candidate_source']=files['rejected_inputs']
        by_id[row['id']]['route_state']='OPEN_REJECTED_GEOMETRY_AND_LEGACY100MM_LIMIT'
    current=sum(r['current_selected_route_checked'] for r in by_id.values())
    data['coverage']=dict(P0_physical_conductors=80,ends=160,selected_nominal_cuts=current,
      remaining_body_ledger_cuts=80-current,
      distinction='Coverage is this P0 ledger only. Separate selected head/PWM/cassette leads are preserved; not a whole W5 completion percentage.')
    assert current==10
    data['already_selected_interfaces'].update(MAIN_positive=files['positive'],MAIN_return=files['W060'],G1_G2=files['W061'],DATA=files['DATA'])
    data['open_design']=[
      'Twelve fuse-input full routes/restraints: first R44 candidate rejected; no selected input blank yet.',
      'Other body/leg/source/balance routes, ends requiring delivered mating details and joint restraints.',
      'Complete stock allocation including separate selected head/PWM interfaces; no K3 completion.',
      'E3 source/branch protection, K2/A2/A3 remain open.']
    data['source_bindings']={**data['source_bindings'],**{p:sha(ROOT/p) for p in files.values()}}
    stock=docs['positive']['stock'];q=docs['quantities']['lines']
    k1474=next(r for r in q if r['id']=='p0:PI-POWER-CABLE')
    lapp=next(r for r in q if r['id']=='p0:WIRE-INLET-BLACK12-P0')
    liy=next(r for r in q if r['id']=='p0:DATA-BRIDGE-WIRE-P0')
    assert k1474['planning_quantity']==1 and lapp['planning_quantity']==2 and liy['planning_quantity']==7
    stockrows=[dict(stock_id='JoyIT K-1474',purchase_quantity=1,unit='one1000mm_two_colour_cable',
      allocation_per_colour_mm={'red':{'Pi':stock['Pi_conductor_bound_mm'],'W078':210},'black':{'Pi':stock['Pi_conductor_bound_mm'],'W060':220}},
      remaining_per_colour_mm={'red':stock['red_remaining_mm'],'black':stock['black_remaining_mm']},
      allocation_status='SELECTED_NOMINAL_COLOUR_BUDGET',cable_bought_twice=False),
      dict(stock_id='LiY 4126002S',purchase_quantity=7,unit='m',selected_allocations_mm={w:200 for w in ('W007','W011','W012')},
        known_selected_mm=600,unallocated_mm=6400,unallocated_is_not_final_spare=True,allocation_status='PARTIAL_NOT_ALL_BLUE_WIRE'),
      dict(stock_id='LAPP 0107001',purchase_quantity=2,unit='m',selected_input_allocations_mm=None,
        battery_legacy_reserve_mm=150,legacy_input_maximum_mm=1200,
        failed_candidate_mm=docs['rejected_inputs']['stock']['inputs_candidate_mm'],
        failed_candidate_with_BAT_overrun_mm=-docs['rejected_inputs']['stock']['remaining_mm'],
        allocation_status='OPEN_DO_NOT_CUT_OR_INCREASE_PURCHASE_FROM_FAILED_ROUTE')]
    return data,dict(parent='one-batch-prototype-r44',stock=stockrows,complete=False,
       no_quantity_change=True,physical_pass=False,source_bindings=data['source_bindings'])
def main():
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'interface.json').exists(),'Preserve completed ledgers'
    data,stock=build();save(OUT/'interface.json',data);save(OUT/'stock.json',stock)
    with (OUT/'wire-cuts.csv').open('w',encoding='utf-8-sig',newline='') as f:
        cols=['id','a','b','material','nominal_selected_blank_mm','actual_cut_mm','selected_recipe','unselected_candidate_blank_mm','route_state']
        writer=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');writer.writeheader();writer.writerows(data['conductors'])
    end=datetime.now(timezone.utc)
    save(OUT/'build-checks.json',dict(coverage=data['coverage'],all_actual_cuts_unknown=all(r['actual_cut_mm'] is None for r in data['conductors']),
      W5_complete=False,K3_complete=False,physical_pass=False,script_sha256=sha(Path(__file__)),
      started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(data['coverage']))
if __name__=='__main__':main()
