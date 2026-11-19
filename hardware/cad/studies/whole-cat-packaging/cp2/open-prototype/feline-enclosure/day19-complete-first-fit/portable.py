from common import *
import re,subprocess,zipfile,datetime
from xml.etree import ElementTree as ET
from collections import Counter
status=rd(P/'decision.json')
parent=H19/'whole-cat19H.FCStd';prior=rd(H19/'verified-19H.json');assert sha(parent)==prior['native']['final_sha256']
with zipfile.ZipFile(native) as z,zipfile.ZipFile(P/'geometry-tested.FCBak') as t:
 def shapes(z):
    root=ET.fromstring(z.read('Document.xml'))
    return {o.get('name'):z.read(a.get('file')) for o in root.findall('./ObjectData/Object') if (a:=o.find('./Properties/Property[@name="Shape"]/Part')) is not None and a.get('file')}
 assert z.testzip() is None;ss=shapes(z);assert ss==shapes(t)
 receipt=dict(final_sha256=sha(native),saved_utc=datetime.datetime.fromtimestamp(native.stat().st_mtime,datetime.timezone.utc).isoformat(),objects=len(ss),native_entries=len(z.namelist()),identical_world_BRep_streams=len(ss),geometry_tested_sha256=sha(P/'geometry-tested.FCBak'))
wr('native-receipt.json',receipt);pins={};assets={}
def pin(p):
 p=p.resolve();k=p.relative_to(R).as_posix();pins[k]=sha(p);return pins[k]
doc_changes={}
for f,h in prior['sources'].items():
 current=pin(R/f)
 if current!=h:
    assert f in {'hardware/print-package-2026-11-19/ELECTRICAL_ASSEMBLY.md','hardware/print-package-2026-11-19/SOURCES_ELECTRICAL.json'},f
    at=lambda commit:hashlib.sha256(subprocess.check_output(['git','show',commit+':'+f],cwd=R)).hexdigest()
    assert at('23f37ea7')==h and at('eb18a705')==current,f
    doc_changes[f]=dict(source_19H=h,accepted_guide=current)
wr('electrical-guide-receipt.json',doc_changes)
for p in [parent,H19/'verified-19H.json',H19/'material-index.json',H19/'whole-termination-plan.json',H19/'stock-and-joint.json',H19/'final-motion.json',H19/'anchor-seats.json',E/'fit-out.py',O/'day19-common-floor-and-bundle-assembly/anchor-seats.json',O/'day19-source-bom-budgets/source-budget.json']:
 if p.is_file():pin(p)
idx=rd(P/'material-index.json');parts=idx['parts'];assert len(set(q['part'] for q in parts))==len(parts) and len(parts)==50
for q in [*parts,idx['off_robot'],*idx['steps']]:
 kind='step' if q in idx['steps'] else 'stl';p=(P/q[kind]).resolve();assert sha(p)==q['sha256']
 k=('STEP/' if kind=='step' else 'sample/' if q is idx['off_robot'] else 'STL/')+p.name
 assert k not in assets;assets[k]=p;q['zip_entry']=k
 if P not in p.parents:pin(p)
for q in parts:
 q.pop('installed_hazards',None);q.pop('assembly_status',None)
 n=q['part']
 if not q.get('hardware_use'):
    q['hardware_use']=('fabryczny zespół nogi WAVEGO, zachować właściwy komplet śrub/dystansów przy danej osi' if n in ['WConnector','Bracket_v','LegLink','LegSpacer'] else 'zachowana część zespołu '+n.split('_')[0]+'; orczyk, sworzeń, bieżnie, dystanse i pełna stal zgodnie z montażem natywnym')
assert all(max(q['envelope_with_allowance'])<=256 for q in parts);qty=sum(q['qty'] for q in parts);m=idx['geometric_P_g'];mx=max(max(q['envelope_with_allowance']) for q in parts)
idx.update(native_sha256=receipt['final_sha256'],whole_print_kit=status['digital_first_fit'],physical_PASS=False,actual_cut_fit_slack=None);wr('material-index.json',idx)
# Portable index paths resolve inside the extracted archive, while repository paths remain live outside.
portable_idx=json.loads(json.dumps(idx))
for q in [*portable_idx['parts'],portable_idx['off_robot'],*portable_idx['steps']]:
 q['step' if 'step' in q else 'stl']=q['zip_entry']
docs=H/'print-package-2026-11-19';elect='hardware/print-package-2026-11-19/ELECTRICAL_ASSEMBLY.md'
source=subprocess.check_output(['git','show','eb18a705:'+elect],cwd=R)
s=source.decode();ch=s.split('## Mapa i identyfikacja',1)[1].split('## Otwarte poprawki projektu',1)[0]
s='# Montaż elektryczny bez zasilania — 19I\n\nOdłączyć główne złącze baterii, balanser i zewnętrzne USB. Montaż mechaniczny i obowiązujące położenia podaje [instrukcja 19I](MONTAZ.md). Rozdziały elektryczne opracowano z odebranej wersji eb18a705.\n\n## Mapa i identyfikacja'+ch
def rewrite(m):
 link=m[1]
 if not link.startswith('..'):return m[0]
 p=(docs/link).resolve()
 if p.parent==E and p.name in ['MONTAZ.md','material-index.json']:return ']('+p.name+')'
 if p==H19/'whole-termination-plan.json':return '](whole-termination-plan.json)'
 assert p.is_file();k='source/'+p.name
 if k in assets:assert sha(assets[k])==sha(p)
 assets[k]=p;pin(p);return ']('+k+')'
s=re.sub(r'\]\(([^)]+)\)',rewrite,s).replace('[montaż 19E]','[montaż 19I]')
(P/'ELECTRICAL_ASSEMBLY.md').write_bytes(s.encode());assets['ELECTRICAL_ASSEMBLY.md']=P/'ELECTRICAL_ASSEMBLY.md'
for f in ['MATERIALY.csv','POLACZENIA.csv']:
 p=H/'electronics/full-cat/closed-prototype-add7-2026-11-16/assembly-reference'/f;assets['source/'+f]=p;pin(p)
for f in ['leg-mouths.json','leg-delta.json','stock-and-joint.json','service-final.json']:
 p=H19/f;assets['reference-19H/'+f]=p;pin(p)
budget=O/'day19-source-bom-budgets/source-budget.json';assets['source/source-budget.json']=budget;pin(budget)
# Include an explicit CSV to read at the printer without opening the CAD or JSON.
import csv
with (P/'PRINT.csv').open('w',encoding='utf-8-sig',newline='') as h:
 w=csv.writer(h,lineterminator='\n');w.writerow(['STL w ZIP','szt.','orientacja','X z rezerwa','Y z rezerwa','Z z rezerwa','mocowanie'])
 for q in parts:w.writerow([q['zip_entry'],q['qty'],q['print_pose'],*[round(x,2) for x in q['envelope_with_allowance']],q['hardware_use']])
msg=f"""# WAVEGO 19I — przymiarka i montaż

**{status['label_pl']}** {status['decision_pl']}

[Model FreeCAD](whole-cat19I.FCStd) · [montaż dwóch osób](MONTAZ.md) · [elektryka](ELECTRICAL_ASSEMBLY.md) · [lista wydruków](PRINT.csv) · [pełne połączenia](whole-termination-plan.json) · [zakres odbioru](decision.json)

Zestaw zawiera {len(parts)} typów STL na {qty} części robota. Pięć identycznych obejm FHAC ma jeden plik. Dwadzieścia części nóg pochodzi z czterech zachowanych plików. Poza robotem jest jeden opcjonalny kupon MTA. Ustawienia względem stołu są zapisane w STL. Maksymalny wymiar wraz z rezerwą na brim i podpory wynosi {mx:.2f} mm przy polu 256 mm. Dostępne są także {len(idx['steps'])} pliki STEP.

Dla objętości pełnego materiału model daje {m:.2f} g PETG. Z dotychczasowym zakresem masy wyposażenia odpowiada to {(m+1853.4)/1000:.3f}–{(m+2593.4)/1000:.3f} kg dla kompletnego robota. Masę po wydruku, nośność nóg oraz ruch pod obciążeniem ustala się fizycznie.

[Widok całego robota](three-quarter.png) · [przód](front.png) · [bok](side.png) · [wnętrze](interior.png) · [przekroje](critical-sections.png)

| Sprawdzenie w zapisanym modelu | Wynik dla przymiarki |
|---|---|
| Osiem oparć na bazie | Powierzchnie kontaktu od {min(q['contact_patch_mm2'] for q in rd(P/'final-anchor-seats.json')['pads']):.2f} do {max(q['contact_patch_mm2'] for q in rd(P/'final-anchor-seats.json')['pads']):.2f} mm². Dojście wkrętaka przy pustych podstawach i pełnym osprzęcie gimbala opisuje [pomiar](anchor-access.json). |
| G1, P_FRONT i F_PWM | Pięć zajętych wejść G1 oraz trzy czynne dojścia P_FRONT. Przy P_FRONT pozostaje 21,5 mm długości dojścia Ø4,7 mm. Półka F_PWM zachowuje oba otwory mocowania. |
| Pakiet i XT60 | Dla W075 przewidziano 45 mm dojścia i 5 mm zakończenia. Obie żyły dostarczonego pakietu potrzebują w modelu po około 208 mm przed uwzględnieniem rzeczywistych końców. Najmniejszy odstęp od przydzielonych grup przy rozpinaniu w pozycji neutralnej wynosi {status['neutral_14mm_withdrawal_min_clearance_to_allocated_groups']:.2f} mm. |
| W041 przy przednim banku | Fabryczna strona ma przydzielony dostęp do górnej złączki, a osobny przewód do P_FRONT.2 ma roboczy promień wewnętrzny co najmniej 25,5 mm. Długości i metraż są rozpisane oddzielnie dla każdej jednostki w [bilansie](source-units.json). |

W przedniej ramie pozostają cztery kotwy i pełny gimbal. Tylna podstawa niesie cztery kolejne kotwy i ruchomy ogon. Pięć projektowych obrysów FHAC ma oparcie w otwartych gniazdach. Oba poziomy G1/P_AUX są dostępne przy podpartym przodzie przed zamknięciem. Przy czynności wymiany pakietu głowa jest ustawiona prosto, a obsługa XT60 odbywa się po otwarciu pokryw. Odczepy R7–R9 wymagają przymiarki na dostarczonym JR przed przygotowaniem przewodów.

Ruch nóg w głębokich pozycjach źródłowych ma status planistyczny. Dane obejmują wcześniejszy ujemny wynik i lokalny pomiar zmienionego nadkola. Rzeczywiste ograniczniki przegubów, fizyczne dopasowanie opraw MTA, długości kabli dostarczonego pakietu oraz USB_AUDIO, chłodzenie, nadlewy USB i mapa wnęk G-Tech wymagają pomiaru. Alarm pozostawić zamontowany i odłączony. Zmierzony luz i cięcia pozostają nieustalone.
"""
(P/'START_HERE.md').write_bytes(msg.encode())
for n in ['START_HERE.md','MONTAZ.md','decision.json','PRINT.csv','native-receipt.json','whole-termination-plan.json','lower-unit-lengths.json','tap-carriers.json','tap-sections.json','installed-rests.json','battery-jackets.json','seated-units.json','load-and-seats.json','terminal-bearing.json','fl-region.json','neck-local-fit.json','frame-mesh-proof.json','critical-sections.png','front.png','side.png','opposite-side.png','three-quarter.png','interior.png',native.name]:assets[n]=P/n
for n in ['anchor-access.json','final-anchor-seats.json','rear-cap-bearing.json','front-mouths.json','fl-hand-check.json','affected-bearer.json','battery-lower-fit.json','source-units.json','distribution-shelf.json','two-plug-seats.json']:assets[n]=P/n
for p in P.glob('*'):
 if p.suffix.lower() in {'.py','.json','.md'}:p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
archive=P/'19I-WAVEGO-first-fit.zip'
for n in ['export-identity.json','W075-seated.json','gimbal-steel-access.json']:assets[n]=P/n
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=2) as z:
 for k,p in assets.items():z.write(p,k)
 z.writestr('material-index.json',json.dumps(portable_idx,indent=1,ensure_ascii=False))
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None;entries=len(z.namelist());assert entries==len(assets)+1
 for q in portable_idx['parts']:assert hashlib.sha256(z.read(q['stl'])).hexdigest()==q['sha256']
for p in P.glob('*'):
 if p.suffix.lower() in {'.py','.json','.md'}:p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
files={p.relative_to(P).as_posix():sha(p) for p in sorted(P.rglob('*')) if p.is_file() and p.suffix.lower() in {'.py','.md','.json','.png','.stl','.step','.zip','.fcstd','.csv'} and p.name!='verified-19I.json'}
wr('verified-19I.json',dict(files=files,sources=pins,native=receipt,archive_CRC_checked_entries=entries,electrical_guide_commit='eb18a7057e39e8c5546a3015bbbcd50d1c5331b7',electrical_source_sha256=hashlib.sha256(source).hexdigest()))
print(receipt,qty,len(files),len(pins),entries,sha(archive))
