# Mapa mocowań — stan do przymiarki 15.11.2026

To aktualizacja starego planu grup, bez ponownego doboru części i bez potwierdzania zakupów. Szczegółowa lista wybranych części jest w source-lists/selected-components.csv. Pole stock_confirmed=False w historycznym CSV znaczy brak potwierdzenia zapasu w tamtym rejestrze, a nie ustalenie, że użytkownik części nie ma. Trzy MG92B są na głowę/ogon; nie są już zamontowanymi napędami WAVEGO.

| Moduły / funkcja | Aktualny stan mocowania |
|---|---|
| 12×ST3215 i WAVEGO | Baza ruchu pozostaje; rzeczywista rewizja/masa/ruch to FIT1. P00 przed większymi drukami. |
| Pi4B | Cztery integralne słupki i pełne M2.5×8 w P10/P12; nominalnie odebrane, fizyczna próbka i rzeczywiste końce otwarte. |
| BUS Waveshare25514 | Osobny mostek P13 i wolne nominalne chłodzenie nad Pi; retencja samej płytki BUS nadal planowana, nie mylić z przykręceniem mostka do ramy. |
| PCA9685 + lutowane E1 | Wspólna półka przewidziana; właściwe mocowanie płytki/końce nadal otwarte. Nie odpinamy lutów w modelu. |
| MAIN4853 + AUX4092 | Dolna stopa odrzucona. NOWA cała otwarta warstwa na górnej belce P11: pełne MAIN/AUX i metale mają lokalnie sprawdzoną przestrzeń, lecz INITIAL ASSEMBLY HOLD. Dostęp do M2/root przecina integralne P11; oś root pod AUX blokuje automatyczne preassembly. Potrzebna konkretna wykonalna kolejność lub prawdziwy podział nośny P11. Bez nowych STL; kupon nie oznacza gotowego mocowania. |
| BNO085 | Dostępne miejsce/półka do zaplanowania; rzeczywiste bezpieczne oparcie i retencja otwarte. |
| MAX98357A + głośnik | Zachowany układ i połączone miejsce audio; przykręcenie konstrukcji półki nie mocuje samego wzmacniacza ani kosza głośnika. Rzeczywisty kosz/otwory do przymiarki, bez nacisku na membranę. |
| TTP223 + ReSpeakerLite | Dwie osobne szyny, touch zostaje, mic może być demontowany; mocowania samych PCB i rzeczywiste porty nadal otwarte. |
| Bateria +2 paski | P19, pełne oparcie, dwa rzeczywiste okna kotwiące i przedni/tylny węzeł ramy odebrane nominalnie. Prawdziwa klamra, tkanina i nośność do próbki; ogniwo przed zamknięciem P12. |
| 12×MTA0300330 +TE IN/OUT +ATO | Dwa rzędy zachowane. Źródłowy kołnierz/zatrzaski; jedna próbka panelu, nie gotowe dwie listwy. |
| 16×WAGO415 +4×615 +POST_F0/412 | Zachowana liczba/rola i miejsca. Wspólna retencja korpusów/otwarte dźwignie i porty do realizacji po jednej reprezentatywnej przymiarce; osobnych adapterów DIN nie wybrano. |
| F0 +5 małych FHAC | Zachowane pełne fabryczne końce i ochrona. Wspólny przedni/tylny uchwyt planowany; krótki niechroniony odcinek zasilania do pomiaru na rzeczywistych końcach. |
| 4×MTA0100335 ochrony nóg | Części i cztery niezależne fabryczne220 zachowane; wspólna retencja jeszcze niezrealizowana. |
| S0, S1 i monitor | S0 ma odebrany nominalny panel podstawy; rzeczywisty interfejs do FIT. Wspólny montaż S1/monitora nadal planowany. |
| Głowa: 2×MG92B, kamera/ToF, łożyska, CSI/E2 | Miejsce i wizualna propozycja są; nośnego korzenia głowy nie ukończono. Najpierw jeden prawdziwy róg/serwo i jego wymiary, potem mostek. |
| Ogon: 1×MG92B i 608 | Otwarty korzeń P07 do przymiarki, bez odbioru pełnego napędu/rogu. |

Nie usuwamy wyposażenia dlatego, że mocowanie jest otwarte. Pierwsza próba ruchu może odbyć się bez osłon, ale wymaga stabilnego rzeczywistego zamocowania elektroniki i sprawdzenia ochrony; ten pakiet nie zezwala na zasilanie luźnych modułów.
