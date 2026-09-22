# Modułowy CAD — AUX i podparcie ogona

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
- `modules/tail/TailSupport.FCStd` — siedem części PETG z historią operacji;
- `modules/tail/TailPurchased.FCStd` — nominalne łożyska i łączniki podparcia;
- `assembly/RobotCat.FCStd` — złożenie rozwojowe; **45 zewnętrznych App::Link**:
  18 elementów AUX i 27 podparcia ogona. Pozostałe 275 to snapshoty v35.

Zestaw liczy dziewięć dokumentów. Zakres podparcia, interfejsy i ograniczenia
opisuje [moduł ogona](modules/tail/README.md). Pierwszy pilot AUX jest zachowany
w historii Git (`92e7312`); pliki historycznych checkpointów v34/v35 są niezmienione.

Nie utożsamiać tych częściowych dokumentów z ukończonymi masterami całej ramy,
głowy czy ogona. Bazy płyty/mostka/skorupy pozostają odziedziczonymi bryłami;
przenoszona jest ich istniejąca historia otworów, nie wymyślona historia WAVEGO.

Wspólna średnica `AuxHoleDiameter` steruje otworami płyty, mostka i podpór.
Szkice kół otrzymują wymiary zamiast `Block`. Rozstaw płytki jest wymiarem
referencyjnym, nie obietnicą parametrycznej zmiany całej płytki handlowej.
Zmiana otworów nie oznacza zatwierdzenia nowego pasowania ani doboru śrub.

Otwieraj `assembly/RobotCat.FCStd`, zachowując całą strukturę katalogów.
`MountParameters` i `TailParameters` są jawnymi odnośnikami do parametrów, nie
fizycznymi częściami robota. Są potrzebne przy częściowym wczytywaniu zewnętrznych Bodies.
Moduły korzystające z parametrów mają też lokalny `MountInterface` lub
`BearingInterface`. Same wyrażenia lub zwykła właściwość
XLink nie wystarczyły w teście automatycznego wczytania FreeCAD 1.1.3.
Bryły mają `DisplayModeBody=Tip`, aby pod odnośnikami nie znikała skorupa.

## Narzędzia i dowody

`tools/cad/pilot.py` oraz `tail_module.py` wykonują kontrolowane kopiowanie historii, podmianę na
odnośniki i testy; interaktywne zmiany szkiców/parametrów wykonuje FreeCAD MCP.
`prepare` odmawia nadpisania istniejących modułów; nie uruchamiać ponownie na
gotowym drzewie. To narzędzie migracji, nie alternatywne źródło geometrii.

W Pythonie dostarczonym z FreeCAD, z korzenia repo:

```text
python tools/cad/pilot.py parameter-test
python tools/cad/pilot.py compare
python tools/cad/pilot.py relocation-test
python tools/cad/pilot.py native-test
python tools/cad/tail_module.py check-owners
python tools/cad/tail_module.py parameter-test
```

Historyczne `pilot.prepare/integrate` dotyczą tylko pierwszego etapu AUX;
`tail_module.prepare/integrate` dotyczą jednokrotnej migracji podparcia.
Nie uruchamiać ich ponownie jako generatora całego kota.
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

## Dowody bieżącego etapu

- [Geometria](validation/geometry.json): wszystkie 320 części, bezpośrednio
  z bazowego FCStd. Porównanie zapisu BRep; dla przebudowanych historii podpory
  dopuszczona jest ścisła kontrola BOP i pusta różnica brył w obu kierunkach,
  bez przesuwania i naprawiania. Nie stosuje się jej do wadliwych skorup.
- [Kinematyka](validation/native-motion.json): 22 klatki, 306 Fixed + 13 Revolute,
  nogi ±3°, ogon ±30°, powrót do spoczynku; nadal 29 TEMP. Kontrola obejmuje
  położenie geometrii odnośników, w tym pięciu obracających się części podpory.
- [Parametry](validation/parameter-update.json): otwór 2,4 → 2,6 → 2,4 mm,
  aktualizacja sześciu brył i odtworzenie ich objętości.
- [Parametr ogona](validation/tail-parameter-update.json): 22,2 → 22,4 → 22,2 mm;
  oba gniazda w górnym bloku aktualizują się, dolny wspornik serwa nie zmienia się.
- [Historia podpory](validation/tail-owners.json): 15 obiektów źródłowych,
  zachowane 25 w pełni związanych szkiców; dwa szkice gniazd mają wymiary
  i wspólną średnicę zamiast `Block`. Pozostałe odziedziczone blokady nie znikają.
- [Przeniesienie](validation/relocation.json): świeży proces, 45 odnośników,
  dziewięć dokumentów z nowego katalogu, solver oraz zmiany obu parametrów poprzez
  odnośnik do złożenia. Nie korzystano z oryginalnych ścieżek plików CAD.
- [Fasteners](validation/fasteners-smoke.json) i [widok kota](validation/whole-cat.png).
- [Testy ROS/narzędzi](validation/tests.json): 656 zaliczone dla v35,
  bez pominiętych; trzy istniejące ostrzeżenia bibliotek.

Uruchom pełne testy z `ROBOT_CAT_CAD_REVISION=v35`; domyślne v28 pomija testy
nowszej mechaniki. Nowych prób dynamicznych Gazebo nie wykonywano: geometria
i położenia są zachowane, a to zadanie dotyczy organizacji CAD i narzędzi.

Manifest [modular-pilot.json](../releases/modular-pilot.json) przypina konkretne
pliki. Kontrola integralności ma przejść, `--require-print-ready` ma odmówić.

## Oddzielne studia konstrukcyjne

[Boczny dostęp do nakrętki ogona](studies/tail-coupling/README.md) jest
niezależnym wariantem nasady, **nie zmianą złożenia**. Ma własny audyt i manifest.
Nie zamyka brakującego orczyka MG92B, TEMP ani wymagań wytrzymałościowych PETG.
Aktualny [PNG całego kota](validation/before-tail-coupling.png) pochodzi
bezpośrednio z FreeCAD, przed pracą nad tym wariantem.
Zestaw 656 testów obejmuje cztery kontrole dowodów tego studium. Manifest
modułowy przypina też jego osobny manifest, bez włączania części do złożenia.
