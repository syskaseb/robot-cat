"""Bind reconciled installed roles to commercial identities, with open gates."""
import json,math,time,re
from pathlib import Path
from collections import Counter
from plan_current_harness_interfaces import ROOT,BASE,SHA
from current_work_guard import check
from release_check import verify,REQUIRED_GATES


def matches(size,r):
    d=r['dimensions_mm']
    m=re.fullmatch(r'M([\d.]+)x(\d+)',size)
    if m:return d.get('d')==float(m[1]) and d.get('L')==int(m[2])
    m=re.fullmatch(r'M([\d.]+) nut',size)
    if m:
        if d.get('d')==float(m[1]) and 'AF' in d:return True
        return float(m[1]) in (6,10) and d.get('AF')=={6:10,10:17}[float(m[1])] and 'L' not in d
    m=re.fullmatch(r'M([\d.]+) washer(?: OD([\d.]+))?',size)
    if m:
        diameter=float(m[1]);od=float(m[2]) if m[2] else {6:12,10:20}[diameter]
        return d.get('OD')==od and d.get('ID')=={2:2.2,3:3.2,6:6.4,10:10.5}[diameter]
    return False


def run():
    check();tick=time.monotonic();candidate=BASE/'phase1-purchased-role-plan-r3.json'
    p=json.loads(candidate.read_text());pins=dict(p['source_sha256'])
    proof_file=BASE/'commercial-hardware/washer-checks.json';proof=json.loads(proof_file.read_text())
    assert proof['status']=='COMMERCIAL_WASHERS_CHANGED_MATERIAL_CLEAR' and not proof['errors']+proof['contacts']
    assert len(proof['rows'])==20 and proof['relocated_reopen']
    for f in (candidate,proof_file):pins[f.relative_to(ROOT).as_posix()]=SHA(f)
    pins.update(proof['source_sha256']);pins[proof['native']]=proof['native_sha256']
    roles=[];totals=Counter()
    for row in p['roles']:
        row=dict(row)
        if row['canonical_size']=='M2 washer OD4.3':
            assert row['installed']==20;row.update(canonical_size='M2 washer OD4.5',commercial_overlay=proof_file.relative_to(ROOT).as_posix())
        totals[row['canonical_size']]+=row['installed'];roles.append(row)
    catalog=p['current_catalog'];catalog.append(dict(supplier='KRAFTBERG / TME',supplier_sku='M3X45/D912-A2',
        url='https://www.tme.eu/pl/details/m3x45_d912-a2/sruby/kraftberg/',
        dimensions_mm=dict(d=3,L=45,b=18,head_d=5.5,head_h=3,key=2.5,pitch=.5),
        retail_minimum_pieces=100,retail_multiple_pieces=100,
        evidence='TME nominal45/head5.5x3/key2.5; DIN912 partial-thread family18mm. Nut39..41.4mm from head lies within last18mm. No physical torque or tolerance approval.'))
    tail=json.loads((BASE/'tail-mount-checkpoint/selection.json').read_text())
    catalog.append(dict(supplier='Rosentaler',supplier_sku='0200912020030',
        url=tail['shared_rear_frame_hardware']['supplier_url'],dimensions_mm=dict(d=2,L=30,b=30),
        retail_minimum_pieces=1,retail_multiple_pieces=1))
    products=[]
    for size,count in sorted(totals.items()):
        found=[r for r in catalog if matches(size,r)]
        assert len(found)==1,(size,[r['supplier_sku'] for r in found])
        r=found[0];spare=max(1,math.ceil(.2*count));planned=count+spare
        minimum=r['retail_minimum_pieces'];multiple=r['retail_multiple_pieces']
        order=math.ceil(max(planned,minimum)/multiple)*multiple
        products.append(dict(size=size,installed=count,project_spare=spare,planned=planned,
            retail_nominal_order=order,pack_excess=order-planned,purchased=0,
            supplier=r['supplier'],supplier_sku=r['supplier_sku'],url=r['url'],dimensions_mm=r['dimensions_mm'],
            allocations=[dict(id=x['id'],installed=x['installed']) for x in roles if x['canonical_size']==size]))
    assert sum(r['installed'] for r in products)==sum(r['installed'] for r in roles)
    for c in p['components']:
        if c['id']=='Head pitch bearing':c.update(manufacturer='SMB Bearings',supplier='SMB Bearings',supplier_sku='688-2RS',
            url='https://www.smbbearings.com/firebrick/ckeditor/plugins/upload/Uploads/Documents/bearingpdfs/688-2RS-miniature-bearing-8x16x5mm.pdf',dimensions_mm=dict(ID=8,OD=16,B=5))
        if c['part']=='Adafruit1208':c.update(manufacturer='Adafruit',supplier_sku='1208',url='https://www.adafruit.com/product/1208',
            commercial_unit='pack3 bare boards; installed1, package surplus2; headers separate')
        if c['part'] in ('M20-7821242','M20-9991245'):
            c.update(manufacturer='Harwin',supplier_sku=c['part'],url='https://www.harwin.com/products/'+c['part'])
        if c['id']=='WAGO opposed inline':
            c.update(manufacturer='WAGO',supplier_sku='221-2411',url='https://www.wago.com/global/installation-terminal-blocks-and-connectors/inline-splicing-connector-with-levers/p/221-2411')
        assert c.get('part') and c['installed']>0,(c['id'],'Unbound identity')
    connectorfacts=ROOT/'hardware/reference/u1-socket-connectors-2026-10-12/facts.json'
    pins[connectorfacts.relative_to(ROOT).as_posix()]=SHA(connectorfacts)
    for f in (Path(__file__),ROOT/'tools/cad/compose_phase1_purchased_set.py'):
        pins[f.relative_to(ROOT).as_posix()]=SHA(f)
    for n,h in pins.items():assert SHA(ROOT/n)==h,n
    result=dict(p,status='K2_CURRENT_PURCHASED_IDENTITIES_AND_INSTALLED_HARDWARE_SELECTED',selected=True,K2_complete=True,
        roles=roles,installed_hardware=dict(sorted(totals.items())),hardware_products=products,
        current_catalog=None,gaps=[],resolved_gaps=p['gaps'],commercial_washer_overlay=proof_file.relative_to(ROOT).as_posix(),
        new_electrical_approval=False,material_draws_and_tooling='K3, not another copy of these component counts',
        scope='One installed purchased identity/fastener allocation set for current open prototype, after explicit P0/CP2 substitutions. Nominal hardware sizes and20commercial washer overlay; electrical E3 and physical delivery/fit gates remain separate.',
        gates=['Actual servo factory horn/screw inventory and fit in phase2; no invented accessory totals',
            'Electrical fuse/source candidates remain E3 conditional; no power approval',
            'Commercial stock/prices/packs refreshed before any phase2 purchase; none purchased',
            'Delock/K1474 and socket/contact delivered fit reservations remain explicit phase2 gates'],
        source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3))
    f=BASE/'phase1-current-purchased-selection-r3.json';f.write_text(json.dumps(result,indent=2)+'\n',newline='\n');pins[f.relative_to(ROOT).as_posix()]=SHA(f)
    manifest=dict(schema_version=1,readiness='prototype',result_id='K2',selected=True,K2_complete=True,physical_pass=False,
        scope=result['scope'],selection=f.relative_to(ROOT).as_posix(),files=[dict(path=n,sha256=h) for n,h in sorted(pins.items())],
        gates={g:dict(status='open',reason='Physical/electrical/wholeassembly readiness is not implied by nominal identity reconciliation.') for g in REQUIRED_GATES})
    assert verify(ROOT,manifest)['integrity_ok']
    f=BASE/'phase1-purchased-manifest-r3.json';f.write_text(json.dumps(manifest,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(hardware_products=len(products),roles=len(roles),components=len(p['components']),seconds=result['worker_seconds'])))


if __name__=='__main__':run()
