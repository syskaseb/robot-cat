# E4: jedna mapa połączeń wybranego prototypu

Zestaw R35 zachowuje mechanikę i wszystkie ilości R34. Zero nowych STL,
bez nowej trawionej PCB, firmware, ROS, zakupów lub zasilania sprzętu.
Schemat nominalny to przygotowanie do montażu, nie wynik prób fizycznych.

`01-power`, `02-drives`, `03-logic` (SVG i PNG) pokazują zasilanie, masy,
12 ST3215 i 3 MG92B, sterowanie, rozłączanie oraz elementy lokalne.
Dokładne końce są w `connections.csv` / `netlist.json`; `pinouts.csv`
łączy model, pin/oznaczenie, kierunek patrzenia i źródło. `passives.csv`
obejmuje wszystkie 21 elementów. `cassette-pad-map.json` zachowuje
współrzędne i ścieżki wybranego Perma-Proto1608, bez nowego layoutu.

## Ważne identyfikacje

Adafruit815 revC: Pi3V3 trafia do JP3.2 VCC, nie JP3.1 V+.
Pi fizyczne1/3/5/6/11 to 3V3/SDA/SCL/GND/BCM17-OE. Pozostałe pozycje
obudowy1992 puste, zwłaszcza 5V2/4. Przewody GPIO to wybrane Pololu1871
600mm26AWG, nie stary model300mm. Wtyk nie jest kluczowany: oznaczyć pin1.

Kanały815 trzeba rozpoznać po oznaczeniu kanału i S, nie kolejności JP:
CH0/1/2 = JP2.10/.7/.4. `pca-source-trace.json` przechodzi od pinów
scalaka PWM0/1/2 przez rezystory producenta do rzeczywistych padów.
Robocze JP1.1/.4/.7 odrzucone: to PWM7/6/5. Rezystory220Ω na815 nie
zastępują R1–3 po wyjściach bufora U1.

JPWM: źródłowa obudowa430250200, modułowa430200201; obie oznaczone
1=wejście regulatora/czerwony, 2=masa/czarny. Orientować wg numerów
gniazd na każdej obudowie, nie „lewa/prawa” z przeciwnych stron.
Wybrane cztery fabryczne przewody Molex zapisane przy odpowiednich końcach.
Nie wykonywać ręcznego zacisku luźnej żyły0,5mm² w dawnych kontaktach.

ST3215: zachować fabryczny kluczowany wtyk przy serwie. Biały=DATA,
czerwony=V+, czarny=masa, wg zdjęć producenta z kablami i oznaczeniami S/V/G.
Numeracji H3 adaptera nie przenosić na lustrzany widok gniazda serwa.
Drugie gniazdo każdego serwa puste, inaczej można ominąć indywidualną wkładkę.
Na BUS H3:1D/2V/3G; usunąć przewódV ze źródłowej wiązki D/G, izolować go.
BUS zasilany logicznie przez USB przy przełącznikuB; wejścia DC/power/UART NC.
Nie zasilać silników przez USB ani podłączać całych pęków między serwami.

MG92B: fabryczny JR, czerwony środkowy=V+, brązowy=masa, żółty/pomarańczowy
skrajny=PWM. Oba końce przedłużenia586761 dopasować funkcjami/kolorami,
nie utożsamiać odbicia zdjęcia z innym pinoutem. R7–9 przy stronie serwa,
PWM do tej samej masy za R1–3. Zachować wybrane recepty głowyR28 i ogonaR29.

U1: właściwa strona adaptera575070 ma raster0,65mm; nominał1:1 pozostaje
warunkowy względem dostarczonego adaptera. Widok TI jest OD GÓRY układu.
L78L05ACZ ma oddzielną regułę OD DOŁU:1OUT/2GND/3IN. Nie mostkować
wyjść MAIN5,1V, AUX6V, PWM5V ani logicznego3,3V.

## Rozpinanie i granice wyników

Przed rozpięciem odłączyć BAT i wszystkie USB, nie tylko S1. GPIO rozłącza
się całą obudową1992; BUS fabrycznym USB; głowę/ogon przy JR i opisanych
końcach WAGO po uwolnieniu opasek. JPWM rozpiąć na stole po uwolnieniu
P_REAR.4/G_TAIL.3 i mocowań, wg wybranego E2; nie wyciągać za luty.
Fusy wyjmuje się przy odłączonym źródle. Nie wpinać multimetru jako zwarcia.

S0OFF usuwa zasilanie robota, ale P309 na balansie nadal jest podłączony.
S1OFF pozostawia Pi i logikę adapteraUSB, odłącza15napędów oraz PWM5.
U1/OE HIGH ma poprzedzać wyłączenie silników; po S1ON wymagana świeża ramka
i świadome enable. Nie deklarować sprzętowego restart-latch ani zerowego
czasu zaniku, izolacji sygnałów czy braku przepływu w stanach przejściowych.

P309 zdjęcie dokładnego SKU pokazuje tył: piny po lewej, od dołu minus,
1S/2S/3S. Schemat ogniw:B0/B1/B2/B3 do tych czterech oznaczeń; wyższe NC.
Fotografia dokładnego pakietu pokazuje G-Tech, ale NIE dowodzi kolejności
odczepów ani pinu ID. Nie wciskać nieustalonego G-Tech w P309 na podstawie
koloru lub czterech wybranych otworów. Fizyczną identyfikację/połączenie
balansu uwzględnia otwarta W5; schemat15napędów jej nie zamyka.

E3 pozostaje otwarte (źródło, fabryczne przewody, końce przed wkładkami,
obciążenie przełącznika/przetwornic). W5, K2/K3 i A2/A3 osobno otwarte.
Sprawdzenia grafu nie symulują zwarcia, upływów, termiki ani impulsów.
Nie są KiCad ERC. Phase2: dostarczone modele/oznaczenia, ciągłość/polaryzacja
bez baterii, pasowania i kontrolowane próby zasilania/ruchu. Phase3: ROS2.

Odtworzenie: `python tools/electronics/connection_map_e4_r1.py`.
Zatwierdzenie po obejrzeniu wyników: ten sam skrypt z `--seal`.
Przed zapisaniem pakietu skrypt sprawdza wszystkie piny R34 i zachowanie
71zadań/110PETG/4próbek/113pozycji ilości. Nie zmienia dawnych pakietów.
