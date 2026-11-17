# Wspólne mocowania korpusu — nominalny CAD, częściowy eksport

Aktualny model: **common-body-mounts.FCStd**. Wykonano wspólny odbiornik PCA/E1, BUS, BNO, MAIN/AUX i AMP; keeper P_SYS, zamknięte przepusty opasek F_PI oraz rzeczywisty keeper POST. Integralny nośny ruszt i osobne zdejmowane belki mają zachowane materiały, połączenia oraz rzeczywisty podział. Nie jest to przyjęty cały robot ani gotowy zestaw do zasilania.

**Najważniejsze ograniczenie eksportu:** N1_common_front_PCB_frame ma poprawną pojedynczą bryłę BRep i zachowane wszystkie zamierzone składniki, lecz STL nie jest zamknięty. NIE DRUKOWAĆ. Nie nazwano tego pomiarem FIT. Nie wypełniano otworów siatki ani nie zmieniano geometrii, by ukryć problem. N1 przekazano w native/BRep; nieudany plik zachowano z rozszerzeniem .stl.unreceived. Pięć pozostałych STL odczytano ponownie: zamknięte, dodatnie, pod256 z4mm brimu każdą stroną. Obowiązuje wyłącznie current-print-index.json.

## Co jest wykonane

- PCA: cztery rzeczywiste otwory źródłowej PCB, podpory i pełne zestawy M2. E1 pozostaje całym lutowanym zespołem; otrzymało izolujące prowadzenia krawędzi i palce zdejmowanej wspólnej belki BUS. Bezpieczne pola FR4 trzeba sprawdzić na jednym module, bez nacisku na elementy.
- BUS/BNO/AMP: podpory według pierwotnych wzorów otworów. Dla uproszczonych pól instalacyjnych jawnie zastosowano nominalne płaszczyzny PCB, nie udawano dokładnych ustników producenta. Pełne części/koperty pozostawiono. Jedna przymiarka rewizji/annuli pozostaje wymagana.
- MAIN/AUX: całe moduły podniesiono o10mm, razem z pełnymi rezerwami komponentów. Otwarta wspólna płaszczyzna jest nad baterią. Śruby od dołu z pełnymi nakrętkami powyżej PCB; łby wstępnie założyć PRZED baterią. Zmiana końców unieważnia dawny kredyt długości, nie daje nowego.
- Dolny uchwyt MTA: rzeczywiste przejścia dwóch pełnych zestawów AUX oraz obejście nośne pod nimi; części kupne/pełne TE/ATO nieprzycięte. Kolejność: pusty dolny uchwyt, PCB/całe końce, późniejszy górny odbiornik — bez wirtualnego wypinania.
- P_SYS: dolne ustalenie, otwarty środek dźwigni i osobny keeper. F_PI ma kołyskę oraz dwa rzeczywiste zamknięte przepusty opasek. Cały wybrany zapas/zamek opasek sprawdzić przy OTWARTYM montażu; dopiero człowiek po zablokowaniu może przyciąć nieużywany plastikowy ogon. Żadnych cięć przewodów/FFC/pasków tekstylnych.
- POST: rzeczywista podstawa, dwa pełne M2x20, dolne kieszenie pod całe nakrętki, keeper z otwartym polem dźwigni i wybraniem omijającym stały korzeń ogona. Nie zakładano demontażu integralnego korzenia.

486 aktualnych relacji: brak nowego obcego konfliktu.36 odczytów przy nominalnych otworach w nieliteralnych kopertach instalacyjnych pozostaje jawnie niepotwierdzonych fizycznie; nie potraktowano ich jako dowodu nacisku na PCB. Materiał źródłowego rusztu zachowany; reszta zamierzonych składników poza zadeklarowanymi otworami ma brak objętości poniżej1e-8mm³. To nie certyfikat wytrzymałości.

## Przymiarka i dwie osoby

1. P00/osiem otworów i rzeczywisty gwint bazy najpierw. Bez siłowego montażu, wiercenia lub gwintowania części kupnych.
2. N2/N3/N6 można wydrukować do niezależnej przymiarki stołowej właściwego modułu. N4/N5 do pustej bazy po P00. N1 pozostaje BRep-only; nie składać kompletnego korpusu z mieszaniny starych i nowych STL.
3. Puste podstawy, śruby od spodu i nakrętki przed baterią/bankami. Jedna osoba podtrzymuje pełną nakrętkę, druga używa właściwego klucza imbusowego. PCB potem, wspólna belka BUS/E1 i keepery na końcu. Całe E1/fabryczne końce zachowane; pokrywy późno.
4. Druk w lokalnym Z0, PETG źródłowe. N3/N6 płasko; N2/N4/N5 potrzebują oceny podparć spodnich w granicach wskazanego obrysu. Nie uruchomiono slicera/drukarki. Kontrolować rzeczywistą rewizję PCB, plastikowe pola WAGO, klips MTA, zamki/opaski i swobodę narzędzi przed dokręceniem.

## Przewody i reszta

occupied-body-group-corridor.json zawiera rzeczywisty odczyt dwóch pełnych profili BTL pod bankiem, liczbę5+2 przy AMP, rozdzielone gałęzie i jawne niezamknięte końce. To nie przyjęta cała trasa/stock. FFC200 nadal ma poprzednią odrzuconą receptę226,208mm; ToF4×OD2,1/R31,5/JR i użyteczny zapas ruchu nie są zamknięte. Cztery niezależne E2 min220 nie są wiązkami MTA. W078red210 pochodzi z tej samej K1474; prawidłowe lap8+MAINfull12 liczone raz. Pięć rodziców600 dotyczy tylko właściwych ADD7, bez puli odcinków. Actual fit/cut/slack=NULL.

Nie wykonano jeszcze bieżących mocowań speaker/MIC/TTP, panelu S1/monitor, pozostałych banków i pełnego prowadzenia wszystkich jednostek. Cztery MTA0100335 pozostają wymagane/UNBOUND. Osłony są wcześniejszą nieprodukcyjną obwiednią, wygląd nadal nieprzyjęty. Wholekit=false, physicalPASS=false. FIRST/runtime/currentassembly nieedytowane; wszystkie dawne źródła i rawHOLD zachowano.
