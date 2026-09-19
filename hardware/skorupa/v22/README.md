# v22 — przykręcana osłona brzucha PETG

**Prototyp montażowy, nie wydanie całego robota do druku.**

Złożenie: [Kot_v22_BRZUCH_PETG.FCStd](Kot_v22_BRZUCH_PETG.FCStd).
Wersja v21 i wszystkie wcześniejsze pliki zostały zachowane.
Nie przesunięto serw, osi łap, głowy, ogona ani elektroniki.

## Co zmieniono

Stara owiewka `BellyPod`, przecinająca ramę i panele, została zastąpiona
osobną dolną osłoną `Belly22`. Podłoga i boczne ścianki mają **3 mm**.
Osłona ma zaokrąglenia naroży w rzucie R8/R5 i dolną krawędź zewnętrzną R3.
Otwarte przejścia na końcach pozostawiają miejsce na podwozie i jego dolną
płytę. To osłona mechaniczna z wybraniami serwisowymi, **nie szczelna obudowa**.

Do `SideLeft22` i `SideRight22` dodano po dwa zintegrowane gniazda PETG
na nakrętki M3. Boki zastępują v21 — nie są dodatkowymi nakładkami.
Zachowano pogrubiony środek v21, końce z dotychczasowymi otworami oraz
górną część paneli. Nowe otwory dotyczą tylko dolnych mocowań osłony.

Każde z czterech połączeń ma:

- śrubę **M3×16** od spodu, łeb walcowy Ø6 × 3 mm;
- metalową nakrętkę M3, nominalnie AF5,5 × 2,4 mm;
- otwór przelotowy Ø3,4 mm i kieszeń nakrętki AF5,8;
- pełne podparcie łba, nakrętki i obu stykających się podkładek PETG;
- nominalnie 0,8 mm końca śruby za nakrętką.

Osie mocowań: global X = **−35 i 80 mm**, Y = **±40 mm**, kierunek Z.
Płaszczyzna styku osłona–bok: Z = −2 mm. Podparcie łba: Z = −6,5 mm;
dno kieszeni nakrętki: Z = 6,3 mm. Łby wystają 3 mm pod podłogę.
Kanał wkładania nakrętki przechodzi również przez skośną ściankę boku,
aby nie pozostawał nad gniazdem blokujący ją nawis.

Wymiary otworów i wykonanie szkic/Pocket oparto na skillu FreeCAD
**Fastener Hole Patterns**. Nakrętki wkłada się od wnętrza podwozia,
przed śrubami; nie gwintujemy bezpośrednio PETG. Sprawdź pasowanie
próbką PETG z v19 oraz próbnym wydrukiem rzeczywistego gniazda.

W złożeniu są cztery śruby i cztery nakrętki. To obwiednie bez gwintów
i gniazd narzędzia. Połączenie jest odwzorowane geometrycznie — nie dodano
więzów solvera Assembly ani symulacji naprężeń.

## Kontrole

- Trzy poprawne pojedyncze bryły drukowane i osiem brył metalowych;
  kontrola BOP oraz ponowne otwarcie zapisanego FCStd przeszły.
- Brak statycznych kolizji nowej osłony, dodatków do boków i łączników
  z zachowaną geometrią ani między nowymi elementami.
- Usunięto stwierdzone w v21 przecięcia brzucha z obiema ramami i bokami.
  To nie oznacza audytu wszystkich innych par części całego robota.
- Odstęp osłony od ram poprzecznych wynosi około 2,5 mm, od akumulatora
  9,7 mm, od jego tacki 4,5 mm. Minimalny wskazany odstęp od dolnej
  płyty WAVEGO to **0,5 mm** — wymaga sprawdzenia tolerancji na wydruku.
- 16 kontroli geometrycznego podparcia połączeń: co najmniej 99% zadanej
  powierzchni ma materiał. Nie jest to pomiar nośności.
- Obwiednie wkładania nakrętek od środka i opuszczania do kieszeni są wolne.
  Sprawdzono też dostęp wałka śrubokręta Ø5, długości 30 mm, poniżej łba;
  nie całej rękojeści ani dłoni.
- Zachowano geometrie i położenia 241 obiektów źródłowych. Zastępowane
  części ukryto, nie usunięto. Stara notatka o kolizjach v21 jest oznaczona
  jako archiwalna. Model nadal jest prototypem.

## Demontaż — nie ciągnij prosto w dół

Przy pozycji nóg zapisanej w modelu samo opuszczanie osłony dalej niż
20 mm prowadzi do kolizji z przednimi łapami. Odrzucone próby 40/60 mm
pozostawiono w raporcie, aby tego ograniczenia nie zgubić.

Sprawdzony w **19 pozycjach** wariant drogi serwisowej:

1. Wyłącz zasilanie i stabilnie podeprzyj podwozie; potrzebne jest miejsce
   pod robotem. Wykręć wszystkie cztery M3×16.
2. Opuść osłonę o 20 mm.
3. Przesuń ją o 20 mm ku ogonowi, czyli w kierunku +X.
4. Opuść o dalsze 20 mm — łącznie 40 mm.
5. Przesuń o kolejne 10 mm ku ogonowi — łącznie 30 mm.
6. Opuść o dalsze 20 mm — łącznie 60 mm; montaż w odwrotnej kolejności.

W testowanych pozycjach nie ma kolizji. **To próbkowanie, nie ciągły dowód
bezkolizyjności całej trajektorii ani fizyczny test montażu.** Wynik dotyczy
aktualnej pozycji łap, bez niezamodelowanych przewodów. Nie wymuszaj ruchu
osłony siłą i nie zakładaj takiego samego wyniku dla innego ustawienia nóg.

## Druk i pliki

Wszystkie trzy nowe części są przeznaczone na czarny PETG; łączniki są stalowe.
W `stl-prototype/` znajdują się tylko zamienniki zmienione w tym etapie:

| część | gabaryt STL, mm | orientacja eksportu |
|---|---|---|
| `Belly22` | 170 × 106 × 41 | podłogą na stół |
| `SideLeft22` | 212 × 40,52 × 22,34 | obrót X o 90° |
| `SideRight22` | 212 × 40,52 × 22,34 | obrót X o 90° |

Zamknięte siatki bez krawędzi niemanifoldowych mieszczą się w 256³ mm,
także z brimem 8 mm. Orientacja nie zastępuje sprawdzenia podpór, warstw
i adhezji w slicerze. Pozostałe części i śruby v20 pozostają oddzielnym zestawem.

Nie wykonano prób wydruku, obciążenia, pełzania PETG, FEA, prób cieplnych
ani symulacji ruchu nóg względem nowej osłony. Końcowe strefy ramy nadal
mają odziedziczone cienkie ścianki. Uchwyty reszty elektroniki, przewody
oraz mechanika głowy/ogona (w tym 3 mikroserwa w BOM wobec 4 w starym
modelu) nadal wymagają dokończenia. To nie komplet do finalnego druku.

## Podgląd

- [Cały kot](kot-v22-zlozony.png) — taki widok pozostawiono w FreeCADzie.
- [Osłona z miejscami mocowania](brzuch-v22-oslona.png).
- [Rzeczywisty przekrój mocowania](brzuch-v22-mocowanie-przekroj.png):
  pomarańczowy bok PETG, ciemna osłona, szare metalowe łączniki.
  Pomarańczowy jest wyróżnieniem kontrolnym, nie kolorem filamentu.

Wybierz `ShellMounted20` lub `Belly22` i naciśnij Spację, by ukryć daną
osłonę. `V22_Views.FCMacro` przełącza obie naraz; to podgląd wnętrza,
nie przekrój. `Detail22.FCMacro` odtwarza obrazy na kopiach brył, zamyka
podgląd pomocniczy i przywraca całego kota.

Raporty: `validation.json`, `assembly-validation.json`, `print-validation.json`,
`saved-document-validation.json`. Skrypty: `build22.py`, `check22.py`,
`export22.py`, `Apply22.FCMacro`, `verify22.py`, `Detail22.FCMacro`,
`V22_Views.FCMacro` w `tools/freecad/skorupa/`.
`BellyMountDesign22.FCStd` zawiera pomocnicze szkice i etapy otworów,
**nie końcowy zestaw do druku**; kieszenie nakrętek są dopracowane w skrypcie
i końcowych bryłach złożenia. Geometrię obliczono Pythonem FreeCADa,
a zapis złożenia i podglądy wykonano przez MCP FreeCAD.
