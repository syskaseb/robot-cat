"""Select the entire nominal material/tool provision, preserving power gates."""
import json,time
from pathlib import Path
from plan_current_harness_interfaces import ROOT,BASE,SHA
from current_work_guard import check
from release_check import verify,REQUIRED_GATES


def validate(data):
    assert len(data['wire_blanks'])==len({r['id'] for r in data['wire_blanks']})
    for r in data['bulk_wire_stock']:assert r['project_supply_mm']>=r['nominal_fit_draw_mm']>0
    assert data['factory_units']['SR900']['installed_cables']==17
    assert data['factory_units']['SR900']['packs']*6==18
    assert max(data['factory_units']['K1474']['draw_per_colour_mm'].values())<1000
    mats={r['sku']:r for r in data['materials']}
    assert mats['111-01910 T18R']['installed']==9
    assert mats['AlphaWire802534B']['installed_blanks']==89
    assert mats['3M SJ4570']['installed_pairs']==20
    assert mats['111-02370 T18I']['installed']==sum(r['installed'] for r in mats['111-02370 T18I']['allocations'])==143
    assert mats['111-02370 T18I']['nominal_pack100_count']*100>=143+mats['111-02370 T18I']['project_service_spares']
    assert mats['AlphaWire802534B']['minimum_spool_mm']>=mats['AlphaWire802534B']['project_required_access_mm']
    return mats


def run():
    check();tick=time.monotonic();file=BASE/'phase1-material-plan.json';p=json.loads(file.read_text());mats=validate(p)
    pins=dict(p['source_sha256']);pins[file.relative_to(ROOT).as_posix()]=SHA(file)
    bonds=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint/case-bond-material-contribution.json'
    b=json.loads(bonds.read_text());width=max(r['cut_width_project_mm'] for r in b['patches']);assert width<=12
    pins[bonds.relative_to(ROOT).as_posix()]=SHA(bonds)
    mats['3M VHB4905'].update(selected_nominal_unit='3M4905P12mmx33m roll',selected_roll_count=1,
        manufacturer_catalogue='https://multimedia.3m.com/mws/media/2363355O/3m-iatd-cmsd-product-catalogue-double-sided-tapes-es.pdf?fn=3m-iatd-cmsd-product-catalogue-double-sided-tapes-es.pdf',
        selected_width_mm=12,selected_length_mm=33000,largest_actual_patch_width_mm=width,
        stock_unit='One nominal manufacturer4905P12mmx33m roll; actual cuts<=8.1mmwide, not a12.7mm commercial cut strip',
        stock_basis='Explicitly replaces project12.7mm stock-strip width, NOT any installed patch. Largest selected cut8.1mm fits12mm; unchanged0.5mm4905family. No thinner/narrower installed patch substituted.')
    dispositions=[
        dict(id='CURRENT_MAIN_INSULATION',nominal_source='main-positive-wiring-card-r1/interface.json MAIN_input_insulation',
            raw_blanks_mm=dict(red_inner=7,black_inner=4,shared_outer=20),
            retained_nominal_supply_only=True,
            limitation='Supply inventory is complete; MAIN restricted recovery/coverage at current end geometry is M4/E3/phase2, not certified by stocking a sleeve. Preinsulated S0/S1TE barrels do not cover their exposed metal eyes/studs; guards stayM4 OPEN.'),
        dict(id='YAW_AND_SHARED_BANDS',yaw_anchors=['JR housing','factory insulation','HELU straight X-70'],
            yaw_nominal_T18I=3,delivery_fit_gate=True,
            paired_E2_W4_allocated_once_to='E2 ten',tail_additional_T18I=12,AUX_shared_tail_reference_not_extra=True,
            evidence='head-local-interface.json anchors + tail-wiring selection support_plan; ordinary replaceable ties, no invented extra fixed anchor.'),
        dict(id='SUPPLY_UNITS',rule='Project cut stock/access is NOT a fictitious manufacturer short roll or owned inventory.',
            AlphaWire='One500yard standard spool457.2m (minimum443.484m), shared; borrowed verified20m cut supply alternative needs receipt before assembly.',
            TF31='One30m manufacturer reel, not0.5m retail unit.',
            VHB='One nominal4905P12mmx33m manufacturer roll; cuts unchanged.',
            tesa='Require one verified25x200mm cut of same4965 via workshop access; no claim this is a manufacturer pack or already owned.',
            SJ4570='Require verified25x1000mm cut supply of sameSJ4570 via workshop access, not a standard DualLock substitution or purchased roll.')]
    p.update(status='K3_ONE_CURRENT_NOMINAL_MATERIAL_TOOL_PROVISION_SELECTED',selected=True,K3_complete=True,
        review_gaps=[],review_dispositions=dispositions,physical_pass=False,
        scope='Complete current nominal wire/factory-unit/cut-insulation/adhesive/tie/lace/PETG/tool provision for the selected open prototype, with overlaps removed. Requirements for stock/tool access, not owned inventory, purchases, physical fit or electrical E3 acceptance. Unselected M4 guard redesign is explicitly not fabricated.',
        current_M4_and_E3_open=True,all20_results_complete=False,
        worker_seconds=round(time.monotonic()-tick,3))
    for n,h in pins.items():assert SHA(ROOT/n)==h,n
    for f in [Path(__file__),ROOT/'tools/cad/compose_phase1_materials.py',ROOT/'tools/cad/phase1_filament_budget.py',ROOT/'tools/cad/test_phase1_materials.py']:
        pins[f.relative_to(ROOT).as_posix()]=SHA(f)
    f=BASE/'phase1-material-selection.json';f.write_text(json.dumps(p,indent=2)+'\n',newline='\n');pins[f.relative_to(ROOT).as_posix()]=SHA(f)
    manifest=dict(schema_version=1,result_id='K3',selected=True,K3_complete=True,readiness='prototype',physical_pass=False,
        scope=p['scope'],selection=f.relative_to(ROOT).as_posix(),files=[dict(path=n,sha256=h) for n,h in sorted(pins.items())],
        gates={n:dict(status='open',reason='Nominal preparation only. Physical supply, tooling access, PETG/adhesion/coverage and E3 readiness are not demonstrated by stock budget.') for n in REQUIRED_GATES})
    assert verify(ROOT,manifest)['integrity_ok']
    f=BASE/'phase1-material-manifest.json';f.write_text(json.dumps(manifest,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(wire_blanks=len(p['wire_blanks']),sleeves=len(p['sleeves']),stock_rows=len(p['materials']),seconds=p['worker_seconds'])))


if __name__=='__main__':run()
