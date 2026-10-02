"""24 end recipes and revised input conductor losses; no E3 safety approval."""
from pathlib import Path
from datetime import datetime,timezone
import json,math
ROOT=Path(__file__).resolve().parents[2]
from servo_fuse_inputs_r1 import save,sha
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-electrical-r1'
def main():
    begin=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'interface.json').exists():assert not json.loads((OUT/'interface.json').read_text(encoding='utf-8'))['selected']
    sources=[ROOT/'hardware/electronics/full-cat/servo-fuse-side-bank-r11/checks.json',
             ROOT/'hardware/electronics/full-cat/servo-fuse-bank-outputs-r1/checks.json',
             ROOT/'hardware/electronics/full-cat/source-switch-selected-r1/body-harness.json',
             ROOT/'hardware/electronics/power-platform/SERVO-HOLDERS-P0.md',
             ROOT/'hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json']
    routes=json.loads(sources[0].read_text(encoding='utf-8'));outputs=json.loads(sources[1].read_text(encoding='utf-8'))
    ledger=json.loads(sources[2].read_text(encoding='utf-8'));byid={r['id']:r for r in ledger['conductors']}
    q=json.loads(sources[4].read_text(encoding='utf-8'));rows=[];ends=[]
    rho=.0175;alpha=.00393;temperature=60;area=3.31
    for spec in routes['lengths']:
        wire=byid[spec['id']];fuse=next(e for e in (wire['a'],wire['b']) if e.startswith('F_')).split('.')[0]
        length=spec['nominal_unselected_blank_mm'];r=rho*(length/1000)/area*(1+alpha*(temperature-20))
        scenarios=[dict(current_A=i,voltage_mV=i*r*1000,conductor_loss_mW=i*i*r*1000) for i in (2.7,4,10)]
        assert length>=spec['path_mm']+14+8.3+10-1e-7
        rows.append(dict(id=spec['id'],path_mm=spec['path_mm'],nominal_blank_mm=length,actual_cut_mm=None,
            conductor_R60_mOhm=r*1000,scenario=scenarios,
            limitation='Cu model only, not guaranteed LAPP resistance, admissible current or fuse coordination. Contacts/fuse/return excluded.'))
        ends.append(dict(id=fuse+'.in',wire_id=wire['id'],terminal='TE4-520448-2',
            strip_mm=[7.54,8.30],tool='TE69710-1 +224027-2, single AWG12; manufacturer114-2123K8',
            wire='LAPP0107001 black12AWG CuAg/PTFE, both positive ends marked red',
            straight_grip_mm=spec['straight_grip_mm'],restraint='Integral input seat +T18I; W046 head+0.6mmZ from input-fit-r1.',
            blade_axis_and_engagement='Provisional e=0 / axes+/-7mm; fit coupon after delivery. No measured spline/blade claim.'))
    for spec in outputs['lengths']:
        wire=byid[spec['id']];fuse=next(e for e in (wire['a'],wire['b']) if e.startswith('F_')).split('.')[0]
        recipe=wire['ends'][0 if wire['a']==fuse+'.out' else 1]
        assert recipe['sku']=='TE2-520184-2' and recipe['tool']=='TE58628-1'
        ends.append(dict(id=fuse+'.out',wire_id=wire['id'],terminal='TE2-520184-2',
            recipe=recipe,
            local_exit_mm=spec['bank_exit_mm'],restraint='Integral output seat +T18I; no additional splice.',
            limitation='Local portion of continuous factory servo lead only. Delivered copper/OD and correct crimp tool must match supplier application specification; full moving leg route/E3 remain open.'))
    assert len(ends)==24 and len({r['id'] for r in ends})==24 and len(rows)==12
    total=sum(r['nominal_blank_mm'] for r in rows)+byid['W001']['nominal_selected_blank_mm']
    assert total==2180
    cable=next(r for r in q['lines'] if r['id']=='p0:WIRE-INLET-BLACK12-P0')
    tie=next(r for r in q['lines'] if r['id']=='tie:111-02370')
    end=datetime.now(timezone.utc)
    save(OUT/'interface.json',dict(status='LOCAL_RECIPES_CALCULATED_NOT_SELECTED_E3_OPEN',selected=False,W5_complete=False,E3_complete=False,physical_pass=False,
        input_ends=12,output_ends=12,ends=ends,input_losses=rows,
        copper_model=dict(rho20_Ohm_mm2_per_m=rho,alpha_per_K=alpha,assumed_temperature_C=temperature,nominal_area_mm2=area,
            manufacturer_Rmax_verified=False,permissible_continuous_current_verified=False),
        stock_candidate=dict(selected_LAPP_purchase_m=cable['planning_quantity'],candidate_LAPP_purchase_m=3,
            nominal_required_mm=total,candidate_remainder_mm=3000-total,selected_stock_insufficient=True,
            candidate_selected=False,T18I_selected_quantity=tie['planning_quantity'],bank_ties=24,
            whole_robot_working_count_before=tie['installed'],whole_robot_final_count_verified=False),
        assumptions=['The historical100mm maximum is superseded ONLY if this longer interface is selected with stock/E3 updates.',
            '2.7/4/10A are inherited sensitivity scenarios, not admissible running currents or instantaneous fuse thresholds.',
            '3m includes820mm beyond current nominal blanks; reserves for coupons/rework not yet consumed.',
            'Do not solder crimp terminals or use an arbitrary yellow crimp cavity. Inspect manufacturer tool/strip instructions.',
            'Open E3 data and phase2 tests remain prerequisites to powering hardware.'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sources},script_sha256=sha(Path(__file__)),
        started_utc=begin.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-begin).total_seconds()))
    print(json.dumps(dict(ends=24,nominal_mm=total,max_R60_mOhm=max(r['conductor_R60_mOhm'] for r in rows))),flush=True)
if __name__=='__main__':main()
