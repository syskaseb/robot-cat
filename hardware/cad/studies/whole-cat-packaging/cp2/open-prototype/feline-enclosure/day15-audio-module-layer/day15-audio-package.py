from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile,subprocess,shutil
ROOT=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical');P=ROOT/'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-audio-module-layer';OLD=P.parent/'day15-shared-module-fit';r=json.loads((P/'result.json').read_bytes());plan=json.loads((P/'proposal.json').read_bytes())
text='''# Cała warstwa audio + wspólne podparcie — jeden układ, HOLD pola zawrotu

**Bieżący model:** `audio-layer-proposal.FCStd`, widokcałości i lokalnyPNG. To nie zwolnienie druku ani zasilonego robota. Zachowano pełne części, podstawę,4mocowania z całym metalem i31mm rezerwyPi/BUS. Nie uruchomiono nowej rodziny po wyniku.

## Wspólna decyzja przestrzenna i źródła

- Głośnik100×45×21: X−113..−13/Y−19,5..25,5/Z65,5..86,5, w całości, bez skalowania. Wspólna półka63..65,5 leży nad WAGOdo61,52; korpus pod belkąod88 ma1,5mm. Przesunięcie całego modułu wynika z warstwy nad rozdziałem i bocznego pełnegoBNO, nie z ułamkowego przesuwania belki.
- MAX98357A27×24×13 z terminalami obrócono jako CAŁOŚĆ do pionowej pozyX−62..−35/Y21..34/Z96..120. Podparcie krawędzi na wspólnej płycie; pełne8424mm³ zachowane. Retencja rzeczywistej wersji płytki jest nadal essentialNEXT, nie potwierdzono otworów fabrycznych.
- ReSpeakerLite pozostaje86×35×10 pod grzbietem; zachowane źródło projektu zawiera pełną rezerwę94×43×16 zUSB, X−9..85/Y±21,5/Z140..156. To projektowe założenie komponentów/wtyku, nie dokładny model dostawcy. ReSpeaker iTTP223 są na jednej zdejmowanej górnej ramce opartej na4rzeczywistych portalach; TTPpozostajeX5..30/Y45..65/Z141..149.
- BNO zachowano razem z30×28×10 rezerwą złącza ze źródła, nie tylko25,6×22,7×4,6 gołegoPCB. Głośnik ma do tej rezerwy3,15mm wY. Pełny mikrofon/USB/touch i pozostałe wymagane rozszerzenia nie zniknęły przez brak w57CSV.

Źródłem tych nominalnych profili jest istniejące `robot-cat/hardware/wavego/layout/components.json` — historyczne studium, nie printPASS/nowy wybór katalogowy. Przypięto użyte5rekordów i plik. Z archiwalnego kontraktu interfejsów użyto wyłącznie faktów: AMP=I2S, ReSpeaker=osobnyUSB, para głośnikaBTL — żaden przewód nie jest masą. Nie zmieniano grafu ani aktualnego pinoutu ochrony.

## Materiał, prowadzenie i montaż

Wspólny nośny model dostał półkę głośnika i jej przednią poprzeczkę/tylne podwieszenia, dwa podparciaAMP oraz celowy otwarty kanał w płycie logiki X−75..−63/Y23..43/Z90..94. Nie jest to przycięcie belki pod dawnymAMP: AMPprzeniesiono w całości, a kanał służy układaniu przewodów przed pionowąPCA. Zachowano pozostałe korzenie/belki; rzeczywiste zamierzone składniki bez braków, wspólny materiał1validSolid. Górna ramka mikrofon/dotyk jest osobna, bez wspólnej objętości z dolną konstrukcją. Podział na płaskie wydruki, pełne łączniki, dociskiPCB/obudowy głośnika i dostęp narzędzi pozostają do zaprojektowania po rozwiązaniuHOLD.

Dwa połączone obszary robocze miały poprowadzić5sygnałów/zasilaniaI2S oraz parę głośnika: w kanale7profilów (5×Ø1,6 i2×Ø2,1/.2odstępy/.4zewnętrzny margines), pakowanie7,8×4,7 w8×5; dalej otwarte pole nadPi i pole zawrotu przyAMP. Promienie6,4/8,4 to własne założenia do przymiarki, nie producent ani dawneR35,1. Faktyczne pady/kierunki i długości nie są z tego powodu przyjęte.

**Pierwszy nowy HOLD:** pole `AL_AMP_FREE_TURN_BAY` X−77..−63,25/Y21..34/Z95,25..134,25 dochodzi do krawędzi tackiPi. Poprawne pełne operandy: gap0/common0, próg1,25. To konflikt przydzielonego pola, nie kontakt fizycznego przewodu ani dowód niemożliwości wszystkich przebiegów. OperandyBRep i lokalnyPNG zachowane. Nie wykonano kolejnego wariantu wysokości/roll/cięcia. Ciągłość tego pola i końcowe promienie pozostająnieodebrane.

Zmieszczono w badanym sąsiedztwie zmienione pełneAMP/głośnik, nowe podparcia i rezerwyBNO/ReSpeakerUSB. Dokończono11wcześniej nieodebranych modułów/łożysk.4rooty/BUS i fabryczne źródło są bajtowo identycznymiBRep wworldframe; po serializacjiMCP pointerIsSame nie wystarczał, użyto SHA256 tych samych geometrii. Nie ponawiano pierwszej bramki ani61starych par.

## Kolejność dwóch osób — ta sama konfiguracja, warunkowa

1. A: zachowanyP00/rewizja/8osi/gwint; B: odłączona bateria, przygotowanie E1/MODULE i końców na stole pozaPETG. Nie rozłączać wirtualnie lutów.
2. Banki/WAGO/pełne końce układać przed wspólnym szkieletem i głośnikiem. A podtrzymuje konstrukcję, B montuje4zachowane zaciski/metal. Rzeczywiste związane zestawy i długości muszą pozwolić na tę kolejność; nie usztywniać ilustracyjnych krzywych.
3. Głośnik na dolnej półce, AMPna wspólnej płycie, pozostałe PCBna właściwych izolujących podporach. Parę głośnika iI2S układać w otwartym kanale PRZED założeniem pionowejPCA/docisków. Nie przeciągać dużych fabrycznych końców przez zamknięty otwór.
4. Górny mikrofon/dotyk zamykać po ułożeniu przewodów i potwierdzeniu pełnychUSB. Przed baterią: rozłączyć istniejącyUSB_AUDIO, zdjąć górną ramkę; następnie rzeczywiste rozłączne końceUSB/zasilaniaBUS i mostekBUS; dopiero odłączona bateria. To plan, nie odebrana trajektoria całego przewodowego zestawu ani szybki serwis.

USB_AUDIO jest OSOBNYM wymaganym przewodem, jegoSKU/długość/matingPi nieodebrane. Nie używać drugi raz dedykowanegoUSB500DelockBUS. Wszystkie4niezależne220/obaMTA, FHACminimum84,5, K1474właściwe de-bity i fabryczne końce pozostają. Actualinstalledlength/fit/cut/slackNULL, bez wymyślonego zapasu/cięcia/przedłużania. Bieżące57części, S0pełne11, S1 i ochrona zachowane.

**Następna decyzja przed detalami:** adekwatne ciągłe pole skrętu/układania z pełnym lokalnym pakowaniem i promieniami względem tackiPi; nie ogłaszaćWholePASS na podstawie wolnych modułów. Nadal potrzebne essential: faktyczny podział i połączenia wspólnej podpory, pełne łączniki/narzędzia/dociskiPCB iretencja banków/baterii, rzeczywiste końce. FIT1rama/masa/ruch,FIT2końce/S0/chłodzenie/stock,FIT3obrysOli/głowaogon nie zostały fizycznie wykonane. BezSTL/slicera/druku/zasilania/zakupu/nowej recenzji.
'''
(P/'ASSEMBLY_PROPOSAL.md').write_bytes(text.encode())
for n in ['day15-audio-build.py','day15-audio-checks.py','day15-audio-package.py']:shutil.copyfile(Path('C:/Users/Sysq/AppData/Local/Temp')/n,P/n)
def pin(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
assert pin(OLD/'manifest.json')['sha256']=='25528ddb41c2b6a1fca378591a1c934bc339276f7d405290b0083bec4b26adfa'
for x in json.loads((OLD/'manifest.json').read_bytes())['files']:assert pin(Path(x['path']))['sha256']==x['sha256']
for folder,want in [(P.parent/'day14-fasttrack-first-fit/fit-kit-ready','addaabc4ed3316366fed61812b85e1805013d67ee67cadf5fb96cb165bde2861')]:
 assert pin(folder/'manifest.json')['sha256']==want
 for x in json.loads((folder/'manifest.json').read_bytes())['files']:assert pin(Path(x['path']))['sha256']==x['sha256']
saved=json.loads((P/'native-save-received.json').read_bytes());assert saved['gui_modified'] is False and saved['objects']==243
with zipfile.ZipFile(P/'audio-layer-proposal.FCStd') as z:assert z.testzip() is None;crc=len(z.namelist())
files=sorted(p for p in P.iterdir() if p.is_file() and p.suffix!='.FCBak' and p.name!='manifest.json')
m=dict(status='ONE_WHOLE_AUDIO_MODULE_COALLOCATION_WITH_ALLOCATED_TURN_HOLD',frozen_utc=datetime.now(timezone.utc).isoformat(),files=[pin(p) for p in files],source_manifest=pin(OLD/'manifest.json'),source21and36_unchanged=True,native=dict(pid=8920,document=saved['document'],objects=243,saved=True,pending=None,unsaved=False,GUI_left_open=True,zip_crc_members=crc),source_contract=plan['source_audio_contract'],source_signal_contract=plan['source_signal_contract'],changed_bought_poses=plan['rigid_changes'],root_BUS_reuse=r['reused'],material_checks=len(r['checks']),numericbounds=len(r['bounds']),previous11_received=r.get('previous11_received'),first_falsifier=r['first_falsifier'],wall_seconds=r['wall_seconds'],cpu_seconds=r['cpu_seconds'],coarse_common_material_coverage=dict(missing=plan['all_new_common_members_missing_mm3'],feed=plan['intended_feed_cut'],uppercap_missing=plan['uppercap_member_missing_mm3']),disposition='Stoponehypothesisatallocatedturnfield/Pitray gap0/common0. No actualwirecontact/allroutesimpossible claim. Needcontinuousoccupiedprofile/roll/R/layadequacy before essentialdetails.',factory_stock=plan['stock'],physical_pass=False,whole_feasible=False,print_release=False,actual_cut_fit_slack=None,review_reopened=False,new_geometry_family_after_falsifier=False)
(P/'manifest.json').write_bytes((json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode())
paths=[str(Path(x['path']).relative_to(ROOT)).replace('\\','/') for x in m['files']]+[str((P/'manifest.json').relative_to(ROOT)).replace('\\','/')];cmd=['git','-c','core.autocrlf=false'];subprocess.run(cmd+['add','--']+paths,cwd=ROOT,check=True);subprocess.run(cmd+['commit','--only','-m','Freeze whole audio layer and allocated turn-bay HOLD','--']+paths,cwd=ROOT,check=True)
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();raw=subprocess.check_output(['git','ls-tree','-r','-z',commit,'--',str(P.relative_to(ROOT)).replace('\\','/')],cwd=ROOT);cnt=0
for rec in raw.split(b'\0'):
 if not rec:continue
 meta,path=rec.split(b'\t',1);blob=subprocess.check_output(['git','cat-file','blob',meta.split()[2].decode()],cwd=ROOT);assert blob==(ROOT/path.decode()).read_bytes();cnt+=1
actual=subprocess.check_output(['git','diff-tree','--no-commit-id','--name-only','-r',commit],cwd=ROOT,text=True).splitlines();assert sorted(actual)==sorted(paths) and cnt==len(paths)
v=dict(commit=commit,exact_files=cnt,manifest_sha256=pin(P/'manifest.json')['sha256'],native_crc_members=crc);Path('C:/Users/Sysq/AppData/Local/Temp/day15-audio-verified.json').write_bytes((json.dumps(v)+'\n').encode());print(json.dumps(v))
