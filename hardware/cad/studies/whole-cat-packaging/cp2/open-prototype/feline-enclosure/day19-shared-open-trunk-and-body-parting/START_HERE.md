# WAVEGO 19H — przednia rama i wspólny kanał przewodów

**HOLD dla całego montażu.** ZIP zawiera 49 modeli STL na 65 sztuk, 5 plików STEP i osobny kupon MTA. Cztery zmienione części wyeksportowano i ponownie otwarto. Największy wymiar z rezerwą na brim i podpory wynosi 234.00 mm. Model pełnego materiału daje 1351.86 g PETG oraz 3.205–3.945 kg dla całego robota.

[Model FreeCAD](whole-cat19H.FCStd) · [widok robota](three-quarter.png) · [wnętrze](interior.png) · [przekroje](critical-sections.png) · [montaż dla dwóch osób](MONTAZ.md) · [indeks wydruków](material-index.json)

Zintegrowana rama zastępuje osobną przednią podłogę i nieruchomą osłonę. Obie pokrywy wewnętrzne są zdejmowane. Wstępne długie rozcięcie odłączyło kilka podpór; ostateczny wspólny otwór przy podziale zachowuje mocowania i dojście do końcówek. Prześwit przy żuchwie pozostaje widoczny na widoku ¾. W odniesieniu do usuniętych trzech dolnych ścian sprawdzono 32 lokalne przypadki z 49 zachowanych póz nóg. Liczba przecięć z nowym materiałem wyniosła 0. Podparcie pełnego modułu mikrofonu i obu kompletów stalowych zmieniono w obrębie wieka.

| Zakończenia | Wynik modelu |
|---|---|
| Dziewięć odgałęzień JR | Wspólne przejście 3 × 3 między pokładami. Osobne grupy do FHAC, G i lutowanej E1. Powrót PWM omija podporę ogona. |
| BUS | D_FL obrócony jako całe pięć torów. Dłuższa z dwóch żył pojedynczego kabla 900 mm potrzebuje 472 mm z końcami i rezerwą. |
| MAIN i K1474 | Obie żyły wyjściowe [250, 258] mm. Wejście W078 potrzebuje 105 z osobnych 210 mm tej samej jednostki. |
| Pi i audio | Właściwe projektowe nadlewy DATA i AUDIO mają 4,23 mm odstępu poprzecznego w dwóch stosach. Wcześniejszy obszar 26 × 26 × 24 mm obejmował obsługę. Na wzmacniaczu X1.1 to VO−, X1.2 to VO+. Podstawą są dwa otwory źródła 3006 zgodne z rozstawem 12,7 mm; poziom wejścia przewodu i końcówki głośnika wymagają sprawdzenia. |
| Bateria | Pakiet wysuwa się po rozłączeniu. Połówka przy pakiecie może przemieścić się w polu modelu o 14 mm. Odcinek W075 z końcem zajmuje 45.90 z 50 mm. Swobodny górny odcinek zachowuje 82.41 mm w obu położeniach. |
| Nogi | Cztery zaokrąglone przejścia 23,5 × 10,5 mm; pełne wtyczki przeprowadzać kolejno. Sprawdzić rzeczywiste końce i zapasy od wyjść do poruszających się napędów. |

**Odbiór.** Spośród 16 wybranych nowych profili wiązek wskazania materiału wystąpiły w 0 przypadkach. Oddzielnie sprawdzono 74 położeń i profili źródłowych oraz 30 par ruchomych sztywnych. Łączna liczba wskazań w tych dwóch testach wyniosła 0. Źródłowa mapa zachowuje 134 + 26 połączeń. Rzeczywiste cięcia, masę i luz ustala się podczas przymiarki.

**Pozostałe blokady.** Łuk serwisowy baterii i dziewięć odgałęzień JR współdzielą okno. Najbliższe osie izolowanych przewodów w przyjętym ułożeniu dzieli 0,09 mm przy sumie promieni 3,45 mm. Wymaga to rozdzielenia dwóch warstw i zachowania 14 mm ruchu przy rozpinaniu. Fizyczna swoboda w tym oknie pozostaje otwarta. Wyjście W001 przy G1.2 trafia w przednią ramę. Dwie próby odrzuciły dojście do tej samej strony złączki. Kolejna korekta wymaga wspólnego ustawienia całego banku G1 i jego dojść. W przyjętych polach montażowych 51 × 22 × 20,25 mm cztery stanowiska FHAC mają dodatnią wspólną objętość z drukami: {'F_HY': [('H19_FrontFrame', 49.5)], 'F_HP': [], 'F_TY': [('H19_FrontFrame', 158.76)], 'F_PI': [('E19_RearBase', 67.888)], 'F_AUX': [('H19_FrontFrame', 438.747)]}. Są to pola źródłowe; fizyczny profil uchwytu i klapki pozostaje do ustalenia. Zdjęcie Pi i banku daje dostęp, lecz samo nie potwierdza osadzenia tych czterech jednostek. F_HP wymaga odsunięcia F0 przed otwarciem w rozpatrywanym kierunku. Oddzielnie pozostają rzeczywiste kontakty R7–R9, dojście do terminali głośnika i części gniazd na modułach, skok rozłączenia i długość przewodu dostarczonej baterii, nadlewy obu USB i długość USB_AUDIO, cztery pełne MTA0100335, chłodzenie i mapa wnęk G-Tech. Wartości złożenia fizycznego pozostają niezmierzone.

Źródłem położenia i biegunowości X1 jest projekt płytki mono dla wybranego modułu 3006. [Pliki producenta](https://github.com/adafruit/Adafruit-MAX98357-I2S-Amp-Breakout)

[Wskazania i zakres](effectivity.json) · [połączenia i jednostki](whole-termination-plan.json) · [przestrzeń rozłączenia baterii](service-final.json) · [obudowy FHAC](five-fuse-service.json) · [parametry siatki ramy](frame-mesh-proof.json)
