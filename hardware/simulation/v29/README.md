# Gazebo v29 — rzeczywisty CAD z nowym ogonem

Źródło: [v29](../../skorupa/v29/README.md), 252 rzeczywiste bryły CAD.
13 dynamicznych ciał i 12 osi nóg; głowa oraz nowy ogon są w tym eksperymencie
unieruchomione względem korpusu. Masa i bezwładność ogona **nie są pominięte**:
eksport przenosi etap `Motion_Tail_Yaw` do korpusu i zapisuje jego pochodzenie.
Natywny ruch ogona w FreeCAD testowany jest osobno, nie jako napęd w Gazebo.

## Wyniki 22.09.2026

Masa nominalna **2,416 kg**, dolny i górny scenariusz **2,139–2,875 kg**.
PETG liczony jest z pełnej objętości brył × 1,27 g/cm³, nie z procentu
wypełnienia. Części kupne mają osobne założenia masy, w tym cały MG92B
13,8 g (podział obudowa/wyjście 12,8/1 g jest niezmierzonym przybliżeniem).
Pozostaje 120 g jawnej rezerwy na brakujące wiązki i mocowania.

| Próba | Masa | Ruch po ustaleniu | Największy RMS momentu | Nasycenie limitu, najgorszy przegub |
|---|---:|---:|---:|---:|
| Stanie | 2,416 kg | poniżej 0,001 mm | 0,534 Nm | 0% |
| Wolny chód | 2,416 kg | 79,0 mm / 12 s | 0,573 Nm | 3,8% |
| Wolny chód, cięższy wariant | 2,875 kg | 82,2 mm / 12 s | 0,650 Nm | 15,3% |

Trzy próby zakończyły się bez upadku i bez naruszenia modelowanej
charakterystyki moment/prędkość. Nie jest to certyfikat napędów.
Parametry: stopy 30 mm w tył i 5 mm w dół względem CAD, krok 24 mm,
uniesienie 6 mm, cykl 4 s, podparcie 87,5%, μ=0,4. Około 6,6 mm/s
w próbie nominalnej to ustawienie tej próby, **nie maksymalna prędkość robota**.
Nie zmieniono zapisanej pozycji FreeCAD ani kontrolera starego ROS w `src/`.

Sterowanie PD 1 kHz zadaje moment, z limitem testowym 1 Nm i liniowym
oszacowaniem obwiedni ST3215 przy 10,5 V. Chwilowe dojście do 1 Nm oznacza
obcięcie komendy, a nie dowód, że zapotrzebowanie nigdy nie przekracza 1 Nm.
Brak sztucznego hamującego limitu prędkości przegubu. Momenty są komendami
sterownika, nie pomiarem fizycznego serwa. Krótkie szczyty prędkości od
uderzeń stopy również nie dowodzą osiągalnej prędkości napędzanego ruchu.

**ST3215 pozostaje kandydatem do ostrożnego, wolnego chodu.** W cięższym
scenariuszu największy RMS nieznacznie przekracza roboczy próg 0,644 Nm.
Ten próg to arbitralne 25% momentu zatrzymania, nie moment ciągły producenta.
Nie zatwierdzono biegu, czasu pracy, temperatury, przewodów ani zabezpieczeń.
Źródło charakterystyki katalogowej: [Waveshare ST3215](https://www.waveshare.com/wiki/ST3215_Servo).

## Co test potwierdza, a czego nie

[RESULTS.md](RESULTS.md) i [trial-comparison.json](trial-comparison.json)
zawierają dokładne wyniki; pełna telemetria i światy są w `telemetry.zip`.
[checkpoint-integrity.json](checkpoint-integrity.json) sprawdza zgodność
hashy CAD, raportów, mas, siatek, testów natywnych i prób Gazebo.

Samokolizje Gazebo są wyłączone, kontakt podłogi wykorzystuje uproszczone
stopy. Dokładny audyt BRep v29 obejmuje nowe części i próbki obrotu ogona,
nie cały ciągły chód. Nie ma modelu pełzania PETG, kabli, luzów przekładni,
spadku napięcia ani termiki. Głowa, elektronika i połączenie orczyka ogona
wciąż wymagają projektu. Akumulator ma założoną masę kandydata 174 g,
ale jego stara obwiednia nie odpowiada nowym wymiarom — nadal otwarty temat.

Osobny [bilans ogona](../../skorupa/v29/tail-budget.json) daje 55,6 g,
0,000433 kg·m² bezwładności wokół osi, około 0,0122 Nm dla założonego
przechyłu robota 15° i przyspieszenia 2 rad/s² oraz 0,0437 Nm zginania
wałka w poziomie. Nie uwzględnia uderzeń i oporu przewodów; **brak podparcia
oraz zweryfikowanego orczyka wyklucza zatwierdzenie mechanizmu**.

## Odtworzenie na Windows / Linux

Domyślna rewizja narzędzi pozostaje v28, aby nie zmieniać dotychczasowego
eksperymentu bez jawnego wyboru. Dla v29 ustaw `ROBOT_CAT_CAD_REVISION=v29`.
W istniejącym kontenerze opisanym w [run/docker](../../../run/docker/README.md):

```bash
docker exec -e ROBOT_CAT_CAD_REVISION=v29 robot-cat-cad-v25 bash -c 'source /opt/ros/jazzy/setup.bash && python3 tools/simulation/prepare_assets.py && python3 tools/simulation/verify_v29.py && pytest -q tools/simulation'
docker exec -e ROBOT_CAT_CAD_REVISION=v29 -e GZ_SIM_SYSTEM_PLUGIN_PATH=/tmp/robot-cat-cad-plugin-build:/opt/ros/jazzy/lib robot-cat-cad-v25 bash -c 'source /opt/ros/jazzy/setup.bash && python3 tools/simulation/run_cad_gazebo.py --mode crawl --seconds 15 --step-seconds 1 --stance-x=-0.03 --stance-z=-0.005'
```

Kontener musi mieć zbudowaną wtyczkę z `tools/simulation/plugin`, według
głównego [README symulacji](../README.md). Nazwa i katalog wtyczki powyżej
odnoszą się do bieżącej lokalnej sesji; nie twórz drugiego tego samego kontenera.
Próby są izolowane `GZ_PARTITION`; skrypt kończy tylko własny proces Gazebo.
Żadnych komend nie wysłano do fizycznego robota.

Eksport od zera: `cache29.py` w Pythonie FreeCAD, następnie
`export_dynamics.py` i `export_dynamics.py --meshes` z powyższą zmienną
rewizji. Dalej `cad_model.py`, `auxiliary_budget.py`, próby Gazebo,
`summarize_trials.py`, `package_results.py` i `verify_v29.py`.
581 testów ROS pozostało zgodnych. Pakiet CAD v29 obejmuje 25 testów:
dotychczasowe 22, masę MG92B/śrub i zamrożenie ogona oraz dwie regresje
pakowania wyników bez zmieniania historycznych archiwów.
