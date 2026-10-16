"""One current cut/stock/tool budget; never sums historical variants.

Draws are nominal fit blanks. Stock is project supply/access, not an owned
inventory, purchase or permission to energize. Conditional E3 insulation stays
explicitly conditional. M4 guards not yet selected are not invented here.
"""
import json,math,time,re
from pathlib import Path
from collections import Counter
from plan_current_harness_interfaces import ROOT,BASE,SHA
from current_work_guard import check


def canonical_sku(s):
    if s.startswith('HELU'):return re.match(r'HELU\d+',s)[0]
    if s.startswith('LAPP'):return re.match(r'LAPP\w+',s)[0]
    return s


def run():
    check();tick=time.monotonic();pins={}
    def read(p):
        f=ROOT/p;pins[p]=SHA(f);return json.loads(f.read_text())
    prefix=BASE.relative_to(ROOT).as_posix()+'/'
    def local(n):return read(prefix+n)
    w5=local('body-harness-checkpoint/w5-nominal-material-selection.json')
    head=local('head-wiring-checkpoint/fixed-head-current-selection.json')
    tail=local('tail-wiring-checkpoint/selection.json');aux=local('aux-wiring-checkpoint/selection.json')
    e2=local('pwm-branch-checkpoint/selection.json');e1=local('body-harness-checkpoint/e1-selection.json')
    prints=local('phase1-current-print-selection.json');petg=local('phase1-filament-budget.json')
    local('phase1-current-purchased-selection-r3.json')
    read('hardware/reference/alpha-802534b-2026-10-12/dimensions.json')
    read('hardware/reference/case-retention-2026-10-16/facts.json')
    read('hardware/reference/u1-socket-connectors-2026-10-12/sleeve-facts.json')
    read('hardware/manufacturing/one-batch-prototype-r28/head-local-interface.json')
    read('hardware/electronics/full-cat/main-positive-wiring-card-r1/interface.json')
    read('hardware/electronics/full-cat/main-input-return-finish-r3/interface.json')
    retention=local('mounting-checkpoint/wago-retention-plan.json')
    rows=[dict(id=r['wire']+'/'+r['portion'],wire=r['wire'],sku=canonical_sku(r.get('sku',w5['factory_cables']['sku'])),
        nominal_fit_blank_mm=r['nominal_fit_blank_mm'],physical_unit=r['physical_unit'],source='W5',
        actual_cut_mm=None) for r in w5['portions']]
    for module,data in [('head-current',head),('tail-current',tail),('aux-current',aux)]:
        for r in data['length_stock_rows']:
            mm=r.get('conservative_continuous_fit_blank_mm',r.get('nominal_fit_blank_mm'))
            assert mm>0
            rows.append(dict(id=r['wire']+'/custom',wire=r['wire'],sku=canonical_sku(r['sku']),
                nominal_fit_blank_mm=mm,physical_unit=r['wire']+'_custom',source=module,actual_cut_mm=None))
    # W079/80 are already W5; sealed K1474 is one two-colour product.
    for r in e1['full_routes']:
        if r['wire'] in ('W079','W080'):continue
        rows.append(dict(id=r['wire']+'/fixed',wire=r['wire'],sku=r['sku'],nominal_fit_blank_mm=r['nominal_fit_blank_mm'],
            physical_unit=r['wire'],source='E1 fixed',actual_cut_mm=None))
    for r in e1['local_links']:
        rows.append(dict(id=r['ref']+'/local',wire=r['ref'],sku=r['sku_candidate'],nominal_fit_blank_mm=r['nominal_blank_mm'],
            physical_unit=r['ref'],source='E1 fixed local',actual_cut_mm=None))
    rows.append(dict(id='XP01/custom',wire='XP01',sku='HELU23302',nominal_fit_blank_mm=34,
        physical_unit='XP01_custom',source='E2',actual_cut_mm=None))
    assert len({r['id'] for r in rows})==len(rows)
    bulk=Counter()
    for r in rows:
        if r['sku'].startswith(('LAPP','HELU','TKD')) or r['sku']=='Adafruit1446':bulk[r['sku']]+=r['nominal_fit_blank_mm']
    wires=[]
    for sku,draw in sorted(bulk.items()):
        required=math.ceil(draw*1.25)
        stock=200000 if sku=='Adafruit1446' else max(7000 if sku=='LAPP4126002S' else 1000,math.ceil(required/1000)*1000)
        wires.append(dict(sku=sku,nominal_fit_draw_mm=draw,project_supply_mm=stock,
            project_spare_mm=stock-draw,actual_owned_mm=None,ordered_mm=0,
            stock_basis='Adafruit1446 manufacturer200m spool' if sku=='Adafruit1446' else 'Nominal metre cut-stock budget; historical LAPP4126002S7mMOQ retained; commercial refresh before purchase',
            uses=[r['id'] for r in rows if r['sku']==sku]))
    assert bulk['LAPP4126002S']==1185+474
    assert bulk['Adafruit1446']==e1['materials']['Adafruit1446_fixed_logic_mm']==773
    k={r['wire']:r['nominal_fit_blank_mm'] for r in w5['portions'] if 'K-1474' in r.get('sku','')}
    assert set(k)=={'W060','W078','W079','W080'}
    colour=dict(red=k['W078']+k['W079'],black=k['W060']+k['W080'])
    assert max(colour.values())<1000
    factory=dict(SR900=dict(w5['factory_cables'],not_additional_to_K2=True),
        K1474=dict(product_count=1,nominal_per_colour_mm=1000,draw_per_colour_mm=colour,paired_USB_cores_not_two_cables=True),
        JR300=dict(product_count=3,installed_cores=9,spare_product=1,three_cores_not_three_purchased_products=True),
        MG92B=dict(included_uncut_products=3,nominal_each_mm=250,additional_purchase=0),
        Pololu1871=dict(used_whole_600mm_wires=5,pack_contains=5,selected_pack_count=2,whole_wire_spares=5,
            manufacturer_url='https://www.pololu.com/product/1871'),
        E2=dict(used225mm_leads=['2147612113','2147611113','2147632113','2147631113'],quantity_each=1,
            minimum_catalogue_mm=220,not_added_to_K2_again=True),
        FHAC=dict(products_in_K2=6,included_leads_not_extra_wire_purchase=True),
        MTA=dict(products_in_K2=4,eight_factory_ends_not_eight_new_holders=True))
    tie_roles=[('W5 moving/fixed',48),('W5 receivers',21),('BUS',1),('E1 retainer',2),
        ('current head fixed pitch',16),('retained head source cases',12),('retained yaw local anchor roles',3),
        ('tail wire local/body',12),('AUX',16),('E2',10),('monitor',2)]
    ties=sum(n for _,n in tie_roles)
    lace=85+len(e1['materials']['AlphaWire802534B_lacing_blanks_mm'])
    assert lace==89 and sum(n for scope,n in tie_roles if scope.startswith('W5'))==69
    sleeves=[]
    def sleeve(sku,owner,blanks):
        for i,mm in enumerate(blanks):sleeves.append(dict(id=owner+'/'+str(i),sku=sku,nominal_blank_mm=mm,actual_cut_mm=None))
    sleeve('RNF100-1/8-9','head yaw',head['quantities']['RNF100_1_8_raw_mm'])
    sleeve('RNF100-3/16-9','head pitch and source',head['quantities']['RNF100_3_16_9_raw_mm'])
    sleeve('RNF100-1/8-9','tail',tail['quantities']['RNF100_1_8_9_raw_mm'])
    sleeve('RNF100-3/16-0','tail power',[35])
    sleeve('RNF100-3/16-9','AUX',[18,20])
    sleeve('RNF100-3/32-0','E2',e2['quantities']['RNF100_3_32_blank_mm'])
    sleeve('RNF100-3/16-0','E2',e2['quantities']['RNF100_3_16_blank_mm'])
    sleeve('RNF100-1/8-9','E2',e2['quantities']['RNF100_1_8_9_blank_mm'])
    sleeve('333-30300 TF31-3/1','12 source joins',[20]*12)
    sleeve('CR3042-000','E1 fixed logic',[r['nominal_fit_blank_mm'] for r in e1['materials']['sleeve_blanks']])
    sleeve('RNF100-3/16-0','F_PI output',[20])
    # Retained R53 shared MAIN boot replaces the W060-only outer3/16;
    # these are planning blanks, not a newly demonstrated insulation fit.
    sleeve('RNF100-3/32-0','MAIN inner necks',[7,4])
    sleeve('RNF100-3/8-0','MAIN shared outer',[20])
    st=Counter()
    for r in sleeves:st[r['sku']]+=r['nominal_blank_mm']
    sleeve_stock=[dict(sku=s,cut_mm=n,project_spare_mm=200,
        nominal_supply_unit_mm=30000 if s.startswith('333-') else 1220,
        supply_units=1,owned_units=None,ordered=0,
        note='TF31 manufacturer30m reel, not0.5m invented retail unit; other TE standard stick stock, verify exact suffix/delivery before purchase') for s,n in st.items()]
    for r in sleeve_stock:assert r['cut_mm']+r['project_spare_mm']<=r['nominal_supply_unit_mm']
    materials=[
        dict(sku='AlphaWire802534B',installed_blanks=lace,blank_mm=150,cut_draw_mm=lace*150,
            project_practice_mm=400,project_required_access_mm=20000,manufacturer_spool_yards=500,
            nominal_spool_mm=457200,minimum_spool_mm=443484,selected_spool_count=1,
            note='One shared spool or verified sameSKU borrowed cut supply>=20m, not several project15m retail spools; no order.'),
        dict(sku='111-02370 T18I',installed=ties,allocations=[dict(role=s,installed=n) for s,n in tie_roles],
            project_service_spares=math.ceil(ties*.25),nominal_pack100_count=math.ceil(ties*1.25/100),
            no_double_count='W4 existing E2 shared tie already in E2 ten; W1 shared tail pair does not create another product'),
        dict(sku='111-01910 T18R',installed=e1['materials']['new_T18R'],nominal_pack100_count=1,
            no_double_count='W5 two MAINpower ties are in E1 nine, not another two'),
        dict(sku='3M SJ4570',installed_pairs=20,raw_pieces=40,raw_piece_xy_mm=[20,10],
            selected_project_strip_mm=[25,1000],nominal_cut_run_mm=800,
            no_double_count='Head source1pair and AUX2pairs reused from20, not23; spare stock remains for M4 after actual case allocation'),
        dict(sku='3M VHB4905',patches=w5['case_adhesive']['quantity_patches'],cut_draw_mm=374,
            nominal_installed_thickness_mm=.5,project_access_strip_mm=[12.7,500],
            stock_unit='One manufacturer4905roll at least12.7mmwide/500mmlong; narrower12mm may NOT silently substitute. Commercial cut supply verified before purchase.',
            case_only=True),
        dict(sku='Henkel EA3430 IDH242865',shared_cartridge_ml=24,selected_cartridges=1,
            known_case_working_allowance_ml=1,R6_and_coupon_project_allowance_ml=8,actual_used_ml=None),
        dict(sku='3M Temflex165 LAPP61721030',nominal_roll_width_mm=15,nominal_roll_length_mm=10000,
            E1_replacement_wraps_mm=[[300,10],[300,10]],retained_E2_wrap_mm=[300,10],
            tail_wrap_mm=[50,15],AUX_contribution_mm=60,selected_roll_count=1,
            note='Three E2 wraps total, not old three plus new two. Individual insulation coverage is a phase2/E3 gate.'),
        dict(sku='tesa4965',patches_mm=e2['quantities']['tesa4965_patch_mm'],
            project_strip_mm=[25,200],actual_owned=None),
        dict(sku='Closed cell PE foam 1mm',battery_pad_xy_mm=[107,36],project_sheet_xy_mm=[150,100]),
        dict(sku='Closed cell PE foam 2mm',E1_retainer_pads_xyz_mm=[[5,3,2],[5,3,2]],project_sheet_xy_mm=[100,100],
            note='Project cushion specification, not proof of supplied hardness, flame rating or primary electrical insulation'),
        dict(sku='Sunlu PETG black1.75mm Botland24167',selected_1kg_spools=max(3,petg['selected_1kg_spools']),
            budget=prefix+'phase1-filament-budget.json',profile_slicer_and_physical_strength_not_qualified=True),
    ]
    workshop=read('hardware/electronics/full-cat/assembly-tools-k3-r2/tools.json')
    crimps=read('hardware/electronics/full-cat/termination-tools-k3-r1/tools.json')
    legacy=read('hardware/electronics/full-cat/assembly-materials-k3-r1/materials.json')
    # Reuse only processing supplies, never historical installed tie/braid sets.
    processing=[r for r in legacy['lines'] if any(x in str(r).lower() for x in ('abrasive','ipa','242865'))]
    result=dict(status='CURRENT_WHOLE_MATERIAL_AND_TOOL_BUDGET_REVIEW',selected=False,K3_complete=False,result_id='K3',
        physical_pass=False,purchase_authorized=False,wire_blanks=rows,bulk_wire_stock=wires,factory_units=factory,
        sleeves=sleeves,sleeve_stock=sleeve_stock,materials=materials,processing_supplies=processing,
        solder=workshop['solder'],workshop_tools=workshop['tools'],workshop_requirements=workshop['workshop_requirements'],
        crimp_tools=crimps['tools'],crimp_processes=crimps['processes'],
        tooling_provision='Access by borrowing or competent service allowed. Nothing purchased and actual owned tools unknown. Demonstrate matching terminal/wire/tool sample before making powered harness.',
        eliminated_duplicates=['Historical920mm not a fifthsource wire','Old moving pitch loops not added to new head',
            'W079/80 are W5 once, not E1 again','MAINpower2ties/1lace already inE1nine/four',
            'R53 old wire lengths/ties/braid are not another installed set','20WAGO SJ4570 pairs include three reusedW1/W3'],
        review_gaps=['Confirm complete inherited MAIN/source insulation recipe against current end geometry; do not label stock as its qualification',
            'Three retained yaw anchor tie identities and full shared E2/W4 count require explicit allocation binding',
            '4905/tesa cut supply exact commercial unit vs project strip must be distinguished before selection'],
        phase2_gates=['Actual Cu/OD/usable lengths/retention/polarity and E3 power qualification remain open',
            'All sleeve/restricted recovery/coverage, adhesive/substrate/cure, ties/lacing/PETG/tool access trials must be performed',
            'Manufacturer spool/cut-stock budget is not actual inventory or current supplier price/availability'],
        source_sha256=pins,worker_seconds=round(time.monotonic()-tick,3))
    f=BASE/'phase1-material-plan.json';f.write_text(json.dumps(result,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(wire_blanks=len(rows),bulk_products=len(wires),sleeves=len(sleeves),T18I=ties,laces=lace,review_gaps=len(result['review_gaps']),seconds=result['worker_seconds'])))


if __name__=='__main__':run()
