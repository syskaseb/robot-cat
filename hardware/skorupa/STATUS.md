# Stan mechaniki — 2026-09-21

Branch: **`codex/robot-cat-mechanical`**, repo **syskaseb/robot-cat**.
Ostatnie złożenie: [v25](v25/README.md). **Nie jest wydaniem do druku.**
[v26](v26/README.md) zawiera kolejny audyt części rzeczywistych i dostępu
serwisowego; nie zastępuje ukończonym modelem brakujących mechanizmów.

## Ustalenia już zamknięte

- Wszystkie części projektowane do druku: PETG. Pole drukarki 256³ mm.
- Robot do domu; spodnia osłona nie jest wanną ani podporą akumulatora.
- Lista `docs/plan-zakupowy.pdf`, strona 1: **2 serwa głowy + 1 ogona**.
  Nie ma zgody ani potrzeby interpretacyjnej na czwarte serwo pomocnicze.
- Złożenie ma 12 natywnych Revolute nóg i 225 Fixed, w tym **64 tymczasowe**
  blokady. Fixed nie zastępuje rzeczywistego wspornika, śruby ani łożyska.
- Test v25: 22 klatki ±3°, nie pełny chód ani pełne zakresy serw.

## Blokady wymagające konkretnych części / decyzji zakupowej

1. **Dokładne 3 serwa pomocnicze i orczyki.** PDF nie określa modelu.
   Do ustalenia są gabaryty z uszami, raster otworów, wieloklin, oś,
   moment przy napięciu roboczym i dopuszczalny zakres. Alternatywa:
   użytkownik zleca dobór konkretnych modeli, zamiast dopasowania do zakupionych.
2. **Akumulator** — konkretny model, wymiary z przewodami i złączami.
   Obecne 90 × 43 × 19 mm jest przykładem, nie potwierdzonym zakupem.
   Alternatywne 3000 mAh z PDF nie określa jednoznacznie gabarytów.
3. **Warianty elektroniki**: BNO085, VL53L5CX, przetwornica AUX,
   głośnik, moduł IR, wyłącznik i oprawka głównego bezpiecznika.
   Nazwa układu scalonego lub prąd przetwornicy nie określają obudowy/otworów.
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
