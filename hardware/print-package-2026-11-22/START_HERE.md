# WAVEGO-kot — komplet do pierwszej przymiarki

**Zacznij od [małego kuponu FIT_S0](sample/FIT_S0_coupon.stl).** Przymierz go z rzeczywistym wyłącznikiem, kluczem, oboma oczkami i osprzętem. Dużą tylną podstawę drukuj po udanej próbie kuponu i sprawdzeniu wejścia baterii. [Instrukcja FIT_S0](FIT_S0.md)

[Pakiet ZIP](WAVEGO_KOT_22_FIRST_FIT.zip) · [Spis druku](PRINT.csv) · [Model FreeCAD](whole-cat22-head-first-fit.FCStd) · [Montaż we dwoje](MONTAZ.md)

W zestawie jest **61 modeli STL na 81 części robota i osobny kupon**. Największa część zajmuje 234 mm z rezerwą na brim i podpory przy polu 256 × 256 × 256 mm. Komplet zawiera też 14 plików STEP i mapę 160 połączeń. Jeśli masz już niezmienione części bazy i nóg WAVEGO, użyj ich ponownie.

## Głowa i przewody

Kamera jest w lewym oku z perspektywy patrzącego, a czujnik odległości ToF w prawym. Maska i tył opierają się na czterech śrubach M2 × 16 z czterema nakrętkami i ośmioma podkładkami. Uszy, wkładki i nos pasują do powierzchni przeznaczonych pod klej. Zestaw ma dwie osie głowy i grafitowy ogon poruszający się góra–dół.

Do kamery przygotuj całą taśmę CSI 15↔15 o długości nominalnej 300 mm. Nowa prowadnica na szynie POST pozwala taśmie przesuwać się przy ruchu głowy. W CAD sprawdzono neutralną i cztery skrajne pozy. Przy montażu sprawdź oba końce taśmy, jej rzeczywisty luz i odstęp od radiatora, a potem zważ złożoną głowę. [Instrukcja głowy i taśmy](GLOWA.md) · [Widok otwartej głowy](22-head-open-csi.png) · [Przekroje mocowań](22-sections.png)

## Kolejność pierwszych przymiarek bez zasilania

1. Wykonaj FIT_S0. Sprawdź oparcie, pełne zazębienie śrub i dostęp narzędzia przy wkładaniu, obrocie i wyjmowaniu klucza. Przygotuj 2 × M6 × 20 DIN 912, cztery podkładki 6,4 × 12 × 1,6 mm i dwie nakrętki M6 AF10. [Instrukcja FIT_S0](FIT_S0.md)
2. Zmierz obie fabryczne żyły baterii i jej dwa pełne wtyki. Układ przewiduje około 135 mm dodatniej i 132 mm ujemnej żyły, z zapasem ułożenia. Przymierz pełne F0 i cztery MTA wraz z odgiętkami, klapkami oraz obiema żyłami przed drukiem dużej podstawy. Zachowaj fabryczne końce i ochronę. [Wejście baterii](WEJSCIE_BATERII.md)
3. Złóż mechanikę i układaj grupy kabli przy otwartym korpusie. Sprawdź nadlewy USB, chłodzenie, końcówki nóg, izolację odczepów R7–R9 oraz luz głowy i ogona. Pokrywy zamknij na końcu. [Połączenia i układanie przewodów](ELECTRICAL_ASSEMBLY.md)

## Bieżące pliki

Drukuj według [PRINT.csv](PRINT.csv). Spis zastępuje dziesięć wcześniejszych plików głowy trzynastoma bieżącymi. W korpusie obowiązują [tylna podstawa 20H](STL/20H_RearBase_CONDITIONAL_AFTER_FIT_S0.stl), przednia rama C20 i trzy adaptery D20. Wiersz kuponu ma zakres poza robotem. Dane 19I i 20H w dokumentach źródłowych zachowują pochodzenie części. Bieżące drogi wejściowe W001, W075, W076 i W066 podaje [bilans wejścia](BODY_FEED_UNITS.json). Nominalny budżet K3/r4 obejmuje 3 m LAPP 0107001 i 9 m HELU 23802. Dostarczone metraże i cięcia potwierdź na egzemplarzach.

[Cały robot z FreeCAD](robot-front.png) · [Zbliżenie głowy](head-three-quarter.png) · [Widok próby S0](FIT_S0-trial-CAD.png)

Zielony walec w widoku pokazuje przestrzeń potrzebną na obsługę klucza S0. W ruchomej szczelinie szyi widać wnętrze. Dopasowanie, rzeczywiste długości i luzy, masa, nośność i chód wymagają prób fizycznych.
