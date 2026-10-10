# Aktualna wiązka jednej osi ogona W4

Jedyny wybrany model po poprawnym pakietowaniu: `TailWiringRelease.FCStd`.
Wyłącznie cztery `*_selected_x1.stl` z selection.json, nie pliki pośrednie.
To przygotowanie otwartego prototypu, nie sprawdzony fizycznie robot.
Bank R47, napędy15/P0/E6/wymienne adapteryMG92B pozostają bez zmian.

Zakres: F_TY wyjście, trzy pełne HELU/JR, fabryczny niecięty250mm,
R9, końce/izolacja, niezależne odciążenia, podparcie/retencja, montaż,
nominalne cięcie po przymiarce oraz lokalny wkład do materiałów.
Port5 G_TAIL zastępuje dawny port2 tej SAMEJ masy. Port4 pozostaje XL09.
Sygnał wychodzi ze znanego B3 po R3. Nie zakładamy pinoutu zewnętrznego U1.
Pozostała wiązka i całe wejście F_TY/źródło920mm nadal należą do W5.

Montaż i serwis: wykonywać kolejność z selection.json, bez źródeł energii.
M3x10/nakrętki/podkładki montować przed płytkami i oprawką. Opaski idą
przez pełne przeloty; trzymają korpus lub nieuszkodzoną izolację, nie lut.
Na szynie są dwie opaski do starych natywnych tuneli118/138, jedna JR,
dwie lokalne żył i jedna fabrycznej pętli. Centralny zestaw to6 nowych.
Wspólna opaska dwóch mas zastępuje jedną istniejącą E2, nie podwaja ilości.
Po odpięciu JR, uwolnieniu obu końców/odciążeń i zdjęciu przewodów można
unieść samą drukowaną szynę o30mm; ciągły ruch tej części sprawdzono.
Nie jest to deklaracja ruchu podłączonych kabli ani rzeczywistych dłoni.
ATO wymaga zdjęcia dwóch opasek korpusu. E2 zachowuje rozłączenie po
uwolnieniu obu końców i opaski, podparciu PCB; w razie napięcia bench.

W fabrycznych250mm zawierają się3mm wyjścia i10mm prostego dojścia JR.
R21 to jawne założenie projektu6×3,5mm, nie katalogowy promień kabla.
Poprzednia pętla247mm pomijała dojście10mm i nie została wybrana.
Dostawa ma potwierdzić długość, profil, promień, wyjścia i polaryzację;
przy braku zgodności zmienić wymienną szynę przed drukiem, nie ciąć kabla.

Zagięcie końca B3 wymaga pełnej izolacji aż do spodu PCB, z >=3mm
zakładu na nieuszkodzonej izolacji. Zbędna prosta koszulka osłaniająca
już izolowany przewód została usunięta. Nowy model rezerwuje0,33mm dla
dwuwarstwowej owijki Temflex165; nie dowodzi jej rzeczywistego wykonania.
[Karta3M](https://multimedia.3m.com/mws/media/2145173O/3m-temflex-vinyl-electrical-tape-165-datasheet-en-ner.pdf)
opisuje typowe0,15mm i nakładanie warstw z zakładem. Przydatność tej
małej owijki, pełne pokrycie, przyczepność i brak gołej żyły pod PCB trzeba
sprawdzić bez zasilania. Taśma nie służy jako odciążenie.

Nominalne długości uwzględniają końce i zapas przymiarki, ale nie
oznaczają dodatkowego luźnego zwoju w pokazanym CAD. Dociąć po ułożeniu;
25% to rezerwa materiału, nie automatyczna długość montowana. Pełny stock
robota/K2/K3, E3, slicer/druk i próby pozostają otwarte. Wszystkie eksporty
mają10mm łącznego zapasu względem256³; podpory i drożność kanałów faza2.
