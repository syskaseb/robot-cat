# WAVEGO 19I — przygotowanie druku i montażu

Odebrano **komplet cyfrowy do pierwszej przymiarki bez zasilania**. Zapisany model rozstrzyga wcześniejsze znane kolizje w przyjętym zakresie. Fizyczne dopasowanie, cięcia i zmierzony luz pozostają nieustalone. Kierunek skrzynkowego tułowia, kociej głowy i widocznego ogona jest przyjęty.

## Przed drukiem dużych części ramy

1. **Zmierz osobno oba fabryczne przewody dostarczonej baterii.** W 19I każdy wymaga około **208 mm samej drogi przewodu, przed doliczeniem rzeczywistych końców**. Model przyjmuje wyjście przy +X na górnej powierzchni pakietu. Potrzeba obejmuje 125,72 mm dolnego przejścia i 82,41 mm górnej pętli obsługowej. Zapisz długość od faktycznego wyjścia do złącza oraz wymiary końców i porównaj rzeczywiste miejsce wyjścia z modelem. Długości dostarczonej baterii pozostają UNKNOWN. Krótsza żyła lub inne wyjście pozostawia dopasowanie baterii OPEN. Tego warunku nie zamyka sam odbiór cyfrowy.
2. **Sprawdź cztery pełne MTA0100335.** Zmierz korpus z MINIVAL, pokrywę z uwięzią, oba wyjścia, średnicę izolacji i niezależną długość każdego nieciętego przewodu. Osobny opcjonalny kupon `E19_MTA_sample_land` służy przymiarce podparcia i opaski poza robotem. Znajdziesz go jako `sample/E19_MTA_sample_land.stl` w archiwum.
3. Sprawdź rewizje i mocowania dostarczonych płytek, oba nadlewy USB przy Pi, chłodzenie oraz długość osobnego USB_AUDIO. Przy R7–R9 przymierz zakładanie izolacji i odciążony odcinek JR przed przygotowaniem okien w izolacji.

Pierwsze dwa sprawdzenia wykonaj przed dużymi wydrukami podstaw. Szczegóły drogi przewodów i rozliczenie oddzielnych jednostek zawiera [bilans 19I](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-complete-first-fit/source-units.json).

## Pliki bieżącego kompletu

| Materiał | Zastosowanie |
|---|---|
| [Archiwum 19I](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-complete-first-fit/19I-WAVEGO-first-fit.zip) | Rozpakuj w całości. Zawiera model, STL, STEP, instrukcje i folder `source` z mapą 160 połączeń oraz źródłami elektrycznymi. |
| [PRINT.csv](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-complete-first-fit/PRINT.csv) | Pliki w archiwum, ilości, orientacje, gabaryty z rezerwą i mocowania. |
| [Pełny indeks części](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-complete-first-fit/material-index.json) | Bieżący wybór obejmuje 50 modeli STL na 70 części i pięć STEP. Kompletuj według tego indeksu, uwzględniając zastąpione i wycofane części. Zachowany starszy STL liczy się w podanej tu ilości. |
| [Model FreeCAD 19I](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-complete-first-fit/whole-cat19I.FCStd) | Złożenie odpowiadające temu kompletowi. |
| [Montaż mechaniczny we dwie osoby](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-complete-first-fit/MONTAZ.md) | Pełne śruby, mechanizmy, pokłady, moduły, dojścia i zamknięcie. |
| [Bieżąca instrukcja elektryczna](ELECTRICAL_ASSEMBLY.md) | Identyfikacja końców, R7–R9, izolacja i kontrola bez zasilania. [Instrukcja w pakiecie 19I](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-complete-first-fit/ELECTRICAL_ASSEMBLY.md) korzysta z folderu `source` po rozpakowaniu ZIP. |
| [Mapa 160 połączeń](../electronics/full-cat/closed-prototype-add7-2026-11-16/assembly-reference/POLACZENIA.csv) i [bilans zakończeń 19I](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-complete-first-fit/whole-termination-plan.json) | 134 połączenia bazy i 26 ADD7 oraz tożsamości całych jednostek. |

Największy wymiar z rezerwą na brim i podpory wynosi 234 mm przy polu 256 × 256 × 256 mm. Objętość pełnego materiału odpowiada 1361,11 g PETG. Scenariusz masy robota wynosi 3,215–3,955 kg. Masa po wydruku, nośność i chód wymagają prób fizycznych.

[Widok ¾](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-complete-first-fit/three-quarter.png) · [przód](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-complete-first-fit/front.png) · [bok](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-complete-first-fit/side.png) · [wnętrze](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-complete-first-fit/interior.png) · [zakres odbioru cyfrowego](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-complete-first-fit/decision.json)

## Kolejność pierwszego montażu

Osoba A składa otwartą ramę i pełne mechanizmy, osoba B przygotowuje śruby, porównuje części z indeksem i prowadzi wtyki. Następnie osadza się elektronikę i ochronę, rozpoznaje fabryczne końce, wykonuje i izoluje właściwe łączenia, ręcznie układa grupy z luzem ruchowym oraz mierzy ciągłość odłączonej wiązki. Pokrywy zakłada się na końcu, obserwując przewody i nasadę ogona.

Zachowaj wszystkie 57 pozycji bazy i ADD7, ochronę, trzy MG250, trzy JR300, cztery E2 i pięć GPIO600. Dwie porcje każdego GPIO pochodzą z jego własnych 600 mm. DATA, POWER i USB_AUDIO mają odrębne funkcje. FFC i ToF zachowują swoje zakończenia. Ogon porusza się wokół Y.

R7–R9 mają warunkową metodę lokalnych odczepów oraz podparcia w 19I. Sprawdź ją na dostarczonym JR z zachowaniem fabrycznych styków, izolacją i odciążeniem. Alarm MOD05015 pozostaw zamontowany i odłączony do uzyskania mapy komór G-Tech/ID konkretnej baterii. Dalsze sprawdzenia fizyczne obejmują wyjścia i końce nóg, rzeczywiste pola płytek, klapki FHAC, optykę, dźwięk, chłodzenie, ruch głowy i ogona oraz wyjęcie baterii. Głębokie pozycje nóg pozostają materiałem planistycznym.

## Historia źródeł

Wcześniejsze odbiory i zamrożone kopie przewodników zachowano w [SOURCES_ELECTRICAL.json](SOURCES_ELECTRICAL.json). Bieżący komplet i zakres przymiarki wiążą źródła 19I.
