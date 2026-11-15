# Tylny obrys carriera — jeden wynik i jeden kupon

**Do pomiaru na stole wydano tylko `MEASURE_ONLY_rear_floor_endstop_coupon.stl` (1szt). Cały carrier pozostaje HOLD. Nie montować kuponu jako części zabezpieczającej baterię.**

Aktualny cały model: `carrier-contour.FCStd`. Najważniejsze źródłowe dane i porównanie obu stron: `actual-rear-two-sided-section.png`. `whole-contour-context.png` jest rzeczywistym widokiem wnętrza. Nowy pionowy węzeł P12/carriera, wszystkie kupne części/pozy i cztery stopy są zachowane. Nie zmieniano głowy/wyglądu ani nie prowadzono nowej rundy recenzji.

## Co zamknięto

Z rzeczywistego walca S0 R28,5/środek(135,5;-29,328917) oraz zapasu1,25 wynika R naroża≥3,739. Nominalne ogniwo, luz przymiarki0,5 i przyjęta do próby użyteczna ścianka2mm dają R≤5,414. Wybrano R5, bez siatki prób. To jeden ciągły obrys tylnej podłogi i roboczego stopera; skrajne X108 pozostawiono, wewnętrzny tył maX105. Naroże ma2,172mm materiału, a rzeczywisty odstęp od pełnego S0 wynosi **1,627055mm/common0/valid**. Jawnie zastąpiono130,572mm³ roboczego starego prostokątnego obrysu; nie ukryto straty materiału.

Dziewięć chronionych rzeczywistych grup (4stopy, tylne ramię, wspólna MTAfloor i3człony nowego korzenia) ma0missing. Nowy pionowy root/pełna stal/parting i Pi4/guide/audio odziedziczone tylko w niezmienionym odebranym zakresie; bez powtórki1815/6 lub dawnych macierzy. Obie całe200opaski pozostają dla baterii, bez udawania kotwy ramy.

## Dlaczego nie ma dużych STL

Pierwszy dotąd nieodebrany sąsiad po tej poprawce: **P19–H03 gap0,5<1,25/common0**. ID `H03_panel_M3x55_1` oznacza obecny **pełny M3x50**, oś(110,15), wałekZ42,52..92,52 — nie wolno go skasować jako starej rezerwy. Zapisany świadek P19 `(108,15,Z60,8/65/68)`.

Ten sam aktualny węzeł ma rzeczywistą podporę `P05_spacer_instance2`: lewa pełna powierzchnia X107, Y12..18/Z48,52..88,52. **Aktualny P19 przecina ją na41,231061mm³**; to nominalny kontakt dwóch obecnych wydruków, nie dopuszczony interfejs ani fizyczny pomiar. Dla pozostawienia1,25 wolnego miejsca zewnętrzna ściana może kończyć się najwyżejX105,75. Przy ogniwie doX104,5 i luzie0,5 zostaje **0,75mm** na ciągłą pełną tylną ściankę w tym pasie; to mniej niż wybrana próbna2mm. To granica tej pełnoszerokiej ścianki, nie dowód niemożliwości innego funkcjonalnego rozłożenia stopów.

Nie ruszono podpory/śruby/S0/ogniwa ani nowego korzenia, nie obniżono marginesu i nie zbudowano drugiego konturu. Następna decyzja: rzeczywiste funkcjonalne zatrzymanie końca baterii **wokół zachowanego P05**, z zachowaniem podparcia, izolacji i całych pasków. Nie kolejny łeb/oś/root ani przypadkowy mikroradius.

## Kupon i konkretny pomiar — dwie osoby

A trzyma rzeczywiste niepodłączone ogniwo lub jego wzornik, B sprawdza kupon na stole: długość i tylny narożnik, luz0,5 i brak nacisku na ogniwo. Kupon jest przycięciem obecnej geometrii,8×42×7,2mm, jedna zamknięta dodatnia siatka, PETG płaskim spodemZ0; lokalna podłoga4,2/stop3mm. Profil drukarki i rzeczywiste tolerancje nieprzypięte. To nie polecenie druku ani odbiór wytrzymałości.

Zmierz rzeczywisty tył ogniwa względem przedniego stopuX−2 oraz pozycję lewego boku P05 w aktualnej rewizji. Ta sama pełnoszeroka ścianka2mm/luz0,5 wymagałaby długości ogniwa≤105,25mm zamiast nominalnych106,5; nie zaliczono takiej różnicy ani nowej wersji baterii na papierze. Nie dociskać znanego kolizyjnego obrysu kuponu do P05. Rzeczywista izolacja/padding/pasek/buckle/lap/masa i nośność pozostają do przymiarki, bez zabierania na nie dostępnego luzu.

## Rzeczywisty otwór wejścia i kolejność

Aktualny przekrój P12 przyX40 ma krawędzieY−14/+16: **otwór30mm, ogniwo nominalnie35mm**. Nie przyjęto pionowego dropin przez zamkniętą ramę. Jedna proponowana kolejność po rozwiązaniu obrysu: dummy/ogniwo i całe paski na otwartym P19 przed rzeczywistym zamknięciem P12, pełne4MTA220/oba końce układane otwarcie przed keeperami, driver/nut przed MAIN/bankami. Pełny feed/tool i cała instalacja pozostają UNRECEIVED poHOLD.

Sporadyczna wymiana może wymagać P15mic -> P13BUS -> rzeczywiste XT60/balance, zwolnienia rzeczywistego roguPi naP10 i mocowań P12, a potem podniesienia całego podpartego zestawu. Nie udawać odpięcia lutowanego E1; realny luz/zasięg końców przy takim podparciu toFIT2 i nadal brak dowodu pełnego wyjmowania. Nie obiecano szybkiego serwisu.

`current-print-index.json` wskazuje WYŁĄCZNIE kupon jako nowy STL. P10 z wewnętrznym Pi-capture/P12/P19 są bieżącymi zależnościami native, nie starymi STL o tych samych nazwach. P11/P13/P14/P15/jaws wskazane przez niezmienione SHA bez kopiowania dziewięciu siatek; nie jest to wholekitGO. Wszystkie57+extras/ochrona/4DATA5plus7G/4niezależne220 i fabryczne końce zachowane. Actualfit/cut/slack=NULL, physicalPASSfalse/wholekitfalse; pozostałe mocowania PCB/bank/audio i korzeń głowy nadal odrębnieOPEN.
