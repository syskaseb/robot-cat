# Niższy front i boczny korytarz — propozycja CAŁOŚCI, nie wydruk

**Stan: WHOLE PROPOSAL REJECTED / HOLD przed detalami.** Wybrany układ ma pionowe Pi po dodatniej stronie wewnętrznej, osobną ujemną płaszczyznę BUS, cały lutowany PCA–E1 pomiędzy nimi, po sześć pełnych zespołów MTA/TE/ATO na każdym boku oraz poziomy głośnik nad sterowaniem. Kamera zachowuje oś optyczną; zegar płytki wraca do wyjścia taśmy w dół. Bateria, S0, tylny F0 i mechanika nóg/ogona nie zostały przestawione. AUX i wspólna górna warstwa MIC/AMP/TTP zostały rozdzielone od rzeczywistych portów i S0.

Otwórz **low-side-front-whole-proposal.FCStd**. Zdjęcia bieżącej propozycji: **whole-opaque-front.png**, **whole-opaque-side.png**, **whole-opaque-front-three-quarter.png**, **whole-interior.png**; osobno **raw-before-effectivity-section.png** jest surowym etapem pól pojemności i odrzuconej trasy, sprzed korekty zastąpionego obiektu415; nie jest bieżącym widokiem montażu. whole-initial.png jest wyłącznie wczesnym surowym checkpointem, nie bieżącym widokiem. Wszystkie bryły D18_FORM i pola wiązek są NOT PRINT / NOT MASS. Nie ma nowych STL ani przyjętych mocowań.

## Co faktycznie sprawdzono

149 przekształconych obiektów zachowuje objętość źródłową. Dokończona skończona kontrola 22 głównych modułów nie znalazła dodatniego nakładania ich BBox; to jedynie wstępny ekran, nie dowód wszystkich szczelin/końcówek/śrub. Zapisano i usunięto z tej alokacji dwie wspólne przyczyny: DATA–AUX oraz MIC–S0. Uzupełniony ekran WSZYSTKICH dwunastu przestawionych pełnych banków wobec bieżących modułów wykazał rzeczywisty problem, którego sam ekran22 modułów nie obejmował: **klucz S0 wspólnie z dolnym/ górnym MTA ma4658,284505 /1271,650870 mm³ (oba BRep i wyniki valid, distance0)**. Nie jest to przenikanie pustej rezerwy kabla. Dodatkowo S1/stem/nuts/lever wymagają kwalifikacji w tym samym banku; P_SYS/F_PI mają tylko1 mm odstępu BBox od pełnego MTA przy starym kryterium1,25. Nie waivujemy tego i nie nazywamy próby gotowym układem. Dane: whole-bank-operator-cull.json i actual-key-vs-selected-bank.json.

Cztery 615, 15 danych415 + P_AUX415 (razem16 wybranych415), POST412, 12 pełnych MTA0300330 i osiem inline pozostają oddzielnymi jednostkami.

Rachunek jednej niskiej rodziny łuk–S–łuk daje **163,67–188,45 mm wraz z końcami10 liczonymi raz**, promień osi13,5 i większy promień środkowej części. Pozostaje11,55–36,33 mm tej SAMEJ taśmy. Jednak pełny przekrój16,8×1,8 w pięciu pozycjach daje punkty WEWNĄTRZ rzeczywistego BRep łożyska688. **Ten przebieg jest odrzucony.** Nie jest to brak kabla ani dowód braku wszystkich bocznych dróg. Nie wydajemy go do montażu. Fakty: actual-local-bearing-falsifier.json. Surowy wcześniejszy kubiczny przebieg także zachowano jako odrzucony ze względu na promień. Nie wykonano trzeciej próby krzywej.

## Montaż dwóch osób — plan wymagający materializacji

1. P00, rzeczywiste osie i gwinty ramy; bez wymuszania, wiercenia lub cięcia kupnej bazy. Zachować P01 i osiem istniejących osi H01.
2. Wspólny niski nośnik trzeba dopiero wykonać: P01/istniejące osie → ciągła podłoga → stałe siodło głowy i dwie otwarte płaszczyzny elektroniki. Stare A17/N1, wysoki carrier/hood oraz jednostronne słupki banku zostały WYCOFANE jako niezbudowane role; nie zostały uznane za gotowy nowy nośnik. Widoczne źródłowe P02/P03 są odniesieniem podłogi, nie nowym wydaniem STL.
3. Wstępnie przełożyć dwie całe taśmy tekstylne; bateria i dolne pełne zespoły MTA przed zamknięciem górnych odbiorników. Rzeczywista retencja baterii nowym nośnikiem nadal OPEN.
4. Pi: cztery rzeczywiste osie i całe zestawy M2,5 przeniesione sztywno. Narzędzie/nakrętki przed dodatnim bankiem. BUS: cztery źródłowe otwory i pełne aktualne zestawy CSK zachowane. PCA–E1 instalować jako cały lutowany zestaw od góry; nie odpinać fikcyjnie E1. Nowe wspólne podpory/feed/narzędzie nadal UNBUILT, nie fizyczny FIT.
5. Ułożyć wszystkie pełne FHAC, WAGO i końce przy otwartym wierzchu; S1 na przednim panelu ujemnego boku. W043 ma jeden analityczny plan84,5=70,5+14, ale rzeczywisty ustnik/strip/R pozostaje jednym testem próbki. XA01 nie dostał nowego przedłużenia.
6. Po prawdziwym przyjęciu bocznego przejścia przy688 ułożyć cały FFC200 i ToF/JR. USB_DATA500 ma własną warstwę R30 nad WAGO, oddzielną od POWER/K1474. Sama pojemność pierścieni nie kwalifikuje transportu całej500; pełna droga i zapasy pozostają OPEN.
7. Dopiero po ręcznym ułożeniu i kontroli przyłączy zamknąć rzeczywiste osłony. Obecny obrys nie ma jeszcze ścian, kołnierzy, podziału256 ani zatwierdzonych otworów operatora/chłodzenia/akustyki. Sporadyczna wymiana baterii może wymagać rzeczywistego demontażu; nie deklarujemy szybkiego serwisu.

## Uczciwy wygląd, masa i następny krok

Wysoki hełm/łuk wycofano. Obrys tułowia ma X−147..178 (325), maksymalną szerokość220 i grzbiet184; głowa jest osobną bryłą proponowanej formy z otworami optycznymi. **Ocena własna: wygląd nadal NIEPRZYJĘTY** — wciąż długa prosta dolna linia i niewykonane rzeczywiste przejścia/otwory. Nie traktować ciemnej bryły jako zamkniętej gotowej skóry. Pokazano wystające elementy, nie retuszowano obrazu.

Środek geometryczny samej płytki Pi obniżono145,8→97,0 mm. Nie oznacza to znanego COM całego modułu ani kota. Nowa masa materiału NIE została policzona: podpory i lekkie ściany nie istnieją jeszcze; prowizorycznych pełnych objętości nie wolno ważyć jako PETG. Dawne+69,384g to koszt wycofanej propozycji, nie gwarantowana oszczędność.

**Pierwsza następna decyzja CAŁOŚCI:** przerwać/reorganizować własny ujemny bank wokół całej strefy operatora S0/S1 i ogona, zachowując12 pełnych jednostek i ich końce. Nie przesuwać samego klucza/łba ani dorabiać osłony na konflikt. Równocześnie wspólnie zrealizować odbiór przewodów na zewnętrznym boku688 i funkcję ramy czujników. next-whole-decision.json opisuje potrzebną organizację operator–bank i odbiór taśmy, bez kolejnej nowej pozy CAD, bez wydłużania kabla i bez twierdzenia o pełnej wykonalności. F0 pozostaje jednym z rzeczywistych ograniczników długości; nie dostał nowej pozy.

Minimalne fizyczne niewiadome: jedna Pi/FFC/cooler/DATA/POWER próbka; rzeczywisty MG/JR/horn/bearing; cztery wymagane MTA0100335 kwalifikowane jedną właściwą próbką pełnego zespołu; rzeczywiste ustniki FHAC/WAGO i delivered PCB. Nie zamieniono ich na fałszywe pudełka. Pozostałe budżety fizycznych jednostek są jawne w physical-unit-budget-and-unknowns.json. Cały kot, masa/ładowność, ruch i wygląd pozostają OPEN; physicalPASS=false, actualfit/cut/slack=NULL.

Plik build-proposal.py jest surowym pierwszym checkpointem, nie końcowym generatorem. Bieżącą wersją jest zapisany native oraz jawne delty. Źródła/negatywy nie zostały nadpisane.
