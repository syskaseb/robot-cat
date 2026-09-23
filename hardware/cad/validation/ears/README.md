# Uszy E1 — obła małżowina inspirowana referencją Oli

Punkt wejścia: `hardware/cad/assembly/RobotCatEars.FCStd`.
Właściciel geometrii: `hardware/cad/modules/head/HeadEars.FCStd`.
Status: **PROTOTYP, nie wydanie do druku**. Nie przebudowano pyska, nóg,
korpusu ani napędu ogona. Poprzednik R4 pozostaje na dysku bez zmian CAD.

## Konstrukcja

Dwie małżowiny PETG, każda z szeroką podstawą, wypukłym tyłem, wklęsłym
wnętrzem i zaokrągleniem czubka R0,8. Sześć przekrojów eliptycznych tworzy
gładki loft zewnętrzny, cztery — wybranie. Wysokość całej części ok. 60 mm;
część podstawy zachodzi w obrys tylnej półskorupy. Nie są to dekoracyjne
siatki. Są natywne loft/pocket/fillet/boolean i 31 w pełni związanych szkiców.
Wymiary elips określają długości ich odsłoniętych osi, nie blokada Block.

Każde ucho: dwie nominalne śruby stalowe M2x12, dwie nakrętki M2 (AF4,
wysokość 1,6). Osie w układzie robota: X=-122/-112, Y=-32/+32, kierunek Z.
Szczeliny nakrętek otwierają się ku tyłowi (+X); łby są wewnątrz głowy.
Otwory Ø2,4 są ślepe od strony małżowiny; górna granica Z=176.
Pod łbami dodano cztery cylindryczne podparcia z płaskimi powierzchniami,
przycięte do dziedziczonej powierzchni głowy. Uszy mają zgodne siodła.

Powierzchnia oparcia łba nominalnie 9,33 mm², nakrętki 6,82 mm²;
nominalna śruba wystaje 0,4 mm za nakrętkę. To obwiednie nominalne,
**nie zweryfikowane modele dostawcy**, nie model gwintu i nie dobór momentu.
Nie kupowano żadnych elementów ani nie zatwierdzono dostępności nowych śrub.

## Montaż i serwis

1. Na zdjętych uszach wsunąć nakrętki od tyłu nasad.
2. Przyłożyć uszy do tylnej półskorupy. Od wnętrza wprowadzić M2x12
   i dokręcić ostrożnie do płaskich podparć. Nie ustalono momentu dokręcania.
3. Mikrofony montować przed zamknięciem głowy; pozostawić dostęp wymagany
   przez wcześniejszy audyt v33. Tylną półskorupę z uszami zakładać później.

Próba narzędzia obejmuje nominalny trzpień R1,7: wejście przez otwarty
przedni podział głowy i ruch ku łbowi. Nie obejmuje dowolnej rękojeści
śrubokręta, przewodów ani fizycznej próby montażowej. Nakrętki są sprawdzane
w kilku położeniach wsuwania, nie jako matematycznie ciągła obwiednia ruchu.

## Złożenie i własność

Wymieniono EarL/EarR/HeadRear na odnośniki do modułu E1. Usunięto z tej
wersji dwie osobne dekoracyjne wkładki i ich blokady — wnętrze jest teraz
częścią tego samego wydruku. Dodano osiem łączników handlowych i ich Fixed.
**335 części, 321 Fixed, 13 Revolute, 65 odnośników, 11 dokumentów.**
Uszy są teraz Fixed do HeadRear, a nie do ramy. Znika 4 z 29 blokad TEMP;
**25 pozostaje**, w tym odziedziczone mocowanie głowy. Ta zmiana nie dodaje
napędzanego obrotu głowy ani nie zatwierdza jej mocowania do szyi.

## Dowody i ograniczenia

- `module.json`: kontrola brył, 31 szkiców, par części, miejsc podparcia,
  wsuwania nakrętek, narzędzia i trzech zmian parametrów.
- `assembly.json`: świeże otwarcie z przeniesionego katalogu, kontrola
  324 niezmienionych części, odnośników, parametru otworów i 22 klatek
  natywnej animacji (nogi ±3°, ogon ±30°). To nie nowa symulacja Gazebo.
- `migration.json` i `assembly-plan.json`: jawne dodania/usunięcia i SHA-256.
- `head-ears.png`, `robot-ears.png`: podglądy rzeczywistego modelu FreeCAD.

Wynik końcowy: **79 testów CAD zaliczonych**, 22 klatki natywne bez zerwania
połączeń, 11 dokumentów otwartych z przeniesionej kopii bez zależności poza
nią. Sprawdzenie manifestu obejmuje 153 pliki. Kontrola `--require-print-ready`
ma nadal kończyć się odmową — to nie zatwierdzenie wykonania robota.

Dziedziczona tylna półskorupa ma błędy strict BOP (C0 i krzywe na powierzchni).
Nie ukryto ich: globalna bramka geometrii pozostaje FAIL. Jej BRep zachowano
bez przekształcania powierzchni: to bazowa bryła ze starym położeniem w
kontenerze o położeniu jednostkowym. Nowe cechy dodają tylko podparcia/otwory.

OCCT 7.8 zwracał niewiarygodne różnice Boolean dla niemal identycznych
przeliczonych loftów. Test przywracania parametrów jawnie używa wszystkich
wierzchołków, dwukierunkowych próbek powierzchni (<0,0001 mm), całkowanej
objętości (tolerancja numeryczna 2 ppm) i strict BOP uszu;
**nie jest to dokładny dowód równoważności Boolean/Hausdorffa**.

Test przeniesienia ujawnił odnośniki PropertyXLink do kopii FreeCAD AI w
AppData. Zresetowano 26 odnośników modułów HeadEars/TailCartridge z pustego
dokumentu roboczego i dodano test Document.xml odrzucający ścieżki kopii.
Nie zapisano żadnego historycznego właściciela części.

## PETG / pole 256³

Oba uszy i tylna półskorupa mieszczą się w polu z zapasem na 20 mm obwiedni
technologicznej. Dla uszu proponowana orientacja: długość małżowiny w
płaszczyźnie stołu, wypukły tył na podporach; wnętrze skierowane ku górze.
Ogranicza to poziome linie osłabienia w poprzek wysokiego ucha, ale wymaga
oceny podporowania, mostów gniazd nakrętek i wykończenia wypukłego tyłu
w slicerze. Alternatywy należy porównać na próbce, nie zatwierdzać z BBox.

Dysza, warstwa i profil PETG pozostają nieustalone. Przed drukiem właściwym
potrzebne: kupon Ø2,4/gniazda 4,3×2,2, sprawdzenie najcieńszych ścian/rantu,
próba mocowania, nośności warstw i pełzania pod śrubami. Brak zgody na
druk całego kota: odziedziczone błędy i pozostałe bramki nadal otwarte.

## Zmiana metadanych historycznego R4

R4 wcześniej przypinał zmienny `current-assembly.json` i aktywny plik testu.
Ich identyczne bajtowo wersje przeniesiono do podkatalogu `checkpoint/`
w dowodach R4 i skierowano tam dwie pozycje manifestu. Hasze pozostają
te same; żaden stary CAD ani raport pomiarowy nie został nadpisany.
Test R4 sprawdza teraz własny checkpoint, nie przyszłą wersję aktywną.
