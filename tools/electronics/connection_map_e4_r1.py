"""Selected prototype assembly schematic. No hardware I/O, ROS or custom PCB.

Copper connectivity is separate from regulator/signal transfer and passives.
Physical deliveries still require the explicitly listed phase-2 checks.
"""
import argparse
import copy
import csv
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/electronics/full-cat/connection-map-e4-r1'
OLD = ROOT / 'hardware/manufacturing/one-batch-prototype-r34'
BATCH = ROOT / 'hardware/manufacturing/one-batch-prototype-r35'
BASE = 'hardware/electronics/full-cat/netlist-r1/netlist.json'
POP = 'hardware/electronics/full-cat/pwm-carrier-r3/population.json'
PI = 'hardware/electronics/full-cat/pi-interface-final-r2/wiring-card.json'
E2 = 'hardware/electronics/full-cat/pwm-complete-e2-r1/interface.json'
SCH = 'hardware/reference/adafruit815-2026-09-26/Adafruit PCA9685 rev C.sch'
PROTECT = 'hardware/electronics/full-cat/protection-selection-r2/branch-protection.json'
START = datetime.fromisoformat('2026-10-01T22:02:39+00:00')
NET_ALIAS = {'G_SYS': 'LOCAL.GND', 'LOGIC3V3': 'LOCAL.LOGIC3V3',
             'PWM5_SW': 'LOCAL.PWM5', 'PWM_REG_IN': 'U_PWM.3',
             'OE_N_3V3': 'U1.22', 'PWM_HEAD_YAW_3V3': 'U1.3',
             'PWM_HEAD_PITCH_3V3': 'U1.4', 'PWM_TAIL_YAW_3V3': 'U1.5',
             'PWM_HEAD_YAW_BUF': 'U1.21', 'PWM_HEAD_PITCH_BUF': 'U1.20',
             'PWM_TAIL_YAW_BUF': 'U1.19', 'PWM_HEAD_YAW_OUT': 'C_HY.PWM',
             'PWM_HEAD_PITCH_OUT': 'C_HP.PWM', 'PWM_TAIL_YAW_OUT': 'C_TY.PWM'}


def read(path):
    p = Path(path)
    return json.loads((p if p.is_absolute() else ROOT / p).read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def pca_outputs():
    """Follow IC PWMn through the onboard resistor to the actual output pad."""
    nets = ET.parse(ROOT/SCH).findall('.//net')
    rows = []
    for channel in range(3):
        input_net = next(n for n in nets if any(p.get('part')=='U1' and
            p.get('pin')=='PWM'+str(channel) for p in n.findall('.//pinref')))
        resistor = next(p for p in input_net.findall('.//pinref') if p.get('part').startswith('R'))
        output_net = next(n for n in nets if any(p.get('part')==resistor.get('part') and
            p.get('gate')==resistor.get('gate') and p.get('pin')=='2' for p in n.findall('.//pinref')))
        pad = next(p for p in output_net.findall('.//pinref') if p.get('part').startswith('JP'))
        rows.append(dict(channel=channel, header=pad.get('part'), pad=pad.get('pin'),
            onboard_resistor=resistor.attrib, source_net=output_net.get('name')))
    assert [(x['header'],x['pad'])for x in rows]==[('JP2','10'),('JP2','7'),('JP2','4')]
    return rows


def component(edges, start, extra=()):
    graph = {}
    for a, b in [(e['a'], e['b']) for e in edges] + list(extra):
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set()).add(a)
    seen, queue = {start}, [start]
    while queue:
        for n in graph.get(queue.pop(), ()):
            if n not in seen:
                seen.add(n)
                queue.append(n)
    return seen


def powered(net, s0=True, s1=True, cut=None):
    edges = copy.deepcopy(net['edges'])
    for f in net['fuses']:
        if f['ref'] != cut:
            edges.append(dict(a=f['ref']+'.in', b=f['ref']+'.out'))
    if s0:
        edges.append(dict(a='S0.in', b='S0.out'))
    if s1:
        edges.extend([dict(a='S1.2', b='S1.3'), dict(a='S1.5', b='S1.6')])
    seen = component(edges, 'BAT.plus')
    # Directional functional transfer, never added to copper-components.
    while True:
        old = set(seen)
        for c in net['converters_functional_not_galvanic']:
            if c['input'] in seen:
                seen.update(component(edges, c['output']))
        if old == seen:
            return seen


def build():
    net = copy.deepcopy(read(BASE))
    edges = net['edges']
    def add(i, a, b, kind='wire', area=None, source=None, sku=None):
        assert not any(e['id'] == i for e in edges), i
        edges.append(dict(id=i, a=a, b=b, kind=kind, area_mm2=area,
                          source=source, sku=sku, physical_pass=False))
    pi = read(PI)
    # Actual selected Pi factory leads, not the superseded 300 mm lead.
    for row in pi['GPIO']:
        e = next(e for e in edges if e['id'] == row['wire'])
        e.update(area_mm2=.129, sku='Pololu1871 + housing1992', source=PI,
                 landing=row['board_landing'], physical_pi_pin=row['pi_pin'])
    for i in ('PI_POWER', 'PI_POWER_G'):
        e = next(e for e in edges if e['id'] == i)
        e.update(area_mm2=.823, sku='JoyIT K1474 EAN4250236828305', source=PI)
    # A keyed, separable two-circuit Micro-Fit replaces the old direct lead.
    edges[:] = [e for e in edges if e['id'] not in ('XP02', 'XP03')]
    add('XP02.source', 'F_PWM.out', 'JPWM_SOURCE.1', area=.519,
        source=E2, sku='2147612113 factory female red225mm')
    add('JPWM_1', 'JPWM_SOURCE.1', 'JPWM_MODULE.1', 'mating_contact', source=E2)
    add('XP02.module', 'JPWM_MODULE.1', 'U_PWM.3', area=.519,
        source=E2, sku='2147632112 factory male red150mm')
    add('XP03.source', 'G_TAIL.3', 'JPWM_SOURCE.2', area=.519,
        source=E2, sku='2147611113 factory female black225mm')
    add('JPWM_2', 'JPWM_SOURCE.2', 'JPWM_MODULE.2', 'mating_contact', source=E2)
    add('XP03.module', 'JPWM_MODULE.2', 'U_PWM.2', area=.519,
        source=E2, sku='2147631112 factory male black150mm')
    # USB is a factory cable; do not fabricate or renumber USB-C contacts.
    add('PI_USB_VBUS', 'PI.USB_C.V', 'PI.USB2_A.VBUS', 'module_internal')
    add('PI_USB_GND', 'PI.USB_C.G', 'PI.USB2_A.GND', 'module_internal')
    for role in ('VBUS', 'GND', 'D+', 'D-'):
        add('USB_BUS_'+role, 'PI.USB2_A.'+role, 'BUS.USB_C.'+role,
            'factory_cable', source=PI, sku='Lanberg CA-USBO-10CU-0005-BK')
    add('BUS_USB_GND', 'BUS.USB_C.GND', 'BUS.G', 'module_internal',
        source='hardware/reference/power-platform-2026-09-23/README.md')
    net['converters_functional_not_galvanic'].extend([
        dict(ref='PI_3V3', input='PI.USB_C.V', output='PI.H1', ground='PI.H6', nominal_v=3.3),
        dict(ref='BUS_LOGIC', input='BUS.USB_C.VBUS', output='BUS.LOGIC', ground='BUS.G')])
    # Port aliases reference actual rev-C plated holes, not a clone board.
    for row in pca_outputs():
        channel=row['channel']
        add('PCA_OUTPUT_'+str(channel), f'PCA.CH{channel}.S', f"PCA.{row['header']}.{row['pad']}",
            'module_internal', source=SCH)
    # Make both passive ends visible. Previously several existed only as net labels.
    for p in net['passives']:
        targets = p['ends']
        p['ends'] = [p['ref']+'.1', p['ref']+'.2']
        for n, target in enumerate(targets, 1):
            if p['ends'][n-1] != target:
                add(f"P_{p['ref']}_{n}", p['ends'][n-1], target, 'local_link', source=POP)
        p['location'] = 'servo-side joint' if p['ref'] in ('R7','R8','R9') else 'fixed cassette'
    # Bind actual Perma-Proto terminal coordinates/copper groups without new layout.
    population = read(POP)
    copper_nets = {}
    for t in population['terminals']:
        copper_nets.setdefault(t['source_copper_group'],set()).add(t['net'])
    assert all(len(n)==1 for n in copper_nets.values()), 'Existing PermaProto copper-group net conflict'
    pads = []
    for row in population['terminals']:
        target = NET_ALIAS.get(row['net'])
        if row['net'].endswith('_UNUSED'):
            target = 'U1.'+str(18-int(row['net'][1])+4)
        if target:
            if target != row['ref']:
                add('PAD_'+row['ref'], 'PCB1608.'+row['ref'], target,
                    'existing_copper_or_selected_local_link', source=POP)
            pads.append(dict(**row, endpoint=target,
                view='Adafruit1608 Eagle component-side XY, NOT mirrored solder-side'))
    net.update(selected='one-batch-prototype-r35', fuses=read(PROTECT)['rows'],
        scope='Nominal prototype assembly schematic and role/pin maps, not energize approval',
        new_stls=0, physical_pass=False,
        no_connect=['BUS.H3.2(V)', 'BUS.H5 entire unused', 'BUS.DC5521',
            'BUS.power_screw', 'BUS.UART_header', 'PCA.JP3.1(V+)', 'PCA.JP3.5(OE)',
            'PCA.JP4 entire externally unused', 'PCA.all16servoV+', 'PCA.power_screw',
            'PCA.CH3..15 externally unused, configureFULL_OFF', 'AUX.EN', 'AUX.PG',
            'AUX.VRP', 'MAIN.EN/PG optional pads', 'PI.J8 other35positions',
            'ST3215 second socket on EACH of12servo bodies'],
        open=['E3 source/fault/lead coordination remains OPEN',
              'W5 remaining body/leg/battery harness lengths and strain relief remain OPEN',
              'G-Tech physical cell-tap/ID position must be identified before connecting P309; semantic tap map only',
              'Delivered U1 adapter routing, connector polarity, continuity and rails require phase2 checks'],
        E4_complete=False, service_connector='430250200 SOURCE /430200201 MODULE',
        adapter='575070 SSOP24 side0.65mm, nominal1:1 pad map conditional on unpowered continuity',
        balance='BAT.B0/B1/B2/B3 -> P309 labels minus/1S/2S/3S; no ID terminal or pack-power bridge')
    save(OUT/'cassette-pad-map.json', dict(terminals=pads,
        internal_links=population['internal_links'], adapter_leads=population['adapter_leads'],
        source=POP, sha256=sha(ROOT/POP), physical_pass=False))
    net['source_bindings'] = {p:sha(ROOT/p) for p in (BASE, POP, PI, E2, SCH, PROTECT,
        'hardware/manufacturing/one-batch-prototype-r28/head-local-interface.json',
        'hardware/manufacturing/one-batch-prototype-r29/tail-wiring-interface.json',
        'hardware/electronics/full-cat/pwm-signal-r1/circuit.json')}
    net['balance_interface'] = [dict(tap=f'BAT.B{n}',to='P309.'+label,
        physical_GTech_cavity=None,ID_must_not_be_used=True) for n,label in enumerate(('minus','1S','2S','3S'))]
    net['drive_assignments'] = [dict(ref=f'{leg}{n}',model='Waveshare22414 ST3215 12V',
        proposed_ID=i*3+n,configured_physically=False) for i,leg in enumerate(('FL','FR','RL','RR')) for n in (1,2,3)]
    net['drive_assignments'] += [dict(ref='C_'+axis,model='TowerProMG92B positional',
        PCA_channel=n,actual_calibration=False)for n,axis in enumerate(('HY','HP','TY'))]
    return net


def pinouts():
    ports = []
    def row(device, sku, physical, role, endpoint, view, evidence, conditional=False):
        ports.append(dict(device=device, sku=sku, physical_pin=physical, role=role,
            endpoint=endpoint, view=view, evidence=evidence,
            nominal_design=True, conditional_delivery=conditional, physical_pass=False))
    pi = read(PI)
    for x in pi['GPIO']:
        role = {1:'3V3',3:'BCM2 SDA',5:'BCM3 SCL',6:'GND',11:'BCM17 U1 /OE'}[x['pi_pin']]
        row('PI','Raspberry Pi4B',str(x['pi_pin']),role,'PI.H'+str(x['pi_pin']),
            '40-pin PHYSICAL numbering; pin1 at square pad; mark housing, no5V pins2/4',PI)
    sch = ET.parse(ROOT/SCH)
    observed = {p.get('pin'): n.get('name') for n in sch.findall('.//net')
                for p in n.findall('.//pinref') if p.get('part')=='JP3'}
    assert observed == {'1':'5.0V','2':'VCC','3':'SDA','4':'SCL','5':'OE','6':'GND'}
    for x in read('hardware/electronics/full-cat/board-interfaces-r1/interfaces.json')['adafruit815']['logic_headers']:
        row('PCA','Adafruit815 revC',x['connector']+'.'+x['pad'],x['function'],
            'PCA.'+x['connector']+'.'+x['pad'],f"component-side Eagle XY {x['xy_mm']}mm",SCH)
    for x in pca_outputs():
        c=x['channel']
        row('PCA','Adafruit815 revC',x['header']+'.'+x['pad'],f'CH{c} signal',f'PCA.CH{c}.S',
            'component-side; labelled channel0/1/2 S row; adjacent V+ NC',SCH)
    expected = {1:'VCCA3V3',2:'DIR3V3',3:'A1',4:'A2',5:'A3',6:'A4GND',7:'A5GND',
        8:'A6GND',9:'A7GND',10:'A8GND',11:'GND',12:'GND',13:'GND',14:'B8',
        15:'B7',16:'B6',17:'B5',18:'B4',19:'B3',20:'B2',21:'B1',22:'/OE',23:'VCCB5V',24:'VCCB5V'}
    for p, role in expected.items():
        row('U1','SN74LVC8T245PW',str(p),role,'U1.'+str(p),
            'TI PW TOP view; notchup left1..12down right24..13down;5750700.65mm side',
            'https://www.ti.com/lit/ds/symlink/sn74lvc8t245.pdf',True)
    for p, role in ((1,'VOUT5V'),(2,'GND'),(3,'VIN fused')):
        row('U_PWM','L78L05ACZ TO92 bag',str(p),role,'U_PWM.'+str(p),
            'BOTTOM lead-exit flat edgeup: left1/centre2/right3; oppositeview3/2/1',
            'hardware/electronics/full-cat/f-pwm-axial-r1/regulator-pinout.json')
    for module, sku in (('MAIN','Pololu4853 D30V33MAL'),('AUX','Pololu4092 D36V50F6')):
        for role in ('VIN','VOUT','GND'):
            row(module,sku,role,role,module+'.'+role,'Use printed pad NAME, not apparent left/right photo',
                'https://www.pololu.com/product/'+('4853' if module=='MAIN' else '4092'))
    for half, sku in (('SOURCE','430250200'),('MODULE','430200201')):
        for p, role in ((1,'PWM_REG_IN red'),(2,'G_SYS black')):
            row('JPWM_'+half,sku,str(p),role,'JPWM_'+half+'.'+str(p),
                'Molded cavity numbers on each housing; opposite faces mirror; no left/right rule',E2,True)
    for p, role in ((1,'D white'),(2,'V red NC'),(3,'G black')):
        row('BUS','Waveshare25514 BusServoAdapterA','H3.'+str(p),role,
            {'D white':'BUS.D','V red NC':'BUS.V','G black':'BUS.G'}[role],
            'Manufacturer H3 numbering; switchB forUSB; power/DC/UART connectorsunused',
            'hardware/reference/power-platform-2026-09-23/README.md')
    for leg in ('FL','FR','RL','RR'):
        for n in (1,2,3):
            device=f'{leg}{n}'
            for color,role,suffix in (('white','DATA','D'),('red','V+ individual4Afuse','V'),('black','GND powerreturn','G')):
                row(device,'Waveshare22414 ST3215 12V',color,role,device+'.'+suffix,
                    'Retain supplied keyed SERVO-end plug; wire-side colour identity, NOT H3 cavitynumber',
                    'sources/st3215-details-23.jpg + sources/st3215-factory-pack.jpg',True)
    for axis in ('HY','HP','TY'):
        for color,role,suffix in (('brown','GND powerreturn','GND'),('red centre','V+ AUX6 through1Afuse','V+'),('yellow/orange outer','PWM afterU1+220ohm','PWM')):
            row('C_'+axis,'TowerProMG92B BotlandDNG24409',color,role,'C_'+axis+'.'+suffix,
                'JR wire-side colour/role; centre redV+; alignKamami586761extension colour-for-colour',
                'sources/mg92b-factory.jpg; https://www.adafruit.com/product/2307',True)
    for pin, role in (('minus','B0 zero'),('1S','B1 cell1'),('2S','B2 sumcell1+2'),('3S','B3 sumcell1+2+3')):
        row('P309','BotlandMOD05015',pin,role,'P309.'+pin,
            'REAR label visible, pinsleft: bottomminus then1S/2S/3Sup; higherpinsNC',
            'sources/p309-labels.jpg',True)
    for p, role in ((2,'front bank IN'),(3,'front bank switchedOUT'),(5,'rear bank IN'),(6,'rear bank switchedOUT')):
        row('S1','NKK S821 DPST ON-OFF',str(p),role,'S1.'+str(p),
            'Manufacturer numbered solder terminals; ON2-3 +5-6, OFF bothopen',
            'hardware/electronics/power-platform/manual-stop-p0.json')
    for p,role in (('in','F0.out input'),('out','P_SYS.1 switchedoutput')):
        row('S0','HELLA6EK002843-002',p,role,'S0.'+p,
            'Project labels on the two switch terminals, not invented manufacturer cavity numbers',
            'hardware/electronics/power-platform/manual-stop-p0.json',True)
    return ports


def validate(net, ports):
    e = net['edges']; checks = {}
    def check(name, value):
        checks[name] = bool(value)
        assert value, name
    drives = [f'{leg}{n}.V' for leg in ('FL','FR','RL','RR') for n in (1,2,3)]+[f'C_{a}.V+' for a in ('HY','HP','TY')]
    states = []
    for s0,s1 in ((False,False),(False,True),(True,False),(True,True)):
        p=powered(net,s0,s1)
        check(f'state_{s0}_{s1}_15drive_supplies',sum(d in p for d in drives)==(15 if s0 and s1 else 0))
        check(f'state_{s0}_{s1}_Pi',('PI.USB_C.V' in p)==s0)
        check(f'state_{s0}_{s1}_PWM5',('LOCAL.PWM5' in p)==(s0 and s1))
        check(f'state_{s0}_{s1}_BUSlogic',('BUS.LOGIC' in p)==s0)
        states.append(dict(S0=s0,S1=s1,drive_supplies=sum(d in p for d in drives),Pi='PI.USB_C.V'in p,PWM5='LOCAL.PWM5'in p))
    branches = {}
    for f in net['fuses']:
        ref=f['ref']; p=powered(net,cut=ref)
        removed=sorted(set(drives)-p)
        expected = (drives if ref=='F0' else [f'{ref[2:]}.V'] if ref.startswith(('F_FL','F_FR','F_RL','F_RR')) and ref[-1:].isdigit()
                    else [f'{ref[2:]}{n}.V' for n in (1,2,3)] if ref in ('F_FL','F_FR','F_RL','F_RR')
                    else ['C_'+ref[2:]+'.V+'] if ref in ('F_HY','F_HP','F_TY')
                    else [f'C_{a}.V+' for a in ('HY','HP','TY')] if ref=='F_AUX' else [])
        check('cut_'+ref,removed==sorted(expected))
        if ref in ('F0','F_PI'): check('cut_'+ref+'_Pi','PI.USB_C.V'not in p)
        if ref in ('F0','F_PWM'): check('cut_'+ref+'_PWM','LOCAL.PWM5'not in p)
        branches[ref]=removed
    check('23fuses',len(branches)==23)
    g=component(e,'BAT.minus'); data=component(e,'BUS.D')
    check('15power_returns',all(f'{l}{n}.G'in g for l in ('FL','FR','RL','RR') for n in (1,2,3)) and all(f'C_{a}.GND'in g for a in ('HY','HP','TY')))
    check('12DATA',all(f'{l}{n}.D'in data for l in ('FL','FR','RL','RR') for n in (1,2,3)))
    check('DATA_isolated_from_V_G',not any(x in data for x in drives+['BAT.minus','BUS.V']))
    rails=['MAIN.VOUT','AUX.VOUT','LOCAL.PWM5','LOCAL.LOGIC3V3']
    check('4positive_domains_separate',all(b not in component(e,a) for i,a in enumerate(rails) for b in rails[i+1:]))
    check('Pi_binding',{p['physical_pin'] for p in ports if p['device']=='PI'}=={'1','3','5','6','11'})
    check('PCA_outputs_follow_chip_and_resistor',[(p['physical_pin'],p['role'])for p in ports
        if p['device']=='PCA' and p['role'].startswith('CH')]==[('JP2.10','CH0 signal'),('JP2.7','CH1 signal'),('JP2.4','CH2 signal')])
    check('U1_24pins',len([p for p in ports if p['device']=='U1'])==24)
    check('U1_enable_and_dual_supply_pinout',{p['physical_pin']:p['role']for p in ports
        if p['device']=='U1' and p['physical_pin']in ('1','2','22','23','24')}==
        {'1':'VCCA3V3','2':'DIR3V3','22':'/OE','23':'VCCB5V','24':'VCCB5V'})
    check('drive45ports',len([p for p in ports if p['device']in [f'{l}{n}' for l in ('FL','FR','RL','RR') for n in (1,2,3)]+['C_HY','C_HP','C_TY']])==45)
    check('21passives',len(net['passives'])==21)
    check('no_unused_B_direct_ground',all('LOCAL.GND'not in component(e,'U1.'+str(p)) for p in range(14,19)))
    check('unique_edges',len({x['id']for x in e})==len(e))
    check('JPWM_correct_polarity','U_PWM.3'in component(e,'JPWM_SOURCE.1') and 'U_PWM.2'in component(e,'JPWM_SOURCE.2'))
    check('JPWM_two_nets_separate','JPWM_SOURCE.2'not in component(e,'JPWM_SOURCE.1'))
    check('OE_not_PCA_OE','PCA.JP3.5'not in component(e,'U1.22'))
    check('Pi_GPIO_edges_5_exact',all(any(x['id']==wire and x['a']==a and x['b']==b for x in e)
        for wire,a,b in [('XL01','PI.H1','LOCAL.LOGIC3V3'),('XL10','PI.H6','LOCAL.GND'),
                       ('XL05','PI.H3','PCA.JP3.3'),('XL06','PI.H5','PCA.JP3.4'),('XL07','PI.H11','U1.22')]))
    check('no_synthetic_hardware_claims',all(not p['physical_pass']for p in ports) and
          all(not x['physical_pass']for x in net['edges']))
    check('regulator_NOT_AUX_motor_supply','C_HY.V+'not in component(e,'U_PWM.1'))
    resistors=[tuple(p['ends']) for p in net['passives'] if p['ref']in ('R1','R2','R3')]
    for n,axis in enumerate(('HY','HP','TY')):
        check('PWM_path_'+axis,'C_'+axis+'.PWM'in component(e,'PCA.CH'+str(n)+'.S',
            resistors+[(f'U1.{n+3}',f'U1.{21-n}')]))
    negative={}
    for name, a, b, test in (
        ('MAIN_AUX_bridge','MAIN.VOUT','AUX.VOUT',lambda x:'AUX.VOUT'not in component(x,'MAIN.VOUT')),
        ('wrong_JPWM_polarity','JPWM_SOURCE.1','U_PWM.2',lambda x:'JPWM_SOURCE.2'not in component(x,'JPWM_SOURCE.1')),
        ('ST_second_socket_power_bypass','FL1.V','FL2.V',lambda x:'FL1.V'not in powered(dict(net,edges=x),cut='F_FL1')),
        ('OE_tied_to_PCA','U1.22','PCA.JP3.5',lambda x:'PCA.JP3.5'not in component(x,'U1.22')),
        ('motor_power_on_PCA','C_HY.V+','PCA.JP3.2',lambda x:'C_HY.V+'not in component(x,'LOCAL.LOGIC3V3'))):
        bad=copy.deepcopy(e)+[dict(id='SYNTHETIC_'+name,a=a,b=b)]
        negative[name]=not test(bad)
        assert negative[name],name
    bad=copy.deepcopy(e)
    next(x for x in bad if x['id']=='PCA_OUTPUT_0')['b']='PCA.JP1.1'
    negative['wrong_PCA_channel_socket']=('PCA.JP2.10'not in component(bad,'PCA.CH0.S'))
    assert negative['wrong_PCA_channel_socket']
    return dict(checks=checks,tests_passed=len(checks),negative_injections_detected=negative,
        states=states,fuse_cut_removed_drives=branches,rows=len(e),ports=len(ports),
        physical_pass=False,scope='Graph/pinout source reconciliation only; not transient/fault simulation or KiCadERC')


def tables(net, ports):
    for name, rows, keys in (
        ('connections.csv',net['edges'],['id','a','b','kind','area_mm2','sku','source']),
        ('pinouts.csv',ports,['device','sku','physical_pin','role','endpoint','view','evidence','conditional_delivery']),
        ('passives.csv',net['passives'],['ref','value','ends','location'])):
        with (OUT/name).open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore')
            writer.writeheader(); writer.writerows(rows)


def render(name, title, lines):
    # Native editable SVG plus PNG with the same block/arrow topology.
    width,height=1600,155+len(lines)*67
    img=Image.new('RGB',(width,height),'#f7f9fc');d=ImageDraw.Draw(img)
    font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',21)
    big=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',28)
    d.text((28,20),title,font=big,fill='#182c45')
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         '<rect width="100%" height="100%" fill="#f7f9fc"/>',
         f'<text x="28" y="48" font-family="Arial" font-size="28" font-weight="bold">{html.escape(title)}</text>']
    for i,line in enumerate(lines):
        y=78+i*67
        d.rounded_rectangle((22,y,1578,y+55),radius=7,fill='white',outline='#bccadd',width=2)
        d.text((34,y+14),line,font=font,fill='#152d48')
        svg.append(f'<rect x="22" y="{y}" width="1556" height="55" rx="7" fill="white" stroke="#bccadd"/><text x="34" y="{y+35}" font-family="monospace" font-size="21">{html.escape(line)}</text>')
    footer='NOMINAL PROTOTYPE | exact wire/pad rows: connections.csv + pinouts.csv | no physical PASS; E3/W5 OPEN'
    d.text((28,height-40),footer,font=font,fill='#7a3508')
    svg.append(f'<text x="28" y="{height-22}" font-family="monospace" font-size="19">{html.escape(footer)}</text></svg>')
    img.save(OUT/(name+'.png'))
    (OUT/(name+'.svg')).write_text('\n'.join(svg)+'\n',encoding='utf-8')


def sheets(net):
    lines=['BAT XT60(+) -> F0 30A -> S0 HELLA -> P_SYS.1; BAT(-) -> G1.1',
        'P_SYS.2 -> F_PI 3A -> MAIN4853 VIN / VOUT5.10V -> JoyITK1474 -> PiUSB-C',
        'P_SYS.3 -> S1.2--3 -> P_FRONT.1; P_SYS.4 -> S1.5--6 -> P_REAR.1',
        'P_FRONT.2 -> F_FL 10A -> FL_P.1; P_FRONT.3 -> F_FR 10A -> FR_P.1',
        'P_REAR.2 -> F_RL 10A -> RL_P.1; P_REAR.3 -> F_RR 10A -> RR_P.1',
        'P_REAR.5 -> XA01 -> F_AUX4A -> XA02 -> AUX4092 VIN; VOUT6V -> P_AUX.1',
        'P_AUX.2/3/4 -> F_HY/F_HP/F_TY 1A -> C_HY/C_HP/C_TY red V+',
        'P_REAR.4 -> XP01 -> F_PWM0.1A -> XP02.source -> JPWM_SOURCE.1',
        'JPWM_SOURCE.1 <mate> JPWM_MODULE.1 -> XP02.module -> U_PWM.3(VIN)',
        'G_TAIL.3 -> XP03.source -> JPWM_SOURCE.2 <mate> MODULE.2 -> U_PWM.2(GND)',
        'U_PWM.1(OUT5V) -> XP04A/B/C -> U1.23/24; NOT servo power!',
        'Returns: FL_G/FR_G -> G1; RL_G/RR_G/BUS -> G2; G1.5 <-> G2.1',
        'G2.5 -> XA05 -> G_AUX.1; AUX.GND -> G_AUX.2; HY/HP -> G_AUX.3/4',
        'G_AUX.5 -> XA06 -> G_TAIL.1; TY -> G_TAIL.2; logic -> G_TAIL.4',
        'Balance B0/B1/B2/B3 -> P309 minus/1S/2S/3S; live even with S0 OFF',
        'G-Tech physical tap/ID identification remains W5; no guessed plug orientation']
    render('01-power','E4 / 1 POWER + RETURNS / selected R35',lines)
    rows=[]
    for l in ('FL','FR','RL','RR'):
        for n in (1,2,3):
            rows.append(f'{l}{n}: {l}_P.{n+1} -> F_{l}{n} (4A) -> RED | {l}_G.{n+1} -> BLACK | D_{l}.{n+1} -> WHITE')
    rows += ['Factory keyed servo plug retained; OTHER servo socket NC on all12 bodies',
             'BUS H3.1 DATAwhite -> D_FL.1; H3.3 Gblack -> G2.4; H3.2 V(red) REMOVED',
             'DATA links: D_FL.5 -> D_FR.1 / D_FR.5 -> D_RR.1 / D_RR.5 -> D_RL.1']
    for n,axis in enumerate(('HY','HP','TY')):
        rows.append(f'{axis}: F_{axis} (1A) -> JR redcentre | powerGND -> JR brown | U1.{21-n} -> R{n+1} (220ohm) -> JR yellowPWM')
    rows += ['R7/R8/R9 10k: PWM -> SAME servo-side GND after R1/R2/R3; insulated joints',
             'IDs project allocation: FL1..3=1..3 / FR=4..6 / RL=7..9 / RR=10..12; configure in phase2']
    render('02-drives','E4 / 2 ALL15 DRIVES / leg and JR endpoints',rows)
    render('03-logic','E4 / 3 LOGIC + LOCAL PASSIVES / no custom etched PCB',[
        'PiH1 -> XL01 -> LOGIC3V3 -> PCA JP3.2 VCC + U1.1VCCA + U1.2DIR',
        'PiH3 BCM2 -> XL05 -> PCA JP3.3 SDA; PiH5 BCM3 -> XL06 -> PCA JP3.4 SCL',
        'PiH6 -> XL10 -> G_LOGIC; PCA JP3.6 -> XL08 -> G_LOGIC; localG -> G_TAIL.4',
        'PiH11 BCM17 -> XL07 -> U1.22 /OE; R15 10k to3V3 => default DISABLED',
        'PCA JP3.5 OE NC(factory pulldown); JP3.1 V+ NC; JP4 externally unused',
        'CH0 JP2.10 -> XS11 -> U1.3 A1 / U1.21 B1 -> XS12 -> R1 -> XS13 -> HY',
        'CH1 JP2.7 -> XS21 -> U1.4 A2 / U1.20 B2 -> XS22 -> R2 -> XS23 -> HP',
        'CH2 JP2.4 -> XS31 -> U1.5 A3 / U1.19 B3 -> XS32 -> R3 -> XS33 -> TY',
        'R4/5/6 10k: A1/2/3 -> GND; A4..8 pins6..10 -> GND; GND pins11/12/13',
        'B4..8 pins18..14 -> R10..14 10k -> GND; no direct short toground',
        'C1 100nF VCCA-GND / C2 100nF VCCB-GND; R16 10k PWM5-GND',
        'L78L05ACZ: C_IN330nF VIN-GND; C_OUT100nF OUT-GND; R_LOAD2.2k OUT-GND',
        'U1 PW TOP-view: notchup left1..12 / right24..13; adapter0.65mm side',
        'U_PWM TO92 BOTTOM flatup: 1OUT /2GND /3IN; opposite view3/2/1',
        'PiUSB2-A <factory Lanberg500mm> BUSUSB-C; switchB; USB powers ONLY adapterlogic',
        'PiJ8 housing1992: 5xPololu1871 600mm; 5Vpins2/4 EMPTY; markpin1',
        'MOTORON requires fresh frame + deliberateenable; S1ON is NOT automatic START'])


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--seal',action='store_true'); args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    # Save recoverable intent before generation/hash operations.
    save(OUT/'plan.json',dict(start_utc=START.isoformat(),scope='E4 only, selected R34 interfaces into R35',
        E3_complete=False,W5_complete=False,new_STL=0,physical_pass=False))
    net=build(); ports=pinouts(); checks=validate(net,ports)
    save(OUT/'pca-source-trace.json',dict(source=SCH,sha256=sha(ROOT/SCH),outputs=pca_outputs(),
        source_channel_identity='IC PWM0/1/2 -> onboardR13 gates4/3/2 -> JP2pads10/7/4',
        rejected_working_sheet='JP1pads1/4/7 are PWM7/6/5, NOT CH0/1/2',physical_pass=False))
    save(OUT/'netlist.json',net); save(OUT/'pinouts.json',ports)
    save(OUT/'checks.json',checks); tables(net,ports); sheets(net)
    print(json.dumps(dict(connection_rows=len(net['edges']),port_rows=len(ports),
        checks=checks['tests_passed'],negative_injections=len(checks['negative_injections_detected']),seal=args.seal)))
    if not args.seal:
        return
    # Mark E4 only after checking the generated sheets and conditional interface scope.
    net['E4_complete']=True
    net['completion_scope']='Nominal schematic/pinout of15drive assembly; delivered checks and remaining mechanical harness W5 not claimed'
    save(OUT/'netlist.json',net)
    checks.update(E4_complete=True,phase1_percent=70,new_STL=0)
    save(OUT/'checks.json',checks)
    BATCH.mkdir(exist_ok=True)
    parent=read(OLD/'manifest.json')
    sys.path.insert(0,str(ROOT/'tools/cad')); from release_check import verify
    assert verify(ROOT,parent)['integrity_ok']
    s=copy.deepcopy(read(OLD/'selection.json')); q=copy.deepcopy(read(OLD/'one-order-quantities.json'))
    s.update(parent_selection_sha256=sha(OLD/'selection.json'),E4_complete=True,
        connection_map=(OUT/'netlist.json').relative_to(ROOT).as_posix(),
        connection_map_sha256=sha(OUT/'netlist.json'))
    s['conditions'].append('R35 nominal E4 map includes15drives; E3/W5 OPEN; actual adapter/servo/balance roles need unpowered phase2 inspection before energizing.')
    q['selected_prints']=(BATCH/'selection.json').relative_to(ROOT).as_posix()
    q['electrical_connection_map']=s['connection_map']
    assert s['prints']==read(OLD/'selection.json')['prints'] and q['lines']==read(OLD/'one-order-quantities.json')['lines']
    save(BATCH/'selection.json',s); save(BATCH/'one-order-quantities.json',q)
    (BATCH/'README.md').write_text('# R35: jeden zestaw R34, scalony schemat E4\n\nWszystkie71zadań/110PETG/4próbki i113pozycji ilości zachowane.0nowychSTL.\nE4 nominalny schemat15napędów ukończony; E3/W5/K2/K3/A2/A3OPEN.\n14/20=70%. Nie jest fizycznymPASS ani zgodą na zasilanie.\n',encoding='utf-8')
    end=datetime.now(timezone.utc)
    save(OUT/'work-time.json',dict(start_utc=START.isoformat(),end_utc=end.isoformat(),
        wall_seconds=(end-START).total_seconds(),kind='E4 instructions/sources/connection map/pinouts/sheets/regression/package',
        separately_measured_phases=False,new_STL=0,physical_pass=False,sealing_verification_follows=True))
    pins={x['path']:x['sha256']for x in parent['files']}
    deps=[Path(__file__),Path(__file__).with_name('e4_source_probe.py'),
          Path(__file__).with_name('test_connection_map_e4_r1.py'),OLD/'manifest.json']
    deps += [ROOT/p for p in net['source_bindings']]
    deps += [p for d in (OUT,BATCH) for p in d.rglob('*') if p.is_file() and p.name not in ('manifest.json','validation.json')]
    for p in deps:
        name=p.relative_to(ROOT).as_posix(); digest=sha(p)
        assert name not in pins or pins[name]==digest,name
        pins[name]=digest
    m=copy.deepcopy(parent)
    m.update(E4_complete=True,E3_complete=False,new_stls=0,newly_selected_stls=0,parent_pins_preserved=len(parent['files']),
        files=[dict(path=p,sha256=h)for p,h in sorted(pins.items())])
    m['gates']['electrical']=dict(status='open',reason='E4 nominal map integrated. E3 source coordination and physical trials OPEN.',evidence=[s['connection_map']])
    report=verify(ROOT,m); assert report['integrity_ok']
    assert not verify(ROOT,m,True)['integrity_ok']
    save(BATCH/'manifest.json',m)
    save(BATCH/'validation.json',dict(integrity=report,parent_pins_preserved=len(parent['files']),
        all_prints_and_quantity_lines_unchanged=True,print_ready_denied=True,physical_pass=False))
    print(json.dumps(dict(pins=len(pins),parent_pins=len(parent['files']),E4_complete=True,phase1_percent=70)))


if __name__=='__main__':
    main()
