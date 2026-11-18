# Warunkowe przymiarki frontu — nie cały kot

Bieżący model: **connected-storage-pitch-frame.FCStd**. Trzy aktualne STL w **CURRENT-conditional-print-index.json** są wyłącznie do niepodłączonej przymiarki mechanicznej. Nie używać wcześniejszego conditional-print-index.json ani starych trzech pionowych połączeń: to zapisane, odrzucone etapy.

Zrealizowano jeden rzeczywisty odbiornik kamery/ToF na obracanej części pitch oraz wspólny otwarty nośnik Pi z czterema zintegrowanymi podporami 3 mm. Nowy P02 zachowuje cały materiał źródłowej podłogi i osiem H01; dodaje dwa boczne gniazda nad kupną bazą. Zestaw PCA–E1 pozostaje cały, teraz poprzecznie; jego nowe podpory, podobnie jak BUS/AMP/operator/głośnik, nie są jeszcze wykonane.

FFC200: osobne podejścia i zmienne proste odcinki magazynowania; dziewięć pozycji zachowuje całe200 z10końcami raz, wewnętrzny promień co najmniej18,307 wobec wymaganego12,5. Nazwane sprawdzenie pełnego profilu przy688/odbiorniku daje minimum1,988mm. To sprawdzenie próbek, nie ciągły ani fizyczny PASS. DATA500 jest połączoną konstrukcją448+52raz zR30 i konserwatywną pojemnościąØ6,8; aktualna trasa omija PCA o co najmniej6,608mm. Poprzednie negatywy zachowano.

## Montaż przez dwie osoby

1. P00/osie/gwinty przed drukiem pustej bazy. Oryginalne P01 i osiem pełnych H01 pozostają; bez wiercenia kupnych części.
2. Założyć P02 z dwoma bocznymi gniazdami. Zamocować nośnik Pi DWOMA pełnymi M3x12, czterema podkładkami7x3,2x0,5 i dwiema nakrętkamiAF5,5/h2,4 od strony+Y, przed bankami/Pi. To zapotrzebowanie NIEPOTWIERDZONE, nie stwierdzenie posiadania.
3. Wsunąć cztery pełne nakrętki i dolne podkładki Pi do otwartych kanałów; założyć Pi na podporach3mm, używając zachowanych czterech pełnych M2,5x8 z górnymi podkładkami. Nie dokładać drugiego dystansu. Przymiarka rzeczywistych bezpiecznych pierścieni PCB i cienkiej krawędzi kieszeni przed dokręceniem.
4. Złożyć zachowane yaw/pitch/łożyska/horny. Odbiornik pitch nasunąć na rzeczywisty drukowany journalØ8, nie na wyjście MG. Zachowany CAŁY zestaw M2x20 odwrócony: łeb od+X, nakrętka/podkładka podawane z boku+Y; klucz4mm i sterownik przed Pi/bankami. Dwa pełne zestawy kameryM2x12 i dwa ToFM2x10 pozostają. Zegar kamery180 musi być uwzględniony w późniejszym obrazie; ROS/power teraz nie uruchamiano.
5. Pozostałe moduły i całe lutowane PCA–E1 instalować otwarcie dopiero po wykonaniu ich aktualnych podpór. Włożyć rzeczywiste DATA/POWER/FFC, sprawdzić zatrzaski i chłodzenie, ułożyć zapas przed osłonami. Nie udawać gotowych podpór lub odłączenia lutów.
6. ToF4/JR/POWER wymagają jeszcze połączonego planu kotew, użytecznego ruchu i aktualnych górnych budżetów. Nie zamykać robota z tymi lukami. Cztery pełne MTA0100335 wymagają jednej właściwej próbki. Plastikowe ogony opasek człowiek może przyciąć dopiero po zablokowaniu; nie dotyczy przewodów/FFC/JR/taśm baterii.

## Druk i granice

Każdy z3STL jest zamknięty po ponownym odczycie i mieści się w256 z8mm łącznej rezerwy. LokalnyZ0, natywna orientacjaXYZ; podpory pod mostkami/wspornikiem i dachem kanału według próby, bez slicera. Nie drukować całego kota. Nazwa obiektu P02 zawierająca THREE jest historyczna: aktualny STL **P02-floor-two-side-receivers-FIT.stl** ma DWA boczne gniazda, bez trzech nowych otworów w podłodze.

Obrysy głowy/korpusu/karku są PROPOSED_NOT_PRINT_NOT_MASS. Cztery PNG pokazują tę samą geometrię, także rzeczywiste wystające części; obejrzano pełne kadry. Sylwetka nadal nieprzyjęta: beczkowaty korpus/prosty brzuch/tylne występy i lokalny kark wymagają dalszej wspólnej decyzji. Nie jest to zaakceptowany zamknięty kot Oli.

Dodano rzeczywisty materiał potrzebnych mocowań, nie wykazano spadku masy całego robota. Dokładne wartości w current-material-effectivity-and-mass.json. Stare wycofane, niewybrane ramy nie są zaliczone jako oszczędność. Udźwig/masa rzeczywista/wytrzymałość pozostają nieznane. physicalPASS=false, actualfit/cut/slack=NULL.
