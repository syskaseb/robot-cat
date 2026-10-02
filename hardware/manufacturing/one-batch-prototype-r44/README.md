# MAIN: oprawka F_PI i komplet nominalnego wejścia

R44 wybiera F_PI/W043/W077/W078 oraz zamienne Deck i uchwyt MAIN.
P0, E6, pozostałe69 wydruków, DATA/PWM i drogi W060/W061 zachowane.
Nie zamyka całego W5, E3 ani fazy1. Fizycznego PASS nie ma.

## Montaż bez zasilania

1. Na pustej płycie ułóż pas T30L w nowym płytkim kanale od góry.
   Jego dolny odcinek jest nad podporą P0, nie pod płytą. Stare otwory
   oprawki pozostają nieużywane. Osadź zamkniętą FHAC0001ZXJ i zapnij pas
   bez naciągania przewodów. Aby otworzyć pokrywkę, najpierw odłącz baterię
   i przetnij/wymień ten pas.
2. Fizyczne klatki P_SYS od−X mają etykiety .2/.1/.3/.4/.5, ten sam
   wspólny potencjał. W043 z pierwszej klatki do F_PI: nominalny blank40mm,
   świeże12–14mm niepocynowanej żyły w WAGO. Nie używaj długości fabrycznej
   odsłoniętej końcówki jako wymaganej długości odizolowania WAGO.
3. W077: nominalny fabryczny blank80mm. W078: czerwony blank210mm ze
   wspólnego K-1474. Najpierw załóż20mm RNF3/16 na żyłę. Na stole połącz
   po8mm odsłoniętej miedzi na zakładkę8mm, bez gołego styku obok opaski.
   Osłona ma obejmować po6mm nienaruszonej izolacji. Rezerwa gotowego
   profiluØ4,2 jest prowizoryczna: po dostawie sprawdź i w razie potrzeby
   zmień SpliceGrooveRadius. Nie nagrzewaj PETG ani baterii.
4. Dwie opaski T18I w bocznych kanałach mostkaX31/49 podpierają izolację
   łączenia nad złączką WAGO. Przewód czerwony prowadź przez nowy pełny
   przelotX129/Y−8 i jego własny zacisk. Ten przelot nie jest płytką rysą.
5. MAIN przygotuj na stole przed mocowaniem. Czerwony koniec:8mm strip,
   nominalnie5mm odsłoniętego górnego odcinka i3mm rezerwy wejścia w pole;
   dopasuj/dotnij do rzeczywistego pola. Na obu wejściach oddzielne cienkie
   RNF3/32 chronią miedź. Jedna wspólna zewnętrzna RNF3/8 zastępuje
   W060-only RNF3/16. Blank20mm przytnij poza PCB do rzeczywistej pozycji,
   zachowując co najmniej6mm izolacji na obu żyłach; długość blanku nie
   oznacza przewidywanego skurczu do11,01mm.
6. Zamontuj MAIN na zachowanych osiach i osprzęcie. Zachowaj dotychczasową
   opaskę W060; czerwony przewód ma osobną poprzeczną opaskę na nowym
   wypuście MAIN. Nie ściągaj obydwu dróg jednym kolizyjnym pasem.

## Jeden zapas, nie kolejne zamówienie

W043/W077 pochodzą z fabrycznych żył tej samej oprawki. Minimum katalogowe
84,5mm na żyłę pokrywa nominalne40/80mm, ale tnij po przymiarce.
K-1474 pozostaje JEDEN: każda barwa ma swój1m. Po Pi290,249mm i wejściu
zostaje nominalnie czerwony499,751mm/czarny489,751mm. Nie sumuj obu barw.
T18I:93−2 stare oprawki+4 nowe=95 roboczych z tego samego worka100.
T30L: jeden pas zamiast dwóch małych, roboczo21 z dotychczasowego worka100.
Główka6×6×4mm jest rezerwą projektu do przymiarki, nie wymiarem producenta.
Zapas koszulek pozostaje wspólny;
wyjściowa wspólna osłona Pi15mm nie jest podmieniona przez wejściową20mm.

## Dowody i granice

`interface.json`: końce, cięcia, źródła, opaski i izolacja.
`main-positive-complete-r8/checks.json`: zmienione drogi i sąsiedztwo;
wcześniejsze rzeczywiste konflikty zachowano jako odrzucone.
`main-positive-native-r2/checks.json`: natywny model, parametry,
przeniesione ponowne otwarcie i zamknięte STL. Podmieniono dwa wydruki,
nie dodano odrębnej części ani osprzętu gwintowanego. R7 nie wybrano:
dwa rowki dokładnie styczne dawały krawędzie siatki o czterech ścianach.
Wybrane promienie 2,2mm mostka i 1,8mm portalu otwierają te rowki,
bez naprawiania siatki przez wypełnianie otworów.

Miękka rezerwa wspólnej osłony wejściowej styka się z przewodem Pi:
około0,17747mm³. To jawna przymiarka profilu koszulki, NIE twierdzenie
o bezkolizyjnym ani fizycznie zaliczonym robocie. Także rzeczywisty profil
oprawki, Øżył i promienie/pasowania PETG są do sprawdzenia po dostawie.
E3, reszta wiązki i wspólny montaż nadal otwarte. Nie podłączać zasilania
na podstawie tej karty.
