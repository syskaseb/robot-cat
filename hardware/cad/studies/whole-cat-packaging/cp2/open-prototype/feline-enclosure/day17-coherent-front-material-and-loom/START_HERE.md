# Przód kota — rzeczywisty nośnik i przejścia, wynik częściowy

Otwórz **coherent-front-material-and-loom.FCStd**. Jest to nowa kopia źródła 751e0f93; źródła i poprzednie paczki pozostają zamrożone. Nie jest to wydanie całego kota ani zestaw STL do drukowania.

**Wynik ostatniej bramki: HOLD pokrywy HC_BACK_UPPER.** Pełny FFC po zmianie ramy jest od niej oddalony o3.725..3.754 mm w trzech sprawdzonych pozycjach, lecz nadal przecina górną pokrywę: wspólne objętości4.048051/92.565841/131.633953 mm³. Sam tylny kanał nie wystarczył. Następna decyzja dotyczy funkcjonalnego podziału centralnego dachu głowy i stałej osłony barku z rzeczywistymi mocowaniami, nie kolejnego przesunięcia przewodu. Nie zgłoszono wszystkich dróg jako niemożliwych.

Trzy nowe części nośnika to23.916955 g pełnego modelowego PETG. Ten sam zbiór zastępowanych funkcji plus nowe pełne mocowanie zasilania zmienia modelowy wynik289.328871→294.785802 g, czyli+5.456931 g; to nie masa całego kota. Środek masy wyłącznie tego zmienionego podzbioru Z91.72517→91.75365. Podniesienie kupnego Pi i osprzętu o4 mm ma dodatkowy koszt momentu4×ich rzeczywista masa; mas tych nie wymyślono.

Wykonano trzy osobne części: wspólny stały nośnik Pi/BUS/zasilania, zdejmowaną poprzeczkę E1 oraz izolujący docisk pełnego adaptera Delock60047 i zachowanego buta K1474. Pi pozostaje poziomo, kamera obrócona optycznie o 180°, BUS pionowy, cały lutowany PCA/E1 pozostaje razem. Rzeczywiste pełne mocowania wymusiły podniesienie całej stałej warstwy Pi o 4 mm: PCB145..146.6, CSI[-80.5,-16.5,152.1]. Minimalna wysokość wynikała z pełnego mocowania przeciw ruchomej obudowie głowy, nie ze skracania śruby. Zmieniły się wszystkie porty Pi, docisk zasilania, podpory i koniec FFC; pozostałe moduły nie zostały automatycznie przesunięte.

Dwa istniejące oparcia A17 mają po 37.1608 mm² wspólnej nominalnej powierzchni z nowym nośnikiem; wspólna objętość rozdzielnych części wynosi 0. Zakończono stare, niezbudowane funkcje podpory jednego narożnika Pi i starego mostka BUS/E1. A17 zachowuje podłogę, źródłowe osie i korzeń głowy. Jego stara stopa Pi została funkcjonalnie zastąpiona czterema nowymi podporami; przy czynnym wsporniku AMP wykonano lokalną ulgę na pełny węzeł BUS. Pozostały rzeczywiste połączenia materiałowe; nie sklejono oddzielnych wydruków ani części kupnych. Mały narożny odcinek podłogi AMP ma lokalnie 0.75 mm, środkowe pełne oparcie pozostaje grubsze: wymaga próby obciążenia i nie jest dowodem wytrzymałości.

Pełne metalowe zestawy: 4×M2.5x8 + 8 podkładek + 4 pełne nakrętki; 2×M3 stożkowe16 + 2 dolne podkładki + 2 pełne nakrętki; 4×M2 stożkowe10 + 4 przednie podkładki + 4 pełne nakrętki BUS; 2×M2x16 + 4 podkładki + 2 pełne nakrętki docisku zasilania. Są to zapotrzebowania NEEDED_UNCONFIRMED, nie potwierdzony stan magazynu ani zakupy. Długość śruby stożkowej obejmuje łeb. Zastąpione stare zestawy są zachowane jako wyłączone referencje. Surowa odległość starych podkładek BUS/AMP 1.124228857 mm pozostaje w historii; po zmianie kompletnego węzła najbliższy sprawdzony nowy łeb/metal AMP ma 1.752200855 mm.

W ramie czujników są rzeczywiste kanały kamery i ToF oraz dwie zastępcze poprzeczki. Brakująca objętość źródła poza nazwanymi wycięciami: 0; nowe poprzeczki łączą się dodatnimi objętościami 44.8 i 93.19993 mm³. Zachowano górne lądy dwóch mocowań kamery, ramię gimbala i dolny wspornik ToF. Ruchoma górna pokrywa ma przejście otwarte do tylnej krawędzi; jej boczne mocowania pozostają. **Stała osłona łącząca bark z tym przejściem nie jest jeszcze wykonana.** Nie oznaczamy otwartej szyi jako zamkniętej obudowy.

## Kabel i pozostałe grupy

FFC to nadal jeden 200 mm, pełny profil16.8×1.8, 10 mm na oba końce tylko raz, projektowe R wewnętrzne12.5 oraz zakres yaw±20/pitch±10. Nowa warstwa została przeliczona tym samym prawem zmiennego łuku; 9 pozycji to próbki, nie dowód całego ruchu. Osobno są 3 pełne pola do miejscowego sprawdzenia ramy i pokrywy. Pełna wcześniejsza rezerwa chłodzenia Pi pozostała jako rezerwa komponentów/powietrza, nie została uznana za bryłę dostarczonego radiatora. Nominalne pola złączy i czteromilimetrowa rezerwa małych elementów zostały sprawdzone osobno. Potrzebna jedna rzeczywista przymiarka Pi + chłodzenie + zatrzask/FFC + adapter zasilania; brak osobnej pozycji radiatora w CSV nie dowodzi jego braku.

Cztery przewody ToF mają połączenie regionalne od rzeczywistego rzędu padów do istniejącego rejonu PCA/E1: fanout18.8 mm przechodzi w grupę10.4×2.9; stałe zakręty R38 zostawiają co najmniej32.78 mm dla profilu wobec wymaganego R31.5. Bezpośrednia granica geometryczna długości z wielokąta kontrolnego krzywej i łuków, a nie cięciwy, wynosi maks.390.171 mm na rdzeń razem z 20 mm prac końcowych; projektowe zaokrąglenie395 mm. Podział kolorów i rzeczywista dostępność wspólnych szpul pozostają do związania. **Pełny skręt czterech przewodów i cała ciągła rodzina ruchu nie są zakwalifikowane.** Rząd padów nie oznacza wymyślonego nowego złącza ani wolnych pinów. EXT011/012 to istniejące LOGIC3V3/GND; EXT013/014 to PI.H3/SDA i PI.H5/SCL.

JR250 obu serw i istniejący JR300 są oddzielnymi pełnymi jednostkami; yaw ma stały korpus, pitch porusza się tylko z yaw. Ich całe zajęte ułożenie i nadmiar pozostają projektem OPEN. Tak samo pełne DATA Lanberg500 z min. projektowym R30: wcześniejsza spirala R25 nie jest zaakceptowaną drogą i nie jest aktualnym dowodem długości.

POWER jest odrębny od DATA. W078 to czerwony210 projektowy odcinek z tej samej pary K1474: SPLICE_PI.18→MAIN.VIN, lap8 + pełne12 przy MAIN tylko raz. W079/W080 to MAIN.VOUT/GND→VBUS/GND adaptera. Nowe ustalenie adaptera kończy się rejonami[-74.3,-37.15,148.2]/[-74.3,-40.65,148.2]; rzeczywiste drogi i dekrementy jednostki wymagają jeszcze wykonania. Nie otrzymują kredytu z dawnych150/250/350 ani z pięciu par Pololu600. Nie dodano przedłużenia ani połączenia.

## Kolejność dla dwóch osób

1. Pusta baza i aktualna wersja A17 po P00/zgodności prawdziwych osi. Cztery niezwiązane modele MTA0100335 pozostają wymagane; nie są zastąpione fałszywym pudełkiem.
2. Podtrzymać wspólny nośnik na dwóch rzeczywistych górnych lądach A17. Dolne podkładki i nakrętki korzeni ładować przed bankami.
3. Cały lutowany PCA/E1 założyć przy zdjętej poprzeczce. Poprzeczka i dwa pełne stożkowe M3 przed założeniem Pi; nie odpinać wirtualnie lutów E1.
4. BUS i cztery kompletne stożkowe M2 montować od -Y przed F_PI/bankami. Pi i jego cztery pełne zestawy zakładać od góry. Docisk zasilania osobno, bez przenoszenia siły przez żyły.
5. Podłączyć prawdziwe końce i ręcznie ułożyć pełne jednostki kabla przed późnymi pokrywami. Założyć ramę czujników i ruchomą pokrywę z otwartym przejściem. Zamknięcie stałej osłony szyi czeka na rzeczywiste grupy DATA/JR/POWER i pełną kwalifikację bightu.

Powyższa kolejność jest rzeczywistą zasadą partingu, lecz pełne pola narzędzi/wprowadzania wszystkich modułów i ruchu po zmianach pozostają OPEN. Nie awansowano ich do próby fizycznej.

Nie wydano STL tej paczki: lokalne nośniki istnieją jako BRep/native, ale nie ma kompletnej kwalifikacji całego stocku, narzędzi i zamknięcia. Bez zasilania/drukowania/cięcia. Cały kot, wygląd, fizyczny PASS=false; rzeczywiste cięcia, luz i przymiarki=NULL. Następne działanie ma domknąć te nazwane interfejsy w tym samym układzie, a nie rozpoczynać nowy wariant bryły.
