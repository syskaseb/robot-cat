# Integracja elektroniki

Źródła części kupnych są w [reference](../reference/), a aktualne mocowania
i braki w [STATUS mechaniki](../skorupa/STATUS.md). Nie tworzymy fikcyjnego
schematu KiCad tylko po to, aby zapełnić katalog: brak obecnie autorytatywnego
projektu PCB robota i ukończonej wiązki.

Przed wydaniem trzeba ustalić rewizje wszystkich płytek, piny i typy złączy,
długości/przekroje przewodów, zabezpieczenia, odciążenie kabli, bilans szczytowy
i ciągły oraz termikę. Główna i AUX przetwornica 5 V mają osobne wyjścia;
nie wolno traktować ich jako zatwierdzonych do połączenia równoległego.

KiCad/CLI i StepUp są kolejnym etapem, kiedy powstanie własny schemat lub PCB.
Do montażu kupnych modułów nadal służą przypięte modele/dokumenty dostawców.
ERC/DRC nie zatwierdza obciążalności całej wiązki ani chłodzenia przetwornic.
