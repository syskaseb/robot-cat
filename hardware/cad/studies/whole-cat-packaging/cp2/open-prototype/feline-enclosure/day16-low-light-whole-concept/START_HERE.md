# Niższy i lżejszy cały układ — pierwszy koncept, nie zestaw do druku

Otwórz `low-light-whole-concept.FCStd`. Jedna propozycja z aktualnymi częściami. Nie eksportowano STL. Aktualne nogi, 12 ST3215 i 3 MG pozostają.

Zmiana: Pi i bateria obok siebie, poziome naprzemienne banki MTA, niski wspólny ruszt/półka, pozioma drabinka FHAC i cztery cienkie, nienośne osłony. Dach tułowia 145 zamiast 185,201 mm; głowa -20 mm, ogon i cały zespół osi Y -42 mm. Głowa i ogon zachowują swoje wcześniejsze mechanizmy, lecz nowe podstawy i ich mocowania nie są jeszcze zakwalifikowane.

## Rzeczywisty pomiar i granica porównania

Przy niezmienionym PETG 1,27 g/cm³: 70 poprzednich wybranych druków 1778,501 g; 51 aktualnych (nowych i zachowanych) 1114,852 g. Różnica 663,649 g /37,315%. To pełna modelowana objętość, nie masa wydruku ani gotowego kota. Część usuniętych funkcji mocowań wymaga jeszcze wykonania: robocza rezerwa 50–120 g nie jest ścisłym górnym limitem. Nie przypisano elektronice masy z pudełek. Nogi niezmienione. Przy wcześniejszym roboczym 4 kg, sam ten bilans sugeruje około 3,39–3,46 kg po doliczeniu tej rezerwy; nie potwierdza udźwigu ani celu 2,5 kg.

## Pierwszy rzeczywisty problem

Głośnik kontra pełne pole wtyku GPIO Pi: odstęp nominalnych źródeł 0 mm. To odrzuca przyjętą koalokację tych dwóch elementów; nie dowodzi dostarczonego fizycznego kontaktu ani niemożliwości całej niższej architektury. Nie wykonano drugiej serii przesunięć. F0–PiPCB ma 1,5 mm, XT60-pole–klucz S0 10,5 mm; te dwie relacje nie przyjmują całej trasy.

CSI200: obejmuje odcinek w głowie, szyję i Pi. Plan komponentów 170,72 mm w neutralnej /maks.178,29 mm w sprawdzonych narożach ruchu, przed 10 mm roboczego osadzenia. To nie jest jeszcze ciągła trasa z promieniami, profilem i rezerwą ruchu. Wszystkie dziesięć końców FHAC i 25 komór WAGO pozostaje w planie, lecz pełne ich zajęte połączenia i nadmiary wymagają dowodu.

## Rzetelna ocena wyglądu

Widoki są rodzimym CAD, bez retuszu. Tułów istotnie niższy, bez poprzedniego wysokiego pudełka przy ogonie, ale nadal za długi i zbyt skrzynkowy względem robota z projektu Oli. Głowa i wyraz maski nie zostały poprawione. Przedni i tylny koniec cienkiego loftu pozostają otwarte; to nie zamknięta gotowa obudowa. Rzeczywiste wystające części i stare niezakwalifikowane zapotrzebowania na śruby pozostają widoczne, nie ukryto ich dla urody. Oba 253-mm profile WAGO potrzebują prawdziwego podziału przed drukiem z brimem w 256 mm. Wszystkie nowe kształty mają nominalnie dodatnie, poprawne pojedyncze bryły, co nie zastępuje dowodu nośności, połączeń i montażu.

`whole-functional-layer-and-assembly-plan.json` opisuje kolejność dwóch osób i pozostające braki; `same-density-mass-and-height.json` wybór każdej bryły; `whole-low-layout-effectivity.json` jawne zachowania/zastąpienia/pozy całych modułów; `per-physical-unit-premise.csv` kontrakty fizycznych jednostek. Żadnych fizycznych cięć, włączenia zasilania ani zmiany mapy elektrycznej. wholekit=false / physicalPASS=false / cut/slack=NULL.
