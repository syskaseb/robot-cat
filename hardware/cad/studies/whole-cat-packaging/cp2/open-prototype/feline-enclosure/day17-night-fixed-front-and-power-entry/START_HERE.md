# Stały komputer przy szyi + tylne wejście zasilania — HOLD

Jedna wspólna propozycja została sprawdzona i odrzucona przed budową mocowań. Model `fixed-front-and-power-entry.FCStd` jest zapisem roboczym tej propozycji, **nie bieżącym zestawem do druku ani przyjętym całym kotem**. Nie powstały STL.

Pi obrócono jako cały stały zestaw PCB/chłodzenie/GPIO/Delock do pionowej płaszczyzny przy głowie. F0, pełne XT60 z osłonami i POST przestawiono jako całe jednostki do tylnego wejścia. Wszystkie siedem brył zachowało objętości i sztywne położenia względne wewnątrz własnych zespołów. Inne części i źródłowy cb0fcc8c są zachowane. Dwa świadki ruchu/przecięcia nie są nowymi częściami BOM.

## Fakty rozstrzygające

- Po nowym ustawieniu F0 pełne wybrane pole XA01 ma do niego **2,55 mm** odstępu. To zamyka tylko tę parę przy raw84,5; nie całą rodzinę zapasu ani wszystkie ogony.
- Do rzeczywistego korzenia ogona F0 ma **1,00 mm**, mniej niż 1,25 mm; common=0 nie wystarcza. Najbliższe punkty leżą między Y17,5 i18,5 przy X133..141. F0 jest pełną konserwatywną kopertą instalacyjną, nie dokładnym plastikiem dostawcy: HOLD alokacji, nie dowód kontaktu dostarczonych części.
- Niezależny odczyt wybranej pionowej pozy Pi: przy yaw−20°/pitch−10° pełna instalacyjna koperta GPIO z fabrycznymi końcami przecina zachowaną ruchomą ramę głowy: **176,239 mm³**, valid/common valid. Konstruktor tej koperty jawnie mówi „installed assembly envelope”; to nie dokładny model formowanego złącza. Odrzucono zajętą przestrzeń tej propozycji bez zmniejszania koperty.

129 relacji zmienionych części/przestrzeni oraz22 relacje próbkowanych pozy głowy do pierwszego falsyfikatora. To lokalne, ograniczone odczyty: bez powtarzania całej macierzy świata, bez dowodu ciągłego ruchu z dziewięciu próbek. Po HOLD nie wykonano drugiej pozy/wysokości/krzywej ani podpór.

## Co dalej wynika z tego układu

Przed mocowaniami potrzebna jest wspólna decyzja o przednim odbiorniku i kierunku pełnego złącza GPIO względem rzeczywistej przestrzeni ruchu głowy. Z tyłu granica F0 i nośnego korzenia ogona wymaga prawdziwego funkcjonalnego interfejsu, bez zmniejszenia F0 lub skasowania ochrony. Nie wystarczy przesunięcie końca FFC. Nowy komputer nadal nie ma wykonanego odbiornika/pełnego mocowania; stare poziome śruby i U pozostają historycznym drukiem, nie przeniesionym mocowaniem.

FFC200, ToF4×OD2,1/R31,5, pozostałe8ogonów FHAC,4niezależneE2, pełne25komór i przewody, retencje oraz obudowa pozostają jawnie OPEN. Nie ma nowego kredytu długości z cięciwy, dawnej krzywej ani W078150. W078RED210 jest blankiem projektowym z tej samej K1474_1000; właściwe końce liczone raz. Cztery MTA0100335 nadal wymagane/UNBOUND, bez wymyślonej koperty.

`whole-disposition-and-assembly.json` rozdziela niewykonane połączenia CAD od fizycznych FIT i podaje proponowaną, **niezwolnioną do montażu** kolejność dwóch osób. Pokrywy późno, całe E1/JR/fabryczne końce, żadnego wirtualnego odpinania lutów. Podpory, śruby i bezpieczne styki trzeba dopiero wykonać po zmianie wspólnego interfejsu.

## Widoki

`whole-opaque-front/side/three-quarter.png` pokazują tę samą propozycję z wcześniejszą nieprodukcyjną obwiednią; realne wystające części pozostawiono. Wygląd nadal nieprzyjęty; brak nowej kosmetyki i masy ze szczelnej obwiedni. `whole-current-interior.png` pokazuje wszystkie aktualne grupy. Dwa `local-...HOLD.png` są jawnie izolowanymi dowodami: ruchomy świadek ramy przy−20/−10 i tylne7operandów. Nie przedstawiają całego robota.

Źródła i hashe: `sourcepins.json`, dowody: `one-whole-cheap-gate.json`, `independent-head-nine-sample-gate.json`, `actual-rear-root-nearest-points.json`. Actual fit/cut/slack=NULL, wholekit=false, physicalPASS=false. FIRST/runtime/currentassembly nieedytowane. Jedna GUI pozostaje otwarta i zapisana; częściowy wynik nie zamyka autoryzowanego okna.
