"""One complete34external-section interface contract, not a routing approval.

Use selected named pad/receiving sources instead of master display curves where
those have stale frames. Local fuse datums remain unplaced until joint layout.
Accounting boundaries are explicitly NOT plugs or extra solder joints.
"""
import json
import math
import sys
import time
from pathlib import Path
from compose_feline_n01_allocation import ROOT,OUT,sha,mv,plus

BASE=OUT.parent


def compose():
    tick=time.monotonic()
    files={k:p for k,p in dict(source=OUT/'n01-extra-circuit-source-ends.json',
        wago=OUT/'n01-twenty-wago-port-contract.json',modules=OUT/'n01-module-plan-r5.json',
        inventory=OUT/'n01-remaining-selected-inventory.json',
        carrier=BASE/'body-harness-checkpoint/u1-socket-carrier-plan.json',
        common=BASE/'body-harness-checkpoint/u1-common-wiring-plan.json',
        tail=BASE/'tail-wiring-checkpoint/selection.json',
        local_sources=OUT/'n01-selected-local-head-tail-sources.json',
        head=BASE/'head-supply-checkpoint/selection.json',
        head_frame=ROOT/'tools/cad/plan_current_head_wiring.py',
        ecad=ROOT/'hardware/electronics/kicad-current/design.json').items()}
    data={k:json.loads(p.read_text()) for k,p in files.items() if p.suffix=='.json'}
    groups={g['role']:g for g in data['modules']['groups']}
    guides={r['label']:r for r in data['source']['source_guides']}
    wg={r['endpoint']:(st,r) for st in data['wago']['stations'] for r in st['occupied_ports']}
    endpoints={};forms=[];holds=[]
    def transfer(group,p,d):
        g=groups[group]
        return plus(mv(g['rotation_rows'],p),g['translation_mm']),mv(g['rotation_rows'],d)
    def put(ref,group,p,d,basis,**extra):
        assert ref not in endpoints,ref
        endpoints[ref]=dict(endpoint=ref,group=group,point_mm=p,departure_axis=d,basis=basis,
            supplier_datum_guaranteed=False,current_route_or_grip_verified=False,**extra)
    for ref,(st,r) in wg.items():
        put(ref,st['current_group'],r['point_mm'],r['departure_axis'],st['prototype']['basis'],
            physical_cavity=r['physical_port'],schematic_cavity=r['schematic_port'])
    external11={}
    for r in data['source']['current_external_ends']:
        external11[r['wire'],r['side']]=dict(r)
    # Infer actual carrier origin from a calibrated named pad, never from a
    # board bbox centre. E1 deliberate OE/PCA rebindings do not move B1/B2/B3.
    logic=next(r for r in data['source']['current_external_ends'] if r['wire']=='XL01' and r['side']=='b')
    term={r['ref']:r for r in data['carrier']['terminals']}
    local=term['LOGIC3V3.in'];old=logic['source_point_mm'];origin=[old[0]-local['x'],old[1]-local['y'],old[2]]
    assert math.dist(origin,[91.59,0,84.3202])<1e-5
    for ref,physical in (('R1.2','B1.out'),('R2.2','B2.out'),('R3.2','B3.out'),
        ('U_PWM.3','XP02.board'),('U_PWM.2','XP03.board')):
        t=term[physical];q=[origin[0]+t['x'],origin[1]+t['y'],origin[2]]
        p,d=transfer('PWM1608_U1',q,[0,0,1])
        put(ref,'PWM1608_U1',p,d,'Named selected carrier terminal, common copper net; not the IC leg or an invented external board pinout',
            named_physical_interface=physical,source_point_mm=q,formed_bare_exit_required=True)
    # Actual AUX formed bare guide joins exact pad to jacket, which may lie
    # outside the board outline. Do not mistake that jacket end for a pad.
    for wire,ref in (('XA02','AUX.VIN'),('XA03','AUX.VOUT'),('XA04','AUX.GND')):
        bare=guides['wire/'+wire+'_bare'];es=bare['source_ends'];assert len(es)==2
        pad=min(es,key=lambda e:e['source_point_mm'][2]);jacket=max(es,key=lambda e:e['source_point_mm'][2])
        js=guides['wire/'+wire]['source_ends']
        jacket_land=min(js,key=lambda e:math.dist(e['source_point_mm'],jacket['source_point_mm']))
        assert abs(math.dist(jacket_land['source_point_mm'],jacket['source_point_mm'])-3)<1e-5
        p,d=transfer('AUX4092',jacket_land['source_point_mm'],jacket_land['source_departure_into_guide'])
        pp,_=transfer('AUX4092',pad['source_point_mm'],[0,0,1])
        put(ref,'AUX4092',p,d,'Saved selected formed bare AUX end, current rigid transform ONCE; jacket land not PCB pad',
            actual_source_pad_mm=pp,source_point_mm=jacket_land['source_point_mm'],bare_guide=bare['object'],
            bare_to_jacket_source_overlap_mm=3,bare_tip_source_point_mm=jacket['source_point_mm'])
        forms.append(dict(wire=wire,source_guide=bare['object'],sha256=bare['source_guide_sha256'],
            current_group='AUX4092',selected_insulation='Temflex165 two layers, delivered coverage gate',
            no_extra_joint_at_pad_to_jacket_boundary=True))
    # Rolled selected FHAC AUX case: source input/output faces differ from
    # the start/end of its complete historical factory curves.
    g=groups['F_AUX'];lo,hi=g['current_bounds_mm'];mid=[(a+b)/2 for a,b in zip(lo,hi)]
    assert abs(hi[0]-lo[0]-51)<1e-4
    for side,ref in ((-1,'F_AUX.in'),(1,'F_AUX.out')):
        q=[lo[0] if side<0 else hi[0],mid[1],mid[2]];p,d=transfer('F_AUX',q,[side,0,0])
        put(ref,'F_AUX',p,d,'Rolled actual selected51mm source casing face + current rigid transform',
            minimum_jacket_grip_mm=9,factory100mm_is_provisional=True)
    # Both JPWM mouths are explicitly2.3mm outside the mould, from saved
    # selected physical wire exits. Keep both halves, including both power poles.
    for wire,ref,index in (('XP02_source','JPWM_SOURCE.1',1),('XP03_source','JPWM_SOURCE.2',1),
        ('XP02_module','JPWM_MODULE.1',0),('XP03_module','JPWM_MODULE.2',0)):
        guide=guides['wire/pwm-branch-checkpoint/'+wire];e=guide['source_ends'][index]
        p,d=transfer('JPWM',e['source_point_mm'],e['source_departure_into_guide'])
        put(ref,'JPWM',p,d,'Named selected JPWM source/module wire mouth, outside mould, transform ONCE',
            physical_side='source' if 'SOURCE' in ref else 'module',source_point_mm=e['source_point_mm'])
    # Factory CASE exits are1mm below FHAC case bounding-box mid-Z in the
    # preserved source. This is a project datum, not a manufacturer tolerance.
    templates={r['role']:r for r in data['inventory']['parts'] if not r['placed_current']}
    fuse_datums={}
    for role,inputlabel,outputlabel in (
        ('F_HY','wire/F_HY_factory_in','wire/head-supply-checkpoint/F_HY_out'),
        ('F_HP','wire/head-supply-checkpoint/F_HP_input_prefix','wire/head-supply-checkpoint/F_HP_out'),
        ('F_TY','wire/tail-wiring-checkpoint/F_TY_input_prefix','wire/tail-wiring-checkpoint/F_TY_factory_out')):
        lo,hi=templates[role]['bounds_mm'];centre=[(a+b)/2 for a,b in zip(lo,hi)]
        for label,ref in ((inputlabel,role+'.in'),(outputlabel,role+'.out')):
            es=guides[label]['source_ends'];matches=[e for e in es if min(abs(e['source_point_mm'][0]-lo[0]),abs(e['source_point_mm'][0]-hi[0]))<1e-5 and abs(e['source_point_mm'][1]-centre[1])<1e-5]
            assert len(matches)==1,(role,label)
            e=matches[0];q=[a-b for a,b in zip(e['source_point_mm'],centre)]
            assert abs(q[2]+1)<1e-5,(role,'Case midZ is not leadZ')
            side=-1 if q[0]<0 else 1
            put(ref,role,None,[side,0,0],'Exact named saved guide on actual source case face; target module still unplaced',
                local_point_mm=q,source_point_mm=e['source_point_mm'],source_guide=guides[label]['object'],
                allocation_required=True,factory100mm_is_provisional=True)
            fuse_datums[ref]=q
    # Existing sealed inline fuse/insulation: electrical accounting contacts
    # are inside the42mm sleeve. Geometry grips start beyond sleeve, not there.
    lo,hi=templates['F_PWM']['bounds_mm'];centre=[(a+b)/2 for a,b in zip(lo,hi)]
    for ref,label,index,side in (('F_PWM.in','wire/pwm-branch-checkpoint/XP01',1,-1),
        ('F_PWM.out','wire/pwm-branch-checkpoint/XP02_source',0,1)):
        q=guides[label]['source_ends'][index]['source_point_mm'];loc=[a-b for a,b in zip(q,centre)]
        put(ref,'F_PWM',None,[side,0,0],'Selected inline-fuse accounting point inside sleeve, NOT external jacket mouth',
            local_accounting_contact_mm=loc,local_jacket_exit_mm=[side*21,0,0],allocation_required=True,
            independent_grip_after_sleeve_mm=9)
    # Six whole head links terminate at already qualified receiving boundaries.
    # Both selected W3 yaw GUIDE and saved W2 local curves ALREADY include
    # CP2SHIFT. Their actual native boundary receipt proves this; shift neither
    # a second time. The boundary is not a physical JR face or an added joint.
    for wire,ref in (('XB12','C_HY.V+'),('XB13','C_HY.GND'),('XS13','C_HY.PWM')):
        es=guides['wire/head-supply-checkpoint/'+wire]['source_ends']
        matches=[e for e in es if abs(e['source_point_mm'][0]+112)<1e-5]
        assert len(matches)==1,(wire,'Named fixed yaw boundary is not maximumX source on signal wire')
        e=matches[0]
        receipt=next(b for b in data['local_sources']['boundaries'] if b['wire']==wire)
        assert math.dist(e['source_point_mm'],receipt['source_CP2_point_mm'])<1e-5
        assert receipt['native_gap_mm']<1e-5 and receipt['CP2SHIFT_already_in_both_selected_sources']
        p,d=transfer('HeadMechanism',e['source_point_mm'],e['source_departure_into_guide'])
        assert math.dist(p,receipt['current_point_mm'])<1e-5
        put(ref,'HeadMechanism',p,d,'Actual selected W3/W2 native boundary, already CP2; current head transform ONCE; no new joint',
            accounting_boundary_not_connector_pin=True,source_frame_registration='Selected W3/W2 already CP2; R5 once, NO additional SHIFT',
            full_local_factory_and_JR_required=True,receiver_mould_face_qualification_pending=False,
            selected_W2_boundary_gap_mm=receipt['native_gap_mm'])
    for wire,ref in (('XB22','C_HP.V+'),('XB23','C_HP.GND'),('XS23','C_HP.PWM')):
        e=guides['headwire/0/Interface_'+wire]['source_ends'][1]
        p,d=transfer('HeadMechanism',e['source_point_mm'],e['source_departure_into_guide'])
        put(ref,'HeadMechanism',p,d,'Current fixed JR actual named guide on source case face, current head transform ONCE',
            source_point_mm=e['source_point_mm'],manufacturer_cavity_view_is_delivery_gate=True)
    assert data['tail']['selected'] and data['tail']['tail_boundary_x_mm']==88
    for wire,ref in (('XB32','C_TY.V+'),('XB33','C_TY.GND'),('XS33','C_TY.PWM')):
        part=data['tail']['routes'][wire]['parts'][-1];q=part['end'];assert q[0]==88
        d=[-x for x in [1,0,0]]
        put(ref,'TailElectricalFixed',q,d,'SELECTED W4 accounting boundary88, not older master display guide at68 or actual JR pin',
            accounting_boundary_not_connector_pin=True,full_local_factory_and_JR_required=True,
            selected_tail_native=data['tail']['current_native'],source_case_bounds_mm=data['tail']['JR_bounds_mm'])
    # Compose45schematic rows without allocating duplicate wires insideU1.
    internal=set(data['source']['retained_U1_internal_sections']);sections=[]
    for wire in data['ecad']['wires']:
        if wire['id'].startswith('W0') or wire['id'] in internal:continue
        ends=[]
        for side in ('a','b'):
            ref=wire[side]
            if (wire['id'],side) in external11:
                r=external11[wire['id'],side]
                ends.append(dict(endpoint=ref,group=r['current_group'],point_mm=r['point_mm'],
                    departure_axis=r['departure_axis'],basis=r['basis'],source_kind=r['source_kind'],
                    named_physical_interface=r['named_physical_interface'],current_route_or_grip_verified=False))
            else:assert ref in endpoints,(wire['id'],ref);ends.append(dict(endpoints[ref]))
        fixed=all(e['point_mm'] is not None for e in ends)
        sections.append(dict(wire=wire['id'],ends=ends,fixed_endpoint_pair=fixed,
            straight_chord_only_mm=math.dist(*(e['point_mm'] for e in ends)) if fixed else None,
            chord_is_not_route_or_cut_length=True,full_route_or_stock_accepted=False))
    assert len(sections)==34 and len({r['wire'] for r in sections})==34
    return dict(status='ALL34EXTERNAL_EXTRA_INTERFACES_ACCOUNTED_NOT_LAYOUT_OR_WIRING_APPROVAL',
        selected=False,N01_complete=False,physical_pass=False,sections=sections,
        source_local_fuse_ports=fuse_datums,internal_sections_retained_not_duplicated=sorted(internal),
        extra_external_sections=34,extra_external_section_ends=68,
        fixed_pairs=sum(r['fixed_endpoint_pair'] for r in sections),
        unplaced_module_endpoints=sum(e['point_mm'] is None for r in sections for e in r['ends']),
        AUX_formed_bare_forms=forms,current_E1_carrier_origin_source_mm=origin,
        explicit_geometry_holds=['PiGPIO five housing mouthsZ115.7 above roof112',
            'PCA top solder exits require supported formed bare-to-horizontal plan, not9mmUP through roof',
            'Three FHAC factory exits below case midZ by1mm; do not use centreZ',
            'Yaw accounting boundary native registration qualified; retained factory220 plus30mm delivery fit budget still requires shared allocation',
            'Full selected tail rail/JR/factory250 source bounds125..155/-54..-42/Z107..117 need common body/cowl allocation; do not drop this reference',
            'All34fullroutes, all20independent grips, new head root/33oldneck replacement and assembly remain OPEN'],
        selected_parts_or_ECAD_changed=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (*files.values(),Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,4))


def main():
    dest=OUT/'n01-all-extra-interface-contract.json'
    if dest.exists():
        assert '--update-own-unselected-draft' in sys.argv
        old=json.loads(dest.read_text());assert not old['selected'] and not old['N01_complete']
    p=compose();dest.write_text(json.dumps(p,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(p['status'],p['fixed_pairs'],p['unplaced_module_endpoints'],p['worker_seconds'])


if __name__=='__main__':main()
