# v23 — mocowanie akumulatora, PETG

**Prototyp montażowy. To nadal nie komplet robota zatwierdzony do druku.**

Złożenie: [Kot_v23_AKUMULATOR_PETG.FCStd](Kot_v23_AKUMULATOR_PETG.FCStd).
Poprzednie wersje, w tym v22, zachowano. Nie zmieniono geometrii ani położeń
serw, łap, głowy, ogona, elektroniki ani dolnej płyty podwozia. Starą
`BatteryTray` ukryto, nie usunięto. Nowa część to `BatteryCarrier23`.

## Pakiet i założenia

Istniejący model opisuje pakiet **Gens ace GEA223S60X6SGT**. Producent podaje
obwiednię około **90 × 43 × 19 mm**, masę około 158 g, softcase i XT60-F:
[karta Gens ace](https://gensace.de/de/collections/test-new/products/gea223s60x6sgt)
(sprawdzono 2026-09-19). To potwierdzenie wymiarów katalogowych, **nie
potwierdzenie modelu zakupionego przez użytkownika**. Obwiednia nie obejmuje
przewodów i złączy; ich wyjście oraz rzeczywiste tolerancje trzeba zmierzyć.

Akumulator pozostał w globalnym X = −18…72, Y = ±21,5, Z = 6,2…25,2 mm.
Pod nim dodano kupną miękką, nieprzewodzącą podkładkę o nominalnej grubości
1 mm. Konkretny materiał/dostawca i grubość pod obciążeniem wymagają doboru.
Nie drukować podkładki ani pasków z PETG.

## Połączenia mechaniczne

Tacka opiera się na dolnej płycie WAVEGO na Z = 0, a nie wisi 1 mm nad nią
jak poprzednia geometria. Osie czterech mocowań pochodzą z rzeczywistych
otworów tej płyty: **X = 1 i 59 mm, Y = ±24,5 mm**.

- 4 śruby **M2.5×8 ISO 7380-1**, bez kołnierza, od spodu;
  obwiednia łba maksymalnie Ø4,7 × 1,5 mm.
- 4 metalowe nakrętki M2.5, nominalnie AF5 × 2 mm, wsuwane z boku tacki
  przed jej instalacją. Kieszenie AF5,3, wysokość 2,3 mm.
- Śruba przechodzi przez istniejący otwór płyty Ø2,6 i otwór tacki Ø2,9.
  Dolnej płyty w tym etapie nie rozwiercono; Ø2,6 to ciasny nominalny luz
  dla M2.5, wymagający sprawdzenia rzeczywistego wykonania.
- Nakrętka opiera się na podłodze PETG na Z = 3,2. Śruba kończy się na
  Z = 6,5, czyli 1,3 mm ponad nakrętką; jej kanał jest zamknięty od góry.
  Metal nie przecina obwiedni pakietu.
- Dwa kupne paski na rzep szerokości 15 mm, nominalnie 1 mm grubości,
  przechodzą pod tacką w kanałach 16 × 2,2 mm i nad pakietem. Osie pasków
  X = 14 i 44 mm. Podłoga nad kanałami ma **3 mm**.
  Model uwzględnia lokalną zakładkę do 2 mm grubości. Długość do doboru
  do rzeczywistego paska i zakładki (orientacyjnie 250 mm, nie wybrany SKU).

Otwory zaprojektowano według skilla MCP FreeCAD **Fastener Hole Patterns**
(szkic i Pocket, Ø2,9 dla M2.5). Wymiary niskiego łba sprawdzono w
[karcie dostawcy Ettinger, rodzina ISO 7380-1 M2.5](https://www.ettinger.de/en/product-datasheet/e7dd412396afa2367749a67e2eda66cd/create).
Podlinkowana karta dotyczy długości 6 mm i potwierdza łeb; projekt wymaga
**8 mm**. Nie zastępować zwykłym wysokim łbem walcowym ani wersją z kołnierzem.
Gwinty i gniazdo narzędzia nie są modelowane — łączniki to obwiednie.
Nie dodano więzów solvera Assembly ani symulacji naprężeń.

## Kontrole i ograniczenia

- Jedna poprawna bryła PETG oraz 11 poprawnych obwiedni kupnych:
  osiem metalowych łączników, podkładka i dwa paski. Kontrola BOP przeszła.
- Brak statycznych kolizji nowych elementów z widocznymi zachowanymi
  częściami i między nowymi elementami (próg objętości 0,001 mm³).
- 16 kontroli podparcia łbów, tacki i nakrętek przeszło; cztery kontrole
  styku pasków z tacką/pakietem wykazują kontakt po obu stronach pętli.
  To geometria, **nie dowód nośności, siły zacisku ani skuteczności rzepu**.
- 32 pozycje wsuwania nakrętek w tackę poza robotem nie wykazały kolizji.
  Paski również należy przewlec przed przykręceniem tacki. Nie dowodzi to
  możliwości montażu całego zespołu w zamkniętym podwoziu.
- Wałek śrubokręta Ø4 × 30 mm ma dostęp od spodu **po zdjęciu brzucha**.
  Nie modelowano rękojeści ani dłoni.
- Wszystkie 19 pozycji drogi demontażu brzucha z v22 pozostaje wolne od
  nowych elementów. To nadal kontrola próbkowana, nie ciągła trajektoria.
- Między łbem śruby i brzuchem jest nominalnie **0,5 mm**. Nie zakładać,
  że druk zachowa ten luz bez prób; nie dodawać podkładek pod łby bez
  ponownego sprawdzenia stosu wymiarów.
- Otwory są blisko krawędzi starej płyty, która ma tylko **1,5 mm**.
  Jej nośność w PETG, pełzanie i cały układ przenoszenia obciążeń nadal
  wymagają oceny. Ten etap nie zatwierdza odziedziczonej cienkiej płyty.
- **Droga wyjmowania samego akumulatora, dostęp do rzepów w pełnym robocie
  i przewody nie są jeszcze zweryfikowane.** Górna płyta podwozia znajduje
  się nad pakietem; nie traktować go jako gotowego modułu szybkiej wymiany.
- Nie przeprowadzono prób druku, obciążenia, temperatury ani dynamicznych
  kolizji. Nie zaciskać mocowania siłą na miękkim pakiecie. Przed fizycznym
  montażem trzeba potwierdzić pakiet, paski, podkładkę i dostęp serwisowy.

Pozostają też pozostałe uchwyty elektroniki, przewody i mechanika głowy/
ogona, w tym nierozstrzygnięte 3 mikroserwa w BOM wobec 4 w starym modelu.

## Druk i podgląd

`stl-prototype/BatteryCarrier23.stl`: **100 × 59 × 9,2 mm**, czarny PETG,
płaską podstawą na stół. Zamknięta siatka mieści się w 256³ z brimem 8 mm.
Kanały pasków mają 16-mm przęsła, a kieszenie nakrętek niskie stropy:
sprawdź mosty, podpory i pasowanie w slicerze oraz na próbce PETG.
To jedyna część do druku dodana w v23, nie pełny zestaw robota.

- [Cały kot](kot-v23-zlozony.png) — taki widok pozostawiono w FreeCADzie.
- [Mocowanie z pakietem i paskami](akumulator-v23-zlozenie.png).
- [Rzeczywisty przekrój śruby i gniazda](akumulator-v23-przekroj.png).

Na przekroju pomarańczowa jest dolna płyta, szare są metalowe łączniki,
ciemna jest tacka, niebieski jest pakiet. Kolory kontrolne płyty i pakietu
w obrazach pomocniczych nie zmieniają materiałów głównego złożenia.
W głównym modelu drukowane części są czarne, paski ciemne, metal szary.

W FreeCAD można ukryć `ShellMounted20`, `Belly22` oraz `Part__Feature038`
(górną płytę) klawiszem Spacja, aby obejrzeć wnętrze. Nie jest to demontaż
mechaniczny. `Detail23.FCMacro` odtwarza widoki na kopiach, a potem przywraca
całego kota. `BatteryCarrierDesign23.FCStd` zawiera pomocnicze etapy projektu
wraz ze szkicem i Pocket oraz finalną geometrią kanałów nakrętek.

Raporty: `validation.json`, `assembly-validation.json`, `print-validation.json`,
`saved-document-validation.json`. Skrypty w `tools/freecad/skorupa/`:
`build23.py`, `check23.py`, `export23.py`, `Apply23.FCMacro`, `verify23.py`,
`Detail23.FCMacro`. Geometria obliczona Pythonem FreeCADa; zapis złożenia
i podglądy przez MCP FreeCAD. v22 nie nadpisano.
