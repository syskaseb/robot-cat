# Carrier baterii/MTA — części do warunkowej suchej przymiarki

**Bieżący zestaw:3nowe STL po1szt +1kupon kotwy. To przymiarka BEZ ZASILANIA, nie gotowy cały kot ani komplet mocowań elektroniki.**

Najpierw P00/source8osi z zamrożonego zestawu podstawy i rzeczywista rewizja/gwinty. Potem `COUPON_actual_anchor_feed.stl` z dwiema wybranymi opaskami; na końcu trzy aktualne części z `current-print-index.json`. W tym folderze są jedyne bieżące P10/P12/P19; nie używać dawnych STL P10/P12 o tych samych nazwach. P11/P13/P14/P15/jaws i podstawa są wskazane przez niezmienione SHA bez kopiowania9siatek. Model całości: `carrier-capture.FCStd`.

## Jedna wspólna poprawka trzech przyczyn

Przed zmianą wykonano skończony przegląd brakujących zależności:1756bounds/27exact, reuse33+1815wcześniejszych. Zebrano razem P05/H03, brak oparcia przedniej podkładki i brak kotew pasków. Nie robiono kolejnych rodzin lokalnych śrub.

Tylny stop jest szeroki na wolnej części: pokrywa27mm z35mm nominalnej tylnej powierzchni ogniwa. Przy zachowanym P05/H03 jest otwarta zatoka z zapasem1,5mm (1,25+własne0,25), nie cienkaścianka0,75. Cała podłoga2mm pod nominalnym obrysem106,5×35 pozostała:0missing. R5 od strony S0,4stopy, ramię95..100 i odebrany węzeł P12 pozostały. Nowe sprawdzenia obejmują rzeczywiste P05,pełneM3x50,S0 i dodatni materiał; 1461bounds/22kontrole bezHOLD.

Przedni pełny M3x16 pozostał na tej samej osi, z2podkładkami i pełną nakrętką. Zrealizowano brakujące ucho P10 na rzeczywistym48mm³ połączeniu z jego podłogą, teraz podkładka ma gap0/common0. Nie przestawiono łba/tipa ani kupnego modułu. Odebrany pełny pionowy M3x12zachowany; wycofano rolę NIEZBUDOWANEGO tylnego poziomegoM3x25, zostawiając jego ukrytą geometrię historyczną. Nie wycięto jego padów z czynnego ramienia.

## Rzeczywiste zamocowanie obu pasków

Każda CAŁA200opaska przechodzi przez zamknięte okno16,2×4,6mm. Jej pętla obejmuje drukowany mostek (105mm³ wewnątrz każdej pętli), którego dwa boki poza pełną15mm szerokością paska łączą się dodatnią objętością z podłogą. Powstaje rzeczywiste przeplecenie dwóch zamkniętych obwodów, nie etykieta ani tarcie. Bar21mm, endwebs2,4, bok1,75/wysokość4, własny boczny luz0,6; nominalne1,25 od ogniwa. Kotwy po przeciwnych stronach ograniczają boczny przesuw, front/rearstop blokująX, podłoga i zamknięte pasyZ. Dokładna sztywność/luz po naciągnięciu to próba fizyczna, nie rattle/strengthPASS.

Pełny wolny koniec15×2,2 ma ciągłą18mm drogę przewlekania z common0; przewlekać PRZED ogniwem. Sprzączka pozostaje na zewnątrz, nie przechodzi przez cienkie okno. Każda opaska nadal200tkaniny:130,65pętla+20projektclosure+49,35cała reszta;210zawiera sprzączkę. Brak nowych jednostek, cięcia, zapasu25 czy kredytu za krótsze przewody.

## Składanie we dwie osoby

1. Na stole A trzyma P19, B przewleka wolne końce obu opasek i sprawdza kupon. Buckle poza oknem; nie przeciskać metalowego ani grubego szytego końca na siłę. Rzeczywiste maksymalne szerokość/grubość/sewnend muszą zmieścić się w zmierzonym oknie.
2. Dummy/niepodłączone ogniwo i luźne paski układa się PRZED zamknięciem P12: otwór30mm nie przepuszcza pionowo ogniwa35mm. P10/P11 pozostają rzeczywistymi osobnymi, luźnymi elementami podczas ustawiania P19/ogniwa/P12, potem łączymy istniejące otwarte półzakładki i podstawę. Bez wirtualnego odczepiania integralnych części.
3. Dla opuszczania P12 wykazano ciągłe ograniczenie rzeczywistym materiałem nad ogniwem (1,5mm) oraz wszystkimi6polami pasków (2,6/0,4mm lub brak materiału w kolumnieXY); osobno kluczowe nowe człony carriera. To nie pełny rigidtrajectory całego okablowanego kota. Dopasowanie półzakładek/revizji sprawdzić najpierw bez ogniwa.
4. Pełną przednią śrubę/2washers/nut oraz pionowąISO10642M3x12/washer/nut dokręcać w otwartym układzie przed MAIN i bankami. HEX2R4,25 koliduje tylko jako przestrzeń narzędzia z MAIN, więc MAIN później; dolny klucz/nakrętka od−X. Nowe standardowe łączniki: zapas niepotwierdzony, bez twierdzenia o dostarczonym gwincie/torque.
5. Zachowane S0/P06/P05/H03 montować według zestawu podstawy przy luźnych jeszcze elementach ramy; nowa zatoka zapewnia ich miejsce. Pełne banki/MTA220 z obiema fabrycznymi końcówkami i połączony benchkit E1/TTP układać otwarcie; nie udawać rozpinania lutów ani przedłużenia krótkich końców. Elementy ochrony pozostają kompletne. Nacisk MTA wyłącznie na sprawdzony plastik, nie metalowy terminal.
6. Dopiero po suchej przymiarce zamknąć opaski z rzeczywistym właściwym zakładem/naciągiem i zaparkować całe końce. Wszystkie porty/USB/krótkieFHAC/rzeczywiste wyjście ogniwa muszą być sprawdzone na miejscu (FIT2), bez obcinania fabrycznych długości czy pożyczania zapasu.

Późniejsze wyjęcie baterii może wymagać P15mic->P13BUS->rzeczywisteXT60/balance, zwolnienia roguPi naP10 oraz P12/mocowania carriera i podparcia całego połączonego zestawu przez drugą osobę. LutowanyE1 pozostaje cały. Parkowanie pełnych końców i rzeczywista droga demontażu pozostająFIT2; nie przyznano rapidservice ani wholekitGO.

## Druk i granice odbioru

STL są zamknięte,dodatnie,Z0 i poniżej256mm. P10:89,48×176×54, przodem na stole; P12:193×91×43; P19:206×40×93,5 bokiem na zewnętrznej powierzchni MTAfloor. PETG. P19 potrzebuje dobranej adhezji i podparcia pierwszej krawędzi tacki/kołnierza; P12 podniesionej półki logicznej, P10 wystających stop/postów według drukarki. Nie ma przypiętego slicera/profilu ani twierdzenia „bez podpór”. Kupon jest w tej samej orientacji coP19 i służy fitowi oraz próbie kotwy przed dużym wydrukiem.

FIT1:source8otworów/revizja/połączeniawydruków/masa i ręczny ruch nóg; FIT2:całe fabryczne końce,rzeczywisty leadexit i późniejszy demontaż; FIT3:cloth/buckle/lap/tension/padding oraz próba obciążenia kotwy. Bez nacisku przez nieznane powierzchnie ogniwa. Wszystkie57+extras/4DATA5plus7G/ochrona/4niezależne220/MTA zostają. Pozostałe PCB/WAGO/bank/audio retention i korzeń głowy OPEN. Actualfit/cut/slack=NULL; fizycznych prób, zasilania, druku ani zakupu nie wykonano.
