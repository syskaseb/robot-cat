# Stan porcji — korpus, wspólny nośnik i przewody

To jest zapis roboczy całego układu, **nie zatwierdzony zamknięty kot ani zestaw do druku**. Natywny plik zawiera wszystkie zachowane części źródłowe. Cztery PNG pokazują tę samą geometrię; wnętrze wyłącza wyłącznie własne osłony i dekoracje.

Zrealizowano materiał czterech cienkich części korpusu oraz dwóch wydrążonych części głowy. Nominalna ściana 1,6 mm, korpus z ograniczonych przekrojów i prostokreślnego loftu. Nowy nośnik łączy istniejące podpory Pi i dwa boczne korzenie z otwartymi płaszczyznami pod BUS oraz cztery fabryczne otwory PCA. Cały materiał poprzedniego, już podciętego nośnika Pi jest zachowany. Usunięto tylko zadeklarowany lewy półksiężyc podpory BUS, poza pełnym śladem podkładki, uzyskując od głośnika 1,50 mm. Nadal trzeba potwierdzić faktyczny datum PCB BUS względem pełnego pola instalacyjnego: surowe wspólne 126 mm³ pozostaje zapisane i nie jest uznane za zgodę na kontakt.

S0 z całym kluczem i 11 elementami przeniesiono na poprzeczną płaszczyznę operatora. Zachowano oba zaciski i rzeczywiste oczka kablowe. Obrót wejściowego oczka na prawdziwej osi zacisku daje 8,037 mm od pełnego AUX i 12,565 mm od WAGO615. Wspólne F0/S1 zastąpiono rozdzielonymi strefami: obecny odstęp 8,0 mm. Pełny zapas pary XT60 z osłonami ma 2,0 mm od F_AUX. To są wyniki nominalnych modeli, nie pomiar dostawy ani potwierdzenie długości końców.

**Ocena obrazów jest negatywna.** Bok nadal zbyt prosty; nowe policzki zasłaniają dekoracyjne oczy; szyja i część tylna nie mają ukończonego zamknięcia. Nie wolno traktować samych poprawnych brył jako zamontowanych pokryw. Nie ma nowych STL: osłony nie mają pełnych połączeń, a nowy wspólny nośnik wymaga ukończenia lokalnego testu datum BUS/śrub i nowej konfiguracji montażowej.

## Co rzeczywiście jest zamontowane w modelu, a co pozostaje otwarte

| Grupa | Aktualny stan |
|---|---|
| Pi / dwa boczne korzenie P02 / prawdziwy odbiornik pitch | D1 odebrany; Pi zachowuje śruby i cztery podpory. W tej porcji zmieniony nośnik, więc stary STL Pi nie jest aktualny. |
| BUS / PCA | Nowy wspólny otwarty materiał, otwory i istniejące pełne zestawy śrub; nominalne oparcia. BUS pole 126 pozostaje UNQUALIFIED; dodatkowy test pełnego sprzętu/narzędzi nie jest ukończony. |
| E1 | Cały lutowany z PCA zestaw zachowany; odstęp do nowego nośnika 3 mm. Górny docisk E1 pozostaje niezbudowany. |
| MAIN/AUX, BNO/AMP, MIC/TTP, monitor/S1, WAGO/MTA | Aktualne całe moduły i metale zachowane; ich zmienione wspólne podpory, zamknięcia i część mocowań nadal niezbudowane. Nie nazywać tego tylko FIT. |
| Głośnik | Zachowany cały; nowy nośnik ma odstęp 1,50 mm. Retencja kosza i spasowanie ze ścianą nadal otwarte. |
| Korpus / głowa / uszy / dekoracje | Rzeczywiste cienkie ściany, ale połączenia między drukami, pełne mocowanie głowy do pitch i uszu oraz szyja/ogon nadal otwarte. |
| 4 MTA0100335 | Cztery wymagane całe jednostki nadal bez wiarygodnej pełnej geometrii. Potrzebna jedna właściwa próbka; nie zastąpiono wymiarami WAGO. |

## Montaż dwuosobowy — kolejność i granice

1. P00 i rzeczywiste osie/śruby źródłowej podstawy; P02/P03 oraz istniejące kotwy bez forsowania kupnej ramy.
2. Dwa boczne pełne M3 nośnika Pi przed bankami. Wstępne nakrętki/podkładki i dostęp narzędzia; potem Pi i BUS/PCA. E1 pozostaje całym lutowanym zestawem. Nowy nośnik wymaga jeszcze potwierdzenia narzędzi i datum BUS.
3. Dolne pełne MTA/TE/ATO oraz dostęp do końców przed montażem górnych odbiorników. Zmiana pochylenia górnych sześciu jednostek wymaga nowych prawdziwych odbiorników — nie ma wirtualnie odpiętej integralnej belki.
4. Oba całe tekstylne pasy przed baterią; istniejące prowadnice zachowane. Dostęp baterii może wymagać MIC → BUS → prawdziwy XT60/balanser i częściowego demontażu; brak twierdzenia o szybkim serwisie.
5. Otwarte ręczne ułożenie przewodów, dostęp do dźwigni WAGO i klucza S0. Dopiero po potwierdzeniu stanu końców i ruchu wolno zamknąć przyszłe pokrywy. Zatwierdzone przycinanie dotyczy wyłącznie niewykorzystanego plastikowego ogona opaski po zaciśnięciu przez człowieka.

## Przewody i masa — bez pozornego zaliczenia

D1 FFC200 i DATA500 zachowane przez tożsamość Pi/kamery/BUS i tych samych końców; **nowe osłony nie dziedziczą ich sprawdzenia**. Cztery ToF mają zapisaną jedną rodzinę środkowego łuku: promień wewnętrzny 32,04–40,02 mm, długość 122,72–151,87 mm dla dziewięciu korelowanych pozycji. Nie jest to cały przewód: pad/header → chwyt oraz dok → prawdziwe H3/H5/3V3/GND nadal otwarte. JR250+250+300 i POWER W079/W080 nie uzyskały jeszcze pełnych aktualnych górnych budżetów z końcami. W078 pozostaje 210 z tej samej czerwonej żyły K1474, nie wolnym przewodem Pi ani pulą 600. W043/XA01 zachowują tę samą jednostkę FHAC z jednym debitem końców; inne XA/XB mają własne istniejące receptury. Cztery E2/JPWM pozostają osobnymi jednostkami min220. Rzeczywiste cięcia i luz po montażu: NULL.

Sześć nowych wydrążonych osłon: 330,187 g modelowego PETG przy 1,27 g/cm³. Nowy wspólny nośnik po celowym podcięciu: 33,317 g; przyrost względem poprzedniego podciętego nośnika 15,001 g. To **nie masa całego kota ani oszczędność całego układu**: brak połączeń, strażników ruchu i części retencji; dekoracje, pozostałe druki i metale liczone osobno. Bez twierdzenia o udźwigu/CG całego robota.

Najbliższa wspólna decyzja: oprzeć rzeczywiste zamknięcie i połączenia na ukończonych wspólnych nośnikach oraz zajętej przestrzeni pełnych ToF/JR/POWER, zamiast uznać nową ścianę za pokrywę gotową do montażu. Całościowy wynik: **OPEN / wygląd niezaakceptowany / physical_PASS=false**.
