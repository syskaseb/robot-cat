# 20B | Wejście baterii i uchwyty MTA

**Propozycja do recenzji całego układu.** Zaparkowana para XT60H-M + XT60H-F leży nad narożnikiem pakietu. Przy rozpinaniu jedna osoba trzyma nieruchomą połówkę pakietu. Druga zwalnia i przesuwa w −X o 14 mm stronę instalacji wraz z F0 i POST_F0 na jednym otwartym nośniku. Zespolony ruch chroni krótki W075 i oba fabryczne przewody F0 przed zmianą geometrii podczas skoku. Domknięcie całej obsługi baterii zależy od przejścia jej rzeczywistego wyjścia przez górny próg drzwi. [Rzut i przekrój](20B-przekroj.png)

Baza cyfrowa to commit `1d428594af9db9f49fa931e72d51fe48f611a21d` i `whole-cat20A.FCStd` o SHA-256 `365633e3f78d40f6140c7169a1fd67dd5a9141935ca7c6937dba5ed664bd4f46`. Model 551 obiektów dostarcza geometrii sąsiadów w układzie świata. Pierwszy widok zachowuje wszystkie 57+ADD7, osiem kotew, S0, Pi z chłodzeniem, napędy, nogi, ruch głowy i ogona oraz zewnętrzną skrzynkę. Decyzja o materiale i mocowaniach nastąpi po odbiorze geometrii całego interfejsu. [Inwentarz modelu](20B-native-inlet-inventory.json) · [Widok zewnętrzny 19I](../day19-complete-first-fit/three-quarter.png)

## Rozmieszczenie i pierwszy test

Przedziały X/Y/Z podano w milimetrach. F0 to wybrany Littelfuse FHAC0002ZXJ, z dwoma fabrycznymi żyłami pomarańczowymi 12 AWG. Rysunek rodziny podaje 50 ±1 długości i 17,2 ±0,25 przekroju korpusu oraz pokazuje klapkę na uwięzi z własnymi wymiarami 20 ±0,25 i 21,2 ±0,25 mm. Orientacja w układzie ma umożliwić otwarcie klapki w stronę wnętrza przy zdjętej pokrywie. Zamkniętą klapkę, jej przebieg i położenie fabrycznych odgiętek trzeba porównać z dostarczonym FHAC0002. [Rysunek rodziny FHAC](../../../../../../../reference/fhac0001zxj-2026-10-02/datasheet.png)

| Element | X | Y | Z | Test |
|---|---:|---:|---:|---|
| BAT w istniejącym gnieździe | −12…94,5 | 20…55 | 52…73,5 | Korpus źródłowy 106,5 × 35 × 21,5. Wyjścia [86,5; 32,65; 73,5] i [86,5; 27,35; 73,5] są projektowe. |
| Para XT60H z obiema osłonami | 1…51 | 18,8…42,8 | 112,5…130,5 | Rezerwa instalacyjna 50 × 24 × 18. Przyjęto źródłowe połówki M i F oraz osłony. Dokładny obrys konkretnej połówki pakietu pozostaje do pomiaru. |
| F0 zamknięty | −70…−19 | 30…50 | 111,65…129,15 | Pas pomiędzy kanałem sterowania do Z110 i lokalnym żebrem od Z130,4. Wąska rezerwa na korpus i zamkniętą klapkę. |
| F0, miejsce na klapkę i bezpiecznik | −51…−5 | 18…41 | 129,15…175 | Przestrzeń dostępna po zdjęciu pokryw i podparciu mikrofonu wraz z jego pokrywą. Kierunek otwarcia i faktyczny chwyt do sprawdzenia na próbce. |
| WAGO 221-412 POST_F0 | −106…−86 | 36,75…49,75 | 116,5…126,5 | Oba porty od +X. Dźwignie mają osobne podejście od góry. |
| Chwyt przy rozpinaniu | −17…58 | 12…46 | 132,3…161 | Górna rezerwa między korpusami. Sprawdzono obwiednię po zdjęciu pokryw. |
| S0 i G1.2 | — | — | — | Zachowana geometria. Końce przewodów na S0.in [161,5; 74; 113,16] i G1.2 [−0,5; 70; 151]. |

Pierwsza obwiednia XT60 weszła w BNO i regionalne pole sterowania. Podniesiona weszła w obrzeże od Y44,7. Pas po wewnętrznej stronie tego obrzeża przechodzi sprawdzenie złożonych obwiedni XT60, F0 i POST_F0 oraz pokryw. Przesunięcie samej połówki pakietu o +14 mm ściskało projektową trasę żył do ok. 5 mm wewnętrznego promienia w próbnej krzywej. Przesunięcie całej strony instalacji po zdjęciu pokryw zachowuje obrys fabrycznych żył pakietu. Odpowiednie obwiednie sztywne i droga chwytu przeszły sprawdzenie z nazwanymi sąsiadami. Analiza porównuje obwiednie z bryłami 19I, w tym zebranymi polami przewodów i chłodzenia. [Niższy układ](20B-first-screen.json) · [Podniesiony układ](20B-raised-screen.json) · [Wybrany pas](20B-inboard-screen.json) · [Skok nośnika](20B-carrier-screen.json)

**Drzwi +Y wymagają decyzji po pomiarze pakietu.** Przy zachowaniu pozycji korpusu w otworze Z51,35…74,15 nad pakietem zostaje 0,65 mm. Odcinek górnego progu pozostaje w `E19_RearBase` po zdjęciu `E19_BatteryDoor`. Przecięcie strefy przypuszczalnego wyjścia [82…92; 97…103,05; 73,5…81] z tą podstawą wynosi 181,101 mm³. Sprawdzenie trzeba odnieść do faktycznego kierunku wyjścia i sztywnej odgiętki. Jeżeli pokrywają się z tym obszarem, proponowany układ wymaga lokalnie zdejmowanego odcinka górnego progu między sąsiednimi oparciami. Najpierw potwierdzić jego funkcję w ścieżce obciążenia, przejście fabrycznych końców i zamknięcie drzwi. [Test progu](20B-door-exit.json)

## Cztery stanowiska MTA0100335

Otwarty nośnik ma dwa rozstawne punkty opaski lub mocowania na osobnym małym drukowanym elemencie. Regulacji podlegają podparcie długości, rozstaw opasek i lokalny rozkład wyjść. Pole próbki **32 × 18 × 18 mm** obejmuje korpus zamknięty, łącznie z bezpiecznikiem i klapką. Obok korpusu pozostaje wymagany dostęp do obu niezależnych fabrycznych przewodów i elementu regulacji. To projektowy korpus próbki. Próba na wszystkich czterech sztukach rozstrzygnie, które otwory i oparcia wystarczą. Przy większym korpusie, wyjściach kolidujących z sąsiednim złączem lub klapce poza poniższą przestrzenią trzeba wrócić do ułożenia pełnej jednostki i jej przewodów. [Kupon 28 × 20 × 2,6 z 19I](../day19-simple-box-common-core/components/E19_MTA_sample_land.stl)

| Stanowisko | Strefa zamknięta X / Y / Z | Dostęp po zdjęciu pokrywy |
|---|---|---|
| FL | −49…5 / −100…−78 / 140…161 | Ponad obwiednią JR. Otwarcie od góry do Z184. |
| FR | −68…−28 / 67,5…89,5 / 144…165 | Pole klapki ograniczone do X−63…−28 nad Z165. Szerszy obrys trafia w przednią ramę. |
| RL | 100…154 / −98…−76 / 141…162 | Otwarcie od góry do Z185. |
| RR | 141…195 / 60…82 / 140…161 | Otwarcie od góry do Z184 po podparciu zdejmowanej pokrywy z modułami. |

Wszystkie cztery zamknięte strefy minęły nazwanych sąsiadów w modelu. Testy nie rozstrzygają długości obu końców ani skierowania fabrycznych wyjść do odpowiadających im zacisków. Zmiana podpory, rozstawu i klina w podanym gabarycie dotyczy małego uchwytu. Jego połączenie z istniejącą podporą podlega następnemu etapowi po zamknięciu sekwencji montażu. [Bryły sąsiadów i pola MTA](20B-inboard-screen.json) · [Sprawdzenie okna klapki FR](20B-pocket-screen.json)

## Długości i odciążenie

| Jednostka | Projektowe odcinki i warunek |
|---|---|
| Obie fabryczne żyły pakietu | Od przewidywanego wyjścia izolacji do końca odgiętki XT60 projektowa droga wynosi ok. 64,2 mm (+) i 64,1 mm (−). Z 8 mm rezerwy ułożenia potrzeba ok. **72,2 mm (+) i 72,1 mm (−)** w tej definicji pomiaru. Przy pomiarze do punktu elektrycznego trzeba osobno doliczyć rzeczywiste odcinki w obu końcach. Skok rozpinania nie dodaje długości po stronie pakietu. |
| W075, pierwszy koniec FHAC0002 | **20,32 + 5 = 25,32 mm** do istniejącego miejsca zakończenia XT60 wobec limitu 50 mm. Fabryczne wyjście F0 pozostaje podparte, obie osłony XT60 zachowane. Wewnętrzny promień modelowy wynosi 26,12 mm przy obwiedni Ø4,8 mm. |
| W076/factory, drugi koniec FHAC0002 | W osi do POST_F0 wymagane minimum projektowe **16 + 11 = 27 mm**. Pomierzyć obie fabryczne żyły F0, środek i podparcie wyjść, faktyczne diametry oraz długości przygotowanych końców. Na nadmiar zachowanej fabrycznej żyły przeznaczono pole 34 × 29 × 32 mm nad nośnikiem, X−105…−71, Y30…59, Z134…166. Obwiednia minęła nazwanych sąsiadów w pozycji zamkniętej i przy skoku. Ułożenie całej rzeczywistej długości, wejście do pola i właściwy promień nadal wymagają sprawdzenia. [Sprawdzenie pola](20B-pocket-screen.json) |
| W001, czarny LAPP 0107001 12 AWG | Ciągła żyła do G1.2. Podejścia w modelu 98,74 / 111,75 mm. Z 19 mm na końce i 15 mm ułożenia zapotrzebowanie projektowe **146 mm**. Źródłowe Ø3,1 mm i rezerwa Ø4,8 mm w kieszeni złącza. |
| W076/custom, HELU 23802 | Odcinek chroniony z POST_F0.2 do S0.in. Podejścia w modelu 266,63 / 280,53 mm. Z 26 mm na końce i 20 mm ułożenia zapotrzebowanie projektowe **327 mm**, Ø4,2 mm. |

Do AUX zastosowano osobny lokalny test, ponieważ ogólna obwiednia nie rozstrzyga mijania narożnika płytki. Dla założonych wyjść i Ø4,8 mm próbka przebiegu daje ok. **1,44 mm** do bryły PCB AUX, z modelowanym promieniem wewnętrznym ok. **13 mm** na obu żyłach pakietu. Do przymiarki przyjąć rzeczywistą średnicę, miejsce wyjścia, nadlew złącza i akceptowalne zgięcie dostarczonych przewodów. W001 i chronione HELU mają wspierane pierwsze odcinki na ruchomym nośniku oraz odciążenie przed miejscem przejścia do stałych kanałów. Zapas ruchu rozkłada się po zwolnieniu zaczepów. Budżety W001 i HELU wynikają z przejść regionalnych, więc długość i ułożenie z pełnymi końcówkami sprawdza się na prototypie. Projekt zachowuje jeden ciągły W075 przed F0, ciągłe W001 oraz wybrane POST_F0 za ochroną. [Długości i próbki krzywych](20B-dlugosci.json)

Stan dostępnych długości LAPP i HELU jest **UNKNOWN**. 2 m/2 m pochodziły z planu koszyka, a 4 m/5 m to wariant nieprzyjęty. Powyższe zapotrzebowania dotyczą tylko zmienionych jednostek.

## Kolejność dla dwóch osób

1. Na odłączonym prototypie podeprzeć zdjęte pokrywy z ich wyposażeniem. Stabilnie osadzić i oznaczyć pełne BAT, F0, oba korpusy XT60 i POST_F0, potem ułożyć W001 i chroniony HELU w wspólnych zajętych regionach. Przymierzyć każde MTA z oboma końcami przed założeniem pokryw.
2. Oprzeć i odciążyć oba końce w otwartym nośniku. Sprawdzić chwyt obudów oraz niezależne prowadzenie przewodów. Domknąć klapkę F0, zamknąć drzwi i pokrywy z kontrolą przycięcia.
3. Do wyjmowania otworzyć pokrywy i zwolnić nośnik. Ustawić głowę neutralnie. Pierwsza osoba trzyma połówkę pakietu, druga przesuwa stronę instalacji o 14 mm. Odłożyć rozpięte izolowane połówki, zwolnić pasy i drzwi, a pakiet i fabryczną odgiętkę przeprowadzić przez sprawdzone przejście +Y po rozstrzygnięciu progu.

**Decyzja 20B.** Przekazać ten układ do jednej recenzji całości. Przed szczegółem rozstrzygnąć próbkę BAT i próg, obie pełne fabryczne żyły F0 z rzeczywistą klapką oraz dostęp do pokryw i obu końców czterech MTA. Fizyczne `actualfit`, `cut`, `slack` pozostają `null`, `physicalPASS=false`. Wejście Banacha `01a1f91c-36eb-7c70-8a49-9d8023b132ac`.