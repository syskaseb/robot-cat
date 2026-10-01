"""Finish lengths/pinout from saved final centreline replacements, not guesses."""
import json,math
from pathlib import Path
import pi_wiring_complete_r1 as M
ROOT=M.ROOT;E=ROOT/'hardware/electronics/full-cat';F=E/'pi-interface-final-r2'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
    result=read(F/'checks.json');assert not result['hits']
    old=E/'pi-wiring-complete-r13';routes=read(old/'checks.json')['routes'];rows=[]
    for row in routes:
        n=row['wire'];edges={p.name:p for p in old.glob(n+'_*CENTERLINE.brep')}
        edges.update({p.name:p for p in F.glob(n+'_*CENTERLINE.brep')})
        ins=sum(M.load(p).Edges[0].Length for name,p in edges.items() if '_insulated_' in name)
        bare=sum(M.load(p).Edges[0].Length for name,p in edges.items() if '_bare_' in name)
        need=ins+bare+6+30;assert need<=600
        r=dict(row);r.update(insulated_route_mm=ins,bare_tail_mm=bare,required_factory_length_mm=need,factory_margin_mm=600-need,
            factory_lead='Pololu1871 brown26AWG nominal600mm; actual area0.129mm2, CAD copper radius reserve0.14mm2',
            Pi_contact='Factory female in1992; no hand-crimp; numbered physical Pi pin',
            cassette_contact='Trim female crimp only at cassette end after dry-fit; solder named pad; do not add an uncounted splice',
            insulation_blank_mm=15,insulation_overlap_mm=6,takeoff_radius_mm=2,
            geometry_sources={p.relative_to(ROOT).as_posix():M.sha(p) for p in edges.values()})
        rows.append(r)
    c=read(E/'pi-power-usb-r4/checks.json')
    card=dict(status='SELECTABLE_NOMINAL_PI_WIRING',GPIO=rows,
        J8='Physical1/3/5/6/11 only, pin1 marked on non-keyed2x20housing;5V2/4 empty; unplug housing with power off',
        power=dict(cable='JoyITK1474EAN4250236828305',red='MAINVOUT5.10V->PiUSB-C5V',black='MAINGNDOUT->PiUSB-CGND',
            nominal_area_mm2=.823,strip_mm=5,pad_upper_bare_neck_mm=2,power_route_max_mm=max(c['centreline_lengths_mm'][n] for n in ('PI5V','PI_GND')),
            nominal_cut_bound_mm=c['power_max_cut_mm'],minimum_radius_mm=18,black_return_radius_mm=21.2,
            shared_factory_leftover_mm=c['power_factory1000_after_main300_margin_mm'],
            nominal_3A_R60_drop_V=c['power_drop3A_V'],remaining_connection_resistance_budget_ohm=c['remaining_connections_budget_ohm'],
            insulation='Two independent4mmRNF3/32 blanks on short bare necks; one15mmRNF3/8 COMMON outer boot with6mm intact-insulation overlap; shrink offPETG',
            actual_wire_diameter_and_voltage_drop_trial_phase2=True),
        USB=dict(cable='LanbergCA-USBO-10CU-0005-BKEAN5901969416237',ends=['PiUSB2Aeastlowerport','Waveshare25514USB-CmodeB'],
            nominal_factory_mm=500,route_mm=c['centreline_lengths_mm']['USB_BUS'],service_reserve_mm=60,body_allowance_mm=40,
            margin_mm=c['USB500_margin_mm'],radius_mm=24,cut=False,
            excess='One loose storage reserve;60service is from the same leftover pool, not an added second loop. No poweredhub, externalBUSpower or servoV+throughUSB.',
            D_G_only_servo_bus_harness='PreserveP0selecteddata/groundlead; servo power stays on its fusedMAINbranches. Finalglobal E4 stillopen.'),
        restraints={'GPIO':6,'power_USB_MAIN':4,'USB_park':2,'SKU':'111-02370','new_installed':12,'working_total':81,'existing_bag':100},
        bend_bounds_mm={'GPIO_initial':41**2/(6*27.55),'G_LOGIC_Zfans':15**2/(6*1.75),'OE_upper_fan':24.5**2/(6*math.sqrt(3**2+.03**2)),'OE_terminal_fan':14.5**2/(6*math.sqrt(3**2+1.78**2))},
        nominal_small_clearances={'G_LOGIC_to_PCB_underside_mm':.05,'OE_upper_lane_to_PCB_underside_bound_mm':.02,'G_LOGIC_to_revised_E2_return_layer_separation_minus_radii_mm':0,
            'note':'Nominal insulated-wire surface contact is allowed, NOT positive clearance/short between bare conductors. Actual OD/PCB height may require repositioning a replaceable insulated lead inphase2.'},
        E2_red_return_override=result['E2_override_budget'],
        assembly=['Fit nut pockets and tray/BUS bolts before routing power cables','Thread all ties before PCB/soldering; dry-fit leads, mark bothends and pin1','Solder and sleeve offPETG, then fasten insulation only','No battery or USB before E3/E4 review and phase2 unpowered continuity checks'],
        removal=['Allsources/USBoff; coveroff','UnplugJ8,PiUSB-C,PiUSB-A andBUSUSB-C; cut/release relevantties','Move free powerlead away from southtraykey corridor; do not pull solderedMAINends','Remove4traybolts and liftBUSbracket separately; liftPiTray15mm','Renewcut ties; soldered cassette ends stayfixed'],
        physical_pass=False,phase1_complete=False,CP_PI_complete=False,
        provisional=['Matedheader/plug/PCB heights and wireODs','Shrink wall/profile','PETG/nut/washer fit and actual hand/tool movements','Operating voltage/current/thermal readings'],
        source_script_sha256=M.sha(Path(__file__)),checks_sha256=M.sha(F/'checks.json'))
    (F/'wiring-card.json').write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'GPIO_requirements_mm':{r['wire']:r['required_factory_length_mm'] for r in rows},'physical_pass':False}))
if __name__=='__main__':main()
