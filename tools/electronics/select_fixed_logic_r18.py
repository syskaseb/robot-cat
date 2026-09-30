"""Select short fixed hook-up wires, preserving the separate moving-signal requirement."""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / 'hardware/manufacturing/one-batch-prototype-r17'
OUT = ROOT / 'hardware/manufacturing/one-batch-prototype-r18'
POP = ROOT / 'hardware/electronics/full-cat/pwm-carrier-r3/population.json'

def read(p):
    return json.loads(p.read_text(encoding='utf-8'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, value):
    p.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def preview(leads):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(12,8))
    colors={'red':'#b82126','black':'#222222','yellow':'#b88300'}
    for index,row in enumerate(leads):
        y=len(leads)-index
        ax.plot([0,1],[y,y],color=colors[row['color']],linewidth=3)
        ax.text(-.04,y,row['from_ref'],ha='right',va='center',fontsize=9)
        ax.text(1.04,y,f"adapter {row['pin']} | {row['net']} | {row['wire_sku']}",va='center',fontsize=9)
    ax.set_xlim(-.65,3.8);ax.set_ylim(0,len(leads)+1);ax.axis('off')
    fig.suptitle('R18: 19 inherited fixed leads, <=50mm on one rigid cassette',fontsize=13)
    fig.text(.1,.025,'Logical map only, NOT physical pad locations. Continuity first. No moving-wire or physical PASS.',fontsize=10)
    fig.tight_layout(rect=[0,.05,1,.95]);fig.savefig(OUT/'preview.png',dpi=150);plt.close(fig)

def main():
    OUT.mkdir(exist_ok=True)
    selection, ledger, population = read(PARENT/'selection.json'), read(PARENT/'one-order-quantities.json'), read(POP)
    specs = {'red': ('118-0', 'LOGIC3V3_red'), 'black': ('118-1', 'GND_black'), 'yellow': ('118-3', 'PWM5_SW_yellow')}
    items = {}
    for color, (sku, old_suffix) in specs.items():
        row = next(r for r in ledger['lines'] if r['id'] == 'wire:0.15mm2_26AWG:'+old_suffix)
        if color == 'yellow':
            moving = copy.deepcopy(row)
            moving.update(id='wire:moving-PWM-0.14:SKU_OPEN', name='Separate moving PWM wire, actual flex-rated SKU OPEN',
                          note='Preserve former6m planning allowance ONLY for moving signals; no LiY118-3 qualification for XS23/head loop. Exact SKU, radius, routes and terminations remain phase1 work.')
            ledger['lines'].append(moving)
        manufacturer = 'https://donau-elektronik.de/artikel/kabel-litzen/'
        supplier = f'https://www.tme.eu/pl/details/d-{sku}/przewody-jednozylowe-linka/donau-elektronik/{sku}/'
        row.update(id=f'wire:fixed:Donau-{sku}', name=f'Donau{sku} {color} LiY0.14mm2, fixed cassette ONLY',
                   manufacturer_sku=sku, supplier='TME', supplier_sku='D-'+sku, url=supplier,
                   source=manufacturer, planning_quantity=1, unit='roll10m', contained_length_m=10,
                   note='One ordinary10m roll, not500m industrial spool. Fixed local logic/PWM supply and signal return ONLY, no servo power or moving loop. Cut after bench fitting; this is not a10m harness. Phase2 refresh stock/price/delivery.')
        items[color] = {'manufacturer_sku':sku, 'supplier_sku':'D-'+sku, 'manufacturer_source':manufacturer,
                        'supplier_source':supplier, 'conductor_mm2':0.14, 'strand_count':18, 'strand_diameter_mm':0.1,
                        'insulation':'PVC', 'roll_m':10, 'od_supplier_nominal_mm':1.0,
                        'supplier_voltage_v':60, 'supplier_temperature_c':[-10,85],
                        'design_envelope_od_mm':1.1, 'dynamic_rating_confirmed':False}
    leads = copy.deepcopy(population['adapter_leads'])
    assert {r['pin'] for r in leads} == set(range(1,6)) | set(range(11,25))
    for row in leads:
        color = 'red' if row['net']=='LOGIC3V3' else 'black' if row['net']=='G_SYS' else 'yellow'
        row.update(wire_sku=items[color]['manufacturer_sku'], color=color,
                   label_both_ends=f"U1.{row['pin']}:{row['net']}",
                   termination='Solder to inherited U1_LAND and continuity-confirmed adapter outer pad; no new crimp contact',
                   routing_scope='Fixed same rigid cassette, <=50mm; do not extend to a moving servo',
                   cut_length_mm=None, stripped_length_mm=None, physical_pass=False)
    counts = {c:sum(r['color']==c for r in leads) for c in specs}
    assert counts == {'red':2,'black':3,'yellow':14}
    preview(leads)
    assignment = {'scope':'Wire material and exact inherited19 local leads, not a complete harness',
        'sources_sha256':{POP.relative_to(ROOT).as_posix():sha(POP)}, 'parts':items, 'adapter_leads':leads,
        'adapter_ground_bridges':population['adapter_ground_bridges'],
        'ground_bridge_wire':'Donau118-1 black insulated local jumpers; trim/strip after verified pad positions',
        'lead_counts_by_color':counts, 'max_19_leads_total_mm':950,
        'purchasing':'1roll10m of each color includes substantial spare; lengths are not asserted from unmeasured pads',
        'mounting':'Keep all19 leads and XP04 on original single rigid cassette; no free span to deck/body. Support cassette while soldering, guide insulated leads inside its reserved wiring space, no force on adapter pads. Existing cassette fastening unchanged.',
        'bend':'No cyclic-flex qualification. Planning fixed radius>=max(10mm,6D); nominalOD1mm, envelope1.1mm. Supplier does not specify a minimum radius; clearance of actual19-wire population remains to be verified.',
        'insulation':'Do not bridge adjacent signal/power pads; insulate exposed junctions with selected existing shrink/sleeves where geometrically possible. Do not use 1.1mm envelope as proof of pad clearance.',
        'service':'Battery/USB disconnected; remove whole cassette before rework. No new detachable connector in these19 leads. Mark both ends; inspect solder and continuity before power.',
        'forbidden':['servo motor supply/return','XS23/head moving loop','manual replacement of factory JPWM_IN leads'],
        'physical_pass':False, 'new_stls':0, 'whole_harness_complete':False,
        'open':['actual adapter revision/pad continuity and resulting local cut/strip lengths','all moving-signal SKU/radius/route','full upstream XB11 and XA02-XA06','whole-cassette occupied-wire clearance and strain relief','source/branch protection']}
    write(OUT/'fixed-logic-wire.json',assignment)
    ledger.update(selected_prints='hardware/manufacturing/one-batch-prototype-r18/selection.json',line_count=104,phase1_complete=False)
    assert len(ledger['lines']) == len({r['id'] for r in ledger['lines']}) == 104
    assert all(sha(ROOT/r['stl'])==r['sha256'] for r in selection['prints'])
    selection['parent_selection_sha256']=sha(PARENT/'selection.json')
    selection['fixed_logic_wire_sha256']=sha(OUT/'fixed-logic-wire.json')
    selection['conditions'].append('R18 fixed Donau118-0/1/3 ONLY for rigid cassette; all19 original adapter leads and five ground bridges retained. Separate6m moving-PWM allowance remains SKU_OPEN. No new prints/CAD or physical pass.')
    write(OUT/'selection.json',selection); write(OUT/'one-order-quantities.json',ledger)
    files=[OUT/n for n in ('selection.json','one-order-quantities.json','fixed-logic-wire.json','README.md','preview.png','stage-time.json')]
    files += [Path(__file__).resolve(), POP, PARENT/'manifest.json', PARENT/'wire-material-overrides.json']
    write(OUT/'manifest.json', {'status':'PHASE1_INCOMPLETE_R18_FIXED_WIRE_SELECTED', 'files_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in files},
        'jobs':65,'installed_petg_parts':98,'fit_samples':4,'ledger_lines':104,'new_stls':0,'new_cad':0,
        'inherited_print_hashes_unchanged':True,'physical_pass':False,'phase1_complete':False})
    print(json.dumps({'jobs':65,'petg':98,'ledger_lines':104,'fixed_adapter_leads':19,'colors':counts,'new_stls':0,'moving_wire_sku':'OPEN'}))

if __name__=='__main__':
    main()
