# Aktualna próba osłon i wspólnych interfejsów

Model jest roboczym montażem do dalszej przymiarki, NIE gotowym zamkniętym kotem. Nie włączaj zasilania na podstawie tego pakietu. Części kupne i końce fabryczne zachowano. Nie wykonano fizycznego druku, cięcia ani przymiarki.

Otwórz `whole-floor-cowl-head-tail.FCStd`. Stan źródłowy z poprzedniego pakietu pozostał nietknięty. Aktualne części i dopuszczone małe próby wskazuje wyłącznie `current-print-index.json`; stare HB_* i wcześniejsze maski są alternatywami wycofanymi. Plik BRep nie oznacza dopuszczenia do druku.

Co rzeczywiście powstało:

- Dno elektroniki tworzą istniejące P02/P03. Cztery nowe wydrążone osłony obejmują boki, końce i górę. Zastosowano kontrolowane przekroje, 5 zachowanych mocowań dolnych oraz rzeczywiste połączenie przednich połówek i dwa połączenia boków M2. Szósty stary korzeń przy GPIO wycofano jako niezbudowany; funkcję przejmuje górne połączenie połówek.
- N1 ma rzeczywiste wzmocnienia w pięciu miejscach dawnych połączeń wyłącznie krawędziowych. Pierwsza kontrola dała zamkniętą siatkę; bieżący eksport po dodaniu podpór jest oceniany oddzielnie w indeksie.
- Trzy wydrążone części głowy mają poprawne bryły, rzeczywiste cztery mocowania do ramy czujników oraz dwa połączenia maski. Ciemne oczy i wąskie złote obrzeża to propozycja malowania powierzchni, NIE nowe kupne oczy ani osobne wydruki.
- Ogon ma zachowany CAŁY poprzedni korzeń, oś Y i nową wydrążoną końcówkę. Dla ±15° podano trzy pozycje i ograniczony ciągły warunek przestrzeni wyłącznie nowej końcówki. To nie potwierdzenie całego mechanizmu w ruchu.
- Wspólny panel operatora ma dwa rzeczywiste korzenie w ramie i pełne zestawy śrub. Przełącznik S1 otrzymał jawnie nominalną płaszczyznę montażu, pełną konserwatywną obudowę, trzpień i dźwignię. Monitor przesunięto jako całą część o 2 mm w X; jego nakrętki znajdują się na zewnętrznych uszach.
- Odbiornik dotyku ma rzeczywistą wspólną podporę i zdejmowaną tacę. Głośnik ma wspólną regulowaną ramę odbiorczą z połączeniem do dolnego wspornika MTA. Bez próbki głośnika nie wolno dokręcać go przez membranę, zawieszenie ani magnes.

## Montaż przez dwie osoby, bez zasilania

1. Najpierw P00 i zgodność ośmiu osi/rewizji bazy. Bez wymuszania dopasowania, wiercenia i gwintowania kupnej ramy.
2. Jedna osoba podtrzymuje ramę, druga osadza pełne śruby, podkładki i nakrętki przed zabudową modułów. N1/N5 są nośne; cienkie osłony nie zastępują podpór baterii ani głowy.
3. Wstępnie przełóż obie CAŁE taśmy tekstylne 200 mm. Bateria 35 mm nie przechodzi pionowo przez otwór 30 mm: początkowy montaż przed zamknięciem P12. Późniejszy demontaż jest częściowy, nie szybki serwis.
4. Montuj pełny lutowany zestaw PCA/E1, płyty i pełne jednostki bez wirtualnego rozpinania lutów. Panel S1/monitor przygotuj na stole, połącz do ramy przed bankami i późnymi osłonami. Nakrętki i podkładki wsuwa się rzeczywistymi otwartymi dojściami.
5. Obudowy MTA0300330: nominalny panel 2 mm i otrzymana próbka. Pełne TE/ATO pozostają; końce prowadź przed zamknięciem górnego poziomu. Nie utożsamiaj 4 MTA0100335 z 8 WAGO2411 ani z 4 jednostkami E2/JPWM.
6. BUS/MIC montuj przed tacą TTP. Do późniejszego zdjęcia mostka najpierw odkręć tacę TTP, zachowując jej przewody; rzeczywisty zapas do odłożenia wymaga sprawdzenia. Brak zgody na wirtualne odlutowanie E1.
7. Głowę złóż wokół mechanizmu: dolna i górna część osobno, fabryczne rogi/śruby i łożyska zachowane. Maska na końcu. Nie poruszaj siłowo: pełny ruch nowych osłon i prowadzenie przewodów nie są odebrane.
8. Wiązki ułóż ręcznie przy otwartym korpusie. Dopiero po zamocowaniu opasek człowiek może zgodnie z wcześniejszą decyzją odciąć niewykorzystany PLASTIKOWY ogonek; nie przewody, FFC, JR/Molex ani taśmy tekstylne.
9. Osłony zakładaj na końcu, po sprawdzeniu wszystkich rzeczywistych końców, chłodzenia, przełączników i braku zaciskania przewodów. Aktualny pakiet NIE zamyka tych warunków.

## Co nadal jest otwarte

- FFC 200 mm: rzeczywisty połączony tor, kontakt/skręt i użyteczny zapas przy yaw ±20°/pitch ±10°. Odrzucona droga 226 mm nie jest minimum. Nie wolno dopisać kabla ani zmniejszyć promienia/końców dla wyniku.
- ToF 4×OD2,1 i R31,5 oraz pełne JR: prowadzenie ruchowe, punkty chwytu i przestrzeń odłożenia; nie są potwierdzone samymi pustymi regionami.
- Cztery pełne MTA0100335 z pokrywą, uwięzią, bezpiecznikiem i oboma przewodami nadal wymagają jednej właściwej próbki. Nie mają wiarygodnego pełnego modelu liczbowego; ich zależne zamknięcie pozostaje otwarte.
- Pełna próba wszystkich nowych ścian, całego ruchu głowy i pełnego sprzętu oraz pozostałych jednostek fabrycznych nie jest zakończona. `current-only-functional-neighbor-gate.json` podaje rzeczywisty kursor, nie ukończony PASS.
- Bezpieczne obrzeża PCB, kosz/kołnierz głośnika, rzeczywiste nakrętki S1/rewizja/gwinty i pasowanie łożysk/rogów MG: celowane fizyczne przymiarki. Niezbudowane lub kolidujące połączenie nie jest oznaczane samym FIT.
- Wygląd nadal wymaga odbioru: twarz ma duży otwór na rzeczywiste pola optyczne, obok Pi pozostał funkcjonalny występ portów. Zdjęcia CAD nie są retuszowane. Nie deklaruję zgodności wyglądu z Olą.

Masa w indeksie to objętość rzeczywistego modelowanego PETG ×1,27 g/cm³, bez sztucznego założenia wypełnienia. Nie jest masą całego robota. Poprzednie 535 g dotyczyły odrzuconego kandydata obudowy i nie są przyjętą bazą oszczędności.

## Faktyczny wynik końcowy

Osłona przy pełnym nominalnym głośniku: 0,667674 mm < 1,25. Nowy drukowany uchwyt przenika osłonę na 136,689134 mm³. Korpus HOLD, bez STL głowy i korpusu. Bieżący N1 po dodaniu podpór ma niezamkniętą siatkę: BRep-only. Dawna zamknięta siatka dotyczy innej wersji i jest tylko diagnostyczna.

Cztery rzeczywiste STL do ograniczonych przymiarek: TAIL_ROTATING_HOLLOW_REAL_ROOT, RG_REAR_GRID_WITH_STEPPED_RECEIVING_CROSSMEMBER, OP_MONITOR_REMOVABLE_TOPKEEPER, TOUCH_REMOVABLE_SAFE_EDGE_TRAY. Zamknięte, dodatnie, ponownie odczytane; nie tworzą całego zestawu. Pozostałe wymagane podpory wskazano jako BRep-only; nie zastępuj ich starym STL o podobnej nazwie.
