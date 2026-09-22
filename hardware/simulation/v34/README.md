# Gazebo v34 — dodatkowa masa podparcia ogona

Źródło: [Kot v34](../../skorupa/v34/README.md), SHA256
`b3b342604b649bde0f2224462c6ea8d241b0b2a4d46479756a4aad8877da7182`.
306 komponentów CAD,13 ciał dynamicznych i12 osi nóg.
**Głowa i ogon nadal zamrożone w fizyce**; masa i bezwładność nowego
podparcia są uwzględnione. Test nie symuluje tarcia łożysk, orczyka,
ugięcia PETG ani ruchu napędów pomocniczych.

Masa nominalna **2,501738 kg**, zakres założeń2,218581–2,966950 kg.
Wzrost względem v33 wynosi77,676 g. PETG jest liczone z pełnej objętości
CAD przy1,27 g/cm³; każde 608ZZ ma jawne założenie13 g, nie masę
wynikającą z pełnej stalowej obwiedni i nie zweryfikowaną masę produktu BTC.
Masy zakupu, gęstość i rezerwa wiązki są objęte wariantami bilansu.
Rzeczywistą masę trzeba zważyć po wydruku i złożeniu.

Nieruchoma podpora trafia do korpusu. Przy osobnym bilansie ogona
`auxiliary-budget.json` wirujący zespół ma60,563 g, w tym czop, pierścień,
śrubę i nakrętkę. Budżet yaw na pionowej osi nie jest zatwierdzeniem
łożysk ani MG92B. Fizyczny orczyk pozostaje niezaprojektowany.

## Zakres prób

| Próba | Masa | Najwyższy RMS stawu | Droga po rozruchu | Wynik |
|---|---:|---:|---:|---|
| Stanie8 s | 2,502 kg | 0,5635 Nm | <0,001 mm | ukończona |
| Crawl15 s | 2,502 kg | 0,6055 Nm | 84,2 mm/12 s | ukończona |
| Crawl15 s, cięższy | 2,967 kg | 0,6806 Nm | 89,5 mm/12 s | ukończona |

Trzy próby bez wykrytego upadku. W staniu1/801 próbka była nieaktualna,
wyłączono ją z obliczeń; oba chody mają1501/1501 świeżych próbek.
Wszystkie12 przegubów pozostało w użytej obwiedni moment–prędkość.
632 testy ROS/CAD/narzędzi zaliczone przed Gazebo; regresja poprzedniego
v33:622. Trzy ostrzeżenia deprecacji dotyczą zależności protobuf.

Konfiguracja porównawcza: stanie8 s oraz wolny crawl15 s nominalnie i
w wariancie cięższym. Krok24 mm, unoszenie6 mm, cykl4 s, duty87,5%,
stopy−30/−5 mm względem CAD, tarcie0,4, limit komendy1 Nm i zależna
od prędkości obwiednia ST3215 przy10,5 V. Nie ma sztucznego ogranicznika
prędkości jointów. To krótkie próby z uproszczonymi stopami, bez pełnych
samokolizji i modelu termicznego. Wyniki i telemetria: [RESULTS](RESULTS.md).

`duration_completed` oznacza zakończenie bez wykrytego upadku, **nie
zatwierdzenie do biegu ani pracy ciągłej**. Stall i umowne25% stall nie
są podanym przez producenta momentem ciągłym. Wnioski trzeba odnieść do
ważenia, pomiarów prądu, temperatury i rzeczywistego napędu.

Względem v33 RMS wolnego chodu wzrósł z0,5750 do0,6055 Nm nominalnie
i z0,6514 do0,6806 Nm dla cięższego wariantu. **ST3215 pozostaje kandydatem
do powolnego chodu**, bez potwierdzenia pracy ciągłej. Wyniku nie można
traktować jako zapasu na szybszy ruch; limit sterownika ucina moment.
Najbardziej obciążony przegub dobijał do limitu przez4,4% próbek nominalnie
i21,3% w cięższym chodzie. Rzeczywiste zapotrzebowanie przy idealnym
śledzeniu może być większe niż zarejestrowany limit1 Nm.

## Odtwarzanie i spójność

Ustaw `ROBOT_CAT_CAD_REVISION=v34`. Python FreeCAD:
`tools/freecad/skorupa/cache34.py`, potem `export_dynamics.py`
i `export_dynamics.py --meshes`. W środowisku z NumPy: `cad_model.py`
i `auxiliary_budget.py`. W Dockerze ROS Jazzy/Gazebo Harmonic:
`python3 -m pytest src tools/simulation -q`, następnie
`python3 tools/simulation/run_v32_screening.py --suite baseline`.
Historyczna nazwa runnera jest zachowana; obsługuje też v34.

Przed uruchomieniem Gazebo w kontenerze wykonaj
`source /opt/ros/jazzy/setup.bash` (bez `set -u`), aby CLI `gz` było w PATH.
Pierwsze uruchomienie v34 pominięło ten krok i nie wystartowało symulatora;
zapisano `startup-failure.json` i log w archiwum telemetrii. Nie jest to
próba ruchowa, nieudany chód ani upadek.

Plugin: `GZ_SIM_SYSTEM_PLUGIN_PATH` musi zawierać katalog biblioteki
`librobot_cat_cad_actuator.so` i `/opt/ros/jazzy/lib`. Runner uruchamia
własny `GZ_PARTITION` i kończy tylko swoją grupę procesów; nie steruje
prawdziwymi serwami. Szczegóły środowiska: [README nadrzędne](../README.md).

`inputs.zip`, `meshes.zip`, `telemetry.zip` są bezstratne, podpisane
`.sha256`; lokalne pliki surowe nie są kasowane. `prepare_assets.py
--revision v34` odtwarza dane, `verify_v34.py` wiąże archiwa z CAD,
masterem, testem natywnym i audytem dziedziczenia geometrii. Fit-audit
powstał przed integracją, na podpisanym masterze/v33;27 porównań kopii
master→złożenie domyka jego powiązanie z finalnym v34.

Nadal30 więzów tymczasowych, dwa napędy głowy i część elektroniki niegotowe,
stare konflikty głowy OPEN. Nowa podpora nie jest wydaniem całego robota.
