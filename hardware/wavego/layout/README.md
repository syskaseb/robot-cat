# WAVEGO: rozmieszczenie naszego BOM-u

Studium montażowe, aktualizacja 2026-09-09. Branch: `codex/wavego-component-layout`.
Model: [WAVEGO_component_layout.FCStd](../WAVEGO_component_layout.FCStd).
Podstawa: aktualny [plan zakupowy](../../../docs/plan-zakupowy.pdf) i
[ADR-0001](../../../docs/adr/0001-prototyp-zasilania-i-modularny-komputer.md).

## Wniosek

Przy pełnym BOM-ie, wymiennym pakiecie i przyjętych rezerwach na złącza
potrzebna jest nadbudowa. Obecna płaska pokrywa nie zamyka proponowanego
układu. Wariant zachowujący dużą listwę zaciskową i głośnik potrzebuje
obwiedni nadbudowy **229 x 132 x 85,48 mm**, liczonej od starej górnej
powierzchni Z=38,52 do Z=124 mm. To propozycja przestrzeni zabudowy,
**nie matematycznie najmniejszy plecak ani gotowa obudowa do druku**.

Wysokiego prostokątnego pudełka nie trzeba zachowywać jako wyglądu kota:
kształt grzbietu można później dopasować do komponentów. Zaokrąglenia, ściany,
żebra, tacki i przewody muszą jednak pozostać poza zarezerwowaną przestrzenią.
Zmniejszenie nadbudowy wymaga przede wszystkim doprecyzowania wiązek i
osprzętu zasilania; ewentualna zmiana głośnika lub dystrybucji zmieniałaby BOM.

Pomarańczowe bryły oznaczają dolną elektronikę, turkusowe górną,
zielone sensory głowy, fioletowe mikroserwa/obszar ogona. Są to kolory
diagnostyczne rezerw przestrzeni, a nie deklaracje materiału kupnych części.
Czerwone obwiednie określają przestrzeń obudów. Żadnej z tych brył nie należy
eksportować jako gotowej części do wydrukowania.

## Co faktycznie zmierzono

- 126 brył źródłowych w neutralnej pozycji, z pełnymi transformacjami rodziców.
- Wszystkie 8 elementów ramy, boków i pokryw; 374 powierzchnie cylindryczne.
  Powierzchnia cylindryczna nie jest jednoznaczna z osobnym otworem:
  zestawienie rozróżnia promienie zewnętrzne, otwory i częściowe łuki.
- 45 poprzecznych przekrojów wnętrza, 9 pozycji X i 5 wysokości Z.
- Zewnętrzne obrysy oraz wzajemne kolizje 26 rezerw komponentów.
- Kolizje z bryłami nóg w 25 fazach obecnego podglądu chodu.
- Próby skrętu i pochylenia obwiedni głowy względem nadbudowy.

Surowe wyniki: [measurements.json](measurements.json),
[validation.json](validation.json). Procedura: [wavego_layout_analysis.py](../../../tools/freecad/wavego_layout_analysis.py).
Do źródłowych modeli oraz ich geometrii nie wprowadzono zmian.
Po korekcie przodu ponownie sprawdzono obrysy, objętości i liczbę brył
wszystkich 126 źródłowych elementów względem neutralnego pomiaru bazowego.

Układ współrzędnych: milimetry, **−X przód, −Y lewa strona, +Z góra**.
Kierunek poprawiono zgodnie z uwagą użytkownika o ustawieniu łap.
Rezerwy elektroniki, głowy i ogona obrócono o 180° wokół pionu przez (21;0),
bez obracania źródłowego podwozia. Kamera patrzy w −X, ogon jest po stronie +X.
Nazwy FR/FL/RR/RL w starym makrze ruchu są historycznymi identyfikatorami
importu, a nie oznaczeniem przodu nowej zabudowy. Przy nowej orientacji
mapowanie do nich to: przód-prawa → RL, przód-lewa → RR,
tył-prawa → FL, tył-lewa → FR. Nie zmieniano osi ani mechaniki nóg.
Środek między osiami bioder ma X=21, Y=0. Wewnętrzne dno leży na Z=0,
spód starej pokrywy na Z=37,02, wierzch na Z=38,52 mm.

| Pomiar | Wynik |
|---|---:|
| Długość między końcami bocznych paneli | 212 mm |
| Szerokość zewnętrzna ram głównych | 100,456 mm |
| Wolna szerokość w przekroju Z=2 | 74,379 mm |
| Wolna szerokość w przekroju Z=10 | 90,379 mm |
| Wolna szerokość w przekroju Z=20 | 95,679 mm |
| Wolna szerokość w przekroju Z=30 | 84,996 mm |
| Wolna szerokość w przekroju Z=35 | 74,996 mm |
| Wysokość między pokrywami | 37,02 mm |
| Górne oszacowanie wolnej objętości starego środka | 0,74869 l |
| Suma przyjętych rezerw dolnej i górnej elektroniki | 1,22406 l |

Ostatnie dwie wartości porównują **rezerwy montażowe**, nie samą objętość
materiału elektroniki. Oszacowanie starej przestrzeni celowo jest korzystne:
od dużego prostopadłościanu odejmujemy bryły robota, pozostawiając nawet
zewnętrzne zakamarki i przestrzeń potrzebną do obsługi. Nie jest to szczelna
komora o pojemności 0,75 l. Z kolei część rezerw serwisowych można przy bardziej
szczegółowym projekcie współdzielić. Wynik uzasadnia proponowany wariant,
ale nie dowodzi niemożliwości każdego gęstszego upakowania.

## Rozmieszczenie

Pełne 26 pozycji, ich współrzędne, wymiary, źródła i stopień pewności zawiera
[components.json](components.json). `size` oznacza zajęty obrys montażowy,
`min` jego dolny narożnik XYZ. `nominal`, jeśli podano, dotyczy samej części.
Nie należy mylić tych wymiarów ani traktować wpisu bez konkretnego modelu
jako potwierdzonego dopasowania zakupionego produktu.

| Element | Rezerwa XYZ [mm] | Miejsce / zamocowanie do opracowania |
|---|---|---|
| LiPo | 120 x 46 x 33 | Na dole, centralnie; tacka z paskiem i miękką podkładką |
| Pololu z ARK | 28 x 52 x 22 | Tył dolnej komory, płytka obrócona w planie |
| Druga przetwornica | 28 x 44 x 25 | Przód dolnej komory; model do dobrania |
| BNO085 | 30 x 28 x 10 | Sztywna platforma przy przedniej ramie |
| Pi 4 / Pi 5 + HAT i chłodzenie | 110 x 76 x 42 | Wymienna tacka nad pakietem, USB skierowane w −X |
| Głośnik z BOM-u | 106 x 51 x 27 | Przednia część nadbudowy, otwory akustyczne z boku |
| Cała listwa 12-torowa | 164 x 32 x 25 | Boczny pas dystrybucji; dostęp do śrub od góry |
| Grove PCA9685 | 68 x 48 x 25 | Nad głośnikiem, odłączane przewody szyi i ogona |
| ReSpeaker Lite | 94 x 43 x 16 | Pod grzbietem; otwory w miejscach rzeczywistych mikrofonów |
| Bus Servo Adapter A | 54 x 43 x 24 | Górny obszar serwisowy, krótki przewód USB |
| 4 oprawki bezpieczników | 4 x (45 x 16 x 16) | Boczny rząd; rezerwa korpusów i końców przewodów |
| Wyłącznik, główny bezpiecznik, XT60 | 70 x 30 x 26 | Górny obszar serwisowy; dokładne części nie są wybrane |
| MAX98357A, TTP223, kondensator | Osobne bryły w modelu | Miejsce przy górnej elektronice; kondensator opcjonalny |
| 4 pary XT30 + TTL | Dwa obszary 24 x 26 x 22 | Rozłączanie przednich i tylnych nóg |
| Dwa serwa głowy + serwo ogona | Osobne rezerwy | Wymagają konkretnego modelu, orczyków i wsporników |

Komputer oraz HAT są jednym wariantem wymiennym. Nie wkładamy Pi 4 i Pi 5
jednocześnie. Ładowarka, zapasowe bezpieczniki, drugi doświetlacz i drugi pakiet
nie jadą na robocie. Kamera i czujnik ToF są w głowie; ReSpeaker pozostaje
w tułowiu, bo ma długą wspólną płytkę 86 x 35 mm.

Pakiet jest na razie ograniczeniem zakupowym: **maks. 110 x 40 x 30 mm**.
Kieszeń uwzględnia dodatkowy luz; pojemność 3000 mAh nie gwarantuje tego
rozmiaru. Wymiana wymaga odpięcia i uniesienia górnej tacki, a następnie
wyjęcia pakietu do góry. Nie przewidujemy wysuwania przez serwa na końcach
ani przeciskania przez boczne panele. Tory przewodów, promienie gięcia
oraz pełny ruch wyjmowania tacki nie są jeszcze zweryfikowane.

## Istniejące otwory i plan mocowania

| Zestaw | Współrzędne osi [mm] | Geometria / przeznaczenie |
|---|---|---|
| Górna pokrywa | X=-80,-70,112,122; dla każdego Y=±22,5 | 8 przelotów Ø2,6, powierzchnia górna Z=38,52 |
| Otwory ram pod pokrywą | Te same X,Y | Ø2,05, górny kołnierz Z=35,52..37,02 |
| Mocowanie boków | Te same X; Y=±31,5 | Przeloty Ø2,6 nad otworami ram Ø2,05; zajęte przez panele |
| Cztery otwory w dnie | X=1,59; Y=±24,5 | Ø2,6, rozstaw **58 x 49**, zgodny z Raspberry Pi |

Proponowana podstawa plecaka wykorzystuje 8 punktów starej pokrywy i przenosi
obciążenie na dwie ramy końcowe. Przednie 4 punkty (X=−80,−70) są także bazą
dla wspornika szyi, tylne (X=112,122) dla wspornika ogona. Nie traktujemy cienkiego środka pokrywy
jako samodzielnej belki nośnej. Mocowanie Pi w tej przymiarce jest odsunięte
od wzoru w dnie: będzie potrzebna tacka-adapter. Słupki puszczone bezpośrednio
od otworów dna mogą kolidować z bokiem kieszeni baterii.

Eksport STEP nie potwierdza rodzaju gwintu, materiału gwintowanego elementu,
zajęcia otworu śrubą ani wymaganej długości śruby. Nie dobierano długości
śrub i nie wykonano otworów pod wkładki termiczne na podstawie samych średnic.
Czerwone znaczniki są **osiami istniejących otworów**, a nie nowymi mocowaniami.

## Głowa i kamera

Proponowana obwiednia głowy ma 82 x 92 x 76 mm, w pozycji neutralnej
X=−183..−101, Y=−46..46, Z=142..218. To przestrzeń do zaprojektowania lekkiej
skorupy, nie koci kształt ani kompletny mechanizm. Szyja musi podnieść głowę
ponad wysoki grzbiet, żeby mogła się obracać.

- Kamera: prawe oko, obiektyw nominalnie **(−180,4; 18; 187)**, patrzy w −X.
- Doświetlacz 850 nm: lewe oko, osobna przegroda optyczna i miejsce na chłodzenie.
- VL53L5CX: nos poniżej oczu; rzeczywisty wariant płytki wymaga potwierdzenia.
- Proponowana oś yaw: pion przez (−117; 0; 123), zakres badania ±45°.
- Proponowana oś pitch: −Y przez (−130; 0; 166), zakres badania ±25°.
- Osie szyi są **propozycją**, a nie osiami wałków kupionych mikroserw.

Kamera Wide ma ok. 25 x 24 x 12,4 mm. Oficjalny rysunek pokazuje płytkę
23,862 mm wysokości i nieco inny wymiar całkowitej grubości; do przymiarki
zostawiono większy obrys z tabeli producenta. Wzór mocowania: **4 x Ø2,2,
21 x 12,5 mm**. Lokalnie względem dolnego narożnika płytki otwory leżą
w (2;2), (23;2), (2;14,5), (23;14,5), a oś obiektywu w (12,5;14,4).
Znacznik w CAD ma płaszczyznę adaptera X=−168; osie otworów mają Y=7,5/28,5
i Z=174,6/187,1. Jej dystans do PCB trzeba
ustalić po wymodelowaniu uchwytu i złącza CSI.

Pole widzenia to **102° poziomo x 67° pionowo**; 120° oznacza przekątną.
Obiektyw powinien być przy powierzchni pyska. Dla cofnięcia najwyżej 2 mm
proponujemy na początek otwór optyczny Ø16 mm: oszacowanie geometryczne
6,95 + 2*2*tan(60°) ≈ 13,88 mm, powiększone o luz. Nie jest to gotowy
projekt uszczelnionej szybki ani wynik testu winietowania. Brwi i obrzeże
oczodołu muszą pozostawać poza narysowanymi promieniami widzenia.

Taśma CSI powinna biec z Pi do podstawy szyi, z odciążeniem na nieruchomej
części i luźną pętlą do ruchomej głowy. Nie można jej zaciskać między
orczykiem a obudową ani zakładać nieograniczonego skrętu. Długość oraz
trwałość pętli wymagają przymiarki wybranej taśmy; Pi 5 potrzebuje innego
złącza niż Pi 4. Przewody LED/mikroserw są osobną wiązką.

## Granice tej przymiarki

Końcowe wyniki: **0 kolizji między rezerwami komponentów, 0 kolizji z
zachowanymi bryłami robota, 0 kolizji z 92 ruchomymi bryłami w 25 fazach
chodu** (sprawdzono też obwiednie plecaka i głowy). W **209 kombinacjach
yaw/pitch** obwiednia głowy nie przecina obwiedni plecaka; najmniejszy
odstęp wynosi **7,9927 mm**. Nie jest to gwarancja dla pozycji między próbkami.
Pełne wyniki znajdują się w `validation.json`.
Wyniki powtórzono 2026-09-09 po obrocie całej przymiarki względem podwozia.
Źródłowa pokrywa i dwa umieszczone na niej drobne elementy są w wariancie
nadbudowy wyłączone; pozostały w pliku do porównania. Kolizja IMU z dawną
pokrywą jest świadomie wykazana w raporcie, a nie ukryta jako pomyślny test.

Przed drukiem wciąż wymagane są: konkretne modele baterii, mikroserw,
drugiej przetwornicy, głównego wyłącznika/oprawki, LED i breakoutów;
projekt tacek, szyi i śrub; pełne prowadzenie przewodów oraz test cieplny,
masy i momentów. Sprawdzenie 25 faz kinematyki nie potwierdza wszystkich
ustawień ręcznych ±60°, ciągłego ruchu, obciążenia konstrukcji ani realnego
chodu. Głowa jest na razie badana geometrycznie poza animacją, nie ma jeszcze
działających więzów dwóch nowych osi w panelu ruchu.

## Otwieranie i ponawianie pomiarów

Otwórz `WAVEGO_component_layout.FCStd` i rozwiń grupę `PACKAGING STUDY`.
Właściwości każdej bryły podają źródło, stopień pewności i uwagi montażowe.
Można ukrywać całe bryły-klatki oraz komponenty, aby obejrzeć kolejne warstwy.
Makro `WAVEGO_Motion.FCMacro` zachowuje teraz osobny plik tego studium zamiast
zapisywać go pod nazwą zaakceptowanego modelu ruchu.

Skrypt pomiarowy wykonuje `inspect(doc)` dla 126 importowanych brył
(pomija dodane pomoce studium), `configure(doc)` dla metadanych i znaczników, `validate(doc)` dla
testów. Przed testami zatrzymaj animację i przywróć pozycję neutralną;
`verify_source(doc)` odrzuci inną pozę lub zmienione obrysy/objętości źródła.
`show_layer(doc, 'lower'/'upper'/'head'/'all')` zmienia widoczność.
`object-map.json` łączy 26 rekordów z bryłami utworzonymi narzędziami MCP.
Przy zmianie rozmiaru/położenia trzeba uaktualnić zarówno bryłę CAD, jak
rekord JSON; walidacja zatrzymuje się przy niezgodności ich obrysów.

Widoki po korekcie przodu: [całość](layout-isometric.png), [bok](layout-side.png),
[dolna komora](layout-lower.png), [głowa i pole widzenia](layout-head.png).

## Źródła wymiarów

- [Raspberry Pi 4: rysunek mechaniczny](https://datasheets.raspberrypi.com/rpi4/raspberry-pi-4-mechanical-drawing.pdf).
- [AI HAT+: obrys, nie dokumentacja wykonawcza obudowy](https://datasheets.raspberrypi.com/ai-hat-plus/raspberry-pi-ai-hat-plus-product-brief.pdf).
- [Camera Module 3 Wide: rysunek](https://datasheets.raspberrypi.com/camera/camera-module-3-wide-mechanical-drawing.pdf) i [wymiary/pole widzenia](https://www.raspberrypi.com/documentation/accessories/camera.html).
- [Pololu D24V90F5](https://www.pololu.com/product/2866/specs): podane wymiary nie obejmują dołączonych zacisków.
- [Bus Servo Adapter A](https://docs.waveshare.com/Bus_Servo_Adapter_A).
- [Grove PCA9685](https://wiki.seeedstudio.com/Grove-16-Channel_PWM_Driver-PCA9685/).
- [ReSpeaker Lite](https://wiki.seeedstudio.com/reSpeaker_usb_v3/).
- [BNO085 Adafruit 4754](https://www.adafruit.com/product/4754).
- [Listwa KAB-06897](https://botland.com.pl/produkty-wycofane/6897-kostka-elektryczna-12pin-16mm-30a250v-5904422357825.html); gabaryty konkretnej pozycji katalogowej, nie porada zakupowa.
- [Oprawki KAB-05473](https://botland.com.pl/bezpieczniki/5473-gniazdo-bezpiecznika-5x20mm-z-przewodami-10szt-5903351245982.html): brak pełnego wymiaru korpusu, dlatego rezerwa pozostaje założeniem.
