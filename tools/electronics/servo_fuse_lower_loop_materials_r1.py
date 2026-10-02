"""Account for the longer saved twelve input loops; not whole E3/K3.

Stock is rounded to metres for planning, not a retail-order promise. Copper
resistance/current sensitivities do not qualify insulation or fuse clearing.
Preserve the currently selected R51 list until the complete bank is chosen.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,math,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    begin=datetime.now(timezone.utc)
    src=ROOT/'hardware/electronics/full-cat/servo-fuse-bank-connected-release-r4/checks.json'
    intent=src.with_name('intent.json')
    order=ROOT/'hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json'
    r=json.loads(src.read_text(encoding='utf-8'));i=json.loads(intent.read_text(encoding='utf-8'))
    q=json.loads(order.read_text(encoding='utf-8'))
    old=next(v for v in q['lines'] if v['id']=='p0:WIRE-INLET-BLACK12-P0')
    assert not r['hits'] and not r['errors'] and len(r['new_nominal_input_blanks'])==12
    blanks=r['new_nominal_input_blanks'];bank=sum(v['blank_mm'] for v in blanks)
    assert bank==i['nominal_bank_input_stock_mm']==2880
    inlet=140;total=bank+inlet;metres=math.ceil(total/1000)
    assert total==i['nominal_bank_input_and_W001_mm']==3020 and metres==4
    # Same explicit copper model as earlier sensitivity calculations.
    rho20=.0175;alpha=.00393;temperature=60;area=3.31
    rho=rho20*(1+alpha*(temperature-20))
    added=r['added_insulated_path_mm_per_wire']/1000
    delta_R=rho*added/area
    rows=[]
    for v in blanks:
        rows.append(dict(wire=v['wire'],nominal_blank_mm=v['blank_mm'],actual_cut_mm=None,
            copper_area_assumed_mm2=area,delta_insulated_path_mm=added*1000,
            delta_R_at_60C_ohm=delta_R,
            sensitivity=[dict(assumed_A=a,delta_V=a*delta_R,delta_W=a*a*delta_R) for a in (2.7,4,10)]))
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-lower-loop-materials-r1';out.mkdir(parents=True,exist_ok=True)
    assert not (out/'materials.json').exists()
    now=datetime.now(timezone.utc)
    save(out/'materials.json',dict(selected=False,physical_pass=False,E3_complete=False,K3_complete=False,
        phase1_percent=75,stock=dict(manufacturer='LAPP',part='0107001',supplier_sku='HEAT260SC-12BK',
            material_roles='Twelve marked-positive bank inputs plus W001 battery return only.',
            selected_R51_m=old['planning_quantity'],bank_blank_mm=bank,W001_blank_mm=inlet,
            nominal_required_mm=total,candidate_metres=metres,planning_excess_mm=metres*1000-total,
            retail_multiple_unverified=True,entire_robot_stock_census_complete=False),
        rows=rows,copper_model=dict(rho20_ohm_mm2_per_m=rho20,alpha_per_C=alpha,temperature_C=temperature,
            project_assumptions_not_measured=True),
        gates=['Current sensitivities are not allowed continuous currents or motor measurements.',
               'No fuse coordination, source fault current, insulation or termination heating approval.',
               'Parent factory feed extensions, outputs and whole-robot stock/termination census remain open.',
               'Keep selected R51 unchanged; propagate candidate4m only with complete bank selection.'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (src,intent,order)},
        script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=now.isoformat(),
        worker_wall_seconds=(now-begin).total_seconds()))
    print(json.dumps(dict(required_mm=total,candidate_metres=metres,delta_R_ohm=delta_R)))


if __name__=='__main__':main()
