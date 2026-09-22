# Gazebo v33 — aktualna głowa, regresja obciążeń nóg

Źródło: [Kot v33](../../skorupa/v33/README.md), SHA256
`8a6056496a2e4aeb1ad7b7887c94a9a9f4b9419e202aa05c7d2888851dbe07a4`.
289 komponentów CAD, 13 ciał dynamicznych i 12 osi nóg.
**Głowa i ogon są zamrożone w fizyce**, ale ich masa i bezwładność są policzone.
Jednoczęściowy przód nie dubluje masy dawnego `Muzzle`; śruby mikrofonów
są stalą, moduł zachowuje niezważony zapas 20 g. Siatki pochodzą z tego CAD.

Masa nominalna **2,424062 kg**, zakres założeń 2,147210–2,881743 kg.
To szacunek z objętości PETG i mas zakupowych, nie wynik ważenia wydruku.
Masa zespołu głowy do wstępnego bilansu 187,2 g. Dla starej osi zastępczej
wyliczono 0,0743 Nm przy ±20° i przyspieszeniu 2 rad/s²; nie jest to
zatwierdzenie MG92B, jego orczyka ani uchwytu. Korzystniejsze wyważenie
przy środku masy nadal wymaga rzeczywistego projektu obu osi.

## Trzy nowe próby

| Próba | Masa | Najwyższy RMS stawu | Przemieszczenie po rozruchu | Wynik |
|---|---:|---:|---:|---|
| Stanie, 8 s | nominalna | 0,5352 Nm | <0,001 mm | ukończona |
| Wolny crawl, 15 s | nominalna | 0,5750 Nm | 78,2 mm /12 s | ukończona |
| Wolny crawl, 15 s | cięższa | 0,6514 Nm | 82,1 mm /12 s | ukończona |

Krok 24 mm, uniesienie 6 mm, cykl 4 s, duty87,5%, położenie stóp −30/−5 mm,
tarcie 0,4, ograniczenie sterownika 1 Nm oraz zależna od prędkości obwiednia
ST3215 przy 10,5 V. Brak sztucznego limitu prędkości jointów. Obciążenia liczone
ze świeżej telemetrii po rozruchu. W staniu 1/801 próbek była nieaktualna
i została wyłączona z obliczeń; w obu chodach 1501/1501 świeżych próbek.
To krótkie, uproszczone testy, bez pełnych samokolizji i termiki.

622 testy ROS/CAD/narzędzi przeszły przed uruchomieniem Gazebo, w Dockerze
z ROS Jazzy. Włączono regresję współrzędnych otworów i podpisu audytu siatki.
Regresja v32: 619 przeszło, 3 testy wyłącznie v33 pominięte. Trzy ostrzeżenia
deprecacji pochodzą z zależności protobuf, nie są nieudanymi testami mechaniki.
Zwykły Python Windows nie ma pakietów Gazebo; nie zastępuje tego środowiska.

**Wniosek bez zmian:** ST3215 pozostaje kandydatem do wolnego chodu.
Nie zatwierdzono biegu ani pracy ciągłej. Umowne 25% stall nie jest momentem
ciągłym producenta; cięższy crawl nadal przekracza ten próg. Poprzednie
17 prób v32, w tym upadek wariantu cięższego przy limicie0,65 Nm, pozostają
zachowaną historią — nie przenosimy ich jako wykonanych prób v33.

## Dane i odtwarzanie

Pierwszy szkic v33 i jego trzy inne próby odrzucono po audycie geometrii.
Są zachowane w [rejected-initial](rejected-initial/README.md), z osobnymi
archiwami i podpisami. Nie mieszają się z trzema próbami aktualnego modelu.
Nowy audyt usuwa wadliwe krawędzie siatki głowy, ale nie rozwiązuje wszystkich
błędów BOP (w tym SelfIntersect), kolizji wkładek/szyi ani mocowania ucha do serwisu.

`inputs.zip`, `meshes.zip`, `telemetry.zip` są bezstratne i mają podpisy
`.sha256`. Surowe pliki robocze są lokalne; archiwa nie zmieniają dawnych wersji.
`baseline-suite.json` wiąże konfiguracje z wynikami, `checkpoint-integrity.json`
sprawdza również podpisy CAD/mastera, geometrię, więzy i telemetrię.

Ustaw `ROBOT_CAT_CAD_REVISION=v33`. Odtworzenie danych:
`python tools/simulation/prepare_assets.py --revision v33`.
Eksport BRep/siatek: Python FreeCAD i `tools/freecad/skorupa/export_dynamics.py`
(siatki z `--meshes`). Obliczenia: `cad_model.py`, `auxiliary_budget.py`.
W kontenerze z ROS i pluginem aktuatora:
`python tools/simulation/run_v32_screening.py --suite baseline` — historyczna
nazwa skryptu, obecnie obsługuje v32 i v33. Kontrola: `verify_v33.py`.
Pełny opis środowiska i ograniczeń: [README nadrzędne](../README.md).
