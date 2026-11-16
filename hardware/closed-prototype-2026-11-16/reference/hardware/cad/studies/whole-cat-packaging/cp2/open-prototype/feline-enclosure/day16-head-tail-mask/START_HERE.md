# Głowa, ogon i maska Oli — częściowy wynik CAD

Bieżący **head-tail-mask.FCStd** zawiera nominalny podzespół konstrukcyjny i propozycję osłon. Nie jest kitem do druku, odbiorem całego ruchu ani złożonym kotem. Trzy opaquePNG i interior przedstawiają ten sam zapis; oczy/nos są jawnie niezamocowanymi referencjami. Bez nowego LED/hardware. Mocowania uszu i szyja OPEN.

## Rzeczywisty materiał i transmisja

P10→dwa608→niezależny journal/pin→widelec→688→sensorplate. Naprawiono wcześniejszą przerwę1mm płyta/ramię. Osobne pokrywy bieżni, dystanse/opory osiowe, pełny metal i realnie zdejmowane siodła serw. P07→wieże/mostek→osobny wkład608→journal/pin→pusta nasada zachowanego łuku ogona. Dziewięć części sprzęgieł valid1solid, dziewięć ich par common0. To dowód podziału, NIE całego ruchu, wytrzymałości ani wszystkich sąsiadów.

Moment: cały fabryczny róg→dwie połówki klucza/pokrywa→niezależny journal→pełny poprzeczny M2→element ruchomy. Ø8łożyska NIE jest wyjściem serwa. Nie drukujemy wieloklinu ani warstwy pod fabryczną śrubą centralną. Historyczna nazwaM3x4 nie potwierdza gwintu egzemplarza. Wspólny krzyż28×16,7/1,95 jest referencją społecznościową Dtto, nie producenta. ONEFIT3 wiąże rzeczywisty róg, śrubę/seat, bieżnie i luzy; bez tego NIE ma potwierdzonej fizycznej transmisji. AtrybucjaAlberto/otrebla333/CC-BY-SA4.0 i LICENSE-Dtto przypięte w source-pins.json.

3pełneMG92B są ze źródłowych6Solids, jawne nowe pozy w mapie. Ich końce/długości nie dziedziczą starych tras. Nowe standardowe śruby/nakrętki/podkładki to UNCONFIRMEDdemand, nie stan magazynu. Dwie nakrętki stałej pokrywy yaw mają rzeczywiste oparcie przy133,7: dolne podkładki wycofane, górne zachowane; aktualnyCSV koryguje pierwotny builder2washers.

## Sensory i maska

CameraPCB25×24/1,12 z primary4otworami21×12,5;2przeciwległeM2/4oparcia. ToF3417: rzeczywistySTEP/primary2otwory12,7, nie8elektrycznych. Całe dotychczasowe capacity są nadal odrębnymi polami, nie pomniejszonymi częściami. Nowe pozy/normalne/końce jawne w mask-sensor-realization.json. WycięciaFOV102×67 oraz45×45 przechodzą przez grubość maski; obaTX/RX wolne, brak założonego szkłaIR. Rewizja, autofocus/header/CSI i ich bezpieczne strefy nadalFIT3.

Przód/tył są osobnymi valid1solid osłonami z zakładką i8nominalM2 do wspólnej ramki. Próba scalenia oczu/nosa zwróciłaNULL BOP; przywrócono dokładny poprawny front z checkpointu. To techniczny brak realizacji dekoracji, nie zaakceptowana utrata materiału. Oczy/nos/uszy nadal potrzebują realnych mocowań. Sam wygląd nie przyjmuje montażu; nie eksportować tej maski jako kompletnego druku.

## Dwie osoby — montaż

1. Na stole ONErzeczywistyMG/róg/śruba/608/688: porównać wspólne parametry, wysokość seat, bieżnie. Bez wiercenia kupnych części. Jedna osoba podtrzymuje podzespół, druga podaje pełne nakrętki/śruby.
2. Korzenie/nakrętki przed bankami. Realne osobne siodła: yaw od dołu, pitch od−Y, tail od góry. Fabryczne centrum skręca się przez journal przed poprzecznym pinem; potem thrust/capy. Integralna belka/E1 nie są wirtualnie odpinane.
3. Sensory na ramkę; całeCSI15×pitch1 i4żyłyToF przed pokrywami. ToFHELU0,5:OD2,1/R31,5. Ciągłe regiony sensor→yaw/pitch→stałe kotwy oraz aktualneLi/range/luz są OPEN; brak starego lengthcredit. FFC17×10 nie dowodzi całej drogi.
4. Początkowe yaw±20°/pitch±10°/tailZ±20° to wybór projektu, NIE zakres dostawcy/kalibracja/ciągły motionPASS. Do odebrania tylko zmienione siodła/capy/metal/skin i pinch, nie stare globalne macierze.
5. Osłony LATE po realnej retencji, kablach, narzędziu i ruchu. NadalOPEN: neckguard/uszy/dekoracje, pełny nowy tool/metal/insertion; bodyBNO/inline8/speaker/S1monitor. Parent dodatkowo ustalił za krótki bezpośredniW043 dla obecnej wyspy zasilania — potrzebna wspólna alokacja, nie przedłużanie.

Bez nowych STL/physicalPASS. fit/cut/slack=NULL. Źródłowe26pliki6ec29029 niezmienione. To częściowy zapis do dalszego domknięcia w aktywnym oknie08UTC.
