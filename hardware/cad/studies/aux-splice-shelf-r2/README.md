# Jedna półka i przejście XB11

Wybrany lokalny prototyp: AuxSpliceShelfR2.FCStd i osobny STL ×1,74×30×3mm.
Dwa związane szkice, Pad/Pocket, osiem szczelin opasek i okno26×12mm.
Próba grubości3→3,2→3 oraz ponowne otwarcie przeniesionej kopii poprawne.
Osobny element nie zmienia źródeł P0/Deck. R1 jest tylko diagnostyką,
nie drukować obu półek. R2 ma szersze pola i przejście przewodów.

Półka wchodzi między Deck i F_HY na jego istniejących dwóch T18I.
Obniża oprawkę3mm doZ90..102. Nad jej prawym ramieniem WAGO221-412
łączy czerwony HELU23502 z wejściowym fabrycznym leadem16AWG oprawki.
Dwie kolejne T18I mocują złącze; dwie odciążają izolowane przewody przez
połączenie z istniejącymi pętlami mocującymi (assembly.json). Nie ma
nieopisanych otworów, śrub ani nowych zaczepów w P0. Dwie klatki WAGO
są tym samym XB11/AUX6, nigdy parą V+/GND. Serwis z odłączoną baterią:
przeciąć opaski złącza/odciążenia, otworzyć dźwignie, założyć świeże opaski.

Pięć zmienionych obwiedni bez trafień w zapisanej E6, sprawdzonych po
pojedynczych bryłach: półka, obniżona oprawka, WAGO, rezerwa dźwigni
i wejścia. Dwie osobne rurki projektoweS/R15 omijają półkę, oprawkę
i złącze; dodatkowe sprawdzenie E6 w wire-e6.json. Projektowy odcinek
34,331837mm plus11mm odizolowania zostawia39,168163mm z nominalnych
minimalnych84,5mm. To nie pomiar końcówki ani długość do cięcia.
OD fabrycznego leadu≤3mm, jego wyjście oraz wysokość/pitch klatek są
tymczasowymi założeniami. Przy dostawie dopasować tę małą wymienną półkę,
nie przebudowywać P0. Pełna droga P_AUX→półka jeszcze otwarta.

Pierwszy eksport odziedziczył przesunięcieZ−103 z R1 i zaczynał sięZ−1;
naprawiono wyłącznie położenie siatki na stole, model natywny bez zmian.
Obecny STL:Z0..3, zamknięty/jedna składowa, brim5 daje84×40 na256².
Geometryczny kontakt z Deck potwierdzony małym przesunięciem0,01mm:
744,44mm² pola, NIE pomiar docisku/wytrzymałości.

PETG: na płasko, minimum4 obrysy jako ustawienie próbne. Usunąć ostre
krawędzie okna bez zwężania przejścia. Slicer/profil/podpory w fazie2;
sprawdzić ugięcie ramienia, pełzanie i nacisk opasek na silikon. Nie ciągnąć
wiązki za złącze. Bez twierdzeń o fizycznym PASS lub gotowości całej fazy1.
