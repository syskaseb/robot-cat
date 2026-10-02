"""One manufacturing card for the nominal F_PI and MAIN input interface."""
from pathlib import Path
import copy,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/cad'))
from release_check import sha256
OUT=ROOT/'hardware/electronics/full-cat/main-positive-wiring-card-r1'
SCREEN=ROOT/'hardware/electronics/full-cat/main-positive-complete-r8'
NATIVE=ROOT/'hardware/electronics/full-cat/main-positive-native-r2'

def payload(screen,native):
    assert screen['status']=='SCREEN_CLEAR_WITH_EXPLICIT_SOFT_FIT' and not screen['blocking_hits']
    assert native['status']=='NATIVE_COMPLETE_WITH_SOFT_FIT_CONDITION'
    lengths=screen['lengths_mm']
    rows=[dict(wire='W043',source='P_SYS.2',destination='F_PI.in',material='FHAC0001ZXJ factory black16AWG',
          route_to_datum_mm=lengths['W043'],nominal_blank_mm=40,prepared_end='Trim factory tinned tip; fresh12..14mm strip, ONE untinned wire in WAGO221-615',
          required_bound_mm=lengths['W043']+14+8),
          dict(wire='W077',source='F_PI.out',destination='SPLICE_PI.16',material='FHAC0001ZXJ factory black16AWG',
          route_to_datum_mm=lengths['W077'],nominal_blank_mm=80,prepared_end='Fresh8mm strip, solder overlap8mm with W078, off PETG',
          required_bound_mm=lengths['W077']+4+4),
          dict(wire='W078',source='SPLICE_PI.18',destination='MAIN.VIN',material='Red18AWG0.823mm2 from SAME K-1474 cable used for Pi and W060',
          route_to_datum_mm=lengths['W078'],nominal_blank_mm=210,prepared_end='Splice8mm strip; MAIN8mm strip =5mm exposed individually insulated neck +3mm insertion allowance, trim at real pad',
          required_bound_mm=lengths['W078']+4+3+12)]
    assert all(r['required_bound_mm']<=r['nominal_blank_mm'] for r in rows)
    assert max(r['nominal_blank_mm'] for r in rows[:2])<=84.5
    result=dict(status='NOMINAL_MAIN_POSITIVE_INTERFACE_COMPLETE_WITH_PHASE2_FITS',parent='one-batch-prototype-r43',
        selected=False,W5_complete=False,physical_pass=False,collision_free=False,rows=rows,
        holder='LittelfuseFHAC0001ZXJ, fuse0287003.PXCN3A; E3 remains OPEN, not power authorization',
        confirmed_factory_lead_minimum_mm=84.5,confirmed_closed_body_including_reliefs_mm=[49,51],
        closed_height_22mm_and_factory_OD3p4_are_project_reserves=True,minimum_geometric_radius_mm=6,
        P_SYS_cage_X_mm=[-84,-76.5,-69,-61.5,-54],P_SYS_labels_plus_X=['.2','.1','.3','.4','.5'],
        cage_rule='First two labelled physical cages exchange roles on the same common potential. Electrical graph unchanged; source/BAT full route still OPEN. Not an additional connection.',
        splice=dict(axis_yz_mm=[-30,130],solder_overlap_X_mm=[36,44],bare_overlap_mm=8,
            maximum_joint_OD_project_mm=2.8,outer_sleeve='RNF-100-3/16-0-STK',blank_and_nominal_placement_mm=20,
            sleeve_X_mm=[30,50],intact_overlap_each_side_mm=6,finished_OD_project_mm=4.2,
            no_terminal_or_extra_splice=True,restraints='Two independent T18I loopsX31/49 on the integral above-WAGO beam, not around an exposed solder joint'),
        MAIN_input_insulation=dict(red_inner='RNF-100-3/32-0-STK7mm blank trimmed to5mm bare neck',
            black_inner='Retained RNF3/32 individual2mm bare neck; no change to W060',
            outer='ONE RNF-100-3/8-0-STK20mm blank, shared over two individually insulated input necks; replaces single W0603/16 outer boot, not another overlapping sleeve',
            intact_overlap_each_wire_minimum_mm=6,red_nominal_path_placement_mm=11.01,
            no_claim_blank_shrinks_to_placement=True,actual_profile_and_wall_phase2=True),
        retention=dict(large_SKU='111-03410',source_holder_large_installed=1,source_holder_small_replaced=2,
            small_SKU='111-02370',new_small_installed=4,new_small_roles=['splice left','splice right','red Deck portal','red MAIN seat'],
            prior_small_working=93,small_working_after=95,shared_small_bag=100,full_K3_census_complete=False,
            prior_large_working_allowance=20,large_working_after=21,shared_large_bag=100,
            large_loop_bound_mm=2*(56.2+23.2)+12,large_minimum_length_mm=190,
            small_loop_bounds_mm={'splice':2*(9.4+8.1)+12,'Deck':2*(8.2+7.5)+12,'MAIN':2*(9.9+11.4)+12},
            small_minimum_length_mm=145,retained_W060_MAIN_strap=True),
        stock=dict(one_K1474_factory_conductor_length_mm=1000,Pi_conductor_bound_mm=290.24916022252154,
            red_W078_mm=210,black_W060_mm=220,red_remaining_mm=1000-290.24916022252154-210,
            black_remaining_mm=1000-290.24916022252154-220,parallel_conductors_not_summed=True,no_second_K1474=True),
        source_complete=True,positive_input_complete_nominal=True,remaining_W5=['BAT/source/balance routes','other body and leg ends/routes','W025/W036 and other unfinished returns'],
        native_final_objects={'Deck':'MainPositiveDeck','MAIN':'MainPositiveAdapter'},
        soft_contacts=screen['soft_contacts'],physical_conditions=[
            'Delivered FHAC closed cap/height, OD, T30L head (6x6x4 project reserve) and source cage mouth: trim40/80mm only after dry fitting, never tension holder.',
            'Delivered splice wall/finishedOD:4.2mm is a PROJECT allowance, not a supplier guaranteed OD. Adjust parametricSpliceGrooveRadius and reprint only that Deck if needed.',
            'Shared input outer boot9.5mm expanded must fit the actual assembled pair. Keep individual copper insulation; shrink/trim off PETG, adjust local profile without treating nominal soft contact as PASS.',
            'No power until E3 protection and phase2 electrical checks. Current/thermal tests not fabricated.'])
    assert result['retention']['small_working_after']<=100
    assert result['retention']['large_working_after']<=100
    assert result['retention']['large_loop_bound_mm']<=190
    assert max(result['retention']['small_loop_bounds_mm'].values())<=145
    return result

def build_selection(card,selection,quantities,native):
    s,q=copy.deepcopy(selection),copy.deepcopy(quantities)
    for row in s['prints']:
        if row['identity']=='P0-MAIN-MOUNT-R5':key,model='MAIN','MainPositiveMount.FCStd'
        elif row.get('native','').endswith('DeckG1ExitRestraints.FCStd') or row.get('identity')=='P0-DECK-P10':key,model='Deck','DeckMainPositive.FCStd'
        else:continue
        row.update(stl='hardware/cad/studies/main-positive-native-r2/'+key+'_x1.stl',
            native='hardware/cad/studies/main-positive-native-r2/'+model,recipe=OUT.relative_to(ROOT).as_posix()+'/interface.json',
            status='conditional_hobby_phase1_selection',print_size_mm_including_5mm_brim=[v+(10 if i<2 else 0) for i,v in enumerate(native['native_checks'][key]['dimensions_mm'])])
        row['sha256']=sha256(ROOT/row['stl'])
        row['supports']='Phase2 slicer: inspect integral splice cantilever and strap channels, MAIN tongue and grooves. Not qualified here.'
    s.update(main_positive_input=OUT.relative_to(ROOT).as_posix()+'/interface.json',
             main_positive_input_sha256=sha256(OUT/'interface.json'),W5_complete=False,K3_complete=False,
             W5_recipe_precedence='R44 overrides F_PI/W043/W077/W078, integral Deck and MAIN positive seats, source physical labels and ONE shared input outer boot. R41 G1 and all R40 W060 routes/ends/other restraints retained. R33 output boot retained. No W036 trial selected.',
             current_main_input_outer_boot='Shared RNF3/8 replaces W060-only3/16 reserve; other R40 return geometry retained',
             unselected_MAIN_positive_work={'rejected_before_selection':['main-positive-complete-r3','r4','r5','r6','r7: two exact groove tangencies produce nonmanifold mesh edges'],
                                          'retained_for_evidence_only':True})
    for row in q['lines']:
        if row['id']=='tie:111-02370':row['installed']=95;row['note']+=' R44: replace2 oldF_PI small loops with1T30L; add4small splice/portal/MAIN loops. Working95, same100bag; full census OPEN.'
        elif row['id']=='consumable:p0:1':
            assert row['manufacturer_sku']=='111-03410' and row['existing_working_allowance']==20
            row.update(existing_working_allowance=21,unallocated_stock=79)
            row['note']+=' R44 adds1 explicitF_PI holder strap to the prior20 working allowance;21+79=100, same bag. Actual head6x6x4 is a project fit reserve, not supplier measurement.'
        elif row['id']=='p0:K-1474' or 'K-1474' in row.get('name','') or 'K1474' in row.get('name',''):
            row['note']+=' R44 supersedes old unrouted red150mm: W078 nominal210mm, W060black220mm retained. Per colour Pi290.249+input, redleft499.751/blackleft489.751mm; same single cable.'
        elif row['id']=='sleeve:5052942064':row['note']+=' R44 adds7mm red inner blank, retained black inner; actual neck fit/trim offPCB.'
        elif row['id']=='sleeve:5053042067':row['note']+=' R44 removes W060-only15mm outer allowance and adds20mm splice outer; shared MAIN input uses existing3/8 stock.'
        elif row['id']=='insulation:Pi:RNF-100-3/8-0-STK':
            row.update(installed_blanks=2,blank_lengths_mm=[15,20],name='TE RNF1003/8 black9.5/4.8mm COMMON MAIN input/output boots');row.pop('blank_mm',None)
            row['note']+=' R44 adds ONE20mm shared MAIN INPUT outer blank; retained output15mm commonboot unchanged. Do not add a second stock purchase.'
    assert len(q['lines'])==len(quantities['lines']) and len(s['prints'])==len(selection['prints'])
    return s,q

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/'interface.json').exists()
    screen=json.loads((SCREEN/'checks.json').read_text(encoding='utf-8'))
    native=json.loads((NATIVE/'checks.json').read_text(encoding='utf-8'))
    card=payload(screen,native)
    card['source_sha256']={p.relative_to(ROOT).as_posix():sha256(p) for p in [SCREEN/'checks.json',NATIVE/'checks.json',ROOT/'hardware/reference/fhac0001zxj-2026-10-02/README.md',Path(__file__)]}
    (OUT/'interface.json').write_text(json.dumps(card,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status=card['status'],small_ties=95,phase1_percent=70)),flush=True)

if __name__=='__main__':main()
