from pathlib import Path
import json,hashlib,csv,shutil,zipfile
from datetime import datetime,timezone
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Ellipse
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit')
d=json.loads((P/'layout.json').read_bytes());rows=d['rows']
for name in ['day14-firstfit-build.py','day14-firstfit-complete.py','day14-firstfit-report.py']:
 shutil.copyfile(Path('C:/Users/Sysq/AppData/Local/Temp')/name,P/name)
def colour(n):
 if 'WAVEGO' in n:return '#c4c7ca'
 if 'WAGO' in n:return '#a4c6df'
 if 'ATO4A' in n or 'FHAC' in n or 'MTA010' in n:return '#dc9775'
 if n.startswith('S0_') or n.startswith('S1_'):return '#bd9bcb'
 if 'Battery_GEA' in n:return '#9bc997'
 if 'MG92B' in n or '608' in n or '688' in n:return '#d5ba6c'
 return '#7caeaa'
def dim(ax,a,b,label,vertical=False):
 ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='<->',color='#333',lw=.9))
 ax.text((a[0]+b[0])/2+(3 if vertical else 0),(a[1]+b[1])/2+(0 if vertical else 3),label,fontsize=8,rotation=90 if vertical else 0,ha='left' if vertical else 'center',va='center' if vertical else 'bottom')
fig,(top,side)=plt.subplots(2,1,figsize=(14,11),layout='constrained')
for ax,axes,title in [(top,(0,1),'TOP — shared support and occupied component projections'),(side,(0,2),'SIDE — accessible layers / ground datum')]:
 ax.set_title(title,loc='left',fontsize=13,fontweight='bold');ax.set_aspect('equal');ax.grid(alpha=.12);ax.set_axisbelow(True)
 ax.set_xlabel('X [mm]  FRONT ←');ax.set_ylabel('Y [mm]' if axes[1]==1 else 'Z [mm]')
 a,b=axes
 # Physical source projection is deliberately a bounds reference, actual geometry in native views.
 lo,hi=d['base']['bounds_mm'];ax.add_patch(Rectangle((lo[a],lo[b]),hi[a]-lo[a],hi[b]-lo[b],facecolor='#eee',edgecolor='#888',lw=1,linestyle='--',zorder=0))
 for r in sorted(rows,key=lambda r:r['bounds_mm'][0][2]):
  n=r['id'];lo,hi=r['bounds_mm']
  if n.startswith('Ola_') or n.startswith('WAVEGO') or r['evidence'].startswith('GROUP') or 'support' in r['evidence'] or 'PROPOSED' in r['evidence'] or 'bracket_space' in n or 'components_and_cooling' in n:continue
  ax.add_patch(Rectangle((lo[a],lo[b]),hi[a]-lo[a],hi[b]-lo[b],facecolor=colour(n),edgecolor='#35504d',alpha=.65,lw=.45,zorder=2))
 # Shared 265x164 deck and outline of cosmetic envelope.
 if b==1:
  ax.add_patch(Rectangle((-105,-82),265,164,fill=False,edgecolor='#555',lw=1.5,zorder=3))
  ax.add_patch(Ellipse((25,0),290,180,fill=False,edgecolor='#20222a',lw=1.4,linestyle='--',zorder=4))
  ax.add_patch(Ellipse((-174,0),110,130,fill=False,edgecolor='#20222a',lw=1.4,linestyle='--',zorder=4))
  ax.plot([185,210,229,233],[0,0,0,0],color='#24262c',lw=6,alpha=.7)
  dim(ax,(-105,-110),(160,-110),'deck 265 = 135 + 130')
  dim(ax,(180,-82),(180,82),'164 deck',True)
  ax.set_xlim(-260,250);ax.set_ylim(-133,140)
  labels=[('Pi4',(-56,-10),(-66,-120)),('12 × motor fuse + full TE/ATO',(0,65),(-10,115)),('16 × WAGO415',(40,22),(30,92)),('4 × WAGO615',(-86,0),(-205,-95)),('battery',(50,0),(45,-93)),('S0 complete11',(137,-29),(203,-84)),('5 × FHAC',(110,67),(157,115)),('MAIN / AUX',(96,35),(135,94)),('PCA / E1',(-45,42),(-105,102)),('F0 30A',(-119,49),(-201,100)),('camera / ToF',(-230,-15),(-230,-120))]
 else:
  ax.plot([-250,245],[-168.24665]*2,color='#595959',lw=1)
  ax.text(130,-159,'source neutral ground −168.25',fontsize=8)
  ax.add_patch(Rectangle((-105,45.52),265,3,fill=False,edgecolor='#555',lw=1.5,zorder=3))
  ax.plot([-115,-50,50,130,170],[119,158,158,155,124],ls='--',color='#252830',lw=1.4)
  ax.add_patch(Ellipse((-174,141),110,100,fill=False,edgecolor='#252830',lw=1.4,linestyle='--'))
  ax.plot([185,210,229,233],[142,165,199,214],color='#252830',lw=6)
  ax.plot([-197,-183,-169],[181,222,188],color='#252830',lw=2)
  dim(ax,(200,48.52),(200,158),'body/back ≈110 above deck',True)
  dim(ax,(-105,25),(160,25),'265 shared deck')
  ax.set_xlim(-260,250);ax.set_ylim(-190,235)
  labels=[('front head / yaw / pitch',(-163,143),(-245,213)),('Pi / BUS',(-60,121),(-77,202)),('removable back + microphone',(45,146),(50,213)),('battery lifts after back removed',(50,76),(67,175)),('S0 key',(135,126),(165,189)),('banks sideways open',(15,110),(0,-65)),('speaker',(-60,62),(-97,-49)),('12 original ST3215 in sourcebase',(60,-55),(90,-125)),('three MG92B, 3×608 +688',(-126,113),(-245,-74))]
 for text,xy,t in labels:ax.annotate(text,xy,xytext=t,fontsize=8,ha='center',bbox=dict(fc='white',ec='none',alpha=.85,pad=1.5),arrowprops=dict(arrowstyle='-',color='#666',lw=.6),zorder=10)
fig.suptitle('WAVEGO + OLA CAT • ONE FIRST-FIT ARRANGEMENT • 14 Nov 2026',fontsize=16,fontweight='bold')
fig.text(.01,.002,'Occupied bounds / nominal installation envelopes; no collision, print, payload or physical PASS. Source neutral pose, no scaling. Actual CAD views accompany this sheet.',fontsize=9)
fig.savefig(P/'dimensioned-top-side.png',dpi=150);plt.close(fig)
md='''# WAVEGO + kot Oli — jeden układ do oceny przymiarki

**Wynik:** zapisany cały układ, bez skalowania bazy i bez dawnych chwytów N01. To koncepcja do jednej oceny całego montażu, nie gotowy wydruk ani fizyczny PASS. Płyta 265 × 164 mm dzieli się na 135 i 130 mm; dwie listwy korzystają z ośmiu istniejących pionowych otworów. Obrys grzbietu ma około 285 × 180 mm. Głowa, uszy i ogon nawiązują do zdjęcia Oli; nogi pozostają widoczne.

Na dole są 16 WAGO danych i 4 WAGO zasilania, głośnik oraz zdejmowana tacka baterii 106,5 × 35 × 21,5 mm z dwiema opaskami. Po bokach stoją dwa otwarte banki po sześć kompletnych oprawek silników z TE IN/OUT i ATO. Cztery niezależne zabezpieczone przewody 220 mm pozostają całe. Z przodu osobno F0; z tyłu pełny S0 na wspólnym panelu, S1, monitor i pięć oprawek pomocniczych. Pi/BUS, właściwy Adafruit815, E1 i oba Pololu mają wspólną górną ramę. ReSpeaker jest na zdejmowanym grzbiecie, kamera/ToF w głowie, BNO/amp/touch we wskazanych miejscach.

## Składanie przez dwie osoby

1. A: zgodność ośmiu mocowań WAVEGO, dwie listwy i dwie połówki płyty. B: przygotowanie istniejącej wiązki na stole, bez nowych cięć, lutowania na PETG lub zmian zabezpieczeń.
2. Przy otwartej górze: dolne WAGO, pełne oprawki/końcówki, głośnik i czujnik. Dostęp do dźwigni przed tacką baterii.
3. Wspólna rama/półki, izolowane mocowania PCB, Pi i pozostałe płytki. Założyć złącza i odciążenia przed zamknięciem sąsiednich warstw. Pełny USB500 z wybranym Delockiem, fabryczne końce GPIO/MTA i właściwe przydziały K1474 zostają.
4. Panel S0, terminale i osłona elektryczna, S1, bezpieczniki i monitor. Obciążenia na panel/ramę, nie na przewody. Potem tacka, paski i odłączona bateria.
5. Wsporniki głowy/ogona, trzy MG92B, trzy 608 i jeden 688. Ułożyć przewody i pętle ruchowe w otwartych regionach; sprawdzić na prawdziwych złączach i ruchu, nie sztywnych ilustracjach każdej żyły.
6. Osłony kosmetyczne na końcu. Do baterii zdejmujemy grzbiet z mikrofonem i odpinamy XT60/balance; do rzadkiej naprawy dopuszczamy zdjęcie tacki/półki. Brak wymogu szybkiego serwisu.

## Niezbędne proste druki i łączniki — jeszcze do dopracowania

Dwie listwy źródłowych mocowań, dwie połówki płyty z prostym łączeniem, dwa wspólne boczne stelaże/półki, tacka baterii z dwoma poprzeczkami, otwarte wspólne mocowania obu banków, tylny panel ochrony i proste wsporniki głowy/ogona. Docelowo osobne osłony głowy, grzbietu i ogona. Otwory PCB/oporów, osłony terminali i sprzęgła osi są nieukończone. M2.5 do istniejących ośmiu otworów oraz M3/nakrętki/dystanse do nowych druków są planem montażowym: rzeczywiste gwinty, długości i liczba ze stosu do potwierdzenia; bez deklaracji zapasu ani zakupu.

## Trzy próby, które rozstrzygną układ

1. **Baza i obciążenie:** wzornik ośmiu otworów/mała próbka korzenia, zważenie kompletnego zestawu, ręczny ruch wszystkich nóg z płytą. Źródłowo płyta zaczyna się 6 mm nad najwyższym punktem pozycji neutralnej; to nie dowód ruchu ani nośności. Masa dodana 0,9–1,4 kg jest tylko szacunkiem ryzyka, nie obliczoną wartością.
2. **Złącza i ochrona:** przymiarka pełnych banków, WAGO, pięciu par fabrycznych przewodów FHAC≥84,5 mm, czterech osobnych 220 mm, Pi/USB/GPIO, XT60/balance i rozdzielonych przydziałów 210 MAIN/350 Pi. Sprawdzić odciążenia, izolację, R/OD, długości i luzy w otwartych polach. Zapisane oprawki/inne niepełne modele są opisanymi rezerwami instalacji, nie dostarczonym materiałem. Brak wartości cut/installed-fit/slack do czasu próby.
3. **Głowa i wygląd:** jeden otwarty model z prawdziwymi MG92B/łożyskami, ważenie głowy i dźwigni, obrót z CSI oraz wzornik sylwetki. Rewizje modułów audio/czujników i rzeczywiste przyłącza wymagają tej samej lokalnej przymiarki; nie rozpoczynamy audytu katalogu.

Dokładny dobór 57 pozycji CSV jest zachowany w `selected-parts-allocation.csv` i `layout.json`; drobne elementy E1, bezpieczniki, pierścienie, złącza i rezystory przy końcach są rozliczone funkcjonalnie, bez fikcyjnych dodatkowych modułów. Kamera/audio/czujniki to jawne rozszerzenie użytkownika poza obecną listą elektryczną; integracja pozostaje otwarta. Stare badania i negatywy pozostają historią, bez przenoszenia flag PASS do nowych pozycji.
'''
(P/'assembly-plan.md').write_bytes(md.encode('utf-8'))
with (P/'selected-parts-allocation.csv').open('w',encoding='utf-8',newline='') as f:
 fields=list(d['selected_rows'][0])+['placement_or_function','status'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
 for r in d['selected_rows']:
  text=' '.join(r.values()).lower()
  if any(x in text for x in ['resistor','capacitor','78l05','harwin','1608','1208','74lvc']):alloc='E1 populated prototypeboard / named remoteMG resistor ends'
  elif any(x in text for x in ['fuse','mta','520448','520184','fhac','0287','0242']):alloc='12motor banks / 4protectedleg units / F0 / 5auxiliary holders / E1logic fuse; match exact row quantity and source graph'
  elif any(x in text for x in ['wago','221-']):alloc='16data+4power+POST_F0+8distributed inline, open lower deck / head-tail connection bays'
  elif any(x in text for x in ['688','608','mg92','jr300']):alloc='headyaw/pitch/tail assembly, bearings and3separate extensions'
  elif any(x in text for x in ['st3215','22414']):alloc='12servos already in retained126solid WAVEGO source compound'
  else:alloc='Named selected assembly in layout.json / electrical sourcegraph; whole installed region retained, detailed ports/strain and fastening pending FIT2'
  w.writerow(dict(r,placement_or_function=alloc,status='SELECTED_NOT_PHYSICAL_INVENTORY_OR_FIT_PASS'))
with (P/'necessary-print-and-fastener-list.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['group','quantity','role','readiness'])
 for row in [('Source-hole rails',2,'WAVEGO8hole root','coupon/stack fit first'),('Split deck halves',2,'135+130 by164','join/mount details pending'),('Shared side frames',2,'upper logic+power shelf','coarse native blanks only'),('Battery tray and crossarms','1+2','two selected straps','slots/capture pending'),('Motorbank shared mounts',2,'6fullunits each','unbuilt mount details'),('Rear protection panel','1+4posts','S0/S1/monitor/FHAC root and guards','coarse native blanks only'),('Head/tail brackets',2,'3MG and4bearings','couplings/fit pending'),('Cat cosmetics','head/back/tail','Ola silhouette','envelopes only no printablewall'),('M2.5 source root','8candidate','sourcehole stack','actualthread/grip length unknown'),('M3 joints/standoffs','TBD','shared plate and PCB assembly','selected existing hardware role/count to confirm no purchase')]:w.writerow(row)
print('Reports and dimensioned sheet saved; rows',len(rows),'selected',len(d['selected_rows']))
