# Gazebo v32 — nos ToF i granice chodu

Źródło: [Kot v32](../../skorupa/v32/README.md), **286 części CAD**, 13 ciał
fizycznych / 12 osi nóg. Głowa i ogon zamrożone, ich masa i bezwładność
uwzględnione. Nie zmieniano historycznego kontrolera ROS w `src/`.
To eksperyment obciążenia napędów, **nie wydanie mechaniki do druku**.

Masa nominalna **2,420484 kg**, scenariusze **2,143753–2,878113 kg**.
To szacunek: objętość PETG × 1,27 g/cm³, osobne masy części kupnych,
rezerwa 120 g na niedokończone przewody/mocowania. Nie masa ze slicera.
Pololu 3417 ma [0,5 g bez pinów według producenta](https://www.pololu.com/product/3417/specs).
Dwa dystanse PETG i cztery części stalowe dodano do bilansu głowy;
ujemna różnica masy netto −0,42 g względem v31 obejmuje także usunięty
materiał nosa, pyszczka i przepustu głowy. Pozostałe założenia jak w v31.

## Wynik: silniki nadal warunkowym kandydatem, nie zatwierdzone

Zachowano **17 prób: 16 ukończonych i 1 upadek przy rozruchu**.
[Wszystkie wyniki](RESULTS.md), [liczby i błędy pozycji](trial-comparison.json),
[3 próby bazowe](baseline-suite.json), [14 prób rozszerzonych](sweep-suite.json).
Droga jest mierzona po t=3 s, moment RMS po t=2 s; każda próba chodu
planowana na 15 s. RMS dotyczy komendy napędu, nie pomiaru sprzętowego.

| Warunki | Masa | Droga przez 12 s | Maks. RMS | Nasycenie limitu |
|---|---:|---:|---:|---:|
| Stanie 8 s | 2,420 kg | — | 0,535 Nm | 0% |
| Wolny crawl, cykl 4 s, limit 1 Nm | 2,420 kg | 78,5 mm | 0,575 Nm | 3,8% |
| Ten sam crawl, cięższy model | 2,878 kg | 82,7 mm | 0,651 Nm | 15,4% |
| Crawl, cykl 0,6 s, limit 1 Nm | 2,420 kg | 911,4 mm | 0,685 Nm | 26,9% |
| Cykl 0,6 s, cięższy model | 2,878 kg | 597,3 mm | 0,741 Nm | 41,4% |
| Cykl 4 s, limit 0,65 Nm | 2,420 kg | 83,0 mm | 0,503 Nm | 36,0% |
| Cykl 4 s, limit 0,65 Nm | 2,878 kg | **upadek przy t=1,002 s** | brak statystyki | brak statystyki |

W ostatniej próbie wysokość korpusu spadła do 91,96 mm, poniżej progu
przerwania 100 mm, **jeszcze przed rozpoczęciem chodu**. To problem utrzymania
rozruchu przy tym limicie, nie zmierzony moment ciągły ani dowód, że serwo
ST3215 fizycznie ma tylko 0,65 Nm. Telemetria ma 101 świeżych próbek;
brak RMS po t=2 s jest oznaczony jako `null`/„—”, nie zero i nie pominięcie.
Poprawiono generator raportów i dodano testy regresyjne tego przypadku.

Szybsze próby to nadal **crawl z podparciem 87,5%**, nie kłus ani bieg.
Cykl 0,6 s daje duże nasycenie i błąd przegubu do 8,77°. Nominalna
prędkość kinematyczna 45,7 mm/s różni się od wyniku 76,0 mm/s — możliwy
wpływ poślizgu/uderzeń oraz modelu kontaktu, nie obietnica takiej prędkości
sprzętu. Chwilowe prędkości przegubów do 14 rad/s są również uderzeniowe;
nie ma sztucznego ogranicznika, który bezkosztowo wyhamowuje zderzenie.

Zmieniono też tarcie μ=0,25/0,6 (cykl 2 s). Cięższy model przy μ=0,6
przeszedł tylko 52,5 mm, z RMS 0,716 Nm i nasyceniem 29,7%. Tarcie nie
jest pomiarem PETG na podłodze użytkownika. Nie dobierać parametrów
wyłącznie według największej drogi bez oceny poślizgu, błędu i grzania.

**ST3215 12 V pozostaje kandydatem do spokojnego chodu. Nie zatwierdzono
pracy ciągłej ani biegu.** Limit 1 Nm ucina sterowanie, nie ogranicza
rzeczywistego zapotrzebowania mechaniki. Roboczy próg 25% stall przy 10,5 V
to 0,644 Nm, nie rating termiczny producenta; wariant cięższy go przekracza.
Zanim rozważać wymianę napędów, trzeba zważyć wydruki i podzespoły oraz
sprawdzić prąd/temperaturę na podpartym robocie z odłącznikiem zasilania.
Nie wysłano żadnych poleceń do fizycznych serw.

## Zakres i wiarygodność

Parametry bazowe: stopy −30/−5 mm względem CAD, krok24 mm, uniesienie6 mm,
cykl4 s, μ0,4, PD1 kHz, limit1 Nm, szacowana obwiednia moment/prędkość
dla ST3215 12 V przy 10,5 V. Sweep: cykle3/2/1/0,6 s × dwie masy,
tarcie0,25/0,6 × dwie masy oraz limit0,65 Nm × dwie masy.
Bez samokolizji w Gazebo; uproszczone stopy i podłoga. Brak termiki,
pełzania PETG, luzów przekładni, modelu pełnej wiązki i regulacji serw
zidentyfikowanej na sprzęcie. Jedna krótka próba każdej konfiguracji,
nie statystyka powtarzalności ani stabilności długookresowej.

Wszystkie **świeże surowe próbki**, także przed t=2 s i podczas upadku,
sprawdzono względem tej samej modelowanej obwiedni — zero naruszeń.
Dwie pojedyncze nieświeże próbki (cykl3 s nominalny i0,6 s nominalny)
są zapisane i wykluczone ze statystyk, nie interpolowane.
Natywny FreeCAD:22 klatki, nogi±3° / ogon±30°, bez ruchu głowy.
Lokalny audyt ToF:45 par, zero nowych przecięć, otwarta rezerwa optyczna
i przewodów, kontakty zacisku. **12 dawnych przecięć głowy pozostaje OPEN.**
32 tymczasowe blokady złożenia nie są fizycznymi mocowaniami.

Bilans głowy:183,6 g; stara zastępcza oś pochylenia daje0,0723 Nm przy
±20° i2 rad/s². To nie prawdziwa oś zamontowanego MG92B ani rozwiązane
łożyskowanie. Ruchomy ogon55,6 g, nadal brak zatwierdzonego orczyka/podparcia.

## Odtwarzanie i archiwa

Ustaw **`ROBOT_CAT_CAD_REVISION=v32`**; domyślnie skrypty nadal mają v28.
[Konfiguracja Docker/WSL i wtyczki](../README.md). Na Windows poprzedź
poniższe `docker` przez `wsl -d Ubuntu --`; użyj istniejącego kontenera:

```bash
docker exec -e ROBOT_CAT_CAD_REVISION=v32 robot-cat-cad-v25 bash -c 'source /opt/ros/jazzy/setup.bash && python3 tools/simulation/prepare_assets.py && python3 tools/simulation/verify_v32.py && pytest -q tools/simulation && pytest -q src'
docker exec -e ROBOT_CAT_CAD_REVISION=v32 -e GZ_SIM_SYSTEM_PLUGIN_PATH=/tmp/robot-cat-cad-plugin-build:/opt/ros/jazzy/lib robot-cat-cad-v25 bash -c 'source /opt/ros/jazzy/setup.bash && python3 tools/simulation/run_v32_screening.py --suite all --max-wall-seconds 1200'
```

Eksport: `cache32.py` w Pythonie FreeCAD, następnie `export_dynamics.py`
oraz `export_dynamics.py --meshes` z rewizją v32. Potem `cad_model.py`,
`auxiliary_budget.py`, testy, próby, `summarize_trials.py`,
`package_results.py` i `verify_v32.py`. Audyt CAD osobno według README v32.
Nie przeliczać historycznych wersji tylko dla zmiany widoku.

`inputs.zip`, `meshes.zip` i `telemetry.zip` mają SHA-256; ostatnie zachowuje
również nieudaną próbę, pełne próbki, SDF i logi. Katalog `trials/` jest
ignorowany w Git: aby działały odnośniki do prób na świeżym klonie,
rozpakuj `telemetry.zip` **w tym katalogu v32** (archiwum ma prefiks `trials/`).
[checkpoint-integrity.json](checkpoint-integrity.json) potwierdza zgodność
CAD, raportów, mas, archiwów i wszystkich17 prób. Nie daje zgody do druku.

Testy: **581 ROS + 38 CAD/narzędzi = 619 zaliczonych**.
Regresja v31:37 zaliczonych +1 pominięty (tylko nowy montaż ToF);
historyczne CAD-y i archiwa v31 pozostały niezmienione.
