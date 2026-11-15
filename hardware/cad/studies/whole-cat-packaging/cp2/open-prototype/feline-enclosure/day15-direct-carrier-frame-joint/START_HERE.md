# Bezpośredni pionowy węzeł carriera — wynik jednej porcji

**Nowa droga obciążenia ma odebrany lokalny materiał i pełną stal. CAŁY P19 nadal HOLD; brak STL do druku.**

Otwórz `direct-carrier.FCStd`, potem `actual-joint-and-HOLD-sections.png`. `whole-direct-joint-context.png` jest rzeczywistym widokiem całego wnętrza; kosmetyka tylko ukryta, S0 zaznaczony czerwono. Jedna propozycja, bez drugiej osi, pętli ani ruchu kupnych modułów.

## Co zostało rzeczywiście zrealizowane

Odczyt właściciela: wROI X68..84/Y18..26/Z88,52..92,52 jest512mm³ materiału **P12**,0P11. Dokładny odczyt całego pola później wykazał, że pełna półka16×23,5×4 (1504mm³) JUŻ należy do P12; nie dobudowano fikcyjnej kotwy ani nie sklejono jej z P11. Dodano dwa integralne boki ustalające i nominalne gniazdo stożkowe. Obecny MAIN nie przesunięty: spód94, łeb92,52, odstęp1,48mm.

Nowy rzeczywisty P19 ma belkę X74..100/Y35,5..41,5/Z62..66 -> pionowy wspornik7,6×6 -> dolny kołnierz. Belka łączy się z istniejącym tylnym ramieniem na90mm³; riser/belka i kołnierz/riser po91,2mm³. Oba boki P12 mają po70mm³ rzeczywistego dodatniego połączenia z półką. To geometria połączenia, **nie strengthPASS ani bramka100mm²**. Wszystkie6zamierzonych nowych członów0missing, źródłowy materiał poza zadeklarowanym otworem/stożkiem0missing, oba wydruki osobne/common0. Cztery stopy i wspólny MTAfloor67 zachowane.

Pełny nowy standardowy zestaw: **ISO10642M3×12, długość wraz z łbem**, pełny łebD6,72/h1,86/HEX2, pełna nakrętkaAF5,5/h2,4 i dolna podkładkaOD7/ID3,2/t0,5. Bez górnej podkładki: jej funkcję jawnie przejęło rzeczywiste nominalne oparcie stożkowe. Tip80,52, dno pełnej nakrętki81,62, wystawanie1,1mm. Nowe zapotrzebowanie niepotwierdzone, bez zakupu/inventory/threadPASS. Sześć par całej stali z oboma drukami ma validcommon0. Nowe człony i cała stal:1815tanie bounds +6koniecznych exact bez nowego foreignHOLD. Wszystkie stare kupne części/57+extras/końce pozostają.

## Co zatrzymało CAŁY carrier

Pierwszy wcześniej NIEODEBRANY pełny P19/S0 test: **gap0,233618853<1,25mm, validcommon0**. Świadek P19 jest na oryginalnym tylnym narożniku tacki/stopera `(108,-21,Z60,8/65/68)`; rzeczywista krzywa S0 w `(108,223589,-21,067718,Z)` jest za blisko. Nie jest to kontakt ani stara śruba; nie chodzi o nowy pionowy węzeł. Świadkowie BRep i JSON zachowane.

STOP po tym jednym falsyfikatorze. Nie przycięto teraz narożnika/łba/tipa, nie ruszono baterii/S0, nie zbudowano drugiej rodziny i nie wydano STL. Stare rearM3/S0common60,309861 i P11ROI0 nadal w historii. Stary tylny zestaw/pad nie wycofany przed pełnym dowodem; przedni pełny zestaw pozostał odniesieniem, bez nowego frontrootGO. Nowy węzeł jest PROPOSED/local-scoped, cały kit nie jest gotowy.

## Montaż dwóch osób — plan, jeszcze nie cały dowód

A opiera pusty P19 czterema stopami; B osadza rzeczywisty osobny P12 i jego otwarte od dołu boki wokół kołnierza. Wstępna idea nutloading od+Y nie jest odebrana; dojście od-X pod kołnierzem należy sprawdzić jako otwarty dostęp, nie przenosić w ciemno nakrętki przez riser. Pełny driver od góry ma być przed MAIN i późnymi górnymi panelami. To sourceorder, a pełny feed/tool/ciągła instalacja pozostają **UNRECEIVED po firstHOLD**, nie załatwione słowemFIT.

Potem dopiero pełne banki i4niezależne MTA220 z obiema końcówkami, same2całe200paski w prawdziwych prowadnicach wyłącznie dla baterii, PCB/micP15->BUS/P13->XT60+balance->ogniwo. Lutowane E1 pozostaje połączone, bez cięcia/extension/nowego splice. Rzeczywiste grubość/sprzączka/lap/take-up/padding/bezpieczny plastik MTA/masa/ruch to nazwane próby fizyczne; brak root/access nie jest maskowany jako takieFIT.

Następna konkretna decyzja dotyczy **tylnego obrysu tacki i funkcjonalnego zatrzymania baterii przy realnym S0**, z zachowaniem tego nowego pionowego węzła. Nie wracać do kolejnych osi dolnego P11 ani nowej pętli. Odbiór pozostałych wcześniej nieodebranych sąsiadów i feed/tool dopiero po tej przyczynie. Pi4/guide/audio i dawne scope są tylko niezmienionym re-use, nie powtórką globalnych testów. Actualfit/cut/slack=NULL, physicalPASSfalse, wholekitfalse. Brak druku/zasilania/slicera/zakupu.
