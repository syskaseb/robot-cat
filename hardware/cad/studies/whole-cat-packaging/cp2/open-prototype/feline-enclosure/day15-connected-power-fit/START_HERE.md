# Bieżący model przymiarki — obszar zasilania HOLD

Otwórz `connected-power-fit.FCStd`. To jedna propozycja bieżącej ramy, bez nowej części drukowanej. Pełny wybrany XT60 z osłonami zachowuje obszar 50×24×18 mm; poprzedni blok zawierał także zapas na luźne przewody, nie był sztywnym portem baterii.

Wybrano zatokę nad przednim północnym bankiem X−96..−46/Y40..64/Z125..143. Osiem połączonych obszarów prowadzi dwa końce baterii, powrót W001 i krótki koniec F0. Geometria łączy regiony, lecz nie dowodzi rzeczywistych końców ani wszystkich promieni przy ręcznym rozgałęzieniu.

**Wynik:** cały obszar XT60 przeszedł swoją kontrolę sąsiadów. Pierwsze dojście dwóch przewodów ma do P12 **1,10 mm zamiast 1,25 mm**, common=0, poprawna geometria. Jest to HOLD przydzielonego pola, nie kontakt dostarczonego przewodu. Zatrzymano tę jedną hipotezę. Dalsze pola i brakujący delta-test druków/audio pozostają NIEODEBRANE; nie wznowiono starego iteratora. `power-region-result.json` oraz dwa świadki BRep są autorytatywne. `whole.png` i `power-local.png` pokazują obecną konfigurację, nie gotowego kota.

## Kolejność dwóch osób

1. A podtrzymuje ramę, B wstępnie ładuje pełne nakrętki/podkładki i skręca ramę przed płytkami. Dotychczasowe dziesięć zestawów ISO10642 i cztery zaciski bazy pozostają bez zmian.
2. Bez zasilania rozłożyć pełne rzeczywiste końce baterii/XT60, F0 i G1 w otwartej ramie; najpierw sprawdzić FIT2. Nie przedłużać ani nie przycinać przewodów na podstawie tego modelu. Nie montować stałej retencji w polu HOLD.
3. P14 z dotykiem pozostaje stały; E1 nie jest wirtualnie rozlutowywany. Przy dostępie do baterii: zdjąć późną osłonę i P15 po rozłączeniu rzeczywistego USB mikrofonu, następnie rzeczywiste końce BUS/P13, rozłączyć XT60 oraz zachowany interfejs balancera, dopiero wyjąć baterię. Trasa/zakres rzeczywistego wyjmowania nadal FIT2, bez obietnicy szybkiego serwisu.

## Trzy fizyczne przymiarki

- FIT1: P00 i osiem osi źródłowej ramy, rzeczywiste gwinty/revizja, nominalne stożki 90° śrub i dostęp narzędzia. Bez wiercenia lub gwintowania kupnej ramy.
- FIT2: rzeczywiste wyjścia/średnice/promienie i długości baterii, XT60 z osłonami, balancer, G1 i F0. Przyjęte OD6/R24 to jawna pojemność projektowa, nie dane producenta. Krótki W075 ma nadal limit projektowy 50 mm; stare 30/70/545 nie są wykonanymi cięciami ani kredytem długości. W076 fabryczny i custom/POST_F0/S0 zachowane. Cztery niezależne 220/MTA, USB500+Delock, FHAC i audio wymagają rzeczywistej przymiarki, bez pożyczania długości między przewodami.
- FIT3: chłodzenie Pi/BUS, retencja PCB/audio/banków/baterii, porty, ruch/nogi i udźwig. Zachowane 4DATA/5plus/7G, wszystkie 57 pozycji oraz dodatki audio/czujniki.

9 STL/10 sztuk i BOM skopiowano bajtowo z poprzedniej ramy wyłącznie jako odniesienie przymiarki; ten pakiet **nie zwalnia nowego druku ani całego układu**. Stare negatywy nie zostały skasowane. Brak zmian materiału/śrub/pozy kupnych części. Następny krok: rozstrzygnąć rzeczywisty interfejs wyjścia baterii i dostępny otwarty wspólny transport względem poprzecznego P12, bez kolejnego przesuwania tego samego łuku. Retencja PCB/audio/banków/baterii to późniejszy niezbędny zakres, nie obecny PASS.
