# R19: podparta droga XB11

Wybrany zestaw: 66 zadań STL, 100 zamontowanych części PETG i 4 próbki.
Jedna zamienna płyta Deck z czterema otworami oraz dwa jednakowe uchwyty
przewodu zastępują R18 w tym interfejsie. Pozostałe 64 STL bez zmian.
Nie drukować diagnostycznych uchwytów R1: nakrętka przy X15 trafia w pionową
ściankę (4,685125 mm³). R2 przenosi tę śrubę na X13, zostawiając nominalnie
0,691 mm między obwiednią nakrętki a ścianką.

Przewód HELU23502 z P_AUX.2 do XB11 przechodzi po zewnętrznej stronie
chłodzenia Pi, z gięciami R15 i podporami na Y±50,5. Oba końce pozostają
na AUX6; fabryczny przewód wejściowy F_HY łączy się z drugą klatką XB11.
W `xb11-interface.json` są zakończenia, odciążenia, zapas i kolejność montażu.
Wybrane otwarte przejście nie wymaga wycinania ściany skorupy.

Stara ShellMounted20 nie jest częścią tego zestawu, co potwierdza istniejący
plan dolnych osłon. Zastępuje ją wybrana podniesiona osłona. Nową drogę,
uchwyty i łby śrub sprawdzono względem właściwej osłony. Nie oznacza to
kontroli całej przyszłej wiązki ani fizycznego pasowania.

Montaż na pustej płycie: dwa uchwyty od spodu, cztery M2×10 DIN912,
cztery nakrętki AF4 DIN934 i cztery podkładki OD5/ID2,2/t0,3. Następnie
ukształtować przewód i zapiąć dwie T18I przez pary otworów w dolnych półkach.
Nie ściskać izolacji i usunąć ostre krawędzie przed montażem. Nie zastępować
odciążenia końców samymi środkowymi podporami. Ilości dodane do jednej listy;
opaski pochodzą z istniejącego opakowania 100, bez nowego SKU.

PETG: uchwyt odwrócony, górną płytką na stole; wspornik dolnej półki wymaga
oceny podpór w fazie 2. Bryły ważne/jednobryłowe, STL zamknięte, ponowne
otwarcie i przeliczenie po relokacji poprawne. Wstępne obrysy z brimem 5 mm
mieszczą się w 256³. Nie uruchamiano slicera ani sprzętu.

Faza 1 pozostaje otwarta: pozostałe drogi AUX, pełna ruchoma wiązka głowy,
pozostałe zakończenia i koordynacja zabezpieczeń. Nie jest to zgoda na
zamówienie ani deklaracja fizycznego PASS. Źródła i dowody przypina manifest.
