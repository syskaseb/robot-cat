"""Reconcile actual installed roles, not historical shopping-cart totals.

This candidate deliberately cannot award K2 while a commercial size differs
from the verified model. No purchases, no price or electrical safety claim.
"""
import json,time
from collections import Counter
from pathlib import Path
from plan_current_harness_interfaces import ROOT,BASE,SHA
from current_work_guard import check


def run():
    check();tick=time.monotonic();pins={};roles=[];components=[];gaps=[]
    prefix=BASE.relative_to(ROOT).as_posix()+'/'
    def read(name):
        p=ROOT/name;pins[name]=SHA(p);return json.loads(p.read_text())
    def local(name):return read(prefix+name)
    def group(owner,source,items,note=''):
        for size,count in items.items():
            assert isinstance(count,int) and count>0
            roles.append(dict(id=owner+':'+size,owner=owner,size=size,installed=count,source=source,note=note))
    catalog=read('hardware/manufacturing/one-batch-prototype-r53/nonfastener-catalog.json')
    catalog={r['quantity_id']:r for r in catalog['rows']}
    fast=read('hardware/manufacturing/one-batch-prototype-r53/fixed-fastener-cart.json')['rows']
    head=local('head-mount-checkpoint/selection.json')
    tail=local('tail-mount-checkpoint/selection.json')
    m5=local('mounting-checkpoint/current-M5-selection.json')
    e1=local('body-harness-checkpoint/e1-selection.json')
    w5=local('body-harness-checkpoint/w5-nominal-material-selection.json')
    net=read('hardware/electronics/full-cat/connection-map-e4-r1/netlist.json')
    pins['hardware/electronics/power-platform/MONTAZ-P0.md']=SHA(ROOT/'hardware/electronics/power-platform/MONTAZ-P0.md')
    group('P0 base', 'MONTAZ-P0 P3 step2', {'M2.5x12':4,'M2.5 nut':4,'M3x16':4,'M3 nut':4})
    group('P0 battery R4/R6','MONTAZ-P0 P3 step6',{'M2x6':8,'M2 nut':8,'M2 washer OD5':16})
    group('Head internal','head-mount-checkpoint/selection.json',head['internal_hardware_totals'])
    # Lower P0 front bolts/nuts/washers allocated HERE, not added again.
    group('Neck front shared','head-mount-checkpoint/selection.json',
        {'M2x10':4,'M2x12':4,'M2 nut':8,'M2 washer OD5':16},'Replaces old upperM2x14; lowerP0 reused once')
    group('MAIN neck','head-mount-checkpoint/selection.json',
        {'M2x12':2,'M2 nut':2,'M2 washer OD5':2},'E1 integral feet replace TWO upper washers; M5 explicitly excludes MAIN')
    tail_counts=Counter()
    for row in tail['tail_internal_hardware']['groups']:
        tail_counts[row['item']]+=row['quantity']
    assert dict(tail_counts)==tail['tail_internal_hardware']['nominal_internal_tail_totals']
    # Source has a selected explicit nominal-total table; do not count the
    # rear shared frame kit or bearing a second time through group totals.
    group('Tail internal','tail-mount-checkpoint/selection.json',
        {'M3x16':4,'M3x30':1,'M3x12':2,'M2x12':10,'M3 nut':7,'M2 nut':14,'M2x10':4})
    group('Tail rear shared','tail-mount-checkpoint/selection.json',
        {'M2x30':4,'M2 nut':4,'M2 washer OD5':8},'Replaces rearP0M2x10 and historicalM2x14; no second rear kit')
    group('M5 current boards','mounting-checkpoint/current-M5-selection.json',
        dict(m5['quantities'],M2_washer_OD4p3_ID2p2_t0p3=20),
        'E1 replaces FOUR GPIO/PCA upper washers with integral PETG feet; M5 MAIN excluded')
    group('Tail wire fixture','tail-wiring-checkpoint/selection.json',
        {'M3x10':2,'M3 nut':2,'M3 washer OD7':2})
    local('tail-wiring-checkpoint/selection.json')
    group('W5 source detachable rail','body-harness-checkpoint/w5-nominal-material-selection.json',
        {'M3x8':2,'M3 nut':2,'M3 washer OD7':2})
    group('W5 receiver cap','body-harness-checkpoint/w5-nominal-material-selection.json',{'M2x14':1,'M2 nut':1})
    group('Current four leg station feet','tools/cad/plan_current_data_ground_mounts.py',
        {'M3x16':4,'M3 nut':4,'M3 washer OD7':4},
        'Four current low foot load paths on retained P0 boss bores; not old Deck/Bank fastening')
    f=ROOT/'tools/cad/plan_current_data_ground_mounts.py';pins[f.relative_to(ROOT).as_posix()]=SHA(f)
    # S0 body fixing is integral in CP2; old separate Deck/M2 kit is retired.
    read('hardware/electronics/full-cat/source-switch-selected-r1/interface.json')
    group('S0 terminals and case','source-switch-selected-r1/interface.json',
        {'M6x20':2,'M6 nut':2,'M6 washer':4,'M10 nut':2,'M10 washer':2},
        'Retained switch hardware only, not old Deck attachment2M2x12')
    def add(role,key,count):
        old=catalog[key]
        components.append(dict(id=role,installed=count,manufacturer=old.get('manufacturer'),
            part=old.get('manufacturer_part') or old.get('supplier_sku'),supplier=old['supplier'],
            supplier_sku=old['supplier_sku'],url=old['supplier_url'],catalog_role=key,
            purchased=0,electrical_selection_conditional=role.startswith(('Fuse','Source','Battery'))))
    for role,key,count in [
        ('Drive ST3215','p0:DRIVE-12',12),('Drive MG92B','additional:AUX-SERVO-MG92B',3),
        ('BUS','p0:BUS',1),('MAIN','p0:REG-MAIN',1),('AUX','additional:AUX6-REGULATOR',1),
        ('PCA9685','additional:PWM-CONTROLLER',1),('Battery','p0:BATTERY',1),
        ('Battery monitor','p0:BATTERY-MONITOR',1),('Battery straps','p0:BATTERY-STRAPS-P0',2),
        ('Source S0','p0:MAIN-SWITCH',1),('Source S1','p0:MOTOR-STOP-MANUAL-P0',1),
        ('Source XT60 pair','p0:XT60',1),('WAGO power221615','p0:DISTRIBUTION',4),
        ('WAGO 221415','p0:DATA-JUNCTIONS-P0',16),('MTA four legs','p0:FUSE-HOLDERS',4),
        ('MTA servo bank','p0:SERVO-HOLDERS-P0',12),
        ('Bank TE input','p0:TERMINAL-SERVO-IN-P0',12),
        ('Bank TE output','p0:TERMINAL-SERVO-OUT-P0',12),
        ('S0 ring M10','p0:TERMINAL-S0-P0',2),('S1 rings','p0:TERMINAL-S1-P0',4),
        ('F0 holder','p0:MAIN-FUSE-HOLDER',1),('Small FHAC holders','fuse:FHAC0001ZXJ',5),
        ('JR extension','additional:MG92B-JR-EXTENSION',3),
        ('E2 source housing','connector:430250200',1),('E2 module housing','connector:430200201',1),
        ('E2 source V contact','connector:2147612113',1),('E2 source G contact','connector:2147611113',1),
        ('E2 module V contact','connector:2147632113',1),('E2 module G contact','connector:2147631112',1),
    ]:add(role,key,count)
    fusecounts=Counter(r['sku'] for r in net['fuses'])
    for sku,count in fusecounts.items():
        keys=[k for k,v in catalog.items() if v.get('manufacturer_part')==sku]
        if sku.startswith('MTA MINIVAL'):keys=['p0:FUSES']
        assert len(keys)==1,(sku,keys)
        add('Fuse '+sku,keys[0],count)
    for part,count in e1['components'].items():
        key=next((k for k,v in catalog.items() if v.get('manufacturer_part')==part),None)
        if part=='Adafruit1608':key='additional:PWM-PROTOTYPE-BOARD'
        if key:add('E1 '+part,key,count)
        else:components.append(dict(id='E1 '+part,part=part,installed=count,
            evidence=prefix+'body-harness-checkpoint/e1-selection.json',purchased=0))
    add('Remote R7 R8 R9','passive:Vishay MRS16000C1002FCT00',3)
    add('Pi power K1474','p0:PI-POWER-CABLE',1)
    add('Pi BUS USB cable','p0:BUS-USB-CABLE-P0',1)
    components.append(dict(id='Pi passive angle adapter',part='Delock60047',installed=1,
        evidence=prefix+'body-harness-checkpoint/e1-selection.json',
        url=e1['USB_receiver']['manufacturer_source'],provisional_fit_reservation=True,purchased=0))
    components.extend([
        dict(id='Owned Pi4B',part='Raspberry Pi4B',installed=1,owned=True,purchased=0),
        dict(id='WAGO opposed inline',part='221-2411',installed=8,
            evidence='hardware/reference/wago-inline-2212411/source.json',purchased=0),
        dict(id='Head pitch bearing',part='688-2RS 8x16x5',installed=1,
            evidence=prefix+'head-mount-checkpoint/selection.json',purchased=0),
        dict(id='Head yaw and tail bearings',part='SKF608-2Z',installed=3,
            evidence='hardware/manufacturing/one-batch-prototype-r53/fixed-fastener-cart.json',purchased=0),
    ])
    pins['hardware/reference/wago-inline-2212411/source.json']=SHA(ROOT/'hardware/reference/wago-inline-2212411/source.json')
    for role in roles:
        size=role['size']
        # Normalize only naming, never installed quantities or commercial OD.
        if size.startswith('M2 ') or size.startswith('M2_'):
            if 'nut' in size:size='M2 nut'
            elif 'OD4p3' in size:
                size='M2 washer OD4.3';gaps.append(dict(id=role['id'],cause='Model washerOD4.3; catalog DIN433OD4.5. Changed interface needs actual material check, not a nominal relabel.'))
            elif 'OD4.5' in size or 'DIN433' in size:size='M2 washer OD4.5'
            elif 'washer' in size:size='M2 washer OD5'
        if size.startswith('M3 ') or size.startswith('M3_'):
            if 'nut' in size:size='M3 nut'
            elif 'OD9' in size:size='M3 washer OD9'
            elif 'washer' in size:size='M3 washer OD7'
        role['canonical_size']=size
    totals=Counter()
    for r in roles:totals[r['canonical_size']]+=r['installed']
    result=dict(status='CURRENT_PURCHASED_ROLE_RECONCILIATION_OPEN',result_id='K2',selected=False,K2_complete=False,
        fixed_total=20,physical_pass=False,purchase_authorized=False,
        roles=roles,installed_hardware=dict(sorted(totals.items())),components=components,
        drive_count=sum(r['installed'] for r in components if r['id'].startswith('Drive ')),
        current_catalog=fast,old_cart_quantities_NOT_selected=True,
        substitutions=['Old DeckR2/R3/MAINR5 hardware NOT retained','Rear4M2x30 replaces4M2x10/old14',
          'Front4M2x10 counted once at neck','MAIN2upper washers and GPIO/PCA4upper washers retired',
          '1208+Harwin headers replace old575070 adapter','No old bankDeck/Guard metal kit; CP2 integral seats',
          'SourcepowerE1/W5 ties/lacing overlap belongs K3, not an extra installed kit'],
        gates=['Delivered servo horn/screw kits must be inventoried; do not invent factory accessory quantities',
            'Electrical fuse/source candidates remain E3 conditional; no power authorization',
            'Complete commercial fastener binding, including M3x45 and washer mismatch'],
        gaps=gaps,source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3))
    assert result['drive_count']==15
    path=BASE/'phase1-purchased-role-plan.json';path.write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(roles=len(roles),component_rows=len(components),gaps=len(gaps),seconds=result['worker_seconds'])))


if __name__=='__main__':run()
