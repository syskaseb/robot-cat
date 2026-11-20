**Pakiet20H do przymiarki bez zasilania. Duża podstawa dopiero po FIT_S0.**

# Montaż elektryczny WAVEGO bez zasilania

Instrukcja dla dwóch osób do kompletu cyfrowego CAD20 z zachowaną bazą19I i pierwszej przymiarki bez zasilania. Przez cały montaż i kontrolę odłącz główne złącze baterii, balanser oraz zewnętrzne USB. Zachowaj 57 pozycji bazy i ADD7. Fizyczne dopasowanie, rzeczywiste cięcia i luz pozostają nieustalone (`physical_PASS: false`). [Punkt wejścia](START_HERE.md)

## Przed drukiem dużych części ramy

Zmierz obie fabryczne żyły wybranego pakietu od wyjścia izolacji do wejścia w sztywną odgiętkę; osobno sprawdź pełne końce oraz dodatkowy fabryczny mały wtyk. Zdjęcie producenta zgodnego SKU GEA223S30X6GT wskazuje wyjście przy krótkim końcu, lecz nie podaje dokładnej osi ani długości. Stare 208 mm i górna pętla były trasą projektu19I; nie obowiązują jako długość dostawy ani wymaganie nowego wejścia. Porównaj egzemplarz z bieżącą instrukcją CAD20. Nie dodawaj przedłużki ani nie skracaj przewodów baterii.

Przymierz cały F0/FHAC0002 z klapką i obiema żyłami oraz wszystkie cztery MTA0100335 z klapkami i oboma końcami. Regulowane małe uchwyty przewidują przymiarkę, nie gwarantują wymiarów dostawy. Plan K3/r4 wybiera nominalnie 3 m LAPP0107001 i 9 m HELU23802; dostarczone ilości pozostają niepotwierdzone. Dopiero po ręcznym ułożeniu ustala się rzeczywiste cięcia i luz.

## Mapa i identyfikacja

Otwórz [POLACZENIA.csv](source/POLACZENIA.csv) z 134 połączeniami bazy i 26 ADD7. Jedna osoba odczytuje ID i koniec A, druga wskazuje koniec B na dostarczonej części. Oznacz oba końce tym samym ID, a cały kabel dodatkowo nazwą jego jednostki. H oznacza fizyczny pin Pi, BCM oznacza numer GPIO. USB_AUDIO i CSI_CAM to całe interfejsy.

Dla bazy używaj pól `a/b` w [design.json](source/design.json) i numeracji w [pinouts.csv](source/pinouts.csv). Dawne numery zacisków E4 sprawdzaj według aktualnych aliasów. Sieci można prześledzić w [schemacie PDF](source/robot_cat-schematic.pdf). Wybór części i połączenia ADD7 są w [selected-components.csv](source/selected-components.csv) i [connections.json ADD7](source/connections.json).

## Kolejność przy otwartych pokrywach

1. **Złóż mechanizmy i mocowania.** Kolejność przygotowania i przymiarek wskazuje [montaż](MONTAZ.md). Zamontuj podstawę, nogi, mechanizm głowy i ogona z pełnymi śrubami i nakrętkami oraz wsporniki modułów według odebranej rewizji. Dobór i ilości druków odczytaj z [bieżącego indeksu druku](PRINT.csv) z uwzględnieniem części wycofanych. Zostaw dojście od spodu i otwarte pokrywy.
2. **Osadź elektronikę i ochronę.** Zamocuj Pi z chłodzeniem, pozostałe moduły, banki oraz ochronę według przyjętych mocowań. Zachowaj pełne BAT/S0/S1/F0, MAIN/AUX, alarm, cztery MTA0100335 oraz dwanaście MTA0300330 z właściwymi TE IN/OUT i ATO. Zachowaj krótkie fabryczne końce par P_SYS–F_PI i P_REAR–F_AUX. PCA–E1 montuj jako lutowany zespół, a osiem inline 221-2411 rozmieść parami przy nogach zgodnie z mapą. Przymierz baterię odłączoną i sprawdź drogę jej wyjęcia.
3. **Zachowaj fabryczne końce i przygotuj łączenia.** Dopasuj klucze, zatrzaski i polaryzację według mapy oraz oznaczeń dostarczonych części. Stosuj przewidziane złącza i łączenia, zaizoluj każde wykonane łączenie i odciąż je na izolacji kabla. Pozostaw końce dostępne do kontroli. Wstrzymaj cięcie przewodów korpusowych do odbioru tras i przymiarki. Dla każdego z pięciu przewodów Pololu 600 mm dwie trasy wraz z zakończeniami, luzem i stratą cięcia muszą się zmieścić w tej jednej sztuce. Oba fabryczne styki pozostają przy Pi.
4. **Ułóż grupy ręcznie i sprawdź luz w ruchu.** Osobno prowadź baterię i ochronę, napędy, dane, optykę i audio. Każda oś MG ma własne dwie jednostki z tabeli poniżej. Przymierz pełne DATA500 Lanberg, POWER Delock 60047/K1474 i osobny USB_AUDIO ReSpeaker równocześnie przy Pi i chłodzeniu. W CSI FFC 15↔15 / 200 mm zachowaj strony styków, dostęp do zatrzasku i łącznie 10 mm na oba końce. ToF EXT011/012/013/014 prowadzą odpowiednio do JP3.2/6/3/4. Przy JP3.2 i JP3.3 sprawdź miedź, lut, początek izolacji i podkładkę. Źródłowe 12 mm na oba końce ToF licz raz. W odgałęzieniach 3V3/GND/SDA/SCL potwierdź pola i odciążenie. Używaj komór WAGO zgodnie z ich obsadą w mapie. AMP zachowuje własne MAIN5V1/GND EXT018/019 i W079/W080. Odizoluj oba przewody BTL głośnika od GND. Ręcznie sprawdź przewody w zakresie yaw ±20°, pitch ±10° i ruchu ogona góra–dół wokół Y. Sprawdź naciąg przy złączach, promienie, ocieranie i miejsca przycięcia. [Źródłowe końce](source/frozen-unit-receipt.json) · [Typy zakończeń JP3](source/typed-jp3.json)
5. **Zmierz ciągłość.** Przy odłączonej baterii, balanserze i USB jedna osoba sprawdza miernikiem dostępne końce odłączonej wiązki, druga odczytuje mapę i zaznacza wynik. Potwierdź przypisanie obu końców i brak przypadkowych zwarć pomiędzy odseparowanymi żyłami. Gdy podłączona elektronika wpływa na pomiar, odłącz badany odcinek. Przed wpięciem U1/575070 sprawdź jego orientację i ciągłość według numeracji. Sprawdź izolację przy śrubach i dostęp do wyłączników.
6. **Przymierz osłony na końcu.** Po kontroli kabli, odciążenia i ruchu sprawdź, czy pokrywy nie ściskają wiązek oraz zostawiają dostęp do baterii i wyłączników. Oznacz nierozstrzygnięte połączenia jako OPEN. Instrukcja kończy się na przymiarce bez zasilania.

## Całe przewody MG i JR

| Oś | Fabryczny przewód serwa | Osobny przedłużacz JR |
|---|---|---|
| Głowa, yaw | MG92B yaw, 250 mm | JR yaw, 300 mm |
| Głowa, pitch | MG92B pitch, 250 mm | JR pitch, 300 mm |
| Ogon, ruch góra–dół | MG92B tail, 250 mm | JR tail, 300 mm |

Zachowaj sześć oznaczonych jednostek, każdą z fabrycznymi końcami. JR to wybrane przedłużacze 586761. Podane liczby opisują całe jednostki. Projektowe trasy i podziały jednostek zawiera [bilans 19I](source-units.json). Rzeczywista długość zamontowana, cięcie i luz pozostają `null` do fizycznej przymiarki. Dawne JR500, W003310 i długości tras z referencji 160 połączeń pomiń przy wyznaczaniu nowych długości. [Budżety źródłowe 19.11](source/README.md)

## R7–R9 przy fabrycznych złączach MG/JR

Każdy z trzech wybranych MRS16000C1002FCT00 ma 10 kΩ. Łączy PWM za odpowiednim szeregowym R1–R3 z lokalną masą G_SYS przy złączu serwa. Jest to ściąganie sygnału do masy przy wyjściu U1 w stanie wysokiej impedancji. Źródłowy obwód przewiduje je po stronie serwa, poza kasetą E1. Funkcja zależy od ciągłości obu połączeń. [Obwód PWM](source/circuit.json) · [Rozmieszczenie elementów zdalnych](source/population.json)

| Rezystor | Punkt PWM | Druga nóżka |
|---|---|---|
| R7 | C_HY.PWM, sieć N_C_HY_PWM po R1 | C_HY.GND, sieć G_SYS |
| R8 | C_HP.PWM, sieć N_C_HP_PWM po R2 | C_HP.GND, sieć G_SYS |
| R9 | C_TY.PWM, sieć N_C_TY_PWM po R3 | C_TY.GND, sieć G_SYS |

Nazwy C_TY dotyczą wybranego serwa ogona poruszającego się wokół Y. Połączenia powyżej wynikają z [aktualnego grafu](source/design.json).

**Metoda proponowana warunkowo — `PROPOSED_CONDITIONAL`.** Na ciągłych żyłach wybranego JR586761, tuż za złączem łączącym je z MG, wykonać dwa przesunięte odczepy przez małe okna izolacji. Nóżki rezystora przylutować wzdłuż miedzi PWM i GND. Fabryczny przewód MG250, długość JR300, zakucia i pola sprężyste pozostają całe. Rezystor jest lokalnie przy parze serwa, na członie niosącym złącze. Dla pitch ten człon porusza się z yaw, lecz sam lutowany odcinek jest nieruchomy względem swojego podparcia i znajduje się poza pracującą pętlą.

Starszy kontrakt pozostawia rozwój metody przejścia otwarty. Ta propozycja rozwija montaż lutowanego prototypu. Wcześniejszy sposób lutowania nóżek bezpośrednio do zachowanego styku pozostaje niezweryfikowany. [Kontrakt MG/JR](source/interface.json) · [Zaplanowane wolne końce JR](reference19I/whole-termination-plan.json)

1. **Rozpoznaj żyły i miejsce.** Odłącz baterię, USB, serwo i końce korpusowe JR. Jedna osoba odczytuje PWM i GND z tabeli, druga identyfikuje ich ciągłość w odłączonym JR i oznacza widok złącza. Użyj właściwej dokumentacji dostarczonej pary. Kolor i raster nie ustalają pinów. Oznacz odcinek statyczny przy złączu, poza nadlewem, zakuciem i wyjściowym odgięciem kabla.
2. **Najpierw załóż zamknięte koszulki.** Przed wykonaniem zaplanowanych spoin korpusowych nasuń po jednej koszulce TF31-3/1 na indywidualną żyłę PWM i GND od ich dostępnych wolnych końców, przesuń w pobliże przyszłych okien i odsuń od grzania. Rozdzielenie płaskiej wiązki jest dopuszczalne tylko bez naruszenia izolacji. Jeśli dostarczony JR ma na drugim końcu zamkniętą obudowę, sprawdź przejście koszulki przez sam terminal dopiero po udokumentowanym, odwracalnym wypięciu styku z rzeczywiście rozbieralnej obudowy. Zachowaj mapę komór, języczek i ponowne zatrzaśnięcie. Przy obudowie zalanej lub niewypinanej oraz braku wolnego końca droga nasunięcia pozostaje OPEN. Nie otwieraj dodatkowej żyły przez jej przecięcie ani nie rozcinaj koszulki wzdłuż.
3. **Przymierz rezystor i izolację nóżek.** MRS16 ma według zapisanej karty korpus maksymalnie Ø1,6 × 3,6 mm i nóżki nominalnie Ø0,5 mm. Uformuj je z podparciem, bez zginania przy korpusie. Nasuń na każdą nóżkę CR3042-000 od jej wolnego końca przed lutowaniem. Pozostaw odsłonięty tylko planowany fragment zakładki, a koszulkę odsuń od grotu. Połączenie ma wyjść z końca TF31 już jako izolowana nóżka. [Karta MRS16, strona 3](source/mrs16m25.pdf) · [CR3042-000](source/sleeve-facts.json)
4. **Przygotuj dwa okna.** Robocza propozycja to okno do 3 mm na PWM oraz do 3 mm na GND, z przesunięciem środków o 20 mm wzdłuż kabla. Usuń tylko izolację nad miedzią. Żadnego drucika nie wolno naciąć ani odciąć. Przymierz nóżki równolegle do żył, z wyprowadzeniem ku końcowi każdej koszulki. Jeśli dostępny przewód lub narzędzie nie pozwala odsłonić okna bez uszkodzenia linki, wykonanie pozostaje OPEN.
5. **Lutuj na stole.** Ustal kabel i rezystor tak, aby spoiny nie przenosiły obciążenia montażowego. Zastosuj wybrane spoiwo Weller T0051402499 i proces odpowiedni dla rzeczywistej izolacji JR. Ogranicz podciąganie cyny pod izolację, skontroluj ciągłość wszystkich drucików, obie spoiny i obudowę złącza. Grzanie wykonuj poza PETG i baterią. Podane okno jest propozycją wykonawczą, a dopuszczalny czas i temperatura grzania dostarczonego JR wymagają potwierdzenia.
6. **Zaizoluj odczepy osobno.** Osłoń nóżki CR3042 do korpusu i przesuń TF31 na każde połączenie. Po obkurczeniu wymagane są pełne zakrycie metalu oraz co najmniej 6 mm zakładki na nienaruszoną izolację kabla po obu stronach okna i na osłonę wychodzącej nóżki. Przy wyjściu odgałęzienia sprawdź zakrycie z każdej strony. Dopasowanie koszulki do kabla wraz z nóżką i do cieńszego kabla obok spoiny musi być sprawdzone na rzeczywistej sztuce. Koszulka CR3042 ma źródłowo otwór przed obkurczeniem co najmniej 1,02 mm i po pełnym obkurczeniu najwyżej 0,33 mm. Potwierdź przesuwanie, dopasowanie i długość po obkurczeniu obu typów.
7. **Podeprzyj i policz miejsce.** Korpus i osłonięte nóżki połóż w istniejącym podparciu przy złączu. Istniejące odciążenia mają chwytać izolację poza usztywnionymi spoinami. Spoiny, nóżki i koszulki nie zastępują odciążenia. Roboczo zarezerwuj 50 mm statycznej długości na JR, obejmujące przesunięcie 20 mm, koszulkę do 20 mm i po 5 mm dojścia do odciążenia. Przekrój mierzy się z gotowym rezystorem, obiema koszulkami i pełną parą wtyków. Jeśli ten obrys nie mieści się w istniejącej stacji, dopasowanie pozostaje OPEN.
8. **Pierwszy z trzech zespołów sprawdź bez zasilania.** Przed podłączeniem serwa i elektroniki porównaj rezystancję PWM–GND z wartością zmierzonego osobno rezystora 10 kΩ. Sprawdź ciągłość obu torów i V+, brak zwarcia do V+, pełne wsunięcie i zatrzymanie pary. Obejrzyj izolację przy delikatnym poruszeniu odciążonym przewodem. Następnie ręcznie sprawdź wymagany ruch z dostępem do wiązki. Wynik dotyczy tej dostarczonej sztuki. Każdy pozostały zespół także wymaga kontroli.

**Rozliczenie propozycji.** Na trzy rezystory przewidziano sześć blanków TF31-3/1 po 20 mm, razem 120 mm, i sześć blanków CR3042-000 do nóżek po 15 mm, razem 90 mm. Są to nowe debety w istniejących typach materiału. Źródłowy plan ma po 200 mm rezerwy każdego z tych typów. Przed wykonaniem potwierdź rzeczywistą dostępność i pozostałe przydziały, a także czy blanki po obkurczeniu zapewniają opisane zakładki. Plan nie potwierdza posiadania materiału. [Materiały, spoiwo i rezerwy](source/phase1-material-selection-r4.json)

Odcinek statyczny jest częścią dotychczasowych 246 mm transportu i zapasu, więc roboczy podział każdego JR to `12 + (50 + 196) + 25 + 9 + 8 = 300 mm`. Potwierdź, że pozostała długość wystarcza na rzeczywistą trasę i wymagany ruch. Powstające usztywnienie nie może zużyć zapasu pętli. Nie dodano długości kabla ani dodatkowej jednostki. Nóżki muszą wystarczyć po uformowaniu i osłonięciu. Rzeczywiste cięcia, dopasowanie i luz pozostają `null`, `physical_PASS=false`.

## Zakres cyfrowy i przymiarka fizyczna

Odebrany 19I rozstrzyga wcześniejsze znane kolizje w przyjętym zakresie cyfrowym. Bieżące mocowania, zamknięcie i trasy wyznaczają model, instrukcja montażu i bilans 19I. Warunkowe odczepy R7–R9 mają lokalne podparcia i przydział 50 + 196 mm w 246 mm JR. Dostarczone części wymagają opisanych pomiarów, przymiarki izolacji i ręcznego sprawdzenia ruchu. Głębokie pozycje nóg pozostają materiałem planistycznym. [Zakres odbioru 19I](reference19I/decision.json)

## Przymiarki i warunki elektryczne

- **Cztery MTA0100335 z MINIVAL 10 A.** Zachowaj każdą oprawkę z pokrywą, uwięzią i oboma nieciętymi przewodami. Gabaryt pełnej oprawki, obrys zamkniętej i otwartej pokrywy, średnica zewnętrzna izolacji i długość każdego z dwóch przewodów pozostają UNKNOWN. Przymierz całą oprawę do właściwego osobnego uchwytu C20_MTA_FL/FR/RL/RR z [bieżącego indeksu](PRINT.csv), poza dużą ramą. Nie oceniaj całego korpusu na podstawie dawnej płaskiej próbki19I. Na właściwej dostarczonej sztuce zapisz oznaczenie lub rewizję, gabaryty z bezpiecznikiem i pokrywą, miejsce obu wyjść, średnicę izolacji i długość osobno od wyjścia izolacji z oprawki do faktycznego końca każdego przewodu. Sprawdź zgodność czterech dostarczonych sztuk. Katalogowe L120 i L140 pochodzą z różnych rewizji i nie ustalają długości żadnego z dwóch końców. W [MATERIALY.csv](source/MATERIALY.csv) pomiń 84,5 mm dla W026, W037, W041, W042, W044, W045, W052 i W053 oraz to przypisanie w kroku 3 dawnej referencji. Zakres 84,5–94,5 mm dotyczy końców FHAC. Cztery osobne przewody stykowe E2/JPWM mają po 225 mm nominalnie i źródłowy budżet 220 mm na sztukę z zachowaniem obu dostarczonych końców. [Dane jednostek 19.11](source/source-budget.json)
- **Alarm MOD05015/P309.** Patrząc na tylną etykietę, z pinami po lewej, kolejność od dołu to minus, 1S, 2S, 3S. Role logiczne to odpowiednio BAT.B0, B1, B2 i B3. Fizyczne komory BAT G-Tech dla B0/B1/B2/B3 oraz pozycja ID pozostają UNKNOWN. Zamocuj alarm i zostaw jego wtyk odłączony oraz dostępny. Do późniejszego połączenia potrzebna jest dokumentacja producenta dla dostarczonej rewizji, która wiąże role i ID z numerami komór oraz określa stronę patrzenia. W tym montażu pozostaw komory niepodłączone. Nie sonduj złącza baterii ani nie identyfikuj go po kolorach. Styk ID pozostaje bez połączenia z alarmem. [Mapa logiczna bazy](source/design.json)
- **Warunki elektryczne.** Kwalifikacja ochrony SOURCE/LEADS/CLEARING/TRANSIENTS, budżety MAIN/3V3 i fizyczne wykonanie odgałęzień ADD7 pozostają otwarte po pomiarze ciągłości. [Zakres schematu](reference/hardware/electronics/kicad-current/README.md)

## Powiązanie pakietu i historia

Instrukcja jest powiązana z odebranym kompletem cyfrowym 19I w [SOURCES_ELECTRICAL.json](SOURCES_ELECTRICAL.json). Archiwum 19I zachowuje zamrożoną kopię przewodnika i mapy w folderze source. Wcześniejsze odbiory oraz dokładne bajty źródeł wykorzystanych przy odbiorze 19I zachowano w sekcji historycznej tego JSON. Obecna aktualizacja tekstu nie zmienia zapisanego modelu ani wyniku przymiarki fizycznej.

## Aktualna przymiarka opraw

Cztery małe uchwyty C20_MTA_FL/FR/RL/RR w [PRINT.csv](PRINT.csv) są osobne.
Przymierz do każdego rzeczywistą oprawę MTA0100335 z klapką i obiema żyłami.
FIT_S0 i kolejność montażu całego wyłącznika
opisuje [bieżące wejście baterii](WEJSCIE_BATERII.md). Rozliczenia19I zachowują
niezmienione jednostki; dla W001/W075/W076 oraz W066 obowiązuje nowszy
interfejs i bilans całych jednostek. Rzeczywiste cięcia i luz pozostająNULL.
