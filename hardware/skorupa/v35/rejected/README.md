# Odrzucony wariant — nie składać według tego pliku

`AuxPower35-deck-rear-collision.FCStd` ma cztery śruby M2 do płyty ramy
i dwa krótkie dystanse pod mostkiem. `deck-rear-collision-fit.json` dokumentuje
pięć przecięć: tylne śruby i nakrętki z ramą oraz przedni słupek z krążkiem
`Part__Feature106`. Plik jest zachowany dla porównania, **nie jest v35 do montażu**.

Docelowa korekta: tylne M2 od spodu samego mostka, bez dolnych dystansów
i bez dwóch tylnych nowych otworów w płycie; podcięcie przedniego słupka
według zmierzonego krążka X98,7,Y0,R7,5. Aktualny master jest katalog wyżej.

Raport starej próby dotyczy SHA
`be74bdeb3da73f51a3a66e4b5ea144785fe50e56e15eaf79dd33351e354ae1ed`.
Pierwsza kopia mastera w tym katalogu ma tę samą zapisaną geometrię; nie
jest używana przez integrator ani eksport dynamiki.
