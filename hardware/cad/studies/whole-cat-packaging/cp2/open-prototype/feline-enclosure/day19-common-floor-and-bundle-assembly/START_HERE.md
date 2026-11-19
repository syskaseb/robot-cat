# 19B — podłoga na ośmiu kotwach i montaż tylnego JR

**Stan złożenia: HOLD.** Przymiarkę przewodów głowy blokują powierzchnie obecnego tyłu czaszki i barków. Zapis 19B jest bazą następnej pracy. Punkt wyjścia to zamrożone 19A z commitu `0736a387`.

[Złożenie FreeCAD](whole-cat19B.FCStd) · [Przekroje na kotwach, wale yaw i wale ogona](critical-sections.png) · [Przód](front.png) · [Bok](side.png) · [Widok ¾](three-quarter.png) · [Wnętrze z regionem JR](interior.png)

## Co można przejąć

Przednia i tylna podłoga mają po jednej bryle i po cztery kotwy. Na wszystkich ośmiu lokalnych wycinkach powierzchnia bazy dochodzi do podłogi na Z=38,52 mm. W oknie 9,2 × 9,2 mm wokół każdej osi wspólne płaskie powierzchnie mają 78,41–78,48 mm². [Płaszczyzny oporowe i pełny osprzęt yaw](anchor-seats.json). Przednie ukośne żebra łączą gniazda kotew z obrobioną częścią gniazd 608. Siodło yaw i dolny kołnierz szyi są integralnym materiałem przedniej podłogi. Dotychczasowe szyny, portal, ruszty, siodło yaw i wewnętrzna skorupa szyi są wycofanymi obiektami odniesienia w pliku. Nie dodawać ich do zamówienia druku. Model zachowuje oddzielne źródłowe śruby i serwa. Tył ma dwa oparcia mechanizmu ogona, cztery tuleje przy wspólnej płycie PCA–E1 i dostępny od góry pokład JR. [Wynik sprawdzeń](changed-checks.json) · [Dwie bryły STEP po ponownym imporcie](floor-step-receipt.json)

Oba eksporty STEP ponownie wczytano jako pojedyncze poprawne bryły. Różnica objętości po imporcie przedniej wynosi 1,66 mm³ na 75 714 mm³ (0,0022%).

Przy neutralnym ustawieniu materiał obu podłóg jest rozdzielony od pełnych śrub H01, MG yaw i MG tail, obu 608 yaw, wału poprzecznego yaw z osprzętem, pól DATA i połączonego JR. Sprawdzono walcowe dojście wkrętaka Ø5,3 mm przez 38 mm nad łbami H01 przy pustym nośniku. Wspólne 847 mm³ z dawnym siodłem yaw wynika z jego włączenia do nowego wydruku. Fizyczna długość zazębienia i dopasowanie klucza wymagają przymiarki na posiadanej bazie. [Przód STEP](B19_FrontFloor.step) · [Tył STEP](B19_RearFloor.step)

## Kolejność dwóch osób do przymiarki bez zasilania

1. Na pustą bazę założyć oddzielne podłogi. Jedna osoba dociska pary płaszczyzn oporowych, druga wprowadza od góry osiem źródłowych M2,5×16 w osiach X −80, −70, 112 i 122 oraz Y ±22,5. Sprawdzić dosiad łbów i zazębienie przed założeniem modułów.
2. Przed osłoną i częścią optyczną wprowadzić pełny yaw w siodło od otwartej strony. Druga osoba podtrzymuje korpus serwa przy montażu śrub uszu, pełnego zestawu łożysk, nakrętek i sworznia. Przebieg przewodu musi opuścić siodło przed zasłonięciem wyjścia.
3. Na tyle osadzić oddzielne siodło MG i nieruchomy kartridż 608 na poprzecznych płaszczyznach oporowych. Druga osoba podaje pełne śruby, podkładki i nakrętki od otwartej strony. Stopa serwa, część obracana i fabryczny przewód zachowują osobne role. [Przebieg korzenia przy −15°, 0°, +15° wokół Y po poszerzeniu tylnej krawędzi otworu](tail-swing.json)
4. Wsunąć oba paski baterii 15×200 przez otwory siodeł przed osadzeniem baterii. Klamra wchodzi do długości całego paska. Sprawdzić zapas i dostęp do baterii z rzeczywistą obsadą. Umieścić cały lutowany PCA–E1 na czterech tulejach, wykorzystując źródłowe komplety śrub. Droga wyjęcia baterii po założeniu pozostałych modułów jest otwarta konstrukcyjnie do rozwiązania.
5. Przy pustym lewym banku połączyć pełne złącze ogonowego MG250 z JR300. Włożyć JR od góry w płaski nawrót pod bankiem. Jego przydział wynosi 12 mm wtyku + 246 mm wspólnego przebiegu i zapasu + 25 mm rozprowadzenia + 9 mm odcinka izolowanego + 8 mm zakładki = 300 mm. R wewnętrzny 22,25 mm. Osobne wyjścia XB32 → F_TY.out, XB33 → G_TAIL.5, XS33 → R3.2. Koszulka 20 mm osłania połączenie. Pełne 250 mm z serwa nadal wymaga osobnego ułożenia. Po założeniu opaski dopuszczalne jest odcięcie zbędnego końca tworzywa. [Sprawdzenia złącza, nawrotu i zakończeń](changed-checks.json)
6. Wstawić całe pary F_PI–P_SYS i F_AUX–P_REAR. Zachować po dwa fabryczne wyjścia każdej oprawy i możliwość otwarcia pokryw. Pełne MTA0300330 z końcami leżą w bankach. Kształt regulowanych mocowań czterech osobnych MTA0100335 wymaga dostarczonej próbki. Testy pozostałych mocowań i dostępu do pokryw są otwarte.

## Przewody głowy i zmienione stacje

Cztery przewody ToF zachowują pad JP3.2, .6, .3 i .4 oraz Ø2,1 mm. Przeniesienie płyty dało nowe końce na X=75, Y=40. Przeliczono cały stały odcinek do każdego pola lutowniczego. Robocze długości 615–630 mm zawierają jeden łączny debet 12 mm na końce. To propozycje tras odrzucone na obecnej geometrii. Nie ciąć według nich. FFC ma nadal 190 mm swobodnych i 10 mm łącznie na końce. W pięciu pozach sprawdzono wejście przewodów w nowy materiał. Znaleziono punkty wspólne ruchomej wiązki ToF z barkiem i tyłem głowy, czterech stałych gałęzi z tyłem głowy oraz FFC z tyłem głowy. Źródłowe oparcie stałej wiązki na X=−145, Y=58, Z=178 wypada wewnątrz strefy ruchomej głowy. Następna zmiana obejmuje położenie stałego odbioru na barku, ruchomy zapas oraz zachodzące na siebie osłony po obu stronach tego przejścia. [Pełne ślady i bilanse](head-field-result.json)

| E2 | Pełne zakończenia | Przydział |
|---|---|---|
| XP02.source | F_PWM.out → JPWM_SOURCE.1 | osobne 220 mm |
| XP03.source | G_TAIL.3 → JPWM_SOURCE.2 | osobne 220 mm |
| XP02.module | JPWM_MODULE.1 → U_PWM.3 | osobne 220 mm |
| XP03.module | JPWM_MODULE.2 → U_PWM.2 | osobne 220 mm |

Zestawienie E2 wiąże cztery odrębne jednostki z grafem. Brakuje osadzenia obu połówek złącza oraz sprawdzenia dojść do czterech rzeczywistych końców i miejsca na nadmiar. DATA500 ma warstwę szerokości 9,8 mm wokół odcinka magazynowania, z oddzielnymi podejściami do obu portów do sprawdzenia. USB_AUDIO wymaga wymiaru dostarczonej sztuki. POWER ma własne końce. Stan ról modułów, zachowanych długości i źródeł obejmuje [odebrany budżet 57+7](../day19-source-bom-budgets/README.md).

## Druk, masa i wygląd

[Indeks materiału](material-index.json) zawiera podłogi, osłony, przód, mechanizmy i 20 elementów czterech nóg. W kolumnie gabarytowej doliczono po 8 mm z boków i 4 mm w Z. Największy wymiar w tym zestawieniu wynosi 224 mm. Podparcie rzeczywistego wydruku i orientacja osłon wymagają potwierdzenia. Cztery pliki STL w katalogu `retained-legs` są zapasowymi geometriami posiadanych nóg, zorientowanymi płaską powierzchnią do stołu. Zapisano ilości, sprawdzono zamknięcie siatek i zgodność objętości. Pliki STEP podłóg służą sprawdzeniu interfejsu. Dla osłon pozostają mocowania, przejście ruchowe i ostateczna orientacja z podporami.

Masa pełnego materiału pozycji z indeksu wynosi 863,69 g PETG przy 1,27 g/cm³. Około 118 g z tej wartości przypada na zachowane części nóg. Obecny zakres całego robota z tym materiałem wynosi około 2,72–3,46 kg przed dodaniem brakujących mocowań. WAGO i metal bazy są już uwzględnione w dodatkach. Rzeczywista masa wydruków i nośność pozostają niezmierzone.

Widać krótszy kołnierz szyi i otwory głośnika oraz chłodzenia. Spod policzka nadal widać elementy wewnętrzne, a tułów jest wyższy i bardziej pudełkowaty niż w robocie Oli. Tęczówki w tym zapisie mają kolor nadany powierzchniom. Fizyczne detale oczu, retencje zdejmowanych osłon, pewne dojście do baterii oraz część mocowań modułów pozostają do wykonania. [Wzór Oli](../../../../../../../reference/appearance/ola-cat-reference.jpg)

Cały pakiet do druku i montażu pozostaje niekompletny. Fizyczny fit, cięcia i końcowy luz są niezmierzone. Mapa komór baterii GTech do alarmu MOD05015 wymaga potwierdzenia przed zasilaniem.

