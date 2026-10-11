"""One complete copper allocation for a socketed1208 on1608.

Replaces the rejected19-long-wire architecture, not the selected assembly.
Three explicit copper cuts allow three series resistors on their own columns.
Preserve all16 signal resistors, two decouplers and the original regulator.
No claim of formed-lead, whole-cat, electrical or physical acceptance.
"""
import copy
import hashlib
import json
import math
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype'
OUT=BASE/'body-harness-checkpoint'
POP=ROOT/'hardware/electronics/full-cat/pwm-carrier-r3/population.json'
MAP=OUT/'u1-documented-adapter.json'
SIGNAL=ROOT/'hardware/electronics/full-cat/pwm-signal-r1/circuit.json'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def plan():
    old=json.loads(POP.read_text());m=json.loads(MAP.read_text())
    p=dict(status='SOCKET_CARRIER_COPPER_ALLOCATION_ONLY',selected=False,
           E1_complete=False,E2_requalified=False,physical_pass=False,
           board=copy.deepcopy(old['board']),terminals=[],parts=[],links=[],
           copper_cuts=[dict(x=x,y=10.16,across_trace_x_mm=.8,along_trace_y_mm=.4,source_wire_y_mm=[8.89,11.43],
                             instruction='Remove ONLY copper in0.8X by0.4Y rectangle;0.4 fits the0.6096 gap between annuli. Do not drill substrate/pad; unpowered continuity proves isolated halves.')
                        for x in (-10.16,-7.62,-5.08)],
           adapter={'sku':'Adafruit1208','face':'TSSOP up','rotation_deg':90,
                    'center_local_mm':[-1.27,-3.81],'size_xy_mm':[35.56,17.78],
                    'chip_pin1_local_mm':[-17.78,-11.43],
                    'unused_holes':'JP1.13/14 andJP2.13/14 deliberately unpopulated',
                    'candidate_bottom_world_z_mm':95.3602,
                    'thickness_project_mm':1.6,'thickness_verified':False},
           connectors=[dict(sku='M20-7821242',quantity=2,contacts=12,height_above_board_mm=8.5,
                            tail_mm=3,body_mm=[30.88,2.5,8.5],
                            source='https://www.harwin.com/products/M20-7821242'),
                       dict(sku='M20-9991245',quantity=2,contacts=12,mating_pin_mm=6.1,
                            body_height_mm=2.54,tail_mm=3,body_mm=[30.48,2.54,2.54],
                            source='https://www.harwin.com/products/M20-9991245')],
           electrical_change='Only physical population/copper allocation; same24pin nets, all16 signal resistors/C1/C2 and separate L78L05ACZ signal supply. No MAIN/AUX parallel and no motor current in signal returns.',
           supersedes_if_selected=['Ambiguous575070 adapter','19 adapter jumper leads and5 assumed header bridges',
                                  'old U1 platform/spacers/insulators/mount screws','old PWM1 population and E2 board-end geometry'],
           required_before_selection=['Actual local cap/formed-link/insulation geometry and independent external cable grips',
                                      'Replace obsolete over-board U1 platform in native carrier; accessible whole-module screws/socket withdrawal',
                                      'Rebind changed E2 board-end approach and all E4 current physical endpoints',
                                      'One actual shared solid/lead/body/contact check, native parameter/reopen and selected stock/export'],
           delivery_gates=['1208 original artwork/thickness and all24 chip continuity/no shorts',
                           '1608 copper cuts isolated, no pad damage or substrate weakness',
                           'M20 female recommended PCB drill1.02+/-0.05 versus1608 actual1.2: solder joint retention must be checked, not called manufacturer-approved',
                           'Unpolarized socket: mark chip1 and block reversed placement with asymmetric passive stop before selection',
                           'Actual5V/OE/3V3 sequencing, PWM edges and decoupling/thermal tests remain phase2'])
    def term(ref,x,y,net):p['terminals'].append(dict(ref=ref,x=round(x,6),y=round(y,6),net=net))
    def pair(ref,a,b,nets,sku,**kw):
        term(ref+'.1',*a,nets[0]);term(ref+'.2',*b,nets[1])
        p['parts'].append(dict(ref=ref,sku=sku,quantity=1,ends=[ref+'.1',ref+'.2'],**kw))
    def link(ref,a,b,net):
        term(ref+'.1',*a,net);term(ref+'.2',*b,net)
        p['links'].append(dict(ref=ref,ends=[ref+'.1',ref+'.2'],net=net,
                              construction='Formed fixed component-lead offcut with insulating sleeve; NOT a flexible stranded cable with relaxed R10',
                              actual_geometry_qualified=False))
    for row in m['rows']:
        x,y=row['TSSOP_face_up_xy_mm'];xx=-1.27-(y-17.78);yy=-3.81+x-8.89
        net=json.loads(SIGNAL.read_text())['pins'][str(row['chip_pin'])]
        term('U1.'+str(row['chip_pin']),xx,yy,'G_SYS' if net=='GND' else net)
    # Series outputs use a deliberate cut; all five copper pads are accounted.
    for i,(x,axis) in enumerate(zip((-10.16,-7.62,-5.08),('HEAD_YAW','HEAD_PITCH','TAIL_YAW')),1):
        pair('R'+str(i),(x,6.35),(x,13.97),('PWM_'+axis+'_BUF','PWM_'+axis+'_OUT'),
             'MRS16000C2200FCT00',value_ohm=220,formed_pitch_mm=7.62,
             body_center_local_mm=[x,8.7,1.8],body_size_mm=[1.6,3.6,1.6],
             forming='Asymmetric lead forming, body offset1.46mm from hole midpoint; inspect bend/body gap at assembly')
        term('B'+str(i)+'.out',x,11.43,'PWM_'+axis+'_OUT')
    for i,(x,axis) in enumerate(zip((-12.7,-10.16,-7.62),('HEAD_YAW','HEAD_PITCH','TAIL_YAW')),4):
        pair('R'+str(i),(x,-13.97),(x,-21.59),('PWM_'+axis+'_3V3','G_SYS'),
             'MRS16000C1002FCT00',value_ohm=10000,formed_pitch_mm=7.62,
             body_center_local_mm=[x,-17.78,1.8],body_size_mm=[1.6,3.6,1.6])
        term('A'+str(i-3)+'.in',x,-3.81,'PWM_'+axis+'_3V3')
    for i,x in zip(range(10,15),(-2.54,0,2.54,5.08,7.62)):
        pair('R'+str(i),(x,11.43),(x,19.05),('B'+str(i-6)+'_UNUSED','G_SYS'),
             'MRS16000C1002FCT00',value_ohm=10000,formed_pitch_mm=7.62,
             body_center_local_mm=[x,15.24,1.8],body_size_mm=[1.6,3.6,1.6])
    pair('R15',(-12.7,13.97),(12.7,13.97),('OE_N_3V3','LOGIC3V3'),
         'MRS16000C1002FCT00',value_ohm=10000,formed_pitch_mm=25.4,
         body_center_local_mm=[-8.89,13.97,5.6],body_size_mm=[3.6,1.6,1.6],
         forming='Entire long leads sleeved, lifted above short vertical load resistors; not qualified by copper graph')
    pair('R16',(-17.78,8.89),(10.16,8.89),('PWM5_SW','G_SYS'),
         'MRS16000C1002FCT00',value_ohm=10000,formed_pitch_mm=27.94,
         body_center_local_mm=[-13.97,8.89,5.6],body_size_mm=[3.6,1.6,1.6],
         forming='Entire long leads sleeved above series bodies; no geometry/lead stock acceptance yet')
    # Regulator moves to the genuinely free final three columns, not occupied chip pins.
    for pin,x,net in [(1,12.7,'PWM5_SW'),(2,15.24,'G_SYS'),(3,17.78,'PWM_REG_IN')]:term('U_PWM.'+str(pin),x,-13.97,net)
    p['parts'].append(dict(ref='U_PWM',sku='L78L05ACZ',quantity=1,
                         body_center_local_mm=[15.24,-16.4,10.375],body_size_mm=[4.95,3.94,4.95],
                         forming='Candidate body bottom7.9mm, first3mm straight, shift2.43mm south; actual rounded leads/stock must pass'))
    pair('C_IN',(17.78,-8.89),(15.24,-8.89),('PWM_REG_IN','G_SYS'),'C320C334K5R5TA',
         body_center_local_mm=[16.51,-7.89,5.44],body_size_mm=[5.08,3.18,5.84],
         forming='Actual max body H5.84,1.52mm projection plus1mm stand-off below body. Both leads offset1mm north above fixed holes; full formed leads/7mm minimum stock still required.')
    pair('C_OUT',(12.7,-11.43),(15.24,-11.43),('PWM5_SW','G_SYS'),'C315C104K5R5TA',
         body_center_local_mm=[13.97,-11.43,4.09],body_size_mm=[3.81,2.54,3.14],
         forming='Actual max body H3.14;1.52mm projection plus1mm stand-off modeled separately from resin body.')
    pair('R_LOAD',(17.78,6.35),(15.24,13.97),('PWM5_SW','G_SYS'),'MRS16000C2201FCT00',
         value_ohm=2200,formed_pitch_mm=math.hypot(2.54,7.62),
         body_center_local_mm=[16.51,10.16,1.8],body_size_mm=[2.656,3.921,1.6])
    for ref,x,y,net in [('XP02.board',17.78,-6.35,'PWM_REG_IN'),('XP03.board',15.24,-6.35,'G_SYS'),
                        ('LOGIC3V3.in',-17.78,-13.97,'LOGIC3V3'),('OE.in',-12.7,8.89,'OE_N_3V3'),
                        ('G_HY.out',-17.78,19.05,'G_SYS'),('G_HP.out',-15.24,19.05,'G_SYS'),
                        ('G_TY.out',-12.7,19.05,'G_SYS'),('G_LOGIC.in',17.78,19.05,'G_SYS')]:term(ref,x,y,net)
    # Known duplicate power/ground strips joined explicitly, never by nonexistent copper.
    for i,(a,b,net) in enumerate([
        ((-17.78,-8.89),(-15.24,-8.89),'LOGIC3V3'),
        ((-15.24,-6.35),(12.7,11.43),'LOGIC3V3'),
        ((-17.78,6.35),(-15.24,6.35),'PWM5_SW'),
        ((12.7,-3.81),(-15.24,8.89),'PWM5_SW'),
        ((12.7,-6.35),(17.78,11.43),'PWM5_SW'),
        ((15.24,3.81),(10.16,6.35),'G_SYS'),
        ((10.16,-8.89),(15.24,-3.81),'G_SYS'),
        ((10.16,-3.81),(10.16,11.43),'G_SYS'),
        ((10.16,-13.97),(10.16,-21.59),'G_SYS'),
        ((10.16,13.97),(10.16,19.05),'G_SYS')],1):link('J'+str(i),a,b,net)
    # One insulated comb: distinct pad per ground pin, no two terminals forced through one hole.
    ground=[(-5.08,-6.35),(-2.54,-6.35),(0,-6.35),(2.54,-6.35),(5.08,-6.35),(7.62,-6.35),(10.16,-6.35)]
    for i,(x,y) in enumerate(ground):term('JG_COMB.'+str(i),x,y,'G_SYS')
    p['links'].append(dict(ref='JG_COMB',ends=['JG_COMB.'+str(i) for i in range(7)],net='G_SYS',
                          construction='One formed/sleeved ground comb, exposed ONLY at assigned pads',actual_geometry_qualified=False))
    p['adapter_local_parts']=[dict(ref=c,sku='C315C104K5R5TA',quantity=1,
                                  between_chip_pins=[pin,11 if pin==1 else 13],
                                  body_center_local_mm=[-2.245,y,16.73],body_size_mm=[3.81,2.54,3.14],
                                  note='Direct local supply/GND loop at TSSOP pads; body2.52mm above adapter. Actual formed/sleeved cap leads and retention OPEN, not a remote decoupler claim')
                              for c,pin,y in [('C1',1,-9.5),('C2',24,.61)]]
    p['remote_parts']=copy.deepcopy(old['remote_components'])
    return p


def check(p):
    # Materialized copper connectivity after the THREE proposed cuts.
    groups={};assigned={};occupied={};terms={}
    for g in p['board']['groups']:
        for q in g['pads']:
            split=any(abs(c['x']-q['x'])<1e-6 and q['y']>c['y'] for c in p['copper_cuts'])
            groups[(q['x'],q['y'])]=g['source_net']+('_CUT_UP' if split and q['y']<15 else '')
    for t in p['terminals']:
        key=t['x'],t['y'];assert key in groups,('Not an actual source pad',t)
        assert key not in occupied,('Two ends one hole',t,occupied.get(key))
        assert t['ref'] not in terms
        occupied[key]=t['ref'];group=groups[key];terms[t['ref']]=t
        assert group not in assigned or assigned[group]==t['net'],('Source copper short',group,t)
        assigned[group]=t['net'];t['source_copper_group']=group
    parent={g:g for g in assigned}
    def find(g):
        while parent[g]!=g:g=parent[g]
        return g
    for link in p['links']:
        ends=[terms[n] for n in link['ends']]
        assert all(t['net']==link['net'] for t in ends),('Cross-net link',link)
        for t in ends[1:]:parent[find(t['source_copper_group'])]=find(ends[0]['source_copper_group'])
    for net in set(assigned.values()):
        roots={find(t['source_copper_group']) for t in p['terminals'] if t['net']==net}
        assert len(roots)==1,('Disconnected same-net groups',net,roots)
    expected={int(k):'G_SYS' if v=='GND' else v for k,v in json.loads(SIGNAL.read_text())['pins'].items()}
    assert {int(t['ref'].split('.')[1]):t['net'] for t in p['terminals'] if t['ref'].startswith('U1.')}==expected
    parts=p['parts']+p['adapter_local_parts']+p['remote_parts'];by_ref={c['ref']:c for c in parts}
    assert len(by_ref)==len(parts)
    assert {'R'+str(i) for i in range(1,17)}|{'C1','C2','C_IN','C_OUT','R_LOAD','U_PWM'}==set(by_ref)
    for i in range(1,17):assert by_ref['R'+str(i)]['value_ohm']==(220 if i<=3 else 10000)
    for i,axis in enumerate(('HEAD_YAW','HEAD_PITCH','TAIL_YAW'),1):
        assert [terms[r]['net'] for r in by_ref['R'+str(i)]['ends']]==['PWM_'+axis+'_BUF','PWM_'+axis+'_OUT']
        assert [terms[r]['net'] for r in by_ref['R'+str(i+3)]['ends']]==['PWM_'+axis+'_3V3','G_SYS']
    for i in range(10,15):assert [terms[r]['net'] for r in by_ref['R'+str(i)]['ends']]==['B'+str(i-6)+'_UNUSED','G_SYS']
    for ref,nets in [('R15',['OE_N_3V3','LOGIC3V3']),('R16',['PWM5_SW','G_SYS']),
                     ('R_LOAD',['PWM5_SW','G_SYS']),('C_IN',['PWM_REG_IN','G_SYS']),('C_OUT',['PWM5_SW','G_SYS'])]:
        assert [terms[r]['net'] for r in by_ref[ref]['ends']]==nets
    for c,pins in [('C1',[1,11]),('C2',[24,13])]:assert by_ref[c]['between_chip_pins']==pins
    for cut in p['copper_cuts']:
        assert cut['across_trace_x_mm']>.4064 and cut['along_trace_y_mm']<=2.54-1.9304-.2
    return dict(occupied_holes=len(occupied),copper_groups=len(assigned),chip_pins=24,
                signal_resistors=16,decouplers=2,source_circuit_preserved=True,
                copper_graph_connected=True,copper_cuts=3,adapter_long_jumpers=0,
                formed_local_links=len(p['links']),physical_pass=False,
                scope='Source pads/occupancy/modified copper graph and complete circuit refs ONLY; not geometry/thermal/mating/whole E1')


def run():
    tick=time.monotonic();p=plan();p['checks']=check(p)
    p['source_sha256']={f.relative_to(ROOT).as_posix():sha(f) for f in (POP,MAP,SIGNAL,Path(__file__))}
    p['worker_seconds']=round(time.monotonic()-tick,4)
    (OUT/'u1-socket-carrier-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=p['status'],**p['checks'],worker_seconds=p['worker_seconds'])))


if __name__=='__main__':run()
