# WAVEGO-kot20H — pliki do pierwszej przymiarki

**Zacznij od [kuponu FIT_S0](sample/FIT_S0_coupon.stl) i [instrukcji próby](FIT_S0.md).**
Duża tylna podstawa jest warunkowa: drukuj ją dopiero po udanej przymiarce
rzeczywistego wyłącznika, klucza i pełnego kompletu mocowania.

[Cały pakietZIP](WAVEGO_KOT_20H_FIRST_FIT.zip) · [IndeksPRINT.csv](PRINT.csv) ·
[ModelFreeCAD20H](whole-cat20H.FCStd) · [Montaż dwóch osób](MONTAZ.md) ·
[Wejście baterii/S0](WEJSCIE_BATERII.md) · [Połączenia elektryczne](ELECTRICAL_ASSEMBLY.md)

Pakiet zawiera **58modeli na78drukowanych części robota i jeden osobny kupon**,
STL w orientacjach z indeksu, STEP-y zmienionych części, modelFreeCAD,
mapę160połączeń oraz źródła wybranych57pozycji+7dodatków. Największy gabaryt
z przewidzianym brimem i rezerwą podpór wynosi234mm, wobec pola256×256×256mm.
Indeks obejmuje komplet. Niezmienione, posiadane elementy bazy WAVEGO i nóg
można wykorzystać ponownie; nie trzeba ich drukować drugi raz.

## Co zostało przygotowane

- Nieruchoma strona XT60–F0–POST, krótki odcinek przed bezpiecznikiem,
  dostęp do obu korpusów złącza i rozłączenie połówki baterii o14mm.
- Zdejmowany górny mostek drzwi zachowujący podparcie banków; miejsce na
  ręczne przełożenie obu fabrycznych wtyków i elastyczne ułożenie przewodów.
- Cztery oddzielne małe regulowane uchwytyMTA, trzy adaptery wejścia,
  poprawiony kandydat podstawy z gniazdemS0 oraz jego mały kupon.
- Oba pełne oczkaS0, regiony ułożenia przewodów ze źródłowym R25,2mm
  i kolejność montażu przygotowanegoS0 przed lutowanymE1.
- Zachowane wszystkie wybrane moduły, ochrona, fabryczne końce, obecne nogi,
  12ST3215+3MG92B, dwie osie głowy i rzeczywisty ogon góra–dół wokółY.
  Tułów pozostaje zaakceptowaną prostą skrzynką.

## Najbliższa praca fizyczna — bez zasilania

1. **FIT_S0:** kupon56×57×3mm, centralneØ24 i dwaØ6,5 w rozstawie38mm.
   Potrzebne są rzeczywisty S0/klucz/oba pełne oczkaM10 i nominalnie
   2×M6×20DIN912,4podkładki6,4×12×1,6 oraz2nakrętkiM6AF10h5.
   Sprawdź oparcie, pełne zazębienie, narzędzia oraz klucz przy wkładaniu,
   obrocie i wyjmowaniu. Modelowy zielony walec jest rezerwą obsługi,
   nie dokładnym kształtem części. Ilości dostarczone są niepotwierdzone.
2. **Bateria:** zmierz osobno obie żyły od wyjścia izolacji do wejścia
   w sztywną odgiętkę oraz pełne końce. Pokazany układ przewiduje około
   135mm dodatniej i132mm ujemnej żyły, z zapasem ułożenia już wliczonym.
   To projektowa droga, nie deklaracja długości dostawy. Uwzględnij także
   mały fabryczny wtyk. Stara pętla208mm nie jest wymaganiem tej wersji.
3. **Pełne F0 i4MTA:** przymierz korpusy, klapki, uwięzi, obie żyły
   i odgiętki do małych uchwytów przed drukiem dużej ramy. Gabaryty
   planistyczne nie zastępują pomiaru egzemplarzy.
4. **Pierwszy montaż:** sprawdź nadlewyUSB i chłodzenie, pełne końce nóg,
   wykonanie/izolację odczepówR7–R9, ułożenie grup i luz przy potrzebnych
   ruchach. Zamykaj pokrywy na końcu. Szczegóły w instrukcjach.

Jeśli FIT_S0 nie przejdzie, wstrzymaj dużą podstawę i zanotuj konkretne
wymiary z instrukcji kuponu. Nie usuwaj klucza z działającego robota,
nie skracaj fabrycznych przewodów i nie dodawaj przedłużki baterii.

## Które pliki są bieżące

Drukuj według [PRINT.csv](PRINT.csv). Kandydat
`20H_RearBase_CONDITIONAL_AFTER_FIT_S0` zastępuje `C20_RearBase` oraz dawną
`E19_RearBase`. Nie drukuj obu wersji. `C20_FrontFrame` zastępuje dawną
`H19_FrontFrame`; trzy adapteryD20 zastępują stare mocowaniaF0/POST20C.
Wiersz kuponu ma zakres poza robotem. STEP-y służą do edycji w układzie
złożenia; orientację druku podajeSTL i indeks.

[Przód3/4](robot-front.png) · [Bok](robot-side.png) ·
[Widok próbyS0](FIT_S0-trial-CAD.png)

To rzeczywiste obrazy bieżącegoCAD, bez upiększania. Zielony walec przy
wyłączniku jest przybliżoną rezerwą klucza. Przymiarka rzeczywistego klucza
pozostaje otwarta. Historia19I w `reference19I` nie jest bieżącą listą cięcia.
Aktualny [bilans wejścia](BODY_FEED_UNITS.json) zastępuje dawne dojścia
W001/W075/W076 orazW066. Pozostałe jednostki źródłowe są zachowane.

Nominalny wybrany budżet K3/r4 to3mLAPP0107001 i9mHELU23802. Dostarczone
ilości wymagają potwierdzenia. Wszystkie wartości cięć i rzeczywistych luzów
pozostająNULL. Objętość pełnego materiału druków odpowiada około1,39kgPETG;
rzeczywista masa zależy od wykonania. Nośność, chód i kalibracja wymagają prób.

**Stan: kompletny warunkowy zestaw cyfrowy do pierwszej przymiarki,
nie potwierdzenie zmontowanego ani działającego robota.**
