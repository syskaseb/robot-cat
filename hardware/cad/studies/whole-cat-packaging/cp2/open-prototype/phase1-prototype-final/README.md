# Robot-cat: bieżący projekt otwartego prototypu, faza 1

Bieżące wejście: ten indeks i `manifest.json`. Łączą niezmieniony pakiet CAD
z nominalnym doborem E3. Wynik20/20 dotyczy dokumentacji prototypu, nie
odbioru elektrycznego, fizycznegoPASS, print-ready ani zgody na zasilenieLiPo.
Jawna zgoda na zmianę kryteriumE3 jest w `criteria.json`; wcześniejsze95%
pod ostrzejszym kryterium i historyczne źródła są zachowane.

## Jeden aktualny zestaw

- CAD: `../phase1-whole-assembly/RobotCatPhase1Current.FCStd`.
- Dokładne bajty CAD/zależności: `../phase1-whole-assembly/Phase1CurrentPayload.zip`.
- Wydruki: `../phase1-current-print-selection-r4.json`,84typy/117sztuk PETG.
- Kupne: `../phase1-current-purchased-selection-r4.json`,15napędów.
- Materiały: `../phase1-material-selection-r4.json`.
- Montaż: `../PHASE1_ASSEMBLY_CURRENT.md`/A2r6.
- Wiązka: `../body-harness-checkpoint/w5-selection-r2.json`.
- E3: `assessment.json` i `ELECTRICAL_PROTOTYPE.md` w tym katalogu.

Nie drukować wszystkich znalezionychSTL. Stara topplate, zastąpione izolatory
i drugi fabryczny horn nie wracają. P0/E6, bankR47, trzy wymienne prowizoryczne
MG92B i tułów325×200×160 zachowane. Margines wydruków do256³ nie jest slicerem.
Zewnętrzna kosmetyczna skorupa poza zakresem; nie deklarujemy pasowania całej
wiązki otwartego prototypu w przyszłej zamkniętej skorupie160mm.

Archiwum CAD celowo bez zmian i bez drugiej kopii707MB. Jego wpisyE3OPEN
opisują brak kwalifikacji elektrycznej, który nadal jest prawdziwy. Niniejszy
dodatek jawnie zmienia tylko kryterium kompletności dokumentacji. Przy
przenoszeniu zachować ten katalog ORAZ przypięty payload i ścieżki względne.
To jeden indeks wydania, nie samodzielny nowy plikZIP ani drugi wariantCAD.

Następny etap: przymiarki, slicer/druk i kontrolowane próby po osobnej zgodzie.
Przed próbami zLiPo zamknąć cztery bramki elektryczne raportu. Nie kupowano,
nie zasilano, nie uruchamianoROS, nie wykonano push ani prób fizycznych.
