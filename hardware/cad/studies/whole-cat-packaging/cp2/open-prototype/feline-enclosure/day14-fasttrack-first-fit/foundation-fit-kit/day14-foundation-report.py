from pathlib import Path
import json,csv,hashlib,shutil,zipfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
P=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit/foundation-fit-kit')
d=json.loads((P/'foundation-kit.json').read_bytes())
for n in ['day14-foundation-report.py']:
 shutil.copyfile(Path('C:/Users/Sysq/AppData/Local/Temp')/n,P/n)
raw=json.loads((P/'source-eight-hole-interface.json').read_bytes());cover=raw[0];front=raw[1];rear=raw[2];axes=[]
for x in [-80,-70,112,122]:
 for y in [-22.5,22.5]:
  c=min([r for r in cover['cylinders'] if abs(r['r']-1.3)<1e-6],key=lambda r:abs(r['center'][0]-x)+abs(r['center'][1]-y))
  f=min([r for r in (front if x<0 else rear)['cylinders'] if abs(r['r']-1.025)<1e-6 and r['z'][0]>30],key=lambda r:abs(r['center'][0]-x)+abs(r['center'][1]-y))
  axes.append(dict(x_mm=x,y_mm=y,cover_diameter_mm=2*c['r'],frame_model_diameter_mm=2*f['r'],relative_axis_error_mm=((c['center'][0]-f['center'][0])**2+(c['center'][1]-f['center'][1])**2)**.5,thread='UNKNOWN_modeldiameter_not_supplierthreadproof'))
assert max(a['relative_axis_error_mm'] for a in axes)<1e-6
(P/'eight-source-axes.json').write_bytes((json.dumps(axes,indent=2)+'\n').encode())
with (P/'print-list.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['part','quantity','STL','print_size_mm','orientation','status'])
 for r in d['parts']:
  lo,hi=r['print_bounds_mm'];size=[round(b-a,3) for a,b in zip(lo,hi)]
  scope='template / primary foundation fit only; physical8hole/thread check first' if r['name'][:3] in ['P00','P01','P02','P03','P04'] else 'FIT GEOMETRY ONLY — rearM3fixing and logicinterface HOLD, no loadedassembly release'
  w.writerow([r['name'],r['quantity'],r['stl'],'x'.join(map(str,size)),r.get('print_orientation','flatZ0'),scope])
with (P/'used-fasteners.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['role','count','nominal','source_status'])
 for r in d['fasteners']:w.writerow([r['role'],r['count'],r['nominal'],('HOLD CURRENT NOMINAL STACK — tip/TopCover gap~0, do not assemble as drawn. ' if r['role']=='4S0panel spacers' else '')+r['source']])
with (P/'WAGO415-station-role-net-map.csv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f,lineterminator='\n');w.writerow(['physical_station','role','nets','assembly_object','placement_status'])
 for r in d['station_mapping']:w.writerow([r['station'],r['role'],'|'.join(r['nets']),r['object'],'movable trial on common open deck; port/lead fit not accepted'])
fig,(a,b)=plt.subplots(2,1,figsize=(13,10),layout='constrained')
col={'P01':'#d1bb92','P02':'#c7c9cd','P03':'#81b3aa','P04':'#d4a68c','P05':'#c9a7cd','P06':'#9ab9da','P07':'#d2c275'}
for ax in [a,b]:ax.set_aspect('equal');ax.grid(alpha=.15);ax.set_axisbelow(True);ax.set_xlabel('X [mm]')
for r in d['parts']:
 if r['name'].startswith('P00'):continue
 lo,hi=r['bounds_mm'];c=col[r['name'][:3]]
 a.add_patch(Rectangle((lo[0],lo[1]),hi[0]-lo[0],hi[1]-lo[1],facecolor=c,edgecolor='#555',alpha=.6,lw=.8))
 # side source-negativeY branch and depthshown; blocks intentionallyprojections notsolid material.
 b.add_patch(Rectangle((lo[0],lo[2]),hi[0]-lo[0],hi[2]-lo[2],facecolor=c,edgecolor='#555',alpha=.6,lw=.8))
for q in axes:a.add_patch(Circle((q['x_mm'],q['y_mm']),1.4,fc='white',ec='#222',lw=.8))
a.plot([30,30],[-82,82],'k--',lw=.8);a.text(30,87,'seamX30',ha='center',fontsize=8)
a.set_title('TOP — printable foundation / actual eight source axes',loc='left',fontweight='bold');a.set_ylabel('Y [mm]');a.set_xlim(-115,210);a.set_ylim(-100,105)
for text,xy,pt in [('P02 front135×164',(-45,-65),(-60,-95)),('P03 rear + real load yoke',(120,-60),(125,-95)),('P06 panel +4×P05',(135,-29),(135,93)),('P07 open tail root',(185,0),(190,70)),('2×P04 seam straps',(30,-44),(5,-95))]:a.annotate(text,xy,xytext=pt,fontsize=9,ha='center',arrowprops=dict(arrowstyle='-',lw=.7))
# A real Y=-22.5section shows source rail step / rear load yoke; fillexactrectangles.
b.clear();b.set_aspect('equal');b.grid(alpha=.15);b.set_xlabel('X [mm]');b.set_ylabel('Z [mm]');b.set_title('REAR LOAD SECTION + installation levels (world mm)',loc='left',fontweight='bold')
for p,size,c in [((-86,38.52),(190,7),'#d1bb92'),((104,38.52),(24,3),'#d1bb92'),((30,45.52),(147,3),'#c7c9cd'),((104,41.52),(73,4),'#81b3aa')]:b.add_patch(Rectangle(p,*size,fc=c,ec='#333',lw=.8))
# Separate projected panel / posts and tail located at other Y explicitlylabelled.
for x in [107,161]:b.add_patch(Rectangle((x,48.52),6,40,fc='#c9a7cd',ec='#555',alpha=.8))
b.add_patch(Rectangle((107,88.52),70,3,fc='#9ab9da',ec='#333'))
b.add_patch(Rectangle((171,48.52),27,4,fc='#81b3aa',ec='#333'));b.add_patch(Rectangle((171,52.52),27,4,fc='#d2c275',ec='#333'))
for x in [178.5,195]:b.add_patch(Rectangle((x,55.52),3,51.48,fc='#d2c275',ec='#333'))
b.axhline(39.52,c='#888',ls='--',lw=.8);b.text(-80,36,'retained base neutral highest39.52; actualthread/grip fit required',fontsize=8)
for z in [41.52,45.52,48.52,52.52,88.52,91.52]:b.annotate(str(z),xy=(177,z),xytext=(207,z+(2 if z in [41.52,48.52,88.52] else 0)),fontsize=8,arrowprops=dict(arrowstyle='-',lw=.5))
b.text(0,74,'Load: panel →4spacers →integrated rear deck/yoke\n→stepped rails →4rear source bolts/frame.\nTailfoot sits at52.52, no3/7mm air gaps.',fontsize=10,ha='center')
b.text(110,112,'Posts and tail shown as projections from their own Y;\nnative rear-view shows actual disjoint parts.',fontsize=8)
b.set_xlim(-100,225);b.set_ylim(32,121)
fig.suptitle('SAME-GEOMETRY FOUNDATION KIT • REAR M3 FIXING HOLD • TEMPLATE / PRIMARY FIT ONLY',fontsize=13,fontweight='bold')
fig.text(.01,.002,'Actual local H03 screw-tip / retained TopCover gap ≈0 <1.25; no loaded rear assembly release. Unbuilt logicbrace/panel interface also OPEN. Whole source parts retained.',fontsize=9,color='#a22')
fig.savefig(P/'foundation-dimensioned-plan-and-load-section.png',dpi=160);plt.close(fig)
text='''# WAVEGO — zestaw płyty do pierwszej przymiarki

**Odbiór cyfrowy dotyczy nowego fundamentu. Nie jest to gotowy do zasilenia kot ani finał skorupy.** Poprzednie 16 plików pozostaje bez zmian; jedynym bieżącym modelem tej korekty jest `foundation-assembly.FCStd`. Zawiera cały układ jako odniesienie, a tylko grupę PRINT_PARTS eksportowano do STL.

## Co drukujemy

Najpierw **P00, jeden wzornik 214×55×1,2 mm**. Sprawdzić na posiadanej ramie osiem osi: X−80/−70/112/122, Y±22,5. Zapis źródłowy ma Ø2,6 w pokrywie i Ø2,05 w ramie, nie dowodzi gwintu. Jeśli wzornik/śruba nie pasują ręcznie, przerwać przymiarkę; nie wiercić ani gwintować kupnej ramy.

Po zgodności: P01 listwa **2 szt.**, P02 przód **1**, P03 tył z rzeczywistym tylnym węzłem **1**, P04 łącznik spodu **2**, P05 słupek40 mm **4**, P06 panel **1**, P07 otwarty korzeń ogona **1**. Łącznie 12 elementów nośnych i osobny wzornik; 8 unikalnych STL. Wymiary/orientacja i ilości są w `print-list.csv`. Każdy STL jest już ustawiony dodatnio i na Z=0, bez skalowania. PETG, proponowane 0,2 mm / 4 obrysy / 5 warstw góra-dół / 35% wypełnienia. Listwy i płyty płasko, słupki na boku; otwarty korzeń ogona podstawą w dół. Nie wykonano slicingu ani druku.

Tylny deck ma część pełnej szerokości do X177 oraz wąski język ogona do X198. Zintegrowane pogrubienie schodzi do Z41,52 i opiera się na stopniach obu listew. Cztery słupki mają powierzchnię oparcia na Z48,52; panel na Z88,52, zgodnie z rzeczywistą górą nominalnego korpusu S0. Stopa ogona siada na Z52,52. Nie ma dawnych przerw3/7 mm ani słupka poza podparciem. Słupek tylnego prawego naroża jest poza otwartym wspornikiem ogona; żadne dwa zamierzone osobne druki nie dzielą objętości. Te połączenia mają rzeczywiste śruby/nakrętki oraz sprawdzone powierzchnie styku — nie fuzję z kupną ramą i nie pusty opis.

## Kolejność i łączniki

1. Przymierzyć P00 i sprawdzić rzeczywisty typ/zaangażowanie gwintu. Osiem **M2.5×16 łeb stożkowy**, długość całkowita, to zapotrzebowanie nominalne do potwierdzenia, nie stwierdzenie zapasu ani typu fabrycznej śruby. W płytach są własne pogłębienia90° Ø5, z zachowaniem1,9 mm materiału pod łbem. Żadnej zmiany kupnej ramy.
2. Na stole połączyć połówki przez dwa P04: **4×M3×10, 4 nakrętki M3, 4 podkładki0,5 mm od spodu**. Założyć listwy i luźno przykręcić osiem źródłowych punktów, zanim WAGO, bateria lub S0 zasłonią łby. Właściwy gwint i długość potwierdzić bez wymuszania.
3. Korzeń ogona mocować **4×M3×20 +4 nakrętki +4 podkładki od spodu**. Dostęp od góry i boków pozostaje otwarty; to wspornik do przymiarki, bez gotowego sprzęgła/uchwytów serwa.
4. Panel na czterech P05 mocować **4×M3×55 +4 nakrętki +4 podkładki od spodu**. Dwa milimetry miejscowego pogrubienia pod łbami zapewniają nominalnie pełną nakrętkę. Klucz do nakrętek używać przed bankami/elektroniką; mały dostęp sprawdzić w otwartym montażu. S0 ma wyjmowany klucz w OFF według zachowanej notatki źródłowej: zdjąć go do nałożenia panelu, następnie przywrócić. To plan bez rzeczywistej operacji elektrycznej.
5. **Dwa otwory M6 w rozstawie38 mm są założeniem rodziny projektowej**, nie odebranym gwintem kupnej obudowy. M6×12 to tylko nominalna pozycja do potwierdzenia; nie jest wliczana jako zainstalowana geometria. Dopasować rzeczywisty korpus/neck i mocowanie przed obciążeniem S0. Nie wiercić jego obudowy. Osłona terminali i dwa odciążenia pozostają wymagane przed jakimkolwiek uruchomieniem.

Tylko wymienione łączniki są rozliczone w `used-fasteners.csv`; ich dostępność jest **NIEPOTWIERDZONA**, bez zakupu/nowej inwentaryzacji. Złącza i drobna elektronika nie są nowymi częściami tego wydruku.

## Rozdział przewodów i otwarty montaż

16 sztuk221-415 to **4DATA: D_FL/D_FR/D_RL/D_RR; 5plus: FL_P/FR_P/RL_P/RR_P/P_AUX; 7masa: FL_G/FR_G/RL_G/RR_G/G2/G_AUX/G_TAIL**. Dokładna mapa stacja–sieć–końce jest w CSV/JSON z bieżącego schematu; nie zmieniono ani jednego połączenia elektrycznego. Wewnętrzne dawne nazwy geometrii nie są rolami elektrycznymi. Miejsca oprawek są ustawne, bez16 dedykowanych kaset; odstęp3 mm nie jest dowodem wolnego miejsca na porty/zgięcia.

Przed utrwaleniem chwytów wykonać jeden otwarty bench-fit czterech NIEZALEŻNYCH220 mm z oboma fabrycznymi końcami, krótkich par FHAC≥84,5 mm oraz pełnego USB500 z wybranym Delockiem. Zachować izolację, odciążenia, rzeczywiste promienie i luz; brak cięcia, łączenia zapasów i zmyślonego PASS długości. Pi/BUS pozostaje próbną wspólną półką: rezerwa chłodzenia nakłada się nominalnie3,12 mm, więc nie drukować stałych dystansów przed rzeczywistą przymiarką. Papierowy/kartonowy obrys całego kota ma objąć także panel doX177 i język ogonaX198; dawneX170 nie jest gotową osłoną.

**Najbliższe trzy próby:** osiem mocowań + ręczny ruch nóg/masa; faktyczne końce/ochrona/S0; stos Pi/BUS i kartonowa sylwetka. Nie są pretekstem do pełnego audytu123 żył ani produkcyjnej obsługi serwisowej. Druk fundamentu i wzornik mogą poprzedzać dopracowanie pozostałej elektroniki. Zachowane źródła/negatywy pierwszego układu pozostają w nadrzędnym manifestcie.
'''
warning='''
**BIEŻĄCA BLOKADA — NIE MONTOWAĆ TYLNEGO MOCOWANIA JAK NA RYSUNKU.** Lokalny pełny test nominalnej śruby `H03_panel_M3x55_1` i rzeczywistej pokrywy źródłowej WAVEGO dał gap≈0 mm (common0), zamiast1,25 mm. Nie jest to stwierdzenie kontaktu dostarczonych części, lecz obalenie narysowanego stosu55 mm. Rysunek śrub i ich lista służą śledzeniu tej wersji, nie są zatwierdzonym doborem do tylnego montażu. Drugi jawny interfejs: panel S0 dzieli310,075352 mm³ ze STARYM NIEZBUDOWANYM projektem tylnej belki półki elektroniki. To zależność druków do integracji, nie kolizja kupnych modułów ani zgoda na usunięcie belki z nazwy.

W tej porcji odzyskano **identyczne osiem STL — każdy SHA zgodny z kopią sprzed restartu**. Nie zmieniono kształtów, nie próbowano kolejnej rodziny. Gotowy użyteczny pierwszy krok to wzornikP00 i przymiarka głównego fundamentuP01–P04 po potwierdzeniu ośmiu rzeczywistych mocowań. P05–P07 pozostają geometrią do przymiarki, bez odbioru obciążonego tylnego zespołu, aż do rozstrzygnięcia powyższych interfejsów. 19 rzeczywistych płaskich powierzchni oparcia jest dodatnich (minimum27,447014 mm²); to dowód materiałowej drogi oparcia, nie pomiar wytrzymałości ani odbiór śrub.

'''
text=text.replace('## Co drukujemy',warning+'## Co drukujemy',1)
text=text.replace('Panel na czterech P05 mocować', '**NIE WYKONYWAĆ w tej wersji — nominalny stos H03 ma HOLD.** Pokazany panel na czterech P05 miał być mocowany',1)
text += '\nOdzyskanie usługi: GUI19584 zakończony dopiero po kopii15źródeł/eksportów oraz10plików temp100,7MB; kod wyjścia nieznany. Jeden nowy GUI8920, bez równoległego CAD. Zapis native nastąpił przed testami. Globalnej dokładnej kontroli126brył nie powtórzono: liczbowy cull i jeden mały lokalny kandydat36ścian ujawniły H03HOLD. Wynik timeoutu nie jest negatywem geometrii.\n'
(P/'assembly-and-print-notes.md').write_bytes(text.encode('utf-8'))
print('Foundation report saved; parts',len(d['parts']),'contactrows',len(d['contacts']))
