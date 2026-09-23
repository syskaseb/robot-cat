# R4 w pełnym złożeniu kota

23.09.2026. **Zintegrowany prototyp, nie wydanie do druku.**

[Cały kot](whole-cat.png) · [Pokrywa R4 w złożeniu](tail-installed.png).

Otwieraj `hardware/cad/assembly/RobotCatTailCartridge.FCStd` z zachowaniem
struktury repo. To cały robot, nie studium adaptera. Aktualny punkt wejścia
wskazuje `hardware/cad/current-assembly.json`. Poprzedni `RobotCat.FCStd`
i wszystkie jego osiem zależności pozostają niezmienione dla odtwarzalności
wcześniejszych audytów. Nie otwieraj obu pełnych złożeń równocześnie.

## Zakres integracji

- Nasada `TailRoot29` i pokrywa `BearingCap34` wskazują teraz edytowalny
  `modules/tail/TailCartridge.FCStd`, skopiowany z zatwierdzonego do integracji
  zakresu studium R4, bez przebudowy jego geometrii.
- Dodano dolną płytkę PETG, cztery nominalne M2×10 i cztery nakrętki M2.
  Dziewięć nowych Fixed łączy je z wirującą nasadą. Osie i ramki wszystkich
  319 wcześniejszych połączeń pozostają niezmienione.
- 329 części, 315 Fixed + 13 Revolute; nadal **29 TEMP**. 54 części mają
  zewnętrzne App::Link, 275 jest odziedziczonymi snapshotami. Dziesięć
  dokumentów w sesji oznacza jedno złożenie i dziewięć zależności.
- Nowy moduł posiada 25 w pełni związanych szkiców, trzy fizyczne części PETG
  i osiem nominalnych łączników. `UpperCarrierPETG` jest zużytą historią
  operacji, nie dodatkowym wydrukiem. Stare nasada/pokrywa pozostały w
  historycznym masterze, ale nie są instancjami obecnego kota.
- Orczyk społecznościowy nie jest traktowany jako zamontowana część.
  Dotychczasowe tymczasowe sprzęgnięcie napędu pozostaje jawnie niezatwierdzone.

[BOM różnicowy](../../../bom/tail-cartridge-installation.json) zastępuje dwa
wpisy poprzednika i dodaje dziewięć części. Nie sumować obu wersji nasady/pokrywy.
Orientacje PETG, nominalne wymiary i otwarte bramki są w BOM oraz
[studium R4](../../studies/tail-cartridge-clearance/README.md).
Gabaryty nowych wydruków zmierzone także przez MCP w złożeniu:
nasada około 47,10 × 32,99 × 33 mm, płytka 25,2 × 32,5 × 4,2 mm,
pokrywa 38 × 34 × 5 mm. Z zapasem 20 mm mieszczą się na stole 256³;
nie zastępuje to kontroli podpór i ścieżek w slicerze.

Pochodzenie referencji orczyka: Alberto / otrebla333, Dtto v2.0.1,
CC BY-SA 4.0, jak w przypiętym studium R4. Nie pobrano nowej obcej geometrii.

## Dowody i ich granice

Wszystkie poniższe kontrole integracji zakończone pozytywnie. **70 testów CAD**
(w tym 9 nowych), bez pominięć; wynik w `tests.json`. Manifest obejmuje także
wcześniejsze checkpointy i nadal odmawia wydania do druku.

- `migration.json` przypina źródła i zachowanie poprzednich dziewięciu plików.
- `geometry.json` porównuje 318 niezmienionych części z poprzednikiem i
  11 nowych/zmienionych z R4. Sprawdza BOP nowych brył, spoczynek oraz
  13 próbek ogona od −30 do +30° co 5°. To inkrementalne sprawdzenie
  zmienionych części względem reszty, nie naprawa dawnych kolizji i skorup.
- `relocation-native.json` pochodzi ze świeżego procesu i kopii w nowym
  katalogu. Sprawdza automatyczne wczytanie zależności, zmianę promienia
  słupków, otworów śrub i wybrań pokrywy przez odnośniki oraz przywrócenie.
  Natywny test obejmuje 22 klatki, nogi ±3°, ogon ±30°, wszystkie ramki
  połączeń i globalne położenia geometrii, także nowych śrub i nakrętek.
  W każdej klatce mierzone są ramka bryły oraz pierwszy/środkowy/ostatni
  wierzchołek każdej części. Przemieszczenia środków nowych części wynikają
  z tak zweryfikowanych transformacji sztywnych, nie z ponownego liczenia
  ich całek objętościowych w każdej klatce.
- Kolejność montażu i dostęp narzędzi dziedziczą dowody studium R4 dopiero
  po potwierdzeniu tożsamości geometrii/położeń; nie wykonano fizycznego montażu.
- Zapis audytów nie zapisuje CAD. Kopie niezapisanej wcześniejszej sesji
  zachowano lokalnie w ignorowanym `_before-tail-cartridge-integration`.

**Nie zatwierdzono** rzeczywistego orczyka, śruby centralnej/wieloklinu,
pasowań łożysk/PETG, momentu dokręcenia, trwałości i pełzania ani wiązki.
Błędy BOP odziedziczonej skorupy i 29 TEMP pozostają. Gazebo v35 dotyczy
poprzedniej geometrii; nie wykonano nowej próby dynamicznej tej integracji.

## Odtworzenie

Python dostarczony z FreeCAD 1.1.3, z korzenia repo, jeden proces naraz:

```text
python tools/cad/validate_tail_integration.py geometry
python tools/cad/validate_tail_integration.py relocation
python tools/cad/package_tail_installation.py
python -m unittest discover -s tools/cad -p "test_*.py"
python tools/cad/release_check.py hardware/releases/tail-cartridge-installation.json
```

`--require-print-ready` ma odmówić. `integrate_tail_cartridge.py` to jednokrotna
migracja przez GUI/MCP, nie generator do ponownego uruchamiania na gotowych plikach.
Źródłem kolejnych zmian jest edytowalny moduł. Nie tworzono tagu produkcyjnego.
