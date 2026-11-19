"""Bind the saved model, checked geometry streams and the portable assembly inventory."""
from pathlib import Path
P=Path(__file__).parent;F=P.parent/'day19-connected-servo-usb-and-closure'
s=(F/'package.py').read_text(encoding='utf8')
head=s[:s.index('for n,v in rd(E/')]
head=head.replace("nat=P/'whole-cat19F.FCStd'","nat=P/'whole-cat19G.FCStd'").replace("parent=E/'whole-cat19E.FCStd'","parent=F/'whole-cat19F.FCStd'").replace('cef650870eb4fd430b0b9ff2900217996992c553051fe5c5d594a0e2ff38330c','9083ceb3a74698a199f38ee7a70c7b57be3ae515e3c1a1d61a53a32adc20b146')
exec(head)
prior=rd(F/'verified-19F.json')
superseded={}
for path,want in prior['sources'].items():
    actual=pin(root/path)
    if actual!=want:superseded[path]=dict(parent=want,current=actual)
for p in [parent,F/'verified-19F.json',F/'material-index.json',F/'service-lay.json',F/'unit-plan.json',F/'occupied-check.json',P.parent/'motion-layout.json',hw/'simulation/p0/e6-leg-compatibility.json',P.parent/'FelineInteriorMotion.FCStd',hw/'electronics/full-cat/pwm-carrier-r3/population.json',hw/'electronics/full-cat/pi-bus-primary-r1/H3.brep',hw/'electronics/full-cat/w5-bus-assembly-r1/assembly.json',hw/'print-package-2026-11-19/START_HERE.md']:pin(p)
idx=rd(P/'material-index.json');exec(s[s.index('parts=idx'):s.index("hits=[dict")])
assert not lost and len(parts)==50
checks=rd(P/'final-profiles.json');station=rd(P/'final-stations.json');motion=rd(P/'final-motion.json');ret=rd(P/'retained-runs.json');svc=rd(P/'assembly-check.json')
assert len(checks['rows'])==70 and len(ret['rows'])>=25 and len(station['rows'])>=40
def witnesses(rr):return [dict(field=r['field'],yaw=r['yaw'],pitch=r['pitch'],obstructions=r['hits']) for r in rr if r['hits']]
hits=witnesses(checks['rows']);oldhits=witnesses(ret['rows']);rigid=[r for r in station['rows'] if r.get('common_mm3',0)>.00001 or 'error' in r];moving=[r for r in motion['rows'] if r['surface_hit']]
plan=rd(P/'whole-termination-plan.json');assert len(plan['wires'])==160
effect=dict(native=nh,source_19F=h(parent),source_coverage=rd(F/'effectivity.json')['effective_selected'],changed_prints=list(rd(P/'new-members.json')),retained_prints=len(parts)-len(rd(P/'new-members.json')),checked_profiles_with_witness=hits,retained_stock_witness=oldhits,static_witness=rigid,motion_witness=moving,source_updates=superseded,physical_PASS=False,whole_print_GO=False,actual_cut_fit_slack=None)
wr('effectivity.json',effect)
mass=idx['geometric_P_g'];units=sum(q['qty'] for q in parts); k=plan['units']['K1474'];mi=rd(P/'mounted-mic.json')
side=rd(P/'side-clearance.json')
for part in parts:
    name=part['part']
    reasons=[r['a']+' / '+r['b'] for r in rigid if name in [r['a'],r['b']]]
    reasons.extend(sorted({r['field'] for r in hits for hit in r['obstructions'] if hit['part']==name}))
    if name=='E19_FrontShroud' and side['material_intersections']:reasons.append('added lower wall intersects retained leg members in poses 46, 47 and 48')
    if reasons:part.update(assembly_status='HOLD at named installed interfaces; individual mesh only',installed_hazards=reasons)
idx['whole_print_kit']=False
wr('material-index.json',idx)
summary=f"""# WAVEGO 19G — zakończenia wiązek i montaż skrzynki

**Status całego montażu: HOLD.** Zapisana geometria obejmuje prostą skrzynkę, ruchomy ogon, obie pokrywy i nowe stanowiska zakończeń. ZIP zawiera {len(parts)} modeli STL na {units} sztuk, {len(idx['steps'])} plików STEP oraz osobny kupon MTA. Największy wymiar w orientacji z rezerwą na brim i podpory wynosi {mx:.2f} mm. Pełna objętość druków odpowiada {mass:.2f} g PETG. Zakres masy robota wynosi {(1853.4+mass)/1000:.3f}–{(2593.4+mass)/1000:.3f} kg przy dotychczasowych założeniach.

[Model FreeCAD](whole-cat19G.FCStd) · [widok całego robota](three-quarter.png) · [wnętrze](interior.png) · [przekroje](critical-sections.png) · [montaż dla dwóch osób](MONTAZ.md) · [ilości i orientacje](material-index.json)

| Grupa | Koniec fizyczny i rozliczenie | Montaż |
|---|---|---|
| BUS D/G | Jeden H3, D_FL.1 i G2.4. Dwie żyły wspólnego 900 mm. Dłuższa potrzebuje {plan['units']['BUS900']['required_axial_length']} mm w rozpatrywanym ułożeniu z końcami i rezerwą. | Najpierw wsunąć pełny wtyk od góry, następnie rozdzielić żyły przy banku. |
| Trzy MG i trzy JR | Osobno 250 i 300 mm na napęd. Dziewięć końców idzie do FHAC, zacisków powrotu oraz pól R1–R3. | Wkładać od strony otwartego podziału wieka, następnie połączyć zakładki. |
| MAIN i Pi | K1474 ma dwie żyły po 1000 mm. Odcinki wyjściowe {k['power_pair_kept']} mm. Z dodatniej żyły pochodzi też wejściowy odcinek 210 mm, którego proponowany przebieg z końcami zajmuje {k['input_required']} mm. | Zmierzyć przed pierwszym cięciem. Trasy kończą się na zarejestrowanych polach MAIN. |
| ReSpeaker i USB | Złącze USB1 złożenia dostawcy ma wyjście w +X. Dwa wtyki Pi w oddzielnych stosach, DATA i AUDIO na różnych wysokościach. | Sprawdzić oba rzeczywiste nadlewy jednocześnie i długość osobnego przewodu AUDIO. |
| Nogi, optyka, dotyk, głośnik | 134 bazowe i 26 dodatkowych połączeń mają przypisane role i grupy. Część współrzędnych wskazuje strefę dojścia do płytki. Oznaczenia fizycznych padów, wyjścia przewodów nóg i metraż otwartych odcinków wymagają sprawdzenia. | Dwie osoby układają przewody przed zamknięciem, pozostawiając dostęp do złączy i śrub. |

**Wyniki.** Kolizja laminatu 1608 z oparciem wynosiła 19,399 mm³. W końcowym złożeniu tę parę zmierzono ponownie. Mikrofon ma {mi['bodies']} bryły dostawcy i dwa oryginalne zestawy śrub. W końcowym badaniu {len(hits)} z {len(checks['rows'])} przypadków nowych profili dało świadek przecięcia; dotyczą one {', '.join(sorted(set(r['field'] for r in hits))) or 'żadnej grupy'}. W testach zachowanych przewodów wskazań jest {len(oldhits)}. Dodatnie lub nierozstrzygnięte pary sztywne: {len(rigid)}. Wskazania ruchu powierzchni: {len(moving)}. Wyniki pól nadlewów są warunkowe do przymiarki rzeczywistych wtyków. W pliku effectivity.json każde wskazanie ma nazwanego sąsiada. Pierwsze odrzucone przebiegi pozostają w first-profiles.json. Wstępna różnica wysokości nowego boku i skrajnej obwiedni nóg dla 49 póz wynosi {svc['vertical_gap_at_retained_samples']:.2f} mm. Ujemny wynik wymaga porównania tylko tam, gdzie pokrywają się X i Y. Wynik lokalny zawiera side-clearance.json.

**Znane kolizje materiału.** Dolny bok osłony przecina ogniwa nogi w pozach 46, 47 i 48. W największym pojedynczym teście wspólna objętość wynosi {max(r[3] for r in side['material_intersections']):.2f} mm³. Osłona wymaga zmiany dolnego podziału z zachowaniem miejsca na nogę i pokrywy. Widok ¾ pokazuje nadal otwarte przejście pod policzkiem. Mikrofon koliduje z przednim wiekiem na 6,94 mm³. W dziewięciu próbach ToF po zmianie kierunku USB1 zniknęło wskazanie przy wtyku. Dwa projektowe pola nadlewów Pi mają 379,73 mm³ wspólnej objętości. Do oceny nadlewów potrzebne są oba rzeczywiste wtyki.

**Do zamknięcia.** Rozwiązać pozostałe oznaczone wejścia w materiał i potwierdzić dostępny koniec przy każdej niezmierzonej strefie. Dopasować trójki zdalnych rezystorów do rzeczywistego styku z zachowaniem zacisków. Potwierdzić podwójny wtyk Pi, rzeczywistą długość USB_AUDIO, przewody nóg, cztery MTA0100335, wysunięcie obu połówek XT60 przez drzwiczki i prześwit chłodzenia przy zamkniętej pokrywie. Próbę optyczną i akustyczną oraz rzeczywisty pomiar zapasu wykonuje się po przymiarce. Alarm G-Tech czeka na mapę wnęk. Fizyczne cięcia, luz i odbiór pozostają otwarte.

[Bilans jednostek i 160 połączeń](whole-termination-plan.json) · [stacje i materiał](final-stations.json) · [nowe przebiegi](final-profiles.json) · [zachowane jednostki przy nowych częściach](retained-runs.json) · [ruch](final-motion.json) · [obsługa i nogi](assembly-check.json)
"""
(P/'START_HERE.md').write_bytes(summary.encode())
for p in P.glob('*'):
 if p.suffix.lower() in {'.py','.json','.md'}:norm(p)
for name in ['START_HERE.md','MONTAZ.md','material-index.json','native-receipt.json','effectivity.json','whole-termination-plan.json','assembly-check.json','side-clearance.json','final-stations.json','final-motion.json','final-profiles.json','retained-runs.json','first-profiles.json','critical-sections.png','front.png','side.png','three-quarter.png','interior.png','whole-cat19G.FCStd']:assets[name]=P/name
for name in ['ELECTRICAL_ASSEMBLY.md','SOURCES_ELECTRICAL.json']:
 p=hw/'print-package-2026-11-19'/name;assets[name]=p;pin(p)
for name in ['POLACZENIA.csv','MATERIALY.csv']:
 p=hw/'electronics/full-cat/closed-prototype-add7-2026-11-16/assembly-reference'/name;assets[name]=p;pin(p)
exec(s[s.index("archive=P/"):s.index("print('verified")].replace('19F-components','19G-components').replace('verified-19F','verified-19G'))
print(nh,len(files)+1,len(sources),native['objects'],native['native_entries'],len(assets),mass,len(hits),len(rigid),len(oldhits),len(moving))
