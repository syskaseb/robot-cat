# Gazebo v31 — rzeczywiste mocowanie głównej przetwornicy

Źródło: [Kot v31](../../skorupa/v31/README.md), **280 części CAD**, 13 ciał
fizycznych i 12 osi nóg. Głowa i ogon są nadal zamrożone w fizyce;
masa i bezwładność wszystkich nowych części nie są pominięte.
To osobny eksperyment, nie zmiana kontrolera historycznego ROS w `src/`.

Masa nominalna **2,420904 kg**, zakres **2,143932–2,878914 kg**.
Względem v30 przybyło nominalnie 1,56 g netto. Główne Pololu nie jest już
liczone jako dawny ogólny zapas 12 g: [producent podaje 4,8 g bez osprzętu](https://www.pololu.com/product/2866/specs).
Dwa zaciski liczone są osobno po **2 g założenia**, nie wartości katalogowej.
Ich uproszczone obwiednie są kupnym plastikiem/metalem, nie bryłami PETG.
Sześć dystansów PETG i osiem elementów stalowych liczone są z objętości.
Pozostałe założenia, w tym rezerwa 120 g, jak w [v30](../v30/README.md).

## Próby i interpretacja

Dokładne wyniki trzech nowych prób: [RESULTS.md](RESULTS.md),
[trial-comparison.json](trial-comparison.json). Testy: stanie 8 s,
wolny chód 15 s nominalnie i dla górnego scenariusza masy; droga po t=3 s,
statystyki przegubów po t=2 s. Parametry porównawcze bez zmian:
stopy −30/−5 mm względem CAD, krok 24 mm, uniesienie 6 mm, cykl 4 s,
podparcie 87,5%, μ=0,4, PD 1 kHz i limit komendy 1 Nm.

Ukończono wszystkie trzy próby bez upadku. RMS max: **0,535 / 0,576 /
0,649 Nm**; droga chodu **78,8 / 82,1 mm w 12 s**, nasycenie **3,7 / 15,4%**
dla nominalnego/cięższego wariantu. Jedyna nieświeża próbka telemetrii
w staniu wystąpiła na t=0,001 s, przed okresem statystyk; nie wchodzi do RMS.
Próby chodu miały świeżą telemetrię. To nie test momentu ciągłego.

Brak sztucznego ogranicznika prędkości. Liniowa obwiednia moment/prędkość
przy 10,5 V pozostaje oszacowaniem dla ST3215 12 V. Limit 1 Nm ucina
komendę; jego osiągnięcie nie dowodzi zapotrzebowania mniejszego od 1 Nm.
Komendy silników nie są pomiarami momentu fizycznego sprzętu.

**Nie ma zatwierdzenia biegu ani momentu ciągłego ST3215.** To nadal
kandydat do wolnego chodu wymagający ważenia i prób prądu/temperatury.
Zakończenie bez upadku nie certyfikuje mechaniki. Samokolizje są wyłączone,
kontakt stóp uproszczony; brak modeli cieplnych, przewodów, pełzania PETG
i napędów głowy/ogona. Ta rewizja nie zatwierdza chłodzenia Pololu w obudowie.

Natywnie FreeCAD sprawdził 22 klatki z 13 osiami (nogi ±3°, ogon ±30°).
Dokładny audyt nowych części: 63 pary w spoczynku bez przecięć >0,01 mm³,
wszystkie dystanse rzeczywiście kontaktują podpory. Część dojść do zacisków
blokuje górna obwiednia rozdzielacza — zapisano to w audycie, bez ukrywania.
260 pozostałych części jest numerycznie niezmienionych względem v30.

`inputs.zip`, `meshes.zip`, `telemetry.zip` zachowują dane i SHA-256.
[checkpoint-integrity.json](checkpoint-integrity.json) potwierdza zgodność
zapisanych CAD-ów, raportów, eksportu i prób. Raport jawnie nie udziela
zatwierdzenia mechanicznego, cieplnego ani całej ścieżki serwisowej.

## Odtwarzanie

Ustaw `ROBOT_CAT_CAD_REVISION=v31`; domyślna rewizja skryptów pozostaje v28.
Konfiguracja kontenera i wtyczki: [główny README](../README.md).
W bieżącym kontenerze (na Windows poprzedź `docker` przez `wsl -d Ubuntu --`):

```bash
docker exec -e ROBOT_CAT_CAD_REVISION=v31 robot-cat-cad-v25 bash -c 'source /opt/ros/jazzy/setup.bash && python3 tools/simulation/prepare_assets.py && python3 tools/simulation/verify_v31.py && pytest -q tools/simulation && pytest -q src'
docker exec -e ROBOT_CAT_CAD_REVISION=v31 -e GZ_SIM_SYSTEM_PLUGIN_PATH=/tmp/robot-cat-cad-plugin-build:/opt/ros/jazzy/lib robot-cat-cad-v25 bash -c 'source /opt/ros/jazzy/setup.bash && python3 tools/simulation/run_cad_gazebo.py --mode crawl --seconds 15 --step-seconds 1 --stance-x=-0.03 --stance-z=-0.005'
```

Nowy eksport: `cache31.py` w Pythonie FreeCAD, `export_dynamics.py` i
`export_dynamics.py --meshes` z rewizją v31; potem `cad_model.py`,
`auxiliary_budget.py`, testy, próby, `summarize_trials.py`,
`package_results.py`, `verify_v31.py`. Audyty CAD odtwarza się osobno
według README mechaniki. Pakowanie dotyczy tylko wybranej rewizji.
Żadnych komend nie wysłano do fizycznych napędów.

Testy: **581 ROS + 33 CAD/narzędzi = 614 zaliczonych**. Regresja na v30:
32 zaliczone + 1 pominięty (dotyczy wyłącznie nowego mocowania v31).
