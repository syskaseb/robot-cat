"""Verify the saved native file, prior-source bytes and portable component archive."""
from pathlib import Path
import json,hashlib,zipfile,subprocess,datetime,os
from xml.etree import ElementTree as ET
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core';root=next(q for q in P.parents if (q/'.git').exists());hw=root/'hardware'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return json.loads(p.read_bytes())
def wr(n,v):(P/n).write_bytes((json.dumps(v,ensure_ascii=False,indent=1)+'\n').encode())
def norm(p):p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
nat=P/'whole-cat19F.FCStd';nh=h(nat);parent=E/'whole-cat19E.FCStd'
assert h(parent)=='cef650870eb4fd430b0b9ff2900217996992c553051fe5c5d594a0e2ff38330c'
with zipfile.ZipFile(nat) as z:
    assert z.testzip() is None
    obj=ET.fromstring(z.read('Document.xml')).findall('./ObjectData/Object')
    native=dict(final_sha256=nh,objects=len(obj),native_entries=len(z.namelist()),CRC=True,saved_utc=datetime.datetime.fromtimestamp(nat.stat().st_mtime,datetime.timezone.utc).isoformat())
tested=P/'geometry-tested.FCBak';th=h(tested)
def breps(z):
    a=ET.fromstring(z.read('Document.xml'))
    return {o.get('name'):z.read(r.get('file')) for o in a.findall('./ObjectData/Object') if (r:=o.find('./Properties/Property[@name="Shape"]/Part')) is not None and r.get('file')}
with zipfile.ZipFile(nat) as a,zipfile.ZipFile(tested) as b:
    final_streams=breps(a);tested_streams=breps(b)
    assert final_streams.keys()==tested_streams.keys()
    assert all(final_streams[n]==tested_streams[n] for n in final_streams)
    native.update(geometry_tested_sha256=th,identical_world_BRep_streams=len(final_streams))
sources={}
def pin(p):
    k=p.resolve().relative_to(root).as_posix();sources[k]=h(p);return sources[k]
for n,v in rd(E/'verified-19E.json')['sources'].items():assert pin(root/n)==v
for p in [parent,E/'verified-19E.json',E/'material-index.json',E/'installed-looms.json',E/'installed-bus.json',E/'finished-panels.json',E/'occupied-check-final.json',E/'effectivity.json',hw/'electronics/full-cat/pi-bus-primary-r1/PCB.brep',hw/'electronics/kicad-current/design.json',hw/'electronics/full-cat/closed-prototype-add7-2026-11-16/connections.json',P.parent/'day19-whole-appearance-and-moving-neck-correction/unit-stations.json']:pin(p)
idx=rd(P/'material-index.json');stat=rd(P/'stations.json');checks=rd(P/'occupied-check.json');motion=rd(P/'final-motion.json')
assert all(k in {nh,th} for k in [idx['native_sha256'],stat['native'],checks['sha256'],motion['native_sha256']])
assert len(motion['rows']) and len(checks['rows'])>=89
parts=idx['parts'];assets={};lost=[];mx=0
for q in parts+[idx['off_robot']]:
    if not q.get('stl'):lost.append(q['part']);continue
    f=(P/q['stl']).resolve();assert h(f)==q['sha256'];entry=('sample/' if q is idx['off_robot'] else 'STL/')+f.name
    q['zip_entry']=entry;assets[entry]=f
    if P not in f.parents:pin(f)
    mx=max(mx,max(q['envelope_with_allowance']))
for q in idx['steps']:
    f=(P/q['step']).resolve();assert h(f)==q['sha256'];q['zip_entry']='STEP/'+f.name;assets[q['zip_entry']]=f
    if P not in f.parents:pin(f)
assert mx<=256
idx['geometry_tested_sha256']=th;idx['native_sha256']=nh;wr('material-index.json',idx);wr('native-receipt.json',native)
hits=[dict(field=r['field'],yaw=r['yaw'],pitch=r['pitch'],**v) for r in checks['rows'] for v in r['hits'] if v.get('classification')!='end-face rounding within 0.00002 mm']
mhit=[r for r in motion['rows'] if r['surface_hit']];rigid=[r for r in stat['rows'] if r.get('common_mm3',0)>.00001 or 'error' in r]
e=rd(E/'effectivity.json')
effect=dict(effective_selected=e['effective_selected'],source_19E=h(parent),native=nh,changed_prints=list(rd(P/'new-members.json')),retained_STL=len(parts)-len(rd(P/'new-members.json')),whole_print_GO=False,physical_PASS=False,actual_cut_fit_slack=None,screen_witnesses=hits,rigid_contacts=rigid,motion_contacts=mhit,unexported=lost)
wr('effectivity.json',effect)
mass=idx['geometric_P_g'];count=sum(bool(q.get('stl')) for q in parts);units=sum(q['qty'] for q in parts if q.get('stl'))
readme=f"""# WAVEGO 19F — górna komora przewodów i zamknięcie skrzynki

**Pakiet części do przymiarki. Cały robot pozostaje na HOLD.** Archiwum zawiera {count} modeli STL na {units} sztuk, {len(idx['steps'])} modeli STEP, osobny kupon MTA i instrukcję montażu dla dwóch osób. W indeksie pole `zip_entry` wskazuje plik w paczce. Dawne wydruki wykorzystano według skrótu źródła. Zmienione części sprawdzono po ponownym otwarciu siatki. Największy wymiar w orientacji druku z rezerwą na brim i podpory wynosi {mx:.2f} mm.

[Model FreeCAD](whole-cat19F.FCStd) · [widok całego robota](three-quarter.png) · [wnętrze](interior.png) · [przekroje](critical-sections.png) · [instrukcja montażu](MONTAZ.md) · [indeks części](material-index.json) · [bilans jednostek](unit-plan.json)

**Co zmieniono.** Złącza yaw i ogona mają stałe gniazda w górnej komorze. Fabryczny przewód serwa pitch oraz jego pełne złącze obracają się z członem yaw, a oddzielny JR pitch łączy go z korpusem. Nowy nieruchomy bok osłania ruchomy odbiór obok policzka. BUS z czterema zestawami stali, głośnik i dotyk mają nowe mocowania. Dolne wieko można wsunąć wokół całych przewodów przez dwa otwarte boczne wejścia. Dostęp od góry zamykają dwie demontowalne pokrywy. Geometria drukowanego ogona oraz źródłowa oś Y pozostały w modelu.

**Próby.** W ostatnim zapisanym złożeniu wykonano {len(checks['rows'])} sprawdzeń profili i rozgałęzień oraz {len(stat['rows'])} porównań stacji sztywnych. Pozostałe świadki materiałowe przewodów: {len(hits)}. Dodatnie objętości lub nierozstrzygnięte testy stacji: {len(rigid)}. W {len(motion['rows'])} próbach ruchu osłon, pary i ogona liczba wskazań przecięcia powierzchni wyniosła {len(mhit)}. Dwa surowe wskazania przy wyjściu JR zachowano wraz z podpisaną odległością w układzie obudowy. Pierwsze pola leżą na płaszczyźnie wylotu z dokładnością zapisu 0,00002 mm. Pełny przekrój po wyjściu podlega tej samej kontroli co pozostałe przewody. Próby dyskretne obejmują wybrane pozycje, a fizyczny luz pozostaje do zmierzenia. [Stacje](stations.json) · [zajęte profile](occupied-check.json) · [ruch](final-motion.json)

**Pełne jednostki.** Każdy MG ma 250 mm, każdy JR ma 300 mm i własne rozgałęzienie. DATA500 ma 448 mm pomiędzy dwoma końcami po 26 mm, najmniejszy wewnętrzny promień ścieżki wynosi 30,6 mm. Zapas leży w pojedynczym poziomym nawrocie. Dla 4 ToF rozliczono osobno czerwony 667, czarny 654 oraz żółte 672 i 656 mm. Dostępny metraż szpul jest niezmierzony. Cztery E2 i pięć dzielonych przewodów Pololu zachowują oddzielne limity źródłowe. Skrajna pozycja nie odbiera luzu zza zacisku. Praktyczna długość i możliwość ręcznego ułożenia wymagają próby.

**Otwarte interfejsy.** Na widoku ¾ pod policzkiem i przy dolnym końcu barku wciąż widać fragment wnętrza. Pełne zasłonięcie tego przejścia pozostaje otwarte. Do zamknięcia całego zestawu potrzebny jest odbiór dojść od nowych stacji JR do dziewięciu właściwych punktów na korpusie i doprowadzeń do wszystkich używanych portów przeniesionego BUS; wejścia pozostałych grup, w tym Grove i głośnika, muszą współdzielić ten sam przedział. Przy Pi oba rzeczywiste wtyki USB trzeba osadzić równocześnie, a długość osobnego USB_AUDIO jest nieznana. Weryfikacji wymagają otwarcie pięciu pełnych pokryw FHAC, zakres odpięcia baterii i drzwiczek RR z podłączonymi przewodami, luz pocierania przy ruchu, akustyka i przepływ powietrza z zamkniętymi pokrywami. Cztery MTA0100335 pozostają do zmierzenia na regulowanej półce. Alarm G-Tech pozostaje odłączony do identyfikacji wnęk. Żyły izolowane rozdzielić nad i pod wskazanymi skrzyżowaniami. Cięcie, rzeczywisty luz i fizyczny odbiór pozostają otwarte.

**Materiał.** Pełna objętość wszystkich efektywnych wydruków przy 1,27 g/cm³ odpowiada {mass:.2f} g PETG, zmiana względem 19E wynosi {mass-1198.77:+.2f} g. Cały robot według tego samego scenariusza waży {(1853.4+mass)/1000:.3f}–{(2593.4+mass)/1000:.3f} kg. Wynik z ważenia i odbiór obciążenia nóg pozostają otwarte.
"""
(P/'START_HERE.md').write_bytes(readme.encode())
for p in P.glob('*'):
    if p.suffix.lower() in {'.py','.json','.md'}:norm(p)
for n in ['START_HERE.md','MONTAZ.md','material-index.json','effectivity.json','unit-plan.json','service-lay.json','new-members.json','occupied-check.json','stations.json','final-motion.json','module-binding.json','front.png','side.png','interior.png','three-quarter.png','critical-sections.png','whole-cat19F.FCStd','native-receipt.json']:assets[n]=P/n
for p in [hw/'print-package-2026-11-19/ELECTRICAL_ASSEMBLY.md',hw/'print-package-2026-11-19/SOURCES_ELECTRICAL.json',P.parent/'day19-source-bom-budgets/source-budget.json']:assets[p.name]=p;pin(p)
archive=P/'19F-components-and-assembly.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=2) as z:
    for n,p in assets.items():z.write(p,n)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None and len(z.namelist())==len(assets)
files={p.relative_to(P).as_posix():h(p) for p in sorted(P.rglob('*')) if p.is_file() and p.suffix.lower() in {'.py','.md','.json','.png','.stl','.step','.zip','.fcstd'} and p.name not in ['verified-19F.json','resume-gallery.py']}
wr('verified-19F.json',dict(files=files,sources=sources,native=native,archive_CRC_checked_entries=len(assets)))
print('verified',len(files)+1,len(sources),count,units,len(assets),mass,nh,native['saved_utc'],len(hits),len(rigid),len(mhit))
