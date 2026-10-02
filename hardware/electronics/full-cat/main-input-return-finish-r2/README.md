# W060: wejściowy powrót MAIN

Status wybieralności określa `checks.json`; sam zapis źródeł nie zatwierdza
podzespołu. Rodzic R39, bez zmiany schematu: G1.2 → MAIN.input_GND.
Drukowane zamienniki to Deck i uchwyt MAIN, bez osobnej dodatkowej części.
Oryginalne podpory P0, otwory śrub MAIN i wyjściowa wiązka Pi pozostają.

Nominalna droga 178,669 mm, blank do przymiarki 220 mm czarnej żyły
18 AWG ze wspólnego Joy-IT K-1474. Nie kupować drugiego kabla.
Po rezerwie wyjścia Pi 290,249 mm pozostaje 489,751 mm czarnej żyły.
Czerwony odcinek wejściowy W078 ma nadal tylko rezerwę 150 mm i nie jest
tym etapem trasowany. Dwie równoległe żyły kabla nie sumują się do jednego
metra materiału. Promień geometryczny ≥6 mm, OD 3 mm są założeniami
prototypu, nie limitami gięcia ani wymiarami potwierdzonymi przez Joy-IT.

Trzy opaski 111-02370 ze wspólnego worka 100: przy G1, przy pionowym
przelocie Deck i na nowym podparciu MAIN. Robocza suma rośnie 90→93;
nie jest to końcowy spis K3. Wyższa obwiednia opaski MAIN uwzględnia
skośny przewód. Rzeczywiste opaski dociągnąć ręcznie do izolacji,
bez zgniatania kabla; sam model opaski nie dowodzi siły trzymania.

## Lokalna kolejność montażu

1. Bez baterii i USB zamontować śruby i nakrętki uchwytu MAIN. Ustawić
   wymagane napięcie później według procedury fazy 2, nie w tym etapie.
2. Przed rozdzielnią/Carrier przełożyć opaskę G1 przez oba przeloty Deck.
   Założyć luźną opaskę na pionowe podparcie przelotu i na podparcie MAIN.
   Najpierw ułożyć zachowane DATA i W061, następnie W060.
3. Odmierzyć 220 mm czarnej żyły po przymiarce. Przy G1 odizolować
   12–14 mm według oznaczenia dostarczonego 221-615; nie cynować końca.
4. Na wyjętym MAIN wprowadzić jedną żyłę do oznaczonego pola wejściowej
   masy. Nominalne 5 mm odizolowania obejmuje przejście przez PCB i
   2 mm szyjki powyżej pola. Nie obcinać drucików, nie rozwiercać otworu.
   Sprawdzić rzeczywisty nadruk pola, nie lewą/prawą stronę zdjęcia.
5. Zachować indywidualną izolację szyjki: 4 mm RNF-100-3/32-0-STK
   (TE5052942064), zewnętrzny blank 15 mm RNF-100-3/16-0-STK
   (TE5053042067). Zewnętrzna osłona musi zachodzić ≥6 mm na nieuszkodzoną
   izolację. Obie ze wspólnego wybranego zapasu; grzać poza PETG.
   Ostateczne długości/ściankę i brak odsłoniętej miedzi sprawdzić po dostawie.
6. Uformować drogę bez zginania na polu lutowniczym. Wprowadzić izolowany
   odcinek w otwarty rowek pionowego podparcia, osadzić wszystkie trzy
   odciążenia i dopiero wtedy dociągnąć opaski. Nie mocować za gołą żyłę
   ani cynę. Zamontować wyjęty moduł i wprowadzić W060 do G1.2.
7. W fazie 2 sprawdzić polaryzację, ciągłość, brak zwarć, trzymanie kabla,
   pasowanie izolacji i brak kontaktu z PCB/sąsiednimi przewodami przed
   zasilaniem. E3 i reszta W5 pozostają otwarte.

Demontaż: odłączyć wszystkie źródła; uwolnić G1.2 i USB-C Pi, przeciąć
trzy opaski W060, wyjąć MAIN z lutowanymi przewodami. Nie ciągnąć przez
zaciski ani rozlutowywać wewnątrz kota. Wymienić przecięte opaski.

Źródła natywne zachowują szkice i parametry dodanych podpór. Narzędzie
rowka MAIN odtwarza dokładną krzywą z `main-input-return-r4`; po zmianie
jej punktów regenerować je skryptem, nie edytować ręcznie anonimowej bryły.
Kontrole parametru, przeniesionego otwarcia i zmienionych interfejsów są
w `checks.json`. Próby PETG, gięcia i izolacji należą do fazy 2.
Nie deklaruje się fizycznego PASS ani ukończenia całego W5.
