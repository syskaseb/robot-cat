from pathlib import Path
import json,csv,shutil,hashlib,struct,collections,zipfile,math
from datetime import datetime,timezone
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit/fit-kit-final');OLD=P.parent/'foundation-fit-kit'
r=json.loads((P/'result.json').read_bytes());parts=json.loads((P/'parts.json').read_bytes())
for n in ['day14-final-joint.py','day14-final-checks.py','receive-final-joint-hold-native.py','day14-final-report.py']:
 shutil.copyfile(Path('C:/Users/Sysq/AppData/Local/Temp')/n,P/n)
shutil.copyfile(OLD/'WAGO415-station-role-net-map.csv',P/'WAGO-role-map.csv')
checks=[]
for part in parts:
 q=P/part['stl'];raw=q.read_bytes();num=struct.unpack_from('<I',raw,80)[0];assert len(raw)==84+50*num;edges=collections.Counter();lo=[math.inf]*3;hi=[-math.inf]*3;volume=0
 for i in range(num):
  t=struct.unpack_from('<12fH',raw,84+50*i);vs=[t[3:6],t[6:9],t[9:12]];keys=[tuple(round(v,5) for v in p) for p in vs]
  for p in vs:
   for k in range(3):lo[k]=min(lo[k],p[k]);hi[k]=max(hi[k],p[k])
  for k in range(3):edges[tuple(sorted((keys[k],keys[(k+1)%3])))]+=1
  a,b,c=vs;volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
 assert all(x==2 for x in edges.values()) and volume>0 and min(lo)>-1e-4 and max(b-a for a,b in zip(lo,hi))<256
 if not part['changed']:assert raw==(OLD/part['stl']).read_bytes()
 checks.append(dict(part=part['name'],triangles=num,bounds_mm=[lo,hi],volume_mm3=volume,closed=True,same_as_old=not part['changed']))
(P/'STL-integrity.json').write_bytes((json.dumps(checks,indent=2)+'\n').encode())
with (P/'print-parts.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['part','quantity','stl','size_mm','change','release'])
 for p,c in zip(parts,checks):w.writerow([p['name'],p['quantity'],p['stl'],'x'.join(str(round(b-a,3)) for a,b in zip(*c['bounds_mm'])),'CHANGED' if p['changed'] else 'SHA_IDENTICAL_TO_FROZEN','P00root-template-only' if p['name'].startswith('P00') else 'NO_NEW_MOUNT_RELEASE_frontpositive_loadingentryHOLD'])
with (P/'used-fasteners.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['role','quantity','nominal','status'])
 for row in [('8sourceframeanchors',8,'M2.5x16 countersunk overalllength','source2.6cover/2.05frame NOTthreadproof, neededunconfirmed'),('2decksplices',4,'M3x10 +M3nut2.4 +bottomwasher0.5','unchanged neededunconfirmed'),('rearsharedpanel',4,'M3x50 +fullM3nut2.4 +washerOD7x0.5','correctedfullstack48.9 / tip1.1; LOADINGENTRY_HOLD, neededunconfirmed'),('tailrootbase',4,'M3x20 +M3nut2.4 +bottomwasher0.5','unchanged neededunconfirmed'),('S0case familytestholes',2,'M6x12 nominal38pitch','PROJECTfamily/notinstalled/notverifieddeliveredthread')]:w.writerow(row)
fig,(a,b)=plt.subplots(1,2,figsize=(12,6),layout='constrained')
a.set_title('Complete M3×50 joint — actual local clearance closed',fontsize=11);a.set_xlim(-10,10);a.set_ylim(35,99);a.set_aspect('equal');a.grid(alpha=.15)
for z,h,c,label in [(37.02,1.5,'#666','retained TopCover'),(41.52,7,'#b3baad','P03 rear plate'),(48.52,40,'#d7ceb3','P05 40mm'),(88.52,3,'#a4c2cc','P06'),(91.52,1,'#84b5b7','boss1')]:
 a.add_patch(Rectangle((-5,z),10,h,fc=c,ec='#555',alpha=.7));a.text(6,z+h/2,label,fontsize=8,va='center')
a.add_patch(Rectangle((-4.5,43.42),9,3.1,fc='white',ec='#555'));a.add_patch(Rectangle((-2.75,43.62),5.5,2.4,fc='#888'));a.add_patch(Rectangle((-3.5,46.02),7,.5,fc='#555'));a.add_patch(Rectangle((-1.5,42.52),3,50,fc='#a9b8c8'));a.add_patch(Rectangle((-2.75,92.52),5.5,3,fc='#a9b8c8'))
a.annotate('4.0mm',xy=(-6,38.52),xytext=(-6,42.52),ha='right',fontsize=9,arrowprops=dict(arrowstyle='<->'));a.set_xlabel('section, nominalstandardsteel');a.set_ylabel('worldZ mm')
b.set_title('First actual assembly falsifier — entry of pocket1',fontsize=11);b.set_aspect('equal');b.set_xlim(91,116);b.set_ylim(7,23);b.grid(alpha=.15)
b.add_patch(Rectangle((99,11.3),11,7.4,fc='#e0dcc9',ec='#666'));b.add_patch(Circle((110,15),3.7,fc='#e0dcc9',ec='#666'));b.add_patch(Circle((99,15),3.5,fc='#709acf',ec='#345',alpha=.5));b.add_patch(Rectangle((95.5,11.5),3.5,7,fc='#d86152',alpha=.65,ec='#a33'))
b.annotate('13.550718mm³ actualcommon\nX95.5..99 / Y11.5..18.5\nZ45.52..46.32',xy=(97,15),xytext=(102,21),fontsize=8,ha='center',arrowprops=dict(arrowstyle='->'));b.text(109,9,'endseat',fontsize=8,ha='center');b.text(97,9,'loadingstart',fontsize=8,ha='center');b.set_xlabel('worldX mm');b.set_ylabel('worldY mm')
fig.suptitle('ONE PURPOSEFUL REAR JOINT • LOADING HOLD • NO SECOND FAMILY',fontsize=14,fontweight='bold');fig.savefig(P/'joint-and-entry-section.png',dpi=160);plt.close(fig)
notes='''# Zadany tylny węzeł — wynik jednej próby: HOLD wejścia załadunkowego

**Nie ma nowego odbioru zestawu do montażu.** Wypróbowano jeden cały węzeł: M3×50 z gniazdami nakrętki/podkładki oraz P06 łączący panel S0 i funkcję tylnej belki półki. Po pierwszej rzeczywistej blokadzie załadunku zatrzymano próbę; nie wykonano kolejnej wysokości, rodziny ani poprawki ukrywającej wynik. Nazwa folderu `fit-kit-final` nie oznacza zwolnienia druku do obciążonego montażu. Zaczynać można tylko od zachowanego wzornikaP00 i dotychczasowej przymiarki źródłowych ośmiu osi.

## Co wykazano

Właściwy pełny stos wynosi48,9 mm: boss1 +panel3 +słupek40 +rzeczywisty web2 +podkładka0,5 +pełna nakrętka2,4. ŚrubaM3×50 kończy się1,1 mm za nakrętką. Najbliższa rzeczywista pokrywa WAVEGO ma zmierzony odstęp4,0 mm/common0 do krytycznej śruby; wszystkie cztery pełne śruby są poprawne geometrycznie. Każda podkładka ma rzeczywiste oparcie29,931524 mm². Nie skrócono trzpienia, nie poświęcono zazębienia i nie rozluźniono1,25 mm. Łączniki pozostają zapotrzebowaniem nominalnym/NIEPOTWIERDZONYM, bez zakupu ani deklaracji magazynu.

## Co obaliło montaż

Pierwszy kanał od krawędzi przy(110,−73) przyjmuje pełny stos w ciągłym polu10 mm bez wspólnego materiału. Drugi, przedni dodatni przy(110,15), jest zablokowany przy samym wejściuX99: pełny profil nakrętki i podkładki zajmuje13,550717771 mm³ cienkiej części płyty. Świadek jest poprawną geometrią w `feed-entry-blocker.brep` i na `local-entry-HOLD.png`; dokładne granice X95,5..99 /Y11,5..18,5 /Z45,52..46,32. Sam wolny kanał i końcowe gniazdo nie zapewniają sposobu wsunięcia całego stosu. Wymagany jest prawdziwy interfejs załadunku pełnego profilu na początku tej drogi przed uznaniem całej kolejności. **Nie wdrożono tej kolejnej zmiany w tej porcji.** Dwa dalsze kanały oraz odbiór połączeń półki/sąsiadów pozostały nieodebrane po falsyfikacji.

## Wspólna funkcja półki — zbudowana, nieodebrana po falsyfikatorze

Stara NIEZBUDOWANA belka `Upper_frame_end_105` została jawnie zastąpiona integralnym mostkiem P06. Nowe dwa zamknięte gniazda mają pasujące szerokie końce szyn6×1,5 mm (zachowany przekrój9 mm² dawnej szyny3×3), podparcie od dołu i zamknięcie przeciw uniesieniu. Zmieniono tylko lokalne końce dwóch projektowych szyn i wierzchy dwóch projektowych słupków; kupne płytki, S0 z11częściami, rama, osie nóg i porty zachowały położenia. Jest to faktyczna jedna bryła panel/mostek/gniazda, z kontrolą zachowania zamierzonych składników, bez nazywania penetracji OWN. Te dopasowane szyny są odniesieniem przyszłej wspólnej ramy, a nie dodatkowymi wydrukami produkcyjnymi tego pakietu. Testy odbiorcze zamkniętych gniazd i sąsiadów nie zostały wykonane po pierwszym HOLD.

## Eksporty i kolejność wymagająca zamknięcia

Są te same8unikalnych STL/13szt ze wzornikiem. Zmieniono WYŁĄCZNIE P03 iP06;6pozostałych STL skopiowano i zweryfikowano bajtowo. Wszystkie siatki są zamknięte, dodatnie, w mm/Z0/dodatnimXYZ i mieszczą się w256 mm. To poprawność eksportu, nie fizyczny PASS. PETG0,2/4obrysy/5góra-dół/35% to propozycja do przymiarki; zamknięte gniazda mają mały mostek6,3 mm, który wymaga rzeczywistej próby druku/pasowania. Nie wykonano slicingu ani druku.

Plan: wzornik8osi/gwintu → listwy i połówki na stole → rzeczywisty załadunek nakrętek/podkładek PRZED osadzeniem na ramie → osiem źródłowych mocowań → S0 i jego panel/śruby → wsunięcie dopasowanych końców szyn PRZED zamknięciem przedniego połączenia półki i założeniem PCB → wiązki/bateria/osłony na końcu. **Etap załadunku nadal ma wskazany HOLD, więc tej sekwencji nie uznano za wykonalną.** Nakrętki są prowadzone przeciw obrotowi przez5,8 mm szczelinę (nakrętkaAF5,5), podkładkaOD7 przez7,4 mm; nie rozpinamy wirtualnie fabrycznych końców, lutów ani integralnej ramy.

Źródłowe M2.5/Ø2,05 nadal nie są dowodem fabrycznego gwintu. Dwa M6/38 mm dlaS0 pozostają założeniem rodziny do lokalnej przymiarki. Cztery220, krótkieFHAC, USB500/Delock, stosPi/BUS i masa/ruch/skorupa pozostają nazwanymi próbami z poprzedniego pakietu. Mapa16WAGO nadal4DATA/5plus/7masa i dokładnie ten sam graf elektryczny. Brak nowego cięcia, złącza, zakupu, prądu, ROS ani recenzji geometrii. Stare HOLD i33zamrożone pliki pozostają bez zmian.
'''
(P/'assembly-print-notes.md').write_bytes(notes.encode('utf-8'))
print('Reports saved: oneactualHOLD;8closedSTLs;6byteidentity; no conditionalrelease claim')
