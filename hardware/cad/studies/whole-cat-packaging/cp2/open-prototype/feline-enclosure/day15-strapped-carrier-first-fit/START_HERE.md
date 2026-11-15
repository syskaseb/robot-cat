# Carrier baterii/MTA — wynik jednej hipotezy

**HOLD: obecne dwa paski nie zostały zakwalifikowane jako wspólny zacisk P19 do ramy P12. Nie wydano nowego STL ani kompletnego carriera do druku.**

Otwórz `strapped-carrier.FCStd`; bieżący cały układ i stare nieprzyjęte węzły są zachowane. Najważniejszy wynik jest w `actual-two-load-sections.png` oraz `closed-load-path-first-gate.json`. Są to rzeczywiste przekroje BRep w obu aktualnych stacjach X29,5 i52,5, a nie pudełkowy szkic wolnego miejsca.

## Dlaczego nie usunięto tylnej śruby

Obecna zamknięta pętla ma światło Y±21/Z65..86,5 i pełny modelowany pasek2,2mm. W całym15mm pasie każdej z obu pętli **wewnątrz nie ma materiału P12 ani P19: wszystkie4nowe odczyty validcommon0**. Podłoga carriera Z60,8..62,8 leży pod dolnym paskiem Z62,8..65. Dach P12 Z91,3..96 leży nad górnym paskiem Z86,5..88,7; nominalnie2,6mm do dachu. Paski przechodzą przez rzeczywiste otwarte od dołu prowadnice, ale to nie oznacza, że spinają te druki.

Wcześniejsze własne clearance/common0 paska z drukami oraz4stopy na decku są zachowane. Stopy dowodzą oparcia na ściskanie, nie kompletnej retencji przy podnoszeniu/obrocie. Obecna hipoteza wspólnego **obejmującego** zacisku nie została wykazana, dlatego nie wolno na tej podstawie wycofać tylnego węzła. To nie jest dowód niemożliwości wszystkich haków/prowadnic/pasków: ewentualne ograniczenie ruchu po wybraniu luzu wymaga własnego dowodu powierzchni oporowych, drogi wysunięcia i montażu. Tu go nie dorobiono ani nie nazwano gotową kotwą.

Stare rzeczywiste rearM3/S0common60,309861 i P11ROI0materiału pozostają. Nie wycięto łba/tipa, nie przesunięto osi, S0 ani wyposażenia. PełneM3x25/nut/2washers i przód są nadal jawnie nieprzyjętą propozycją; nie ukryto problemu. Nie zbudowano drugiej pętli, nowej podpory ani nowego wariantu ramy.

## Dwie osoby — co wolno przymierzyć, gdzie zatrzymać montaż

1. A podtrzymuje otwarty P19, B wstępnie przewleka dwa CAŁE wybrane paski200 przez istniejące prowadnice. Sprzączki poza feedem, całe reszty w opisanych polach. To przymiarka drogi, nie odbiór zacisku.
2. Cztery niezależne MTA220 i oba fabryczne końce ułożyć otwarcie przed tacką/keeperami; nacisk tylko na potwierdzony plastik obudowy, nie TE. Bez odpinania lutowanego E1.
3. Przedni pełny węzeł i narzędzie przed modułami pozostają do potwierdzenia; ta porcja nie nadaje mu nowego loadPASS.
4. **STOP przed uznaniem tacki/baterii za zabezpieczone.** Potrzebne rzeczywiste dodatnie połączenie P19–rama, niezależne od samego ściskania baterii, albo droga rzeczywiście obejmująca wymagane elementy. W tej porcji nie projektowano kolejnego rozwiązania.
5. Późniejszy serwis po odebraniu mocowania: P14touch pozostaje, micP15 -> BUS/P13 -> rzeczywiste XT60+balance -> bateria. To nadal warunkowa kolejność, nie szybki serwis ani obietnica zasięgu końców.

## Stock i zachowane części

Te same2×RCManiak4982/NSTRIF15200M:15×200mm tkaniny; projektowe210 zawiera sprzączkę, nie dodatkowy lap. Każdy model zachowuje pętlę130,65 +rezerwęclosure20 +całą resztę49,35, bez nowego wymogu25pull i bez cięcia. Rzeczywiste grubość/sprzączka/lap/take-up/padding/wytrzymałość to FIT. Nie dowiedziono fizycznego stockfit. Bateria, wszystkie MTA,4stopy, Pi4/guide, źródłowa rama,57+extras/ochrona/porty/końce i4DATA5plus7G pozostają; actualfit/cut/slack=NULL. Nie powtarzano dawnych macierzy/126compound/F0/PCB/headfamilies. Brak gotowego całego kitu.

## Jedna mała poprawka wyglądu

`whole-opaque-front-three-quarter.png` to rzeczywisty obejrzany widok tego samego układu: cofnięto wyłącznie górny brzeg maski pod pełne złote obramowania oczu (Z133 minus1,25 =131,75). Dolne policzki i wszystkie pełne okna pozostały przez subset, bez ruchu kupnych części; grzbiet/ogon/nogi bez zmian. Piny w `opaque-correction-source-pins.json`. To PROPOSED_NOT_PRINTSKIN, bez STL i bez kolejnej recenzji. `whole-retention-load-context.png` ma tylko kosmetykę ukrytą i przezroczystość P12/P19/baterii dla widoczności pasków; nie udaje skończonej skorupy.
