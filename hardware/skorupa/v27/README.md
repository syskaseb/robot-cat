# v27 — poprawne mocowanie bioder i nowa symulacja

Główny plik: **`Kot_v27_BIODRA_ASSEMBLY.FCStd`**. Oddzielna kopia v25,
bez nadpisywania poprzedniego projektu. **Nie jest wydaniem do druku.**
Branch `codex/robot-cat-mechanical`, repo `syskaseb/robot-cat`.

## Co zmieniono

Otwory M2 w WConnector pokrywają się z osiami otworów w obudowie pierwszego
serwa biodrowego. To obudowa serwa ma się poruszać z łącznikiem, a oba
orczyki pozostawać przy ramie. Dotychczasowe więzy robiły odwrotnie.

Poprawiono **32 rodzice Fixed**: w każdej z czterech nóg sześć części
obudowy/wnętrza serwa przypisano do WConnector, a dwa orczyki do ramy.
Nie zmieniono 12 osi Revolute, geometrii części ani ich pozycji spoczynkowych.
Nie wycinano łączników ani serw. Drugi i trzeci napęd każdej nogi pozostają
bez zmian. Dowód położenia otworów: `mount-axes.json`.

Złożenie ma nadal **2642 obiekty, 238 części, 225 Fixed i 12 Revolute**,
w tym **64 tymczasowe blokady** niedokończonej mechaniki głowy/ogona/elektroniki.
Nie nazywamy tych blokad gotowymi fizycznymi mocowaniami.

`Apply27.FCMacro` zachowuje światowe układy łączników i uruchamia natywny
solver. Wynik: 0 (sukces); **22 klatki ±3°**, największa szczelina łącznika
około **1,23e-13 mm**. Sprawdzono też zgodność osi i brak obrotu Fixed.
Zapisany dokument wrócił do pozycji spoczynkowej.

`assembly-plan.json`, `ownership-changes.json` i `assembly-validation.json`
utrwalają zmianę i hash pliku. Makro należy uruchamiać tylko raz na świeżej
kopii v25 o nazwie v27; asercje chronią przed przypadkową powtórką.

## Gazebo

[Obliczenia i runbook](../../simulation/README.md) obejmują masę, środki masy,
bezwładności, siatki CAD, IK dla zmierzonych osi, regulator ograniczony
momentem/prędkością i osiem rzeczywiście wykonanych prób fizyki.
To model aktualnej geometrii, nie stary kot z prostych brył ROS.

Osobny audyt `hardware/simulation/v27/clearance-samples.json` sprawdził sześć
pozycji (spoczynek, kandydat stania, cztery uniesienia łap). Nie znalazł
nowych przenikań powyżej progu 0,1 mm³ ani wzrostu >5% istniejących.
**Pozostały dwa istniejące przenikania** `FrontRearCover` z obudowami serw,
po około 2,93 mm³. To nie jest wynik „bez kolizji”. Badanie nie obejmuje
ciągłego przebiegu wszystkich trajektorii Gazebo ani wszystkich zakresów.

## Osobny wariant osłony, jeszcze niewstawiony do złożenia

`FrontCoverClearance27.FCStd` to edytowalna część PartDesign z dwiema
natywnymi operacjami odejmowania, wykonanymi przez MCP. Przycięto tylko
zewnętrzne skrzydełka starej przedniej osłony do y=±31 mm. Pozostaje jedna
poprawna bryła; zachowano 2,5 mm materiału radialnie wokół ośmiu otworów M3.
Usunięto 599,28 mm³, czyli około **0,76 g PETG** według modelu gęstości.

`front-cover-clearance.json` zawiera 42 dokładne próby dwóch obudów serw
przy kątach -10..+10° co 1°. Brak wspólnej objętości, minimalny zmierzony
luz **0,936 mm**. `cover_clearance27.py` odtwarza kandydaturę.
Natywna geometria MCP została porównana z obliczoną bryłą dwukierunkową
różnicą boolowską, nie tylko objętością.

**Nie podmieniono części w kocie** ani pliku będącego źródłem zapisanych
wyników Gazebo. Następna rewizja powinna wstawić tę część, zachować więzy
i zweryfikować całość oraz wytrzymałość osłony. To nie zwalnia z testu PETG.

## Odrzucona próba podcinania łączników

`HipReliefStudy27.FCStd` i `hip-relief-candidates.json` są oznaczone
**REJECTED — nie drukować i nie montować**. Próba powstała przed znalezieniem
błędu przypisania serwa; cięcia naruszały okolice otworów M2. Pomoc skillu
`fastener-hole` wykorzystano do ochrony istniejących otworów i oceny
materiału wokół nich. Cięcia odrzucono, zamiast osłabiać mocowanie.

W FreeCAD zostawiono widok całego kota (`whole-cat.png`). Poprzedni model
v25 pozostaje nietkniętym checkpointem/backupem. Stan reszty projektu:
[STATUS](../STATUS.md).
