from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,csv,shutil,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
ROOT=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');P=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-carrier-capture-first-fit';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(P/n).write_bytes((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
r=json.loads((P/'actual-capture-section-curves.json').read_bytes());fig,axs=plt.subplots(1,3,figsize=(15,6));colors={'P19_shared_lower_carrier':'#d17b12','Battery_GEA223S30X6GT':'#25864c','STRAP0_bodyloop_full2p2':'#3747a3','P05_spacer_instance2':'#c93431','H03_panel_M3x55_1':'#444444','S0_body':'#c93431'}
for ax,sec in zip(axs,r):
 for row in sec['curves']:
  p=row['points'];ax.plot([q[0] for q in p],[q[1] for q in p],c=colors[row['name']],lw=1.6)
 ax.grid(alpha=.2);ax.set_aspect('equal')
axs[0].set(xlim=(13,25),ylim=(60,77),xlabel='Y [mm]',ylabel='Z [mm]',title='Actual bar captured inside belt / X29.5')
axs[0].annotate('1.25 cell gap',xy=(18.1,69),xytext=(13.5,75),fontsize=8,arrowprops=dict(arrowstyle='->'))
axs[1].set(xlim=(17,42),ylim=(60,74),xlabel='X [mm]',ylabel='Z [mm]',title='Real CLOSED window / Y19.6')
axs[1].text(22,72,'16.2 x 4.6 slot / full15 x2.2',fontsize=8)
axs[2].set(xlim=(102,115),ylim=(7,23),xlabel='X [mm]',ylabel='Y [mm]',title='Actual open P05 / M3 bay / Z64')
fig.legend(handles=[Line2D([0],[0],c=c,label=l) for l,c in [('P19carrier','#d17b12'),('Fullselectedbeltprofile','#3747a3'),('Nominalcell','#25864c'),('Retainedsourcepost/S0','#c93431'),('FullM3x50','#444444')]],loc='lower center',ncol=3,fontsize=8);fig.tight_layout(rect=[0,.13,1,1]);fig.savefig(P/'actual-capture-window-and-bay-sections.png',dpi=160);plt.close(fig)
ex=json.loads((P/'export-and-local-assembly.json').read_bytes());gate=json.loads((P/'capture-changed-gate.json').read_bytes());mat=json.loads((P/'capture-material-proof.json').read_bytes());assert not gate['failures']
old=P.parent/'day15-frame-fastening';refs=[]
for p in sorted(old.glob('*.stl')):
 if any(n in p.name for n in ['P11','P13','P14','P15','P16','P17','P18']):refs.append(dict(path=str(p),sha256=sha(p),qty=2 if 'P16' in p.name else 1,status='UNCHANGED_SHAPE_REFERENCE_CONDITIONAL_COMPONENTFIT'))
new=[dict(**row,sha256=sha(P/row['file'])) for row in ex['exports']]
write('current-print-index.json',dict(release='CONDITIONAL_UNPOWERED_CARRIER_FIRST_FIT_NOT_WHOLECAT',start='P00source8holetemplate andactualframefit FIRST, thenanchorcoupon, thencurrentthreeparts',new_current_parts=new,coupon=dict(file='COUPON_actual_anchor_feed.stl',sha256=sha(P/'COUPON_actual_anchor_feed.stl'),qty=1,**{k:v for k,v in ex['coupon'].items() if k!='qty'}),unchanged_mesh_references=refs,foundation_manifest=dict(path=str(P.parent/'day14-fasttrack-first-fit/fit-kit-ready/manifest.json'),sha256=sha(P.parent/'day14-fasttrack-first-fit/fit-kit-ready/manifest.json')),no_oldP10P12filename_inheritance=True,no9meshcopy=True))
with (P/'parts-and-fasteners.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f);w.writerow(['role','qty','nominal','status'])
 for row in new:w.writerow([row['part'],1,row['file'],'CONDITIONAL_UNPOWERED_DRYFIT'])
 w.writerow(['Anchorfeedcoupon',1,'16.2x4.6 actualwindow, 15x2.2 fullfreeend, sameprintorientation','FIRST_COUPON'])
 for role,qty,nom in [('Verticalbolt',1,'ISO10642M3x12 lengthINCLUDINGhead D6.72/1.86'),('Verticalfullnut',1,'M3AF5.5/h2.4'),('Verticallowerwasher',1,'M3ID3.2/OD7/t0.5'),('Frontbolt',1,'M3x16 fullheadD5.5/h3 unchanged'),('Frontfullnut',1,'M3AF5.5/h2.4'),('Frontfullwashers',2,'M3ID3.2/OD7/t0.5')]:w.writerow([role,qty,nom,'UNCONFIRMED_STANDARD_DEMAND_NO_PURCHASE'])
 w.writerow(['OldrearhorizontalM3x25+2washers+nut',0,'Unbuiltrole REPLACED bydirectP12joint; sourcegeometrykeptHIDDENreference','RETIRED_ROLE_NOT_BOUGHTPART_DELETE']);w.writerow(['Selectedstraps',2,'SameNSTRIF15200M15x200 textile,total210inclbuckle','ACTUALCLOTH_BUCKLE_LAP_FIT3']);w.writerow(['Allsourcefoundation/framehardware',1,'Unchangedlists referencedbysourceSHA, inclfullH03M3x50/P05','RETAINED_NO_INVENTORY_ASSERT'])
write('bounded-disposition.json',dict(utc=datetime.now(timezone.utc).isoformat(),status='NOMINAL_CARRIER_CAPTURE_AND_STRAP_LOADPATH_CONDITIONAL_FIRST_FIT_RELEASE',finite_read_first=True,finite_missing1756bounds27exact=True,old33_and1815_received_notreplayed=True,whole_material_causes_resolved=['openP05/fullH03bay withbroadremainingrearstop','samefrontjointrealP10receivingearactualsource48','twoactuallinkedclosedbeltwindows'],anchor_actual_captured_member_volumes=[x['bar_inside_closed_cavity'] for x in mat['belt_links']],not_volumealone='Bothbars spanfullbeltwidth, outsideendwebspositivelyjoinfloor andcloseXZwindow linkedbyYZbelt; fullfreeendcontinuousprismcommon0 beforecell. Wholebuckleoutside.',support_full_nominalcellfloor_missing0=True,new_positive1461bounds22checks_clear=True,front_fullbearing_gap0=True,sourcewholeprintparting_and_initialassembly_scope='Actualcriticalcell+6stock+newreceiverpositiveZboundsandfreeendthread areproved. AssemblebareP19/cell/P12 withrealP10P11loose beforetightening, useunchangedopenhalflaps. No claimfullwiredwholekittrajectory; printrevisionfit/actualfactoryleadparkingandlaterbatteryserviceFIT1/2.',driver_phase='HEX2R4.25 overlapsMAIN actual435.5067 airfield; installbeforeMAIN, nooperatingmetalcollision. LowerR4.25nutspannernegativeXclearsource beforebanks.',effectivity=ex['effectivity'],cell_arrest='Frontstop/rear27mmfaceblockX; fullfloorandlinkedclosedbeltsblockZ; opposedsideanchorsandloopwidthlimitY/rotation. Actualtightness/no-rattle/strength physicalFIT, notfriction-onlymechanicalrootclaim.',export=new,coupon=ex['coupon'],physical_pass=False,whole_cat_or_all_module_kit_ready=False,actual_fit_cut_slack=None,remaining=['FIT1source8holes/threadrevision/printedhalflapfit/load/legmotion','FIT2actualfactoryends/stock/leadexitandpartialP12batteryservice withPi-P10cornerrelease, E1stayssoldered','FIT3actualstrapfreeend/sewnend/buckle/lap/tension/cellpadding/loadcoupon','OtherPCB/WAGO/bank/audioretentionandheadroot stillOPEN']))
sources=[P.parent/'day15-carrier-rear-contour-fit/manifest.json',P.parent/'day15-carrier-rear-contour-fit/carrier-contour.FCStd',P.parent/'day15-direct-carrier-frame-joint/manifest.json',P.parent/'day15-p12-integrated-retention/manifest.json',ROOT/'hardware/electronics/kicad-current/selected-components.csv']
for folder in ['day15-carrier-rear-contour-fit','day15-direct-carrier-frame-joint','day15-p12-integrated-retention']:
 base=P.parent/folder
 for row in json.loads((base/'manifest.json').read_bytes())['files']:
  f=Path(row['path']);f=f if f.is_absolute() else base/f;assert sha(f)==row['sha256'],f
write('source-pins.json',dict(source_commit='66b993bc3ebac9deba97488683a8ac69d0cdc6e4',pins=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sources],previous29_plus23_plus36_exact_unchanged=True,physicalparts_factoryends_all57_extras_graph4DATA5plus7G_preserved=True,worldonce_sourceShape_copy_not_byteidentity=True,no_new_strap_purchase_splice_cut_or_boughtpose=True))
for n in ['day15-capture-screen.py','day15-capture-build.py','day15-capture-check.py','day15-capture-export.py']:shutil.copyfile(Path('C:/Users/Sysq/AppData/Local/Temp')/n,P/n)
(P/'START_HERE.md').write_bytes('''# Carrier baterii/MTA — części do warunkowej suchej przymiarki

**Bieżący zestaw:3nowe STL po1szt +1kupon kotwy. To przymiarka BEZ ZASILANIA, nie gotowy cały kot ani komplet mocowań elektroniki.**

Najpierw P00/source8osi z zamrożonego zestawu podstawy i rzeczywista rewizja/gwinty. Potem `COUPON_actual_anchor_feed.stl` z dwiema wybranymi opaskami; na końcu trzy aktualne części z `current-print-index.json`. W tym folderze są jedyne bieżące P10/P12/P19; nie używać dawnych STL P10/P12 o tych samych nazwach. P11/P13/P14/P15/jaws i podstawa są wskazane przez niezmienione SHA bez kopiowania9siatek. Model całości: `carrier-capture.FCStd`.

## Jedna wspólna poprawka trzech przyczyn

Przed zmianą wykonano skończony przegląd brakujących zależności:1756bounds/27exact, reuse33+1815wcześniejszych. Zebrano razem P05/H03, brak oparcia przedniej podkładki i brak kotew pasków. Nie robiono kolejnych rodzin lokalnych śrub.

Tylny stop jest szeroki na wolnej części: pokrywa27mm z35mm nominalnej tylnej powierzchni ogniwa. Przy zachowanym P05/H03 jest otwarta zatoka z zapasem1,5mm (1,25+własne0,25), nie cienkaścianka0,75. Cała podłoga2mm pod nominalnym obrysem106,5×35 pozostała:0missing. R5 od strony S0,4stopy, ramię95..100 i odebrany węzeł P12 pozostały. Nowe sprawdzenia obejmują rzeczywiste P05,pełneM3x50,S0 i dodatni materiał; 1461bounds/22kontrole bezHOLD.

Przedni pełny M3x16 pozostał na tej samej osi, z2podkładkami i pełną nakrętką. Zrealizowano brakujące ucho P10 na rzeczywistym48mm³ połączeniu z jego podłogą, teraz podkładka ma gap0/common0. Nie przestawiono łba/tipa ani kupnego modułu. Odebrany pełny pionowy M3x12zachowany; wycofano rolę NIEZBUDOWANEGO tylnego poziomegoM3x25, zostawiając jego ukrytą geometrię historyczną. Nie wycięto jego padów z czynnego ramienia.

## Rzeczywiste zamocowanie obu pasków

Każda CAŁA200opaska przechodzi przez zamknięte okno16,2×4,6mm. Jej pętla obejmuje drukowany mostek (105mm³ wewnątrz każdej pętli), którego dwa boki poza pełną15mm szerokością paska łączą się dodatnią objętością z podłogą. Powstaje rzeczywiste przeplecenie dwóch zamkniętych obwodów, nie etykieta ani tarcie. Bar21mm, endwebs2,4, bok1,75/wysokość4, własny boczny luz0,6; nominalne1,25 od ogniwa. Kotwy po przeciwnych stronach ograniczają boczny przesuw, front/rearstop blokująX, podłoga i zamknięte pasyZ. Dokładna sztywność/luz po naciągnięciu to próba fizyczna, nie rattle/strengthPASS.

Pełny wolny koniec15×2,2 ma ciągłą18mm drogę przewlekania z common0; przewlekać PRZED ogniwem. Sprzączka pozostaje na zewnątrz, nie przechodzi przez cienkie okno. Każda opaska nadal200tkaniny:130,65pętla+20projektclosure+49,35cała reszta;210zawiera sprzączkę. Brak nowych jednostek, cięcia, zapasu25 czy kredytu za krótsze przewody.

## Składanie we dwie osoby

1. Na stole A trzyma P19, B przewleka wolne końce obu opasek i sprawdza kupon. Buckle poza oknem; nie przeciskać metalowego ani grubego szytego końca na siłę. Rzeczywiste maksymalne szerokość/grubość/sewnend muszą zmieścić się w zmierzonym oknie.
2. Dummy/niepodłączone ogniwo i luźne paski układa się PRZED zamknięciem P12: otwór30mm nie przepuszcza pionowo ogniwa35mm. P10/P11 pozostają rzeczywistymi osobnymi, luźnymi elementami podczas ustawiania P19/ogniwa/P12, potem łączymy istniejące otwarte półzakładki i podstawę. Bez wirtualnego odczepiania integralnych części.
3. Dla opuszczania P12 wykazano ciągłe ograniczenie rzeczywistym materiałem nad ogniwem (1,5mm) oraz wszystkimi6polami pasków (2,6/0,4mm lub brak materiału w kolumnieXY); osobno kluczowe nowe człony carriera. To nie pełny rigidtrajectory całego okablowanego kota. Dopasowanie półzakładek/revizji sprawdzić najpierw bez ogniwa.
4. Pełną przednią śrubę/2washers/nut oraz pionowąISO10642M3x12/washer/nut dokręcać w otwartym układzie przed MAIN i bankami. HEX2R4,25 koliduje tylko jako przestrzeń narzędzia z MAIN, więc MAIN później; dolny klucz/nakrętka od−X. Nowe standardowe łączniki: zapas niepotwierdzony, bez twierdzenia o dostarczonym gwincie/torque.
5. Zachowane S0/P06/P05/H03 montować według zestawu podstawy przy luźnych jeszcze elementach ramy; nowa zatoka zapewnia ich miejsce. Pełne banki/MTA220 z obiema fabrycznymi końcówkami i połączony benchkit E1/TTP układać otwarcie; nie udawać rozpinania lutów ani przedłużenia krótkich końców. Elementy ochrony pozostają kompletne. Nacisk MTA wyłącznie na sprawdzony plastik, nie metalowy terminal.
6. Dopiero po suchej przymiarce zamknąć opaski z rzeczywistym właściwym zakładem/naciągiem i zaparkować całe końce. Wszystkie porty/USB/krótkieFHAC/rzeczywiste wyjście ogniwa muszą być sprawdzone na miejscu (FIT2), bez obcinania fabrycznych długości czy pożyczania zapasu.

Późniejsze wyjęcie baterii może wymagać P15mic->P13BUS->rzeczywisteXT60/balance, zwolnienia roguPi naP10 oraz P12/mocowania carriera i podparcia całego połączonego zestawu przez drugą osobę. LutowanyE1 pozostaje cały. Parkowanie pełnych końców i rzeczywista droga demontażu pozostająFIT2; nie przyznano rapidservice ani wholekitGO.

## Druk i granice odbioru

STL są zamknięte,dodatnie,Z0 i poniżej256mm. P10:89,48×176×54, przodem na stole; P12:193×91×43; P19:206×40×93,5 bokiem na zewnętrznej powierzchni MTAfloor. PETG. P19 potrzebuje dobranej adhezji i podparcia pierwszej krawędzi tacki/kołnierza; P12 podniesionej półki logicznej, P10 wystających stop/postów według drukarki. Nie ma przypiętego slicera/profilu ani twierdzenia „bez podpór”. Kupon jest w tej samej orientacji coP19 i służy fitowi oraz próbie kotwy przed dużym wydrukiem.

FIT1:source8otworów/revizja/połączeniawydruków/masa i ręczny ruch nóg; FIT2:całe fabryczne końce,rzeczywisty leadexit i późniejszy demontaż; FIT3:cloth/buckle/lap/tension/padding oraz próba obciążenia kotwy. Bez nacisku przez nieznane powierzchnie ogniwa. Wszystkie57+extras/4DATA5plus7G/ochrona/4niezależne220/MTA zostają. Pozostałe PCB/WAGO/bank/audio retention i korzeń głowy OPEN. Actualfit/cut/slack=NULL; fizycznych prób, zasilania, druku ani zakupu nie wykonano.
'''.encode())
print(json.dumps(dict(prepared=str(P),parts=3,coupon=1,wholekit=False)))
