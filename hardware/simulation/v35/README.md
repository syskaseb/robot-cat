# Gazebo v35 — mocowanie zasilania AUX

Źródło: [Kot v35](../../skorupa/v35/README.md), SHA256
`11e8c27e496032df6f556736e94699424723cef5fe0192b0ade2d152f810bdc5`.
320 komponentów CAD,13 ciał dynamicznych i12 osi nóg. **Głowa i ogon
nieruchome w fizyce**, ale z całą masą i bezwładnością w modelu.
Nie symulujemy termiki regulatorów, ugięcia PETG ani fizycznego orczyka.

Masa nominalna **2,503128 kg**, zakres założeń2,220387–2,967567 kg.
Wzrost względem v34 wynosi1,390 g. Druga Pololu ma nominalnie4,8 g,
dwa zaciski po2 g są założeniem, nie wynikiem ważenia. Cztery słupki
liczone z pełnej objętości CAD PETG przy1,27 g/cm³, śruby/nakrętki jako
stal. Dwa odrzucone krótkie dystanse nie są w masie ani w złożeniu.
Zachowano jawne założenie13 g na każde608ZZ i rezerwę wiązki.
Rzeczywistą masę trzeba sprawdzić po wydruku i złożeniu.

## Próby i wynik

| Próba | Masa | Najwyższy RMS stawu | Droga po rozruchu | Wynik |
|---|---:|---:|---:|---|
| Stanie8 s | 2,503 kg | 0,5647 Nm | <0,001 mm | ukończona |
| Crawl15 s | 2,503 kg | 0,6050 Nm | 84,1 mm/12 s | ukończona |
| Crawl15 s, cięższy | 2,968 kg | 0,6811 Nm | 89,9 mm/12 s | ukończona |

Trzy próby bez wykrytego upadku. W staniu1/801 próbka była nieaktualna
i została wyłączona ze statystyk momentu. Oba chody mają1501/1501
świeżych próbek. Wszystkie12 osi pozostało w użytej obwiedni
moment–prędkość. Pełna tabela: [RESULTS](RESULTS.md).
639 testów ROS/CAD/narzędzi zaliczono przed symulacją; regresja v34:632.
Trzy ostrzeżenia testów dotyczą deprecacji protobuf.

Warunki porównawcze: krok24 mm, unoszenie6 mm, cykl4 s, duty87,5%,
stopy−30/−5 mm względem CAD, tarcie0,4, limit komendy1 Nm i oszacowana
obwiednia ST3215 przy10,5 V. Bez sztucznego ogranicznika prędkości
jointów; podłoże/stopy uproszczone, pełne samokolizje wyłączone.
Odczytany moment jest komendą silnika, nie pomiarem z prawdziwego serwa.

RMS chodu praktycznie nie zmienił się względem v34 (0,6055/0,6806 Nm).
Nie jest to pomiar powtarzalności ani dowód większego zapasu silnika.
Najbardziej nasycony przegub osiągał limit przez4,6% próbek nominalnego
chodu i21,6% cięższego. Rzeczywiste zapotrzebowanie przy idealnym
śledzeniu może przekroczyć obciętą komendę1 Nm.

**ST3215 pozostaje kandydatem do powolnego chodu**, bez zatwierdzenia
biegu i pracy ciągłej. Stall lub umowne25% stall nie są producentowskim
momentem ciągłym. Potrzebne są pomiary prądu/temperatury i próby fizyczne.
Także Pololu „9 A” nie stanowi gwarancji wydajności w zamkniętym PETG.

## Spójność i odtwarzanie

`checkpoint-integrity.json` wiąże CAD, master,22 klatki natywne,
302 odziedziczone części,18 zmienionych/nowych kopii, audyty i świeżą
telemetrię. **Ścisły audyt BOP skorupy pozostaje niezaliczony**,
podobnie jak globalny test różnicy jej siatek. `prototype-scope.json`
dopuszcza jedynie rozwój AUX na podstawie osobnych kontroli lokalnych;
nie zmienia tych porażek w wynik pozytywny. Gazebo nie waliduje BRep.
29 tymczasowych więzów, dwa napędy głowy, orczyk, pozostała elektronika,
przewody, fizyczne tolerancje i termika nadal OPEN.

Ustaw `ROBOT_CAT_CAD_REVISION=v35`. Python FreeCAD:
`tools/freecad/skorupa/cache35.py`, `export_dynamics.py`, następnie
`export_dynamics.py --meshes`. W środowisku NumPy: `cad_model.py`
i `auxiliary_budget.py`. W Dockerze Jazzy/Harmonic:
`python3 -m pytest src tools/simulation -q`, potem
`python3 tools/simulation/run_v32_screening.py --suite baseline`.
Historyczna nazwa runnera jest zachowana; obsługuje v35.

Przed Gazebo: `source /opt/ros/jazzy/setup.bash`, bez `set -u`.
`GZ_SIM_SYSTEM_PLUGIN_PATH` musi wskazywać katalog
`librobot_cat_cad_actuator.so` i `/opt/ros/jazzy/lib`. Runner używa
własnego `GZ_PARTITION`, sprząta tylko własną grupę procesów i nie otwiera
magistrali prawdziwych serw. Środowisko: [README nadrzędne](../README.md).

`summarize_trials.py` odtwarza tabelę. `package_results.py` zachowuje
bezstratne `inputs.zip`, `meshes.zip`, `telemetry.zip` i pliki `.sha256`,
bez kasowania lokalnych danych. `prepare_assets.py --revision v35`
przywraca wejścia/siatki; `verify_v35.py` sprawdza powiązania i telemetrię.
Nazwy plików prób pochodzą z zegara UTC kontenera (17:00–17:01), czyli
19:00–19:01 czasu lokalnego22.09.2026.
