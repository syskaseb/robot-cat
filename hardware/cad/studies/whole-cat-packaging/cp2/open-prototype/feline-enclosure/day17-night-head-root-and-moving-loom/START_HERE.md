# Rzeczywisty korzeń/ruszt; wybrana zatoka wiązki ma HOLD

Bieżący model `head-root-moving-loom.FCStd`, kandydat NIEPRZYJĘTY jako cały zestaw. Nie wydano STL. Brak physicalPASS, actual fit/cut/slack = NULL. Źródło83b87cfd i wcześniejsze native niezmienione; bez edycji FIRST/runtime/currentassembly.

## Zrealizowany wspólny interfejs

Korzeń i pełny nośnik czterech punktów Pi są teraz rzeczywistym materiałem **przedniej części rusztu**, a nie przenikającymi osobnymi drukami. Druga część jest osobna, ze schodkową zakładką. Dwa pełne M3×12 z dwiema podkładkami i nakrętką każdy znajdują się na X2/Y±65; nowe zapotrzebowanie NEEDED_UNCONFIRMED, bez zakupu ani deklaracji zapasu.

- Przednia/tylna część: poprawne pojedyncze bryły, wspólna objętość0. Rzeczywista powierzchnia zakładki557,842 mm²; nie jest to próg ani dowód wytrzymałości.
- Stara kolizja korzenia z chłodzeniem usunięta przez funkcjonalny receiver z pełnymi polami pod podkładkami; aktualny odstęp1,50 mm przy wymaganiu1,25. Śruby i Pi nie zostały przesunięte.
- Pełna ciągła droga wprowadzania nowych śrub i górnych podkładek oraz podawanie dolnych podkładek: common z drukiem0. Dolny dostęp/narzędzie nie ma kandydatów w pobliżu aktualnych źródłowych części napędu. Dokładne testy dotyczą tylko dwóch nowych operacji; nie powtórzono globalnej macierzy.
- Obie części mieszczą się geometrycznie w256 mm z4 mm brimem na stronę: przednia141×169×31,98; tylna143×169×11. Potrzebne podparcie pod korzeniem i fizyczny test obciążenia nie są wykonane.
- Cały dawny ruszt zachowano poza **jawnym dopasowaniem do rzeczywistego P01**:40,998 mm³ z własnej niezbudowanej poduszki X−48..−38/Y−26..−17,5/Z45..45,52. To dokładna ulga odbiorcza według bryły P01, nie cięcie zakupnej ramy ani wycięcie powietrznego BBox. Po niej common z obiema P01=0; realne powierzchnie styku471,527 i491,685 mm². Osie źródłowych ośmiu mocowań P01 pozostają.

Surowy pierwszy wynik3brył przedniej części i „braki”54,475/63,554 mm³ zachowano: pierwsze oznaczało dwie niepołączone stacje zakładki, połączone teraz użytecznymi żebrami3×5; drugie to objętości celowo zaplanowanych otworów M3, nie zniknięte belki. Bieżące wyniki są w actual-final-root-grid-completion / integral-Pi-receiving-interface / actual-P01-receiving-relief / final-source-contact-and-inherited-Pi-steel.json.

## Dwa jawne ograniczenia całego układu

**Wiązka:** między pełnym polem chłodzenia Pi a P_SYS w ich wspólnym rzucie22×35 mm jest5,38 mm wysokości. Dla wybranej zatoki nawrotu to za mało: obrót szerokości FFC wymaga19,38 mm z marginesami, nawrót cienką stroną R12,5 —29,38 mm. Spakowane cztery ToF OD2,1 potrzebują7,70 mm nawet na przejście proste z marginesem; ich własny flexR31,5 pozostaje. To odrzuca **wybraną zatokę**, nie wszystkie drogi ani dostarczony przewód. Nie zbudowano kolejnej krzywej po tym tanim falsyfikatorze.

Neutralna FFC83b i osiem wcześniej sprawdzonych sąsiedztw są zachowane. Nowy niski materiał jest poniżej53,52, a nowy receiver jest podzbiorem poprzedniego korzenia. Nie ogłoszono przez to PASS całej CSI200:8,666..35,549 mm tej samej jednostki nadal potrzebuje połączonej przestrzeni nadmiaru i dowodu ruchu. Potrzebna jest szersza organizacja pasywnych prowadzeń głowa/szyja/warstwa przednia, bez luzu za stałym chwytem, cięcia200, zmniejszeniaR/zakresu czy kredytu USB/Grove/600.

**Pi/P01:** nowy odczyt ujawnił nieodebrany wcześniej narożny zestaw FORE_PI__42_5__19_5. Śruba, dolna podkładka i pełna nakrętka mają common z rzeczywistym P01 odpowiednio28,962 /6,444 /32,828 mm³. To cyfrowy HOLD własnego nominalnego zestawu, nie twierdzenie o kontakcie dostarczonego sprzętu. Nie naprawiano go kolejną rodziną śrub i nie przeniesiono go do „tylko FIT”. Sam poprawiony korzeń nie oznacza zamocowanego całego Pi.

## Montaż i ruch

Pusta baza/P01 i cztery źródłowe osie na każdą połówkę → zakładka z pełnymi nakrętkami/podkładkami od spodu i narzędziem R4,25 z góry → siodło/kupne serwa/łożyska/fabryczne rogi → całe połączone moduły i końce ręcznie układane przy otwartej górze → pasywne prowadzenia i zakwalifikowany nawrót → pokrywy na końcu. Banki/Pi/E1 są instalowane po śrubach rusztu; nie odpina się wirtualnie lutowanego E1 ani integralnej belki. Narożny zestaw Pi musi najpierw dostać rzeczywisty poprawny interfejs.

YawMG ma stały korpus, więc jego przewód nie podlega obrotowi rogu. Korpus pitchMG porusza się tylko z yaw. ToF i kamera poruszają się z yaw i pitch. Nie narzucono im jednej sztywnej krzywej. Końce/JR pozostają całe; dane o rzeczywistych wyjściach fabrycznych i długościach są wąską luką źródłową. Nie zmieniono2MG/łożysk/rogów/zakresów yaw±20,pitch±10 ani geometrii głowy83b.

Aktualny obraz wnętrza: `whole-interior-fixed-root-and-moving-loom-HOLD.png`. Czerwone pole jest **odrzuconą pojemnością**, nie dostarczonym przewodem. Pozostałe P_REAR/F_AUX,10FHAC/25komór,4E2,4MTA0100335UNBOUND, głośnik/końce i zamknięcie całego robota pozostają OPEN. To nie kolejna recenzja ani zamknięcie nocnego okna.
