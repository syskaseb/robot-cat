"""Full Pi footprint/height and retained mating budgets, no placement approval.

Official DXF footprints and labelled PNG heights are not manufacturer STEP
solids. Project-only ports, extra fit margins and USB boot envelopes stay so.
"""
import json
import time
from pathlib import Path
from compose_feline_n01_allocation import ROOT, OUT, sha, plus, mv

REF=ROOT/'hardware/reference/pi-interface-2026-10-01'
BASE=OUT.parent


def entities(path):
    lines=path.read_text(encoding='utf-8').splitlines();assert len(lines)%2==0
    active=False;kind='';data=[]
    for code,value in zip(lines[::2],lines[1::2]):
        code,value=code.strip(),value.strip()
        if code=='0':
            if active and kind:yield kind,data
            kind=value;data=[]
            if value=='ENDSEC':active=False
        else:
            if code=='2' and value=='ENTITIES':active=True
            data.append((code,value))


def compose():
    tick=time.monotonic()
    files=dict(dxf=REF/'pi4-mechanical.dxf',drawing=REF/'pi4-mechanical.png',
        e1=BASE/'body-harness-checkpoint/e1-selection.json',
        common=BASE/'body-harness-checkpoint/u1-common-wiring-plan.json',
        modules=OUT/'n01-module-plan-r5.json',extra=OUT/'n01-all-extra-interface-contract.json')
    p={k:json.loads(f.read_text()) for k,f in files.items() if f.suffix=='.json'}
    assert p['e1']['selected'] and p['e1']['E1_complete']
    g=next(g for g in p['modules']['groups'] if g['role']=='Pi4')
    polygons={dict(r).get('5'):r for k,r in entities(files['dxf']) if k=='LWPOLYLINE'}
    # Every listed height is visibly labelled on the official drawing.
    # Put it above PCB TOP as a conservative project datum interpretation;
    # this extra1.6mm is not a supplier statement about the drawing's datum.
    parts=[]
    for role,handle,height in [('USB_A_rear','A4',16),('USB_A_front','348',16),
        ('Ethernet','283',13.5),('USB_C','234',3.2),('GPIO_header','D94',8.5),
        ('HDMI0','119',3),('HDMI1','F4',3),('CSI','2A3',5.5),('DSI','2C5',5.5),
        ('Audio','2D7',6),('CPU','D28',2.4)]:
        r=polygons[handle];assert dict(r)['8']=='PARTS_TOP'
        xs=[float(v) for c,v in r if c=='10'];ys=[float(v) for c,v in r if c=='20']
        footprint=[min(xs),min(ys),max(xs),max(ys)]
        source=[[footprint[0]-19,footprint[1]-28,49.32],
                [footprint[2]-19,footprint[3]-28,49.32+height]]
        corners=[plus(mv(g['rotation_rows'],[source[i][0],source[j][1],source[k][2]]),g['translation_mm'])
            for i in range(2) for j in range(2) for k in range(2)]
        parts.append(dict(role=role,source_DXF_handle=handle,official_footprint_board_XY_mm=footprint,
            official_drawing_label_Z_mm=height,source_bounds_mm=source,
            current_bounds_mm=[[min(c[i] for c in corners) for i in range(3)],
                               [max(c[i] for c in corners) for i in range(3)]],
            kind='official_footprint_plus_conservative_height_reservation_NOT_supplier_solid',
            physical_contact_cannot_be_inferred_from_reservation_overlap=True))
    assert len(parts)==11
    receiver=p['common']['USB_receiver'];assert receiver['SKU']=='Delock60047'
    # The occupied female1992 housing is taller than the bare GPIO header.
    # Its project source footprint follows official header position. Neither
    # contact insertion nor mating tolerances have been measured here.
    more=[dict(role='GPIO1992OccupiedHousing',source_bounds_mm=[[-12.05,21.95,51.32],[39.05,27.05,65.57]],
        kind='selected_Pololu1992_mated_project_reservation',
        basis='50.8+/-0.30 x5.10 x14.0+/-0.25; whole-header mating assumptions retained',
        supplier_mated_pose_guaranteed=False)]
    for role,b in receiver['reservations_mm'].items():
        more.append(dict(role=role,source_bounds_mm=[b[:3],b[3:]],kind='retained_E1_USB_C_project_reservation',
            supplier_mated_pose_guaranteed=False))
    # Explicit conservative allowances for unlabelled small components and
    # occupied microSD; not invented guaranteed component heights.
    more.extend([dict(role='UnlabelledTopComponentsBudget',source_bounds_mm=[[-19,-28,49.32],[66,28,53.32]],
        kind='project_4mm_component_budget_not_actual_material'),
        dict(role='microSDCardAndBottomBudget',source_bounds_mm=[[-21.265,-5.89,44.72],[-5.865,6.1,47.72]],
        kind='project_3mm_bottom_budget_DXF_D42_D43_not_actual_material')])
    # Manufacturer page confirms straightUSB2.0 A/C and500mm, but provides no
    # mould dimensions. Retain a named removable fit budget, not a supplier CAD.
    a=next(r for r in parts if r['role']=='USB_A_front');bb=a['source_bounds_mm'];cy=sum(v[1] for v in bb)/2
    lower_port_cz=49.32+4.5
    data_plug=dict(SKU='LanbergCA-USBO-10CU-0005-BK',catalog_total_mm=500,
        source_bounds_mm=[[69,cy-7.5,lower_port_cz-4.5],[95,cy+7.5,lower_port_cz+4.5]],
        source_wire_mouth_mm=[95,cy,lower_port_cz],source_departure_axis=[1,0,0],
        reserved_unplug_stroke_mm=15,independent_first_jacket_grip_mm=9,
        project_minimum_fixed_bend_mm=30,project_jacket_radius_mm=2.5,
        basis='PROJECT26x15x9 mould and lower-port centre4.5 above PCBtop, not supplied dimensions',
        selected_port_pose_qualified=False,
        source='https://lanberg.eu/product/usb-c-m-usb-a-m-2-0-cable-0-5m-black-lanberg',
        manufacturer_mould_dimensions_found=False)
    gpio=[e for r in p['extra']['sections'] for e in r['ends'] if e['group']=='Pi4']
    assert len(gpio)==5
    return dict(status='FULL_PI_PORT_AND_RETAINED_MATING_BUDGET_NOT_PLACEMENT_APPROVAL',
        selected=False,N01_complete=False,physical_pass=False,parts=parts,additional_reservations=more,
        full_selected_USB_C_receiver=receiver,GPIO_endpoints=gpio,USB_A_data_plug_budget=data_plug,
        PCB_source_bounds_mm=[[-19,-28,47.72],[66,28,49.32]],current_Pi_transform=g,
        missing_previous_scene_features='Eleven Pi source shapes were nominalPCB and mounting hardware, not full connectors',
        holds=['EntirePi/occupiedGPIO/USB-Adata/USB-Cpower/frame/mount and wholeWAGO layout together',
               'Delivered mating/boot/component bounds remain unpowered fit gates; reservation overlap is not physical collision',
               'Full500USB middle must retain cable and independent restraints, not use bare connector centre as cable exit'],
        selected_parts_or_ECAD_changed=False,
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (*files.values(),Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,4))


if __name__=='__main__':
    dest=OUT/'n01-pi-full-port-contract.json';assert not dest.exists()
    p=compose();dest.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(p['status'],len(p['parts']),len(p['additional_reservations']),p['worker_seconds'])
