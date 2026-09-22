# v32 — czujnik odległości w nosie, z otwartym torem optycznym

**Prototyp rozwojowy, nie wydanie do druku.** Ten etap dotyczy lokalnego
mocowania ToF/nosa do pyszczka. Nie zatwierdza całej głowy: jej napęd,
połączenie pyszczka ze skorupą i odziedziczone przecięcia nadal są otwarte.
Poprzedni [v31](../v31/README.md) jest zachowany bez zmian.

- [Pełne złożenie](Kot_v32_NOS_TOF.FCStd), [master PartDesign](OpticsDesign32.FCStd).
- [Plan połączeń](assembly-plan.json), [test natywny](assembly-validation.json),
  [audyt geometrii i optyki](fit-audit.json), [dziedziczenie](inheritance-check.json).
- [Stary pełny nos](before-nose.png), [stara wnęka](before-cavity.png).
- [Nowy moduł](tof-mount.png), [cały kot](whole-cat.png).
- [Mocowanie od tyłu — pyszczek półprzezroczysty](tof-rear-mount.png).

Złożenie przechowuje kopie brył, nie automatyczne live-linki do mastera.
Zmiana mastera wymaga odświeżenia kopii, audytów oraz eksportu fizyki.

## Rzeczywista płytka i droga mechaniczna

Zamiast pudełka `ToF` zastosowano zachowany STEP **Pololu 3417 / VL53L5CX**
z [pakietu referencyjnego](../../reference/component-selection-2026-09-22/README.md).
W modelu PCB ma 12,7×17,78 mm, laminat 1,016 mm, całkowitą wysokość 2,566 mm.
Dwa otwory Ø2,1844 są w lokalnych [10,16; 2,54] i [10,16; 15,24] mm.
Nie pomylono ich z małymi otworami do lutowania przewodów.

Baza CAD płytki: **[−200,2; −8,789181; 106,932374] mm**, obrót **Ry(−90°)**.
Normalna optyczna +Z płytki jest skierowana dokładnie w −X robota, do przodu.
Rozmieszczenie to nie jest jeszcze transformacją skonfigurowaną w ROS.

Pyszczek ma dwa integralne mostki PETG pod płytkę, z kieszeniami
odsuniętymi nominalnie o 0,3 mm od trzech pobliskich elementów SMD.
Nos jest osobną zaokrągloną osłoną PETG: 26×17 mm, grubość 2,5 mm,
promień narożników 4 mm. To funkcjonalna ramka otwartego czujnika,
nie przezroczyste okienko ani ostateczna stylizacja całej głowy.

Każda z dwóch osi mocujących ma ciągły stos:

**łeb M2×12 → nos → integralny mostek pyszczka → PCB → dystans PETG
Ø5×4 → metalowa nakrętka M2**.

Stos pod łbem 9,5 mm + nakrętka 1,6 mm; nominalnie zostaje 0,9 mm gwintu.
Otwory drukowane Ø2,4, wykonane według skillu `fastener-hole`; brak
drukowanych gwintów, podkładek i wkładek termicznych. Śruby M2×12 są
tym samym rozmiarem z wcześniej wskazanego zestawu Botland NSZ-00637.
Nie składano zamówienia ani nie zatwierdzano nowego dostawcy.
Modele łbów i nakrętek są nominalnymi obwiedniami, nakrętki uproszczono
do walca opisanego na sześciokącie. Sprawdzić faktyczne wymiary zestawu.

Łby są dostępne od przodu; nakrętki zakładać przy zdjętym pyszczku.
Nie ustalono momentu dokręcania: trzeba uniknąć zginania PCB i pełzania PETG.
Kieszenie pod SMD, luzy wydruku, orientacja warstw i podpory wymagają próbki.

`Fix_ToF` i `Fix_Nose` mają już fizyczną drogę mocowania do `Muzzle`,
zamiast samej blokady do ramy. **`Fix_Muzzle` pozostaje tymczasowy**.
Dodano sześć części: dwa dystanse, dwie śruby, dwie nakrętki.
Razem 286 części / 272 Fixed / 13 Revolute / **32 TEMP**.

## Tor optyczny i przewody

Poprzedni nos był pełną bryłą PETG przed czujnikiem. Teraz jest otwór
**6,5 mm szerokości × 10 mm wysokości**, bez szyby. Nie zakładamy, że
czarny PETG przepuszcza promieniowanie czujnika.

Według [Pololu](https://www.pololu.com/product/3417) typowe pole wynosi
45° w obu kierunkach głównych, a masa płytki bez pinów 0,5 g.
Producent dopuszcza bezpośrednie lutowanie przewodów i wymaga usunięcia
ewentualnej folii ochronnej układu przed pomiarem.

Ukryta bryła `OpticalReserve32` obejmuje **cały prostokąt górnej powierzchni
pakietu optycznego**, powiększony o około 0,3 mm na stronę, następnie
rozszerzony o półkąt 22,5° do lokalnego Z=60 mm. To konserwatywny test
przesłaniania przez obudowę i łby śrub, nie dokładny model dwóch apertur,
kalibracja wszystkich stref ani gwarancja zasięgu. Odbicia, przesłuch,
zabrudzenia, tolerancje i działanie przy podłodze trzeba sprawdzić na sprzęcie.
Nie modyfikowano optyki lasera. Brak szyby oznacza brak uszczelnienia.

`ToFWireReserve32` to lokalna rezerwa 5×18×11,9 mm za polami lutowniczymi.
W przedniej skorupie głowy wykonano rzeczywisty przepust **22×7 mm,
R3,5**, kieszenią o głębokości 14 mm od lokalnego Z=−0,1. Pierwsza
rezerwa przewodów przecinała tę skorupę; przepust usuwa tę przeszkodę.
Nie jest drukowana ani liczona do masy. Wybrano kompaktowe przewody
lutowane zamiast listwy goldpin; nie zamodelowano lutowia, odciążenia,
pełnej wiązki ani konfiguracji zasilania/I²C. Rezerwa nie dowodzi ich gotowości.

## Zakres kontroli

Master zawiera siedem w pełni związanych szkiców, natywne prymitywy,
zaokrąglenie, kieszenie oraz loft rezerwy optycznej. Fizyczne elementy PETG
są poprawnymi pojedynczymi bryłami i mieszczą się w 256×256×256 mm.
To sprawdzenie obwiedni, nie zatwierdzenie parametrów druku.

`RobotConnectionTest32` przelicza 22 klatki: nogi ±3°, ogon ±30°,
kontrola luk/osi oraz powrót do spoczynku. Sprawdzany jest też związek
ToF/nosa z pyszczkiem. Głowa jest nadal zablokowana: **to nie test ruchu
przegubów głowy**. W FreeCAD: złożenie → Simulations → ten test.

276 pozostałych części jest porównywanych z v31 przez tokeny BRep
i ścisłą tolerancję numeryczną. Audyt lokalny mierzy kontakty stosu,
drożność osi M2, rezerwę przewodów, tor optyczny oraz przednie dojście
śrubokręta Ø4×30 mm. Przecięcia dawnych części głowy nie są ukrywane:
osobna lista `inherited_head_interferences` zachowuje je jako **OPEN**.
Nie deklarujemy braku wszystkich kolizji w robocie.

Różnica „nowa powłoka głowy minus stara” dawała w OCC niepoprawną bryłę,
więc jej objętości nie użyto jako dowodu dodania materiału. Audyt sprawdza
zamiast tego obustronną zgodność oryginału z bazą importu i mastera z kopią
w złożeniu (poprawne, puste różnice, tolerancja 0,00001 mm), a także to,
że jedyną zmianą powłoki jest natywna **subtraktywna** kieszeń 14 mm.
Pozwala to odróżnić stare przecięcia od nowych bez ukrywania problemu
jądra geometrycznego. Pozostałe przecięcia muszą być poprawnymi wynikami BRep.

Pierwszy [preflight](preflight.json) jest celowo zachowany jako diagnoza,
nie wynik końcowy: wykrył trzy kontakty SMD, później usunięte kieszeniami.
Przy przenoszeniu mastera audyt wykrył też błędną domyślną oś obrotu
narzędzia. Ustawiono jawnie wszystkie składowe osi (0,1,0), dodano asercje
i ponowiono raporty. Stary eksport z błędnym obrotem nie jest wynikiem fizyki.

[Gazebo v32](../../simulation/v32/README.md) uwzględnia wszystkie nowe masy
i siatki, nadal z zamrożonymi głową i ogonem. Geometria optyczna nie jest
symulowanym czujnikiem Gazebo; próby dotyczą napędów nóg.

## Odtwarzanie

W bieżącym FreeCAD pozostawiono cały kot. Zapisany checkpoint zachowuje
izolowany widok modułu nosa z chwili audytu. Aby po otwarciu pokazać całość,
uruchom makro [View32.FCMacro](../../../tools/freecad/skorupa/View32.FCMacro)
(Makro → Makra → wybierz plik → Uruchom). Zmienia wyłącznie widoczność
i kamerę, bez zapisu; podpisy raportów pozostają ważne. Nie zapisuj pliku
tylko po to, by odświeżyć widok. Przekrój można włączyć przez menu
Widok → Płaszczyzna przycinająca / Clipping plane i wyłączyć w tym samym
oknie; nie jest to operacja wycinania geometrii.

W Pythonie FreeCAD: `cache31.py`, `cache32.py`, `audit32.py` z
`tools/freecad/skorupa/`, potem `inheritance32.py` (także zwykły Python).
Cache oraz diagnostyczne BRep są ignorowane w Git.

`Integrate32.FCMacro` buduje nową kopię i odmawia nadpisania.
`Refresh32.FCMacro` odświeża rozwijany v32 z mastera po sprawdzeniu SHA
i osi; `Validate32.FCMacro` przelicza więzy, zapisuje spoczynek i cache.
Po takim zapisie wszystkie raporty oraz eksport/próby trzeba wykonać ponownie.
Nie uruchamiać zmian w historycznych v29–v31 tylko dla odświeżenia widoku.
