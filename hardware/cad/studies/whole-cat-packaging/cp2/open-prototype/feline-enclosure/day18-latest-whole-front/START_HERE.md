# Cały przód z wysuniętym gimbalem i pionowymi bankami

**Decyzja do odbioru.** Zachować do dalszej oceny podparcie łożysk yaw od tyłu i dwa boczne rzędy pełnych zespołów MTA. Odrzucić obecny przydział miejsca wiązkom. W pozycji neutralnej dodatni korytarz ToF trafia w pole głośnika, a dwa ujemne pola zapasu JR zajmują miejsce ReSpeaker. Montaż zamkniętego kota pozostaje otwarty.

[Przód](whole-front.png) · [Bok](whole-side.png) · [Ujęcie 3/4](whole-three-quarter.png) · [Wnętrze](whole-interior.png) · [Model FreeCAD](whole-front.FCStd)

Cztery widoki pochodzą z tego samego stanu geometrii. W widoku wnętrza zdjęto sześć osłon i schemat malowania oczu oraz pokazano proponowane miejsca wiązek. Osie i linie siatki są częścią widoku FreeCAD. W ujęciu 3/4 widać wyposażenie przez otwarty kark i otwory czujników. Z boku wystaje monitor pod głową, wzdłuż podłogi widać wyposażenie i podpory. Tułów zachowuje długi płaski bok. Zamknięcie i sylwetka Oli wymagają dalszej pracy. [Zapis ujęć](whole-view-receipt.json)

## Co rozstrzyga próba

- Kompletny gimbal i czaszkę wysunięto o 24 mm. Wstępna rama wchodziła w ruchomy widelec przy yaw +20° na 251,21 mm³. Obecna tylna kolumna przenosi obciążenie z gniazda łożysk do wspólnej podłogi. W próbkach −20°, 0°, +20° minimalny odstęp widelca wynosi 2,618 mm, pełnej śruby poprzecznej 7,100 mm i najbliższej podkładki 6,500 mm. Odbiór ciągłego ruchu i nośności pozostaje otwarty. [Pierwsza próba](front-frame-check.json) · [Obecne sprawdzenie](occupied-front-gate.json)
- Dwanaście pełnych oprawek z ATO i dwiema końcówkami TE jest ustawionych pionowo, bezpiecznikami do góry. Panele z oknami nominalnymi 22,2 × 11,3 mm o grubości 2 mm są rozdzielone między przednią i tylną podłogę. Wszystkie cztery mają materiał wspólny z docelową podłogą. Ich ostateczne scalenie z drukiem, podparcie kołnierzy, dostęp do TE i ruch zacisków wymagają kwalifikacji. Wybrane P_REAR i F_AUX zachowują wzajemne położenie dla krótkiego fabrycznego ogona. [Wynik ramy i paneli](frame-and-panels.json)
- FFC200 ma w dziewięciu pozach po 190 mm wolnego odcinka i 10 mm łącznie na oba końce. Najmniejszy wyliczony wewnętrzny promień profilu na łukach to 18,30 mm przy wymaganych 12,5 mm. Przy yaw +20° i pitch +10° naroże taśmy w XYZ = (−86,41, −8,27, 150,56) mm wchodzi w ruchomy tył głowy. Potrzebne jest wspólne przejście od optyki przez tył głowy do stałego złącza Pi. [Rodzina pozycji](front-flex.json) · [Świadek kolizji](occupied-front-gate.json)
- Cztery HELU z zachowanymi padami JP3.2/6/3/4 wymagają w tej próbie 215 mm na ruchomy nawrót i planowo 535 mm na żyłę wraz z końcami i stratą. W neutralnej pozycji naroże profilu 10,4 × 2,9 mm na prostej znajduje się w zajętej przestrzeni głośnika przy XYZ = (−87,73, 37,65, 106,55) mm. Przy ruchomym chwycie wykryto również wejście w tylną skorupę głowy. Te świadki wystarczają do odrzucenia korytarza. Wynik dotyczy tej alokacji i jej punktów kontrolnych. [Sprawdzenie obsady](occupied-front-gate.json)
- JR yaw 250 mm, JR pitch 250 mm i istniejące przedłużenie 300 mm mają oddzielne pola. Pętle korpusowego JR yaw i przedłużenia trafiają w pole ReSpeaker już neutralnie. Otwarty pozostaje ciągły korytarz do pełnej pary wtyczek i trzech stałych złączy przedłużenia oraz pomieszczenie całych jednostek. Położenie wyjść z serw jest projektowe. [Pola jednostek JR](JR-space-plan.json)

## Kolejność montażu dla dwóch osób

1. Przy otwartej podłodze przygotować dolne zestawy mocujące. Jedna osoba podaje czop od dołu, druga osadza widelec i pełną śrubę poprzeczną. Zrobić to przed bankami, modułami i pokrywami. Droga narzędzia przez całą operację pozostaje do potwierdzenia.
2. Przy dostępnym spodzie paneli osadzić oprawki od strony kołnierza, skontrolować zatrzaski i nasunąć obie całe końcówki TE od dołu. Osadzić banki na podłogach. Lutowany PCA–E1 zachować w całości.
3. Przed osłonami ułożyć przewody z fabrycznymi końcami i odciążeniem przy ich właściwych właścicielach ruchu. Ten etap wymaga zmiany wspólnego rozmieszczenia audio i wiązek. Zamknięcie następuje po wykazaniu miejsca na te grupy oraz pokrycia karku w ruchu.

## Zakres następnej decyzji

Do wspólnej recenzji trafia jedna propozycja. Zachować odzyskane miejsce przy podstawie gimbala. Rozważyć przeniesienie całego głośnika i ReSpeaker do stałej strefy dostępnej od góry przy równoczesnym rozmieszczeniu ich końców, portów akustycznych, DATA500 i chłodzenia. Ustalić przekrój prowadzący przez głowę, bark i korpus przed rozwijaniem chwytów. Zmiana położenia audio jest hipotezą do sprawdzenia.

Na obrazach pozostają rzeczywiste obecne otwory twarzy. Do następnej maski dostępne są lokalne bazy modelowe kamery oraz obu okien ToF. Stara bryła rezerwy ToF 14 × 26 × 26 wymaga przeniesienia do bieżącej pozy sensora przy projektowaniu osłony. Źrenica kamery, czynne okna TX/RX i promienie narożne są nieznane. Potrzebna będzie próba rzeczywistych czujników. [Bazy optyczne](../day18-optical-local-apertures/README.md)

Próby fizyczne, rzeczywiste długości po ułożeniu i cięcia pozostają nieustalone. PhysicalPASS = false. Odbiór pozostałych mocowań, czterech pełnych MTA0100335, zamknięcia i gotowości całego kota pozostaje otwarty.
