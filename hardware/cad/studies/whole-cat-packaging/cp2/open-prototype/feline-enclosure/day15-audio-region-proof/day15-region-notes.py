from pathlib import Path
import json,math,shutil,zipfile,xml.etree.ElementTree as E
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,Rectangle
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day15-audio-region-proof');plan=json.loads((P/'proposal.json').read_bytes());r=json.loads((P/'local-result.json').read_bytes())
with zipfile.ZipFile(P/'audio-region-proof.FCStd') as z:
 for n,f in [('COVER_I2S_BCLK.Shape.brp','hazard-allocated-profile.brep'),('WIRE_I2S_BCLK.Shape.brp','hazard-nominal-profile.brep'),('Pi_components_and_cooling.Shape.brp','hazard-Pi-cooling-reserve.brep')]:
  (P/f).write_bytes(z.read(n))
r.update(received_foreign_pairs=4,unreceived_foreign_pairs=80,unreceived_profile_packing_pairs=21,feed_capacity_unreceived=True,decision='STOP this one continuous occupied allocation at required margin to nominal Pi cooling reserve. Not delivered wire/component contact. No second route, module pose, material or radius family. Need whole cooling/port/initiallay disposition before retention.',native_test_stop_mechanism='SystemExit escaped MCP wrapper after result was already saved. Technical service interruption; factual valid gap/common retained. Future reproduction uses normal return.',end_interfaces_unqualified=plan['interfaces'],minimum_fit_cut_slack=None)
(P/'local-result.json').write_bytes((json.dumps(r,ensure_ascii=False,indent=2)+'\n').encode())
fig,axs=plt.subplots(1,2,figsize=(13,5.5));ax=axs[0]
ax.add_patch(Rectangle((-75,23),12,20,fill=False,lw=2,color='black',label='open feed 12 x 20'))
for i,p in enumerate(plan['profiles']):
 u,v=(-2.3,.95) if i==4 else (p['u'],p['v']);x=-69.8+u;y=30+v;rr=p['diameter']/2
 ax.add_patch(Circle((x,y),rr+.4,fill=False,color='darkorange',ls='--'));ax.add_patch(Circle((x,y),rr,color='steelblue' if i<5 else 'seagreen'));ax.text(x,y,str(i+1),ha='center',va='center',fontsize=8,color='white')
ax.set(xlim=(-77,-61),ylim=(21,45),aspect='equal',xlabel='world X [mm]',ylabel='world Y [mm]',title='Feed: 7-profile capacity reference\nActual passage occupancy: speaker pair only; gate UNRECEIVED')
ax=axs[1]
for i,p in enumerate(plan['profiles']):
 if i>=5:continue
 v=p['v'];rad=14+v;ys=[30+v]*2;zs=[114,116]
 for j in range(51):
  a=math.pi/2*j/50;ys.append(16+rad*math.cos(a));zs.append(116+rad*math.sin(a))
 ys.append(-27);zs.append(130+v);ax.plot(ys,zs,lw=3,alpha=.5,label='5 profiles, normal frame' if i==0 else None)
ax.add_patch(Rectangle((-38,100.12),56,26,alpha=.22,color='red',label='Pi component/cooling nominal reserve'))
ax.add_patch(Rectangle((-40,92.52),61,3,alpha=.4,color='grey',label='Pi tray context'))
ax.annotate('Exact full 3D profile+.4: gap 1.184264 < 1.25\ncommon 0; not delivered contact',xy=(18,125),xytext=(-32,136),arrowprops={'arrowstyle':'->'},fontsize=9)
ax.set(xlim=(-43,36),ylim=(88,143),aspect='equal',xlabel='world Y [mm]',ylabel='world Z [mm]',title='Continuous upper I2S branch — one allocation HOLD')
ax.legend(loc='lower left',fontsize=7);fig.suptitle('Regional capacity and local turn — diagrams are explanatory, BRep/result authoritative');fig.tight_layout();fig.savefig(P/'packing-and-local-hazard.png',dpi=160);plt.close(fig)
shutil.copy2(P.parent/'day15-audio-module-layer/whole-native.png',P/'whole-physical-layout-reference-unchanged.png')
text='''# Region audio — jedna obsadzona alokacja, HOLD odstępu chłodzenia

Bieżący zapis `audio-region-proof.FCStd` zachowuje cały układ i materiał poprzedniego pakietu. Dodane obiekty to wyłącznie lokalne profile przewodów, ich marginesy oraz przekrój pojemności; nie nowe części ani zwolnienie druku.

## Co rozstrzyga odczyt

Pusty narożnik dawnego `AL_AMP_FREE_TURN_BAY` nie jest przewodem. Zastąpiono ten dowód jedną lokalną ciągłą obsadą: 5×Ø1,6 od górnego dojścia Pi do AMP oraz 2×Ø2,1 od głośnika przez otwarty kanał do AMP. Przy AMP dochodzi siedem funkcji, ale tylko para głośnika przechodzi dolny feed. Nie wymuszano siedmiu przewodów na całej długości.

Każdy profil ma zachowany margines zewnętrzny 0,4mm. Pakowanie zakłada 0,2mm między nominalnymi profilami; kompletne sprawdzenie wzajemne jest NIEODEBRANE (0/21), ponieważ zatrzymano pierwszą bramkę przestrzenną. Przekrój siedmiu profili w 12×20mm jest referencją pojemności, a nie dowodem całej drogi ani dodatkową obsadą. Jego bramka pozostaje nieodebrana.

Jedna geometria normalna/Bishop: górny łuk YZ ma promień osi14mm, U=X, V jest normalną promieniową, bez dowolnego world-roll. Indywidualne promienie wynikają z odsadzeń; minimum11,3mm względem własnej zasady4×OD (6,4/8,4mm). To założenie prototypu, nie promień producenta. Ciągłe nominalne rury są valid/1solid, ich objętość odpowiada πr²L, brak nominalnego profilu poza jego marginesem wynosi0. Nie stanowi to jeszcze prześwitu ani akceptacji kabli.

**Wynik:** odebrane4/84 nowe relacje lokalnej obsady do wybranych sąsiadów; po3dodatnich relacjach pierwszy I2S_BCLK+.4 względem `Pi_components_and_cooling`: valid gap1,184264447mm <1,25, common0. Pełny łuk podchodzi do narożnika rezerwy chłodzenia, mimo pozornie wolnego odcinka poziomego. Regionalny rysunek sam nie ujawniał tego miejsca, stąd jeden dokładny test pełnego profilu. Pozostałe80relacji i21pakowania NIEODEBRANE. To HOLD przydziału z marginesem względem nominalnej rezerwy komponentów/chłodzenia, nie dowód kontaktu dostarczonego przewodu, wszystkich tras ani fizycznej niemożliwości.

STOP tej jednej alokacji; bez drugiego łuku/wysokości, przesuwania AMP/głośnika/Pi lub zmiany materiału. Raw gap0/common0 starego pustego pola zachowany w poprzednim pakiecie. Następna decyzja dotyczy rzeczywistego interfejsu chłodzenia/złączy i układania całej warstwy przed retencją; nie automatyczne nowe podpory z powodu pudełka.

## Końce i dwie osoby — warunkowa kolejność

1. Poza PETG przygotować E1/lutowane końce. A podtrzymuje otwartą konstrukcję, B układa parę głośnika w otwartym feed przed pionową PCA i dociskami. Nie przeciągać fabrycznych dużych końców przez zamknięty otwór.
2. Pi5 układać od góry w otwartym obszarze do AMP; zachować rozdział od pary BTL. Żaden przewód BTL nie jest masą. Dopiero po rozwiązaniu obecnego HOLD oraz realnych końców można zamknąć dociski.
3. Górną ramkę ReSpeaker ORAZ TTP223 montować na końcu, z istniejącym przewodem dotyku. Nie wymyślono rozłącznego złącza TTP. Dostęp do baterii może wymagać częściowego demontażu; nie deklarujemy szybkiego serwisu.

AMP: rzeczywiste pady/header/kierunki UNKNOWN; lewa strona jest jawnym nominalnym założeniem dojścia do przymiarki. Pi: końcowy pinout/wyjście przewodów z pełnego GPIO1992 nieodebrane. Głośnik: terminale i długość przewodu UNKNOWN. Lokalne długości w JSON to tylko fragmenty tego modelu, nie długości całych kabli/cięcia/minimum. USB_AUDIO jest osobną pozycją FIT, bez ponownego kredytu USB500/Delock dla BUS. Cztery niezależne220/obaMTA/FHAC84,5/K1474 i istniejące końce zachowane; actualcut/fit/slack NULL.

## Stan i granice

Wszystkie pozy/materiał/root/BUS/11odebranych modułów zachowane; nie powtarzano61/11/root/BUS. `whole-physical-layout-reference-unchanged.png` jest jawnie niezmienionym widokiem fizycznej konfiguracji poprzedniego pakietu; diagram lokalny i nowe BRep/JSON dokumentują obecny odczyt. Brak nowego materiału/STL. Zasilanie/druk/przymiarki FIT1/2/3 nie wykonane. Głośnik/mikrofon: realne strefy chwytu i otwory akustyczne pozostają nazwanym FIT, bez nowej komory.

Techniczne przerwanie MCP po zapisie HOLD nie jest nową kolizją/porzuceniem geometrii. Zabezpieczono zapisany checkpoint przed odzyskaniem jednego GUI; status natywny w osobnym potwierdzeniu jest obowiązujący. Nie używać obsługi SystemExit w dalszych skryptach MCP.
'''
(P/'REGION_AND_LAY.md').write_bytes(text.encode())
print('notes, fixed source operands, packing diagram, unchanged whole reference saved')
