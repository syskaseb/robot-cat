from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).parent;ROOT=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan=json.loads((P/'whole-rear-layer-plan.json').read_bytes());gate=json.loads((P/'whole-module-space-and-hardware-falsifier.json').read_bytes());ass=json.loads((P/'assembly-order-disposition.json').read_bytes());rows=json.loads((P/'actual-whole-layer-sections.json').read_bytes())
fig,axs=plt.subplots(2,2,figsize=(12,9),layout='constrained');cols={'P11_rear_gate':'#b44665','P13_BUS_bridge':'#554488','PROPOSED_OPEN_MOUNT_PLANE_NOT_PRINT_PART':'#278f9b','MAIN_Pololu4853':'#318132','AUX_FULL9p5_POPULATED_SCOPE':'#bd8b28','Monitor_MOD05015':'#555555','S1_NKK_S821_installed':'#c43b26'}
for ax,z in zip(axs.flat,[107,113,119,125.5]):
 for row in rows:
  if row['z']!=z:continue
  first=True
  for line in row['curves']:
   if not line:continue
   ax.plot([v[0] for v in line],[v[1] for v in line],color=cols[row['part']],lw=1.2,label=row['part'] if first else None);first=False
 ax.set_aspect('equal');ax.set_xlim(50,135);ax.set_ylim(15,82);ax.set_title('Actual source XY / Z'+str(z));ax.set_xlabel('X [mm]');ax.set_ylabel('Y [mm]');ax.grid(alpha=.2);ax.legend(fontsize=5,loc='upper left')
fig.suptitle('ONE whole rear layer: space scoped clear / initial axial tool order HOLD',fontsize=14);fig.savefig(P/'actual-whole-layer-sections.png',dpi=135);plt.close(fig)
ref=[P.parent/'day15-carrier-capture-first-fit/manifest.json',P.parent/'day15-mta-panel-fit/manifest.json',P.parent/'day15-powerboard-common-shoe/manifest.json',ROOT/'hardware/reference/main-p0-2026-09-24/reg32c.step',ROOT/'hardware/reference/aux4092-2026-09-26/reg24d-drill.dxf',P.parent/'day15-powerboard-common-shoe/MAIN-primary.pdf',P.parent/'day15-powerboard-common-shoe/AUX-primary.pdf',P.parent/'day15-essential-shared-frame/C0-frame-builder.py']
write('source-pins.json',dict(utc=datetime.now(timezone.utc).isoformat(),files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in ref],currentcarrier4f9_unchanged=True,foundation6c6a_unchanged=True,MTAbea67_unchanged=True,ce9not_reselected=True,no_print_exports_or_coupons=True))
with (P/'standard-hardware-proposal.csv').open('w',newline='',encoding='utf-8') as f:
 w=csv.writer(f);w.writerow(['qty','item','role','status']);w.writerows([[5,'M2x12 fullsocketD3.8h2','PCBthroughjoint','NEEDED_UNCONFIRMED'],[10,'M2washerOD5x0.3','AbovePCB+belowopenplane','NEEDED_UNCONFIRMED'],[5,'M2fullnutAF4h1.6','Accessiblebelowplane','NEEDED_UNCONFIRMED'],[5,'M2spacerOD4bore2.2L4','OrdinaryPCBspacer','NEEDED_UNCONFIRMED'],[2,'ISO10642M3x16 inclheadD6.72h1.86','Rootfullhead/tip/shaft','NEEDED_UNCONFIRMED'],[2,'M3washerOD7x0.5','UnderP11beam','NEEDED_UNCONFIRMED'],[2,'M3fullnutAF5.5h2.4','UnderP11beam','NEEDED_UNCONFIRMED'],[2,'M3spacerOD6bore3.2L5','ActualP11top107to112plane','NEEDED_UNCONFIRMED']])
write('bounded-disposition.json',dict(status='STRUCTURAL_SPACE_PROPOSAL_WITH_INITIAL_ASSEMBLY_HOLD',one_whole_geometry_family=True,not_ce9_local_shoe_or_height_retry=True,plane='P11 upper transversebeam107->5mm ordinaryframe spacers->openplane112..115->4mm PCBspacers->PCB119',root=plan['root_actual'],root_antirotation_axes=[[103,35],[103,49]],MAIN='Whole sourcePCB frame rotated180vsce9 clock; sameXY footprint, sourcefamily retained, allterminals toward+X',AUX='Whole full9.5 module Y+25/Z+25 vs old current; northsourcebay47..72.4, ports67..75, not monitorunderlap',available_intervals=dict(PCB_Z=plan['allowed_PCB_Z'],AUX_Ymin=plan['AUX_north_Ymin_interval']),foreign_space=dict(bounds=gate['bounds'],exact=len(gate['checks']),failures=gate['failures']),assembly_HOLD=ass,source_P11_P13_carrier_and_clamps_unchanged=True,print_interfaces_contract_only=['2 futureP11printedbores3.4','ordinary rootheadbearing seats in futureopenplane','5openM2throughclearances; no captivenuts'],whole_feasible=False,print_release=False,new_STLs=0,new_coupons=0,physical_pass=False,whole_kit_ready=False,actual_fit_cut_slack=None,next='Parent consolidation only. Future whole decision is actual side-tool access OR real load-preserving P11 uppercrossmember parting; cannot virtualremove integralbeam or declare chosen longaxialfield an immutabletool/alltoolsimpossibility. No furthergeometrythischunk.'))
(P/'START_HERE.md').write_text('''# Cała tylna warstwa — propozycja przestrzeni, nie zestaw do druku

**Wynik: SPACE scoped clear, INITIAL ASSEMBLY HOLD.** Jedna nowa topologia wspólnego podparcia z górnej belkiP11, nie poprawka dolnej stopyce9. Nie wydano STL, kuponu, kieszeni ani nowego indeksu produkcji. Bieżące pliki do warunkowej przymiarki carriera4f9, foundation6c6a i próbkaMTAbea67 pozostają bez zmian.

## Jedna konfiguracja oparta na całym sąsiedztwie

P11 ma rzeczywisty transversebeamX95..107/Z103..107. Oba odczytane koła podparciaR3,5 na osiach(103,35)/(103,49) obejmują po153,938mm³ rzeczywistego materiału, missing0. Tylną oś wybrano z warunku północnych pełnychFHAC startY56: rootwasherR3,5+1,25 dajeY≤51,25. Wstępny odczyt materiału przy74,5 nie był przyjętą kotwą — leżałby pod pełnymFHACYaw. Nie wykonano drugiego wariantu geometrii.

Loadpath: rzeczywistyP11/rootjaws/sourceclamps → dwa zwykłe dystanseM3 długości5 → wspólna OTWARTA płaszczyznaZ112..115 → pięć zwykłych dystansówM2 długości4 → płytki naZ119. Dwie osie i oparcie utrzymują pozycję/antyobrót; nośność wymaga próby prototypu. Obecne P11/P13 pozostają całe: ich belki, podparcie górnych szyn i BUS/31mmcooling nie zostały wycięte. Dwa przyszłe otwory w DRUKOWANYM P11 i gniazda standardowych łbów są tylko kontraktem przyszłego połączenia, nie wierceniem kupnej ramy ani kwalifikacją obecnegoSTL.

Wyprowadzony wspólny przedział PCBZ118,3752..123,1752: dolna granica z pełnegoM2x12tip nad aktualnymi belkami maxZ107+1,25; górna z P14lower134 minus1,25 i pełnego pola końcówPCB1,5748+8. WybranoZ119, nie serię prób wysokości. AUX odsuwa się jako CAŁY moduł od monitora: z jegoYmax45 wynikaYmin≥46,25; z rzeczywistychP11outeruprightsY80 wynikaYmin≤53,35. WybranoYmin47/Ymax72,4. Nie przesunięto monitora/S1/Pi/BUS/S0.

MAIN zachowuje footprint61..91,48/Y22..44,86, ale cały układ sourceSTEP jest odwrócony o180° względemce9: otwory po prawejX89,321, porty ku+X. AUX zachowuje swoją orientację, otrzymujeY+25/Z+25 względem staregoPCBdatum; wszystkie3mounts i12portpositions idą z CAŁĄ płytką. Pełne AUX9,5 z1,8pod zachowane; PCB1,6starej reprezentacji poprawione tylko do źródłowego1,57, nie cięcie realnej płytki. MAIN zachowuje całą rodzinęSTEP/opcjonalnytrimmer i niezmniejszonycover. Rzeczywiste przewody/krótkie końce/izolacja i reach po tych zmianach sąFIT2, bez kredytu długości, fikcyjnego cięcia lub extension.

## Co sprawdzono, a czego nie

Skończony aktualny test całych modułów/pól zakończeń/pełnych śrub/nakrętek/podkładek/dystansów i obecnego sąsiedztwa:8902numericculls/31exact, brak foreignfailures. Nie odtwarzano dawnych33/1815 ani world126/wirematrices. Rzeczywiste sourceP11/P13 i carrier/straps/Pi/audio/sourceclamps zachowano. Sześć strukturalnych regionów nowej otwartej płaszczyzny ma0missing. To **nie jest** dowód gotowej części: proste przelotowe otworyM2, standardowe rootseats i podział do druku nie były detalowane ani odebrane. Kolorowa płaszczyzna jest wolumenem strukturalnej propozycji, nie fikcyjną gotową fuzją zP11 lub gotową drukowalną stopą.

Kompletne standardowe zestawy są wCSV/native:5M2x12, po2podkładki, pełne nakrętki i dystanse4;2M3x16ISO10642 (długośćZEłbem), dolnepodkładki/pełnenakrętki i dystanse5. Jest to zapotrzebowanie NIEPOTWIERDZONE, bez zakupu. SafePCBannulus/luty/rewizja otworów to istniejący fizyczny kupon/FIT3, nie docisk niewidocznychIC. Własnyprint-fit/rootseat pozostaje projektem przyszłej realizacji, nie Ownwaiver.

## Rzeczywisty problem kolejności — nie usuwać go etapowaniem

Plan zakładał: dwie osoby montują pustą płaszczyznę z dolnymi nakrętkami przed bankami; potem preterminowane płytki/przelotoweM2; monitor/P14/latepanels na końcu. Odczyt narzędzi pokazał, że wybrane pionowe pola25mm dlaM2 i35mm dla rootHEX przecinają **integralną górną belkęP11**. M2/P11allocatedtoolcommon30,410617 i83,629196; obie rootverticalfields po309,448782mm³. Nie można po prostu „założyć P11 później”, bo jego belka i dolna kotwa są jedną rzeczywistą częścią. P14 może być osobnym latepanelem; P11 nie jest wirtualnie rozpinane. Dolne pola spanner mają0,5mm do własnej powierzchniP11 — również nie przyznano uniwersalnegoPASSnarzędzia.

To **HOLD wybranego pionowego dostępu/order**, a nie kolizja dostarczonego narzędzia ani dowód, że wszystkie klucze/ścieżki są niemożliwe. Długości25/35 to nasza rezerwa, nie immutablemanufacturerpart. Następna całościowa decyzja musi wskazać rzeczywisty boczny dostęp narzędzia ALBO rzeczywisty nowy podział górnej belkiP11 z zachowaniem jej podparcia/retencji. Nie wykonano drugiej wysokości/orientacji/śruby ani lokalnego trimu. Dopóki ten kontrakt montażu nie jest zamknięty, nie ma wholefeasible/druków.

`whole-rear-layer.FCStd` jest JEDNĄ niezatwierdzoną propozycją; PNGwhole/local i przekroje pokazują tę samą geometrię. Obudowa/Ola/ogon/nogi bez zmian i bez nowej rundy wizualnej. Factoryparts57+extras/four220/bothMTA/solderedE1/protection zachowane. PhysicalPASSfalse, wholekitfalse, actualfit/cut/slackNULL. Dalej tylko odbiór i konsolidacja parenta, bez kolejnej rodzinyCAD tej nocy.
''',encoding='utf-8')
print(json.dumps(dict(status='WHOLE_SPACE_PROPOSAL_ASSEMBLY_HOLD_PACKAGE_READY',foreign_checks=len(gate['checks']),raw_toolblocks=len(ass['integral_P11_rows']))))
