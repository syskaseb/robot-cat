# Modułowy pilot AUX

To etap migracji, **nie nowa konstrukcja całego kota i nie wydanie do druku**.
Źródłem porównania pozostaje [v35](../skorupa/v35/README.md).

## Dokumenty

- `parameters/RobotParameters.FCStd` — wspólny interfejs AUX, utworzony przez MCP;
- `modules/chassis/Chassis.FCStd` — płyta z otworami AUX;
- `modules/tail/TailMount.FCStd` — mostek z otworami AUX, nie cały ogon;
- `modules/shell/Shell.FCStd` — odziedziczona skorupa z przejściami AUX;
- `modules/electronics/PowerMounts.FCStd` — cztery podpory z historią operacji;
- `modules/electronics/AuxPurchased.FCStd` — przypięte referencje płytki,
  nominalnych zacisków i łączników; nie nowy projekt elektroniki;
- `assembly/RobotCat.FCStd` — złożenie rozwojowe; 18 elementów AUX zastąpiono
  zewnętrznymi App::Link. Pozostałe 302 pozostają snapshotami v35.

Nie utożsamiać tych częściowych dokumentów z ukończonymi masterami całej ramy,
głowy czy ogona. Bazy płyty/mostka/skorupy pozostają odziedziczonymi bryłami;
przenoszona jest ich istniejąca historia otworów, nie wymyślona historia WAVEGO.

Wspólna średnica `AuxHoleDiameter` steruje otworami płyty, mostka i podpór.
Szkice kół otrzymują wymiary zamiast `Block`. Rozstaw płytki jest wymiarem
referencyjnym, nie obietnicą parametrycznej zmiany całej płytki handlowej.
Zmiana otworów nie oznacza zatwierdzenia nowego pasowania ani doboru śrub.

Otwieraj `assembly/RobotCat.FCStd`, zachowując całą strukturę katalogów.
`MountParameters` w złożeniu jest jawnym odnośnikiem do parametrów, nie fizyczną
częścią robota. Jest potrzebny przy częściowym wczytywaniu zewnętrznych Bodies.
Każdy moduł ma też lokalny `MountInterface`. Same wyrażenia lub zwykła właściwość
XLink nie wystarczyły w teście automatycznego wczytania FreeCAD 1.1.3.
Bryły mają `DisplayModeBody=Tip`, aby pod odnośnikami nie znikała skorupa.

## Narzędzia i dowody

`tools/cad/pilot.py` wykonuje kontrolowane kopiowanie historii, podmianę na
odnośniki i testy; interaktywne zmiany szkiców/parametrów wykonuje FreeCAD MCP.
`prepare` odmawia nadpisania istniejących modułów; nie uruchamiać ponownie na
gotowym drzewie. To narzędzie migracji, nie alternatywne źródło geometrii.

W Pythonie dostarczonym z FreeCAD, z korzenia repo:

```text
python tools/cad/pilot.py parameter-test
python tools/cad/pilot.py compare
python tools/cad/pilot.py relocation-test
python tools/cad/pilot.py native-test
```

`integrate()` wymaga GUI FreeCAD; `native-test` korzysta z natywnego Assembly
także w Pythonie dostarczonym z FreeCAD. Żaden test nie zapisuje plików CAD;
nie uruchamiać walidatorów v35 na nowych plikach, bo zapisują checkpoint bazowy.
W konsoli Python FreeCAD można dodać `tools/cad` do `sys.path`, zaimportować
`pilot` i wywołać `pilot.validate_native()` dla złożenia rozwojowego.

Wyniki trafiają do `validation/`. Sukces porównania oznacza zachowanie bazowej
geometrii, **łącznie z jej znanymi wadami**. Nie naprawia BOP skorupy ani 29 TEMP.
Fizyka Gazebo nie jest automatycznie ponownie zatwierdzona przez test jointów.

[Toolchain](toolchain.json) przypina wersje i dodatek Fasteners. Instalacja
dodatku jest lokalna, kod dodatku nie jest kopiowany do repo. Pilot nie zależy
od obiektów Fasteners; próbna śruba służy wyłącznie sprawdzeniu działania dodatku.

## Dowody pilotażu

- [Geometria](validation/geometry.json): 320 części; porównanie BRep bez naprawy
  topologii, bezpośrednio z bazowego FCStd (bez nieśledzonego cache);
  maksymalna różnica liczb około 9e-15.
- [Kinematyka](validation/native-motion.json): 22 klatki, 306 Fixed + 13 Revolute,
  nogi ±3°, ogon ±30°, powrót do spoczynku; nadal 29 TEMP.
- [Parametry](validation/parameter-update.json): otwór 2,4 → 2,6 → 2,4 mm,
  aktualizacja sześciu brył i odtworzenie ich objętości.
- [Przeniesienie](validation/relocation.json): świeży proces, 18 odnośników,
  siedem dokumentów z nowego katalogu, solver oraz zmiana parametru poprzez
  odnośnik do złożenia. Nie korzystano z oryginalnych ścieżek plików CAD.
- [Fasteners](validation/fasteners-smoke.json) i [widok kota](validation/whole-cat.png).
- [Testy ROS/narzędzi](validation/tests.json): 646 zaliczonych dla v35,
  bez pominiętych; trzy istniejące ostrzeżenia bibliotek.

Uruchom pełne testy z `ROBOT_CAT_CAD_REVISION=v35`; domyślne v28 pomija testy
nowszej mechaniki. Nowych prób dynamicznych Gazebo nie wykonywano: geometria
i położenia są zachowane, a to zadanie dotyczy organizacji CAD i narzędzi.

Manifest [modular-pilot.json](../releases/modular-pilot.json) przypina konkretne
pliki. Kontrola integralności ma przejść, `--require-print-ready` ma odmówić.
