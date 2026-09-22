# Stan mechaniki — 2026-09-22

Branch: **`codex/robot-cat-mechanical`**, repo **syskaseb/robot-cat**.
Ostatnie złożenie: [v28](v28/README.md). **Nie jest wydaniem do druku.**
[v26](v26/README.md) zawiera kolejny audyt części rzeczywistych i dostępu
serwisowego; nie zastępuje ukończonym modelem brakujących mechanizmów.
Na zlecenie użytkownika rozpoczęto konkretny
[dobór części i zebranie modeli producentów](../reference/component-selection-2026-09-22/README.md).
Priorytet: Botland, następnie Kamami; maksymalnie 10 dni oczekiwania.
Pobrano i sprawdzono cztery modele STEP, ale nie wdrożono ich w złożeniu.

## Wykonane teraz: więzy oraz Gazebo

- v27 naprawia 32 mocowania: obudowy pierwszych serw biodrowych poruszają
  się z WConnector, orczyki pozostają przy ramie. Geometria i 12 osi bez zmian.
- Natywny test FreeCAD: 22 klatki ±3°, zachowane wszystkie łączenia.
- [Aktualny CAD uruchomiony w Gazebo](../simulation/README.md): 13 ciał,
  12 osi, rzeczywiste siatki, osiem prób v27 i sześć v28. Aktualne wnioski
  opierają się na ostatnich trzech v28, bez sztucznego limitu prędkości.
  Masa v28: nominalna 2,448 kg, zakres 2,167–2,911 kg; **szacunki**, nie ważenie.
- ST3215 pozostaje kandydatem do wolnego chodu. Nie ma potwierdzonego
  momentu ciągłego ani próby termicznej; nie zatwierdzono biegu.
- W v28 zainstalowano `FrontCoverClearance27.FCStd`, usuwając dwa małe
  przenikania osłony z obudowami serw. Zachowane otwory M3; zaliczony test
  22 klatek natywnych i inkrementalna regresja sześciu pozycji. To nadal nie
  jest pełny ciągły test kolizji całego chodu ani walidacja wytrzymałości.
- Odrzucono podcinanie WConnector, które osłabiałoby okolice otworów M2.
- Przeszło 581 dotychczasowych testów ROS i 22 testy obliczeń CAD.
- Stare PDF-y i prosty URDF nie są już przedstawiane jako walidacja
  obecnej konstrukcji. PDF-ów nie przebudowano.

## Ustalenia już zamknięte

- Wszystkie części projektowane do druku: PETG. Pole drukarki 256³ mm.
- Robot do domu; spodnia osłona nie jest wanną ani podporą akumulatora.
- Lista `docs/plan-zakupowy.pdf`, strona 1: **2 serwa głowy + 1 ogona**.
  Nie ma zgody ani potrzeby interpretacyjnej na czwarte serwo pomocnicze.
- Złożenie ma 12 natywnych Revolute nóg i 225 Fixed, w tym **64 tymczasowe**
  blokady. Fixed nie zastępuje rzeczywistego wspornika, śruby ani łożyska.
- Test natywny v28: 22 klatki ±3°, nie pełny chód ani pełne zakresy serw.

## Blokady wymagające konkretnych części / decyzji zakupowej

1. **3 serwa pomocnicze i orczyki.** Użytkownik zlecił dobór, nie trzeba
   ponownie prosić go o linki. Kandydat: 3 x TowerPro MG92B DNG-24409,
   dostępny w Botlandzie. Jest STEP Adafruit 2307 i karta wymiarowa;
   wysokość całkowita różni się między nimi (36,8 vs 35 mm). Do rozwiązania:
   dopasowanie uchwytów, orczyków, podparcia, bilans momentów i zasilania,
   poziom logiczny PWM oraz kalibracja zakresów. Nie zatwierdzono mechanizmu.
2. **Akumulator** — konkretny model, wymiary z przewodami i złączami.
   Obecne 90 × 43 × 19 mm jest przykładem, nie potwierdzonym zakupem.
   Alternatywne 3000 mAh z PDF nie określa jednoznacznie gabarytów.
   Kandydat Gens Ace GEA223S30X6GT ma według producenta około
   106,5 × 35 × 21,5 mm. Znaleziona szybka oferta jest poza preferowanymi
   sklepami; wyjątek zakupowy pozostaje pytaniem do użytkownika.
3. **Warianty elektroniki**: dokument uzupełniający już określa BNO085
   Adafruit 4754 i VL53L5CX Pololu (3417). Ich STEP-y i otwory są zbadane,
   nie należy dalej przedstawiać ich jako nieznanych wariantów.
   Dla AUX zaproponowano drugie D24V90F5 zamiast nieokreślonego 3 A;
   koszt i wymagane lutowanie są jawnie opisane w raporcie. Nadal nie ma
   zatwierdzonych mocowań i bilansu prądu/termiki. Głośnik, moduł IR,
   wyłącznik i oprawka głównego bezpiecznika wymagają dalszego dopracowania.
4. **Dystrybucja zasilania**: PDF wskazuje KAB-06897; karta sprzedawcy
   podaje 154 × 20,5 × 15 mm, a obecna bryła ma 52 × 64 × 14 mm.
   Nie są tym samym modelem. Wymagana decyzja: zakupiona listwa i jej
   rzeczywisty podział czy zmiana na konkretny kompaktowy element.

## Prace do wykonania po zamknięciu interfejsów

- Uchwyt głowy: 2 osie, podparcie obciążeń, orczyki/śruby, mocowania kamery,
  czujnika i reszty części twarzy; sprawdzenie przewodów przez całą trajektorię.
- Ogon: 1 napęd, wymienne segmenty i rzeczywiste połączenia. Stare bryły
  „elastyczny przegub” nie dowodzą poprawnego przegubu z PETG.
- Usunąć z nowej rewizji nadmiarowy napęd ogona po ustaleniu mechanizmu;
  zachować poprzedni checkpoint jako dokumentację, nie jako BOM zakupowy.
- Mocowania elektroniki oparte o faktyczne otwory, wtyki, miejsca serwisowe.
  Zweryfikować termikę regulatorów i chłodzenia, nie tylko statyczny obrys.
- Serwis akumulatora: obecna tacka/paski/nakrętki blokują wyjęcie w dół.
  Wąska tacka i mocowania na końcach są kierunkiem do sprawdzenia, nie
  zatwierdzonym rozwiązaniem ani powodem do wycięcia ramy na ślepo.
- Pełne nominalne zakresy ruchu i kolizje, luzy na wiązki i narzędzia.
- Ocena cienkich płyt ramy PETG, masa, obciążenia i próbny montaż.
- Komplet STL/3MF, pozycje na stole, BOM śrub i instrukcja kolejności składania.

## Kryterium „skończone”

Brak niejawnych obwiedni zakupowych i tymczasowych blokad w mechanizmach,
każda część zamocowana fizycznie, odtwarzalny raport geometrii i ruchu,
wyjmowanie akumulatora oraz dostęp do elektroniki bez kolizji, drukowalne
części 256³ i instrukcja montażu. Wyniki CAD nie zastępują wydruku próbek,
prób obciążenia PETG, rzeczywistych tolerancji ani pomiarów temperatur.
