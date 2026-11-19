# 19A — niski układ całego kota, próba wspólnej obsady

**Całość HOLD. Pakiet 19A służy decyzji konstrukcyjnej.** Baza części to d5baf5e6 z zachowanym źródłem. Obecne złożenie ma niski układ opraw, przeniesiony cały lutowany PCA–E1, tylną strefę operatora, szerszy tył głowy i obrys obejmujący podstawę. Końcowa próba wspólnego nośnika wykazała przerwę w drodze mocowania szyi oraz trzy bryły części tylnej. Pozostała w wynikach jako odrzucona próba. Bieżący native zachowuje poprzednią geometrię podpór.

[Złożenie FreeCAD](whole-cat19.FCStd) · [Przód](front.png) · [Bok](side.png) · [Widok ¾](three-quarter.png) · [Wnętrze](interior.png) · [Dwa krytyczne przekroje](critical-sections.png)

## Decyzja po pierwszym teście

Pierwsze sześć trafień układu dotyczyło stref Pi–S1, E1–S0, MAIN–F0, BNO–F0 oraz BUS–monitor/oprawa. Jedna korekta wydzieliła operatora na tył, przeniosła PCA–E1 na tylną krawędź dodatnią, skierowała pełne pole USB BUS wzdłuż korpusu i rozdzieliła sterowanie od pionowego miejsca zapasu DATA. Po korekcie obwiednie tych sześciu par są rozdzielone. S1 i BUS zachowują klasyfikację konserwatywnych pól źródłowych. Cztery dawne punkty trafienia powrotu ToF leżą poza materiałem nowego tyłu głowy. Pełny nowy ruch i wszystkie przebiegi przewodów pozostają do sprawdzenia. [Pierwsze świadki](first-occupied-gate.json) · [Bieżący test](current-whole-gate.json)

**Pierwsza konstrukcyjna blokada** to podparcie wspólnego zamknięcia. Pierwsze stopy miały 500,1 mm³ styku z portalem i 0 z szyją. Druga próba uzyskała 262,70 mm³ styku z szyją i 0 z portalem. Proponowane połączenie zachowało zerowe przenikanie stóp z pełnym serwem yaw, lecz część tylna rozpadła się na trzy bryły. Wynik nie został zastosowany. Kolejne zadanie musi zmienić organizację nośnika i drogę obciążenia. Projektować jedną podłogę z korzeniami przy rzeczywistych ośmiu źródłowych osiach i otwartym mostem wokół pasma wyjścia serwa, razem z osłoną szyi i pełną obsadą przewodów. Zastąpić warstwowe zestawienie starego portalu, szyn i nowego rusztu. Najpierw przekrój z pełną obudową MG, końcami, sworzniem, zajętymi polami i dostępem do śrub. [Próba mocowania](whole-root-assembly.json) · [Poprzedni pomiar stóp](whole-unit-space-plan.json)

## Obsada i całe jednostki

Dwanaście pełnych MTA0300330 z końcami leży płasko. Zachowano 15 bankowych WAGO415 i czynny PBAY_P_AUX, cztery WAGO615, osiem inline oraz pięć FHAC. P_REAR–F_AUX zachowuje wzajemną pozę. P_SYS–F_PI przesunięto razem o 78 mm w X i 65 mm w Y. Pełne osprzęty S0 i S1 przeniesiono jako grupy. Kupna baza z 126 źródłowych brył, obecne nogi i serwa pozostają w złożeniu. Mapa 57 pozycji i ADD7 pochodzi z odebranego zestawienia źródłowego. [Wybór aktorów](actor-effectivity.json) · [Zestawienie źródłowe](../day19-source-bom-budgets/README.md)

| Jednostka | Plan i stan |
|---|---|
| DATA 500 | 26 + 76 dojścia Pi + 216 otwartego zapasu + 156 dojścia BUS + 26. Model zapasu ma środkowy R33,4 dla Ø6,8, co daje wewnętrzny R30. Oba dojścia mają przydzielone długości i wymagają kwalifikacji wspólnej przestrzeni. |
| Trzy JR 300 | Każda osobno ma 12 wtyku + 246 transportu i zapasu + 25 rozprowadzenia + 9 odcinka izolowanego + 8 zakładki. Plany transport/zapas to yaw 120/126, pitch 180/66, tail 145/101. Regiony pozostają warunkowe, w tym strefa tail przy pełnym MG i AMP. |
| Trzy fabryczne MG 250 | Zachowane pełne przewody i klucze. Głowa ma źródłowe pola yaw/pitch. Po zmianie podpór i stacji trzeba odebrać rzeczywiste dojścia i rezerwę ruchu. Wyjście MG i stub11,45 są projektowe. |
| FFC 200 | 10 łącznie na oba końce, 190 wolnego odcinka. Pi i kamera zachowują pozę, zmienione osłony wymagają sprawdzeń sąsiadów. |
| Cztery ToF | Ø2,1 na żyłę, ruchomy R31,5, te same sieci JP3. Tył głowy ma szerokość180 i ścianę1,4. Stałe dojścia i długości trzeba przeliczyć do przesuniętego całego PCA–E1. |
| Cztery E2 | Cztery odrębne jednostki po220 dostępnego z zachowaniem obu końców. Dalszy plan zmienionych stacji jest otwarty. |
| USB_AUDIO i POWER | USB_AUDIO ma nieznaną długość dostarczoną. Osobne pola POWER/K1474/Delock zachowane. DATA nie otrzymuje ich funkcji ani długości. |

W tabeli są plany przydziału i warunki. Odbiór pełnej wspólnej przestrzeni jest otwarty. Cztery kompletne MTA0100335, zewnętrzna średnica ich przewodów i rzeczywista długość końców pozostają zależnością od jednej dostarczonej próbki. Zachowano znaczniki czterech sztuk. Obwiednia Pi85×56×26 oznacza komponenty/chłodzenie/powietrze. ReSpeaker otrzymał osobną pełną obwiednię wysokości10,93, a AUX rezerwę9,5. [Jednostki i regiony](whole-unit-space-plan.json)

Pole rezerwy JR300 ogona ma 4991,82 mm³ części wspólnej z pełnym MG i 720 mm³ z polem AMP. Obecny przydział magazynowania wymaga nowego wspólnego miejsca przy nośniku i sprawdzenia właściwych dojść oraz R22. To wynik obsady regionu. Kształt swobodnego przewodu pozostaje zmienny. [Bieżący test wspólnej przestrzeni](current-whole-gate.json)

## Masa i montaż

Nowe wybrane podpory i osłony mają **780,99 g pełnego materiału PETG przy1,27 g/cm³** w bieżącym surowym sumowaniu części. Przydział części do wydruków i objętości wspólnych jest otwarty. Do P dochodzą zachowane drukowane nogi, przód optyczny, pozostały mechanizm głowy i ogona oraz konieczne mocowania. Budżet całego robota wynosi 1853,4–2593,4 g + P. WAGO111,6 g mieści się już w źródłowym dodatku ochrony i wiązek. Masa wykonania i nośność pozostają niezmierzone. [Budżet masy](mass-budget.json)

Docelowa kolejność dla dwóch osób zaczyna się od źródłowej bazy i wspólnego nośnika. Pierwsza osoba podtrzymuje pełny mechanizm głowy podczas zakładania śruby poprzecznej, podkładek i nakrętki. Druga osadza elektronikę, całe pary krótkich FHAC i złącza JR przy otwartym nośniku. Następnie układa oddzielne jednostki DATA, USB_AUDIO, FFC i ToF, izolowane połączenia i rezerwy. Tył głowy i lekkie pokrywy zamykają po tej pracy. Wykonalność tej kolejności zatrzymują wskazana droga mocowania i nieodebrane wspólne przestrzenie przewodów.

Na widokach wciąż widać wyposażenie pod głową, osprzęt operatora i niedokończone połączenie osłon. Sylwetka pozostaje do oceny. Podział na wydruki, ich retencje, pełny ruch głowy ±20/±10 i ogonaY ±15 oraz montaż wymagają dalszej pracy. physical_PASS=false, rzeczywiste fit/cut/slack=NULL. Źródła, pierwsza próba i surowe negatywy są zachowane. [Manifest](verified-whole19.json)
