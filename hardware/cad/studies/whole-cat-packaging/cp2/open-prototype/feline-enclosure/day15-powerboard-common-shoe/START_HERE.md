# MAIN + AUX: wynik wspólnej stopy i próbka M2

**HOLD — nie drukować pełnej stopy ani nowych P11/P12.** Bieżącym warunkowym zestawem carriera nadal jest `../day15-carrier-capture-first-fit/START_HERE.md`, commit4f9ce00a. Tamte29plików pozostają niezmienione.

W tej porcji wybrano jeden wspólny układ. AUX nie jest już traktowany jako sama płytka: PCB1,57, elementy1,8pod/6,1nad i pełne pole9,5mm. MAIN ma prawdziwy obsadzony model rodziny reg32c, z rezerwą opcjonalnego drugiego potencjometru; zakończeń przewodów w STEP nie ma. Płytki ustawiono wspólnie naZ103,52, bez przesuwania innych modułów. Otwory producenta2+3 są przeznaczone dlaM2/#2, nieM2,5.

Stopa kandydująca ma5mm podstawy i6mm słupki. Pod AUX do stopy zostaje4,2mm; pełne śrubyM2x12/podkładki/nakrętki są pokazane. Dwa pełne zestawyM3x14 łączą ją z rzeczywistymi półkamiP12/P11. Długość śruby stożkowej zawiera łeb, długość socketheadM2 jest pod łbem. To zapotrzebowanie NIEPOTWIERDZONE, nie informacja o posiadanych śrubach.

## Dlaczego nie ma pełnego STL

Skończony test zebrał razem zależności: stopa ma tylko1,0mm do polaE2, styka się z istniejącą pełną śrubą ramy i ma0,02mm do paneluS0. Pełny M2 przy trzecim otworzeAUX ma0,89mm do tego panelu. Wymagane1,25mm nie zostało zniesione. Jawne sprawdzenie brakujących bieżących druków jest w `only-missing-current-print-layer-gate.json`: P20/P11 actualcommon3,544973mm³; pełny M2AUX/P11 actual25,767657; pełny M2MAIN/P13 actual2,499696 i washer/P13 actual1,271198. To rzeczywiste druki/stal tej propozycji, bez nameOwn. Nakładanie coverów populacjiAUX812,8 i rodzinyMAIN15mm³ jest natomiast konfliktem rezerwy, nie dowodem kontaktu dostarczonych IC. Pełne końceM2 mają też0,87..0,875mm do istniejących druków. Bieżący P11 nie był operandem starej referencyjnej grupy; brak uzupełniono jawnie, nie przypisano staregoPASS. To problem całej wspólnej warstwy P11/P13/S0/E2, nie powód do pojedynczego przesunięcia łba lub płytki. Nie zbudowano drugiej rodziny.

Pierwszy prostokątny cover drogi nakrętki obejmował też powietrze wokół sześciokąta. Rzeczywisty ciągły swepthex tych samych pełnych nakrętek przechodzi we wszystkich5kanałach, valid/common0. Surowy wynik2,669668mm³ zachowano jako nieadekwatny cover, nie kontakt fizycznej nakrętki. Nie zmieniono geometrii kanału, nut ani pozy.

## Co można przymierzyć

Jedyny wydany STL to `COUPON_M2_fullnut_and_post.stl`: 1szt PETG,12×10,5×11mm, zamknięty/dodatniaobjętość/Z0. Jest rzeczywistym wycinkiem stopy: podłoga2mm, pełne gniazdoM2/antyobrót, dach1,4mm i słupek6mm. Druk podstawą do stołu; sprawdzić jakość dachu kanału, nie zaciskać PCB na niewidocznych elementach. Próbka nie jest częścią do montażu w kocie. Nie wykonywano slicingu ani druku.

Dwie osoby: pierwsza sprawdza całą nakrętkę i śrubę na próbce; druga porównuje rzeczywiste otwory PCB, podkładkę i bezpieczne pole wokół otworu. Najpierw obejrzeć obie strony płytki. Podparcie nie może naciskać IC/lutów ani zasłaniać portu. Producent podaje tolerancję otworów±0,1 i krawędzi±0,3; rewizja dostarczonej płytki pozostajeFIT3. Nominalne pełne zaangażowanie nakrętki nie jest odbiorem tolerancji/wytrzymałości.

## Plan kolejności, jeszcze nie odbiór całego montażu

NakrętkiM2 wsunąć w otwartą stopę na stole, potem pełneM3/nut+washer od dołu przed bankami i płytkami. Płytki preterminować pozaPETG, montować na otworach producenta. Narzędzie dwóch otworówAUX i tylnej śruby ramy zajmuje miejsce monitora: monitor dopiero po dokręceniu, a przy późniejszej naprawie może wymagać demontażu. To nie usuwa stałych kolizji panelu/łba. E1 pozostaje lutowane; bez fikcyjnego odpinania. Rzeczywiste zakończenia i długości MAIN/AUX po zmianieZ wymagająFIT2, bez cięcia i kredytu za starą trasę.

`powerboard-shoe.FCStd` jest zapisanym modelem NIEZATWIERDZONEGO wariantu z pełnym kontekstem, nie następną opcją montażu. `whole-module-layer.png`, `actual-layer-and-blocker-sections.png` oraz `module-layer-dimensions.png` pokazują tę samą konfigurację. Pliki źródłowe/URL i SHA są w `source-pins.json`. Carrier/paski/Pi/audio/pozostałe części zachowane; stare pozytywy nie są ponownie liczone.

Następna decyzja: wspólna dostępna tylna granica P11–łeb ramy–panelS0–E2, zanim powstanie kolejna stopa. Pozostałe mocowania modułów i nośny korzeń głowy nadalOPEN. Cały kot nie jest gotowy; actualfit/cut/slackNULL, physicalPASSfalse, wholekitfalse.
