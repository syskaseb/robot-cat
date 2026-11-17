# Dwie przymiarki mechaniczne — 17.11.2026

Status: **warunkowa przymiarka bez zasilania**, nie gotowy kot ani komplet zamocowanej elektroniki.
Otwórz `two-assembly-interfaces.FCStd`. Jedynym bieżącym wykazem tych dwóch druków jest `conditional-print-index.json`.

## Co rzeczywiście zmieniono

1. **Przedni pokład + N1 to teraz JEDNA część** `A17_front_deck_frame.stl`, ilość 1. Zastępuje jednocześnie stare N1 i P02; nie drukować ich dodatkowo. Zachowano ciągłą podłogę 3 mm, podpory oraz fabryczne osie mocowania. Otwarte dojścia śrub wykonano tylko we własnym druku. Dwie dawne przednie dolne szczęki rusztu nie pełnią już tej roli; nie oznacza to wyrzucenia dostarczonych śrub. P01, P03 i P04 pozostają oddzielnymi częściami.
2. **Osłona przy głośniku** `A17_speaker_side_cowl.stl`, ilość 1. Zastępuje bieżącą FC_F_POS. Ma rzeczywistą zaokrągloną ramkę powrotną i dwa otwory akustyczne Ø40. Pełny głośnik, mocowanie i wszystkie osiem elementów stalowych zachowano w poprzednich pozycjach. Nominalne odstępy: głośnik 4 mm, zdejmowany uchwyt 1,75 mm, stały wspornik 1,5 mm; wymagane 1,25 mm.

## Montaż przez dwie osoby

- **Najpierw P00**: sprawdzić osie, wersję ramy, gwinty i rzeczywiste śruby. Bez wciskania, wiercenia lub gwintowania kupnej ramy.
- Na pustej bazie ustawić integralny przód na P01. Cztery całe źródłowe śruby z łbem stożkowym M2,5×16 wprowadzić od boków: Y±31 do osi Y±22,5, przy łbach na Z72,5; następnie opuścić do istniejących gniazd Z48,52. Osie X−80/−70. Wszystkie wymiary w mm, układ świata CAD.
- Dokręcanie przed PCB i bankami: wspólne dojście od +Y pod 20°, pełny trzon narzędzia 80 mm. Kanały są sprawdzone geometrycznie. Rzeczywisty typ gniazda łba i zgodność klucza sprawdzić na próbce; nie zakładać zgodności katalogowej ze szkicu.
- Druga osoba podtrzymuje pokład oraz pełne nakrętki/podkładki. Połączyć z P03 przez istniejące P04 i kompletne źródłowe zestawy M3×10. Oparcie ma nominalnie ok. 1148 mm² na każdej P01 i 111 mm² na każdym P04. To dowód powierzchni styku, nie obliczenie wytrzymałości.
- Dopiero potem instalować całe moduły i połączony lutowany zestaw E1. Nie odpinać fikcyjnie końców fabrycznych. Uchwyt głośnika zostaje na ramie; docisk wyłącznie do sprawdzonego kosza/kołnierza, nie membrany.
- Ułożyć pełne przewody przed osłoną. Osłonę oferować od +Y na dotychczasowy interfejs. Sprawdzono lokalny obszar akustyczny; pozostałe zależności zamknięcia całego kota nadal są otwarte.

## Pliki i druk próbny

| Plik | Ilość | Wymiary XYZ | PETG 1,27 g/cm³ — pełna geometria |
|---|---:|---|---:|
| A17_front_deck_frame.stl | 1 | 228 × 175,5 × 107,48 mm | 207,84 g |
| A17_speaker_side_cowl.stl | 1 | 238,60 × 117 × 145,38 mm | 112,92 g |

Oba STL zapisano w lokalnym XYZ, minimum Z=0. Największy wymiar z rezerwą 8 mm: 236,0 / 246,6 mm, poniżej 256. Zachować rezerwę na brim i podpory. Podłoga przodu jest do 4 mm ponad najniższymi żebrami: potrzebuje podpór, nie mostu przez całą szerokość. Osłona wymaga podpór pod dachem/ramką. Slicer ani druk nie były uruchamiane. Obie siatki są zamknięte, dodatnie i ponownie odczytane; krawędzie mają po dwie sąsiednie ściany.

Nie drukować innych części tylko dlatego, że są widoczne w złożeniu. Stare nazwy plików N1/P02 nie oznaczają aktualnej wersji. Brak nowych zakupów: istniejące ilości i dostarczone mocowania pozostają do sprawdzenia, nie są potwierdzonym stanem magazynowym.

## Co pozostaje otwarte

Cała ruchoma wiązka FFC200/ToF/JR i jej budżety, cztery pełne MTA0100335, pozostałe mocowania/zamknięcia, wygląd, masa całego robota, obciążenie i próba fizyczna. Te pliki nie awansują ich do PASS. Rzeczywiste dopasowanie, cięcia i luz roboczy: **NULL**. Nie włączać zasilania na podstawie tego pakietu.

Dowody końcowe: `final-intended-front-member-coverage.json`, `actual-front-bearing-and-splice-stock.json`, `front-real-driver-channels-completed.json`, `final-acoustic-full-unit-stock-and-parting.json`. Wcześniejsze negatywne wyniki zachowano jako surową historię. Globalny test 169 pozostał zatrzymany na pozycji 7.
