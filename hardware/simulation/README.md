# Aktualny CAD w Gazebo — v32, 22.09.2026

**Najnowsze wyniki: [v32 — ToF i granice chodu](v32/README.md).**
286 części, nominalnie2,420 kg (2,144–2,878);17 prób:16 ukończonych,
1 upadek w rozruchu przy limicie0,65 Nm i cięższym modelu.
Wolny chód RMS0,575/0,651 Nm; najszybszy crawl cięższego modelu
0,741 Nm i41,4% nasycenia. Nie zatwierdzono biegu ani termiki ST3215.
619 testów. `ROBOT_CAT_CAD_REVISION=v32`, `verify_v32.py`.
[Wyniki v32](v32/RESULTS.md), [spójność źródeł](v32/checkpoint-integrity.json).

## Poprzedni checkpoint v31 — zachowany porównawczo

**[v31 — mocowanie głównej przetwornicy](v31/README.md).**
280 części, masa nominalna 2,421 kg (2,144–2,879 kg), 13 ciał / 12 osi nóg.
Trzy próby bez upadku: RMS max 0,535 Nm stanie, 0,576 Nm wolny chód,
0,649 Nm cięższy chód i 15,4% nasycenia. Nadal brak zatwierdzenia biegu,
pracy ciągłej ST3215, termiki PETG oraz pełnych kolizji/serwisu.
614 testów zaliczonych. `ROBOT_CAT_CAD_REVISION=v31`, `verify_v31.py`.
[Wyniki v31](v31/RESULTS.md), [spójność źródeł](v31/checkpoint-integrity.json).

## Poprzedni checkpoint v30 — zachowany porównawczo

**[v30 — rzeczywiste mocowanie IMU](v30/README.md).**
264 części, masa nominalna 2,419 kg (+3,2 g względem v29).
Trzy próby bez upadku: stanie RMS max 0,534 Nm, wolny chód 0,574 Nm,
cięższy wariant 0,650 Nm / 15,4% nasycenia. Nadal 13 ciał i 12 osi nóg;
głowa/ogon zamrożone w fizyce. Nie zatwierdzono biegu ani termiki serw.
613 testów zaliczonych, zgodność źródeł sprawdza `verify_v30.py`.
Ustaw `ROBOT_CAT_CAD_REVISION=v30`; domyślne v28 pozostaje bez zmian.
[Tabela v30](v30/RESULTS.md), [spójność checkpointu](v30/checkpoint-integrity.json).

## Poprzedni checkpoint v29 — zachowany porównawczo

**[v29 — model z nowym ogonem](v29/README.md).**
252 części CAD, 2,416 kg nominalnie (2,139–2,875 kg), 13 ciał fizycznych
i 12 osi nóg. Nowy ogon jest w tym eksperymencie nieruchomy, ale jego
masa, bezwładność i siatka są w całości uwzględnione. Natywny FreeCAD
osobno testuje 13 ruchomych osi: nogi ±3° i ogon ±30°.

Trzy nowe próby: stanie RMS max 0,534 Nm; wolny chód 79,0 mm/12 s
i 0,573 Nm; cięższy wariant 0,650 Nm i nasycenie do 15,3%.
Nie zatwierdzono pracy ciągłej ani biegu. Fizyczny orczyk i podparcie
ogona oraz mechanizmy głowy nadal wymagają projektu.
Wyniki: [tabela v29](v29/RESULTS.md), [weryfikacja źródeł](v29/checkpoint-integrity.json).

W narzędziach ustaw **`ROBOT_CAT_CAD_REVISION=v29`**; domyślnie zachowano
v28 dla zgodności wcześniejszego eksperymentu. Szczegółowe komendy w README v29.

## Wcześniejsza dokumentacja v28 — zachowana porównawczo

Poniższe liczby, nazwy plików i cztery stare serwa pomocnicze dotyczą
wyłącznie **v28**, nie aktualnego modelu v32.

**Jest działający model fizyczny, ale nie ma jeszcze zatwierdzenia robota do
druku ani napędów do pracy ciągłej.** Nie zastępuje dotychczasowego modelu ROS
w `src/`; jest osobnym eksperymentem opartym na rzeczywistym złożeniu.

Źródło: [Kot v28](../skorupa/v28/README.md), 238 części, 13 ciał sztywnych,
12 zmierzonych osi nóg. Naprawiono odwrócone przypisanie pierwszych serw:
obudowa serwa biodrowego porusza się z łącznikiem, orczyki są przy ramie.
Modele wizualne to siatki z BRep, nie pudełka o wymyślonych wymiarach.
Głowa, ogon i elektronika są na razie sztywno połączone z korpusem.

## Wynik i decyzja o silnikach

- Masa nominalna **2,448 kg**, warianty **2,167–2,911 kg**. To bilans
  obliczeniowy, nie pomiar. PETG: pełna objętość materiału CAD × 1,27 g/cm³;
  części kupne mają osobne masy. Masa korpusu serwa 69 g jest założeniem,
  sprawdzonym w zakresie 60–89 g. Dochodzi jawna rezerwa 120 g na brakujące
  przewody i mocowania. Nie udajemy znajomości masy wydruku ze slicera.
- Stanie w pozycji CAD (porównanie v27): największy RMS sterowanego momentu **0,720 Nm**.
  Kandydat ze stopami 30 mm do tyłu i 5 mm niżej względem korpusu:
  **0,539 Nm**. Korpus stoi około 5 mm wyżej. Nie zmieniono zapisanej pozycji
  spoczynkowej FreeCAD ani domyślnych parametrów starego kontrolera ROS.
- Wolny chód v28: **78,3 mm w 12 s**, około **6,5 mm/s**, masa nominalna,
  μ=0,4. Krok 24 mm, uniesienie 6 mm, cykl 4 s, faza podporu 87,5%.
  RMS najbardziej obciążonego przegubu **0,580 Nm**; sterownik chwilowo
  dobijał do limitu **1 Nm**. To nie dowód, że pełne zapotrzebowanie wynosi
  najwyżej 1 Nm — ogranicznik ucina komendę i pojawia się błąd pozycji.
- Przy 2,911 kg i tym samym ustawieniu RMS rośnie do **0,654 Nm**, a
  najbardziej nasycony przegub osiąga limit przez około **16% próbek**.
  W próbie v27 przy limicie 0,65 Nm nominalny model nadal przeszedł próbę, lecz nasycenie
  sięga **38%**. Nie przedstawiamy tego jako prawidłowo dobranej regulacji.
- Niższe tarcie μ=0,2 także sprawdzono w v27, ale nie jest to zmierzony współczynnik
  PETG na podłodze użytkownika. Sfera kontaktowa nie odwzorowuje pełnej stopy.

Wniosek: **ST3215 12 V pozostaje kandydatem do powolnego chodu; nie ma podstaw
do zagwarantowania jego pracy ciągłej ani biegu.** W najcięższym wariancie
rezerwa według roboczego kryterium jest mała. Przed zmianą silników warto
zważyć wydruki i zespół oraz sprawdzić moment, prąd i temperaturę przy
ograniczonym obciążeniu, z podpartym robotem i możliwością odłączenia zasilania.

[Aktualna tabela](v28/RESULTS.md) zawiera sześć prób v28. Do wniosków używamy
ostatnich trzech, bez sztucznego ogranicznika prędkości przegubu; pozostałe
zachowano porównawczo i oznaczono w tabeli.
[Osiem wcześniejszych porównań v27](v27/RESULTS.md) zachowuje również mniej
korzystne wyniki. [JSON porównawczy v28](v28/trial-comparison.json)
ma także błędy pozycji i kompletne odnośniki do konfiguracji.

## Model napędu i ograniczenia

[Waveshare](https://www.waveshare.com/wiki/ST3215_Servo) podaje dla wersji
12 V moment **zatrzymania** 30 kgf·cm, prędkość **bez obciążenia**
0,222 s/60° i prąd zatrzymania 2,7 A. Wariant 7,4 V to inna wersja serwa,
nie drugi punkt pomiarowy tego samego uzwojenia. Nie znaleziono potwierdzonej
charakterystyki momentu ciągłego/termicznej.

Model używa ostrożnego liniowego oszacowania dla 10,5 V:
2,574 Nm przy zerowej prędkości, 4,127 rad/s bez obciążenia. Dostępny moment
maleje z prędkością; dodatkowy limit testowy to 1 Nm. Wartość 25% momentu
zatrzymania, czyli 0,644 Nm, jest wyłącznie roboczym progiem przesiewowym,
**nie parametrem gwarantowanym przez producenta**.

Własna wtyczka Gazebo wykonuje PD przy 1 kHz i zadaje `JointForceCmd`.
Nie ustawia idealnie pozycji/prędkości przegubu. Telemetria zawiera rzeczywiście
zadaną komendę momentu, a nie zmierzony moment reakcji. W Gazebo 8.11 pole
`JointState.force` w pierwszych próbach pozostawało zerowe; tamte wyniki
odrzucono. Prędkość i moment w kontroli ogranicznika pochodzą z tej samej
klatki `PreUpdate`. Dla obecnych prób nie ma naruszeń modelowanej obwiedni.
Wzmocnienia regulatora i jego pasmo nie są identyfikacją elektroniki ST3215.

Usunięto sztywny `joint/axis/limit/velocity`: prędkość bez obciążenia nie jest
mechanicznym ogranicznikiem, który może bezkosztowo wyhamować uderzenie stopy.
Starsze osiem prób v27 i pierwsze trzy v28 miały ten limit i **nie stanowią
ostatecznego potwierdzenia obciążeń**. W nowych próbach chwilowe prędkości
uderzeniowe mogą przekroczyć prędkość bez obciążenia; nie są deklaracją
osiągalnej prędkości napędzanego chodu. Brakuje rzeczywistej podatności stopy,
przekładni i zmierzonej regulacji serwa. 6,5 mm/s to ustawienie ostrożnej
próby, nie wyznaczona maksymalna prędkość robota.

Fizyka obejmuje kontakt czterech uproszczonych stóp z płaską podłogą oraz
awaryjną bryłę korpusu. **Samokolizje w Gazebo są wyłączone.** Osobny dokładny
audyt BRep bada wybrane pozycje, nie ciągły ruch. Nie wolno na podstawie udanego
przejścia w Gazebo ogłaszać braku kolizji całego robota. Brakuje m.in.
uginania PETG, luzów przekładni, przewodów, temperatur, spadków napięcia,
rzeczywistych stóp oraz ruchomych mechanizmów głowy i ogona.

Dwanaście zatrzymanych serw może według katalogu pobierać łącznie około
32,4 A, jeszcze bez reszty elektroniki. To scenariusz awaryjny do doboru
przewodów, rozdziału zasilania i zabezpieczeń, nie przewidywany prąd chodu.
Nie zatwierdzono prowadzenia zasilania całego robota przez pojedynczy cienki
przewód ani złącze adaptera magistrali.

## Głowa i ogon

[Osobny bilans](v28/auxiliary-budget.json) szacuje głowę na **184 g** bez
nowych wsporników. Dla próbnej osi w środku starej bryły zastępczej serwa
i pochylenia ±20° wychodzi do **0,0725 Nm** (grawitacja + przyspieszenie
2 rad/s²), bez oporu przewodów. To blisko roboczego progu 0,076 Nm dla MG92B
przy 5 V. Oś trzeba umieścić bliżej środka masy i podeprzeć łożyskowo.
**Ten punkt nie jest zmierzonym wałkiem MG92B** i nie zatwierdza uchwytu.

Sama część segmentowa ogona ma około **17,6 g**; pionowy obrót ma niewielką
bezwładność, ale nie rozwiązuje mocowania ani połączeń segmentów PETG.
Pozostaje wymóg **2 napędów głowy + 1 ogona**, mimo czterech starych brył
pomocniczych widocznych w aktualnym złożeniu. [TowerPro](https://towerpro.com.tw/product/mg92b/)
podaje 3,1 kgf·cm zatrzymania przy 5 V; to także nie jest moment ciągły.

## Odtworzenie

Windows: WSL + Docker, zgodnie z [run/docker](../../run/docker/README.md).
Bez `pixi install` na Windows. Z katalogu tego worktree w WSL:

```bash
docker run -d --name robot-cat-cad -v "$PWD:/work" -w /work robot-cat:jazzy sleep infinity
docker exec robot-cat-cad bash -c 'source /opt/ros/jazzy/setup.bash && python3 tools/simulation/prepare_assets.py --history && cmake -S tools/simulation/plugin -B /tmp/cad-plugin && cmake --build /tmp/cad-plugin -j2'
docker exec -e GZ_SIM_SYSTEM_PLUGIN_PATH=/tmp/cad-plugin:/opt/ros/jazzy/lib robot-cat-cad bash -c 'source /opt/ros/jazzy/setup.bash && python3 tools/simulation/run_cad_gazebo.py --mode crawl --seconds 15 --step-seconds 1 --stance-x=-0.03 --stance-z=-0.005'
docker exec robot-cat-cad bash -c 'source /opt/ros/jazzy/setup.bash && pytest -q && pytest -q tools/simulation'
```

Nie twórz drugi raz kontenera o tej samej nazwie; użyj istniejącego.
W sesji autora kontener nazywa się `robot-cat-cad-v25` (nazwa historyczna),
lecz testuje v28. Próby są izolowane przez `GZ_PARTITION`; skrypt kończy
wyłącznie własny proces Gazebo. Nie podłącza portu USB ani sprzętowych serw.

`python tools/simulation/cad_model.py` odtwarza masy i SDF bez FreeCAD.
`stance_search.py`, `auxiliary_budget.py` i `summarize_trials.py` odtwarzają
odpowiednie raporty. Domyślna rewizja: v28. Zmienna
`ROBOT_CAT_CAD_REVISION=v25` służy tylko odtworzeniu odrzuconego eksperymentu.

Do ponownego eksportu siatek v28 potrzebny jest Python FreeCAD, cache BRep
z `Cache28.FCMacro` (otwarty zapisany v28 w spoczynku) oraz
`tools/freecad/skorupa/export_dynamics.py --meshes`.
Eksporter sprawdza hash źródła. Starsze v27 korzysta z cache v26 i osobnego
potwierdzenia niezmienionej geometrii. `check_cover28.py` sprawdza podmienioną
osłonę w sześciu odziedziczonych pozycjach v27; ich niezmienione pary
dziedziczą wcześniejszy audyt, a nie nowy pełny test ciągłego chodu.

`meshes.zip` zawiera 13 siatek, `telemetry.zip` pełne próbki/SDF/logi,
a `inputs.zip` duże tablice geometrii i bezwładności. Na świeżym klonie
uruchom `python tools/simulation/prepare_assets.py` przed testami CAD.
`package_results.py` tworzy archiwa i SHA-256, nie usuwa lokalnych danych.
Stare próby zachowano w [v25/superseded.zip](v25/README.md), z opisem błędów.
Nazwy prób są według zegara kontenera UTC; lokalnie to 22.09.2026.

W tej rewizji przeszło **581 testów dotychczasowego ROS** i **22 nowe
testów obliczeń CAD**. Walidacja SDF: `gz sdf -k`, poprawna. To testy
oprogramowania, nie certyfikat mechaniczny.
