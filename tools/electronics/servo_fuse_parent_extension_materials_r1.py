"""Account for the new four REAL source extensions, not fictional MTA leads.

Local contribution only. Selected R51 and whole E3/K3 stay unchanged.
Factory wire length, supported joints, WAGO grips and shared fit still gate
selection. Electrical sensitivity is copper only, not a fuse qualification.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save


def main():
    begin=datetime.now(timezone.utc)
    out=ROOT/'hardware/electronics/full-cat/servo-fuse-parent-extension-materials-r1'
    out.mkdir(parents=True,exist_ok=True);assert not (out/'materials.json').exists()
    routefile=ROOT/'hardware/electronics/full-cat/servo-fuse-parent-complete-layout-r5/intent.json'
    catfile=ROOT/'hardware/manufacturing/one-batch-prototype-r51/nonfastener-catalog.json'
    qtyfile=ROOT/'hardware/manufacturing/one-batch-prototype-r51/one-order-quantities.json'
    routes=json.loads(routefile.read_text(encoding='utf-8'))['routes']
    catalog=json.loads(catfile.read_text(encoding='utf-8'))['rows']
    quantities=json.loads(qtyfile.read_text(encoding='utf-8'))['lines']
    def part(n):return next(r for r in catalog if r['quantity_id']==n)
    red=part('p0:WIRE-RED4-P0');splice=part('splice:WAGO221-412')
    assert red['manufacturer_part']=='23802' and red['planning_quantity']==2
    assert splice['manufacturer_part']=='221-412' and splice['planning_quantity']==2
    extras=[r for r in routes if r['kind']=='HELU23802_SIF4.00-R'];assert len(extras)==4
    joint_lengths={r['leg']:26 for r in extras if r['leg'].startswith('R')}
    model=dict(copper_rho20_ohm_mm2_per_m=.0175,copper_alpha_per_K=.00393,
               assumed_copper_temperature_C=60,nominal_area_mm2=4,
               provenance='PROJECT sensitivity assumptions, not measured temperature or certified contact resistance')
    accounting=[]
    for r in extras:
        R20=.0175*(r['path_mm']/1000)/4;R60=R20*(1+.00393*40)
        accounting.append(dict(wire=r['id'],installed_nominal_path_mm=r['path_mm'],rough_blank_mm=r['rough_blank_mm'],
            copper_only_R20_ohm=R20,copper_only_R60_ohm=R60,
            copper_only_at_10A=dict(voltage_drop_V=10*R60,heat_W=100*R60),
            excludes='Joint/contact resistance, source fault level, whole loop, crimp/pull/thermal trial and actual delivered lead;10A is sensitivity, NOT verified permissible operating current'))
    ended=datetime.now(timezone.utc)
    value=dict(selected=False,physical_pass=False,E3_complete=False,K3_complete=False,W5_complete=False,
        installed_additional_extensions=4,wire=red,extension_rows=accounting,
        red_4mm2_additional_rough_blank_mm=sum(r['rough_blank_mm'] for r in extras),
        red_4mm2_additional_nominal_path_mm=sum(r['path_mm'] for r in extras),
        red_stock=dict(selected_m=2,local_blanks_only_fit=True,whole_existing_consumption_not_yet_reconciled=True,
                       selection_unchanged=True,do_not_double_count_factory_wires=True),
        WAGO221412=dict(existing_supplier=splice,additional_installed=2,selected_planning_quantity=2,
                       candidate_total_planning_quantity=4,preserve_existing_one_spare=True,selected_unchanged=True),
        rear_solder=dict(installed=2,solder=part('consumable:solder:T0051402499'),
            insulation=part('p0:HEATSHRINK'),candidate_13mm_sleeve_blank_mm=sum(joint_lengths.values()),
            strip_each_mm=8,lap_mm=8,intact_insulation_overlap_each_mm=9,
            open='Must represent stripped bare conductors separately, not intentional overlap of two insulated tubes. Provisional sleeve envelope and stocked13mm piece length/count require confirmation before selection. Add two-sided native insulation grips.'),
        body_ties_additional_installed=8,source_joint_and_WAGO_grips_not_yet_censused=True,
        factory_rows_over_assumed100mm=[r['id'] for r in routes if r.get('within_assumed_factory_length') is False],
        copper_model=model,unresolved=['R5 shared native fit is not yet accepted.',
            'Rear output W045/W053 rough110mm exceeds provisional100mm; current geometric path79.0007+strip11=90.0007mm, remaining9.9993mm does not support10mm trim reserve. Resolve explicitly, not claim supplied110mm.',
            'No whole stock/E3 selection while grips/joints/geometry are open.'],
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (routefile,catfile,qtyfile)},
        script_sha256=sha(Path(__file__)),started_utc=begin.isoformat(),finished_utc=ended.isoformat(),
        worker_wall_seconds=(ended-begin).total_seconds())
    assert value['red_4mm2_additional_rough_blank_mm']==1070
    assert value['factory_rows_over_assumed100mm']==['W045','W053']
    save(out/'materials.json',value)
    print(json.dumps(dict(extra_red_blanks_mm=1070,additional_WAGO221412=2,rear_solder_joints=2,selected=False)))


if __name__=='__main__':main()
