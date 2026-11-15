from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).parent;ROOT=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r=json.loads((P/'coupon-and-whole-unit-result.json').read_bytes());lines=json.loads((P/'actual-unit-panel-section.json').read_bytes())
fig,axs=plt.subplots(1,2,figsize=(12.5,6.5),layout='constrained')
ax=axs[0];colors=['#148b9e','#696b75','#ac3923','#c19c08','#c34949']
for c,row in zip(colors,lines):
 first=True
 for line in row['curves']:
  if len(line)<2:continue
  ax.plot([p[0] for p in line],[p[1] for p in line],color=c,lw=1.5,label=row['name'] if first else None);first=False
ax.axhline(104,ls='--',c='#af358b',lw=1);ax.axhline(102,ls='--',c='#af358b',lw=1);ax.text(8,105,'nominal flange top104 / underside102',fontsize=8,color='#af358b');ax.text(-17,67,'Full TE IN/OUT source allocations;\nmating depth e UNKNOWN',fontsize=8);ax.set_aspect('equal');ax.set_xlim(-19,19);ax.set_ylim(48,126);ax.grid(alpha=.2);ax.set_xlabel('Bench Y [mm]');ax.set_ylabel('Bench Z [mm]');ax.set_title('Actual source section X225; housing is coarse BOX');ax.legend(fontsize=5,loc='upper left')
from matplotlib.patches import Rectangle
ax=axs[1];ax.add_patch(Rectangle((-22,-15),44,30,fill=False,ec='#148b9e',lw=2));ax.add_patch(Rectangle((-11.1,-5.65),22.2,11.3,fill=False,ec='#222',lw=2));ax.add_patch(Rectangle((-14,-7.5),28,15,fill=False,ec='#af358b',ls='--',lw=1.5));ax.annotate('',xy=(11.1,-10),xytext=(-11.1,-10),arrowprops={'arrowstyle':'<->'});ax.text(0,-12.5,'a22.2',ha='center');ax.text(0,0,'b11.3 +0.3/-0\nnominal window',ha='center',va='center');ax.text(0,12,'44x30x2 coupon; NOT installed root',ha='center',fontsize=9);ax.text(0,-19,'Flange28x15: nominal lands2.9 /1.85 each.\nActual latch, bearing and print tolerances NOT tested.',ha='center',fontsize=9);ax.set_xlim(-25,25);ax.set_ylim(-23,18);ax.set_aspect('equal');ax.set_xlabel('Coupon long direction [mm]');ax.set_ylabel('Coupon short direction [mm]');ax.set_title('ONE source panel2 reference opening, not a fit grid');ax.grid(alpha=.15)
fig.suptitle('MTA0300330: free bench interface coupon / physical fit remains OPEN',fontsize=14);fig.savefig(P/'actual-unit-and-panel-section.png',dpi=150);plt.close(fig)
(P/'panel-template-1to1.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="75mm" height="65mm" viewBox="0 0 75 65">
<rect width="75" height="65" fill="white"/><g fill="none" stroke="black" stroke-width="0.15"><rect x="15" y="10" width="44" height="30"/><rect x="25.9" y="19.35" width="22.2" height="11.3"/><rect x="23" y="17.5" width="28" height="15" stroke="#a2398a" stroke-dasharray="1,0.8"/><path d="M12.5 50h50m-50 -1.5v3m50 -3v3"/></g>
<g font-family="sans-serif" font-size="2.4" text-anchor="middle"><text x="37.5" y="6">MTA0300330 | d2 | reference coupon44x30</text><text x="37" y="24">22.2 x11.3 (+0.3/-0 b)</text><text x="37.5" y="46">50mm CONTROL: measure after print</text><text x="37.5" y="57">Print100%, NO fit-to-page. Not delivered-fit proof.</text><text x="37.5" y="61">Magenta: nominal28x15 flange, not cut line.</text></g></svg>''',encoding='utf-8')
refs=[ROOT/'hardware/reference/servo-holder-p0-2026-09-24'/x for x in ['0300330.pdf','README.md','ENVELOPE.md','TE-520448-Conrad.pdf','TE-520184-Farnell.pdf']]+[ROOT/'hardware/electronics/power-platform/servo-terminations-p0.json',P.parent/'day14-fasttrack-first-fit/day14-firstfit-build.py',P.parent/'day15-carrier-capture-first-fit/manifest.json',P.parent/'day15-carrier-capture-first-fit/carrier-capture.FCStd',P.parent/'day15-powerboard-common-shoe/manifest.json']
write('source-pins.json',dict(utc=datetime.now(timezone.utc).isoformat(),files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in refs],primary_MTA_reference_only=True,one_sample_source_legacy='F_L1 in firstfit constructor; current display Motor_ATO4A__1_0; not physical inventory/serial identification',two_existing_rows_of6_unchanged=True,current_conditional_carrier='4f9ce00a634651811c109ed245f917846b59c957',powerboard_shoe='ce9a55c1583f65803faecc63d804d948a94eb2f8 DEFERRED/HOLD, not installed'))
wire=json.loads((ROOT/'hardware/electronics/power-platform/servo-terminations-p0.json').read_bytes())
write('one-unit-end-dependencies.json',dict(scope='Design one-unit example F_FL1, not measured physicalunit. No new wire/electrical graph selection.',source='hardware/electronics/power-platform/servo-terminations-p0.json',ends=wire['ends'][:2],input=dict(sku='LAPP0107001',awg12=True,source_nominal_OD=3.1,source_fixed_Rmin=12.4,maximum100mm_not_factory_length_or_cut=True,actual_length=None),output=dict(servo_factory_positive_wire_preserved=True,source_project0p326_NOTmeasured=True,actual_length=None),initial_lay='Whole alreadycrimped TE wire ends held free on underside bench, mate after housing clipped. Preserve opposite factoryends/servo plug. No actual cutting/extension/recrimp, no solderedMODULE unplug. If a delivered fullyprewired unit prevents this, measure actualconstraint and STOP; do not force rigid complete unit through referencewindow.',all_four_independent_MTA0100335_220_and_bothends_unchanged=True,freeleads_are_flexible_not_rigid_obstacles=True,installed_reach_R_slack_not_qualified=True,physical_pass=False,actual_fit_cut_slack=None))
write('bounded-disposition.json',dict(status='ONE_FREE_BENCH_PANEL_COUPON_CONDITIONAL_PHYSICAL_FIT',source_gap_closed='Current CAD body is six-face28x15x28.5 allocation, not an actual flange/clip model. Flange top is reference drawing binding, not full71.43assemblybottom or proven manufactured datum.',source_order='Housing with supplied internal contacts first; external complete femaleTE ends initially mated from below afterwards; ATOlast. Actual mate depth e, mutualinsulators and clip action physicalFIT. No virtual depinning/disconnect/cut.',one_coupon=r['coupon'],full_unit_preserved=True,full_rigid_unit_projection=r['whole_rigid_TE_projection'],source_box_panel_common338p28_not_physical_contact=True,primary_nominal_bearing=r['nominal_bearing'],actual_bank_mount_root_qualified=False,additional_hardware=0,not_new12bank_or_WAGO_holders=True,carrier4f9unchanged=True,powerboard_commonshoe_deferred=True,unknowns=['Delivered MTArevision/panelwindow/springclips/actualflangeplane','Full insertion of two different TE insulators and depth e, no force; source full box is not a seating datum','Crimped wire/sewnstock/realend reach and applicable radius remain existing physicalFIT; no source audit/purchase or cut'],physical_pass=False,whole_kit_ready=False,actual_fit_cut_slack=None,next='Parent consolidation only after receipt; no next CAD family tonight.'))
with (P/'parts.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['item','qty','role','status']);w.writerows([['MTA0300330_PANEL2_REFERENCE_COUPON.stl',1,'PETG44x30x2 reference panel with22.2x11.3 opening','FREE_BENCH_TRIAL_NOT_INSTALLED'],['MTA0300330',1,'Existing selected holder with2internalcontacts','TEST_ONE_EXISTING_UNIT_NO_PURCHASE'],['TE4-520448-2',1,'Complete selected femaleIN and its attachedlead','SAME_SELECTED_END_NO_CUT'],['TE2-520184-2',1,'Complete selected femaleOUT and its attachedlead','SAME_SELECTED_END_NO_CUT'],['ATO4A',1,'Complete current fuse','SAME_SELECTED_UNIT'],['additionalfasteners',0,'Couponheldfreeonbench','NO_NEW_HARDWARE']])
(P/'START_HERE.md').write_text('''# Jedna próbka panelu MTA0300330

**Tylko beznapięciowa przymiarka na stole.** Nie jest to mocowanie banku do ramy ani odbiór całego kota. Bieżący carrier pozostaje4f9ce00a; stopaMAIN/AUXce9a55c1 jest odłożonymHOLD i nie została włączona do tego modelu.

## Co wydano

1×`MTA0300330_PANEL2_REFERENCE_COUPON.stl`, PETG,44×30×2mm, płasko/Z0, zamknięty i dodatni. Otwór **22,2×11,3mm** jest nominalny dla panelu2mm z rysunkuMTA B0-100.E10A; b ma tolerancję+0,3/−0. Nie dodano ukrytego luzu drukowego. Zmierzyć rzeczywisty otwór i grubość próbki, nie wciskać na siłę. Brak nowych śrub/adapteraDIN/zakupów. Nie wykonywano druku ani slicingu.

`panel-template-1to1.svg` drukować100%, bez dopasowania do strony; najpierw sprawdzić odcinek50mm. Kontur44×30 to próbka,22,2×11,3 to otwór, przerywany28×15 to nominalny kołnierz, nie linia cięcia. Tylko jeden rozmiar, nie siatka wariantów.

## Co rzeczywiście wiemy o oprawce

W obecnym CAD plastikMTA jest pudełkiem28×15×28,5mm o6ścianach. **Nie zawiera rzeczywistego kołnierza ani sprężystych zaczepów.** Zespół obejmuje też osobno pełne polaTEIN/TEOUT iATO; jego71,43mm nie jest wysokością plastikowego korpusu. Nie wolno przyjmować BBox całego zespołu jako płaszczyzny panelu. Rysunek producenta jestONLY FOR REFERENCE, nie certyfikatem pasowania dostarczonej części.

Powiązanie nominalne:28,5mm od góry kołnierza do spodu plastiku; kołnierz2mm, panel2mm — spod panelu plastik schodzi24,5mm. W bieżącym źródle jest to odpowiednioZ104,63/102,63/100,63; są to datums referencyjne przyłożone do pudełka, NIE wykryte w CAD powierzchnie zatrzasków. Na osobnej prezentacji stołowej panelZ100..102, kołnierzpodstawa102/góra104. Transformacja i4pełne źródłowe części zapisane wJSON.

Nominalny kołnierz28×15 daje przy otworze22,2×11,3 szerokości oparcia2,9 i1,85mm oraz planarea169,14mm². Rzeczywiste stykanie, zatrzask, tolerancje i siła zacisku pozostają do sprawdzenia. Wspólny materiał pudełka i próbki338,28mm³ to nadmiar uproszczonego coveru, **nie dowód kolizji prawdziwego plastiku**. Nie wycięto oprawki ani nie udawano dokładnych zaczepów.

## Kolejność dwóch osób — jeden rzeczywisty wariant

1. Pracować na odłączonym komplecie, bez źródła zasilania. Pierwsza osoba trzyma próbkę za zewnętrzny brzeg, pozostawiając cały spód i oba końce zaczepów dostępne. Druga ma MTA0300330 z jego dwoma fabrycznymi stykami wewnętrznymi. Niczego z oprawki nie wypinać.
2. **Początkowo osadzić samą oprawkę w panelu od strony kołnierza.** Sprawdzić przyleganie całego kołnierza i oba sprężyste zaczepy od spodu. Bez wymuszania/ściskania izolatorów. Na wolnym kuponie nie ma ramy/banku zasłaniającego oględziny i dojście do zaczepów; ich dokładna geometria/releaseforce jest fizycznymFIT, nie zamodelowanymPASS.
3. Dopiero po osadzeniu oprawki nasunąć od spodu **obie kompletne żeńskie końcówkiTE**, każdą z zachowanym przewodem i przeciwległym końcem. Nie chodzi o wpychanie żeńskichTE do wnętrzaPA66 ani wyjmowanie stykówMTA. Źródła identyfikująMTA0300330 ze stykami oraz osobneTE6,35×0,81female; to początkowe zestawienie rzeczywistych części, nie fikcyjne odłączenie gotowej wiązki. Głębokośćnasunięciae i wzajemne dopasowanie izolatorów trzeba zmierzyć na1komplecie. Jeżeli rzeczywisty dostarczony komplet jest już trwale okablowany i ta kolejność jest niemożliwa, **STOP: zapisać konkretny wymiar/ograniczenie**; nie przeciągać go na siłę i nie rozcinać przewodów.
4. Przewody ułożyć swobodnie pod próbką; drugi człowiek podtrzymuje cały połączony kit. INLAPP0107001 ma projektowyOD3,1/R12,4 i max100mm, a nie potwierdzony factoryblank. OUT ma rzeczywisty przewód serwa z zachowanym końcem; jego przekrój/długość wymagają właściwegoFIT. Niczego nie ciąć/przedłużać ani nie zmieniać procesu zacisku. Cztery chronione niezależne220 i wszystkie końce pozostają bez zmian.
5. WkładkęATO4A wkładać na końcu od góry, obejrzeć osadzenie i dostęp. To nadal przymiarka mechaniczna bez zasilania, bez odbioru styków/ochrony/siły wyrywania.

Nie deklarujemy, że cały sztywny zespół71,43mm przechodzi otworem. Projekcja dwóch zmontowanychTE ma21,8486mm w krótkim kierunku przy otworze11,3mm — prosty wspólny dropin nie jest przyjęty. Poszczególne nominalne polaTE są mniejsze od otworu, ale to nie dowód dowolnej ścieżki/manualnej próby; wybrana kolejność w ogóle nie wymaga przeciskania razem nasuniętychTE.

## Pliki i granice wyniku

`mta-panel-trial.FCStd`: currentcarrier/sourcepełne12oprawek w2rzędach po6 bez zmian, plus jedna jawna kopia tej samej oprawki przy próbce NA STOLE, nie13. pozycjaBOM. AUXpełne9,5 zaznaczone jakoOPENcontext, nie potwierdzenie starej płytki. `whole-current-context-and-bench.png` i `actual-whole-unit-interface.png` są rzeczywistymi widokami CAD. Magenta to nominalne płaszczyzny kołnierza, przezroczysty korpus to sourceallocation, nie dokładny zakupiony plastik. `actual-unit-and-panel-section.png`/JSON pokazują rzeczywiste zachowane bryły i jedno źródłowe okno.

Źródła/sha w `source-pins.json`, części/ilości w `parts.csv`. Rootbanku i retencja wszystkich12 oprawek nie są w tym zadaniu kwalifikowane. PhysicalPASSfalse, wholekitfalse, actualfit/cut/slackNULL. Dalej tylko odbiór i konsolidacja plików przez parenta — bez kolejnej rodzinyCAD tej nocy.
''',encoding='utf-8')
print(json.dumps(dict(status='ONE_SOURCE_MTA_COUPON_PACKAGE_READY_FOR_SAVE_RECEIPT',coupon=r['coupon'])))
