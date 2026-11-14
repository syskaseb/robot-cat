from pathlib import Path
import json,csv,io,hashlib,shutil,struct,collections,math
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit/fit-kit-ready');OLD=P.parent/'fit-kit-final';FROZEN=P.parent/'foundation-fit-kit'
parts=json.loads((P/'parts.json').read_bytes());checks=[]
for p in parts:
 for key in ['notes','description']:
  if key in p:p[key]=p[key].replace('Four2mm bosses yield completeM3x55 stack.','Four1mm bosses: fullM3x50 stack48.9, nut2.4/washer0.5, tip1.1, deckseatweb2.').replace('M3x55','M3x50')
 if p['name']=='P03_rear_deck_integrated_load_yoke':p['notes']+=' Actualunderside9mm loadingport99,15; two sideentriesoutsideY-82 and one undersideport164,27; preload beforebaseassembly.'
 raw=(P/p['stl']).read_bytes();num=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*num;edges=collections.Counter();lo=[math.inf]*3;hi=[-math.inf]*3;volume=0
 for i in range(num):
  t=struct.unpack_from('<12fH',raw,84+50*i);vs=[t[3:6],t[6:9],t[9:12]];keys=[tuple(round(v,5) for v in q) for q in vs]
  for q in vs:
   for k in range(3):lo[k]=min(lo[k],q[k]);hi[k]=max(hi[k],q[k])
  for k in range(3):edges[tuple(sorted((keys[k],keys[(k+1)%3])))]+=1
  a,b,c=vs;volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
 assert all(x==2 for x in edges.values()) and volume>0 and min(lo)>-1e-4 and max(b-a for a,b in zip(lo,hi))<256
 if p['name'] not in ['P03_rear_deck_integrated_load_yoke','P06_S0_shared_panel']:assert raw==(FROZEN/p['stl']).read_bytes()
 if p['name']=='P06_S0_shared_panel':assert raw==(OLD/p['stl']).read_bytes()
 checks.append(dict(name=p['name'],quantity=p['quantity'],stl=p['stl'],sha256=hashlib.sha256(raw).hexdigest(),triangles=num,bounds_mm=[lo,hi],volume_mm3=volume,closed_edges2=True,localXYZ_Z0=True,under256=True,unchanged_foundation=p['name'] not in ['P03_rear_deck_integrated_load_yoke','P06_S0_shared_panel']))
(P/'parts.json').write_bytes((json.dumps(parts,ensure_ascii=False,indent=2)+'\n').encode());(P/'STL-integrity.json').write_bytes((json.dumps(checks,indent=2)+'\n').encode())
def csvwrite(name,fields,rows):
 s=io.StringIO(newline='');w=csv.writer(s,lineterminator='\n');w.writerow(fields);w.writerows(rows);(P/name).write_bytes(s.getvalue().encode())
csvwrite('print-parts.csv',['part','quantity','stl','size_mm','orientation','status'],[(x['name'],x['quantity'],x['stl'],'x'.join(str(round(b-a,3)) for a,b in zip(*x['bounds_mm'])),'flat lowerface onbed localZ0; mm no scaling','CONDITIONAL_UNPOWERED_FOUNDATION_FIT; no wholecat/logicframe release') for x in checks])
csvwrite('used-fasteners.csv',['role','qty','nominal','bearing_engagement','stock_and_fit'],[
 ('8sourceanchors',8,'M2.5x16 countersunk overalllength','existing8axes; cover2.6/frame2.05 notsupplierthreadproof','NEEDED_UNCONFIRMED; P00first; NOdrill/tap'),
 ('2decksplices',4,'M3x10 +4fullM3nut2.4 +4washerOD7x0.5','two actualsplices, samefrozenstack','NEEDED_UNCONFIRMED'),
 ('rearsharedpanel',4,'M3x50 +4fullM3nut2.4 +4washerOD7x0.5','boss1+panel3+post40+web2+washer.5+nut2.4=48.9;tip1.1','NEEDED_UNCONFIRMED; all4continuousloadingpaths checked'),
 ('tailrootbase',4,'M3x20 +4fullM3nut2.4 +4washerOD7x0.5','unchanged sourcefrozenlocalbearing','NEEDED_UNCONFIRMED'),
 ('S0familyholes_NOTinstalled',2,'M6x12 nominal38pitch','projectfamilyhole only; actualS0supplierinterface NOTverified','NOclaiminstalledorstock; dryfitfamilyfirst')])
shutil.copyfile(OLD/'WAGO-role-map.csv',P/'WAGO-role-map.csv')
for name in ['day14-ready-build.py','day14-ready-checks.py','day14-ready-neighbors.py','day14-ready-final-missing.py','day14-ready-receive-last.py','day14-ready-source-rails.py','day14-ready-report.py']:
 shutil.copyfile(Path('C:/Users/Sysq/AppData/Local/Temp')/name,P/name)
text='''# START HERE — WAVEGO: pierwsza przymiarka podstawy BEZ ZASILANIA

**Bieżący zestaw:** tylko ten katalog `fit-kit-ready`, model `fit-assembly.FCStd`, 8 różnych STL/13 sztuk. Poprzednie katalogi `foundation-fit-kit` i `fit-kit-final` zachowują dowody HOLD; nie są alternatywnymi instrukcjami montażu. To warunkowe zwolnienie do przymiarki podstawy, nie gotowy zasilony kot ani odbiór całej ramy elektroniki.

## 1. Najpierw jedna mała próba

**P00: 214×55×1,2 mm, 1 szt.** Przyłożyć do posiadanej bazy bez przerabiania metalu. Osiem otworów pochodzi z zachowanego źródła WAVEGO. Potwierdzić rewizję, osie, faktyczny gwint i długość chwytu. Ø2,05 w modelu nie dowodzi gwintu M2.5. Jeżeli nie pasuje — zatrzymać montaż; nie wiercić i nie gwintować ramy.

Po zgodnej przymiarce podstawy: P01×2, P02×1, P03×1, P04×2. Tył: P05×4, P06×1, P07×1. Szczegóły ilości i rozmiary są w `print-parts.csv`; wyłącznie te druki są eksportowane, bez przewodów/śrub/kupnych modułów.

## 2. Co rzeczywiście zamknięto w CAD

Wszystkie cztery pełne nakrętki i podkładki mają ciągłą drogę załadunku do miejsca pracy. Dwa wejścia są od wolnego bokuY−: początekY−87 poza krawędzią−82. Dwa są od spodu: (99,15) i (164,27). Nowy portØ9 przy(99,15) dochodzi doZ46,52; nad nim pozostaje rzeczywisty2mmweb do48,52. Nie wystarczyło samo wolne końcowe gniazdo. Zweryfikowano pełne pola ruchu, poprawne bryły i zerowe przenikanie; stary wynik13,550718mm³ pozostaje w zamrożonym pakiecie.

Cztery **M3×50**, boss**1mm**, pełna nakrętka2,4mm/podkładka0,5mm. Cały stos48,9mm, koniec1,1mm za nakrętką; poprzednio odebrany odstęp całej śruby do rzeczywistej pokrywy min4mm i oparcia podkładek29,931524mm² zachowano bez zmian. Nie ciąć śrub. Stare identyfikatory wewnętrzne `H03_panel_M3x55_*` oznaczają teraz nominalne **M3×50** — właściwy opis i BOM są tutaj.

P06 jest jedną rzeczywistą częścią: panelS0 + tylny mostek + dwa zamknięte gniazda wspólnej półki. Zastępuje funkcję starej NIEZBUDOWANEJ `Upper_frame_end_105`; nie ma dwóch nakładających się belek. Odebrano zachowanie8zamierzonych składników/zakresu, dwa oparcia szyn52,8mm², dwa oparcia słupków9mm², ciągłe wsunięcie końców10mm i brak przenikania osobnych druków. Końce przyszłych szyn6×1,5mm zachowują przekrój9mm² dawnego3×3; gniazdo ma nominalnie.15boki/.2dach/.2koniec. Są to referencje przyszłej ramy, nie dodatkowe eksporty produkcyjne.

Nowy materiał szyny jest2,5mm od AUX. Na zachowanym odcinku starej niewydrukowanej szyny jest1,0mm — **otwarte pasowanie makiety elektroniki**, bez waiver1,25 i bez odbioru kompletnej górnej ramy. To ograniczenie nie znika przez nazwę wspólnej podpory. Nie obciążać niezakończonej półki elektroniką bez jej rzeczywistej przymiarki.

Szeroki dawny prostokąt `Rear_aux_open` nie był bryłą przewodów:1725mm³ z panelem zachowano jako wynik rezerwy, nie fizyczny kontakt. Przy panelu wykazano ciągłe boczne okno ręcznego układania25×19,75mm, X130..155/Y20,25..40/Z80..100, z rzeczywistymi sąsiadami. Pełne wtyki, odciążenia, długości i promienie nadal sprawdzane na stole wFIT2 — wolne okno nie dowodzi całej wiązki.

## 3. Kolejność dla dwóch osób

1. A przykłada P00 i sprawdza rzeczywiste mocowania; B porównuje komplet z listą i utrzymuje baterię odłączoną. Dopiero zgodne osie/gwint pozwalają przejść do podstawy.
2. **Na stole, przed osadzeniem P03 na bazie:** B wkłada pełne nakrętki z podkładkami przez cztery opisane wejścia; A prowadzi je do gniazd i sprawdza antyobrót. Nie liczyć na włożenie przez sam otwór śruby. Kieszenie mają podparcie/ścianki; zachować pełne podkładki.
3. Ułożyć dwie listwyP01 i połówkiP02/P03, połączyć dwiemaP04. Osiem nominalnych M2.5 tylko po potwierdzeniu gwintu/chwytu; najpierw lekko, bez wymuszania. M3splices/nakrętki i narzędzie przed elektroniką/baterią. Kupna rama pozostaje cała.
4. Ustawić czteryP05 i P06 na rzeczywistych płaszczyznach. S0ma zachowane11części, a dwa otworyM6/rozstaw38 to tylko nominalna rodzina do przymiarki — nie dowód dostarczonego mocowania. Dopasować bez wiercenia obudowy. CzteryM3×50 z pełnym stosem; potwierdzić brak naprężenia i dostęp klucza przed wiązkami. Sam CAD nie ustala momentu dokręcania/nośności PETG.
5. Referencyjny montaż wspólnej półki: wsunąć dwa luźne końce szyn w P06, zanim zamknie się ich przednie połączenie i założy PCB. Nie odrywać wirtualnie integralnego druku. Półka/AUX/Pi/BUS pozostają próbą regulowaną; nie drukować sztywnego produkcyjnego mocowania według starej makiety.
6. P07na rzeczywistym tylnym padzie, cztery nominalneM3×20. To otwarty korzeń do przymiarki, nie odebrany napęd ogona. Wszystkie kupne części/pozy nóg i źródłowe osie pozostają.
7. Otwarta próba końców na stole według grafu: **16WAGO415 =4DATA/5plus/7masa**. Mapa1:1 wCSV, bez zmiany połączeń. Cztery niezależne220 i oba końce/MTA zachować osobno; moduły lutowane nie są rozpinane. KrótkieFHAC, pełnyUSB500+Delock, K1474 i chłodzeniePi/BUS sprawdzić na prawdziwych częściach. Łączniki/stock NIEPOTWIERDZONE; brak zakupu/cięcia/podłączania zasilania.
8. Ręcznie przeprowadzić pełny zakres nóg z odłączonym zasilaniem i sprawdzić masę/luz/pinch. Bateria/paski i kosmetyczne osłony na końcu. Skorupa i napędy głowy/ogona nie są zwolnione tym zestawem.

## 4. Druk i trzy nazwane FIT

Wszystkie STL wmm, dodatnimXYZ iZ0, zamknięte/dodatnie, każdywymiar<256mm. Duża płaska dolna powierzchnia na stole, bez skalowania. Propozycja PETG: warstwa0,2mm/4obrysy/5góra-dół/35%wypełnienia; to nie zatwierdzony profil ani test wytrzymałości. Dachy kanałów/mały mostek gniazda6,3mm i szczeliny wymagają próbki pasowania; podpory tak, by dało się je wyjąć. Nie wykonano slicingu ani druku.

- **FIT1:** P00, rzeczywista rewizja/gwint/osiem mocowań, masa i ręczny ruch12napędów. Żadnej kwalifikacji udźwigu z pola kontaktu.
- **FIT2:** prawdziwe końce/fabryczne długości/odciążenia, ochrona iS0M6, USB/Delock, cztery220, chłodzeniePi/BUS oraz wspólna makieta logiki/AUX1mm. Bez skracania/łączenia wirtualnie, bez uznania1mm za spełnienie1,25. Aktualne długości/cięcia/luz nieudowodnione pozostająNULL.
- **FIT3:** kartonowy cały obrys Oli z portami/pełnym panelem doX177, głowa/ogon/łożyska i realne proporcje/masa. Nie finalna skorupa ani mechanizm produkcyjny.

Źródła i odebrane granice w `manifest.json`. Pozostałe6STL są bajtowo takie same jak zamrożone źródło; P06identyczny z ostatnim pakietemHOLD, zmieniono tylko P03port. Żadnego starego globalnego exact126/nowej recenzji/nowej rodziny układu. Brak fizycznegoPASS, zakupu, zasilania i druku.
'''
(P/'START_HERE.md').write_bytes(text.encode())
print(json.dumps({'parts':len(checks),'quantity':sum(x['quantity'] for x in checks),'six_frozen_SHA':sum(x['unchanged_foundation'] for x in checks),'STL_closed':True}))
