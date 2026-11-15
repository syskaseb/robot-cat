from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).parent;ROOT=P.parents[8] if False else Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
gate=json.loads((P/'finite-layer-and-joint-gate.json').read_bytes());nut=json.loads((P/'actual-nut-feed-and-coupon.json').read_bytes());curves=json.loads((P/'actual-source-sections.json').read_bytes())
colors={'P20_COMMON_MAIN_AUX_M2_SHOE':'#167d8d','CS_P11_rear_gate_positive_ISO10642_M3x10':'#333333','P06_S0_shared_panel':'#cc4422','PB3_M2x12_full':'#7844aa','MAIN_Pololu4853':'#398638','AUX_Pololu4092':'#398638','P11_rear_gate':'#a33b68','AUX_FULL_POPULATED_OCCUPIED_NOT_PLASTICCASE':'#b77e18'}
fig,axs=plt.subplots(1,3,figsize=(17,5.6),layout='constrained')
for ax,(sec,title) in zip(axs,[('shoe_and_frame_head_Z93','Z93: stopa dotyka istniejacego lba'),('AUX_M2_tip_to_S0_X102p159','X102.159: pelny koniec M2 nad S0'),('current_P11_AUX_post_Z103p25','Z103.25: rzeczywisty P11 i slupek AUX')]):
 for row in curves:
  if row['section']!=sec:continue
  first=True
  for line in row['curves']:
   if not line:continue
   ax.plot([p[0] for p in line],[p[1] for p in line],color=colors[row['part']],lw=1.5,label=row['part'] if first else None);first=False
 ax.set_title(title,fontsize=11);ax.set_aspect('equal')
 if sec=='AUX_M2_tip_to_S0_X102p159':ax.set_xlim(18,51);ax.set_ylim(87,112);ax.set_xlabel('Y [mm]');ax.set_ylabel('Z [mm]')
 else:ax.set_xlim(53,129);ax.set_ylim(18,51);ax.set_xlabel('X [mm]');ax.set_ylabel('Y [mm]')
 ax.grid(alpha=.2);ax.legend(fontsize=6,loc='lower left')
fig.suptitle('HOLD: rzeczywiste przekroje BRep tej samej konfiguracji; nie nowy wariant',fontsize=13)
fig.savefig(P/'actual-layer-and-blocker-sections.png',dpi=150);plt.close(fig)
# Readable stack dimension figure, explicitly source fields vs manufactured material.
fig,ax=plt.subplots(figsize=(10,5.4),layout='constrained');ax.set_xlim(0,76);ax.set_ylim(82,120)
from matplotlib.patches import Rectangle
def rect(x,z,w,h,c,label,alpha=.65):ax.add_patch(Rectangle((x,z),w,h,facecolor=c,edgecolor=c,alpha=alpha));ax.text(x+w/2,z+h/2,label,ha='center',va='center',fontsize=8)
rect(1,88.52,71,4,'#777777','actual P12/P11 ledge, top92.52')
rect(1,92.52,71,5,'#167d8d','P20 candidate: HOLD, no full STL')
for x in [9,29,54]:rect(x,97.52,3.8,6,'#167d8d','')
rect(7,103.52,30.48,1.5748,'#398638','MAIN PCB datum103.52')
rect(7,105.0948,30.48,6.1,'#74aa62','populated family STEP + optional pot')
rect(45,103.52,25.4,1.57,'#398638','AUX PCB1.57')
rect(45,101.72,25.4,1.8,'#d6a354','under-components1.8: SCOPE')
rect(45,105.09,25.4,6.13,'#d6a354','top6.1 +0.03 rounding: SCOPE')
ax.axhline(116,color='#c33',ls='--');ax.text(3,116.6,'S1 source bottom116 (not a continuous free ceiling)',fontsize=8,color='#c33')
ax.set_xlabel('schematic X position [mm], separate module footprints');ax.set_ylabel('actual world Z [mm]');ax.grid(alpha=.15);ax.set_title('One chosen stack; full AUX9.5 retained, contact annulus still FIT3')
fig.savefig(P/'module-layer-dimensions.png',dpi=145);plt.close(fig)
files=[ROOT/'hardware/reference/main-p0-2026-09-24/reg32c.step',ROOT/'hardware/reference/main-p0-2026-09-24/reg32c-drill.dxf',ROOT/'hardware/reference/aux4092-2026-09-26/reg24d-drill.dxf',ROOT/'tools/cad/open_prototype_distribution_mounts.py',P.parent/'day15-carrier-capture-first-fit/manifest.json',P.parent/'day15-carrier-capture-first-fit/carrier-capture.FCStd',P/'MAIN-primary.pdf',P/'AUX-primary.pdf']
write('source-pins.json',dict(utc=datetime.now(timezone.utc).isoformat(),primary_MAIN='https://www.pololu.com/file/0J2038/d30v33max-fine-adjust-step-down-voltage-regulator-dimensions.pdf',primary_AUX='https://www.pololu.com/file/0J1732/d36v50fx-step-down-voltage-regulator-dimensions.pdf',source_product_binding=['https://www.pololu.com/product/4853','https://www.pololu.com/product/4092'],files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in files],current_carrier_commit='4f9ce00a634651811c109ed245f917846b59c957',previous29_exact_unchanged_required=True))
missing=json.loads((P/'only-missing-current-print-layer-gate.json').read_bytes())
write('bounded-disposition.json',dict(status='ONE_WHOLE_COMMON_SHOE_REJECTED_FOR_CURRENT_REAR_SHARED_LAYER_COUPON_ONLY',geometry_family_count=1,no_second_height_or_axis_or_print_family=True,whole_architecture_change_implemented=False,source_closed=dict(MAIN_supplier_STEP_frame_and_two_holes=True,AUX_onlyPCB_scope_corrected_to_full9p5=True,all5_M2_fullsteel_modelled=True,continuous_actual_hexnutfeed5_clear=all(x['clear'] for x in nut['rows']),prior_rectcover_common2p669667_is_NOT_physical_nut_contact=True),finite_gate=dict(bounds=gate['bounds'],exact=len(gate['checks']),raw_gate='finite-layer-and-joint-gate.json',material_interfaces=[x for x in gate['failures'] if 'a' in x],missing_named_current_print_bounds=missing['bounds'],missing_named_current_print_checks=len(missing['checks']),missing_current_print_interfaces=missing['failures'],current_owner_proof='current-owner-missing-link.json',source_scope_correction='scope-correction-and-actual-roots.json'),grouped_causes=['Current printed network P11/P13 and existing frame steel: P20/P11 actualcommon3.544973; AUXfullM2/P11actual25.767657; MAINfullM2/P13actual2.499696 andwasher1.271198. AUXpopulation812.8 andMAINfamily15 are conservative cover overlaps, not deliveredcomponentcontact. FullM2tips gap0.87..0.8748 tocurrentprints alsoheld.', 'S0panel boundary: P20gap0.02 andfullM2gap0.89, sourcecaseunchanged','E2 retained connector allocation gap1.0 below1.25, not deliveredwirecontact'],one_whole_consequence='A common support must coallocate actual P11/P13 load network, existing frame heads, S0 panel and E2 interfaces BEFORE a new shoe. Do not keep old printed layer shapes immutable, but preserve their support/cooling/access functions in one explicit replacement. No individual height/bolt nudge or second family performed.',exports=dict(coupon_only='COUPON_M2_fullnut_and_post.stl',coupon_size=[12,10.5,11],closed_positive_Z0=True,full_P20_STL=False,P11_P12_changed_STL=False,current_print_index_remains='day15-carrier-capture-first-fit/current-print-index.json'),initial_order=dict(bench_M2_nutfeed=True,full_frame_M3_nutwasher_frombelow_before_banks=True,driver_before_both_boards_and_monitor=True,MAIN_trimmer_access_beforelatecover=True,no_soldered_E1_unplug=True,physical_factory_end_reach_FIT2=True,operating_permanent_conflicts_NOT_fixed_by_assembly_order=True),physical_FIT3=['actual PCBrevision mountingaxes/2.18holes','safe underside annulus/headwasher/componentcontact','actual M2 stock nut dimensions/feed/fit'],actual_fit_cut_slack=None,physical_pass=False,whole_kit_ready=False,all57_plus_extras_factoryends_protection_preserved=True))
with (P/'hardware-demand.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['role','qty','description','status']);w.writerows([['board screw',5,'M2x12 socket head D3.8 h2 underhead length12','NEEDED_UNCONFIRMED / WHOLESHOE_HOLD'],['board upperwasher',5,'M2 OD5 ID2.2 t0.3','NEEDED_UNCONFIRMED / safeannulusFIT3'],['board fullnut',5,'M2 AF4 height1.6','NEEDED_UNCONFIRMED / coupon'],['frame screw',2,'ISO10642 M3x14 INCLUDES full head D6.72 h1.86','NEEDED_UNCONFIRMED / WHOLESHOE_HOLD'],['frame lowerwasher',2,'M3 OD7 ID3.2 t0.5','NEEDED_UNCONFIRMED'],['frame fullnut',2,'M3 AF5.5 h2.4','NEEDED_UNCONFIRMED'],['PETG coupon',1,'12x10.5x11mm; not an installed shoe','CONDITIONAL_BENCH_TRIAL_ONLY']])
(P/'START_HERE.md').write_text('''# MAIN + AUX: wynik wspólnej stopy i próbka M2

**HOLD — nie drukować pełnej stopy ani nowych P11/P12.** Bieżącym warunkowym zestawem carriera nadal jest `../day15-carrier-capture-first-fit/START_HERE.md`, commit4f9ce00a. Tamte29plików pozostają niezmienione.

W tej porcji wybrano jeden wspólny układ. AUX nie jest już traktowany jako sama płytka: PCB1,57, elementy1,8pod/6,1nad i pełne pole9,5mm. MAIN ma prawdziwy obsadzony model rodziny reg32c, z rezerwą opcjonalnego drugiego potencjometru; zakończeń przewodów w STEP nie ma. Płytki ustawiono wspólnie naZ103,52, bez przesuwania innych modułów. Otwory producenta2+3 są przeznaczone dlaM2/#2, nieM2,5.

Stopa kandydująca ma5mm podstawy i6mm słupki. Pod AUX do stopy zostaje4,2mm; pełne śrubyM2x12/podkładki/nakrętki są pokazane. Dwa pełne zestawyM3x14 łączą ją z rzeczywistymi półkamiP12/P11. Długość śruby stożkowej zawiera łeb, długość socketheadM2 jest pod łbem. To zapotrzebowanie NIEPOTWIERDZONE, nie informacja o posiadanych śrubach.

## Dlaczego nie ma pełnego STL

Skończony test zebrał razem zależności: stopa ma tylko1,0mm do polaE2, styka się z istniejącą pełną śrubą ramy i ma0,02mm do paneluS0. Pełny M2 przy trzecim otworzeAUX ma0,89mm do tego panelu. Wymagane1,25mm nie zostało zniesione. Jawne sprawdzenie brakujących bieżących druków jest w `only-missing-current-print-layer-gate.json`: P20/P11 actualcommon3,544973mm³; pełny M2AUX/P11 actual25,767657; pełny M2MAIN/P13 actual2,499696 i washer/P13 actual1,271198. To rzeczywiste druki/stal tej propozycji, bez nameOwn. Nakładanie coverów populacjiAUX812,8 i rodzinyMAIN15mm³ jest natomiast konfliktem rezerwy, nie dowodem kontaktu dostarczonych IC. Pełne końceM2 mają też0,87..0,875mm do istniejących druków. Bieżący P11 nie był operandem starej referencyjnej grupy; brak uzupełniono jawnie, nie przypisano staregoPASS. To problem całej wspólnej warstwy P11/P13/S0/E2, nie powód do pojedynczego przesunięcia łba lub płytki. Nie zbudowano drugiej rodziny.

Pierwszy prostokątny cover drogi nakrętki obejmował też powietrze wokół sześciokąta. Rzeczywisty ciągły swepthex tych samych pełnych nakrętek przechodzi we wszystkich5kanałach, valid/common0. Surowy wynik2,669668mm³ zachowano jako nieadekwatny cover, nie kontakt fizycznej nakrętki. Nie zmieniono geometrii kanału, nut ani pozy.

## Co można przymierzyć

Jedyny wydany STL to `COUPON_M2_fullnut_and_post.stl`: 1szt PETG,12×10,5×11mm, zamknięty/dodatniaobjętość/Z0. Jest rzeczywistym wycinkiem stopy: podłoga2mm, pełne gniazdoM2/antyobrót, dach1,4mm i słupek6mm. Druk podstawą do stołu; sprawdzić jakość dachu kanału, nie zaciskać PCB na niewidocznych elementach. Próbka nie jest częścią do montażu w kocie. Nie wykonywano slicingu ani druku.

Dwie osoby: pierwsza sprawdza całą nakrętkę i śrubę na próbce; druga porównuje rzeczywiste otwory PCB, podkładkę i bezpieczne pole wokół otworu. Najpierw obejrzeć obie strony płytki. Podparcie nie może naciskać IC/lutów ani zasłaniać portu. Producent podaje tolerancję otworów±0,1 i krawędzi±0,3; rewizja dostarczonej płytki pozostajeFIT3. Nominalne pełne zaangażowanie nakrętki nie jest odbiorem tolerancji/wytrzymałości.

## Plan kolejności, jeszcze nie odbiór całego montażu

NakrętkiM2 wsunąć w otwartą stopę na stole, potem pełneM3/nut+washer od dołu przed bankami i płytkami. Płytki preterminować pozaPETG, montować na otworach producenta. Narzędzie dwóch otworówAUX i tylnej śruby ramy zajmuje miejsce monitora: monitor dopiero po dokręceniu, a przy późniejszej naprawie może wymagać demontażu. To nie usuwa stałych kolizji panelu/łba. E1 pozostaje lutowane; bez fikcyjnego odpinania. Rzeczywiste zakończenia i długości MAIN/AUX po zmianieZ wymagająFIT2, bez cięcia i kredytu za starą trasę.

`powerboard-shoe.FCStd` jest zapisanym modelem NIEZATWIERDZONEGO wariantu z pełnym kontekstem, nie następną opcją montażu. `whole-module-layer.png`, `actual-layer-and-blocker-sections.png` oraz `module-layer-dimensions.png` pokazują tę samą konfigurację. Pliki źródłowe/URL i SHA są w `source-pins.json`. Carrier/paski/Pi/audio/pozostałe części zachowane; stare pozytywy nie są ponownie liczone.

Następna decyzja: wspólna dostępna tylna granica P11–łeb ramy–panelS0–E2, zanim powstanie kolejna stopa. Pozostałe mocowania modułów i nośny korzeń głowy nadalOPEN. Cały kot nie jest gotowy; actualfit/cut/slackNULL, physicalPASSfalse, wholekitfalse.
''',encoding='utf-8')
print(json.dumps(dict(result='package source sections and coupon only',files=len(list(P.iterdir())))))
