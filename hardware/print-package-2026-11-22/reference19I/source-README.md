# Grupy i masa do niskiego kota — 19 listopada

Mapa obejmuje wszystkie ilości z 57 wierszy wyboru oraz 7 dodatków po jednej
sztuce. JSON wiąże grupy ze źródłami i SHA-256. Bazą odbioru jest d5baf5e6,
z wcześniejszym 8e4 i konstruktywnym 98. Nowe pozy wymagają sprawdzeń
zmienionych interfejsów.

| Grupa | Obsada do wspólnej alokacji |
|---|---|
| Baza i ruch | 12 ST3215, 3 MG92B, 3×608 i 1×688; obecne nogi; głowa yaw±20/pitch±10, ogonY |
| Energia nisko | 1 GEA223S30X6GT 106,5×35×21,5; 2 paski; monitor; pełne końce i droga wyjęcia |
| Ochrona | 12 pełnych MTA0300330+różne TE IN/OUT+ATO4A; 4 MTA0100335+MINIVAL10A; F0; 5 FHAC; S0/S1 z pełnym osprzętem |
| Rozdział | 4 WAGO615, 16 WAGO415, 8 inline2411, POST_F0; WAGO415 =15 bankowych+czynny PBAY_P_AUX |
| Sterowanie | Pi4+pełne porty/POWER/DATA/chłodzenie; BUS25514; MAIN4853; AUX4092; cały lutowany PCA–E1 |
| Głowa i audio | Kamera+ToF; BNO085, touch, AMP, głośnik, ReSpeaker; wszystkie po1; oddzielny USB_AUDIO i para BTL |
| Całe przewody | 3 JR300; MG250 osobno; 4 odrębne E2/JPWM225 nominal/220 dostępne z końcami; CSI200; DATA500 |

Niska otwarta tacka może otrzymać akumulator nisko, wspólny kompletny moduł
sterowania i ochronę wzdłuż boków. Założyć moduły, pełne terminale i wiązki
przed zamknięciem lekkich pokryw. Stare banki, pionowe wieże, ruszty i pozy
mocowań są zmienne. Obrys starego nośnika 250×194 nie ustala rozmiaru nowego
układu. Jedna pełna sztuka MTA0300330 z końcami ma zapisany obrys
71,43×21,85×28 w jednej orientacji. Pełne cztery MTA0100335 nadal wymagają
źródła/przymiarki; stare małe pudełka są placeholderami.

Pi85×56×26 reprezentuje rezerwę komponentów/chłodzenia/powietrza.
Rzeczywisty radiator i jego profil pozostają UNKNOWN. JSON oznacza osobno
materiał PCB, obwiednie źródłowe i pola instalacyjne.

**Pięć ograniczeń zmieniających układ**

1. Dziesięć końców FHAC ma osobno84,5–94,5 mm, z gołymi końcówkami już
   w długości. P_SYS–F_PI oraz P_REAR–F_AUX wymagają bliskiego wspólnego
   montażu i miejsca na pełny nadmiar; pozostałe kompozyty zachowują swoje końce.
2. Zachować12 pełnych MTA+TE, a4 MTA0100335 pozostawić jawną zależnością od
   jednej kompletnej próbki/źródła. E2/220 i FHAC/84,5 dotyczą innych jednostek.
3. PCA–E1 przenosić razem; zachować czynne WAGO16, pełne AUX9,5 mm,
   dostęp do JP3/portów i izolację.
4. Pełne DATA500 z dwoma bootami26, osobne POWER/K1474/Delock i USB_AUDIO
   układać wraz z chłodzeniem i zatrzaskiem CSI. Długość USB_AUDIO jest UNKNOWN.
5. CSI200 ma10 mm na oba końce raz; ToF4×Ø2,1 wymaga ruchomego R31,5.
   MG250/JR300 pozostają odrębne; wyjścia/stub11,45 są projektowe.
   Nowe pozy unieważniają stare podziały tras.

**Budżet masy**

12×69 =828 g ST jako robocze założenie dzisiejszego zlecenia; MG3×13,8
=41,4 g i bateria174 g z cache. Razem1043,4 g. Pozostają wcześniejsze
allowance180–400 g bazy/metalu,180–350 g płytek/chłodzenia/audio
i450–800 g ochrony/wiązek. WAGO111,6 g jest już wewnątrz ostatniej grupy.

Masa robocza wynosi **1853,4–2593,4 g + P**, gdzie P obejmuje zachowane
drukowane nogi i nowe podpory/osłony, z wyłączeniem bazy już w allowance.
P pozostaje do nadania po nowej geometrii. Przykładowe P800 daje2,65–3,39 kg;
P1000 daje2,85–3,59 kg. To scenariusze. Stare modele PETG1,28/1,78 kg
służą porównaniu. Masa fizyczna, COM i nośność pozostają nieustalone.
