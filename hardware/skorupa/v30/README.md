# v30 — rzeczywisty BNO085 i mechaniczne mocowanie IMU

**Checkpoint rozwojowy, nie wydanie do druku.** W tej rewizji zamknięto
geometrię jednego mocowania elektroniki; nie ukończono pozostałych mechanizmów.
Źródłem jest zachowane [v29](../v29/README.md).

- [Kot_v30_ELEKTRONIKA.FCStd](Kot_v30_ELEKTRONIKA.FCStd): pełny kot, 264 części.
- [ElectronicsDesign30.FCStd](ElectronicsDesign30.FCStd): edytowalny master
  PartDesign i źródłowa płytka; sześć w pełni związanych szkiców.
- [Zbliżenie IMU](imu-mount.png), [cały kot](whole-cat.png).
- [Plan](assembly-plan.json), [test natywny](assembly-validation.json),
  [dopasowanie](fit-audit.json), [zachowanie reszty geometrii](inheritance-check.json).

Kopie kształtów w złożeniu są podpisanymi snapshotami, **nie live-link**.
Zmiana mastera wymaga odświeżenia złożenia i wszystkich raportów.

## Fizyczne połączenie

Stary prostopadłościan IMU zastąpiono rzeczywistym, 55-bryłowym STEP
**Adafruit BNO085 4754**. Oryginał i źródło producenta są zachowane w
[raporcie doboru części](../../reference/component-selection-2026-09-22/README.md).
STEP ma 25,4×22,86×4,53 mm, laminat 1,57 mm i cztery otwory Ø2,5 mm
na rastrze 20,32×17,78 mm. Wymiary karty katalogowej nieznacznie różnią się
od STEP; przed drukiem trzeba porównać rewizję kupionej płytki.

Dodano cztery dystanse PETG Ø6×6,48 mm, cztery śruby M2×12 i cztery
nakrętki M2. Dystanse stoją na istniejącej płycie ramy `Part__Feature038`
na Z=38,52 mm; spód PCB jest na Z=45 mm. Nie opierają się na zdejmowanej
skorupie. Płytę przewiercono Ø2,4 mm, a w dnie skorupy wykonano cztery
przepusty Ø6,8 mm, dające 0,4 mm luzu promieniowego wokół dystansów.
Pierwsza kontrola wykazała kolizje ze skorupą — poprawiono je przed integracją.

Środki otworów w układzie CAD:

| Otwór | X [mm] | Y [mm] |
|---|---:|---:|
| 0 | −35,68 | −22,86 |
| 1 | −35,68 | −2,54 |
| 2 | −53,46 | −22,86 |
| 3 | −53,46 | −2,54 |

Nominalny stos pod łbem: PCB 1,57 + dystans 6,48 + płyta 1,50 = 9,55 mm.
Nakrętka 1,60 mm pozostawia 0,85 mm wystawania śruby M2×12.
Podkładek nie dodano; ich zastosowanie wymaga ponownego obliczenia długości.
Modele śrub/nakrętek są nominalnymi obwiedniami, bez gwintów i gniazd.
Łby i tolerancje zestawu Botland NSZ-00637 nadal wymagają pomiaru.
Łącznie ogon v29 i IMU v30 zużywają 16 M2×12, 16 nakrętek M2,
4 M3×12 i 4 nakrętki M3 — **to nie BOM całego robota**.

Proponowana kolejność: zdjąć płytę, przełożyć śruby przez PCB/dystanse/płytę,
założyć nakrętki od spodu, dopiero potem zamontować zespół w ramie.
Pełna kolejność serwisowa całego kota i dostęp narzędzi wymagają sprawdzenia.
Nie ustalono momentu dokręcania PCB/PETG; nie zgniatać laminatu ani dystansów.

## Więzy, przewody i ograniczenia

Każdy nowy element ma natywne Fixed do elementu fizycznie go podtrzymującego.
`Fix_IMU` nie jest już blokadą tymczasową: PCB jest związana z dystansem,
dystanse i nakrętki z płytą, śruby z PCB. Złożenie: **250 Fixed, 13 Revolute,
35 pozostałych blokad tymczasowych**. Rozbudowano `RobotConnectionTest30`:
22 klatki, wszystkie nogi ±3°, ogon ±30°, IMU przez cały czas nieruchome
względem korpusu. Po próbie przywrócono spoczynek i zapisano plik.

W FreeCAD rozwiń `RobotCatAssembly24 → Simulations`, otwórz
`RobotConnectionTest30`, przelicz klatki i uruchom odtwarzanie.
To test trzymania połączeń, nie fizyczna symulacja obciążeń ani komenda sprzętu.

Master zawiera ukryte `IMUPlugKeepout30` i `IMUWireKeepout30`:
rezerwę na lokalny wtyk i uniesienie przewodu. Nie są drukowane ani
liczone jako masa. To **założone obwiednie**, nie pomierzony wtyk i nie
kompletna poprowadzona wiązka. Audyt nie znalazł ich przecięć z częściami.

Obrót płytki w CAD to Rz=90°, względem REP103 Rz=−90°.
Jest to układ mechaniczny PCB, **nie zatwierdzona transformacja danych chipu**.
Nie zmieniono sterownika IMU. Osie czujnika, kalibracja i wpływ magnetyczny
stalowych śrub, przewodów oraz serw pozostają do zbadania; nie gwarantujemy
poprawnego kompasu. Może być potrzebne inne rozwiązanie materiałowe mocowania
lub estymacja bez magnetometru — dopiero po weryfikacji.

Audyt sprawdził 48 par nowych elementów/PCB w spoczynku: zero przecięć
>0,01 mm³. Każdy dystans ma kontakt z płytą około 23,75 mm² i z PCB ponad
20 mm²; osie śrub nie są zablokowane materiałem. Obwiednie wszystkich części
PETG z mastera mieszczą się w 256³ mm. Nie potwierdzono pełzania, drgań,
wytrzymałości płyty 1,5 mm, tolerancji drukarki ani pełnego ciągłego chodu.
Reguły skillu `fastener-hole` zastosowano do natywnych otworów M2 Ø2,4 mm;
rzeczywiste luzy PETG trzeba sprawdzić próbką wydruku.

249 pozostałych części porównano z v29: 162 BRep identyczne bajtowo,
87 różni się tylko zapisem liczb i wyrównaniem białych znaków.
Największa różnica tokenu liczbowego: 1,03×10⁻¹²; struktura bez zmian.
Sprawdzenie nie certyfikuje dawnych kolizji ani nie zamienia tymczasowych
połączeń ogona/głowy w rzeczywiste mechanizmy.

[Gazebo v30](../../simulation/v30/README.md) uwzględnia nową płytkę,
12 części mocowania i zmniejszone objętości skorupy/płyty. Nominalnie
2,419 kg; trzy nowe próby bez upadku. Nadal brak zatwierdzenia biegu,
termiki serw, orczyka/podparcia ogona oraz mechanizmów głowy.

## Odtwarzanie

W Pythonie FreeCAD, przy zachowanych plikach v29/v30:

```powershell
& $freecadPython -X utf8 tools/freecad/skorupa/cache29.py
& $freecadPython -X utf8 tools/freecad/skorupa/cache30.py
& $freecadPython -X utf8 tools/freecad/skorupa/audit30.py
& $freecadPython -X utf8 tools/freecad/skorupa/inheritance30.py
```

`inheritance30.py` nie wymaga FreeCAD i może działać w zwykłym Pythonie.
Cache BRep jest ignorowany przez Git; dane fizyki mają osobne archiwa.
Audyt jest izolowany od GUI — pełne boolean 55 brył płytki potrafi blokować
interfejs na kilka minut. Nie uruchamiać takich operacji przez MCP w pętli.

`Integrate30.FCMacro` buduje tylko **nowy** checkpoint z zapisanego mastera
i v29; celowo nie nadpisuje istniejącego v30. `Validate30.FCMacro` przelicza
istniejące złożenie, zapisuje spoczynek, nowe SHA, cache i test natywny.
Po zmianie CAD trzeba ponowić audyt, eksport, próby i weryfikację źródeł.
