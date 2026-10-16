"""Nominal W5 scope material selection, not inventory, shopping or E3 approval."""
import json,math,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,OUT,SHA


def bulk_stock(draw):
    keys=('LAPP0107001','LAPP4126002S','TKD2500125','HELU23802')
    return [dict(sku=k,nominal_fit_draw_mm=draw[k],project_stock_mm=1000*math.ceil(draw[k]/1000),
                 actual_owned_stock_mm=None,purchase_unit_verified=False) for k in keys]


def run():
    tick=time.monotonic();files=[]
    def read(name):
        f=OUT/(name+'.json');files.append(f);return json.loads(f.read_text())
    fixed=read('fixed-body-cut-contribution');legs=read('body36-fit-material-contribution')
    choice=read('current-operating-native-composition');bond=read('case-bond-material-contribution')
    source=read('current-source-supports');support=read('remaining-supports/manifest')
    lands=read('remaining-loom-roots-plan');sleeves=read('leg-splice-insulation-reference')
    retention=read('remaining-retention-rest');receivers=read('receiver-supports/manifest')
    source_finish=read('source-receiving-plan')
    power=read('u1-power-grips-native');bus=read('BUS-native-checks');native=read('operating-supports-native/manifest')
    lacing_file=ROOT/'hardware/reference/alpha-802534b-2026-10-12/dimensions.json';files.append(lacing_file)
    assert fixed['conductor_count']==44 and legs['conductors']==36
    portions=fixed['portions']+legs['portions'];assert len(portions)==101
    assert all(r['actual_cut_mm'] is None for r in portions)
    factory=dict(installed_cables=legs['total_factory_units_including_fixed44'],packs=legs['candidate_factory_packs'],
        cables_per_pack=6,whole_cable_spares=legs['whole_factory_spares_after_BUS'],sku='SR-Cable-5264-3PIN-900mm-6PCS',manufacturer_sku='34172',
        original_source_units=12,real_donor_units=4,BUS_shared_unit=1,actual_owned_packs=None)
    assert factory['installed_cables']==17 and factory['packs']*6-factory['installed_cables']==factory['whole_cable_spares']==1
    sleeve_rows=retention['sleeve_reservations'];assert len(sleeve_rows)==12
    assert all(r['diameter_project_mm']==10 and r['length_mm']==21 for r in sleeve_rows)
    sleeve=dict(manufacturer='HellermannTyton',sku=sleeves['manufacturer_sku'],description=sleeves['description'],
        installed_quantity=12,blank_mm=20,total_cut_mm=240,coupon_and_trim_project_mm=80,project_stock_mm=500,
        fraction_of_catalogue_reel_NOT_claimed_purchase_unit=True,catalogue_reel_m=sleeves['manufacturer_values']['catalogue_package_m'],
        retained_geometry_reservation_diameter_mm=10,retained_geometry_reservation_length_mm=21,
        delivered_fit_required=True,installed_outer_diameter_guaranteed=False,
        fit_rule='Before use: actual jacket/lap within manufacturer object range; recovered sleeve within retained10mm/21mm envelope and full insulating overlap. Otherwise do not install; replace sleeve choice and recheck only affected interface.')
    new_land_bands=sum(r['installed_independent_bands'] for g in lands['groups'] for r in g['lands'])
    assert new_land_bands==36 and lands['preserved_Hip_moving_lands']==12
    ties=[dict(scope='moving/fixed source lands',installed=36+12,type='T18I',sku='111-02370',supplier_head_fit_gate=True,
               evidence='remaining-supports/manifest.json'),
          dict(scope='body receivers',installed=receivers['T18I_receiver_quantity'],type='T18I',evidence='receiver-supports/manifest.json'),
          dict(scope='BUS pair',installed=bus['T18I_installed'],type='T18I',evidence='BUS-native-checks.json'),
          dict(scope='MAIN/USB power',installed=power['new_T18R'],type='T18R',evidence='u1-power-grips-native.json')]
    lace=choice['lacing']['current_candidate_blanks']+len(power['lacing_blanks_mm'])
    assert lace==86
    result=dict(status='W5_NOMINAL_MATERIAL_SELECTION_NOT_WHOLE_K3_OR_PURCHASE',
        portions=portions,conductor_portions=101,physical_cut_ends=202,logical_nets=80,logical_ends=160,
        bulk_wire_selection=bulk_stock(fixed['nominal_material_draw_mm']),factory_cables=factory,
        source_supplied_and_retained_draw_mm={k:v for k,v in fixed['nominal_material_draw_mm'].items() if k not in {r['sku'] for r in bulk_stock(fixed['nominal_material_draw_mm'])} and not k.startswith('SR-Cable')},
        historical_920mm_extra_wire_count=0,
        lacing=dict(sku='AlphaWire802534B',body_blanks=85,MAIN_power_blanks=len(power['lacing_blanks_mm']),
            blank_mm=150,installed_blanks=lace,nominal_cut_mm=lace*150,project_stock_mm=15000,
            fraction_of_spool_NOT_claimed_purchase_unit=True,physical_tightening_creep_gate_open=True),
        cable_ties=ties,installed_cable_ties=sum(r['installed'] for r in ties),
        tie_stock_rule='Contributions to shared whole-cat stock, not separate bags. No double count of inherited source12 or receiver21.',
        source_join_sleeves=sleeve,case_adhesive=dict(**bond['candidate_stock'],quantity_patches=12,
            patch_cut_draw_mm=bond['sequential_stock_draw_project_mm']+bond['project_cut_allowance_mm'],only_case_loads=True,physical_bond_trial_required=True),
        source_owned_case_bonds=dict(sku='Henkel LOCTITE EA3430 IDH242865',Hip_case_patches=4,Knee_case_patches=4,
            project_working_allowance_ml=1,from_shared_24ml_stock_NOT_another_cartridge=True,
            quantity_is_allowance_NOT_measured_bond_volume=True,physical_PETG_case_peel_creep_cure_trial_required=True),
        retained_F_PI_output_insulation=dict(sku=source_finish['F_PI']['output_sleeve_SKU'],installed_quantity=1,
            nominal_blank_mm=20,source_bounds_mm=source_finish['F_PI']['output_sleeve_mm'],no_extra_wire_restraint_claim=True),
        hardware_contributions=dict(detachable_rail=native['new_rail_hardware_candidate'],receiver_M2x14=1,receiver_M2_nut=1),
        retained_components=dict(MTA0100335_holders=4,WAGO221_2411_opposed_inline=8,bank_MTA0300330_holders=12,
            bank_TE_input_4_520448_2=12,bank_TE_output_2_520184_2=12),
        optional_braid_required=False,optional_braid_basis='No cosmetic braid added to already qualified prototype loops; any later sleeve/braid changes envelope and requires affected-interface review.',
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in files+[Path(__file__)]},worker_seconds=round(time.monotonic()-tick,3),
        selected_for_nominal_W5=True,whole_K3_complete=False,purchase_authorized=False,physical_pass=False,
        gates=['All dimensions/termination/cavity/Cu and sleeve fit after delivery before cutting or use',
               'Factory850usable is a project requirement, not manufacturer guarantee',
               'Verify exact supplier packs/availability and sum other modules at K3; project stock lengths are NOT purchase units',
               'No source fault/ampacity/fuse/E3 or powered acceptance inferred from this ledger'])
    (OUT/'w5-nominal-material-selection.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(portions=101,cut_ends=202,factory_cables=17,lacing_blanks=lace,ties=result['installed_cable_ties'],seconds=result['worker_seconds'])))


if __name__=='__main__':run()
