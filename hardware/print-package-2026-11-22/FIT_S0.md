# 20H — FIT_S0 przed drukiem podstawy

**Najpierw wydrukuj tylko `FIT_S0_coupon.stl` i wykonaj przymiarkę bez zasilania.** Kandydacką tylną podstawę drukuj dopiero, gdy kompletny wyłącznik, mocowanie i klucz przejdą próbę poniżej. W pakiecie dużych części kandydat zastępuje `C20_RearBase`. Pozostałe pliki druków zachowują swoje wersje.

| Plik | Zastosowanie |
| --- | --- |
| [FIT_S0_coupon.stl](sample/FIT_S0_coupon.stl) · [STEP](sample/FIT_S0_coupon.step) | Jeden płaski kupon 56 × 57 × 3 mm, do przymiarki na stole |
| [20H_RearBase_CONDITIONAL_AFTER_FIT_S0.stl](STL/20H_RearBase_CONDITIONAL_AFTER_FIT_S0.stl) · [STEP](STEP/20H_RearBase_CONDITIONAL_AFTER_FIT_S0.step) | Jedna duża podstawa, warunkowo po udanym FIT_S0 |
| [whole-cat22-head-first-fit.FCStd](whole-cat22-head-first-fit.FCStd) · [widok przymiarki](FIT_S0-trial-CAD.png) | Złożenie, zachowane oczka i przebiegi przewodów, pełny referencyjny komplet M6 |

Dla rodziny HELLA 6EK 002 843, obejmującej wybrany S0 6EK 002 843-002, rysunek identyfikuje klucz 9SL 706 728-00. Fotografia pokazuje jego kształt, a instrukcja nie podaje przekrojów klucza przy panelu ani wymiarów tylnego osadzenia.

Oba wydruki mają centralne przejście Ø24 mm oraz dwa otwory Ø6,5 mm na rozstawie 38 mm. Oś pary jest pionowa względem bocznej pary zacisków w projekcie. Na części sprawdź orientację i rozstaw. Uformowane płaskie oparcia podkładek dużej podstawy mają tę samą grubość 3,0 mm co kupon. Kupon odwzorowuje osie i płaszczyzny mocowania. Na widoku przymiarki półprzezroczysty zielony walec po zewnętrznej stronie kuponu oznacza rezerwę klucza, a różowa bryła przedstawia uproszczony korpus. Pełny kształt ramy jest w pliku FreeCAD. [Rysunek HELLA, str. 1](reference/HELLA-46020100.pdf) · [Wymiary i sprawdzenia CAD](checks/FIT_S0-gate.json)

## Próba na stole

1. Zmierz rzeczywisty korpus przy kołnierzu, średnicę i głębokość przejścia, rozstaw otworów oraz ich orientację względem postów IN/OUT. Nałóż kupon bez wciskania. S0 powinien płasko się oprzeć i zachować dostęp do obu zacisków.
2. Załóż oba kompletne oczka i stosy M10 na stole zgodnie z ułożeniem z 20G. Nominalne kąty zmiany wynoszą −30° dla IN i −105,522° dla OUT, wokół osi +Y przez odpowiedni istniejący trzpień. Sprawdź płaskie oparcie oczek, izolację, odstęp od drugiego bieguna i wejście nasadki. Na czas próby użyj pełnych końcówek i luźnego ułożenia przewodów, bez przycinania odcinków docelowych.
3. Przymierz **2× DIN 912 M6×20, 4× podkładka 6,4×12×1,6 mm, 2× nakrętka M6 AF10 h5**. Dla każdej śruby sprawdź kompletny stos od strony klucza: łeb, zewnętrzna podkładka, 3 mm panelu, rzeczywisty kołnierz S0, wewnętrzna podkładka i nakrętka. Obie podkładki muszą się stabilnie oprzeć. Sprawdź pełne zazębienie nakrętki, ile końcówki wystaje i czy ma odstęp od korpusu i zacisków, oraz dojście narzędziem do łba i przeciwtrzymania AF10. Stan magazynowy kompletu jest niepotwierdzony.
4. W pełni osadź klucz, przejdź pełny zakres pracy i wyjmij go w pozycji OFF. Sprawdź odstęp klucza i palców od łbów, podkładek i panelu. Zmierz najmniejszy odstęp od metalu podczas ruchu. Założenie projektu wynosi **co najmniej 1,25 mm**. W razie kontaktu lub braku odstępu zanotuj rzeczywisty profil klucza w pasmach od 0 do 1,6 mm i od 1,6 do 7,6 mm na zewnątrz od powierzchni panelu, zakres kątowy, luz osiowy oraz miejsce ograniczenia. Wstrzymaj dużą podstawę, jeśli którykolwiek punkt próby pozostaje otwarty.

## Po przymiarce

W otwartej ramie montuj S0 z luźnymi przewodami przed kompletnym, lutowanym E1. Następnie osadź E1 i banki, włóż końce przewodów do zacisków WAGO i zamknij pokrywy. Sprawdź ponownie dostęp klucza, izolację i luz przewodów przy zamknięciu. Warunkowe długości HELU 23802 Ø4,2 mm wynoszą **260 mm dla W066 do P_SYS.1** i **389 mm dla W076/custom z POST_F0.2**, z końcami i rezerwą. Fabryczny W076 F0→POST_F0.1 oraz niezależny W077 pozostają w całości. [Kolejność i regiony ułożenia 20G](WEJSCIE_BATERII.md)

Konstruktor nazywa `S0_key` rezerwą do obsługi klucza. To pełny walec R15 × 63,5 mm. Zmierzone nakładanie się łbów i podkładek z tą rezerwą pozostaje wskazaniem do fizycznej próby. Rzeczywisty profil klucza, zakres ruchu, osadzenie, długości cięcia i luzy nie są jeszcze zmierzone. [Konstruktor rezerwy](checks/20H-manifest.json) · [Manifest i piny źródeł](checks/20H-manifest.json)
