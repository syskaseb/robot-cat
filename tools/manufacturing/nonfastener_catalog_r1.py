"""Reconcile R46 non-fastener roles; missing commercial data remains explicit."""
from pathlib import Path
import copy
import hashlib
import json
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/cad'))
from release_check import verify
PARENT = ROOT / 'hardware/manufacturing/one-batch-prototype-r46'
OUT = ROOT / 'hardware/manufacturing/nonfastener-catalog-r1'
BATCH = ROOT / 'hardware/manufacturing/one-batch-prototype-r47'

def read(rel):
    return json.loads((ROOT / rel).read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Exact manufacturer identity or, for a distributor's generic product, exact offer.
# No OEM identity is invented for unbranded products or kits.
P0 = {
 'BUS-USB-CABLE-P0': ('Lanberg','CA-USBO-10CU-0005-BK','14824'),
 'CHARGER': ('SkyRC','SK-100008','6103'),
 'BATTERY-MONITOR': (None,None,'5015'),
 'HEATSHRINK': (None,None,'5375'),
 'DATA-BRIDGE-WIRE-P0': ('LAPP','4126002S','607974'),
 'PI-POWER-CABLE': ('Joy-IT','K-1474','3304684'),
 'TERMINAL-SERVO-OUT-P0': ('TE Connectivity','2-520184-2','488306'),
 'MAIN-SWITCH': ('HELLA','6EK002843-002','256550'),
 'BUS-PIGTAIL-P0': ('Waveshare','34171','1204981'),
 'DATA-JUNCTIONS-P0': ('WAGO','221-415','1188363'),
 'DRIVE-12': ('Waveshare','22414','1181056'),
 'BUS': ('Waveshare','25514','1187948'),
 'REG-MAIN': ('Pololu','4853','1196574'),
 'DISTRIBUTION': ('WAGO','221-615','1180756'),
 'DISTRIBUTION-G2-P0': ('WAGO','221-415','1188363'),
 'DISTRIBUTION-LEGS-P0': ('WAGO','221-415','1188363'),
 'XT60': ('AMASS','XT60H-M/F with covers','581961'),
 'SD': (None,None,'1188166'),
 'BATTERY': ('Gens Ace','GEA223S30X6GT','1570'),
 'BATTERY-STRAPS-P0': (None,None,'4982'),
 'MOTOR-STOP-MANUAL-P0': ('NKK','S821','354-3235'),
 'MAIN-FUSE': ('Littelfuse','0287030.PXCN','0287030.PXCN'),
 'MAIN-FUSE-HOLDER': ('Littelfuse','FHAC0002ZXJ','FHAC0002ZXJ'),
 'FUSES': ('MTA','MINIVAL10A','AMFM-10A'),
 'FUSE-HOLDERS': ('MTA','0100335','MTA-MINI-HOLDER'),
 'SERVO-HOLDERS-P0': ('MTA','0300330','0300330'),
 'WIRE-INLET-BLACK12-P0': ('LAPP','0107001','HEAT260SC-12BK'),
 'WIRE-RED4-P0': ('HELU','23802','SIF4.00-R'),
 'WIRE-BLACK4-P0': ('TKD','2500125','TKD-2500125'),
 'TERMINAL-S0-P0': ('TE Connectivity','130207','130207'),
 'TERMINAL-S1-P0': ('TE Connectivity','130171','130171'),
 'TERMINAL-SERVO-IN-P0': ('TE Connectivity','4-520448-2','4-520448-2'),
 'BATTERY-PAD-P0': ('Rolfoam','PE TR PYR white1mm100x100cm','pianka-polietylenowa-pe-1-mm-biala'),
}
EXTRA = {
 'AUX-SERVO-MG92B': ('TowerPro','MG92B positional','Botland','24409'),
 'MG92B-JR-EXTENSION': (None,None,'Kamami','586761'),
 'AUX6-REGULATOR': ('Pololu','4092','Kamami','586583'),
 'PWM-CONTROLLER': ('Adafruit','815 revC','Kamami','199856'),
 'PWM-U1-ADAPTER': (None,None,'Kamami','575070'),
 'AUX-GROUND-DISTRIBUTION': ('WAGO','221-415','Kamami','1188363'),
 'PWM-LEVEL-TRANSLATOR': ('Texas Instruments','SN74LVC8T245PW','TME','SN74LVC8T245PW'),
 'PWM5-REGULATOR': ('STMicroelectronics','L78L05ACZ','TME','L78L05ACZ'),
 'PWM-PROTOTYPE-BOARD': ('Adafruit','1608','Conrad','1516556'),
}
SUPPORT = [
 'hardware/build-readiness/p0-order-cart.json',
 'hardware/manufacturing/one-batch-prototype-r1/batch-plan.json',
 'hardware/manufacturing/one-batch-prototype-r1/electronics-small-parts.json',
 'hardware/electronics/full-cat/f-pwm-axial-r1/materials.json',
 'hardware/electronics/full-cat/assembly-materials-k3-r1/materials.json',
 'hardware/electronics/full-cat/pi-interface-final-r2/suppliers.json',
 'hardware/electronics/full-cat/power-wire-sku-r1/card.json',
 'hardware/electronics/full-cat/aux-wire-material-r1/card.json',
 'hardware/manufacturing/one-batch-prototype-r24/wire-sources.json',
 'hardware/manufacturing/one-batch-prototype-r26/insulation-sources.json',
 'hardware/electronics/full-cat/connection-map-e4-r1/netlist.json',
 'hardware/electronics/full-cat/body-harness-w5-r2/interface.json',
 'hardware/electronics/full-cat/protection-selection-r2/branch-protection.json',
 'hardware/manufacturing/one-batch-prototype-r5/fuse-order-minima.json',
 'hardware/manufacturing/one-batch-prototype-r18/fixed-logic-wire.json',
 'hardware/cad/studies/rear-fuse-cassette-r2/materials-delta.json',
]

def sources():
    p0 = {r['id']:dict(r, supplier=store)
          for store, rows in read(SUPPORT[0])['stores'].items() for r in rows}
    extra = {r['id']:r for r in read(SUPPORT[1])['additional_exact_product_candidates']}
    passive = {r['manufacturer_part']:r for r in read(SUPPORT[2])['exact_passives']}
    return p0, extra, passive

def bind(q):
    p0, extra, passive = sources()
    materials = {r['id']:r for r in read(SUPPORT[3])['parts']}
    materials.update({r['id']:r for r in read(SUPPORT[4])['lines']})
    rows = []
    for r in q['lines']:
        if r['id'].startswith('supplier:'):
            continue
        ident = r['id']
        b = dict(quantity_id=ident, planning_quantity=r['planning_quantity'],unit=r['unit'],
                 inherited_quantity_source=r['source'],manufacturer=None,manufacturer_part=None,
                 supplier=None,supplier_sku=None,supplier_url=None,
                 product_evidence=r['source'],retail_minimum=None,retail_multiple=None,
                 commercial_refresh='Phase2 before one purchase; no current price/stock/delivery promise.')
        if ident.startswith('p0:'):
            key = ident[3:]
            maker, part, sku = P0[key]
            b.update(manufacturer=maker,manufacturer_part=part,supplier=p0[key]['supplier'],
                     supplier_sku=sku,supplier_url=p0[key]['url'])
        elif ident.startswith('additional:'):
            key = ident[11:]
            maker, part, supplier, sku = EXTRA[key]
            b.update(manufacturer=maker,manufacturer_part=part,supplier=supplier,
                     supplier_sku=sku,supplier_url=extra[key]['url'])
        elif ident.startswith('passive:'):
            key = ident[8:]
            b.update(manufacturer=key.split()[0],manufacturer_part=key.split()[1],
                     supplier=passive[key]['supplier'],supplier_url=passive[key]['url'],
                     supplier_sku='product page '+passive[key]['url'].rstrip('/').split('/')[-1])
        elif ident in materials:
            m = materials[ident]
            b.update(manufacturer=m['manufacturer'],manufacturer_part=m.get('manufacturer_sku',m.get('sku')),
                     supplier_sku=m.get('supplier_sku',m.get('sku')),
                     supplier_url=m.get('supplier_url'),product_evidence=r['source'])
            b['supplier'] = {'consumable:p0:5:abrasive':'Allegro, exact EAN product',
                             'consumable:p0:5:IPA':'Gotronik'}.get(ident,
                             (m.get('supplier_sku','').split(':')[0] or 'TME') if 'consumable:' in ident else 'TME')
        elif ident.startswith('fuse:'):
            part = ident[5:]
            b.update(manufacturer='Littelfuse',manufacturer_part=part,supplier='TME',supplier_sku=part)
            b['supplier_url'] = p0['PI-INPUT-FUSE-HOLDER']['url'] if part=='FHAC0001ZXJ' else p0.get('SERVO-FUSES' if part=='0287004.PXCN' else 'PI-INPUT-FUSE',{}).get('url')
            if part=='0242.100UAT1':
                minimum=read('hardware/manufacturing/one-batch-prototype-r5/fuse-order-minima.json')['rows'][-1]
                assert minimum['sku']==part
                b.update(supplier_url=minimum['supplier_candidate_url'],retail_minimum=1,retail_multiple=1)
            if part=='0287001.PXCN':
                b['supplier_url'] = None  # Preserve exact identity; do not invent an offer URL.
        elif ident.startswith('connector:'):
            part = ident[10:]
            b.update(manufacturer='Molex',manufacturer_part=part)
            known = {
              '430250200': ('WM1783-ND','https://www.digikey.pl/pl/products/detail/molex/0430250200/252496'),
              '2147612113': ('900-2147612113-ND','https://www.digikey.com/en/products/detail/molex/2147612113/12352891'),
              '2147611113': ('900-2147611113-ND','https://www.digikey.com/en/products/detail/molex/2147611113/12352926'),
              '2147631112': ('900-2147631112-ND','https://www.digikey.co.uk/en/products/detail/molex/2147631112/12353007'),
            }
            if part in known:
                sku,url = known[part]
                b.update(supplier='DigiKey',supplier_sku=sku,supplier_url=url)
            if part=='2147612113':
                b['supplier_constraint']='Main DigiKey offer shows3000 minimum and no distributor stock; marketplace is not validated for2pieces. Do not order3000 or assert near-term availability.'
            if part=='2147611113':
                b['supplier_constraint']='DigiKey page shows0 stock and20weeks manufacturer lead time; find exact local alternative, not a different length/contact.'
        elif ident.startswith('wire:HELU2350'):
            colour = 'red' if ident.endswith('red') else 'black'
            m = read(SUPPORT[6])[colour]
            b.update(manufacturer='HELU',manufacturer_part=m['manufacturer_part'],supplier='TME',
                     supplier_sku=m['tme_symbol'],supplier_url=m['url'])
        elif ident.startswith('wire:HELU2330'):
            part = ident.split(':')[1][4:]
            b.update(manufacturer='HELU',manufacturer_part=part)
        elif ident.startswith('wire:fixed:'):
            b.update(manufacturer='Donau Elektronik',manufacturer_part=ident.split(':')[-1][6:],
                     supplier=None,supplier_sku=None)
        elif ident.startswith('filament:'):
            b.update(manufacturer='Sunlu',manufacturer_part='PETG1.75mm1kgBlack',supplier='Botland',
                     supplier_sku='24167',supplier_url=p0['PETG']['url'])
        elif ident=='tie:111-02370':
            b.update(manufacturer='HellermannTyton',manufacturer_part='111-02370',supplier='TME',supplier_sku='T18I-BK',
                     retail_minimum=100,retail_multiple=100)
        elif ident=='splice:WAGO221-412':
            b.update(manufacturer='WAGO',manufacturer_part='221-412',supplier='Kamami',supplier_sku='1188364')
        elif ident=='wire:moving-PWM-HELU23308':
            m=read(SUPPORT[8])['supplier']
            b.update(manufacturer='HELU',manufacturer_part=m['manufacturer_part'],supplier='TME',
                     supplier_sku=m['symbol'],supplier_url=m['url'])
        elif ident=='insulation:RNF-100-1/8-9-STK':
            m=read(SUPPORT[9])
            b.update(manufacturer='TE Connectivity',manufacturer_part=m['manufacturer']['part'],
                     supplier='TME',supplier_sku=m['supplier']['sku'],supplier_url=m['supplier']['url'],
                     retail_minimum=6,retail_multiple=6)
        elif ident.startswith('Pi:'):
            m=read(SUPPORT[5])['GPIO']['housing' if 'housing' in ident else 'wire']
            b.update(manufacturer='Pololu',manufacturer_part=m['sku'].replace('Pololu',''),
                     supplier='Pololu',supplier_sku=m['sku'],supplier_url=m['url'],
                     retail_minimum=1,retail_multiple=1,pack_contents=m['pack'])
        elif ident=='insulation:Pi:RNF-100-3/8-0-STK':
            m=read(SUPPORT[5])['insulation']['MAIN_common_outer']
            b.update(manufacturer='TE Connectivity',manufacturer_part=m['TE_part'],supplier='TME',
                     supplier_sku=m['sku'],supplier_url=m['url'])
        elif ident=='consumable:solder:T0051402499':
            b.update(manufacturer='Weller',manufacturer_part='T0051402499')
        else:
            raise AssertionError('Unassigned role: '+ident)
        assert b['manufacturer_part'] or (b['supplier_sku'] and b['supplier_url']), ident
        rows.append(b)
    assert len(rows)==83 and len({r['quantity_id'] for r in rows})==83
    overrides=read('hardware/manufacturing/nonfastener-catalog-r1/supplier-overrides.json')['rows']
    by={r['quantity_id']:r for r in rows}
    assert len({r['quantity_id'] for r in overrides})==len(overrides)
    for override in overrides:
        b=by[override['quantity_id']]
        assert b['manufacturer_part']==override['manufacturer_part']
        b.update(override)
    return rows

def consolidate(q, bindings):
    by = {b['quantity_id']:b for b in bindings}
    lines = []
    for r in q['lines']:
        r=copy.deepcopy(r)
        if r['id'] in by:
            r['product_binding']=by[r['id']]
        lines.append(r)
    ids=['p0:DATA-JUNCTIONS-P0','p0:DISTRIBUTION-G2-P0','p0:DISTRIBUTION-LEGS-P0','additional:AUX-GROUND-DISTRIBUTION']
    roles=[r for r in lines if r['id'] in ids]
    assert len(roles)==4 and all(by[r['id']]['manufacturer_part']=='221-415' for r in roles)
    assert all(by[r['id']]['supplier']=='Kamami' and by[r['id']]['supplier_sku']=='1188363' for r in roles)
    total=sum(r['planning_quantity'] for r in roles)
    assert total==16 and all(r['unit'] in ('pcs','szt.') for r in roles)
    merged=dict(id='supplier:Kamami:1188363',name='WAGO221-415',unit='pcs',planning_quantity=total,
                product_binding=copy.deepcopy(by[ids[0]]),roles=roles,
                source='hardware/manufacturing/nonfastener-catalog-r1/catalog.json')
    lines=[r for r in lines if r['id'] not in ids]+[merged]
    assert len(lines)==len(q['lines'])-3
    assert len({r['id'] for r in lines})==len(lines)
    return lines

def validate_current_roles(q,net):
    rows={r['id']:r for r in q['lines']}
    legs=[r for r in net['fuses'] if r['holder']=='MTA0100335']
    assert {r['ref'] for r in legs}=={'F_FL','F_FR','F_RL','F_RR'}
    assert all('MINIVAL10A' in r['sku'] for r in legs)
    assert rows['p0:FUSE-HOLDERS']['planning_quantity']==len(legs)==4
    assert rows['p0:FUSES']['planning_quantity']>=len(legs)
    assert len(net['drive_assignments'])==15
    assert rows['p0:DRIVE-12']['planning_quantity']==12
    assert rows['additional:AUX-SERVO-MG92B']['planning_quantity']==3
    return dict(active_minival_refs=[r['ref'] for r in legs],active_minival_holders=4,
                miniVAL_purchase_quantity=10,drives=15,removed_roles=[],physical_pass=False)

def build():
    if (BATCH/'manifest.json').exists():
        assert '--finalize-draft' in sys.argv,'Preserve completed stage'
        tracked=subprocess.run(['git','ls-files','--',str(BATCH.relative_to(ROOT)),str(OUT.relative_to(ROOT))],
                               cwd=ROOT,capture_output=True,text=True,check=True)
        assert not tracked.stdout,'Never rewrite a committed package'
        old=read((BATCH/'manifest.json').relative_to(ROOT))
        own_prefixes=[BATCH.relative_to(ROOT).as_posix()+'/',OUT.relative_to(ROOT).as_posix()+'/']
        unchanged=dict(old,files=[r for r in old['files'] if not any(r['path'].startswith(p) for p in own_prefixes)
                                  and r['path'] not in ('tools/manufacturing/nonfastener_catalog_r1.py',
                                                        'tools/manufacturing/test_nonfastener_catalog_r1.py')])
        assert verify(ROOT,unchanged)['integrity_ok'],'Inherited evidence changed during draft'
    q=read((PARENT/'one-order-quantities.json').relative_to(ROOT))
    parent=read((PARENT/'manifest.json').relative_to(ROOT))
    assert verify(ROOT,parent)['integrity_ok']
    bindings=bind(q)
    checks=validate_current_roles(q,read(SUPPORT[10]))
    OUT.mkdir(parents=True,exist_ok=True)
    pending=[r['quantity_id'] for r in bindings if not r['supplier_url'] or r.get('supplier_constraint')]
    catalog=dict(status='ALL_CURRENT_NONFASTENER_IDENTITIES_BOUND_NOT_COMPLETE_K2',rows=bindings,
                 role_count=83,unbound_identity_count=0,retail_offer_or_availability_pending=pending,
                 source_sha256={rel:sha(ROOT/rel) for rel in SUPPORT},role_checks=checks,
                 K2_complete=False,K3_complete=False,W5_complete=False,phase1_percent=70,
                 no_purchase=True,physical_pass=False,
                 remaining='Resolve listed commercial offers; finish W5 then reconcile stock and any changed terminal/holder SKU. Printed MG92B horn/retention remains replaceable provisional; do not add rejected flag terminals.')
    save(OUT/'catalog.json',catalog)
    BATCH.mkdir(parents=True,exist_ok=True)
    selection=copy.deepcopy(read((PARENT/'selection.json').relative_to(ROOT)))
    selection.update(parent_selection_sha256=sha(PARENT/'selection.json'),
                     nonfastener_catalog='hardware/manufacturing/nonfastener-catalog-r1/catalog.json',
                     K2_complete=False,phase1_percent=70)
    selection['conditions']=[s.replace('13/20=65%','14/20=70%').replace('E3/E4/W5/K2/K3/A2/A3','E3/W5/K2/K3/A2/A3')
                             for s in selection['conditions']]
    q['lines']=consolidate(q,bindings)
    former_line_count=q.get('line_count')
    q.update(line_count=len(q['lines']),selected_prints=(BATCH/'selection.json').relative_to(ROOT).as_posix(),
             nonfastener_catalog=selection['nonfastener_catalog'],K2_complete=False)
    assert len(q['lines'])==109
    save(BATCH/'selection.json',selection)
    save(BATCH/'one-order-quantities.json',q)
    pins={r['path']:r['sha256'] for r in parent['files']}
    inherited=dict(pins)
    for path in [ROOT/rel for rel in SUPPORT]+list(OUT.iterdir())+[BATCH/'selection.json',BATCH/'one-order-quantities.json',
                 PARENT/'manifest.json',ROOT/'tools/manufacturing/nonfastener_catalog_r1.py',
                 ROOT/'tools/manufacturing/test_nonfastener_catalog_r1.py']:
        rel=path.relative_to(ROOT).as_posix()
        digest=sha(path)
        assert rel not in pins or pins[rel]==digest,rel
        pins[rel]=digest
    m=copy.deepcopy(parent)
    m.update(files=[dict(path=k,sha256=v) for k,v in sorted(pins.items())],
             parent_pins_preserved=len(inherited),phase1_percent=70,K2_complete=False,
             quantity_rows=109,new_stls=0,newly_selected_stls=0)
    integrity=verify(ROOT,m)
    assert integrity['integrity_ok'] and not verify(ROOT,m,True)['integrity_ok']
    save(BATCH/'manifest.json',m)
    save(BATCH/'validation.json',dict(integrity=integrity,parent_pins_preserved=len(inherited),
         print_jobs_unchanged=71,installed_petg_parts=110,fit_samples=4,quantity_rows=109,
         former_stale_line_count=former_line_count,nonfastener_roles=83,WAGO221415_consolidated=16,
         retail_offer_or_availability_pending=pending,role_checks=checks,phase1_percent=70,
         K2_complete=False,physical_pass=False))
    print(json.dumps(dict(pins=len(pins),preserved=len(inherited),roles=83,rows=109,pending=pending,percent=70)))

if __name__=='__main__':
    build()
