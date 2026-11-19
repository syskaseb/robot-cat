"""Bind the final save, collect individual components and verify a portable dry-fit archive."""
from pathlib import Path
import json,hashlib,zipfile,os,datetime
from xml.etree import ElementTree as E
P=Path(__file__).parent;root=next(q for q in P.parents if (q/'.git').exists());D=P.parent/'day19-whole-appearance-and-moving-neck-correction';A=P.parent/'day19-whole-closed-print-package'
def read(n):return json.loads((P/n).read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,data):(P/n).write_bytes((json.dumps(data,indent=1,ensure_ascii=False)+'\n').encode('utf8'))
native=P/'whole-cat19E.FCStd';proven=P/'seated-native.FCBak';h=sha(native)
with zipfile.ZipFile(native) as z,zipfile.ZipFile(proven) as initial:
    assert z.testzip() is None and initial.testzip() is None
    a=E.fromstring(z.read('Document.xml'));b=E.fromstring(initial.read('Document.xml'))
    def refs(d):return {o.get('name'):s.get('file') for o in d.findall('./ObjectData/Object') if (s:=o.find('./Properties/Property[@name="Shape"]/Part')) is not None and s.get('file')}
    f,g=refs(a),refs(b);assert f.keys()==g.keys()
    diff=[n for n in f if z.read(f[n])!=initial.read(g[n])]
    assert not diff,diff
    coh=dict(final_sha256=h,before_final_view_sha256=sha(proven),objects=len(a.findall('./ObjectData/Object')),shape_streams=len(f),different_shape_streams=diff,native_entries=len(z.namelist()),CRC=True,saved_utc=datetime.datetime.fromtimestamp(native.stat().st_mtime,datetime.timezone.utc).isoformat())
write('native-receipt.json',coh)
idx=read('material-index.json')
assert len(idx['parts'])==48 and len(idx['steps'])==3 and all(r.get('stl') for r in idx['parts'])
assert idx['native_sha256'] in {h,sha(proven),'540429f2cc96480756c7387e7a7f8786524c55b7f90c4a7e98870a962ae6cced'},idx['native_sha256']
idx['native_sha256']=h
sources={}
def pin(p):
    p=p.resolve();sources[p.relative_to(root).as_posix()]=sha(p);return p
assets={}
for r in idx['parts']+[idx['off_robot']]:
    p=(P/r['stl']).resolve();assert sha(p)==r['sha256']
    if P not in p.parents:pin(p)
    name=('sample/' if not r['qty'] else 'STL/')+p.name;r['zip_entry']=name;assets[name]=p
for r in idx['steps']:assets['STEP/'+(P/r['step']).name]=P/r['step']
write('material-index.json',idx)
budget=pin(P.parent/'day19-source-bom-budgets/source-budget.json')
for r in json.loads(budget.read_bytes())['sources'].values():
    p=pin(root/r['path']);assert sources[r['path']]==r['sha256']
for p in [D/'whole-cat19D.FCStd',D/'verified-19D.json',D/'material-index.json',D/'face-fragments.json',D/'whole-lay.json',A/'actor-effectivity.json',P.parent/'day19-common-floor-and-bundle-assembly/anchor-seats.json',root/'hardware/electronics/full-cat/pi-bus-primary-r1/PCB.brep',root/'hardware/electronics/full-cat/pi-bus-primary-r1/Part__Feature.brep',root/'hardware/electronics/full-cat/pi-bus-primary-r1/catalog.json',root/'hardware/reference/head-electronics-2026-09-22/ReSpeakerLitev1.1.step']:pin(p)
guide=pin(root/'hardware/print-package-2026-11-19/ELECTRICAL_ASSEMBLY.md');elect=pin(guide.parent/'SOURCES_ELECTRICAL.json')
r=read('final-fit.json');assert 'battery_extraction' in r and len(r['rows'])>=23
m=idx['geometric_P_g'];tot=idx['known_robot_scenario_g'];faces=read('occupied-check-final.json')
hits=sorted({row['field']+' / '+q['part'] for row in faces['rows'] for q in row['hits']})
status=dict(effective_selected=json.loads(budget.read_bytes())['coverage'],source_19D_sha256=sha(D/'whole-cat19D.FCStd'),native_sha256=h,printed_dynamic_tail='E19_KeyedTail',tail_stock='separate fixed-case MG250 allocation hits operator/fuse bank; JR300 independent, tray R22.25',head_ranges_deg=[20,10],tail_range_Y_deg=15,factory_fields_failing=hits,fit_cut_slack=None,physical_PASS=False,whole_print_GO=False,retired_prints=idx['retired'],new_prints=[r['part'] for r in idx['parts'] if r['part'].startswith('E19_')])
write('effectivity.json',status)
n=len(idx['parts']);units=sum(q['qty'] for q in idx['parts']);mx=max(max(q['envelope_with_allowance']) for q in idx['parts'])
s=f"""# WAVEGO 19E — skrzynkowy korpus, wspólny nośnik i ogon na osi Y

**Wykonano model i zestaw komponentów. Cały prototyp pozostaje na HOLD.** Indeks zawiera {n} indywidualnych modeli STL na {units} sztuk, trzy STEP oraz odrębny kupon podparcia próbki MTA. W paczce przenośnej pole `zip_entry` wskazuje plik w archiwum. W repozytorium pole `stl` prowadzi do weryfikowanego pliku, w tym czterech źródłowych modeli na 20 części nóg. Maksymalny wymiar w zapisanej orientacji z uwzględnionym zapasem wynosi {mx:.2f} mm. Fizyczny wydruk i dopasowanie pozostają do sprawdzenia.

[FreeCAD](whole-cat19E.FCStd) · [widok ¾](three-quarter.png) · [bok](side.png) · [przód](front.png) · [wnętrze](interior.png) · [przekroje](critical-sections.png) · [montaż dla dwóch osób](MONTAZ.md) · [indeks](material-index.json)

**Wynik konstrukcyjny.** Dwie połówki skrzynki są integralne z niezależnymi czterokotwowymi podłogami. Są dwa zdejmowane wieka, cztery osobne banki WAGO, boczne gniazdo kompletnego S0, panel S1, odbiór złącza yaw i boczne drzwiczki akumulatora z dwiema oprawami RR. Płytka BUS i pełne porty pochodzą z końcowego złożenia dostawcy; 484 bryły źródłowego ReSpeaker v1.1 ustawiono na dwóch otworach. Natywny model, oparcia i sprężyste chwyty wymagają przymiarki do rzeczywistych obudów. Przednia osłona zachowuje dostęp do mechanizmu. Przez styk pod głową nadal miejscami widać wnętrze.

**Próby rozstrzygające.** Pierwszy skrzynkowy układ usunął kolizję górnej osłony yaw z podłogą w trzech różnych ustawieniach yaw; pitch nie zmienia wzajemnej pozy tych dwóch członów. Pełna para złączy yaw ma własny przebadany przydział. Widoczny ogon ma drukowany pusty korzeń i grubszą końcówkę oraz źródłowy czop, róg, łożysko i pełny sworzeń. Pierwszy test dał 0 mm³ ogona z tylnym wiekiem i podłogą przy −15°, 0°, +15°. Nie wykonano pomiaru ciągłego ruchu. Ostatnie poprawki oparto o przecięcia drzwiczek z obydwiema połówkami. Końcowe gniazda mają 0 mm³ wspólnego materiału z drzwiczkami i 0 mm³ korpusu S0 z tylną podstawą. Pełny prostokąt wysunięcia ogniwa do +Y sprawdzono przy zdjętych paskach i odłożonych złączkach RR. [Pierwsze próby](changed-fit-initial.json) · [przekrój i kolizje drzwi przed zmianą](first-door-fit.json) · [ostatni test](final-fit.json)

**Pozostała wspólna warstwa przewodów.** W górnej stacji pitch pełne MG250 i niektóre żyły ToF trafiają w stałą podporę lub ruchome osłony. MG250 yaw przecina rzeczywistą płytkę Pi; powrót fabryczny ogona trafia w S1 i tylną obsadę. Dolny nawrót DATA500 przecina akumulator, MAIN i F_PI. Bilans długości jest zamknięty arytmetycznie. Tych przebiegów nie można użyć do wiązania ani cięcia wiązki. W kolejnym wspólnym układzie potrzebny jest otwarty dostępny przedział serw i USB z pełnymi parami końców poza płytkami, baterią i połączoną stacją operatora. Trasy 4×E2, oddzielnego USB_AUDIO i POWER mają przydziały do przymiarki. Nadal potrzebne są pokrywy FHAC w otwarciu, rzeczywiste pełne wtyki USB przy Pi, luźny zapas podczas wyjmowania baterii, dopasowanie czterech MTA0100335, identyfikacja G-Tech, chłodzenie oraz dostęp optyczny i akustyczny po zamknięciu. [Zajęte regiony](installed-looms.json) · [świadkowie kontaktów](occupied-check-final.json)

**Materiał.** Suma efektywnych wydruków przy 1,27 g/cm³ wynosi {m:.2f} g. Zmiana względem indeksu 19D wynosi {m-923.52:+.2f} g. Zakres scenariusza całego robota wynosi {tot[0]/1000:.3f}–{tot[1]/1000:.3f} kg przed dalszymi zmianami. Podwozie i rozdział elektryczny są uwzględnione raz. Masa zmierzona i potwierdzenie chodu pozostają otwarte.
"""
(P/'START_HERE.md').write_bytes(s.encode('utf8'))
for n in ['START_HERE.md','MONTAZ.md','material-index.json','whole-cat19E.FCStd','front.png','side.png','three-quarter.png','interior.png','critical-sections.png','installed-looms.json','occupied-check-final.json','final-fit.json','changed-fit-initial.json','first-door-fit.json','effectivity.json','native-receipt.json']:assets[n]=P/n
assets.update({'ELECTRICAL_ASSEMBLY.md':guide,'SOURCES_ELECTRICAL.json':elect,'source-budget.json':budget})
if (P/'final-motion.json').exists():
    assets['final-motion.json']=P/'final-motion.json'
    report=read('final-motion.json')
    with (P/'START_HERE.md').open('a',encoding='utf8',newline='\n') as f:
        f.write('\nKońcowa próba powierzchni siatek obejmuje '+str(len(report['rows']))+' par/ustawień. Liczba wskazanych przecięć: '+str(sum(r['surface_hit'] for r in report['rows']))+'. [Wyniki próby yaw i ogona](final-motion.json)\n')
archive=P/'19E-components-and-assembly.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=2) as z:
    for n,p in assets.items():z.write(p,n)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None and len(z.namelist())==len(assets)
files=[p for p in P.rglob('*') if p.is_file() and (p.suffix.lower() in {'.py','.json','.md','.png','.stl','.step','.brp','.zip','.fcstd'}) and p.name!='verified-19E.json']
write('verified-19E.json',dict(files={p.relative_to(P).as_posix():sha(p) for p in sorted(files)},sources=sources,native=coh,archive_CRC_checked_entries=len(assets)))
print(len(files)+1,len(sources),coh,m,units)
