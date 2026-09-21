# v26 — audyt interfejsów zakupowych i serwisu

**Audyt, nie ukończone nowe złożenie ani paczka do druku.**
Model odniesienia: [Kot v25](../v25/README.md), bez nadpisywania geometrii.
Aktualny plan i blokery: [STATUS](../STATUS.md).

## Wyniki

1. PDF na stronie 1 określa 2 osie głowy i 1 ogona. Model ma cztery
   zastępcze bryły serw pomocniczych. Dokładnego mikroserwa/orczyka brak w PDF.
2. Waveshare Bus Servo Adapter (A): w modelu 42 × 27 mm, producent 42 × 33.
   Pobrano oficjalny STEP i zmierzono jego PCB, otwory oraz złącza.
   Nie należy przenosić automatycznie istniejącej obwiedni na wspornik.
3. Grove PCA9685: stara obwiednia 60 × 40 × 15 mm. Katalog określa wysokość
   18 mm, a Eagle obrys z uszami 64,2 × 44,2 mm. Pięć otworów Ø2,2 mm
   nie tworzy standardowego prostokątnego rastra czterech śrub.
4. Listwa KAB-06897 ma według [karty sprzedawcy](https://botland.com.pl/produkty-wycofane/6897-kostka-elektryczna-12pin-16mm-30a250v-5904422357825.html)
   **154 × 20,5 × 15 mm**, a `PowerDistribution` w złożeniu 52 × 64 × 14 mm.
   Karta 2026-09-21 oznacza ją jako wycofaną. Nie zakładamy, że użytkownik
   jej nie kupił, ani że można bez uzgodnienia zmienić dystrybucję zasilania.
5. [Pololu D24V90F5](https://www.pololu.com/product/2866): otwory M2,
   raster 35,56 × 15,24 mm. Nie są to otwory M2,5 lub M3. Pozycje
   wsporników wymagają też wysokości strony lutowania i miejsca na przewody.

Archiwa producentów i instrukcja odtworzenia: [hardware/reference](../../reference/README.md).

## Akumulator — szczegółowy test

`supplier-service-probe.json` rozdziela wcześniejszą kolizję całego zespołu
na rzeczywiste części. Przy opuszczeniu o 1 mm przeszkadzają `BatteryCarrier23`
i oba paski. Przy 5 mm również cztery nakrętki. Przeszkodami są `SideLeft22`
i `SideRight22`. Dolna płyta WAVEGO ani sama bryła akumulatora nie pojawiają
się w wynikach tych pięciu próbek.

Test zakłada usunięcie płaskiej osłony i jej śrub oraz zwolnienie mocowań
zespołu dolnej płyty. Nie testuje ręki, przewodów ani alternatywnych tras.
Wyjęcie osłony nie jest tym samym co możliwość wyjęcia akumulatora.

## Geometria producenta i ograniczenia testu

`supplier-fit.json`: 117 brył STEP, walidacja każdej osobno, otwory PCB.
Jedna bryła (indeks 25) jest wadliwa. Zapisano wynik trybu `--metadata-only`,
**`fit_status=not_run`**: nie ma zaliczonego dokładnego testu dopasowania STEP.
Próby pełnego testu przerwano podczas kosztownych obliczeń OCC; brak wyniku
nie jest wynikiem „bez kolizji”. Nie zmieniono położenia adaptera w kocie.

Skrypt umożliwia osobny test trzech kandydatur położenia. Wadliwe bryły są
w nim zastępowane obwiedniami, co może dawać fałszywe alarmy. Nadal nie jest
to zatwierdzenie uchwytu ani brak kolizji wtyczek — wtyczek w STEP nie ma.

`head-tail-audit.json`: objętości brył i środki objętości segmentów;
nie pomiar masy wydruku ani obciążenia konkretnego serwa. Nie przypisano
na tej podstawie fikcyjnego materiału optycznego oczom czy czujnikom.

Skrypty: `tools/freecad/skorupa/probe26.py`, `supplier26.py`.
Przed `supplier26.py` uruchom `Cache26.FCMacro` przy otwartym, nieruszonym
złożeniu v25 w pozycji spoczynkowej. Zapisuje ignorowaną w Git migawkę BRep
w układzie świata; hash źródła jest sprawdzany przed testem. Migawka pozwala
uniknąć ponownego uruchamiania solvera złożenia w procesie diagnostycznym.
Do odtworzenia zapisanego audytu użyj `supplier26.py --metadata-only`.
`verify26.py` kontroluje pochodzenie raportów i archiwów, a nie gotowość
mechaniki. Sumy JSON w `audit-integrity.json` są liczone po kanonizacji
treści, niezależnie od końców linii Windows/Linux.
Wykonano je przez Python FreeCAD 1.1.3; odczyt modelu działającego
FreeCADa i geometrii głowy/ogona także przez działający MCP.
