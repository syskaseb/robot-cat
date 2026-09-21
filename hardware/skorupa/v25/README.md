# v25 — lekka dolna osłona do domu, PETG

Złożenie: [Kot_v25_DOMOWA_OSLONA.FCStd](Kot_v25_DOMOWA_OSLONA.FCStd).
**Nadal prototyp — nie komplet robota zatwierdzony do druku.**
Branch: `codex/robot-cat-mechanical` — nazwa niezależna od wersji modelu.
v24 i wszystkie poprzednie wersje zachowano.

## Co zmieniono

Wysoką wanienkę zastąpiła płaska osłona `Belly25`. To tylko osłona —
**akumulator nadal leży na osobnej tacce `BatteryCarrier23`, na dolnej płycie
WAVEGO.** Tacka, akumulator, jego paski i mocowania nie zostały zmienione.

| Cecha | v24 / stara wanienka | v25 / płytka |
|---|---:|---:|
| Wysokość części PETG | 41 mm | 3,9 mm z podparciami |
| Objętość bryły PETG | 91,28 cm³ | 31,99 cm³ |
| Najniższy element osłony z jej śrubami, Z | −9,5 mm | −5,9 mm |

Około **65% mniej objętości tworzywa**; to nie wynik ważenia ani obliczenie
zużycia filamentu z wypełnieniem. Zysk prześwitu wynosi **3,6 mm** przy tej
samej pozycji robota. Wcześniejsza wanienka rosła głównie w górę, więc nie
przybyło 37 mm prześwitu.

Płytka ma **141 × 94 mm**, podłogę **2,4 mm**, cztery lokalne podparcia
o łącznej grubości **3,9 mm**, naroża R8 i zmiękczoną dolną krawędź R0,4.
Nie ma wysokich ścian bocznych; nie jest szczelna ani odporna na wodę.
Nie służy do podnoszenia robota ani jako podpora akumulatora.

## Mocowanie

Pozostają istniejące cztery punkty na bokach: **X=−35 i 80, Y=±40 mm**.
Nie zmieniono boków ani ich gniazd i metalowych nakrętek M3.

Zmiana zakupowa: cztery śruby z łbem walcowym zastępują **M3×16 z łbem
stożkowym 90°, ISO 10642**. Długość 16 mm jest tutaj mierzona **razem z łbem**.
Model używa maksymalnej obwiedni łba Ø6,72 × 1,86 mm z
[karty Accu SSK-M3-16-A2](https://www.accu.co.uk/countersunk-socket-head-screws/5427-SSK-M3-16-A2)
(sprawdzono 2026-09-21; źródło wymiarów, nie potwierdzenie dostępności zakupu).

Otwory Ø3,4 i pogłębienia 90° Ø7,12, głębokości 1,86 mm. Maksymalny
modelowany łeb chowa się nominalnie 0,2 mm nad spodem płytki. Górny koniec
śruby jest na Z=10,3, czyli 1,6 mm ponad nakrętką. Rzeczywiste tolerancje
średnicy i kąta łba zmieniają głębokość osadzenia — wymagany próbny wydruk
gniazda i rzeczywista śruba. Obwiednie nie odwzorowują gwintu ani gniazda klucza.

Użyto skilla MCP **Fastener Hole Patterns**: natywne szkice i Pocket na
otwory, następnie odejmowane stożki. Ogólne Ø6,3 z tabeli skilla zastąpiono
Ø7,12, aby uwzględnić maksymalny łeb wybranej rodziny oraz jego zagłębienie.
Wszystkie trzy szkice w `BellyDesign25.FCStd` są w pełni związane. Okręgi
mocowań i otworów mają więzy Block; zmiana ich położeń wymaga odblokowania
albo edycji obu wzorów, nie istnieje automatyczne sprzężenie z bokami ramy.

## Kontrole i demontaż

Raport `validation.json` obejmuje:

- poprawność brył/BOP płytki i czterech nowych obwiedni śrub;
- brak statycznych przecięć zmienionych części z zachowanymi elementami;
- 16 kontroli geometrycznego podparcia: płytka, bok, nakrętka i stożek łba;
- dostęp wałka narzędzia Ø4 × 30 mm od spodu (bez modelu dłoni/rękojeści);
- 12 próbek demontażu płytki **prosto w dół od 0,1 do 80 mm**, bez kolizji;
- 21 próbek małego ruchu nóg ±3° bez kolizji z nową osłoną i śrubami.

Odłącz zasilanie, podeprzyj podwozie, wykręć cztery śruby i zdejmij osłonę
w dół. Test dotyczy zapisanej pozycji nóg; próbkowanie nie dowodzi ciągłej
bezkolizyjności przy dowolnym ustawieniu łap.

Luz do łba najbliższej śruby tacki akumulatora pozostaje **0,5 mm**.
Nie zwiększaj samowolnie grubości płytki w górę. Pasowanie PETG, ugięcie,
pełzanie pod łbami i zabezpieczenie przed odkręcaniem trzeba sprawdzić fizycznie;
nie wykonano prób obciążenia ani FEA.

`simulation-validation.json` to dodatkowy test **natywnego solvera Assembly**:
22 klatki, 12 osi ±3°, kontrola wszystkich 237 jointów oraz przecięć ruchomych
części nóg z nową osłoną i śrubami. To nie test pełnego chodu, wszystkich
kolizji robota ani kontaktu łap z podłożem.

## Natywne złożenie i druk

Zachowano 12 Revolute, 225 Fixed, uziemienie i symulację z v24. Instrukcja
odtwarzania: [v24 — uruchamianie animacji](../v24/README.md#jak-uruchomić-animację-w-samym-freecadzie).
Wewnętrzne identyfikatory `Belly22`, `Rigid_Belly22`, `RobotCatAssembly24`
celowo pozostają, aby nie zerwać odwołań. Etykiety pokazują wersję v25.

- [BellyDesign25.FCStd](BellyDesign25.FCStd) — edytowalna historia PartDesign.
- [Belly25.stl](stl-prototype/Belly25.stl) — jedyna nowa część do druku,
  **czarny PETG**, płaską zewnętrzną stroną na stole.
- Zamknięta siatka 141 × 94 × 3,9 mm, bez krawędzi niemanifoldowych;
  mieści się na stole 256³ także z brimem 8 mm. Sprawdź gniazda w slicerze
  i próbce PETG. Nie drukować metalowych śrub/nakrętek.
- [Cały kot](kot-v25-zlozony.png).
- [Przekrój mocowania](oslona-v25-mocowanie-przekroj.png): pomarańczowy bok
  wyróżniono kontrolnie; docelowo także jest z czarnego PETG.

`saved-document-validation.json` potwierdza ponowne otwarcie, zachowanie
pozostałych 233 brył i ich położeń/materiałów oraz natywnych jointów.
Skrypty: `check25.py`, `Apply25.FCMacro`, `Regression25.FCMacro`,
`verify25.py`, `Detail25.FCMacro` w `tools/freecad/skorupa/`.

## Pozostałe prace — nie ukrywać ich za jointami Fixed

64 tymczasowe blokady głowy, ogona i nieukończonych mocowań pozostają.
Nadal trzeba uzgodnić trzy serwa pomocnicze z BOM z czterema obwiedniami
w starym modelu i dopracować rzeczywiste uchwyty oraz napędy.

Zdjęcie tej osłony **nie naprawia drogi wyjmowania całego zespołu akumulatora**:
przeszkodą są dolne krawędzie boków ramy, opisane w v24. Trasa przewodów
i pozostałe wsporniki elektroniki również nie są ukończone.
