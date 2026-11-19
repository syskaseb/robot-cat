# WAVEGO — od czego zacząć montaż

Dla dwóch osób przygotowano model, indeks części i instrukcje odebranego wariantu **19E**. Prosty skrzynkowy tułów, proporcje głowy i widoczny ogon są przyjętym kierunkiem. **Cały pakiet pozostaje HOLD z powodu znanych kolizji przewodów.** Poprawa wspólnej przestrzeni wiązek i zamknięcia jest w toku. Powiązanie końcowego pakietu ma status **PENDING**.

## Pliki do przygotowania i przymiarek

| Materiał | Jak go używać |
|---|---|
| [Indeks części 19E](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-simple-box-common-core/material-index.json) | Pole `parts` określa 48 modeli STL na 64 sztuki. Sprawdź `qty`, orientację `print_pose` oraz gabaryt z rezerwą `envelope_with_allowance`. Największy zapisany wymiar z rezerwą wynosi 224 mm przy polu 256 × 256 × 256 mm. |
| [Mapa użytych i wycofanych części](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-simple-box-common-core/effectivity.json) | Kompletuj według aktualnego indeksu. Pozycje `retired` są zastąpione. Część zachowana ze starszego folderu występuje w ilości podanej w bieżącym indeksie. |
| [Złożenie FreeCAD 19E](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-simple-box-common-core/whole-cat19E.FCStd) | Pokazuje rozmieszczenie mechanizmów, modułów i osłon tej wersji. |
| [Montaż mechaniczny dla dwóch osób](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-simple-box-common-core/MONTAZ.md) | Kolejność mocowania nośników, głowy, ogona, ochrony, modułów i drzwi baterii. Podane przebiegi przewodów wymagają opisanych niżej poprawek. |
| [Montaż elektryczny](ELECTRICAL_ASSEMBLY.md) i [mapa 160 połączeń](../electronics/full-cat/closed-prototype-add7-2026-11-16/assembly-reference/POLACZENIA.csv) | Identyfikacja obu końców, całych kabli, łączeń i kontrola bez zasilania. |
| [Materiały elektryczne](../electronics/full-cat/closed-prototype-add7-2026-11-16/assembly-reference/MATERIALY.csv) | Tożsamości przewodów. Korektę błędnego 84,5 mm dla MTA0100335 podaje instrukcja elektryczna. |

W indeksie `stl` wskazuje plik względem folderu 19E. `zip_entry` wskazuje go w [archiwum komponentów i montażu](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-simple-box-common-core/19E-components-and-assembly.zip). Osobny kupon `E19_MTA_sample_land` znajduje się w `off_robot` i służy przymiarce jednej oprawki poza robotem. [Kupon STL](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-simple-box-common-core/components/E19_MTA_sample_land.stl)

## Najpierw przymiarki dostarczonych części

1. Zmierz kompletną MTA0100335 z MINIVAL, pokrywą i uwięzią, oba wyjścia, średnicę izolacji oraz osobno oba niecięte przewody. Porównaj cztery sztuki. Na kuponie sprawdź podparcie, przejście opaski i dostęp do jej zaciągnięcia.
2. Sprawdź rzeczywiste obudowy, rewizje płytek i mocowania, szczególnie BUS, Pi z chłodzeniem, ReSpeaker i pełne wtyki USB. Przymierz maskę, gniazda uszu i oczu oraz sworzeń i klucz ogona.
3. Przy odłączonej baterii i USB przymierz boczne drzwi, paski i drogę wyjęcia baterii z odłożonymi złączkami RR. Sprawdź dostęp do wyłączników.

Osoba A montuje pełne mechanizmy i podpory, osoba B porównuje części z indeksem i prowadzi kable przy otwartych pokrywach. Dalej kolejno osadza się elektronikę i ochronę, rozpoznaje fabryczne końce, wykonuje i izoluje właściwe łączenia, ręcznie układa grupy wraz z luzem ruchowym, a następnie człowiek mierzy ciągłość odłączonej wiązki. Pokrywy są ostatnim etapem po rozwiązaniu kolizji i kontroli ruchu.

## Co pozostaje otwarte w projekcie

W 19E MG250 yaw przecina rzeczywistą płytkę Pi. MG250 pitch i część żył ToF trafiają w podporę lub ruchome osłony. Fabryczny powrót ogona przecina S1 i tylną obsadę. Dolny nawrót DATA500 przecina baterię, MAIN i F_PI, a także tylną podstawę. Te przebiegi wymagają zmiany projektu przed wiązaniem i cięciem. Pozostaje domknięcie przestrzeni wiązek przy szyi oraz potwierdzenie ruchu, chwytów i zamknięcia całego układu. [Zakres i otwarte kolizje 19E](../cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day19-simple-box-common-core/START_HERE.md)

Zachowaj pełne 57 pozycji bazy i ADD7, ochronę, trzy osobne MG250 i trzy JR300, cztery przewody E2 oraz pięć Pololu600. Dwie porcje każdego Pololu rozlicza się w granicach jego własnych 600 mm. Fabryczne końce i wymagany ruch pozostają częścią montażu.

Alarm MOD05015 pozostaje zamocowany i odłączony. Przed połączeniem z baterią potrzebna jest właściwa mapa fizycznych komór G-Tech i ID dla dostarczonej rewizji. Szczegóły identyfikacji oraz pomiarów MTA podaje instrukcja elektryczna.

Fizyczne dopasowanie, wykonane cięcia i zmierzony luz pozostają nieustalone. Przymiarki i pomiar ciągłości odbywają się bez zasilania. Integrator po odbiorze końcowej wersji aktualizuje powiązanie plików w [SOURCES_ELECTRICAL.json](SOURCES_ELECTRICAL.json), a następnie odnośniki w tym punkcie wejścia.
