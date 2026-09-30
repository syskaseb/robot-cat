# R18: konkretne przewody stałej kasetki

Zachowane65 STL/98PETG/4 próbki R17;0 nowych wydruków/CAD.104 pozycje.
Trzy ogólne przewody logiki zastąpiono Donau118-0 czerwony,118-1 czarny,
118-3 żółty, każdy jedna zwykła rolka10m. To zapas, nie długość wiązki.
Producent potwierdza18×0,1mm/0,14mm²/PVC/10m; TME podajeOD1mm,
60V i−10..85°C. Przyjęto obwiednięOD1,1mm, nie tolerancję producenta.
LAPP4125xxxS z TME odrzucono zakupowo: minimum500m, nie1m.

Przypięto faktyczne19 leadów z pwm-carrier-r3:2 czerwone/3 czarne/
14 żółtych; pięć mostków masy6→7→8→9→10→11 oddzielnie, czarne.
Nie usunięto B4–B8 ani rezystorów przez błędne uznanie ich za zbędne.
Piny/oba końce/nety/etykiety w fixed-logic-wire.json. Leady≤50mm na
jednej sztywnej kasetce; nie wyprowadzać ich do ruchomego napędu.
Lutowanie do istniejących pól, bez nowej zaciskarki ani własnej PCB.
Masa sygnałowa nie przenosi prądu serw. PWM5 jest osobne odAUX6.
Mapa adaptera nadal wymaga kontroli ciągłości po dostawie; długości
cięcia/odizolowania ustala przymiarka, nie wymyślone pozycje padów.

Osobna dawna rezerwa6m żółtego przewodu ruchomego zachowana jako
SKU_OPEN. LiY nie ma tu potwierdzonego zastosowania do cyklicznej pętli
głowy. Nie traktować tego zakupu jako domknięcia XS23 lub całej wiązki.
Nie zastępować nim fabrycznych leadów Molex JPWM_IN.

Źródła: https://donau-elektronik.de/artikel/kabel-litzen/
oraz dokładne adresy TME każdego SKU w fixed-logic-wire.json.
Stany/ceny/termin jednej dostawy odświeżyć w fazie2. Nic nie zamówiono.
Następny etap: pełna droga XB11 i ruchoma wiązka głowy z właściwym SKU,
odciążeniami i kontrolą zakresu. Faza1 NIEukończona; fizyczny PASS brak.

Etap konstrukcyjny30.09:START11:39:58Z, granica wyniku12:25:49Z,
45min51s czasu ściennego, fazy nierozdzielone (stage-time.json).
Pełne drogiXB11 r1/r2 odrzucone, nie są składnikiem wybranego zestawu.
