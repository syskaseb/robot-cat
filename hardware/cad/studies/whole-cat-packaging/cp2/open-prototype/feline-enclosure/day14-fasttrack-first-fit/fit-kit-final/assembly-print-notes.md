# Zadany tylny węzeł — wynik jednej próby: HOLD wejścia załadunkowego

**Nie ma nowego odbioru zestawu do montażu.** Wypróbowano jeden cały węzeł: M3×50 z gniazdami nakrętki/podkładki oraz P06 łączący panel S0 i funkcję tylnej belki półki. Po pierwszej rzeczywistej blokadzie załadunku zatrzymano próbę; nie wykonano kolejnej wysokości, rodziny ani poprawki ukrywającej wynik. Nazwa folderu `fit-kit-final` nie oznacza zwolnienia druku do obciążonego montażu. Zaczynać można tylko od zachowanego wzornikaP00 i dotychczasowej przymiarki źródłowych ośmiu osi.

## Co wykazano

Właściwy pełny stos wynosi48,9 mm: boss1 +panel3 +słupek40 +rzeczywisty web2 +podkładka0,5 +pełna nakrętka2,4. ŚrubaM3×50 kończy się1,1 mm za nakrętką. Najbliższa rzeczywista pokrywa WAVEGO ma zmierzony odstęp4,0 mm/common0 do krytycznej śruby; wszystkie cztery pełne śruby są poprawne geometrycznie. Każda podkładka ma rzeczywiste oparcie29,931524 mm². Nie skrócono trzpienia, nie poświęcono zazębienia i nie rozluźniono1,25 mm. Łączniki pozostają zapotrzebowaniem nominalnym/NIEPOTWIERDZONYM, bez zakupu ani deklaracji magazynu.

## Co obaliło montaż

Pierwszy kanał od krawędzi przy(110,−73) przyjmuje pełny stos w ciągłym polu10 mm bez wspólnego materiału. Drugi, przedni dodatni przy(110,15), jest zablokowany przy samym wejściuX99: pełny profil nakrętki i podkładki zajmuje13,550717771 mm³ cienkiej części płyty. Świadek jest poprawną geometrią w `feed-entry-blocker.brep` i na `local-entry-HOLD.png`; dokładne granice X95,5..99 /Y11,5..18,5 /Z45,52..46,32. Sam wolny kanał i końcowe gniazdo nie zapewniają sposobu wsunięcia całego stosu. Wymagany jest prawdziwy interfejs załadunku pełnego profilu na początku tej drogi przed uznaniem całej kolejności. **Nie wdrożono tej kolejnej zmiany w tej porcji.** Dwa dalsze kanały oraz odbiór połączeń półki/sąsiadów pozostały nieodebrane po falsyfikacji.

## Wspólna funkcja półki — zbudowana, nieodebrana po falsyfikatorze

Stara NIEZBUDOWANA belka `Upper_frame_end_105` została jawnie zastąpiona integralnym mostkiem P06. Nowe dwa zamknięte gniazda mają pasujące szerokie końce szyn6×1,5 mm (zachowany przekrój9 mm² dawnej szyny3×3), podparcie od dołu i zamknięcie przeciw uniesieniu. Zmieniono tylko lokalne końce dwóch projektowych szyn i wierzchy dwóch projektowych słupków; kupne płytki, S0 z11częściami, rama, osie nóg i porty zachowały położenia. Jest to faktyczna jedna bryła panel/mostek/gniazda, z kontrolą zachowania zamierzonych składników, bez nazywania penetracji OWN. Te dopasowane szyny są odniesieniem przyszłej wspólnej ramy, a nie dodatkowymi wydrukami produkcyjnymi tego pakietu. Testy odbiorcze zamkniętych gniazd i sąsiadów nie zostały wykonane po pierwszym HOLD.

## Eksporty i kolejność wymagająca zamknięcia

Są te same8unikalnych STL/13szt ze wzornikiem. Zmieniono WYŁĄCZNIE P03 iP06;6pozostałych STL skopiowano i zweryfikowano bajtowo. Wszystkie siatki są zamknięte, dodatnie, w mm/Z0/dodatnimXYZ i mieszczą się w256 mm. To poprawność eksportu, nie fizyczny PASS. PETG0,2/4obrysy/5góra-dół/35% to propozycja do przymiarki; zamknięte gniazda mają mały mostek6,3 mm, który wymaga rzeczywistej próby druku/pasowania. Nie wykonano slicingu ani druku.

Plan: wzornik8osi/gwintu → listwy i połówki na stole → rzeczywisty załadunek nakrętek/podkładek PRZED osadzeniem na ramie → osiem źródłowych mocowań → S0 i jego panel/śruby → wsunięcie dopasowanych końców szyn PRZED zamknięciem przedniego połączenia półki i założeniem PCB → wiązki/bateria/osłony na końcu. **Etap załadunku nadal ma wskazany HOLD, więc tej sekwencji nie uznano za wykonalną.** Nakrętki są prowadzone przeciw obrotowi przez5,8 mm szczelinę (nakrętkaAF5,5), podkładkaOD7 przez7,4 mm; nie rozpinamy wirtualnie fabrycznych końców, lutów ani integralnej ramy.

Źródłowe M2.5/Ø2,05 nadal nie są dowodem fabrycznego gwintu. Dwa M6/38 mm dlaS0 pozostają założeniem rodziny do lokalnej przymiarki. Cztery220, krótkieFHAC, USB500/Delock, stosPi/BUS i masa/ruch/skorupa pozostają nazwanymi próbami z poprzedniego pakietu. Mapa16WAGO nadal4DATA/5plus/7masa i dokładnie ten sam graf elektryczny. Brak nowego cięcia, złącza, zakupu, prądu, ROS ani recenzji geometrii. Stare HOLD i33zamrożone pliki pozostają bez zmian.

Orientacja do samej przymiarki: duża płaska dolna powierzchnia każdego STL na stole, lokalneZ0 zgodne z eksportem; bez skalowania, jednostka mm. P00 płasko. P03/P06 pozostają HOLD: orientacja i poprawna siatka nie zwalniają blokady montażu. Cztery identyczne słupkiP05 i dwie listwyP01/łącznikiP04 mają ilości w CSV. Nadwieszone kanały/mostekP06 wymagają próbki pasowania; podpory i parametry nie są zatwierdzonym profilem slicera.
