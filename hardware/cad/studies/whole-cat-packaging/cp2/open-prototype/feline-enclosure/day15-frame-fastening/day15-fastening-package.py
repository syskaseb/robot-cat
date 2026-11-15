from pathlib import Path
from datetime import datetime,timezone
import json,csv,hashlib,zipfile,subprocess,shutil,struct,collections
ROOT=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');P=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-frame-fastening';TMP=Path('C:/Users/Sysq/AppData/Local/Temp');old=P.parent/'day15-essential-shared-frame';material=json.loads((P/'material-result.json').read_bytes());delta=json.loads((P/'delta-result.json').read_bytes());hardware=json.loads((P/'hardware-gate.json').read_bytes());plan=json.loads((P/'whole-fastening-plan.json').read_bytes())
for n in ['day15-fastening-visual.py','day15-fastening-plan-hardware.py','day15-fastening-material-tail.py','day15-fastening-prepare-material.py','day15-fastening-material-build.py','day15-fastening-delta-export.py','day15-fastening-package.py']:shutil.copyfile(TMP/n,P/n)
def pin(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
with (P/'parts.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f);w.writerow(['part','qty','localXYZ_mm','release','sourceSTLreuse'])
 for r in material['parts']:w.writerow([r['name'],r['quantity'],r['print_size_mm'],'HOLD_XT60_NO_PRINT_RELEASE',r.get('unchanged_source_STL_sha256','changednecessarybearing')])
with (P/'fasteners.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f);w.writerow(['joint','type','L_includinghead','shaft_d','head_d_max','head_k_max','headangle','fullnutthickness','nutwasher','stack','tipbeyondnut','inventory'])
 for j in plan['joints']:w.writerow([j['tag'],'ISO10642 full countersunk',j['length_including_head_mm'],3,6.72,1.86,90,2.4,.5,j['printed_stack_mm'],j['tip_beyond_fullnut_mm'],'UNCONFIRMED'])
mesh=[]
for row in material['parts']:
 b=(P/(row['name']+'.stl')).read_bytes();n=struct.unpack_from('<I',b,80)[0];assert len(b)==84+50*n;e=collections.Counter();v=0
 for i in range(n):
  a=struct.unpack_from('<12f',b,84+50*i)[3:];p,q,r=[a[j:j+3] for j in [0,3,6]];v+=sum(p[k]*(q[(k+1)%3]*r[(k+2)%3]-q[(k+2)%3]*r[(k+1)%3]) for k in range(3))/6;pts=[tuple(round(x,5) for x in s) for s in [p,q,r]]
  for j in range(3):e[tuple(sorted([pts[j],pts[(j+1)%3]]))]+=1
 assert all(x==2 for x in e.values()) and v>0;mesh.append(dict(part=row['name'],closed=True,volume_mm3=v,triangles=n))
(P/'mesh-check.json').write_bytes((json.dumps(mesh,indent=2)+'\n').encode())
text='''# START — jedna architektura wszystkich10połączeń, materiał przyXT60 HOLD

**NIE ZWALNIAĆ DO DRUKU:** dodanyfragmentP12 względem pełnegoXT60H zboots: gap0/common0, wymagane1,25. To aktualna blokada prześwitu tego wspólnego rozwiązania, nie kontakt dostarczonych części/niemożliwość wszystkich dróg. Bez drugiej rodziny po wyniku. Model `frame-fastening.FCStd`, nineSTL/BOM i bieżący lokalnyPNG są zapisem inżynierskim. Podstawa6c6a pozostaje zamrożona.

## Widoki dlaZeno — przed zmianą łączników

`visual-baseline/whole-opaque-side.png` i `whole-opaque-front-three-quarter.png` to ten sam acd6układ. IstniejąceOla obrysy są nieprzezroczyste, nie utworzono nowej skóry. Prawdziwe wystające moduły/napędy pozostały; całełapy/ogon w kadrze. ZdjęcieOli, źródłowyFCStd, SHAkształtów osłon, kamery i PNG w `snapshot-source-pins.json`. Linie osi widoku nie są detalem robota. Engineeringpresentation przywrócona po zdjęciach. Nie używać wcześniejszych nieodebranych pustych/kadrowanych prób.

## Całe standardowe łączniki zamiast trzeciego przesunięcia

Wszystkie10NOWYCH zestawów mają pełny łeb stożkowyISO10642, otwórHEX2 głębokości1,1, maksymalny łebØ6,72×1,86/90°. Długość nominalna obejmujeCAŁY łeb; nie dawny odcinek spod łba. Osi/pozy modułów nie przesunięto. Wymiar z pierwotnego dokumentu producenta [BossardBN2104,p1](https://www.tme.eu/Document/8ccf0396b9d8180afe969e47af892318/BN_2104_1_Bossard_1.pdf). BinaryGET403; zapisany odczyt i pin są jawną transkrypcją odczytuPDF, nie udawanym plikiemPDF. Wybrano nowe NIEPOTWIERDZONE zapotrzebowanie, nie dokonano zakupu ani twierdzenia o zapasie/gwincie/nośności.

-8×M3x10 dla zakładek portali i górnych belek,2×M3x12 dlaBUS. Dziesięć pełnych nakrętekAF5,5×2,4 i dziesięć podkładekOD7×0,5 po stronie nakrętki; brak płaskiej podkładki pod stożkiem jest celową zmianą typu połączenia, nie usunięciem kupnego stocku.
-Cztery oryginalne zaciski podstawy z całym metalem pozostają bez zmian:2socketM3x12+2socketM3x16/4nuts/4washers, nie dublować wBOM.
-Warstwa pod łbem4mm, nominalny materiał za stożkiem2,14mm. Dolne zakładki4+2mm; górne4+2mm;BUS4+4mm. Są to wymiary użytecznego gniazda, NIEPASS wytrzymałości. NativeCommon dla łba nie wykazał dodatniego przenikania; niezależna miara powierzchni styku stożka nieodebrana, nie nazywać jej potwierdzonymbearingarea.
-Nakrętka+podkładka mają realny otwarty boczny feed8mm i drukowaną blokadę obrotu. Dziesięć konserwatywnych ciągłych pokryć całego stocku/8mm ruchu ma0wspólnej objętości z właściwym backprint. Nie zastępuje tego wsunięcie w samym ostatnim położeniu. Otwór po stronie nakrętki leży ZA powierzchnią docisku; nie przecina jej chronionego materiału od strony głowy.

## Co rzeczywiście odebrano

30pełnych metali/10zestawów:6480konserwatywnych granic do216aktualnych części/rezerw; brak potrzeby exactBOP dalekich par. Bez globalnego126compound ani starychmacierzy. Własne wydruki9×1validSolid,6głównychczęści/15parcommon0. Sześćdziesiąt relacji metalu z dwoma właścicielami bez dodatniejobjętości. Konieczne70,767mm³ nakładania ściany kieszeni po pierwszej implementacji przydzielono jednemu rzeczywistemu drukowi z0utraty łącznego materiału — naprawa podziału, nie kolejna rodzina aniOWNwaiver.

Narzędzie: normalnyHEX2 zewnętrznykrótkiodcinek12mm i rezerwa uchwytuR2,5. Sprawdzono31bliskich relacji/pozostałe dolnymi granicami w fazie gołej ramy oraz dopasowanie dootworu łba. Nakrętki wkładać przed połączeniem części; A podtrzymuje komplet, B wprowadza śrubę, płaskie kieszeni blokująobrót. Nie wymagano fikcyjnego odpinaniaE1 ani narzędzia przez zamontowanyPCB. Pasowanie rzeczywistego narzędzia i tolerancja druku pozostająFIT.

Nowymateriał doobecnychczęści i przyjętej obsady audio sprawdzano perrzeczywistysolid/cull, zatrzymano po pierwszym P12/XT60. Dalsze dodane części/sąsiedzi są NIEODEBRANE. R12/84+21/pełnyfeed poprzedniejporcji pozostaje odebrany dla niezmienionychfragmentów, ale całanowarama/audio-nowy materiał nie maGO po tymHOLD. StareC0BNO1,6539166 iC1MAIN2,9186763 pozostają zamrożone; nowa architektura nie zeruje historii.

## Dwie osoby — ta sama konfiguracja

1.Próba P00/8osi/rewizji/gwintu i wyłączony sprzęt toFIT1, nie czynność wykonana. Najpierw goły podzespół ramy na stole: A wkłada nakrętki z podkładką przez prawdziwy feed, B wkłada pełne śruby. Wkręcać stopniowo, nie deklarować momentu/siłyPETG.
2.PozaPETG przygotować lutowaneE1/końce; złożyć prostą ramę zanimPCB i banki ograniczą narzędzie. Potem rzeczywiste4zaciski do odebranejpodstawy, otwarte układanie fabrycznych końców/4niezależne220/obaMTA/FHAC/K1474. Krótkich przewodów nie przedłużono ani nie zamieniono ilustracyjnych krzywych w sztywne części.
3.P14zTTP zostaje na stałe, istniejący przewódE1 nie jest odpinany/parkowany na zmyślonym luzie. Po układaniu zamknąćP15ReSpeaker iBUS. Dla baterii: istniejącyUSB_AUDIO/P15, następnie istniejąceUSB+powerBUS/P13, odłączona bateria i częściowy demontaż w razie potrzeby. Rzeczywisty przebieg/stock/końce pozostająFIT2.
4.RetencjaPCB/głośnika/mikrofonu/banków/baterii jest następna po odebranej ramie. Nie dociskać niewidocznych elementów ani membrany/otworów mikrofonu. Bez nowej komoryakustycznej, produkcyjnejskóry, FEA/slicera/druku/zasilania.

DziewięćSTL/10szt, lokalnyXYZ/Z0/<256. Trzy dolne szczękiSTL byteidentical doacd6; pozostałe zmieniono tylko dla rzeczywistych gniazd/feed/bearing. P12nie rozbito dla ogólnegoDfAM; realna próbka podwieszenia i orientacja/podpory toFIT przed większym drukiem. Fizyczne gwinty/masa/ruch/końce/obrysOli/FIT1-3 nie wykonane. actualfit/cut/slackNULL. Okno pracy pozostaje aktywne.
'''
(P/'START_HERE.md').write_bytes(text.encode())
saved=json.loads((P/'native-save-received.json').read_bytes());assert saved['gui_modified'] is False
with zipfile.ZipFile(P/'frame-fastening.FCStd') as z:assert z.testzip() is None;crc=len(z.namelist())
sources=[]
for folder in ['day15-essential-shared-frame','day15-audio-region-proof','day15-audio-module-layer','day15-shared-module-fit','day14-fasttrack-first-fit/fit-kit-ready']:
 q=P.parent/folder/'manifest.json';m=json.loads(q.read_bytes())
 for x in m['files']:assert pin(Path(x['path']))['sha256']==x['sha256'],x['path']
 sources.append(pin(q))
files=sorted(x for x in P.rglob('*') if x.is_file() and x.name!='manifest.json' and x.suffix!='.FCBak' and '.FCStd.' not in x.name)
m=dict(status='ONE_WHOLE_COUNTERSUNK_AND_FEED_ARCHITECTURE_METAL_OWN_CLEAR_NEW_MATERIAL_XT60_HOLD',utc=datetime.now(timezone.utc).isoformat(),files=[pin(x) for x in files],sources=sources,all142_oldfiles_unchanged=True,native=saved,native_crc_members=crc,hardware_gate=hardware['status'],fullsteel30_bounds6480=True,own_print15_disjoint=True,own_metal60_no_penetration=True,continuous_fullstock10_feeds_clear=True,bearing_area_not_qualified=True,head_axial_web_mm=2.14,profile_audio_reuse='Old84+21/1.3feed conditionalidentity/subset; newaddedmaterial/audio notallqualified afterXT60stop',first_falsifier=delta['first_falsifier'],delta_checks=dict(tool=len(delta['tool_checks']),material=len(delta['material_checks']),bounds=len(delta['bounds'])),remaining_added_material_unreceived=True,STL9_pieces10=True,three_jaw_STL_exact_reuse=True,old_negatives2_preserved=True,one_family_no_afterfalsifier_retry=True,print_release=False,physical_pass=False,strength_pass=False,actual_fit_cut_slack=None,window_closed=False)
(P/'manifest.json').write_bytes((json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode());paths=[str(Path(x['path']).relative_to(ROOT)).replace('\\','/') for x in m['files']]+[str((P/'manifest.json').relative_to(ROOT)).replace('\\','/')];cmd=['git','-c','core.autocrlf=false'];subprocess.run(cmd+['add','--']+paths,cwd=ROOT,check=True);subprocess.run(cmd+['commit','--only','-m','Freeze opaque baseline and whole countersunk frame architecture with XT60 material HOLD','--']+paths,cwd=ROOT,check=True)
c=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();raw=subprocess.check_output(['git','ls-tree','-r','-z',c,'--',str(P.relative_to(ROOT)).replace('\\','/')],cwd=ROOT);count=0
for rec in raw.split(b'\0'):
 if not rec:continue
 meta,path=rec.split(b'\t',1);data=subprocess.check_output(['git','cat-file','blob',meta.split()[2].decode()],cwd=ROOT);assert data==(ROOT/path.decode()).read_bytes();count+=1
assert count==len(paths);changed=subprocess.check_output(['git','diff-tree','--no-commit-id','--name-only','-r',c],cwd=ROOT,text=True).splitlines();assert sorted(changed)==sorted(paths);v=dict(commit=c,exact_files=count,manifest_sha256=pin(P/'manifest.json')['sha256'],native_crc_members=crc);(TMP/'day15-fastening-verified.json').write_bytes((json.dumps(v)+'\n').encode());print(json.dumps(v))
