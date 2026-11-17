# WAVEGO-kot — wynik pracy 17 listopada

**Projekt pozostaje częściowy. Nie ma jeszcze kompletnego zamkniętego kota do druku i montażu.** Oczy i widoczny, zakrzywiony ogon poprawiły się; cały wygląd nadal nie został przyjęty względem robota Oli.

Otwórz [aktualny model FreeCAD](assembly/WAVEGO_CAT_WORKING_HOLD.FCStd), [widok całości](views/whole-opaque-three-quarter.png) i [bok](views/whole-opaque-side.png). Model zawiera także znane, nieprzyjęte interfejsy. Zdjęcia pokazują rzeczywisty CAD d18; późniejsza korekta N1 zmienia tylko wewnętrzny interfejs rusztu.

## Użyteczny wynik

Powstały wspólne nominalne mocowania Pi, PCA z całym lutowanym E1, BUS, BNO, przetwornic i wzmacniacza; odbiorniki zasilania, operatora i audio; rzeczywiste wydrążone części korpusu i głowy oraz ogon obracany góra–dół wokół osi Y. Wybrane części i fabryczne końce zachowano.

W [PRINT_STATUS.csv](PRINT_STATUS.csv) jest **7 części do ograniczonych przymiarek oraz 1 kupon pomiarowy**. Każda ma własne warunki i źródło. Zgodność geometrii poszczególnych starszych części z aktualnym modelem sprawdzono przez identyczne bajty BRep i położenia. Nie oznacza to przyjęcia całego montażu.

Nie dodano starych N4/N5 ani diagnostycznego N1. Nie zastępuj brakującego elementu starszym STL o podobnej nazwie. Aktualne gabaryty siedmiu części osłon i głowy mieszczą się w 256 mm z przyjętą rezerwą 8 mm; ich STL nie zostały jednak zwolnione.

## Główne braki

- **N1–P02:** siatka N1 jest już zamknięta, ale 55,5 mm³ nowego materiału przenika osobny pokład. N1 pozostaje bez dopuszczonego STL; potrzebny rzeczywisty podział lub połączenie tych druków.
- **Głośnik–osłona:** 0,668 mm zamiast 1,25 mm oraz 136,69 mm³ przenikania jego uchwytu. Korpus i głowa pozostają bez STL. Pełna kontrola nowych sąsiadów/ruchu jest nieukończona.
- **Przewody głowy:** połączona przestrzeń całej FFC200, skrętu i użytecznego zapasu, ToF oraz JR nadal wymaga projektu. Odrzucona recepta 226 mm nie dowodzi, że wszystkie trasy są niemożliwe.
- **Cztery MTA0100335:** potrzebna jedna rzeczywista kompletna oprawka z pokrywą, uwięzią i oboma przewodami. Dawny mały box nie był jej poprawnym modelem.
- **Wygląd i masa:** korpus nadal wygląda pudełkowato, twarz ma duży otwór optyczny. Nie ustalono pełnej aktualnej masy ani zdolności chodzenia pod tym obciążeniem.

## Następny checkpoint

Najpierw rzeczywisty interfejs N1–P02 i głośnik–osłona oraz przymiarka całego rozmieszczenia z właściwymi częściami i FFC200 na otwartej podstawie. [Sześć grup celowanych przymiarek](reference/PRZYMIARKI.md) wskazuje minimalne próbki. Niewykonana konstrukcja lub znana kolizja pozostaje zadaniem projektowym.

Potem wspólna decyzja o przedniej warstwie funkcjonalnej i barkach/pyszczku z zachowaniem optyki. Audytor nie widzi uczciwej szybkiej kosmetycznej poprawki całej sylwetki.

Szczegóły: [montaż i braki](reference/ASSEMBLY_AND_OPEN_ITEMS.md), [N1](reference/N1_TECHNICAL_STATUS.md), [źródła mas](reference/MASA_ZRODLA.md). Cięcia, zainstalowany luz oraz fizyczne FIT1/2/3 nie są wykonane. Zasilania, druku, zakupów i prób chodzenia nie uruchomiono.
