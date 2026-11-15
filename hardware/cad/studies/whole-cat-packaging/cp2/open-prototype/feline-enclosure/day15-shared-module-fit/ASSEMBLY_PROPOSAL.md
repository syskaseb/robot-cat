# Jedna wspólna architektura modułów — wynik: HOLD przed detalami

**To propozycja całego wspólnego mocowania, nie nowy zestaw do druku.** Źródłem jest zamrożona podstawa `fit-kit-ready`/6c6a1f70; osiem osi, kupna rama/nogi i jej36plików pozostają bez zmian. Bieżący CAD: `shared-module-proposal.FCStd`. Nie wyeksportowano STL ani kolejnej kasety/uchwytu płytki.

## Decyzja i dowód

Wybór: dwa poprzeczne portale mocowane czterema pełnymi zaciskami do krawędzi DRUKOWANEJ płyty. Dwie wewnętrzne belki ponad baterią niosą wspólną płytęPi/logiki oraz boczną półkęMAIN/AUX. Cały BUS przeniesiono znad chłodzeniaPi na osobny środkowy mostek zdejmowany przed baterią. Pozostałe kupne moduły, pełne12bankówMTA/TE/ATO,5FHAC,F0,S0z11częściami/S1 i końce zachowano w aktualnych położeniach.

Odebrano pierwszą przesłankę: rzeczywiste górne i dolne pola oparcia wszystkich4zacisków w geometrii P02/P03; dolne tylne szczęki odwzorowują rzeczywisty schodek P03. Pełne śruby/nakrętki/podkładki pozostają oddzielone od126zachowanych brył WAVEGO przez numeryczne dolne granice odległości; bez globalnego Boolean126. To nie dowód udźwigu ani fizycznego chwytu. Szczegóły `first-gate.json`.

Nowy pełny BUS X18..60/Y−16,5..16,5/Z110..134 jest31mm od pełnej nominalnej rezerwy chłodzeniaPi. Oznacza koniec dawnego konfliktu rezerwy3,12mm dla tej konfiguracji, a nie kwalifikację temperatury ani wszystkich jego portów. Pi i jego GPIO/USB/Delock nie przesunięto.

**Pierwszy rzeczywisty falsyfikator całej alokacji:** wspólna dolna belka dochodzi do pełnej nominalnej rezerwy wzmacniaczaMAX98357A, która ma X−60..−33/Y−39..−15/Z75..88. Belka zaczyna się naZ88. Poprawne pełne bryły: gap0mm/common0. To HOLD przy wymaganym1,25mm, nie kontakt dostarczonej płytki ani globalna niewykonalność. Geometria audio jest nominalną rezerwą wymaganej części, nie zweryfikowanym modelem dostawcy. Nie obcięto jej i nie nazwano OWN. Po tym wyniku zatrzymano rodzinę; pozostałe11modułów/łożysk w tej kontroli jest jawnie UNRECEIVED.

**Skutek:** następna decyzja musi wspólnie rozstrzygnąć dolną warstwę audio/czujników i drogę nośną/wireaccess, zanim powstaną szczegółowe panele, dystanse czy eksporty. Nie przesuwać samej belki o ułamek milimetra i nie udawać kompletnego montażu. Aktualny CAD i obie bryły falsyfikatora są zapisane.

## Jeden układ i funkcje, bez domyślnego zamrażania starych druków

Portal przedni X−104..−98/Z48,52..95,52; tylnyX95..107/Z48,52..107. Zewnętrzne nogi Y−86..−80 oraz80..86 omijają pełne banki, a tylny most przechodzi naZ103 powyżej pełnychFHACdo101. Podstawa nie zmienia długości/szerokości; zaciski zwiększają tylko zewnętrzny zakres mocowania doY±88. Odległości od nóg w ruchu pozostająFIT1.

Belki X−98..95/Y−20..−14 i16..20/Z88..96 mieszczą baterię doZ86,5 poniżej. Wspólna płytaPi ma spód92,52/wierzch95,52; cztery3mm izolujące słupki wykorzystują rzeczywiste osie cylindrówØ2,75 w zapisanym PCB: X−74,5/−16,5 iY−34,5/14,5. To źródłowy odczyt CAD, nie wymyślony rozstaw ani dostarczony gwint. Długość całychM2.5 i spodnie komponenty wymagają przymiarki.

PółkaMAIN/AUX X55..126/Y18,5..50/Z88,52..92,52 zostawia1,48mm do zachowanych płyt; faktyczne odciążenie/śruby lub docisk krawędzi NIEodebrane. PCA/E1 opierają się dolną krawędzią na wspólnym skrzydle; pokazanie tego styku nie zastępuje docisku i dostępu do wszystkich końców.

Stara niewydrukowana rama/logiczne belki, mostkiPi i półkaBUS zostały jawnie wycofane z tej propozycji. Ich funkcje przeniesiono do nowego wspólnego szkieletu; nie przesunięto kupnych płytek w celu ukrycia1mm. P06 pozostaje niezmieniony jako węzełS0; jego stare gniazda nie są już domyślną jedyną kotwą elektroniki. Nowy szkielet ma1poprawną bryłę i zerowy brak wszystkich15zamierzonych składników. Nazwane składowe są ukrytymi referencjami FUNKCJI, nie zdublowanym BOM. Jest to koperta rzeczywistego materiału konstrukcji; **podział na płaskie portale/listwy i kompletne śrubowe połączenia pozostajeOPEN**, bez deklaracji drukowalnego monolitu. Dolne szczęki i zdejmowany mostekBUS są osobne; kupnych modułów nie scalano z drukiem.

## Kolejność dla dwóch osób — warunkowa dla tego samego układu

1. A: P00/8osi/rewizja/gwint na posiadanym WAVEGO; B: komplet części i odłączona bateria. Zachować pierwotną przymiarkę podstawy, bez wiercenia/gwintowania metalu.
2. Zaciski do rzeczywistej drukowanej krawędzi montować przed bankami i baterią. A trzyma górny portal, B podaje dolne dopasowane szczęki/nakrętki i kontroluje pełny chwyt. Nowe standardowe2M3×12+2M3×16,4pełne nakrętki2,4 i4podkładki0,5 są zapotrzebowaniem, nie stanem magazynu. Ostateczny podział portali/listw/połączeń dopiero po usunięciu obecnegoHOLD.
3. E1/MODULE i końceMTA przygotować na stole pozaPETG; nie rozłączać wirtualnie lutów. WAGO montować według ról4DATA/5plus/7masa. PełneMTA/TE/ATO,FHAC i ich dwa końce układać w otwartych obszarach; dawne3mm między stacjami nie dowodzą wyjścia przewodów.
4. Po rzeczywistym zamknięciu warstwy audio i podpór dopieroPCB/izolujące dystanse/porty. ZakresGPIO/USB/Delock/PWM/MAIN/AUX/S0/S1 i narzędzia muszą być dostępne przed dociskami/tylnymi osłonami. Prawdziwa retencja baterii i wybranych2pasków pozostaje osobną brakującą funkcją, nie samym naciskiem grawitacyjnym stóp.
5. BUS na środkowym mostku po podłączeniu jego rzeczywistych końców. Przed wyjęciem baterii: odłączenie baterii, rozłączenie istniejących rozłącznychUSB/zasilaniaBUS zgodnie z faktycznymi portami, odkręcenie mostka i zdjęcie go. Nie zakładać parkowania połączonego przewodami ani dodatkowej długości; tej sekwencji jeszcze nie przyjęto geometrycznie/na sprzęcie. Nigdy nie odpinać lutówE1 dla wygody.
6. Głowa/ogon, kamera/ToF/audio/touch, panel tylny i sylwetkaOli pozostają na całym widoku; ich11dalszych sprawdzeń po falsyfikatorze jest nieodebranych. Rzadka naprawa może wymagać demontażu; nie projektować szybkiego serwisu ani produkcyjnej skorupy w tej porcji.

## Końce, miejsce na wiązki i rzeczywiste niewiadome

Wspólne otwarte obszary: niżej rozdział/WAGO i12zabezpieczeń, nad boczną półką otwartyfanP/G/logika, PiGPIO na otwartej stronie, luźny pełnyUSB500 zDelock i odciążenia obok mostka; banki/FHAC pozostają dostępne od boków. Są to połączone kierunki układania w otwartym prototypie, **nie odebrana pojemność każdej wiązki/R/length/slack**. Każdy krytyczny port i przejście musi po zamknięciu obecnegoHOLD dostać rzeczywiste miejscowe sprawdzenie; same prostokąty nie sąPASS.

4niezależne220 iobaMTAkońce, pełnyUSB500,5parFHACminimum84,5, K1474Pi350/kolor vsinput210 i końce fabryczne zachowane; brak cięcia, nowego złącza/puli albo kredytu starej pozy. Actualinstalledlength/cut/slackNULL.57wybranych wCSV bez zmiany grafu; wymagane audio/sensory zachowane z jawną nominalną geometrią/revisionfit. PraktyczneFIT1(mocowania/masa/ruch),FIT2(porty/końce/S0M6/chłodzenie/stock) iFIT3(pełny obrysOli/głowaogon) nadal niewykonane. Nie ma nowego fizycznegoPASS, zasilania, druku, zakupu ani eksportu do slicera.
