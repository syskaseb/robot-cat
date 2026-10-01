# E3: dobór nominalny, koordynacja źródła nadal otwarta

Jedna karta23wybranych bezpieczników, bez nowych części i wydruków. R33 CAD,
wiązka, ilości i wartości wkładek zachowane. Nie podniesiono amperażu.
Źródłowa karta MTA już była w referencji23.09, ale R30 utraciło ten dowód:
R34 przywraca jej32V/1000A i charakterystykę dla konkretnego MiniVAL10A.
KartaMTA jest v00 PRELIMINARY2018, nie pomiar dostawy. F_PWM ma250VDC/4000A
według wybranego E2; korygujemy stary ogólny wpis32V, nie projekt kasetki.

W sources.json są odnośniki do producentów, rewizje i wynik lokalnego
pobrania. branch-protection.json łączy każdą wkładkę, gałąź i obliczenie.
Prądy referencyjne/zadaną granicę20A oddzielono od prądu zwarcia.
23wkładki NIE chronią same z siebie przed zablokowaniem wszystkich napędów.
Nie twierdzimy pełnej selektywności wkładek10A/4A.

E3 pozostaje OPEN: źródło/F0,15fabrycznych doprowadzeń, cieńsze końce przed
ich wkładkami oraz DCłączone obciążenieS821/przetwornic. To braki dowodu
elektrycznego, nie brak mechaniki głowy. Nie wolno ich zaliczyć jako PASS
ani zastąpić typowym topikowymI²t lub założeniem50mm. Karta dokładnegoS821
podaje DCresistive30A, ocena750Wmotor jestAC125V; S821D to inny model.

Próby fazy2: oględziny przewodów/styków, kontrola odizolowania/polaryzacji,
prądowe i termiczne próby na kontrolowanym zasilaniu po doborze granic.
Bez celowego zwarcia pakietu ani blokowania wałów, bez utożsamiania
odczytu rezystancji ładowarką z gwarantowanym minimum impedancji zwarcia.
Brak zasilania/zakupów/GUARD/BMS. 13/20=65%,0nowychSTL; fizycznyPASS=false.
