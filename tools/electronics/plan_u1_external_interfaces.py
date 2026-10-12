"""One physical terminal ledger, reconciled to E4 before wire generation.

The old population reserved three extra servo signal-ground wires, whereas the
selected E4 graph uses existing motor returns and local R7..9 grounds. Do not
install those thin parallel motor returns. Reuse two reserved ground holes for
the real PCA/reference links, and retain the third hole unpopulated.
"""
import json,math,time,xml.etree.ElementTree as ET
from pathlib import Path
import plan_u1_socket_carrier as U

ROOT,OUT=U.ROOT,U.OUT


def pca_pads(path):
    board=ET.parse(path).getroot().find('./drawing/board');packages={}
    outline=board.findall('./plain/wire[@layer="20"]')
    origin=[min(float(w.get(k)) for w in outline for k in ('x1','x2')),
            min(float(w.get(k)) for w in outline for k in ('y1','y2'))]
    for lib in board.findall('./libraries/library'):
        for package in lib.findall('./packages/package'):packages[lib.get('name'),package.get('name')]=package
    result={}
    for e in board.findall('./elements/element'):
        if e.get('name') not in ('JP2','JP3','JP4'):continue
        rot=e.get('rot','R0');assert 'M' not in rot and rot.startswith('R'),rot
        a=math.radians(float(rot[1:]));x,y=float(e.get('x')),float(e.get('y'))
        for pad in packages[e.get('library'),e.get('package')].findall('pad'):
            px,py=float(pad.get('x')),float(pad.get('y'))
            result[e.get('name')+'.'+pad.get('name')]=[round(-39+x+px*math.cos(a)-py*math.sin(a)-origin[0],6),
                round(-12.7+y+px*math.sin(a)+py*math.cos(a)-origin[1],6),84.32]
    assert result['JP3.2'][:2]==[-37.095,-3.683]
    return result


def build():
    pf=OUT/'u1-socket-carrier-plan.json';p=json.loads(pf.read_text());U.check(p)
    terms={q['ref']:q for q in p['terminals']}
    # This unoccupied hole is on existing N$49 LOGIC3V3 copper. No extra
    # cut, bridge, same-hole splice, source-chip remapping or gauge waiver.
    extra=dict(ref='PCA3V3.out',x=12.7,y=6.35,net='LOGIC3V3')
    checked=json.loads(json.dumps(p));checked['terminals'].append(extra);U.check(checked)
    terms[extra['ref']]=extra
    board=ROOT/'hardware/reference/adafruit815-2026-09-26/Adafruit PCA9685 rev C.brd'
    pads=pca_pads(board);nf=ROOT/'hardware/electronics/full-cat/netlist-r1/netlist.json'
    n=json.loads(nf.read_text());edges={q['id']:q for q in n['edges']}
    bindf=ROOT/'hardware/electronics/full-cat/netlist-r1/logic-binding.json'
    binding=json.loads(bindf.read_text());oldf=ROOT/'hardware/electronics/full-cat/pi-interface-final-r2/wiring-card.json'
    old=json.loads(oldf.read_text());oldpi={q['wire']:q for q in old['GPIO']}
    rows=[]
    def module(ref):
        t=terms[ref];return dict(kind='actual1608pad',ref=ref,world_mm=[91.59+t['x'],t['y'],84.3202],net=t['net'])
    def pca(ref,net):return dict(kind='supplier815revCpad',ref='PCA.'+ref,world_mm=pads[ref],net=net)
    def pi(wid,net):
        r=oldpi[wid];x,y,z=r['start_mm']
        return dict(kind='project40pin_housing_wire_exit',ref='PI.H'+str(r['pi_pin']),world_mm=[x,y,z+47.72-52],net=net,
                    evidence='Preserved XY physical-pin datum; current PCB bottom47.72 replaces52. Connector height/exit is provisional, not a catalogue pin-tip dimension')
    def add(wid,a,b,construction,**kw):
        assert a['net']==b['net'],(wid,a,b)
        rows.append(dict(id=wid,a=a,b=b,construction=construction,actual_cut_mm=None,route_qualified=False,
                         independent_insulation_grips_required=True,**kw))
    for wid,ref,net in [('XL01','LOGIC3V3.in','LOGIC3V3'),('XL10','G_LOGIC.in','G_SYS'),('XL07','OE.in','OE_N_3V3')]:
        add(wid,pi(wid,net),module(ref),'Preserve factory Pi female contact; trim ONLY board end after dry fit',
            sku_candidate='Pololu1871',AWG=26,factory_nominal_mm=600,service_reserve_Pi_mm=30,
            project_radius_mm=10,OD_project_upper_mm=1.4)
    for wid,pad,net in [('XL05','JP3.3','I2C_SDA'),('XL06','JP3.4','I2C_SCL')]:
        add(wid,pi(wid,net),pca(pad,net),'Preserve Pi factory female; solder named PCA pad',
            sku_candidate='Pololu1871',AWG=26,factory_nominal_mm=600,service_reserve_Pi_mm=30,
            project_radius_mm=10,OD_project_upper_mm=1.4)
    add('XL02',module('PCA3V3.out'),pca('JP3.2','LOGIC3V3'),'One fixed PCB-to-PCB logic conductor; not a second Pi feed',
        wire_choice_open=False,sku_candidate='LAPP4126002S',project_radius_mm=10,nominal_area_mm2=.25,OD_project_upper_mm=1.4)
    add('XL08',pca('JP3.6','G_SYS'),module('G_HP.out'),'Repurpose reserved signal-GND port as actual PCA reference wire',
        wire_choice_open=False,sku_candidate='LAPP4126002S',project_radius_mm=10,nominal_area_mm2=.25,OD_project_upper_mm=1.4)
    # Bind the numbered port order from the CURRENT two independently used
    # ports3/5, not the old unrotated G_TAIL coordinates or guessed sign.
    e2f=U.BASE/'pwm-branch-checkpoint/selection.json';e2=json.loads(e2f.read_text())
    tailf=U.BASE/'tail-wiring-checkpoint/current-plan.json';tail=json.loads(tailf.read_text())
    p3=e2['routes']['XP03_source']['parts'][0]['start'];p5=tail['G_TAIL5']['point_mm']
    assert e2['G_TAIL_centre_mm']==[28,-35,141] and e2['G_TAIL_rotation_z_deg']==90
    assert p3==[37.5,-35,141] and p5==[37.5,-44.5,141],(p3,p5)
    p4=[(a+b)/2 for a,b in zip(p3,p5)]
    add('XL09',module('G_HY.out'),dict(kind='current_WAGO_port',ref='G_TAIL.4',world_mm=p4,net='G_SYS',
        departure=[1,0,0],basis='Middle of current numbered ports3/5; provisional4.75mm pitch, not measured supplier cavity'),
        'Preserve E4 LOCAL.GND -> G_TAIL.4 reference; do not combine two ends in an occupied port',
        wire_choice_open=False,sku_candidate='LAPP4126002S',project_radius_mm=10,nominal_area_mm2=.25,OD_project_upper_mm=1.4)
    for wid,i,pad in [('XS11',1,'JP2.10'),('XS21',2,'JP2.7'),('XS31',3,'JP2.4')]:
        net=terms[f'A{i}.in']['net'];assert edges[wid]['a']==f'PCA.CH{i-1}.S'
        add(wid,pca(pad,net),module(f'A{i}.in'),'Whole fixed PWM input including actual board ends; no assigned motor current',
            wire_choice_open=False,sku_candidate='Adafruit1446',AWG=30,
            project_radius_mm=.5,OD_project_upper_mm=.8,
            fixed_low_current_logic_only=True,
            radius_and_OD_are_project_fit_gates_not_catalogue=True,
            endpoint_under_adapter_requires_shared_fan=True)
    occupied={}
    for q in rows:
        for end in ('a','b'):
            t=q[end];key=t['ref'];assert key not in occupied,('Two external ends one physical terminal',key)
            occupied[key]=q['id']
    assert set(q['id'] for q in rows)=={'XL01','XL02','XL05','XL06','XL07','XL08','XL09','XL10','XS11','XS21','XS31'}
    return dict(status='E4_BOUND_EXTERNAL_INTERFACE_PLAN_ROUTES_GRIPS_OPEN',selected=False,E1_complete=False,W5_complete=False,physical_pass=False,
                wires=rows,occupied_external_terminals=len(occupied),added_occupied1608hole=extra,
                unchanged_output_ports=['B1.out/XS13','B2.out/XS23','B3.out/XS33'],
                retained_E2=['XP02.board/PWM_REG_IN','XP03.board/G_SYS fromG_TAIL.3; separate fromXL09/G_TAIL.4'],
                not_installed=['No extra G_HY/G_HP/G_TY thin leads to servo motor-GND contacts',
                               'G_TY.out reserved copper hole remains physically unpopulated'],
                rationale='R7/R8/R9 already use local servo connector GND. Selected E4 uses XB13/XB23/XB33 motor returns; old population separate signalGND names are not extra three physical servo contacts.',
                unchanged_logical_graph='XL03/04/11/12/13 and XP04A/B/C realized by qualified same-net copper/header/local links, not extra long wires',
                GPIO_factory_choice='Later pi-interface-final-r2 Pololu1871/600mm supersedes early1841/300mm candidate; selected stock still must reconcile',
                fixed_link_choice='XL02/08/09 use existing LAPP4126002S0.25mm2 stock candidate: supplier nominalOD1.3/staticR5.2; projectOD<=1.4/R10. No26AWG0.129mm2 direct WAGO termination below0.14mm2 minimum.',
                E4_physical_gauge_deltas={'XS11/21/31':'0.14mm2 generic -> supported fixed30AWG1446 logic only',
                                          'XL02/08/09':'0.14mm2 generic ->0.25mm2 fixedLAPP; electrical nets unchanged'},
                no_connect=['Pi2/4 and other35housing cavities','PCAJP3.1/V+','PCAJP3.5/OE','PCAJP4whole','PCAallservoV+'],
                actual_GPIO_binding=binding,delivery_gate='Unpowered actual connector/pin1/revision/OD/solder/insulation checks, no physicalPASS',
                required_next=['One shared fan for all11conductors plus currentE2/W3/W4/retention, before new mounts',
                               'G_TAIL.4 bound to current ports3/5; independent entry grip and lever access still OPEN',
                               'No radius/gauge relaxation without an explicit supported fixed-wire choice',
                               'Independent cable grips, native assembly, stock, one selection'],
                source_sha256={f.relative_to(ROOT).as_posix():U.sha(f) for f in (pf,board,nf,bindf,oldf,e2f,tailf,
                    ROOT/'hardware/reference/p0-kit-2026-09-25/SIGNAL-CABLES.md',
                    ROOT/'hardware/reference/u1-socket-connectors-2026-10-12/wire-facts.json',Path(__file__))})


def run():
    tick=time.monotonic();p=build();p['worker_seconds']=round(time.monotonic()-tick,4)
    (OUT/'u1-external-interfaces-plan.json').write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=p['status'],wires=len(p['wires']),terminals=p['occupied_external_terminals'],worker_seconds=p['worker_seconds'])))


if __name__=='__main__':run()
