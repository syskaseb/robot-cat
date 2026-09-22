# Gazebo v30 — mocowanie IMU w aktualnym CAD

Źródło: [v30](../../skorupa/v30/README.md), 264 części CAD; 13 ciał fizycznych
i 12 osi nóg. Pełna masa i geometria nowego mocowania są uwzględnione.
Głowa i ogon są unieruchomione w tym eksperymencie; natywny FreeCAD testuje
osobno nogi i obrót ogona. Nie jest to model dynamiczny napędów pomocniczych.

Masa nominalna **2,419 kg**, zakres **2,142–2,878 kg**, o 3,2 g większa
nominalnie od v29. Założenia masowe,
rezerwa 120 g i model ST3215 pozostają jak w [v29](../v29/README.md).
Masa IMU 4 g to założenie bilansu; dokładny STEP nie jest pomiarem wagi.
PETG liczony z objętości × 1,27 g/cm³, śruby osobno jako stal.

## Trzy próby 22.09.2026

| Próba | Masa | Droga po ustaleniu | Największy RMS momentu | Największe nasycenie |
|---|---:|---:|---:|---:|
| Stanie | 2,419 kg | <0,001 mm | 0,534 Nm | 0% |
| Wolny chód | 2,419 kg | 78,8 mm / 12 s | 0,574 Nm | 3,7% |
| Wolny chód, górny scenariusz masy | 2,878 kg | 82,1 mm / 12 s | 0,650 Nm | 15,4% |

Wszystkie próby ukończono bez upadku, bez naruszenia modelowanej obwiedni
moment/prędkość. Warunki porównawcze jak v29: stopy −30/−5 mm względem
spoczynku CAD, krok 24 mm, uniesienie 6 mm, cykl 4 s, podparcie 87,5%, μ=0,4.
Nie zmieniono starego ROS w `src/` ani zapisanej pozycji FreeCAD.

Limit testowy 1 Nm obcina komendę, nie dowodzi maksymalnego zapotrzebowania
poniżej 1 Nm. Brak sztucznego hamującego ograniczenia prędkości osi.
To komendy regulatora, nie zmierzony moment sprzętu. Model przy 10,5 V
dotyczy przybliżenia 12-woltowego ST3215, nie wersji 7,4 V.

**Wniosek bez zmiany: ST3215 pozostaje kandydatem do powolnego chodu,
bez zatwierdzenia momentu ciągłego ani biegu.** Wariant cięższy nadal
przekracza roboczy, arbitralny próg 25% stall (0,644 Nm) na jednym przegubie.
Trzeba sprawdzić rzeczywiste masy, prądy i temperatury. Samokolizje w Gazebo
są wyłączone; stopy uproszczone; brak termiki, kabli, luzów i pełzania PETG.

Pełne wyniki: [RESULTS](RESULTS.md), [tabela liczbowa](trial-comparison.json),
[weryfikacja powiązania CAD i wyników](checkpoint-integrity.json).
`inputs.zip`, `meshes.zip`, `telemetry.zip` mają sumy SHA-256.
Natywny audyt 22 klatek i 48 par IMU nie jest pełnym testem kolizji chodu.
249 odziedziczonych części porównano osobno z v29; masa/bezwładność
ruchomego ogona zgadza się z zapisanym bilansem v29.

## Odtwarzanie

Ustaw **`ROBOT_CAT_CAD_REVISION=v30`**; domyślną rewizją skryptów nadal v28.
W istniejącym kontenerze Docker z zainstalowanymi zależnościami i wtyczką:

```bash
docker exec -e ROBOT_CAT_CAD_REVISION=v30 robot-cat-cad-v25 bash -c 'source /opt/ros/jazzy/setup.bash && python3 tools/simulation/prepare_assets.py && python3 tools/simulation/verify_v30.py && pytest -q tools/simulation && pytest -q src'
docker exec -e ROBOT_CAT_CAD_REVISION=v30 -e GZ_SIM_SYSTEM_PLUGIN_PATH=/tmp/robot-cat-cad-plugin-build:/opt/ros/jazzy/lib robot-cat-cad-v25 bash -c 'source /opt/ros/jazzy/setup.bash && python3 tools/simulation/run_cad_gazebo.py --mode crawl --seconds 15 --step-seconds 1 --stance-x=-0.03 --stance-z=-0.005'
```

Konfiguracja kontenera/wtyczki: [główny README symulacji](../README.md).
Na Windows poprzedź `docker` przez `wsl -d Ubuntu --`; nie instaluj pixi osx.
Harness używa osobnego `GZ_PARTITION` i kończy własny proces Gazebo.
Nie wysłano żadnych komend do rzeczywistych serw.

Eksport od zera: `cache30.py` w Pythonie FreeCAD, potem
`export_dynamics.py` i `export_dynamics.py --meshes` z rewizją v30;
`cad_model.py`, `auxiliary_budget.py`, próby, `summarize_trials.py`,
`package_results.py`, `verify_v30.py`. Pakowanie nie modyfikuje starych rewizji.
Weryfikator korzysta z zapisanych raportów audytów; ponowne wykonanie audytów
wymaga FreeCAD i odtworzenia cache opisanych w README CAD.

Testy: **581 ROS + 32 CAD/narzędzi = 613 zaliczonych**.
Sześć nowych regresji sprawdza rozróżnianie rzeczywistej zmiany BRep
od zaokrągleń zapisu; jedna kontroluje masę/przypisanie mocowania IMU.
