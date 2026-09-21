# v24 — natywne złożenie i test połączeń FreeCAD

**Prototyp kinematyczny, nie zatwierdzony komplet do druku.**

Plik: [Kot_v24_ASSEMBLY.FCStd](Kot_v24_ASSEMBLY.FCStd).
Zachowuje geometrię, kolory i pozycję spoczynkową 238 widocznych części v23.
Nie zmienia kształtów PETG ani elementów kupnych. v23 i jego historia pozostają
osobnym, niezmienionym plikiem; v24 jest niezależnym złożeniem jego brył.

## Co faktycznie połączono

- Natywny `Assembly::AssemblyObject` z jedną uziemioną częścią `Rigid_FrameFront20`.
- **12 Revolute**: trzy osie w każdej łapie.
- **225 Fixed**, w tym **64 jawnie tymczasowe blokady** głowy, ogona,
  elektroniki i innych nieukończonych mocowań. Dokładną listę zawiera
  `assembly-plan.json`, a każdy joint ma właściwość `DesignStatus`.
- Wszystkie 238 części należą do jednego połączonego drzewa. Nie dodawano
  redundantnych pętli więzów przez każdą śrubę tego samego sztywnego zespołu.

Osie nóg odczytano z rzeczywistych powierzchni cylindrycznych orczyków
o promieniu 9,6 mm. Źródło, numer powierzchni, kierunek i położenie każdej osi
są zapisane w planie. Zachowano naprawiony wcześniej podział ruchomych zespołów:
obudowy serw i leg linki nie są przypisane do obracających się orczyków
tego samego serwa. Nie dodano limitów serw bez danych ich rzeczywistego zakresu.

Nazwy wewnętrzne FR/RR pochodzą ze starego WAVEGO. Etykiety jointów pokazują
przód/tył kota poprawnie: **głowa −X, ogon +X**.

Każda część ma własny kontener `Rigid_*` z lokalnym układem solvera.
Bryła źródłowa jest jego dzieckiem. To usuwa zaobserwowany w FreeCAD 1.1.3
błąd solvera przy bezpośrednim wiązaniu importowanych, obróconych brył.
Jointy używają zapisanych układów JCS (`Detach1/2`), nie automatycznego
przesuwania części przy dopasowaniu powierzchni. Przy przyszłej zmianie
geometrii osi trzeba więc ponownie wyznaczyć JCS — nie aktualizują się
automatycznie z nowego kształtu orczyka.

## Jak uruchomić animację w samym FreeCADzie

Sprawdzono w FreeCAD **1.1.3**, wbudowany workbench **Assembly**.

1. Otwórz plik v24 i przełącz na **Assembly**.
2. Rozwiń `RobotCatAssembly24`, następnie grupę symulacji.
3. Otwórz dwuklikiem **Test polaczen lap | 12 osi | bez fizyki kontaktu**
   (`LegConnectionTest24`).
4. W panelu zadań uruchom obliczanie kinematyki (**Run Kinematics**).
   Przy tym rozmiarze złożenia obliczenie może potrwać kilka minut.
5. Użyj przycisku odtwarzania do przodu albo suwaka klatek.
6. Zatwierdź/zamknij panel; standardowy panel przy zatwierdzeniu odtwarza
   położenia części sprzed uruchomienia. Plik zapisano w pozycji spoczynkowej,
   z widocznym całym kotem i ukrytymi znacznikami jointów.

To krótki test wychylenia **±3°** wszystkich 12 osi, nie animacja pełnego chodu.
Wzory ruchu są natywnymi obiektami `Motion`; nie trzeba instalować naszego
makra do normalnego odtwarzania. Funkcje trygonometryczne tej instalacji
przyjmują amplitudę w radianach; sprawdzono to na wyniku solvera.

## Wyniki kontroli

`initial-solve.json`: solver zwrócił 0, bez zmiany pozycji początkowych
(maksymalna różnica translacji około 1,06 × 10⁻²⁶ mm).

`simulation-validation.json`: **22 klatki**, wszystkie 12 osi osiąga 3°.
W każdej klatce sprawdzono wszystkie 237 połączeń:

- maksymalna odległość między początkami JCS: **1,38 × 10⁻¹³ mm**;
- brak mierzalnego względnego obrotu połączeń Fixed;
- brak mierzalnego rozchylenia osi Revolute.

Są to reszty numeryczne modelu, **nie tolerancje rzeczywistego wydruku**.
Kontrola geometrii i ponownego otwarcia jest w `saved-document-validation.json`.
Obejmuje wszystkie 238 brył, ponad 422 tys. punktów kontrolnych powierzchni,
krawędzi i wierzchołków, pola powierzchni i objętości, zapisane materiały
poszczególnych powierzchni oraz ponowne rozwiązanie natywnych więzów.

## Co nadal wymaga pracy

**Fixed nie zastępuje śrub, wsporników ani rzeczywistego napędu.**
Blokady tymczasowe zapobiegają rozsypaniu wizualizacji, ale nie certyfikują
fizycznego zamocowania elementów. Głowa i ogon nie są w tym teście napędzane.
W modelu pozostają cztery obwiednie serw pomocniczych, a lista zakupów mówi
o trzech; wymagany jest wybór konfiguracji oraz potwierdzenie modeli serw
i orczyków przed zaprojektowaniem ich rzeczywistych osi i mocowań.

Nie wykonano tu testu kolizji w ruchu, styku łap z podłożem, dynamiki,
obciążeń silników, naprężeń ani odkształceń PETG. Nie zweryfikowano pełnego
zakresu ruchu. Bryły są sztywne, także obwiednie pasków i elastycznego ogona.

### Audyt serwisu akumulatora — znaleziony problem, jeszcze nie naprawiony

`service-probe.json` sprawdza próbę opuszczenia zespołu dolnej płyty,
akumulatora, tacki, pasków i jej śrub po zdjęciu brzucha.
**Droga pionowo w dół jest zablokowana przez dolne krawędzie SideLeft22
i SideRight22** (próbki przesunięcia 1, 5, 10 i 20 mm mają przecięcia).
Wolna pozycja końcowa poniżej robota nie oznacza wolnej drogi dojścia.
Demontaż samego brzucha pozostaje sprawdzony oddzielnie w v22/v23.

Próbny pionowy kanał przewodu Ø7 przy X=98,7, Y=0, Z=31…78 również przecina
`Part__Feature106` i `ShellMounted20`. Nie wycięto go. Trasa kabli i ich
wyjście z rzeczywistego pakietu są nadal do zaprojektowania.

## Odtworzenie / diagnostyka

Skrypty `tools/freecad/skorupa/`:

- `plan24.py` — plan więzów z zapisanego v23 i starej hierarchii ruchu;
- `Prepare24.FCMacro` — niezależne bryły w kontenerach `Rigid_*`;
- `appearance24.py` — zachowanie materiałów poszczególnych powierzchni
  i opisów produkcyjnych ze źródłowego modelu;
- po przygotowaniu: narzędzie MCP `create_assembly`, etykieta
  `RobotCatAssembly24`, wszystkie kontenery, `Rigid_FrameFront20` jako pierwszy,
  `ground_first=true`;
- `Joints24.FCMacro` — natywne więzy i kontrola pozycji początkowej;
- `Simulation24.FCMacro` — natywna symulacja i kontrola każdej klatki;
- `Save24.FCMacro` — zapis nowego checkpointu i render całego kota;
- `verify24.py` — niezależne ponowne otwarcie, geometria, graf i solver;
- `probe24.py` — audyt nieudanej drogi serwisowej (bez zmian geometrii);
- `debug24.py` — izolowany reproduktor problemu solvera, np. `FR wrappers`.

Uruchamiać skrypty headless interpreterem Python dostarczonym z FreeCAD,
a makra w GUI przez MCP. Nie uruchamiać na Windows macOS-owego środowiska pixi.
Przygotowanie i zapis odmawiają nadpisania istniejącego checkpointu.
