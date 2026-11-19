from common import *
import zipfile,datetime
from xml.etree import ElementTree as ET
from collections import Counter
parent=G/'whole-cat19G.FCStd';assert sha(parent)=='cdfce6210f1e989c03d550bf7c9bb48f5d1ad58e3db0c66fe4fcab0a98d8a168'
def streams(z):
 doc=ET.fromstring(z.read('Document.xml'));return {o.get('name'):z.read(r.get('file')) for o in doc.findall('./ObjectData/Object') if (r:=o.find('./Properties/Property[@name="Shape"]/Part')) is not None and r.get('file')}
test=P/'geometry-tested.FCBak'
with zipfile.ZipFile(native) as z,zipfile.ZipFile(test) as t:
 assert z.testzip() is None;nc=len(z.namelist());a,b=streams(z),streams(t);assert a==b;count=len(a)
receipt=dict(final_sha256=sha(native),saved_utc=datetime.datetime.fromtimestamp(native.stat().st_mtime,datetime.timezone.utc).isoformat(),objects=count,native_entries=nc,identical_world_BRep_streams=count,geometry_tested_sha256=sha(test));wr('native-receipt.json',receipt)
pins={}
def pin(p):
 p=p.resolve();pins[p.relative_to(R).as_posix()]=sha(p);return pins[p.relative_to(R).as_posix()]
prior=rd(G/'verified-19G.json')
for path,h in prior['sources'].items():assert pin(R/path)==h,path
for p in [parent,G/'verified-19G.json',G/'material-index.json',G/'whole-termination-plan.json',G/'final-profiles.json',G/'side-clearance.json',F/'whole-cat19F.FCStd',O/'day07-USB-three-current-valid-source-gates.recipe.py',O/'day19-common-floor-and-bundle-assembly/floor19b.py',G/'mic-port.json']:pin(p)
assets={};idx=rd(P/'material-index.json');parts=idx['parts'];assert len(parts)==49 and all(q.get('stl') for q in parts)
for q in parts+[idx['off_robot']]:
 p=(P/q['stl']).resolve();assert sha(p)==q['sha256'];k=('sample/' if q is idx['off_robot'] else 'STL/')+p.name;assets[k]=p;q['zip_entry']=k
 if P not in p.parents:pin(p)
for q in idx['steps']:
 p=(P/q['step']).resolve();assert sha(p)==q['sha256'];k='STEP/'+p.name;assets[k]=p;q['zip_entry']=k
 if P not in p.parents:pin(p)
mx=max(max(q['envelope_with_allowance']) for q in parts);assert mx<=256
for q in parts:
 q.pop('installed_hazards',None);q.pop('assembly_status',None)
 if q['part'] in ['H19_FrontFrame','E19_RearBase']:q['assembly_status']='HOLD: FHAC case allocations and access; G1.2 wire entry on front frame'
idx.update(native_sha256=receipt['final_sha256'],source_19G_sha256=sha(parent),whole_print_kit=False,actual_cut_fit_slack=None);wr('material-index.json',idx)
def load(n):return rd(P/n)
checks=load('final-profiles.json')['rows'];st=load('static-stations.json')['rows'];j=load('stock-and-joint.json')['rows'];motion=load('final-motion.json')['rows'];ba=load('battery-check.json')['rows'];svc=load('service-final.json');lg=load('leg-delta.json');fuses=load('five-fuse-service.json');unit=load('whole-termination-plan.json')['units']
con={k:[(q['neighbour'],round(q['common_mm3'],3)) for q in v['seated'] if q.get('common_mm3',0)>.001] for k,v in fuses.items()}
eff=dict(selected=rd(G/'effectivity.json')['source_coverage'],replaced=['E19_ForeBase','E19_FrontShroud'],front='H19_FrontFrame',changed_prints=list(load('new-members.json')),static_tests=len(st),static_positive=[r for r in st if r.get('common_mm3',0)>.001 or 'error' in r],named_profiles=len(checks),profile_witness=[r for r in checks if r['hits']],joint_samples=len(j),joint_witness=[r for r in j if r['hits']],motion_cases=len(motion),motion_witness=[r for r in motion if r['surface_hit']],leg_candidates=lg['candidates'],leg_contacts=lg['material_intersections'],battery_service=svc,battery_wire_witness=[r for r in ba if r['hits']],FHAC_seated_fields=con,physical_PASS=False,actual_cut_fit_slack=None,whole_GO=False)
wr('effectivity.json',eff)
mass=idx['geometric_P_g'];bus=unit['BUS900']['required_axial_length'];power=unit['K1474'];ld=load('battery-leads.json')
summary=f"""# WAVEGO 19H — przednia rama i wspólny kanał przewodów

**HOLD dla całego montażu.** ZIP zawiera {len(parts)} modeli STL na {sum(q['qty'] for q in parts)} sztuk, {len(idx['steps'])} plików STEP i osobny kupon MTA. Cztery zmienione części wyeksportowano i ponownie otwarto. Największy wymiar z rezerwą na brim i podpory wynosi {mx:.2f} mm. Model pełnego materiału daje {mass:.2f} g PETG oraz {(1853.4+mass)/1000:.3f}–{(2593.4+mass)/1000:.3f} kg dla całego robota.

[Model FreeCAD](whole-cat19H.FCStd) · [widok robota](three-quarter.png) · [wnętrze](interior.png) · [przekroje](critical-sections.png) · [montaż dla dwóch osób](MONTAZ.md) · [indeks wydruków](material-index.json)

Zintegrowana rama zastępuje osobną przednią podłogę i nieruchomą osłonę. Obie pokrywy wewnętrzne są zdejmowane. Wstępne długie rozcięcie odłączyło kilka podpór; ostateczny wspólny otwór przy podziale zachowuje mocowania i dojście do końcówek. Prześwit przy żuchwie pozostaje widoczny na widoku ¾. W odniesieniu do usuniętych trzech dolnych ścian sprawdzono {lg['candidates']} lokalne przypadki z 49 zachowanych póz nóg. Liczba przecięć z nowym materiałem wyniosła {len(lg['material_intersections'])}. Podparcie pełnego modułu mikrofonu i obu kompletów stalowych zmieniono w obrębie wieka.

| Zakończenia | Wynik modelu |
|---|---|
| Dziewięć odgałęzień JR | Wspólne przejście 3 × 3 między pokładami. Osobne grupy do FHAC, G i lutowanej E1. Powrót PWM omija podporę ogona. |
| BUS | D_FL obrócony jako całe pięć torów. Dłuższa z dwóch żył pojedynczego kabla 900 mm potrzebuje {bus} mm z końcami i rezerwą. |
| MAIN i K1474 | Obie żyły wyjściowe {power['power_pair_kept']} mm. Wejście W078 potrzebuje {power['input_required']} z osobnych 210 mm tej samej jednostki. |
| Pi i audio | Właściwe projektowe nadlewy DATA i AUDIO mają 4,23 mm odstępu poprzecznego w dwóch stosach. Wcześniejszy obszar 26 × 26 × 24 mm obejmował obsługę. Na wzmacniaczu X1.1 to VO−, X1.2 to VO+. Podstawą są dwa otwory źródła 3006 zgodne z rozstawem 12,7 mm; poziom wejścia przewodu i końcówki głośnika wymagają sprawdzenia. |
| Bateria | Pakiet wysuwa się po rozłączeniu. Połówka przy pakiecie może przemieścić się w polu modelu o 14 mm. Odcinek W075 z końcem zajmuje {ld['W075_with_5_termination_mm']:.2f} z 50 mm. Swobodny górny odcinek zachowuje {ld['battery_return'][0]['developed_mm']:.2f} mm w obu położeniach. |
| Nogi | Cztery zaokrąglone przejścia 23,5 × 10,5 mm; pełne wtyczki przeprowadzać kolejno. Sprawdzić rzeczywiste końce i zapasy od wyjść do poruszających się napędów. |

**Odbiór.** Spośród {len(checks)} wybranych nowych profili wiązek wskazania materiału wystąpiły w {len(eff['profile_witness'])} przypadkach. Oddzielnie sprawdzono {len(j)} położeń i profili źródłowych oraz {len(motion)} par ruchomych sztywnych. Łączna liczba wskazań w tych dwóch testach wyniosła {len(eff['joint_witness'])+len(eff['motion_witness'])}. Źródłowa mapa zachowuje 134 + 26 połączeń. Rzeczywiste cięcia, masę i luz ustala się podczas przymiarki.

**Pozostałe blokady.** Łuk serwisowy baterii i dziewięć odgałęzień JR współdzielą okno. Najbliższe osie izolowanych przewodów w przyjętym ułożeniu dzieli 0,09 mm przy sumie promieni 3,45 mm. Wymaga to rozdzielenia dwóch warstw i zachowania 14 mm ruchu przy rozpinaniu. Fizyczna swoboda w tym oknie pozostaje otwarta. Wyjście W001 przy G1.2 trafia w przednią ramę. Dwie próby odrzuciły dojście do tej samej strony złączki. Kolejna korekta wymaga wspólnego ustawienia całego banku G1 i jego dojść. W przyjętych polach montażowych 51 × 22 × 20,25 mm cztery stanowiska FHAC mają dodatnią wspólną objętość z drukami: {con}. Są to pola źródłowe; fizyczny profil uchwytu i klapki pozostaje do ustalenia. Zdjęcie Pi i banku daje dostęp, lecz samo nie potwierdza osadzenia tych czterech jednostek. F_HP wymaga odsunięcia F0 przed otwarciem w rozpatrywanym kierunku. Oddzielnie pozostają rzeczywiste kontakty R7–R9, dojście do terminali głośnika i części gniazd na modułach, skok rozłączenia i długość przewodu dostarczonej baterii, nadlewy obu USB i długość USB_AUDIO, cztery pełne MTA0100335, chłodzenie i mapa wnęk G-Tech. Wartości złożenia fizycznego pozostają niezmierzone.

Źródłem położenia i biegunowości X1 jest projekt płytki mono dla wybranego modułu 3006. [Pliki producenta](https://github.com/adafruit/Adafruit-MAX98357-I2S-Amp-Breakout)

[Wskazania i zakres](effectivity.json) · [połączenia i jednostki](whole-termination-plan.json) · [przestrzeń rozłączenia baterii](service-final.json) · [obudowy FHAC](five-fuse-service.json) · [parametry siatki ramy](frame-mesh-proof.json)
"""
(P/'START_HERE.md').write_bytes(summary.encode())
for p in P.glob('*'):
 if p.suffix.lower() in {'.py','.json','.md'}:p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
for name in ['START_HERE.md','MONTAZ.md','material-index.json','effectivity.json','whole-termination-plan.json','shared-lay.json','leg-mouths.json','service-final.json','battery-check.json','split-occupancy.json','five-fuse-service.json','final-profiles.json','stock-and-joint.json','final-motion.json','leg-delta.json','frame-mesh-proof.json','critical-sections.png','front.png','side.png','three-quarter.png','interior.png','native-receipt.json',native.name]:assets[name]=P/name
for name in ['ELECTRICAL_ASSEMBLY.md','SOURCES_ELECTRICAL.json']:
 p=H/'print-package-2026-11-19'/name;assets[name]=p;pin(p)
for name in ['POLACZENIA.csv','MATERIALY.csv']:
 p=H/'electronics/full-cat/closed-prototype-add7-2026-11-16/assembly-reference'/name;assets[name]=p;pin(p)
archive=P/'19H-components-and-assembly.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=2) as z:
 for k,p in assets.items():z.write(p,k)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None and len(z.namelist())==len(assets)
files={p.relative_to(P).as_posix():sha(p) for p in sorted(P.rglob('*')) if p.is_file() and p.suffix.lower() in {'.py','.md','.json','.png','.stl','.step','.zip','.fcstd'} and p.name!='verified-19H.json'}
wr('verified-19H.json',dict(files=files,sources=pins,native=receipt,archive_CRC_checked_entries=len(assets)));print(count,nc,len(files)+1,len(pins),len(assets),receipt)
