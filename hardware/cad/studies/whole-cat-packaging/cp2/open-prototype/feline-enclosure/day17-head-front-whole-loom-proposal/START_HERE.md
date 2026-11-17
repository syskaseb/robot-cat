# Cały front / głowa — propozycja funkcjonalna, nie zatwierdzony montaż

**Wynik: HOLD bieżącej wspólnej warstwy.** Zachowano jedną propozycję: kamera obrócona o 180° wokół jej niezmienionej osi optycznej, taśma wychodzi ku górze; Pi pozostaje nieruchome na korpusie, leży poziomo, USB/Delock skierowane do wnętrza. Nie wykonano nowych mocowań, osłon ani STL. Otwórz `head-front-whole-proposal.FCStd`.

## Co rozstrzygnięto

- Pełne PCB/obudowy pola instalacyjnego/porty Pi oraz komplet czterech zestawów mocujących przeniesiono jednym sztywnym przekształceniem. Nie przesuwano samego terminala. PCB ma teraz X−126..−41/Y−28..28/Z141..142,6. Pełne pole chłodzenia kończy się na Z168,6, GPIO na Z172,48 — poniżej dotychczasowego dachu189. Warstwa Pi podniosła się o około64 mm: wzrost środka ciężkości jest kosztem tej propozycji, nie zyskiem masy.
- Oś optyczna kamery pozostaje na Y0/Z145, kierunek−X; pełny moduł, pole instalacyjne i dwa kompletne zestawy śrubowe obrócono razem. Nowe C0=[−206,85;0;155,4], PiCSI=[−80,5;−16,5;148,1]. To przekształcone piny projektowe poprzednika; rzeczywiste ustniki/klapki wymagają jednej przymiarki. Obraz kamery będzie obrócony; żadnego ROS ani zasilania nie uruchamiano.
- Dwie ćwiartki R13,5 i środkowa rzeczywista krzywa dają w dziewięciu pozycjach **140,72..166,28 mm z dodatkiem10 mm raz**. Minimum promienia środka próbkowanej części środkowej46,10 mm; łuki zachowują przyjęte R wewnętrzne12,5. To nie ciągły dowód ruchu ani górny budżet pełnej taśmy.
- **Pełne200 mm wciąż trzeba rzeczywiście pomieścić.** Pozostaje33,72..59,28 mm przed uwzględnieniem szerokości, skrętu i bightu. Nie narysowano fikcyjnego „wolnego pudełka”, nie przyjęto schowanego zapasu za zaciskiem. Widoczne krzywa i prostokąty16,8×1,8 są referencją prowadzenia, nie dowodem obsadzonej przestrzeni.
- Pierwszy skończony test40 nowych relacji wykazał **2116 mm³ wspólnego pola Pi_USB_DATA_Delock_mating/BUS25514_installed**. Pozostałe39 relacji neutralnych przeszły odległość lub granicę przestrzenną. Oba operandy pochodzą z jawnych instalacyjnych uproszczeń źródła:26×26×24 dla zestawuUSB/Delock i42×33×24 dlaBUS. To sprzeczność aktualnej alokacji pełnych jednostek, **nie potwierdzona kolizja dostarczonego plastiku**, niedobór kabla ani zgoda na zmniejszenie pól. Nie ponawiano nieważnego pełnegoSTEP BUS.

## Jedna następna decyzja całego frontu

Przed wykonaniem jakiegokolwiek wspornika trzeba wspólnie rozwiązać **stałą płaszczyznę Pi–BUS/E1, pełne wyjście USB/Delock, chłodzenie i dostępny zapas taśmy przy szyi**. Stary mostBUS/E1 i stare pionowe słupki Pi nie są nieruchomymi produktami. Potrzebna jest jedna rzeczywiście zdejmowana wspólna poprzeczka/warstwa z zachowaniem ich funkcji oraz czterech niezależnych E2/JPWM, a nie kolejna mikrokorekta krzywej. Nie wybrano tu drugiego ustawienia ani nie wykonano nowej rodziny druków.

Oparcia tej przyszłej warstwy muszą wynikać z rzeczywistych powierzchni integralnego przodu/P01 i pełnego montażu śrub. Niebieska płaszczyzna oraz linie w modelu są **niematerialnym planem**: nie dowodzą połączenia, nie wchodzą do masy, nie są STL. Dotychczasowe przyjęte podłożeP01/podłoga/sourceH01 oraz osłona głośnika pozostały geometrycznie niezmienione. Zmienione mocowania Pi/kamery i funkcja mostuBUS/E1 wymagają nowego wykonania; nie awansowano ich do FIT.

## Wiązki i montaż

`whole-loom-groups-and-assembly.json` rozdziela pełnąFFC200, czteryToF OD2,1/R31,5 oraz dwa odrębne źródłowe układy JR250+300. Yaw-serwo stoi na korpusie; obudowa pitch-serwa obraca się z yaw, nie z pitch. Rezerwa ma być dostępna przed rzeczywistymi klamrami, w luźnym wspólnym prowadzeniu; przewody nie muszą zachowywać jednej krzywej we wszystkich pozycjach. Czwórka ToF ma jawną nominalną obsadę10,4×2,9 mm i potrzebę łuku co najmniej31,5, ale jej ciągła trasa i budżet nadal nie są wykonane.

Dwie osoby: korpus i pełne śruby najpierw, wspólna zdejmowana płaszczyzna oraz chłodzenie/porty potem; cały lutowany PCA/E1 bez rozpinania; pełna taśma z poprawnymi stronami styków przed pokrywami; ułożenieToF/JR i ręczna kontrola±20yaw/±10pitch; dopiero osłony. Pokrywy oraz barkowo-szyjna forma mają podążać za sprawdzoną obsadzoną przestrzenią. Nie zamykać starej kapsuły nad niewykonaną wiązką.

## Granice wyniku

Wygląd całego robota nadal **niezaakceptowany**; nie zmieniano kosmetyki ani nie ukrywano kupnych wystających części. Widoki opaque są rzeczywistym modelem, nie poprawionym obrazem. Otwarte: rezerwa/szerokość/roll/ruchFFC, ToF/JR i budżety poszczególnych jednostek, nowe rzeczywiste podpory, kontakt chłodzenia/portu, szyja/osłony, cztery pełne MTA0100335, masa/COM/udźwig i próba fizyczna. Rzeczywiste dopasowanie, cięcie i luz **NULL**. Wholekit=false, physicalPASS=false. Wszystkie57+ADD7,12ST3215+3MG, nogi, ogonY i ochrona zachowane.

Źródło1a20991c pozostaje zamrożone; wcześniejszy test169 zatrzymany na7. Ten pakiet nie zastępuje poprzednich STL i nie jest pozwoleniem na druk ani zasilanie całego kota.
