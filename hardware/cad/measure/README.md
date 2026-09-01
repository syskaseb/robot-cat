# Skąd wzięły się wymiary serwa

`params.scad` miało dwie wartości oznaczone `ADJUSTABLE`, bo nie dało się
wtedy dotrzeć do rysunku serwa — Printables i Thingiverse blokują dostęp
automatyczny, a strony sklepowe podają tylko gabaryt. Zostały **zmierzone**,
nie zgadnięte, i to jest opis metody.

## Metoda

STEP zapisuje otwór jako analityczną encję `CIRCLE` — promień i środek stoją
w pliku jako liczby. Nie trzeba więc siatkować, mierzyć na oko ani wierzyć
w tolerancję siatki:

```bash
pip install trimesh scipy shapely rtree cascadio
python hardware/cad/measure/stepdims.py sciezka/do/STS3215_03a.step
```

`stepdims.py` rozkłada plik na encje, rozwiązuje `CIRCLE → AXIS2_PLACEMENT_3D
→ CARTESIAN_POINT` i szuka grup czterech otworów o tej samej średnicy,
leżących w jednej płaszczyźnie na wspólnym okręgu — czyli rozstawów śrub.

`holes.py` robi to samo dla STL-a, który encji nie ma: bierze ściany, których
normalna jest prostopadła do zadanej osi, dzieli je na spójne płaty i dopasowuje
okrąg metodą najmniejszych kwadratów. Ściany zwrócone normalną do środka to
otwór, na zewnątrz — czop.

```bash
python hardware/cad/measure/holes.py sciezka/do/czesci.stl
```

## Źródła i co z nich wyszło

| źródło | co to jest | wynik |
|---|---|---|
| `TheRobotStudio/SO-ARM100`, `STEP/SO100/STS3215_03a.step` | oficjalny model CAD serwa z projektu referencyjnego dla STS3215 | pełny komplet, patrz niżej |
| `garciamathias/OpenRoboticDog`, `3D Files/hip_x4.stl` | wydrukowana część **innego autora**, mocująca to samo serwo | potwierdza pozycje śrub obudowy |
| `garciamathias/OpenRoboticDog`, `Fusion360/servoFeetechSTS3215.STEP` | model uproszczony (SolidWorks) | zgadza się co do osi i gabarytu, nie ma orczyka |

Trzecie źródło ma orczyk zamodelowany jako gładki dysk Ø24, więc rozstawu śrub
nie potwierdza ani nie obala — po prostu go nie zawiera. Liczy się pierwsze
(dokładne) i drugie (niezależny autor, fizycznie drukowane).

## Zmierzone

Układ: początek w środku obudowy, X wzdłuż serwa (45,4), Y w poprzek (24,8),
Z wzdłuż osi wyjściowej (39,6 z czopami).

| wielkość | wartość | skąd |
|---|---|---|
| gabaryt obudowy | 45,40 × 24,80 × 35,40 mm | bbox modelu, ścianki na z = ±17,7 |
| całkowita wysokość z czopami | 39,60 mm | czop wyjściowy do z = +20,2, jałowy do z = −19,4 |
| oś wyjściowa | x = +12,5 od środka | czyli **10,2 mm od bliższego czoła** |
| **rozstaw śrub orczyka** | **4 × Ø2,5 na okręgu Ø14,00**, co 90°, pod 45° | dopasowanie okręgu, błąd 0,000 mm |
| ten sam rozstaw od spodu | tak, identyczny | serwo jest dwuosiowe — czop jałowy ma taki sam wzór |
| kołnierz wokół osi | Ø22,0, wystaje 1,8 mm ponad czoło | okrąg d=22,011 na z = ±15,9 |
| śruba mocująca orczyk | Ø3,4 w osi (M3) | 10 współśrodkowych okręgów na z = +20,2 |
| śruby skręcające obudowę | y = ±10,25, x = +4,2 / −16,5 / −20,3 | Ø1,5 pilot w Ø4,2 pogłębieniu |
| gniazda sygnałowe | 2 × 3 piny Ø2,0, podziałka 2,4 mm | z = −19,4, dwie trójki po obu stronach |

## Czemu poprzednie liczby były złe

Stara wersja `params.scad` podawała okrąg śrub orczyka jako „trzy otwory na
promieniu 6,7 mm, czwarty na 5,6 mm” i traktowała tę asymetrię jako realną
cechę serwa. To był błąd odczytu `hip_x4.stl`: ta część **nie ma** okręgu
orczyka. Ma cztery otwory Ø1,99 na y = ±10,25, w x = 8,75 i 12,5 — a to są
**śruby skręcające obudowę serwa**, w rozstawie 3,75 mm, który w oficjalnym
CAD-zie wynosi 3,8 mm (x = −16,5 i −20,3). Zgadza się co do dziesiątej.

Wniosek jest praktyczny, nie tylko porządkowy: OpenRoboticDog mocuje serwo do
ramy **przez otwory po śrubach obudowy**, a nie przez orczyk. Oba sposoby są
teraz zmierzone, więc żaden nie jest już `ADJUSTABLE` i **nie trzeba pobierać
uchwytu z Printables**, na którym wisiała cała ta niepewność.
