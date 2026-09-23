# Diagnostyka naprawy korpusu — warianty odrzucone

2026-09-23. **Nie ma naprawionego korpusu ani zatwierdzenia wydruku.**
Źródłowe `Shell.FCStd` i złożenie `RobotCat.FCStd` pozostają bez zmian.
Badanie nie zmienia mocowań, jointów, materiału PETG ani parametrów ruchu.

## Wyniki

Kontrole wykonano w osobnych procesach FreeCAD 1.1.3 / OCCT 7.8.1.
Podział C0→C1: osobne środowisko `cadquery-ocp==7.8.1.1`, `vtk==9.3.1`.
Instalację tego środowiska dokończono; wcześniejszy brak miejsca nie jest już
aktualną przeszkodą. Nie modyfikowano instalacji FreeCAD.

| Wariant | Zwykła poprawność | Ścisłe BOP | Decyzja |
|---|---|---|---|
| Obie bryły bazowe | tak | 12 krawędzi i 10 ścian C0; dwa przypadki błędnej krzywej na powierzchni | wymaga naprawy |
| Sam podział C1 | nie | niepoprawne flagi same-parameter | odrzucony |
| Podział C1 + ShapeFix | tak | 21 krawędzi i 2 ściany C0; oba błędy krzywych pozostają | odrzucony |

Każdy wariant sprawdzono dla `Shell35Source` oraz końcowego `Shell35`.
ShapeFix nie oznacza zaliczenia kontroli. Po podziale liczba ścian wzrasta
z 302 do 317 (źródło) i z 304 do 319 (końcowa skorupa). Obwiednia jest taka
sama, ale obliczona objętość zmienia się o około −15,3 do −15,6 mm³.
Nie używać samej obwiedni ani podobnej objętości jako dowodu równoważności;
na wadliwych bryłach te liczby nie rozstrzygają o fizycznej różnicy kształtu.

## Dokładna lokalizacja

`fault-locations.json` wiąże indeksy z SHA-256 konkretnych BRepów:

- Źródłowa bryła: `Face242`, `Edge854` i `Edge855`.
- Końcowy `Shell35`: `Face244`, `Edge862` i `Edge863`.
- Wadliwe krzywe leżą przy X ≈ −57,15 mm, Y ≈ 30,25…38,15 mm,
  Z ≈ 41,99…44,94 mm, w lokalnym układzie bryły.

To dwa przypadki `InvalidCurveOnSurface`; każdy raportuje krawędź i tę samą
ścianę. Nie są to cztery niezależne usterki. Pozostałe 22 zgłoszenia dotyczą
ciągłości C0. Lokalizacja bada wyłącznie te dwie klasy problemów; nie zastępuje
pełnego BOP. Indeksy nie są trwałymi nazwami mocowań i po przebudowie zmienią się.

## Dowody i odtworzenie

- `baseline.json`: kontrola obu brył bazowych i opis powierzchni B-spline.
- `continuity-trial.json`: parametry algorytmu oraz hashe wejść i kandydatów.
- `audit-split.json`, `audit-fixed.json`: zakończone, negatywne kontrole
  kandydatów w FreeCAD, nie deklaracja udanej naprawy.
- `fault-locations.json`: numery ścian/krawędzi i ich obwiednie.
- `study-manifest.json`: przypięte źródła, kod i raporty; bramka geometrii
  ma status `fail`. Integralność przechodzi, zgoda na druk ma zostać odrzucona.

Z korzenia repo, osobne procesy:

```text
<FreeCAD-python> tools/cad/shell_repair_study.py scan
<OCP-venv-python> tools/cad/shell_repair_study.py continuity-trial
<FreeCAD-python> tools/cad/shell_repair_study.py candidate-audit split
<FreeCAD-python> tools/cad/shell_repair_study.py candidate-audit fixed
<OCP-venv-python> tools/cad/shell_repair_study.py locate-faults
<python> tools/cad/shell_repair_study.py package-report
<python> -m unittest discover -s tools/cad -p test_shell_repair_study.py
```

Nie importować OCP i FreeCAD do jednego procesu. Dane `*.brep` są lokalnymi,
ignorowanymi wynikami odtwarzanymi przez pierwsze dwa polecenia, nie masterami
ani plikami do druku. Raporty zachowują ich hashe. Nie pakujemy kolejnych
27 MB odrzuconych kopii do historii repo. Tryb `native-trials` jest dostępny
jako dodatkowy eksperyment, ale **nie był uruchomiony** w tym badaniu.

Następny etap: celowana przebudowa krzywych na wskazanej powierzchni i analiza
pozostałych granic C0. Każdy nowy wariant wymaga pełnego BOP, porównania
powierzchni i sprawdzenia interfejsów mechanicznych przed podmianą modułu.
Po naprawie i zmianie złożenia potrzebne są nowe dowody kinematyki; obecne
wyniki dotyczą niezmienionego modelu. Brakujące pomiary orczyka, pasowania
PETG, obciążenia i montaż głowy pozostają osobnymi otwartymi sprawami.
