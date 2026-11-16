# Głowa–szyja–Pi: jedna propozycja funkcjonalna, HOLD nośnego korzenia

Bieżący model: `head-neck-functional-layout.FCStd`. Jest to kandydat do dalszej pracy, **nie zestaw do druku ani przyjęty zamknięty robot**. Źródła dd64/62c/6a zachowano bajtowo. FIRST/runtime/currentassembly nie były edytowane.

Cały zespół głowy przesunięto o 20 mm do tułowia: oba MG, fabryczne rogi i śruby centralne, 608/688, gimbal, pełne Camera3 i ToF, mocowania oraz odniesienia pól optycznych. Pi i jego porty pozostały w pozie dd64. Zamiast pełnej płyty za kamerą powstał otwarty nośnik z bocznymi drogami obciążenia. Zachowano dwa pełne górne zestawy kamery; dwa niezbudowane dolne dystanse zastępują połączone boczne podparcia krawędzi PCB, wymagające fizycznego potwierdzenia bezpiecznego kontaktu.

Głośnik przeniesiono w całości na dodatni bok Y, z powierzchnią akustyczną na zewnątrz. Ma 1,5 mm nominalnej rezerwy do odbiorników MTA. Jego mocowanie i rzeczywista długość przewodu pozostają OPEN. Nie usunięto żadnej ochrony ani zakupnego modułu.

## Fakty rozstrzygające

- Pełne neutralne pole FFC 16,8 × 1,8 mm z dodatkowym pokryciem 0,04 mm: **8 nazwanych sąsiedztw scoped clear**, minimum **1,36 mm** do nowego nośnika. To jest nowy, rzeczywisty kanał, a nie usunięcie wymaganego profilu lub zgoda na przenikanie.
- Dziewięć skorelowanych pozycji yaw ±20° / pitch ±10° daje analityczne długości osi trasy **164,451–191,334 mm z 10 mm końców**. Próbkowane długości krawędzi także zapisano. Nie jest to ciągły dowód ruchu ani debet gotowej całej taśmy: **8,666–35,549 mm tej samej jednostki 200 mm nadal wymaga wykazanej połączonej przestrzeni nadmiaru**. Nie ma cięcia, dłuższej taśmy ani kredytu z USB/Grove/600.
- Nowy korzeń ma **1,00 mm do pola chłodzenia Pi przy progu 1,25 mm: HOLD rezerwy**, nie kontakt dostarczonych części.
- Korzeń i osobny wspólny ruszt mają **262,861187 mm³ wspólnego rzeczywistego materiału: HOLD podziału/montażu**. Zachowanie starej stopy nie dowodzi poprawnego nowego połączenia. Nie nazwano tego integralnym drukiem ani dozwolonym OWN.
- Korzeń i zdejmowane siodło nie przenikają się; mają **272,853 mm² rzeczywistej powierzchni styku na Z69,5**. Dwa nowe pełne M2×10 z dwiema podkładkami i nakrętką zastępują wyłącznie dwa niezbudowane zapotrzebowania M2×14. To nie naprawia dwóch powyższych ograniczeń korzenia.

Następna potrzebna decyzja to jeden rzeczywisty interfejs korzeń–ruszt–chłodzenie z poprawnym podziałem i pełnymi zestawami śrub, **przed zależnymi detalami**. Nie wykonano trzeciej krzywej, obniżenia promienia, zmniejszenia zakresu ani mikroprzesunięcia dla zielonego testu.

## Widoki i montaż

`whole-opaque-front/side/three-quarter.png` pokazują cały kandydat; `whole-interior-with-FFC.png` pokazuje wnętrze. `head-Pi-local-isolated-interface.png` jest jawną izolacją głowy/Pi, a nie dowodem wolnej przestrzeni w całym robocie. Pozostałe lokalne kadry pokazują kontekst przedniej części, nie przekrój brył.

Nowa twarz jest **PROVISIONAL_NOT_PRINT_NOT_MASS** z zachowanymi otworami pól widzenia. Obejrzano rzeczywiste PNG i wzór Oli: wygląd **nadal nieprzyjęty**; złote dyski, nos, wystające stare mocowania oraz przejście szyi pozostają niedokończone. Niczego zakupnego nie ukryto dla upiększenia całych widoków.

Kolejność: pusty ruszt i rzeczywisty korzeń → wstępnie załadowane nakrętki/podkładki → siodło/serwo yaw i jego fabryczne mocowania → 608/journal/fabryczna śruba → fork i pełny pitch/688 → czujniki i połączony nośnik → podłączenie całej FFC przy zdjętej twarzy → ręczne ułożenie wszystkich grup → pokrywy na końcu. **Pierwszy krok korzenia jest dziś zablokowany**, więc ta kolejność nie jest przyjętym montażem.

ToF zachowany w całości; jego cztery żyły OD2,1 wymagają własnego flex R31,5 i rzeczywistej przestrzeni ruchowej, której tu nie zakwalifikowano. Złącza/revizja PCB, fabryczny róg/łożyska/śruba i kontaktowa strona FFC pozostają wąskimi próbami fizycznymi. Niewykonana konstrukcja korzenia i nadmiaru taśmy nie została przeniesiona do kategorii „tylko zmierzyć”.

Pełna kolejność i statusy: `assembly-and-dependent-unit-status.json`. Tylna para zasilania, wszystkie krótkie końce, cztery wymagane MTA0100335 bez liczbowo powiązanego pełnego modelu i zamknięcie całego robota pozostają OPEN. Nie zmieniono ich na PASS w tej porcji. Actual fit/cut/slack = NULL, physicalPASS=false, wholekit=false.
