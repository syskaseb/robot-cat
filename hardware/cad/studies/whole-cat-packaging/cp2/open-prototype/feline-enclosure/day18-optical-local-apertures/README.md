# Lokalne otwory maski kamery i ToF

Otwory 98 powstały przez odjęcie dwóch rozszerzających się brył. Dla ToF
przekrój startowy miał 26 × 26 mm, czyli rozmiar rezerwy instalacyjnej.
Dla kamery nawet mały przekrój startowy mocno rośnie w poziomie wraz z
odsunięciem maski. Ustaw widoczną krawędź jak najbliżej optyki i zamocuj maskę
do tej samej ruchomej części co czujniki. Poprowadź zewnętrzne przejście
pokrywy tak, by ono także pomieściło pole widzenia. Przy całym przodzie
zachowaj pełne części, mocowania, złącza i zajęte regiony wiązek.
[Wycięcia 98](../day18-closed-whole-common-assembly/whole-working-form.py),
[geometria pól przed 98](../day18-connected-storage-pitch-frame/build-true-pitch-receiver.py).

## Bazy na czujnikach

- **Camera Module 3 NoIR Wide.** Lokalny początek to narożnik tylnej
  płaszczyzny PCB. Osie `u, v` biegną wzdłuż krawędzi 25 i 24 mm, a
  `+n` od PCB w stronę sceny. Z konstruktora walca Ø6,95 wynika środek
  czoła w `(u,v,n) = (12,5; 14,4; 12,4)` mm i kierunek `+n`.
  Walec zaczyna się na wierzchu laminatu `n = 1,12` i ma 11,28 mm długości.
  Cztery otwory Ø2,2 mają współrzędne `u = 2 / 23`, `v = 2 / 14,5` mm.
  Wymiary montażowe 12,4 × 25 × 24 mm, kąty H/V/D 102°/67°/120° i skrót
  rysunku są w zapisanym odczycie źródłowym. Oryginalnych bajtów PDF kamery
  nie znaleziono w cache. **Źrenica wejściowa i jej obrys są UNKNOWN.**
  Zachowaj cały zakupiony obiektyw, obudowę i pracę autofocusa.
  [Zapis źródłowy](../day16-head-tail-mask/sensor-primary-facts.json),
  [konstruktor](../day16-head-tail-mask/build-ola-mask-and-sensors.py#L30).
- **Pololu 3417 VL53L5CX.** Użyj nieprzestawionego układu STEP. Kierunek
  normalnej pakietu to `+z`, poziomy wymiar otworu biegnie wzdłuż STEP
  `y`, pionowy wzdłuż STEP `x`. Zewnętrzne wierzchołki na górze pakietu
  przy `z = 2,566` mm dają `x = 4,429…10,859` i
  `y = 7,310…10,370` mm. Poprzednia rezerwa z zapasem ma tam
  `x = 4,10…11,20`, `y = 6,98…10,70` mm. Obejmuje oba okna,
  więc nadaje się na wspólny przekrój startowy H × V = 3,72 × 7,10 mm.
  **Początki, czynne obrysy i indywidualne osie TX/RX są UNKNOWN.**
  Płytka 12,7 × 17,78 mm i rezerwa 14 × 26 × 26 mm pozostają w
  mechanice. W ustawieniu źródłowym przed 98 rezerwa wystaje 2,434 mm
  przed czoło pakietu. Zachowując ją w całości, przyjmij `s ≥ 2,434 mm`
  dla przekroju pełniącego funkcję maski przed rezerwą.
  [Dane STEP, ZIP i skróty](optical-local-apertures.json).

## Otwór z obu stron ścianki

Dla płaszczyzn prostopadłych do osi ustaw głębokości `d_back = s` i
`d_front = s + t`. `s` to odległość od płaszczyzny odniesienia do tylnej
krawędzi maski, a `t` to grubość wzdłuż osi. Jeśli znasz rzeczywiste
płaszczyzny optyczne, licz każdą odległość od właściwej źrenicy wejściowej
kamery albo od czynnego okna TX/RX. Do odległości od czoła modelu dodaj
`z_ref − z_opt` (oba wzdłuż lokalnej osi). Gdy okno leży głębiej niż czoło,
ta poprawka powiększa otwór. Środek i granice należy wtedy wziąć z tego
samego rzeczywistego obrysu. Dla dwóch okien ToF obejmij sumę ich przekrojów
na każdej głębokości.

Na danej osi poprzecznej i dla płaszczyzny na odległości `d ≥ 0` przed
aperturą rozsuń jej granice `[L, U]` do
`[L − d·tan(θ₋) − m₋, U + d·tan(θ₊) + m₊]`. Kąty są półkątami, a `m`
uwzględnia druk i niedokładność ustawienia. Rozchyl kanał przez całą
grubość. Otwór prosty ma mieć przekrój z przedniej krawędzi na całej
głębokości. Dla krzywej lub pochylonej maski stosuj przekrój obwiedni
w miejscu przecięcia ze ścianką. Zaokrąglenia muszą mieścić założone
promienie również w narożach przekrojów.

| Odległość `d` od czoła modelu [mm] | Kamera H × V [mm] | ToF H × V [mm] |
|---:|---:|---:|
| 0 | 8,00 × 8,00 | 3,72 × 7,10 |
| 1 | 10,47 × 9,32 | 4,55 × 7,93 |
| 2 | 12,94 × 10,65 | 5,38 × 8,76 |
| 3 | 15,41 × 11,97 | 6,21 × 9,59 |

Wymiary poglądowe, z zapasem tylko w przekrojach startowych. Kamera
startuje od projektowego kwadratu 8 × 8 mm ze środkiem na osi walca.
Przykładowo przy `s = 1` i `t = 2` dla kamery tył ma ok. 10,47 × 9,32 mm,
a przód ok. 15,41 × 11,97 mm. Rząd `d = 0` oznacza przekrój odniesienia.
Szczelinę mechaniczną dobierz z pełną geometrią części i montażu.

Kamera ma prostokątną obwiednię z niezależnymi półkątami 51° i 33,5°.
ToF ma projektową piramidę o półkątach 22,5° na obu osiach, rozszerzaną
od całego obrysu pakietu. Okrągły stożek o pełnym kącie 45° uciąłby
naroża tej piramidy. Prostoliniowe modele dają przekątne 108,97° i 60,72°,
podczas gdy zapis źródłowy podaje 120° i 65°. Do zamrożenia naroży i
głębokości osłony potrzeba rzeczywistego przebiegu promieni w narożach,
położenia i czynnego obrysu źrenicy kamery w używanym trybie oraz pozycji,
obrysów i kątów emisji/odbioru TX/RX. Geometria tabeli nadaje się do
wstępnego maskowania PCB.

**Jedna próba na rzeczywistych czujnikach.** Porównaj tę samą scenę z
maską zdjętą i założoną w docelowej odległości i grubości. Użyj jasnego
wzorca z detalami w narożach obrazu i matowego celu ToF obejmującego skrajne
strefy przy bliskim oraz typowym dystansie. Sprawdź nowe winietowanie, utratę
stref, zmianę odległości lub przesłuch ToF, a od strony widza sprawdź
przysłonięcie PCB. Próba pozostaje do wykonania.
