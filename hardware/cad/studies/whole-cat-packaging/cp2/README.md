# CP2: wspólne rozmieszczenie wnętrza

Niewybrana propozycja w zaakceptowanym obrysie CP1, tułów325×200×160mm.
Nie jest zestawem części do druku ani zamknięciem W1/W5. R53 i14/20=70%
pozostają bez zmiany; hook aktywny do06.10.2026 09:00Warszawy, bez harmonogramu.

`WholeCatInterior.FCStd` zawiera zachowane rzeczywiste referencje P0,
przesuniętą głowę/ogon CP1 oraz63 edytowalne rezerwacje modułów i17 dostępu.
Aktualny układ ma dziesięć nominalnych brył przewodów, osiem końców odkrytych,
osiem brył kupnych pierścieni/osprzętu S0 oraz16 brył S1 (cztery pierścienie,
cztery śruby, cztery warunkowe pola podparcia i cztery budżety narzędzia).
To snapshoty z buildera,
nie automatycznie aktualizowana pełna wiązka ani drukowane mocowania.
Stara kaseta została usunięta z tej propozycji, nie z wybranego robota.
Źródło: `tools/cad/whole_cat_interior.py`; wynik i ograniczenia: `layout.json`;
kontrola nominalnego rozmieszczenia: `checks.json`; wymiary, wyjścia i granica
serwisowa: `interfaces.json`. Wcześniejszy plan61 rezerwacji zastąpiony.

| Warstwa | Rozmieszczenie |
|---|---|
| Dół | Akumulator pozostaje; Pi42..64mm, MAIN obrócony przy przodzie, BUS41..55,6mm, monitor50..62mm; para XT60/F0 w przedniej bocznej strefie i6 splices |
| Środek/boki | Sterowniki78..108mm;12 oprawek70..134mm;4 MTA80..96mm;10 bocznych WAGO56..75mm z wejściami w dół |
| Góra/środek | 6 poziomych centralnych WAGO110..121mm; P_FRONT108,2..130,2 wejściami w dół, P_REAR110..121 wejściami ku+X; P_SYS95..117 wejściami w górę, G1 103,5..125,5 wejściami w dół;5 poziomych FHAC125..147mm; ATO nie pod WAGO |
| Źródło/wyłączniki | S0 z kluczem pionowo w przedniej strefie, S1 z osią +Y obok tylnej strefy; otwory/osprzęt jeszcze do zaprojektowania |

Uwzględniono12 MTA0300330/24 zakończenia,20 bloków WAGO,6 splices,
4 MTA0100335,5 FHAC0001ZXJ i1 F0 FHAC0002ZXJ, XT60, osiowy F_PWM
0242.100UAT1 (bez osobnej oprawki) oraz układy sterowania.
Zgodność dokładnego zestawu20 nazw szyn z istniejącym netlist jest sprawdzana
automatycznie. Wybrana topologia/SKU pozostaje R53. Nowy kandydat dodaje
jedno221-412 ZA F0, dzielące fizyczny W076 na fabryczny koniec i przedłużenie;
nie dodaje połączenia przed F0 ani nowego potencjału. Wybór/stock jeszcze otwarte.

## Plan obu wyjść4MTA: dwie próby odrzucone, 06.10.2026

`mta-preflight-rejected.json` przechowuje dwa negatywne wyniki i wspólne
ograniczenia. Dolny plan Z31 wszedł w P0 SideLeft/Right22 (doZ38,52),
nutshoe i połączenie zaF0. Plan nad ramą Z50, z przełożonym Pi/BUS/monitorem
i bocznymi WAGO, naruszył sześć starych splices, F0 oraz trasy W001/W076
i Pi. To nie problem pojedynczej śruby ani dowód gotowej wiązki.

Żadna próba nie zastąpiła dobrego `WholeCatInterior.FCStd`, `layout.json`
ani widoku. `checks.json` przywrócony do odpowiadającego dobremu modelowi
dowodu9beb81c; negatywny wynik osobno, bez mieszania wersji. Domyślny builder
zachowuje układ S1. Opcja `--mta-candidate-rejected` przechowuje odrzuconą
receptę do diagnozy, NIE do powtórki bez zmiany wspólnego planu.

Osiem kandydatów221-412 i trasy fabryczne nie są wybranym stockiem.
Katalogowe L140 NIE dowodzi100mm na każdą stronę. Przed trzecią próbą
przypisać sześć starych splices do rzeczywistych obwodów i zaplanować je
wraz z pełnymi niezmienionymi trasami źródła i ośmioma końcamiMTA.
Nie powtarzać obu układów ani kompensować ich mikroprzesunięciami.
70% bez zmiany, W1/W5 OPEN, brak fizycznegoPASS.
cad-layout-planning: po dwóch porażkach wrócono do wspólnej przyczyny,
zachowano jedną dobrą propozycję zamiast mnożyć części do druku.

## Bieżące cztery pełne trasy S1, 06.10.2026

W064 S1.3→P_FRONT.1 ma nominalny blank204,784mm, W065 S1.6→P_REAR.1
214,819mm. Każdy obejmuje14mm WAGO i14,452mm TE130171, OD4,2/R25,2.
W064 idzie pod centralnymi złączami, W065 pętlą obok ogona z dwoma
przesunięciami korytarza. Proste izolowane końce:9/10mm i9/20,955mm.
P_FRONT obrócony−90X: baza[−58,5;33;130,2], port1[−53;38,5;108,2].
P_REAR obrócony−90Z: baza[50,5;38,5;110], port1[72,5;33;115,5].
D_RL/G2 przełożone razem do środków[94;0]/[129;0]. Poprzednie mocowania
i trasy do tych czterech WAGO nie są zakwalifikowane po zmianie położenia.

Pierwsza próba obu wyjść:0 kontaktów/wyjść/błędów; wcześniejsze wejścia,
S0 i sześć odcinków źródła zachowane.59 niezmienionych modułów korzysta
z poprzedniego dowodu. CAD49,219s; świeży reopen18 wire/strip+8S0+16S1,
objętości i parametr P_REAR Width+1→X+1/przywrócenie:7,578s.
To geometria nominalna, nie pomiar kupnych kieszeni ani fizyczny PASS.

`interfaces.json/source_stock_contribution`: cztery blanki S1 zastąpią
stare920mm (W064220/W065180/W067260/W068260) przez850,853mm,
różnica−69,147mm. Nie sumować starych i nowych równolegle.
Cały dotychczas wymodelowany podzbiór HELU ma1305,187mm, NIE cała wiązka
ani ilość zakupowa. Pozostałe czerwone przewody, zapas/stock i wybór OPEN;
fabryczne F0 nie są dodatkowym HELU, przydzielone pierścienie nie są nowe SKU.
Oba wyjścia4MTA, odciążenia, pozostała wiązka, mocowania/skorupa i pełny
montaż nadal OPEN. R53/14z20=70%, CP2 niewybrany.
cad-layout-planning użyty do wspólnego układu odbiorników i całych łuków
przed podporami; katalogowe promienie oddzielone od prowizorycznych portów.

### Zachowane wejścia i cztery końce S1

Jeden wspólny plan: korpus S1 [114,2;37;64], rezerwa24×37×42mm,
sterowanie ku +Y. Katalogowe24×42/axial34, rozstaw12 oraz M4,5×6;
dodatkowe3mm głębokości, płaszczyzna końcówekY33 i główkiØ8×3 są
założeniami, nie pomiarem kieszeni. Osobny zewnętrzny budżet dźwigni
nie poszerza tułowia; otwór, podparcie gwintu i zdejmowany bok nadal OPEN.
Zaciski2/5 nominalnie Z85,3/6 Z73; oznaczenia i orientację sprawdzić na
dostarczonym S821. Cztery TE130171 już były przydzielone, nie dublować SKU.
Wejścia skierowane w+Z, wyjścia3/6 w−X/+X, zamiast nad mocowaniami nóg.

W067 P_SYS.3→S1.2 nominalnie200,09mm, W068 P_SYS.4→S1.5 231,16mm.
HELU23802 OD4,2/R25,2; każdy blank obejmuje14mm WAGO i14,452mm barrel
TE (strip do zacisku mieści się w tej ostatniej wartości, nie dodawać drugi raz).
Proste izolowane końce odpowiednio9/12,86 i10,3/10,67mm. To długości
do przymiarki, nie polecenie cięcia ani dodatkowe stare260mm odcinki.
Dwie górne trasy idą przeciwnymi korytarzami Y41 i około−0,3, następnie
schodzą doY33. Pierwsze wspólnie biegnące wejścia przecięły W066/siebie;
odrzucono je bez nadpisania dobrego modelu. Zmieniono kierunki korytarzy
i cały poziom S1, nie kolejne mikroprzesunięcia samych przewodów.

Lewy bank ATO ma teraz nominalny pitch30 (flange28+2 przerwy), prawy
pozostaje32; G2 przesunięte doY0.55 niezmienionych modułów używa wcześniejszego
dowodu. Przewody, pierścienie, śruby i cztery proste budżety śrubokrętaØ8/L30
nie przecinają reszty układu; to założone narzędzie, NIE katalogowy ruch.
0 przecięć/wyjść w sprawdzeniu brył. CAD51,532s; świeży reopen14 wire/strip,
8S0/16S1, objętości tras i parametr S1Z+1/przywrócenie:7,656s.
Kontrola obrysu przewodów używa swept pipe+2,4mm, nie bbox całej pętli.
Końcówki/narzędzia mieszczą się nominalnie bez dodatkowej tolerancji obrysu.

W tym wcześniejszym kroku oba wyjścia S1 były jeszcze otwarte; bieżący wynik powyżej.
Oba wyjścia4MTA, odciążenia, pozostała wiązka,
mocowanie, pełny montaż/serwis i stock nadal OPEN. To niewybrany CP2,
nie komplet S1 ani zamknięcie W1/W5. R53/14z20=70%, bez fizycznegoPASS.
Wykorzystano cad-layout-planning: wspólne podejścia czterech końców przed
projektowaniem podpór, rozdział danych katalogowych i założeń, jedna propozycja.

## Historia: obie strony S0, 06.10.2026

Zaciski S0 rozplanowane razem: IN z lewej, OUT z prawej, oba podejścia
TE130207 i istniejące dwie nakrętki/podkładki M10. Rozstaw24 i płaszczyzna
pierścieni80mm to rodzina/prototyp, NIE pomiar dostarczonego HELLA.
W076: fabryczny odcinek79,708mm<=84,5mm (minimum z rysunku, z11mm strip),
potem HELU23802 214,568mm z R25,2 i zakończeniami. W066239,765mm<=330mm,
R25,2,9mm prostego końca przy P_SYS. Nie wydawać polecenia cięcia przed
przymiarką. Nowe długości zastąpią stare, nie dublować żył/pierścieni.
Źródło nowego221-412 i rozdzielenie katalogu/założeń: `post-f0-splice-source.json`.
F0 nominalnie30A, złącze katalogowo32A; to NIE koordynacja zabezpieczenia,
dobór termiczny ani zamknięcie E3. HELU/odciążenia/stock pozostają otwarte.

P_REAR przesunięto do Y0, Splice_R3 dalej wzdłużX, S0 podniesiono8mm
i przesunięto16mmY; stare mocowanie nie jest zakwalifikowane w tej pozycji.
Trzy wcześniejsze trasy W001/W075/W043 zachowane.57 modułów ma niezmienione
dowody; nowe i zmienione interfejsy sprawdzone z zachowanymi rzeczywistymi bryłami.
Przewody, końcówki i17 rezerw dostępu bez kontaktów; obwiednia przewodu z
marginesem2,4mm sprawdzona jako swept pipe, NIE prostokąt obejmujący pętlę.
Reopen10 brył przewodów/strip i8 końcówek, objętości zgodne z długościami,
parametr nowego221-412 i przywrócenie sprawdzone. CAD42,125s, odbiór6,094s.

Odrzucono boczną pętlę przez WAGO nóg, korytarz krzyżujący W001 i osiowe
wyjście pierścienia OUT zahaczające rezerwację PCB. Zmieniono wspólną
orientację zacisków/podejścia, nie P0 ani obrys kota. Nie powtarzać tych prób.
W1/W5 nadal OPEN: narzędzia/mocowanie S0, W067/W068/S1, obie strony4MTA,
pozostałe przewody, odciążenia, skorupa, montaż i wybór. R53/14z20=70%.

Historycznie pierwsze dwie kontrole wykazały brak wspólnego warunku wysokości nad
mocowaniami nóg. Rozwiązanie: cały poziom oprawek oraz WAGO przesunięty
w górę; boczne listwy zwężone razem. Nie wycinano kolejnych dziur w starej
kasecie. Końcowa kontrola używa operacji na bryłach, a nie samego bbox:
rezerwacje nie przecinają się ani zachowanych części P0/głowy/ogona;
wewnętrzne rezerwacje z dodatkowym marginesem2,4mm mieszczą się w obrysie.
Klucz S0 i sterowanie S1 mają osobny zakres otworów obsługowych, nie zostały
udawane jako zamknięte pod skorupą. Ponowne otwarcie i parametr Pi sprawdzone.

## Uzgodnienie gabarytów i dostępu 06.10.2026

Aktualizacja źródeł: P_SYS wejściami w górę Z95..117, P_FRONT/P_REAR/D_RL
przełożone razem, G1 bliżej przodu. W043 F_PI.in→P_SYS.2 ma dwa dokładne
łuki R6, prosty odciążany koniec12mm i nominalny blank48,850mm obejmujący
14mm odizolowania, poniżej50mm. Wymodelowany przewód ma poprawną bryłę,
nie przecina sąsiadów/rezerw dostępu i mieści się w obrysie. Wyjście oprawki,
OD3,4/R6 i fizyczny punkt portu są prowizoryczne; nie oznacza to pomiaru
pasowania ani bezpiecznej koordynacji F0. Styki wewnątrz docelowych oprawek
wyłączono z kontroli rezerwacji korpusów, bo końcówki należą do tych korpusów.
Sprawdzono zmianę parametru P_SYS, nie ponowiono parametru niezmienionego Pi;
57 niezmienionych modułów korzysta z wcześniejszego dowodu i zgodnych hashy.
Pozostała wiązka nadal OPEN. W043 to jawny snapshot przewodu z buildera,
nie parametryczne zależności całej wiązki. Przebieg CAD35,625s.

Wejście baterii sprawdzono jako wspólny układ: XT60 obrócony90X, F0 wzdłużX,
minus do G1 wejściami w dół, MAIN obrócony obok przodu i dwa przełożone splices.
W075 bez dodatkowej spoiny przed F0: nominalny blank30mm (25mm trasy+5mm
umownego zakończenia lutowanego), <=50mm. W001 LAPP:102,056mm obejmuje
14mm WAGO i5mm lutowania, dwa rzeczywiste łuki R12,4 wg źródła przewodu,
34,1mm prostego odciążanego zakończenia. To długości do przymiarki, NIE
polecenie cięcia przed dostawą. W043 pozostaje48,850mm. Trzy przewody mają
poprawne bryły, nie przecinają sąsiadów ani siebie, rezerw dostępu i obrysu.
55 niezmienionych modułów korzysta z wcześniejszego dowodu, sprawdzono zmianę
G1 i pięć zapisanych brył przewodów/odizolowania. CAD37,688s, reopen G1 5,328s.
Poprzedni F0 wzdłużY odrzucony po przecięciach z S0/mocowaniem nogi/splice.
Rama nieprzerobiona; odrzucona próba nie nadpisała dobrego modelu.
Rozstaw kubków7mm, rzeczywista polaryzacja/położenie kupnego XT60, mated plug,
FHAC grubość/wyjścia oraz pola WAGO nadal do przymiarki. W075 jest fabryczną
żyłą F0, NIE dodatkowym LAPP. G1 nie ma dwóch przewodów w jednym porcie.
Przy wyborze tego układu nowe długości zastąpią dawne W001140/W07540/W04340,
nie są dodatkowymi odcinkami do sumowania. W076/F0→S0 i całe W5 nadal OPEN.

Nowy wspólny układ:10 bocznych WAGO niżej,10 centralnych WAGO pod pięcioma
poziomymi FHAC,12 ATO po bokach. WAGO pozostają podłączone przy nominalnym
dostępie do ATO. Sprawdzono razem12 prostych korytarzy wyciągania/narzędzia
ATO45mm i5 górnych budżetów dostępu FHAC40mm z marginesem2mm wXY.
Nie przecinają modułów ani rzeczywistych zachowanych brył. Reopen/parametr Pi
sprawdzone, końcowy przebieg CAD66,140s. To ZAŁOŻONE przestrzenie dostępu,
nie wymiarowany ruch dźwigni/zawiasu/narzędzia producenta. Boczne WAGO
wymagają zdejmowanych boków, centralne dźwignie i pełny demontaż nadal otwarte.

BUS to Waveshare25514, NIE adapter575070. Pełna obwiednia zapisanego modelu
producenta42,024×33,816×14,6mm obrócona90°; USB wychodzi w+X.
Zapisany compound ma117 brył, ale jedna jest niepoprawna. Nie naprawiono ani
nie pominięto części: do kontroli użyto pełnej prostokątnej rezerwacji,
nie wadliwego BRep. Dokładne pasowanie BUS nie jest zakwalifikowane.
U1/57507030,48×17,78mm należy do sterownika PWM1608; nie jest drugim BUS.

P309 ma41×25×12mm według wskazanego dostawcy, zamiast dawnej rezerwy35×25×11.
FHAC mają51mm maksymalnej długości i20,25mm szerokości. Pięć gałęzi ustawiono
poziomo ponad centralnymi szynami; oba wyjścia zachowane. Grubość22mm, OD3,4/R6 przewodu
pozostają założeniami. Fabryczne89,5±5mm obejmuje odkryty koniec; nie liczyć
go drugi raz jako dodatkowej długości. F0 obrócono poprzecznie w wolnej strefie
przed akumulatorem po wykryciu59,079mm³ kontaktu pierwszej rezerwacji z ramą.
Końcowe rezerwacje bez kontaktów; rama P0 bez zmian.

XT60H-M23,9×16,4×9,2mm dotyczy własnej połówki, NIE całej połączonej pary.
Druga połówka, wyjścia i ruch rozłączenia nadal wymagają przestrzeni.
Źródła i oddzielne założenia zapisane w `interfaces.json`.

## Granice tego wyniku i następny krok

Bryły są jawnie opisanymi rezerwacjami, nie dokładnymi modelami każdego SKU.
Podstawowe wymiary BUS/P309/FHAC/XT60 uzgodniono; pełne wyjścia/maty/obudowy
nie są jeszcze dowodem montażu. Rodzina HELLA, wsunięcie TE i wysokości wyposażonych
PCB są nadal założeniami prototypu. Wynik NIE dowodzi kompletnego montażu.

Proponowany poziom sygnałów Z66..76mm, nad Pi/pod sterownikami, NIE jest
wykonaną wiązką. Boczne WAGO wejściami w dół wymagają prostej9mm i pętli
R12,4 w dolnej strefie. Zakręty R25,2 większych trunków muszą mieć osobne
strefy w X/Z; oba wyjścia4MTA zachować. Złącze źródła
wróciło obok F0 zamiast wędrować na tył; droga przed bezpiecznikiem <=50mm
wymaga jeszcze rzeczywistych osi/pinów i pełnej trasy.

Następny krok: dopasować pełne zakończenia i wspólnie poprowadzić wiązkę
w tych strefach, z podparciami i granicami rozłączania. Dopiero potem
wykonać nośniki/skorupę. Nie projektować podpór pod same prostokąty.
Poprzednie górne WAGO stały nad bezpiecznikami. Policzenie granicy z istniejącego
netlist wykazało74 przewody wychodzące poza płytę i6 wewnętrznych połączeń.
Podwójne aliasy G1.5/G2.1 nie oznaczają dwóch fizycznych przewodów.
Odrzucono rutynową wymianę ATO wymagającą74 rozłączeń. Nowy plan bezpośredniego
dostępu ma17 sprawdzonych rezerwacji, nie gotowy serwis. PRZED podporami
domknąć wspólne przewody/dźwignie, obie strony4MTA oraz krótkie wejścia F0/F_PI;
potem mocowania, stock i jeden wybrany eksport. Nie przesuwać samej płyty.
Ruch/dźwignie/parkowanie końców nie zostały zakwalifikowane. Nowy221-412
jest tylko kandydatem, nie zakupem ani zmianą wybranego R53.

Slicer, druk i próby należą do fazy2. Brak fizycznego PASS.

## Bieżący nominalny stos12ATO/24TE, 06.10.2026

`ATOStackCandidate.FCStd` jest JEDNYM osobnym kandydatem planowania, nie
zestawem wydruków. Zachowuje pozostały CP2; nie zastępuje R53 ani bazowego
`WholeCatInterior.FCStd`. Zamiast12 pełnych pudełek28×26×64 ma osobne
12 obwiedni korpusów,12 wkładek,24 końcówki i12 budżetów dostępu. To nadal
obwiednie nominalne, NIE dokładny plastik/zatrzaski/zmierzone wsunięcie TE.

Wspólny datum kołnierzaZ126: panel-top124/underside122, dół korpusu97,5,
końce izolacji IN73,370/OUT75,402; górny ATO144,8, budżet wyciągania do189,8
po zdjęciu górnej osłony. Korpus28×15×28,5 i wymiary TE pochodzą z ENVELOPE.md;
e=0, osie±7mm i wystawanie ATO18,8 są jawnymi założeniami prototypu.
24 wyjścia izolacji mają dokładne ID przewodów i końce z wybranego R53;
9mm prostej pod chwyt jest wymaganiem projektowym, nie wykonanym odciążeniem.

63 pary BRep:0 przecięć rezerwacji,0 wyjść obwiedni z zapasem2,4mm,
0 błędów. Pozostałe265 brył zachowane, bez ponawiania ich wzajemnych kontroli.
FlangeTop126→127 przemieszcza wszystkie60 nowych pudełek+1Z; przywrócono126.
Świeży proces odczytał kopię z `tmp/ato-stack-reopen`:60 poprawnych brył,
24 jednoznaczne końce. CAD52,766s; pierwszy przebieg przerwał się przez brak
jednostek mm w wyrażeniach, nie dostarczył poprawnego CAD i nie jest dowodem.

Wymiana12ATO zakłada WAGO podłączone; nie dowodzi jeszcze ruchu dostarczonej
wkładki, chwytaka, zatrzasków ani pełnego montażu. Trasy24końców/podpory
muszą korzystać z tych datumów we wspólnym planie wraz z8MTA i źródłem.
Nie zmniejszać rezerwacji do rzekomej rzeczywistej bryły ani nie odtwarzać
odrzuconego source-bay. R53/14z20=70%, W1/W5 OPEN, bez fizycznegoPASS.

WAGO221-2411 jest kandydatem przeciwległych wejść, nie wybraną częścią:
`hardware/reference/wago-inline-2212411/source.json` i karta producenta2022.
Przewód drobnożyłowy0,2..4mm², wielodrutowy0,2..2,5mm²; klasa fabrycznej
żyły MTA OPEN. Cztery istniejące złącza wyjściowe zastąpić, nie dublować;
cztery ewentualne wejściowe dodać jawnie do przyszłego stocku. Ruch dźwigni,
rzeczywiste oba wyjścia MTA/L140, pełne8tras, mocowania i E3 nadal OPEN.
cad-layout-planning: wspólny stos i24przypisane końce przed podporami;
PDF: sprawdzony rysunek i instrukcja producenta, bez zakupu.

## Korekta przypisań złączy 221-412

R53 przewiduje pięć złączy zamontowanych i jedną sztukę zapasową, nie sześć
zamontowanych. Źródło: wybrane stock-r13 i katalog R53, ilość6 bez zmiany.
XB11 łączy W077/W078 (Pi/main); pozostałe cztery są połączeniami wyjść
W026/W037/W045/W053. Ich nowe przypisania do dotychczas anonimowych pól
CP2 są w `interfaces.json/splice_inventory`, nie dowodzą gotowych przewodów.
Rezerwacja 221-412 to14×19×9mm wobec katalogowych13×18,3×8,15mm.
Szósty nieprzypisany prostokąt usunięto; zapas pozostaje poza robotem.

Dwie odrzucone próby MTA dublowały cztery role wyjściowe, zachowując sześć
anonimowych rezerwacji obok ośmiu nowych złączy. Zachowane kolizje tamtej
geometrii nie dyskwalifikują poprawionej liczby elementów. Nie powtarzać
tamtych prób. Ewentualne cztery złącza przedłużeń źródłowych są dodatkowe,
natomiast cztery wyjściowe zastępują istniejące role. Z kandydatem post-F0
oznacza to10 zamontowanych +1 zapas =11 kandydatów, NIE wybrany koszyk.
Bez tych czterech przedłużeń:6 zamontowanych +1 zapas =7 kandydatów.

Kontrola zmiany: pięć nowych brył mieści się w poprzednich bryłach, pozostała
geometria natywna i18 brył przewodów/odizolowań pozostaje identyczna.
Test zmiennej długości14→15→14 i ponowne otwarcie dotyczą zmienionych złączy.
Nie powtarzano niezmienionych kontroli tras. W1/W5/stock/mocowania nadal OPEN.

## Wspólny plan ośmiu końców MTA: odrzucony

`mta-shared-plan.json` obejmuje cztery skośne oprawki i oba końce każdej,
osiem przypisanych złączy, zmienione odbiorniki nóg oraz wszystkie zachowane
bryły źródła/narzędzi/dostępu. Nie używa ponownie sześciu anonimowych splices.
Pierwszy plan:15 kontaktów/2 wyjścia poza obrys,26,016s obliczeń. Drugi
zmienia wspólnie kierunki tylnych oprawek, przednich źródeł i parę FR_P/G:
6 kontaktów/2 wyjścia poza obrys,26,484s; błędów Boolean0 w obu kontrolach.
Pozostałe przyczyny: FR source z XT60, RR output z P0_MountRearR,
przecinające się pary fabrycznych przewodów FL/RL oraz FR/RR,
rezerwacje przednich złączy poza obrysem z zapasem2,4mm. Nie akceptowano
układu ani nie zapisano go zamiast dobrego `WholeCatInterior.FCStd`.

Nie uruchamiać kolejnego niezmienionego planu ani drobnych przesunięć.
Następny wspólny plan musi przydzielić rozdzielone korytarze obu oprawek
i rozwiązać front z XT60/F0 jako całą strefę źródła. Jeśli ją przenosi,
unieważnia jawnie odpowiednie dotychczasowe trasy; droga przed F0 nadal≤50mm.
Pełne przedłużenia, fizyczne wyjścia/L140, mocowania, odciążenia, montaż
i stock pozostają OPEN. Nawet brak kontaktów samych ośmiu fabrycznych końców
nie zamknąłby W1/W5. Skrypt blokuje ponowienie niezmienionej odrzuconej recepty.
