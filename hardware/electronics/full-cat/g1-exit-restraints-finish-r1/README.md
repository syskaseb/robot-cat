# R41: niezależne odciążenia dwóch przewodów G1

Jedna poprawka zamienna Deck: węższe, osobne podparcia i opaski W061/G1.5
oraz W060/G1.2. Nie zmienia elektrycznych końców, tras, długości przewodów,
pozostałych podparć ani ilości zamawianych. Dwie opaski zastępują dwie
poprzednie: nadal roboczo 93 z jednego worka 100 szt. 111-02370.
71 zadań wydruku, 110 części PETG, 4 próbki i 114 wierszy ilości.

Trzy szkice w pełni związane, nazwane parametry, cztery pełne przeloty.
Szkice i operacje dwóch poprzednich siodełek pozostają w historii,
ale nie należą do bryły końcowej. Starych szerszych otworów nie używać
do nowych opasek. Nowa bryła końcowa: `G1ExitDeck`, źródło
`hardware/cad/studies/g1-exit-restraints-finish-r1/DeckG1ExitRestraints.FCStd`.
Rzeczywiste sprawdzenia i eksport są w checks.json; samo zapisanie źródła
ani ten opis nie potwierdzają ukończenia eksportu.

Kolejność +X komór G1: [.1,.5,.3,.4,.2], X=[51,58.5,66,73.5,81].
BAT/W025/W036 mają tylko rezerwowane krótkie wyjścia. Nie wybrano ich
pełnych tras. W036 R3 koliduje z XA02/P_AUX, R4 z RL_G i mocowaniem
głowy, R5 z wybranymi XB22/XB23/XS23. Odrzucone próby nie są wydrukami.
Nie ponawiać tych korytarzy bez nowego rozwiązania układu.

Opaski przełożyć przed zapełnieniem elektroniką; główki pośrodku od spodu
każdej pętli. Osadzić nienaruszoną izolację w osobnych rowkach i dociągnąć
ręcznie, nie zgniatając przewodu. Potwierdzić rzeczywisty chwyt i wymiary
główek w fazie 2. Nie pobielać końców do WAGO. Odłączenie baterii przed
demontażem; przeciętą opaskę zastąpić nową.

W1–W4/P0/E6/15 napędów zachowane. Warunek miękkiej izolacji W060 z R40
nadal otwarty. Nie deklarować bezkolizyjności całego robota, fizycznego
PASS ani zamknięcia W5. 14/20=70%, +0 pp. E3/W5/K2/K3/A2/A3 otwarte.
