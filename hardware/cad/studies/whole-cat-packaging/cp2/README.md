# CP2: wspólne rozmieszczenie wnętrza

Niewybrana propozycja w zaakceptowanym obrysie CP1, tułów325×200×160mm.
Nie jest zestawem części do druku ani zamknięciem W1/W5. R53 i14/20=70%
pozostają bez zmiany; hook wyłączony.

`WholeCatInterior.FCStd` zawiera zachowane rzeczywiste referencje P0,
przesuniętą głowę/ogon CP1 oraz62 edytowalne rezerwacje modułów.
Stara kaseta została usunięta z tej propozycji, nie z wybranego robota.
Źródło: `tools/cad/whole_cat_interior.py`; wynik i ograniczenia: `layout.json`;
kontrola nominalnego rozmieszczenia: `checks.json`; wymiary, wyjścia i granica
serwisowa: `interfaces.json`. Wcześniejszy plan61 rezerwacji zastąpiony.

| Warstwa | Rozmieszczenie |
|---|---|
| Dół | Akumulator pozostaje; Pi42..64mm, MAIN, BUS41..55,6mm, monitor50..62mm; poprzeczny F0 przed akumulatorem, XT60 i6 splices |
| Środek | Sterowniki78..108mm; dwie listwy po6 oprawek63..127mm;4 MTA0100335;5 pionowych FHAC75..126mm |
| Góra | Wszystkie20 logicznych WAGO130..141mm; otwierany grzbiet, nie zamknięte dźwignie pod osłoną |
| Źródło/wyłączniki | S0 z kluczem pionowo w przedniej strefie, S1 po prawej stronie ogona; otwory/osprzęt jeszcze do zaprojektowania |

Uwzględniono12 MTA0300330/24 zakończenia,20 bloków WAGO,6 splices,
4 MTA0100335,5 FHAC0001ZXJ i1 F0 FHAC0002ZXJ, XT60, osiowy F_PWM
0242.100UAT1 (bez osobnej oprawki) oraz układy sterowania.
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

## Uzgodnienie gabarytów 06.10.2026

BUS to Waveshare25514, NIE adapter575070. Pełna obwiednia zapisanego modelu
producenta42,024×33,816×14,6mm obrócona90°; USB wychodzi w+X.
Zapisany compound ma117 brył, ale jedna jest niepoprawna. Nie naprawiono ani
nie pominięto części: do kontroli użyto pełnej prostokątnej rezerwacji,
nie wadliwego BRep. Dokładne pasowanie BUS nie jest zakwalifikowane.
U1/57507030,48×17,78mm należy do sterownika PWM1608; nie jest drugim BUS.

P309 ma41×25×12mm według wskazanego dostawcy, zamiast dawnej rezerwy35×25×11.
FHAC mają51mm maksymalnej długości i20,25mm szerokości. Pięć gałęzi ustawiono
pionowo blisko ich szyn; oba wyjścia zachowane. Grubość22mm, OD3,4/R6 przewodu
pozostają założeniami. Fabryczne89,5±5mm obejmuje odkryty koniec; nie liczyć
go drugi raz jako dodatkowej długości. F0 obrócono poprzecznie w wolnej strefie
przed akumulatorem po wykryciu59,079mm³ kontaktu pierwszej rezerwacji z ramą.
Końcowe rezerwacje bez kontaktów; rama P0 bez zmian.

XT60H-M23,9×16,4×9,2mm dotyczy własnej połówki, NIE całej połączonej pary.
Druga połówka, wyjścia i ruch rozłączenia nadal wymagają przestrzeni.
Źródła i oddzielne założenia zapisane w `interfaces.json`.

## Granice tego wyniku i następny krok

Bryły są jawnie opisanymi rezerwacjami, nie dokładnymi modelami każdego SKU.
Podstawowe wymiary BUS/P309/FHAC/XT60 uzgodniono; pełne wyjścia/maty/obudowy
nie są jeszcze dowodem montażu. Rodzina HELLA, wsunięcie TE i wysokości wyposażonych
PCB są nadal założeniami prototypu. Wynik NIE dowodzi kompletnego montażu.

Pionowe FHAC zajmują dawny boczny kanał sygnałowy. Nowy wspólny poziom
sygnałów:X−39..114/Y−10..10/Z112..122mm, nad sterownikami. Boczne korytarze
zasilania10mm pozostają rezerwacją, NIE gotowymi trasami o potwierdzonych
promieniach. Zakręty R25,2mm muszą dostać osobne strefy w X/Z. Złącze źródła
wróciło obok F0 zamiast wędrować na tył; droga przed bezpiecznikiem <=50mm
wymaga jeszcze rzeczywistych osi/pinów i pełnej trasy.

Następny krok: dopasować pełne zakończenia i wspólnie poprowadzić wiązkę
w tych strefach, z podparciami i granicami rozłączania. Dopiero potem
wykonać nośniki/skorupę. Nie projektować podpór pod same prostokąty.
Górne WAGO nadal stoją nad bezpiecznikami. Policzenie granicy z istniejącego
netlist wykazało74 przewody wychodzące poza płytę i6 wewnętrznych połączeń.
Podwójne aliasy G1.5/G2.1 nie oznaczają dwóch fizycznych przewodów.
Odrzucono rutynową wymianę ATO wymagającą74 rozłączeń. PRZED podporami:
uzgodnić wspólnie bezpośredni dostęp do ATO przy podłączonych WAGO albo
rzeczywiście zdejmowalny podzespół ze zdefiniowaną granicą złączy. Obie strony
4 MTA i cała wiązka muszą uczestniczyć w tym planie; nie przesuwać samej płyty.
Ruch/dźwignie/parkowanie końców nie zostały zakwalifikowane. Nie dodano SKU.

Slicer, druk i próby należą do fazy2. Brak fizycznego PASS.
