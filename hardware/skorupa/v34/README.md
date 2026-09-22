# v34 — podparcie ogona na dwóch łożyskach

**Prototyp rozwojowy, nie wydanie do druku ani zatwierdzenie napędu.**
Branch `codex/robot-cat-mechanical`, repo `syskaseb/robot-cat`. v33 zachowane.

- `Kot_v34_PODPARCIE_OGONA.FCStd`: całe złożenie, natywne Fixed/Revolute.
- `TailSupport34.FCStd`: edytowalna historia PartDesign, wykonana przez MCP.
- `assembly-validation.json`: rzeczywiście wykonany test natywny.
- `fit-audit.json`: kontrola nowych części, ruchu i wybranych dróg montażu.
- `inheritance-check.json`: porównanie z v33 i z edytowalnym masterem.
- [Cały kot](whole-cat.png), [podpora ogona](tail-support.png),
  [przezroczysta obudowa podpory](tail-inside.png).
- [Próbki PETG do wydruku](coupons/README.md): trzy gniazda i trzy czopy,
  łącznie około8,7 g; to nie komplet STL robota.

## Wykonane kontrole

306 komponentów,292 Fixed +13 Revolute; **30 połączeń nadal tymczasowych**.
Test natywny przeszedł22 klatki i przywrócił pozycję spoczynkową. Cztery
nowe części wirujące pozostają z ogonem, reszta podpory z korpusem. Głowa
jest zablokowana; jej napędów ten test nie zatwierdza.

Master ma25 faktycznie w pełni związanych szkiców. Wszystkie14 Bodies
przeszło kontrolę BOP, ma po jednej poprawnej bryle i mieści się w256³.
Liczba obejmuje również kupne obwiednie i ukryte wejścia historii, **nie
oznacza14 nowych wydruków**. W złożeniu jest7 końcowych części PETG tego
projektu, w tym zmieniony uchwyt serwa i korzeń ogona.

83 pary spoczynkowe nowych/zmienionych części bez przecięć >0,01 mm³.
13 ustawień ogona co5° od−30 do+30° bez przecięć względem nieruchomego
kota; nogi podczas tego audytu pozostają w pozycji spoczynkowej.
Kontakty nominalnych powierzchni podparcia mają niezerową powierzchnię,
ale obwiednie łożysk nie dowodzą oparcia na właściwych bieżniach.
Próbkowana droga górnej obudowy i89 pozycji wkładania serwa są wolne;
nie jest to ciągły test swept-volume ani walidacja wiązki.

279 części odziedziczonych z v33 zachowano;27 kopii nowych/zmienionych
porównano z masterem. Maksymalna różnica zapisu BRep1,07×10⁻¹³ przy
niezmienionych tolerancjach10⁻⁹/10⁻¹². Stare konflikty głowy pozostają OPEN.

632 testy ROS/CAD/narzędzi zaliczone w Dockerze; regresja v33:622.
Nowy bilans masy2,502 kg (+77,7 g). Osobne wyniki fizyki nóg i ograniczenia:
[Gazebo v34](../../simulation/v34/README.md). Głowa i ogon w tych próbach
są nieruchome, choć ich masa/bezwładność wchodzi do obciążeń nóg.

## Mechanika

Jeden MG92B i sześć wymiennych segmentów ogona pozostają. Segmenty po
skręceniu tworzą sztywny łuk, obracany w całości; nie są sześcioma napędami.
Oś yaw nadal przechodzi przez X171,Y−6; nowy punkt odniesienia Z113 leży
na tej samej prostej co dotychczasowe wyjście serwa Z91.

Uchwyt serwa i dolna podpora są **jednym wydrukiem PETG** (`ServoSupport34`,
w złożeniu zachowuje nazwę `MG92BMount29`). Dolna część nie jest nakładana
na stary uchwyt — taki jednoczęściowy nasuwany wspornik nie dał się złożyć.
Górny blok `UpperHousing34` odkręca się na dwóch M3×12 z nakrętkami w
bocznych gniazdach. Otwory M3 mają Ø3,4, M2 Ø2,4, zgodnie ze skillem
FreeCAD `fastener-hole`; kieszenie dostosowano do nominalnych obwiedni śrub.

Dwa 608ZZ, nominalnie 8×22×7 mm, stoją na Z103–110 i116–123. Rozstaw
środków 13 mm. Gniazdo ma Ø22,2, czop PETG Ø7,9. To **założenia do próbki
tolerancji**, nie zatwierdzone pasowania łożysk. Dystans zewnętrzny ma
Ø21,8/18, wewnętrzny Ø11/8,1; oba mają 6 mm wysokości. Pokrywa pozostawia
nominalnie 0,2 mm luzu osiowego zewnętrznego stosu. Czop z kołnierzem i
pierścieniem dociskowym Ø11 jest spięty M3×30 z nakrętką we wnętrzu korzenia.

Łożyska w CAD są **nominalnymi obwiedniami**, nie modelem kulek i bieżni.
Szerokości powierzchni oparcia trzeba skonfrontować z rzeczywistymi
pierścieniami, aby dystans nie tarł o osłonę łożyska. Nie zatwierdzono
docisku, luzu, wstępnego napięcia, trwałości czopa, pełzania ani orientacji
warstw PETG. Nie modelowano gwintów ani gniazd w łbach kupnych śrub.

**Sprzęgnięcie z dostarczonym orczykiem MG92B pozostaje TEMP.** Nie znamy
jego fizycznych wymiarów/rozstawu śrub i nie zgadujemy wieloklinu. W CAD
Revolute łączy korzeń ogona z górną obudową łożysk, a tymczasowy Fixed
wiąże wyjście serwa z korzeniem. Poprawna animacja nie dowodzi, że taki
orczyk da się już przykręcić. Nie uruchamiać fizycznego napędu według animacji.

## Kolejność i ograniczenia montażu

Podzespół składać na **zdjętym mostku `TailBridge29`**, przed przykręceniem
do kota. Dwa przednie dojścia do śrub podstawy są zasłonięte przez nogi
złożonego robota; raport zachowuje te kolizje. Nie oznaczamy go jako
w pełni obsługiwalnego od spodu gotowego kota.

1. Nakrętki M3 w gniazdach podstawy; cztery M3×16 od spodu mostka.
   Łby pod Z41, nakrętki Z50,6–53, wystający gwint 4 mm. Dno kieszeni
   0,6 mm jest podparte ciągłym materiałem dawnej stopy serwa poniżej Z50.
2. Serwo i jego istniejące M2 na uszach. Sprawdzenie konkretnej drogi
   wkładania opisuje raport: najpierw pochylenie do12° wokół X i przesunięcie
   w Y, następnie wyprostowanie po przejściu występu kablowego przez pokład.
   89 nominalnych pozycji przeszło bez przecięć. Proste wsuwanie pionowe
   koliduje i jest zachowane jako odrzucona próba. To nie dowód ciągłego
   przejścia ani fizycznego luzu montażowego; przewodu/wtyku nie obejmuje STEP.
3. Nakrętka osi M3 w korzeniu przed połączeniem z serwem. Samo połączenie
   z orczykiem nadal wymaga projektu — kolejność w tym miejscu niezamknięta.
4. Górna obudowa od góry nad czopem; boczne nakrętki M3 i dwa M3×12.
   Gniazda pod łby są Ø6,8; dokręcanie przed założeniem pokrywy.
5. Dolne łożysko, dystanse 6 mm, górne łożysko, pierścień Ø11 i M3×30.
   Nakrętka osi Z96–98,4, łeb nad Z125, wystawanie 1 mm.
6. Pokrywa: dwa M2×12, łby nad Z128,2. Nakrętki Z117,6–119,2,
   wystawanie 1,4 mm; dojścia od dołu dla nasadki o obwiedni ≤Ø6.
   Nakrętki trzeba przytrzymać — gniazda nie blokują ich obrotu.

Stos śrub górnego bloku: łeb nad Z105, nakrętka Z94,6–97, koniec Z93,
czyli wystawanie 1,6 mm. Nominalny sześciokąt M3 ma AF5,5, gniazda AF5,7
lub szczelinę 5,7. Fizyczne nakrętki i narzędzia trzeba przymierzyć.

## Zakupy — dodatkowe względem v33

Odczyty 22.09.2026; niczego nie zamówiono. „24 h” to deklaracja wysyłki,
nie gwarancja doręczenia. Ceny/stany należy sprawdzić ponownie przy zakupie.

| Element | Potrzeba | Źródło i odczyt |
|---|---:|---|
| 608ZZ 8×22×7 | 2 | [Kamami 1184707](https://kamami.pl/czesci-mechaniczne-do-drukarek-3d/1184707-608zz-lozysko-kulkowe-8x22x7mm-5902186304048.html), 13 szt.,3,39 zł/szt.,wysyłka24 h |
| M3×16 | 4, zamiast dawnych4×M3×12 | [Kamami 557376](https://kamami.pl/sruby/557376-sruba-m3-philips-dlugosc-16mm-100-sztuk.html),9 opakowań100 szt.,10,01 zł,24 h |
| M3×30 | 1 | [Botland 8087](https://botland.com.pl/srubki-i-nakretki/8087-srubki-m3-dlugosc-30mm-naciecie-krzyzakowe-10szt-5904422307400.html),25 opakowań10 szt.,24 h |
| M3×12 / M2×12 | 2 /2 | [Dotychczasowy zestaw NSZ00637](https://botland.com.pl/srubki-i-nakretki/637-zestaw-srubek-podkladek-i-nakretek-330szt-5410329304478.html); można użyć2 uwolnionych M3×12 |
| Nakrętki M3 / M2 | dodatkowo3 /2 | ten sam zestaw;4 stare nakrętki M3 podstawy wykorzystane ponownie |

Niedostępne M2×10 odrzucono, a pokrywę dostosowano do M2×12. Zakupowe
wymiary łbów nie są potwierdzone przez sprzedawcę; Ø6,2×3 dla M3 i
Ø4,2×2 dla M2 są obwiedniami projektowymi, nie pomiarem partii towaru.

## Widok i odtwarzanie

`tools/freecad/skorupa/View34.FCMacro` pokazuje całego kota bez zapisu.
W masterze pokazane są końcowe cechy (`Tip`) części. Plik złożenia to podpisane kopie geometrii,
nie live-link. Zmiana mastera wymaga ponownej integracji i kontroli.

`RobotCatAssembly24 → Simulations → RobotConnectionTest34` to natywny
test połączeń. Nogi ±3°, ogon ±30°, głowa pozostaje zablokowana. Do podglądu
wnętrza użyj `Std_ToggleClipPlane` (Widok / płaszczyzny przycinania) albo
ukryj `UpperHousing34` i `BearingCap34`. Przycinanie widoku nie usuwa części.

W Pythonie dostarczonym z FreeCAD: `cache34.py`, `audit34.py`,
`inheritance34.py`. W GUI: `Integrate34.FCMacro` odmawia nadpisania;
`Validate34.FCMacro` zapisuje złożenie w spoczynku i odświeża podpis/cache.
Po takim zapisie trzeba odtworzyć także dane symulacji. `support34.py`
przechowuje mapę wystąpień, a nie program generujący wydruki.

## Nadal otwarte

Fizyczny orczyk, próby łożysk/PETG i osłona mechanizmu; dwa napędy głowy,
odziedziczona topologia/przenikania głowy, pozostałe mocowania elektroniki,
wiązka, serwis akumulatora, termika. Zmiana ogona nie zamyka tych punktów.
