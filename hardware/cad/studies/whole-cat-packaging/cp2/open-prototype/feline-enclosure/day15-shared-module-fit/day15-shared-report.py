from pathlib import Path
import json,csv,io,hashlib,shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-shared-module-fit');B=P.parent/'day14-fasttrack-first-fit';plan=json.loads((P/'proposal.json').read_bytes());base=json.loads((B/'layout.json').read_bytes());gate=json.loads((P/'whole-material-gate.json').read_bytes());root=json.loads((P/'first-gate.json').read_bytes())
for n in ['day15-shared-build.py','day15-shared-first-gates.py','day15-shared-material-premise.py','day15-shared-report.py']:shutil.copyfile(Path('C:/Users/Sysq/AppData/Local/Temp')/n,P/n)
shutil.copyfile(B/'fit-kit-ready/WAGO-role-map.csv',P/'WAGO-role-map-unchanged.csv')
selection=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/electronics/kicad-current/selected-components.csv');shutil.copyfile(selection,P/'selected-components-unchanged.csv')
def csvout(n,header,rows):
 s=io.StringIO(newline='');w=csv.writer(s,lineterminator='\n');w.writerow(header);w.writerows(rows);(P/n).write_bytes(s.getvalue().encode())
csvout('support-and-parting-plan.csv',['function','coarseoccupieddimensions','loadroot','retention','status'],[
 ['front portal','X-104..-98 Y-86..86 Z48.52..95.52','2 front2-sidedprinteddeckedgeclamps','M3x12 complete nut+washer; upperfeet integralportal','rootcontact scopedchecked; productionpartingOPEN'],
 ['rear portal','X95..107 Y-86..86 Z48.52..107','2 rear sourceconformingstepjaws onactualP03','M3x16 complete nut+washer; aboveFHAC101at103','rootcontact scopedchecked; no payloadPASS'],
 ['shared inner rails','X-98..95 Y-20..-14 and16..20 Z88..96','front+rearportal','flatparting/4M3interfaces proposed; length/thread OPEN','coarsevalid1solid union, not printableassemblyrelease'],
 ['Pi/commonLwing','trayX-101..-10/Y-41..21 Z92.52..95.52 +uprightwingY18.5..42','commoninnerrails','four actualCADr1.375axes +3mmstandoffs; pressure/bolts toqualify','PCBseat isnotwholeport/retentionPASS'],
 ['MAIN/AUX','ledgeX55..126/Y18.5..50/Z88.52..92.52','positiveinnerrail','1.48mmnominalinsulation gap +futureactualedge/holes','wholemountunreceived'],
 ['BUS removable bridge','X12..66 Y-23..23 Z104..107; BUSX18..60/Y+-16.5/Z110..134','twolegs toinnerrails','4M3jointsites+3mmstandoffs proposed; actualports OPEN','Pi coolinggap31 scopedclear; batteryremoval orderunproven'],
 ['battery','current106.5x35x21.5 /Z65..86.5','currenttray/2crossarms retained; tieintocommonroot must qualify','2selectedstraps4982 fullstockactualfitUNKNOWN','do not creditgravityfoot as closedretention'],
 ['banks/WAGO/S0S1','full12MTA+5FHAC+F0+all16mixedWAGO/4WAGO615/source11S0 unchanged','foundation/sharedopenpanels; P06unchanged','adjustablecommonpressure/stock beforefixedholders','actualends/shortfactoryleads fitOPEN'],
 ['audio/sensors','allrequired fullnominalextensions retained','commonlowvoltagepanel/back/head supports toqualify','no part deleted or purchasedrevisioninvented','FIRSTwholeHOLD AMPtop88 vsrailbottom88']])
csvout('new-hardware-demand.csv',['role','quantity','nominal','actualstock'],[['front2clamps',2,'M3x12 +2nutAF5.5x2.4 +2washerOD7x0.5','NEEDED_UNCONFIRMED'],['rear2clamps',2,'M3x16 +2nutAF5.5x2.4 +2washerOD7x0.5','NEEDED_UNCONFIRMED'],['Pi4actualCADaxes',4,'M2.5+insulating3mmstandoff; fullstacklengthNOTSELECTED','UNQUALIFIED'],['BUSbridge4sites',4,'M3 completejoint lengthNOTSELECTED','UNQUALIFIED'],['portal/railparting','TBD','actualflatparting+standardcompletejoints beforeSTL','UNQUALIFIED']])
items={r['object']:r for r in base['rows']};fig,axs=plt.subplots(2,1,figsize=(13,9),layout='constrained')
names=['Battery_GEA223S30X6GT','Pi4B_actual_PCB','Pi_components_and_cooling','BUS25514_installed','PCA9685_Adafruit815_PCB','E1_populated_prototype_board','MAIN_Pololu4853','AUX_Pololu4092','S0_body','S0_key','MAX98357A_amp']
colors=['#a7b99c','#74a7cb','#c6dcea','#5b94b7','#adcbbf','#c1bf99','#b6d7c4','#b6d7c4','#c7bdaf','#c7bdaf','#d65b4c']
for ax,vertical in zip(axs,[1,2]):
 ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlim(-145,205);ax.set_xlabel('worldX mm');ax.set_ylabel('world'+('Y' if vertical==1 else 'Z')+' mm')
 ax.set_ylim((-100,100) if vertical==1 else (35,167))
 for n,c in zip(names,colors):
  lo,hi=plan['BUS_new_bounds'] if n=='BUS25514_installed' else items[n]['bounds_mm'];ax.add_patch(Rectangle((lo[0],lo[vertical]),hi[0]-lo[0],hi[vertical]-lo[vertical],fc=c,ec='#333',alpha=.6))
  labels={'Battery_GEA223S30X6GT':'Battery','Pi4B_actual_PCB':'Pi PCB','Pi_components_and_cooling':'Pi cooling','BUS25514_installed':'BUS','PCA9685_Adafruit815_PCB':'PCA9685','E1_populated_prototype_board':'E1','MAIN_Pololu4853':'MAIN','AUX_Pololu4092':'AUX','S0_body':'S0 body','S0_key':'S0 key','MAX98357A_amp':'AMP HOLD'}
  x=(lo[0]+hi[0])/2;y=(lo[vertical]+hi[vertical])/2
  if vertical==1 and n in ['Pi4B_actual_PCB','S0_key']:continue
  if vertical==1 and n=='Battery_GEA223S30X6GT':y=-9
  if vertical==1 and n=='BUS25514_installed':y=8
  if vertical==1 and n=='Pi_components_and_cooling':y=-7
  if vertical==2 and n=='Pi_components_and_cooling':y=125
  ax.text(x,y,labels[n],fontsize=8,ha='center',va='center')
 for label,bounds in [('frontportal',[[-104,-86,48.52],[-98,86,95.52]]),('rearportal',[[95,-86,48.52],[107,86,107]])]:
  lo,hi=bounds;ax.add_patch(Rectangle((lo[0],lo[vertical]),hi[0]-lo[0],hi[vertical]-lo[vertical],fc='none',ec='#15577a',lw=2));ax.text(lo[0],80 if vertical==1 else hi[vertical],label,fontsize=7,rotation=90 if vertical==1 else 0)
 for rb in [[[-98,-20,88],[95,-14,96]],[[-98,16,88],[95,20,96]]]:
  lo,hi=rb;ax.add_patch(Rectangle((lo[0],lo[vertical]),hi[0]-lo[0],hi[vertical]-lo[vertical],fc='none',ec='#15577a',lw=1.2))
 ax.add_patch(Rectangle((-105,-82 if vertical==1 else 45.52),282,164 if vertical==1 else 3,fc='none',ec='#666',ls='--'))
axs[0].set_title('ONE whole shared-module hypothesis — source base unchanged / not print release')
axs[1].set_title('First material falsifier: AMP nominal full-envelope top88 / shared rail bottom88 = gap0, common0',color='#a22')
axs[1].axhline(88,color='#b22',ls=':',lw=1);axs[1].text(-130,161,'BUS vs Pi cooling:31mm occupied-space gap; four realdeckclamp contacts scopedreceived',fontsize=9)
fig.savefig(P/'dimensioned-whole-top-side.png',dpi=150);plt.close(fig)
text='''# Jedna wspólna architektura modułów — wynik: HOLD przed detalami

**To propozycja całego wspólnego mocowania, nie nowy zestaw do druku.** Źródłem jest zamrożona podstawa `fit-kit-ready`/6c6a1f70; osiem osi, kupna rama/nogi i jej36plików pozostają bez zmian. Bieżący CAD: `shared-module-proposal.FCStd`. Nie wyeksportowano STL ani kolejnej kasety/uchwytu płytki.

## Decyzja i dowód

Wybór: dwa poprzeczne portale mocowane czterema pełnymi zaciskami do krawędzi DRUKOWANEJ płyty. Dwie wewnętrzne belki ponad baterią niosą wspólną płytęPi/logiki oraz boczną półkęMAIN/AUX. Cały BUS przeniesiono znad chłodzeniaPi na osobny środkowy mostek zdejmowany przed baterią. Pozostałe kupne moduły, pełne12bankówMTA/TE/ATO,5FHAC,F0,S0z11częściami/S1 i końce zachowano w aktualnych położeniach.

Odebrano pierwszą przesłankę: rzeczywiste górne i dolne pola oparcia wszystkich4zacisków w geometrii P02/P03; dolne tylne szczęki odwzorowują rzeczywisty schodek P03. Pełne śruby/nakrętki/podkładki pozostają oddzielone od126zachowanych brył WAVEGO przez numeryczne dolne granice odległości; bez globalnego Boolean126. To nie dowód udźwigu ani fizycznego chwytu. Szczegóły `first-gate.json`.

Nowy pełny BUS X18..60/Y−16,5..16,5/Z110..134 jest31mm od pełnej nominalnej rezerwy chłodzeniaPi. Oznacza koniec dawnego konfliktu rezerwy3,12mm dla tej konfiguracji, a nie kwalifikację temperatury ani wszystkich jego portów. Pi i jego GPIO/USB/Delock nie przesunięto.

**Pierwszy rzeczywisty falsyfikator całej alokacji:** wspólna dolna belka dochodzi do pełnej nominalnej rezerwy wzmacniaczaMAX98357A, która ma X−60..−33/Y−39..−15/Z75..88. Belka zaczyna się naZ88. Poprawne pełne bryły: gap0mm/common0. To HOLD przy wymaganym1,25mm, nie kontakt dostarczonej płytki ani globalna niewykonalność. Geometria audio jest nominalną rezerwą wymaganej części, nie zweryfikowanym modelem dostawcy. Nie obcięto jej i nie nazwano OWN. Po tym wyniku zatrzymano rodzinę; pozostałe11modułów/łożysk w tej kontroli jest jawnie UNRECEIVED.

**Skutek:** następna decyzja musi wspólnie rozstrzygnąć dolną warstwę audio/czujników i drogę nośną/wireaccess, zanim powstaną szczegółowe panele, dystanse czy eksporty. Nie przesuwać samej belki o ułamek milimetra i nie udawać kompletnego montażu. Aktualny CAD i obie bryły falsyfikatora są zapisane.

## Jeden układ i funkcje, bez domyślnego zamrażania starych druków

Portal przedni X−104..−98/Z48,52..95,52; tylnyX95..107/Z48,52..107. Zewnętrzne nogi Y−86..−80 oraz80..86 omijają pełne banki, a tylny most przechodzi naZ103 powyżej pełnychFHACdo101. Podstawa nie zmienia długości/szerokości; zaciski zwiększają tylko zewnętrzny zakres mocowania doY±88. Odległości od nóg w ruchu pozostająFIT1.

Belki X−98..95/Y−20..−14 i16..20/Z88..96 mieszczą baterię doZ86,5 poniżej. Wspólna płytaPi ma spód92,52/wierzch95,52; cztery3mm izolujące słupki wykorzystują rzeczywiste osie cylindrówØ2,75 w zapisanym PCB: X−74,5/−16,5 iY−34,5/14,5. To źródłowy odczyt CAD, nie wymyślony rozstaw ani dostarczony gwint. Długość całychM2.5 i spodnie komponenty wymagają przymiarki.

PółkaMAIN/AUX X55..126/Y18,5..50/Z88,52..92,52 zostawia1,48mm do zachowanych płyt; faktyczne odciążenie/śruby lub docisk krawędzi NIEodebrane. PCA/E1 opierają się dolną krawędzią na wspólnym skrzydle; pokazanie tego styku nie zastępuje docisku i dostępu do wszystkich końców.

Stara niewydrukowana rama/logiczne belki, mostkiPi i półkaBUS zostały jawnie wycofane z tej propozycji. Ich funkcje przeniesiono do nowego wspólnego szkieletu; nie przesunięto kupnych płytek w celu ukrycia1mm. P06 pozostaje niezmieniony jako węzełS0; jego stare gniazda nie są już domyślną jedyną kotwą elektroniki. Nowy szkielet ma1poprawną bryłę i zerowy brak wszystkich15zamierzonych składników. Nazwane składowe są ukrytymi referencjami FUNKCJI, nie zdublowanym BOM. Jest to koperta rzeczywistego materiału konstrukcji; **podział na płaskie portale/listwy i kompletne śrubowe połączenia pozostajeOPEN**, bez deklaracji drukowalnego monolitu. Dolne szczęki i zdejmowany mostekBUS są osobne; kupnych modułów nie scalano z drukiem.

## Kolejność dla dwóch osób — warunkowa dla tego samego układu

1. A: P00/8osi/rewizja/gwint na posiadanym WAVEGO; B: komplet części i odłączona bateria. Zachować pierwotną przymiarkę podstawy, bez wiercenia/gwintowania metalu.
2. Zaciski do rzeczywistej drukowanej krawędzi montować przed bankami i baterią. A trzyma górny portal, B podaje dolne dopasowane szczęki/nakrętki i kontroluje pełny chwyt. Nowe standardowe2M3×12+2M3×16,4pełne nakrętki2,4 i4podkładki0,5 są zapotrzebowaniem, nie stanem magazynu. Ostateczny podział portali/listw/połączeń dopiero po usunięciu obecnegoHOLD.
3. E1/MODULE i końceMTA przygotować na stole pozaPETG; nie rozłączać wirtualnie lutów. WAGO montować według ról4DATA/5plus/7masa. PełneMTA/TE/ATO,FHAC i ich dwa końce układać w otwartych obszarach; dawne3mm między stacjami nie dowodzą wyjścia przewodów.
4. Po rzeczywistym zamknięciu warstwy audio i podpór dopieroPCB/izolujące dystanse/porty. ZakresGPIO/USB/Delock/PWM/MAIN/AUX/S0/S1 i narzędzia muszą być dostępne przed dociskami/tylnymi osłonami. Prawdziwa retencja baterii i wybranych2pasków pozostaje osobną brakującą funkcją, nie samym naciskiem grawitacyjnym stóp.
5. BUS na środkowym mostku po podłączeniu jego rzeczywistych końców. Przed wyjęciem baterii: odłączenie baterii, rozłączenie istniejących rozłącznychUSB/zasilaniaBUS zgodnie z faktycznymi portami, odkręcenie mostka i zdjęcie go. Nie zakładać parkowania połączonego przewodami ani dodatkowej długości; tej sekwencji jeszcze nie przyjęto geometrycznie/na sprzęcie. Nigdy nie odpinać lutówE1 dla wygody.
6. Głowa/ogon, kamera/ToF/audio/touch, panel tylny i sylwetkaOli pozostają na całym widoku; ich11dalszych sprawdzeń po falsyfikatorze jest nieodebranych. Rzadka naprawa może wymagać demontażu; nie projektować szybkiego serwisu ani produkcyjnej skorupy w tej porcji.

## Końce, miejsce na wiązki i rzeczywiste niewiadome

Wspólne otwarte obszary: niżej rozdział/WAGO i12zabezpieczeń, nad boczną półką otwartyfanP/G/logika, PiGPIO na otwartej stronie, luźny pełnyUSB500 zDelock i odciążenia obok mostka; banki/FHAC pozostają dostępne od boków. Są to połączone kierunki układania w otwartym prototypie, **nie odebrana pojemność każdej wiązki/R/length/slack**. Każdy krytyczny port i przejście musi po zamknięciu obecnegoHOLD dostać rzeczywiste miejscowe sprawdzenie; same prostokąty nie sąPASS.

4niezależne220 iobaMTAkońce, pełnyUSB500,5parFHACminimum84,5, K1474Pi350/kolor vsinput210 i końce fabryczne zachowane; brak cięcia, nowego złącza/puli albo kredytu starej pozy. Actualinstalledlength/cut/slackNULL.57wybranych wCSV bez zmiany grafu; wymagane audio/sensory zachowane z jawną nominalną geometrią/revisionfit. PraktyczneFIT1(mocowania/masa/ruch),FIT2(porty/końce/S0M6/chłodzenie/stock) iFIT3(pełny obrysOli/głowaogon) nadal niewykonane. Nie ma nowego fizycznegoPASS, zasilania, druku, zakupu ani eksportu do slicera.
'''
(P/'ASSEMBLY_PROPOSAL.md').write_bytes(text.encode())
print(json.dumps({'root_checks':len(root['checks']),'whole_material_received':len(gate['checks']),'unreceived':len(gate['not_received']),'decision':gate['status']}))
