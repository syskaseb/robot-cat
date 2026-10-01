"""Select the completed nominal Pi interface once; preserve all R32 pins."""
import ast,copy,json
from datetime import datetime,timezone
from pathlib import Path
from check_main_p0_placement import ROOT,sha
from release_check import verify,REQUIRED_GATES
OLD=ROOT/'hardware/manufacturing/one-batch-prototype-r32'
OUT=ROOT/'hardware/manufacturing/one-batch-prototype-r33'
E=ROOT/'hardware/electronics/full-cat';C=ROOT/'hardware/cad/studies'
N=C/'pi-complete-native-r2';F=E/'pi-interface-final-r2'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    assert not (OUT/'manifest.json').exists()
    parent=read(OLD/'manifest.json');assert verify(ROOT,parent)['integrity_ok']
    checks=read(F/'checks.json');native=read(N/'checks.json')
    assert not checks['hits'] and checks['tool_corridors']==12 and checks['continuous_tray_lift_mm']==15
    assert native['reopen_recompute'] and all(r['closed'] and r['components']==1 and r['valid'] for r in native['parts'].values())
    assert (N/'preview.png').exists() and (F/'preview.png').exists()
    previous=read(OLD/'selection.json');s=copy.deepcopy(previous)
    replacements={'M5:PiTray18_x1':'PiTray','electronics:DeckP10-cover-mount':'Deck','electronics:Carrier service ports':'Carrier'}
    for row in s['prints']:
        if row['identity'] in replacements:
            n=replacements[row['identity']];g=native['parts'][n]
            row.update(stl=g['STL'],sha256=g['sha256'],quantity=1,status='conditional_hobby_phase1_selection',
                recipe=(OUT/'README.md').relative_to(ROOT).as_posix(),orientation=g['orientation'],
                print_size_mm_including_5mm_brim=[d+10 if i<2 else d for i,d in enumerate(g['dimensions_mm'])],
                supports='PETG/slicer/bridges/nut and portal fit trials phase2')
    for old,new in zip(previous['prints'],s['prints']):
        if old['identity'] not in replacements:assert old==new
    g=native['parts']['BUSBracket']
    s['prints'].append(dict(identity='Pi:BUSBracket_x1',module='Pi/BUS rigid mount',stl=g['STL'],sha256=g['sha256'],
        quantity=1,purpose='installed_candidate',status='conditional_hobby_phase1_selection',material='PETG',
        orientation=g['orientation'],print_size_mm_including_5mm_brim=[d+10 if i<2 else d for i,d in enumerate(g['dimensions_mm'])],
        supports='Phase2 inspect nut-pocket roofs/bridges and beam support',recipe=(OUT/'README.md').relative_to(ROOT).as_posix()))
    s.update(jobs=71,installed_jobs=67,installed_petg_parts=110,fit_samples=4,CP_PI_complete=True,
        parent_selection_sha256=sha(OLD/'selection.json'),phase1_percent=65,
        Pi_interface=(F/'interface.json').relative_to(ROOT).as_posix(),Pi_checks_sha256=sha(F/'checks.json'),E2_red_return_override=(F/'interface.json').relative_to(ROOT).as_posix(),
        Pi_native_checks_sha256=sha(N/'checks.json'),M5_mount_checks=(F/'checks.json').relative_to(ROOT).as_posix(),
        M5_mount_checks_sha256=sha(F/'checks.json'),M5_native_clamps='hardware/cad/studies/pi4-tray-body-mount-r1/PiTrayClamps.FCStd')
    s['historical_conditions']+=s['conditions']
    s['conditions']=['Phase1 remains13/20=65%; Pi is PART of W5, not entire remaining harness.',
        'R33 nominal Pi interface selected; raised7mm Pi, retained bores/nut pockets, detachable north BUS beam and local restraints.',
        'R32 E2 retained; final Pi interface checks retained PWM service routes, not obsolete short legs.',
        'Populated connector/plug/wire/shrink/PETG assumptions and electrical/current/thermal trials phase2. No physical PASS.',
        'E3/E4/W5/K2/K3/A2/A3 remain; no purchase, powering, slicer or ROS.']
    q=copy.deepcopy(read(OLD/'one-order-quantities.json'));rows={r['id']:r for r in q['lines']}
    for ident,newcount in [('fastener:M5:M2.5x8',2),('fastener:M5:M3x8',4)]:
        r=rows[ident];r['planning_quantity']=newcount;r['installed_M5_quantity']=0 if 'M2.5' in ident else 2
        r['note']+=' R33 replaces installed Pi/north-tray screws only; two previous spare screws retained.'
    rows['fastener:DIN934 nuts:M2 DIN934 AF4']['planning_quantity']+=4
    rows['fastener:DIN934 nuts:M2 DIN934 AF4']['note']+=' R33 adds4 BUS bracket nuts SKL000381; no extra tray nuts.'
    rows['fastener:washers:P0 M2 DIN125 OD5/ID2.2/t0.3']['planning_quantity']+=4
    rows['fastener:washers:P0 M2 DIN125 OD5/ID2.2/t0.3']['note']+=' R33 adds4 BUS washers ART00125202; reuse existing tray/Pi washers.'
    rows['tie:111-02370']['installed']+=12
    rows['tie:111-02370']['note']+=' R33 adds6 GPIO,4 power/USB/MAIN,2 loose-USB-park ties;81 working installed, bag100 unchanged.'
    rows['p0:PI-POWER-CABLE'].update(name='Joy-IT K-1474 USB-C18AWG1m5A; output nominal<=291mm after dry-fit, not old25cm',
        manufacturer_sku='K-1474',EAN='4250236828305',note='One cable shared: MAIN input<=300mm, Pi output<=291mm nominal including36mm ends/slack, >409mm leftover. Cut only after fitting; no second cable.')
    rows['p0:BUS-USB-CABLE-P0'].update(manufacturer_sku='CA-USBO-10CU-0005-BK',EAN='5901969416237',
        note='Pi USB2 to BUS USB-C,500mm factory cable NOT CUT; nominal route308.0703mm+60service+40bodies<=500. Loose excess storage atR>=24; service slack and stored excess are not counted twice.')
    for sku in ('RNF-100-3/32-0-STK','RNF-100-3/16-0-STK'):
        matches=[r for r in q['lines'] if r.get('manufacturer_part')==sku];assert len(matches)==1
        matches[0]['note']+= ' R33 Pi:3/32 supplies5 GPIO15mm blanks and2 MAIN inner neck sleeves;3/16 no longer used as two interfering MAIN outer sleeves. Existing stock unchanged.'
    src=(F/'suppliers.json').relative_to(ROOT).as_posix()
    additions=[
        dict(id='fastener:Pi:M2.5x16',name='KRAFTBERG DIN912 A2 M2.5x16',manufacturer_sku='M2.5X16/D912-A2',planning_quantity=6,installed=4,spares=2,unit='pcs',source=src),
        dict(id='fastener:Pi:M3x10',name='BEJMET DIN912 A2 M3x10',manufacturer_sku='SKL000622',planning_quantity=4,installed=2,spares=2,unit='pcs',source=src),
        dict(id='fastener:Pi:BUS_M2x12',name='BEJMET DIN912 A2 M2x12',manufacturer_sku='SKL000595',planning_quantity=6,installed=4,spares=2,unit='pcs',source=src),
        dict(id='Pi:J8_housing_1992',name='Pololu1992 2x20 female crimp housing',manufacturer_sku='1992',planning_quantity=1,unit='pack5',installed=1,spares=4,source=src),
        dict(id='Pi:GPIO_brown_1871',name='Pololu1871 brown26AWG600mm female-female factory-crimp lead',manufacturer_sku='1871',planning_quantity=2,unit='pack5',installed=5,spares=5,source=src),
        dict(id='insulation:Pi:RNF-100-3/8-0-STK',name='TE RNF1003/8 black9.5/4.8mm COMMON MAIN output boot',manufacturer_sku='RNF-100-3/8-0-STK',planning_quantity=6,unit='m',installed_blanks=1,blank_mm=15,source=src,note='Five1.2m sticks conservative purchase allowance; supplier minimum/availability refreshedphase2. One common boot around both already independently insulated pad necks, not two separate overlapping sleeves.')]
    assert all(a['id'] not in rows for a in additions);q['lines']+=additions
    q['lines']=[r for r in q['lines'] if r['id']!='fastener:M5:M2.5x8'] # obsolete installed size; spares now match M2.5x16
    q.update(selected_prints=(OUT/'selection.json').relative_to(ROOT).as_posix(),line_count=len(q['lines']))
    assert len(q['lines'])==len({r['id'] for r in q['lines']})==113
    OUT.mkdir(exist_ok=True);save(OUT/'selection.json',s);save(OUT/'one-order-quantities.json',q)
    end=datetime.now(timezone.utc);start=datetime.fromisoformat('2026-10-01T21:28:50+00:00')
    save(OUT/'work-time.json',dict(start_utc=start.isoformat(),end_utc=end.isoformat(),wall_seconds=(end-start).total_seconds(),
        kind='Resumed Pi selection window including hook/instruction setup; previous construction time in pi-interface-final-r2/deadline-checkpoint.json; final manifest sealing follows',
        result='E2 R32 plus nominal complete Pi/BUS R33; no physical PASS',newly_selected_stls=4,new_print_jobs=1,
        previously_exported_native_candidate_stls=4,corrected_additional_exports=2,copied_unchanged_native_exports=2,
        corrections=['BUS native orientation/manifold joint','Caddy refilled Pi nut pocket','GPIO sleeves/strap clearances and R2 solder bends','Combined E2/GPIO routes'],
        remaining=['E3','E4','full W5','K2','K3','A2','A3']))
    pins={r['path']:r['sha256'] for r in parent['files']}
    deps=[OLD/'manifest.json',OLD/'work-time.json',Path(__file__),ROOT/'tools/electronics/pi_final_wiring_card_r1.py']
    folders=[OUT,F,N,C/'pi-complete-native-r1']+[E/n for n in ('pi-wiring-complete-r13','pi-gpio-integrated-r10','pi-bus-mount-r3','pi-power-usb-r4','pi-cable-caddy-r3','pi-bus-primary-r1')]
    for folder in folders:
        deps +=[p for p in folder.iterdir() if p.is_file() and p.suffix!='.FCBak' and p.name not in ('manifest.json','validation.json','PiWiringInterface.pre-recompute.FCStd')]
    # Follow local source imports only, not every obsolete candidate folder.
    seen=set();queue=[ROOT/'tools/cad/pi_complete_native_r2.py',ROOT/'tools/cad/pi_complete_native_r1.py',ROOT/'tools/cad/pi_complete_native_finish_r1.py',ROOT/'tools/electronics/pi_interface_final_r1.py',ROOT/'tools/electronics/pi_checkpoint_preview.py',ROOT/'tools/electronics/pi_wiring_complete_r13.py',ROOT/'tools/electronics/pi_power_usb_r4.py',ROOT/'tools/electronics/pi_cable_caddy_r3.py',ROOT/'tools/electronics/pi_bus_mount_r3.py',ROOT/'tools/electronics/pi_gpio_integrated_checks_r10.py']
    while queue:
        p=queue.pop()
        if p in seen:continue
        seen.add(p);deps.append(p)
        for node in ast.walk(ast.parse(p.read_text(encoding='utf-8-sig'))):
            names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module] if isinstance(node,ast.ImportFrom) and node.module else []
            for name in names:
                for sub in ('tools/electronics','tools/cad'):
                    t=ROOT/sub/(name+'.py')
                    if t.exists():queue.append(t);break
    for p in deps:
        rel=p.relative_to(ROOT).as_posix();h=sha(p)
        assert rel not in pins or pins[rel]==h,rel;pins[rel]=h
    assert all(pins[r['path']]==r['sha256'] for r in parent['files'])
    gates={g:dict(status='open',reason='Fullphase1 incomplete or phase2 physical trials') for g in REQUIRED_GATES}
    gates['geometry']=dict(status='pass',reason='Affected native Pi prints/terminal sleeves/stacks/tool and tray-lift screen only',evidence=[(N/'checks.json').relative_to(ROOT).as_posix(),(F/'checks.json').relative_to(ROOT).as_posix()])
    m=dict(schema_version=1,readiness='prototype',phase1_percent=65,CP_PI_complete=True,E2_complete=True,new_stls=4,newly_selected_stls=4,
        parent_pins_preserved=len(parent['files']),files=[dict(path=p,sha256=h) for p,h in sorted(pins.items())],gates=gates)
    report=verify(ROOT,m);assert report['integrity_ok'];assert not verify(ROOT,m,True)['integrity_ok']
    save(OUT/'manifest.json',m);save(OUT/'validation.json',dict(integrity=report,parent_pins_preserved=len(parent['files']),PNG_inspected=True,print_ready_denied=True,physical_pass=False))
    print(json.dumps(dict(CP_PI_complete=True,E2_complete=True,phase1_percent=65,jobs=71,installed_petg_parts=110,fit_samples=4,quantity_lines=113,pins=len(pins),parent_pins=len(parent['files']))))
if __name__=='__main__':main()
