# CP2: wspólne rozmieszczenie wnętrza

Niewybrana propozycja w zaakceptowanym obrysie CP1, tułów325×200×160mm.
Nie jest zestawem części do druku ani zamknięciem W1/W5. R53 i14/20=70%
pozostają bez zmiany; hook wyłączony.

`WholeCatInterior.FCStd` zawiera zachowane rzeczywiste referencje P0,
przesuniętą głowę/ogon CP1 oraz61 edytowalnych rezerwacji modułów.
Stara kaseta została usunięta z tej propozycji, nie z wybranego robota.
Źródło: `tools/cad/whole_cat_interior.py`; wynik i ograniczenia: `layout.json`;
kontrola nominalnego rozmieszczenia: `checks.json`.

| Warstwa | Rozmieszczenie |
|---|---|
| Dół | Akumulator pozostaje; Pi42..64mm, MAIN/BUS/monitor, F0/XT60 i6 splices |
| Środek | Sterowniki78..108mm; dwie listwy po6 oprawek, rezerwacje63..127mm;4 MTA0100335 |
| Góra | Wszystkie20 logicznych WAGO130..141mm; otwierany grzbiet, nie zamknięte dźwignie pod osłoną |
| Źródło/wyłączniki | S0 z kluczem pionowo w przedniej strefie, S1 po prawej stronie ogona; otwory/osprzęt jeszcze do zaprojektowania |

Uwzględniono12 MTA0300330/24 zakończenia,20 bloków WAGO,6 splices,
4 MTA0100335,5 FHAC0001ZXJ i1 F0 FHAC0002ZXJ, XT60 oraz układy sterowania.
Zgodność dokładnego zestawu20 nazw szyn z istniejącym netlist jest sprawdzana
automatycznie. Nie zmieniono topologii, SKU ani przydziału pinów.

Pierwsze dwie kontrole wykazały brak wspólnego warunku wysokości nad
mocowaniami nóg. Rozwiązanie: cały poziom oprawek oraz WAGO przesunięty
w górę; boczne listwy zwężone razem. Nie wycinano kolejnych dziur w starej
kasecie. Końcowa kontrola używa operacji na bryłach, a nie samego bbox:
rezerwacje nie przecinają się ani zachowanych części P0/głowy/ogona;
wewnętrzne rezerwacje z dodatkowym marginesem2,4mm mieszczą się w obrysie.
Klucz S0 i sterowanie S1 mają osobny zakres otworów obsługowych, nie zostały
udawane jako zamknięte pod skorupą. Ponowne otwarcie i parametr Pi sprawdzone.

## Granice tego wyniku i następny krok

Bryły są jawnie opisanymi rezerwacjami, nie dokładnymi modelami każdego SKU.
BUS/P309/FHAC/XT60 wymagają uzgodnienia rzeczywistych wymiarów z istniejącymi
referencjami. Rodzina HELLA, głębokość wsunięcia TE i wysokości wyposażonych
PCB są nadal założeniami prototypu. Wynik NIE dowodzi kompletnego montażu.

Przestrzeń między sterownikami i listwami wynosi11,6mm; boczne korytarze
zasilania10mm. To przydział przestrzeni, NIE gotowe trasy o potwierdzonych
promieniach. Zakręty R25,2mm muszą dostać osobne strefy w X/Z. Złącze źródła
wróciło obok F0 zamiast wędrować na tył; droga przed bezpiecznikiem <=50mm
wymaga jeszcze rzeczywistych osi/pinów i pełnej trasy.

Następny krok: dopasować pełne zakończenia i wspólnie poprowadzić wiązkę
w tych strefach, z podparciami i granicami rozłączania. Dopiero potem
wykonać nośniki/skorupę. Nie projektować podpór pod same prostokąty.
Górne WAGO stoją nad bezpiecznikami, więc ich płytę trzeba zdjąć przed
wymianą ATO: konieczna jest wykonalna granica rozłączania, nie powrót do
przecinania49 opasek. Tej sekwencji jeszcze nie zakwalifikowano.

Slicer, druk i próby należą do fazy2. Brak fizycznego PASS.
