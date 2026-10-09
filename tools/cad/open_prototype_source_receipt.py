"""One current seven-profile receipt, nominal lengths and restraint stations.

Consolidate scoped evidence without relabelling the rejected W068 proof as
clear or turning provisional fit, tie candidates or lengths into a purchase.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,time
import open_prototype_source_low_gap as G
B=G.B;ROOT=G.ROOT;OUT=G.OUT;DEST=OUT/'source-current-receipt.json'
NEW_PROOF=OUT/'source-low-gap-radius.json'

def verified_family():
    p=G.build();old=B.read(G.SIX_PROOF);new=B.read(NEW_PROOF)
    assert not any(new[k] for k in ('conflicts','outside','errors'))
    assert new['changed_profiles']==['W068']
    assert not old['outside'] and not old['errors']
    assert all(r['a']=='W068' for r in old['conflicts'])
    for proof in (old,new):
        assert all(B.sha(ROOT/n)==h for n,h in proof['source_sha256'].items())
    expected={'W064','W065','W067','W068','W044','W052','F_AUX/input'}
    assert set(old['changed_profiles'])==expected
    return p

def build():
    tick=time.monotonic();p=verified_family();rows=[];restraints=[]
    def seats(name,od,lands):
        assert len(lands)>=2
        # Long straight runs are candidate seats, not oversized clamp parts.
        # Pick9mm at the circuit's two available upstream/end lands.
        for side,g in zip(('source','receiver'),(lands[0],lands[-1])):
            a,b=g['start_mm'],g['end_mm'];length=math.dist(a,b);assert length>=9-1e-7
            u=B.unit(B.sub(b,a));mid=[(x+y)/2 for x,y in zip(a,b)]
            start=B.sub(mid,B.mul(u,4.5));end=B.add(mid,B.mul(u,4.5))
            restraints.append(dict(id=name+'/'+side,wire=name,OD_mm=od,
                straight_seat_start_mm=start,straight_seat_end_mm=end,tangent=u,seat_length_mm=9,
                fastening='One T18I tie candidate on a smooth independent structural saddle',
                not_WAGO_glue_or_terminal_screw_or_unknown_board_pad=True,
                native_carrier_and_tie_sweep_and_tool_access_open=True))
    for r in p['s1_routes']:
        rows.append(dict(id=r['wire'],target=r['target'],material='HELU23802',
            nominal_fit_blank_mm=r['nominal_fit_blank_mm'],centreline_mm=r['centreline_mm'],
            allowance_mm=r['termination_allowance_mm'],native_grips_open=True,ready_to_cut=False))
        seats(r['wire'],r['OD_mm'],r['insulation_grip_lands'])
    for r in p['tails']:
        if r['wire'] in ('W044','W052'):seats(r['wire'],r['OD_mm'],r['independent_grip_lands'])
    h=next(h for h in p['holders'] if h['role']=='F_AUX');seats('F_AUX/input',4,h['input_grip_lands'])
    assert len(restraints)==14 and len({s['id'] for s in restraints})==14
    files=[Path(__file__),Path(G.__file__),G.PLAN,G.PROOF,G.SIX_PROOF,NEW_PROOF,
        OUT/'endpoint-plan.json',OUT/'obstacle-map-current.json']
    return dict(status='SEVEN_CURRENT_NOMINAL_PROFILES_RADIUS_CLEAR_NATIVE_RETENTION_AND_WHOLE_WIRING_OPEN',
        current_family_plan=G.PLAN.name,
        radius_receipts=[dict(proof=G.SIX_PROOF.name,profiles=p['six_unchanged_radius_profiles_reused']['profiles'],
            previous_W068_failure_explicitly_not_accepted=True),dict(proof=NEW_PROOF.name,profiles=['W068'])],
        whole_case_positive_point_proof=G.PROOF.name,source_recipes=rows,
        source_nominal_total_mm=sum(r['nominal_fit_blank_mm'] for r in rows),
        old920mm_is_replaced_not_extra_stock=True,whole_stock_total_mm=None,
        factory_nominal_mm={r['wire']:r['required_blank_mm'] for r in p['tails'] if r['wire'] in ('W044','W052')},
        F_AUX_factory_input_nominal_mm=h['input_blank_mm'],
        factory_limits_and_cavity_depths_are_provisional_delivery_gates=True,
        restraint_stations=restraints,tie_station_candidates=14,
        tie_quantity_is_not_a_final_stock_increment=True,
        narrow_gap=p['low_tube_corridor'],
        open=['Native matched S1/P_REAR supports and14restraint seats/tie clearance',
            'Mounted ATO/removal/assembly access with complete harness',
            'Remaining body/head/tail/leg/legacy source wiring, including W066/S0',
            'Current U1 delivery padmap; no invented external pinout',
            'Whole materials/selected CAD-export package'],
        native_files_changed=0,selected=False,stage_completed=False,ready_to_cut=False,physical_pass=False,
        source_sha256={f.relative_to(ROOT).as_posix():B.sha(f) for f in files},
        worker_seconds=round(time.monotonic()-tick,6),finished_utc=datetime.now(timezone.utc).isoformat())

def main():
    assert not DEST.exists(),'No unchanged receipt duplication'
    q=build();DEST.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:q[k] for k in ('status','source_nominal_total_mm','tie_station_candidates','worker_seconds')}))

if __name__=='__main__':main()
