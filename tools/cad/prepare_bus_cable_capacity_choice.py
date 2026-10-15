"""Replace the insufficient300mm BUS stock declaration, not received guides.

One genuine900mm cable supplies BOTH D/G. V contact/wire remains absent.
Manufacturer length/family is evidence; OD/Cu/contact/plug fit are NOT newly
guaranteed. No purchased stock, no wholeW5/native/service acceptance.
"""
import hashlib,json,math,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/body-harness-checkpoint'
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def choice(routes,facts,binding):
    assert facts['part_number']=='SR-Cable-5264-3PIN-900mm-6PCS'
    assert facts['advertised_length_mm']==900 and facts['cables_per_pack']==6
    assert binding['installed_candidate_header']=='H5' and binding['V_contact_and_wire_removed_before_installation']
    records=[]
    for n in ('W002','W003'):
        r=routes[n];minimum=r['minimum_factory_blank_project_mm']
        assert not r['three_hundred_mm_recipe_fits'] and minimum>300
        records.append(dict(wire=n,guide_mm=r['guide_mm'],minimum_blank_project_mm=minimum,
            existing_project_allowance_mm=minimum-r['guide_mm'],minimum_blank_fits_900=minimum<=900,
            project_insulation_radius_mm=r['radius_mm'],project_static_radius_mm=r['project_R_mm'],
            actual_cut_mm=None,route_unchanged=True))
    required=max(r['minimum_blank_project_mm'] for r in records)
    assert required<=900
    return dict(status='ONE_900MM_BUS_CABLE_CAPACITY_CHOICE_W5_STOCK_RECONCILIATION_OPEN',
        part_number=facts['part_number'],wires=records,physical_cables_installed=1,
        conductors_installed=['D','G'],V_contact_and_wire_absent=True,
        header='H5',pin_binding_inherited_not_colour_inferred=True,
        stock_pack_quantity_candidate=1,stock_pack_cables=6,
        unused_pack_cables_candidate=5,not_extra_cables_per_conductor=True,
        minimum_common_blank_project_mm=required,project_round_up_for_fit_blank_mm=5*math.ceil(required/5),
        gross_900mm_surplus_before_actual_trim_mm=900-required,
        existing_12leg_cables_not_reallocated=True,aggregate_pack_count_not_selected=True,
        new_splices=0,new_restraints=0,changed_geometry=0,selected=False,W5_complete=False,physical_pass=False,
        gates=['Actual matching5264/H5 keyed plug and D/G continuity, V absent before power',
            'Delivered900mm usable length/OD/Cu/insulation/contact; project2mmOD/R10 are not new manufacturer guarantees',
            'Trim only after unpowered assembly/fit, then remote D_FL.1/G2.4 termination',
            'K3 reconcile whole900mm pack count and existing planned stock; no purchase',
            'Existing route/full restraint/native/service and E3 gates remain OPEN'])

def run():
    tick=time.monotonic();rf=OUT/'BUS-routes-plan.json';bf=OUT/'BUS-port-binding.json';ff=ROOT/'hardware/reference/waveshare-sr-cable-900-2026-10-15/facts.json'
    result=choice(json.loads(rf.read_text())['routes'],json.loads(ff.read_text()),json.loads(bf.read_text()))
    result.update(source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (rf,bf,ff,Path(__file__))},worker_seconds=round(time.monotonic()-tick,3))
    (OUT/'BUS-cable-capacity-choice.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','physical_cables_installed','minimum_common_blank_project_mm','project_round_up_for_fit_blank_mm','worker_seconds')}))

if __name__=='__main__':run()
