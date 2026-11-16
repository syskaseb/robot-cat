# Niższy wspólny układ — jedna korekta, nadal NIE zestaw gotowy do druku

Aktualny plik: `low-light-whole-correction.FCStd`. Zachowane 12ST3215, 3MG, długości nóg, pełne wybrane części i mapa elektryczna. Źródło e7a96e08 i wcześniejsze pliki są nietknięte. Nie wydano STL.

## Co jest rzeczywiście zrobione

Głośnik przeniesiony jako całość na przeciwną stronę Pi: odstęp od pełnego pola GPIO **112 mm**. Nowa zakładka dwóch rusztów ma poprawny common=0, pełne cztery zestawyM3 i komplementarne powierzchnie. Rzeczywiste dolne stopy zadu uwzględniają stopień P01:41,52, a nie45,52 z całego BBox. Osiem źródłowych osi ma pełne nominalneM2.5x20CS; rzeczywisty gwint pozostaje P00/FIT, nie polecenie wiercenia. Pi, podstawa głowy i ogona mają pełne nowe zestawy i zmierzone powierzchnie wspólnego oparcia:96,953 /539,683 /773,683mm². To nie są progi wytrzymałości ani physicalPASS.

Dwie pełne wybrane opaski200 obejmują modelowaną połączoną platformę. Pola obejmują profil15x2,2, zamkniętą pętlę, przejścieS, zakładkę i całą pozostałą końcówkę. Klamra/dostarczona tkanina/napięcie nadal wymagają jednej próbki. Całe banki MTA i ich panele rozsunięto o3,65mm na stronę z warunku pełny pas+1,25, bez pomniejszania obudów. Logiczna i operatorowa warstwa P_SYS/P_REAR/MAIN/AUX/S1/monitora zmieniona wspólnie; wszystkie dotknięte końce wymagają nowego sprawdzenia długości.

## Masa — pełny aktualny materiał, bez fikcyjnej oszczędności

To samo PETG1,27g/cm³: punkt startowy1778,501g -> **1283.436g** druków, różnica **495.065g**. Pierwsze664g nie jest już aktualną oszczędnością: dodano połączenia i pełniejsze osłony. Nowy pokazany stalowy osprzęt:około39.97g przy7,85g/cm³; masa zastąpionego starego osprzętu nie jest rozliczona. Brakujące mocowania, przewody, materiał wydruku i rzeczywisty COM nadal nie pozwalają podać pewnej masy gotowego robota ani udźwigu.

## Fakty blokujące przyjęcie całości

- Nominalny bark dotykał osłony głowy. Ten sam bark otrzymał relief wyprowadzony z rzeczywistego konstruktora elipsoid: aktualny nominalny odstęp4,236mm. Pełny ruch i zakrycie szczeliny w ruchu pozostająOPEN.
- Ciągłe płaskie pole CSI jest już w CAD od wnętrza głowy do Pi. Wybrana trasa ma nominalne centrumR12,5/profile16,8x1,8, skończony skręt na prostych i skorelowane9pól pozy. **Neutralne zajęte pole dotyka rzeczywistej ramki głowy**: lokalneHOLD alokacji, nie dowód niemożliwości wszystkich tras/za krótkiej dostawy. Pozostaje także pełne schowanie reszty200mm i źródłowe strony styków. Nie ma falsemotionPASS.
- Głośnik zajmuje również istniejącą rezerwę niepowiązanego jeszcze pełnego MTA0100335 z przodu. Rezerwa nie jest dowodem fizycznej kolizji dostarczonej oprawki, lecz nie wolno jej liczyć jako pustej. Całej koalokacji nie przyjęto.
- Wszystkie10końcówFHAC/25komór są jawnie przypisane, ale wspólne zajęte przejścia i całe nadmiary nie są zakwalifikowane. KandydatW04376,63mm jest tylko konstrukcją z umownymi ustami, nie nowym mfgdatum ani gotową wiązką. Pozostałe jednostki zachowują osobne kontrakty; brak cięcia/dodatkowych przedłużeń.
- Mocowania pozostałych grup, komplet osprzętu osłon i ich ruch/pełny montaż są nieukończone. `realized-vs-open-and-assembly.json` rozdziela fakty od planu.

## Rzetelny wygląd

Przód i zad mają rzeczywistą obłą powłokę, przekroje są wypukłe, oczy mają fizyczne obramowanie i policzki, końce nie są płaskimi zaślepkami. Ocenione rzeczywiste obrazy pokazują jednak nadal **za długi, rurowy/niemal równoległy profil boczny i maskową głowę** wobec robota Oli. Poprawa przekroju nie daje akceptacji wyglądu. Widoczne wystające części/otwory nie są retuszowane. Nie wykonano nowej rodziny estetycznej po tym sprawdzeniu.

Cztery części powłoki i cztery krótsze odcinki szynWAGO są tylko nominalnym podziałem; nie eksportowano ich jako gotowych druków. Części muszą zmieścić się z brimem/podporami256; pełne sprawdzenie aktualnego podziału jeszczeOPEN. `wholekit=false`, `physicalPASS=false`, cięcia i zainstalowany luzNULL.
