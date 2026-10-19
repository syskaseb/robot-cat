"""Physical cable assemblies outside the123individual-portion register.

USB500 is ONE retained bought cable, not a shortened drawing or four new
wires. P309 four balance taps remain separate with UNASSIGNED GTech cavities.
No measurements, pinout, curve-space or electrical qualification invented.
"""
import json,math,time
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_atomic_save import save_json


def main():
    tick=time.monotonic();files={k:OUT/n for k,n in dict(core='n01-six-source-current-core.json',bus='n01-bus-both-plugs-plan-r3.json',ends='n01-shared-routing-boundaries.json').items()}
    d={k:json.loads(p.read_text()) for k,p in files.items()};pi=d['core']['shared_fore_units']['PiUSB_changed_profile']
    bus=next(r for r in d['bus']['routes'] if r['wire']=='USB_CableFirst')
    pi_prefix=pi['first_project_mm']+pi['R_mm']*math.pi/2+math.dist(*pi['grip9_mm'])
    a=pi['grip9_mm'][-1];b=bus['end_mm'];lower=math.dist(a,b)
    usb=dict(id='USB500_PiA_to_BUSC',selected_part='LanbergCA-USBO-10CU-0005-BK',quantity=1,catalogue_total_mm=500,
        external452_mm_is_project_mould_allowance_not_supplier_guarantee=True,project_external_target_mm=452,
        project_overmould_allowances_mm=[26,22],project_OD_mm=5,minimum_fixed_project_R_mm=30,
        pi_jacket_mouth_mm=pi['mouth_mm'],pi_prefix_exit_mm=a,pi_prefix_exit_axis=[b-a for a,b in zip(*pi['grip9_mm'])],
        bus_prefix_exit_mm=b,bus_prefix_exit_axis=bus['end_direction'],pi_prefix_length_mm=pi_prefix,bus_prefix_length_mm=bus['length_mm'],
        joined_middle_Euclidean_lower_bound_mm=lower,remaining_middle_budget_mm=452-pi_prefix-bus['length_mm'],
        maximum_slack_if_straight_middle_mm=452-pi_prefix-bus['length_mm']-lower,
        not_a_proven_joined_curve_or_actual_slack=True,do_not_force_a_complete_360degree_coil=True,
        service_bight_space_must_be_allocated_with_both_end_tangents=True,
        not_in_existing_123_portions_or_246_ends=True,no_SKU_change_or_extension=True,
        factory_usable_length_and_mould_fit_delivery_gate=True)
    length=math.sqrt(sum(v*v for v in usb['pi_prefix_exit_axis']));usb['pi_prefix_exit_axis']=[v/length for v in usb['pi_prefix_exit_axis']]
    assert usb['remaining_middle_budget_mm']>=lower
    result=dict(status='PHYSICAL_USB500_AND_BALANCE_ASSEMBLIES_ACCOUNTED_SPACE_OPEN',
        usb=usb,balance=d['ends']['balance_factory_contract'],existing_register_unchanged=dict(portions=123,ends=246),
        physical_pass=False,N01_complete=False,selected=False,all_extra_physical_cables_routed=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (*files.values(),Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-physical-cable-contract.json',result)
    print(json.dumps(dict(status=result['status'],USB_prefixes_mm=pi_prefix+bus['length_mm'],middle_budget_mm=usb['remaining_middle_budget_mm'],
        middle_chord_lower_bound_mm=lower,maximum_unproven_slack_mm=usb['maximum_slack_if_straight_middle_mm'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
