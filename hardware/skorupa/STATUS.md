# Stan mechaniki — 2026-09-22

Branch: **`codex/robot-cat-mechanical`**, repo **syskaseb/robot-cat**.
Ostatnie złożenie: [v35](v35/README.md). **Nie jest wydaniem do druku.**
[Historyczne podsumowanie poranne](MORNING-2026-09-22.md).
[v26](v26/README.md) zawiera kolejny audyt części rzeczywistych i dostępu
serwisowego; nie zastępuje ukończonym modelem brakujących mechanizmów.
Na zlecenie użytkownika rozpoczęto konkretny
[dobór części i zebranie modeli producentów](../reference/component-selection-2026-09-22/README.md).
Priorytet: Botland, następnie Kamami; maksymalnie 10 dni oczekiwania.
Pobrano i sprawdzono modele STEP. W v29 wdrożono MG92B ogona;
v30 integruje rzeczywisty BNO085, v31 główne Pololu, v32 ToF w nosie,
każdy z fizycznym mocowaniem do wskazanej części. v33 scala przód głowy
z pyszczkiem i dodaje mocowanie referencyjnego ReSpeaker Lite v1.1.
v35 dodaje fizyczne mocowanie drugiej przetwornicy AUX. Pozostała
elektronika i dwa serwa głowy nadal czekają na integrację.
Pobrano także [źródłowy ReSpeaker Lite v1.1](../reference/head-electronics-2026-09-22/README.md):
dwa otwory Ø2,2, dwa ustawienia bez nominalnych przecięć. W v33 jest na
dwóch podporach z M2×12/nakrętkami. Różnica gabarytów względem wiki,
potwierdzenie rewizji fizycznej, kable i akustyka pozostają otwarte.

## Modułowy pilot AUX — bez zmiany geometrii v35

[Złożenie rozwojowe i dowody](../cad/README.md) są w `hardware/cad`, poza
historycznymi checkpointami. 18 elementów AUX korzysta z odnośników do pięciu
dokumentów właścicieli i wspólnego dokumentu parametrów. 302 części pozostają
snapshotami. Zachowano geometrię 320 części oraz natywne połączenia; test
22 klatek i przeniesienie zestawu do innego katalogu są osobnymi dowodami.
Skille projektu, częściowy BOM/rewizje i kontrola wydań wspierają dalszą pracę.
Nie zmienia to poniższych braków: 29 TEMP, BOP skorupy i brak zatwierdzenia druku.
Oba bazowe pliki v35 pozostają bez zmian. Nie utworzono wydania produkcyjnego.

## Checkpoint v35 — mocowanie przetwornicy AUX

- Rzeczywisty STEP drugiej Pololu D24V90F5, cztery dystanse PETG,
  cztery M2×19/nakrętki. Dwa słupki stoją na płycie ramy, dwa na mostku
  ogona. Nowe otwory i podcięcie jednego słupka usuwają znalezione kolizje.
  Tylne śruby wkłada się przed montażem mostka; serwis bez demontażu
  niezatwierdzony. Zaciski są nominalnymi obwiedniami, wiązka niegotowa.
- 320 części,306 Fixed +13 Revolute, **29 tymczasowych**. 11 w pełni
  związanych szkiców;22 klatki natywnego testu bez otwierania złączy.
  302 odziedziczone części i18 nowych/zmienionych kopii zweryfikowano.
  51 par spoczynkowych bez nowych przecięć ponad0,01 mm³.
- **Pełny audyt BOP nadal nie przechodzi**: odziedziczone błędy skorupy
  nie zostały naprawione. Jej globalna różnica siatek także nie osiągnęła
  limitu. Niezależne kontrole lokalnych prześwitów i ubytku materiału
  dopuszczają tylko włączenie AUX do prototypu, nie wydanie do druku.
- Bilans2,503 kg (2,220–2,968), wzrost1,4 g. **639 testów zaliczonych**;
  [trzy świeże próby Gazebo](../simulation/v35/README.md) bez wykrytego
  upadku: RMS0,565 Nm stanie,0,605/0,681 Nm wolny chód nominalny/cięższy.
  To test nóg z nieruchomą głową i ogonem, nadal bez zatwierdzenia biegu,
  momentu ciągłego i termiki ST3215/PETG.
- [Cały kot](v35/whole-cat.png), [mocowanie AUX](v35/aux-mount.png).
  `ViewAux35.FCMacro` odsłania podzespół przez ukrycie innych części,
  `View35.FCMacro` przywraca całość. To nie geometryczny przekrój.
- Nadal otwarte: dwa napędy głowy, fizyczny orczyk ogona, stare błędy
  skorup, pozostałe mocowania/wiązka, serwis baterii, pasowania i termika.
  Zakupowy bilans nowych mocowań zawiera22 M2×12; jeden wybrany zestaw
  ma20, więc sam nie wystarcza. Niczego nie zamówiono.

## Poprzedni checkpoint v34 — niezależne podparcie ogona

- Uchwyt serwa i dolna podpora w jednym PETG; odkręcany górny blok,
  dwa608ZZ, dystanse, czop i zabezpieczenie osi M3×30. Jeden MG92B,
  sześć wymiennych segmentów zachowane. **Fizyczny orczyk nadal TEMP**;
  pasowania bieżni i nośność/pełzanie PETG wymagają sprawdzenia.
- 306 części,292 Fixed +13 Revolute, **30 tymczasowych**. 25 w pełni
  związanych szkiców. 22 klatki testu natywnego zaliczone; 279 części v33
  niezmienionych i27 nowych/zmienionych kopii porównanych z masterem.
- 83 pary spoczynkowe i13 położeń ogona ±30° bez nowych przecięć.
  Wkładanie serwa wymaga pochylenia/przesunięcia (89 pozycji bez kolizji),
  nie pionowego wsuwania. Moduł składa się na zdjętym mostku: dwie śruby
  podstawy niedostępne pod zmontowanym kotem. Przewód/wtyk i pełny montaż
  orczyka nadal niezweryfikowane; to nie pełna certyfikacja serwisowa.
- [Sześć małych próbek PETG](v34/coupons/README.md), około8,7 g,
  zamknięte STL. Nie jest to zestaw wydruków całego robota.
- [Cały kot](v34/whole-cat.png), [podpora](v34/tail-support.png),
  [wnętrze podpory](v34/tail-inside.png). `View34.FCMacro` odtwarza widok.
- Bilans2,502 kg (2,219–2,967), wzrost77,7 g. 632 testy ROS/CAD/narzędzi
  zaliczone;622 testy wcześniejszego v33 również. [Gazebo v34](../simulation/v34/README.md)
  jest odrębnym testem nóg, z nieruchomą głową i ogonem. Trzy próby bez
  upadku: RMS0,563 Nm stanie,0,606/0,681 Nm wolny chód nominalnie/cięższy.
  Obciążenie wzrosło; nadal brak zatwierdzenia biegu i pracy ciągłej ST3215.
- Pozostają: orczyk, osłona i próby podpory ogona, dwa napędy głowy,
  dawne błędy/przenikania skorupy, pozostała elektronika/wiązka, serwis
  akumulatora, tolerancje i termika. Nie utożsamiać gotowej animacji z
  zakończonym projektem mechanicznym.

## Poprzedni checkpoint v33 — przód głowy i mikrofony

- Pyszczek i przednia skorupa są jednym ciągłym wydrukiem PETG; nos nadal
  odkręcany. Otwór od środka22×29 R2 jest wycięty przed połączeniem pyszczka.
  Rzeczywisty STEP ReSpeaker v1.1 na dwóch integralnych podporach, cztery
  nowe elementy metalowe. Nie jest to zatwierdzenie innej rewizji płytki.
- 289 części,275 Fixed +13 Revolute, **30 tymczasowych**. Trzy w pełni
  związane szkice. 22 klatki testu utrzymują mikrofony i ToF przy głowie;
  sama głowa nadal zablokowana. 283 pozostałe części zachowane numerycznie.
- Pierwszy szkic v33 odrzucony i zachowany w archiwum: błędny drugi otwór
  mikrofonów i odziedziczona topologia starej skorupy. Poprawiono osie otworów,
  śruby są od spodu; montaż nakrętki przed założeniem lewego ucha. Serwis
  zmontowanego kota nadal niezatwierdzony.
- Odzyskana skorupa ma zamkniętą siatkę bez krawędzi non-manifold, weryfikowaną
  niezależnie od FreeCAD. Błędy BOP (w tym SelfIntersect) i kolizje wkładek/szyi nadal OPEN.
  Dawne deklaracje kontaktów głowy nie dowodzą poprawności jej topologii.
- Aktualny bilans2,424 kg (2,147–2,882),622 testy zaliczone. Wyniki świeżych
  prób Gazebo są opisane w [v33](../simulation/v33/README.md); archiwalne próby
  pierwszego szkicu nie walidują poprawionej geometrii. Brak zatwierdzenia biegu,
  momentu ciągłego i wydania do druku.
- Pełny kot pozostawiony w FreeCAD. `View33.FCMacro` odtwarza widok;
  [wnętrze głowy](v33/inside-head.png), [zakres i ograniczenia](v33/README.md).
  Nadal otwarte: napędy głowy, orczyk/podparcie ogona, odziedziczone
  konflikty wkładek/szyi, pozostała elektronika, serwis akumulatora i termika.

## Nocny checkpoint v32 — ToF w nosie i 17 prób Gazebo

- Rzeczywisty STEP Pololu3417, integralne mostki PETG w pyszczku,
  osobny nos z otwartym oknem, dwa M2×12, dystanse i nakrętki.
  Rzeczywisty przepust przewodów22×7 w skorupie głowy. Pole widzenia
  i lokalna rezerwa lutowanych przewodów bez przeszkód; optyka wymaga próby.
- 286 części, 272 Fixed +13 Revolute, **32 tymczasowe**. 7 pełni związanych
  szkiców; 22 klatki utrzymują ToF/nos przy pyszczku. Pyszczek do głowy
  nadal TEMP. 45 par audytu, brak nowych przecięć; **12 starych przecięć
  głowy nadal OPEN**. 276 odziedziczonych części niezmienionych numerycznie.
- Gazebo:2,420 kg (2,144–2,878),17 prób. Stanie RMS0,535 Nm, wolny chód
  0,575/0,651 Nm nominalnie/cięższy. Najszybszy crawl:0,741 Nm i41,4%
  nasycenia dla cięższego modelu. **Limit0,65 Nm, cięższy wariant:
  upadek już w rozruchu przy1,002 s.** Nie zatwierdzono biegu ani termiki.
- 619 testów ROS/CAD/narzędzi. Wszystkie17 prób zachowane, w tym nieudana;
  wczesny brak RMS oznaczony jako brak danych, nie zero. Pełny kot widoczny
  w FreeCAD; `View32.FCMacro` odtwarza widok bez zmiany podpisanego pliku.

## Nocny checkpoint v31 — główna przetwornica

- Rzeczywisty STEP Pololu D24V90F5, dwa zaciski według rysunku producenta,
  sześć dystansów PETG, cztery M2×19/nakrętki. Krótkie dystanse pod mostkiem
  wypełniają szczelinę, by dokręcanie nie odginało podpory.
- 280 części, 266 Fixed + 13 Revolute, **34 tymczasowe**. Dziewięć w pełni
  związanych szkiców; test 22 klatek utrzymał IMU i Pololu przy korpusie.
- 63 pary bez przecięć >0,01 mm³; kontakty podpór i drożność osi potwierdzone.
  Dwa dojścia do zacisku blokuje górna obwiednia `PowerDistribution`:
  trzeba ją zdjąć do obsługi. Nie udajemy pełnej dostępności serwisowej.
- Gazebo: nominalnie 2,421 kg (2,144–2,879); stanie 0,535 Nm RMS,
  wolny chód 0,576 Nm, cięższy 0,649 Nm / 15,4% nasycenia. Trzy próby
  bez upadku; 614 testów ROS/CAD zaliczonych. Wniosek o ST3215 bez zmian.
- Główna płytka 4,8 g według producenta, zaciski po 2 g jako założenie.
  AUX i zakupy niezmienione; temperatura regulatora/PETG niezatwierdzona.

## Nocny checkpoint v30 — IMU

- Rzeczywisty STEP Adafruit 4754 zamiast pudełka; cztery dystanse PETG,
  cztery M2×12 i nakrętki, przewiercona płyta ramy, przepusty w skorupie.
  IMU stoi na ramie, nie na zdejmowanej skorupie.
- Złożenie: 264 części, 250 Fixed + 13 Revolute, **35 tymczasowych**.
  22 klatki natywne, nogi ±3° i ogon ±30°; IMU pozostaje przy korpusie.
- Sześć w pełni związanych szkiców; zero przecięć nowych części w 48
  sprawdzonych parach. Kontakt czterech dystansów i drożność osi M2 potwierdzone.
  Lokalne rezerwy wtyku/przewodu nie są jeszcze kompletną wiązką.
- 249 odziedziczonych części porównano z v29: różnice tylko numerycznego
  zapisu BRep, maksymalnie 1,03×10⁻¹². Wcześniejsze CAD-y zachowane.
- Gazebo: nominalnie 2,419 kg, trzy próby bez upadku. Stanie RMS 0,534 Nm,
  wolny chód 0,574 Nm, wariant cięższy 0,650 Nm / 15,4% nasycenia.
  613 testów zaliczonych. Nie zatwierdzono biegu ani pracy ciągłej serw.
- Pozostaje kalibracja osi/zakłóceń magnetycznych IMU, próby PETG i serwis.
  Orczyk/podparcie ogona i mechanizmy głowy nadal są nierozwiązane.

## Nocny checkpoint v29

- Sześć wymiennych segmentów PETG, wpusty/gniazda i rzeczywiste otwory
  na M2×12 z nakrętkami. Po skręceniu ogon jest sztywnym łukiem, nie
  łańcuchem sześciu aktywnych przegubów.
- Jeden rzeczywisty model MG92B ogona, uchwyt na uszy 27,5 mm,
  mostek do istniejących otworów ramy, 32 zamodelowane elementy śrubowe.
  Z v29 usunięto nadmiarowy napęd ogona; v28 pozostaje nienaruszone.
- Edytowalny master ma 56 faktycznie w pełni związanych szkiców.
  Nowe części PETG mieszczą się w 256³ mm; mocowania wymagają prób PETG.
- Złożenie: 252 części, 238 Fixed + 13 Revolute, 36 blokad tymczasowych.
  Natywne 22 klatki: nogi ±3°, ogon ±30°, połączenia zachowane.
- Audyt: brak przecięć >0,01 mm³ nowych części z pozostałymi w spoczynku
  oraz w 13 próbkach obrotu ogona. To nie pełny ciągły test całego chodu.
- Ruchomy ogon około 55,6 g, obliczeniowe zginanie wałka 0,0437 Nm.
  **Orczyk i niezależne podparcie wyjścia nadal nierozwiązane** — dlatego
  jedno mocowanie ogona jawnie pozostaje tymczasowe.
- Gazebo v29: pełne 252 bryły, masa nominalna 2,416 kg (2,139–2,875 kg),
  ogon zamrożony w pozycji CAD. Próby stania i wolnego chodu bez upadku:
  RMS max 0,534 / 0,573 Nm, cięższy chód 0,650 Nm i 15,3% nasycenia.
  To nie zatwierdzenie biegu ani momentu ciągłego.
- Źródła, zakres testów i dalsza kolejność: [nocny dziennik](NIGHT-2026-09-22.md).

## Wcześniejsze etapy v27–v28: więzy oraz Gazebo

- v27 naprawia 32 mocowania: obudowy pierwszych serw biodrowych poruszają
  się z WConnector, orczyki pozostają przy ramie. Geometria i 12 osi bez zmian.
- Natywny test FreeCAD: 22 klatki ±3°, zachowane wszystkie łączenia.
- [Aktualny CAD uruchomiony w Gazebo](../simulation/README.md): 13 ciał,
  12 osi, rzeczywiste siatki, osiem prób v27 i sześć v28. Aktualne wnioski
  opierają się na ostatnich trzech v28, bez sztucznego limitu prędkości.
  Masa v28: nominalna 2,448 kg, zakres 2,167–2,911 kg; **szacunki**, nie ważenie.
- ST3215 pozostaje kandydatem do wolnego chodu. Nie ma potwierdzonego
  momentu ciągłego ani próby termicznej; nie zatwierdzono biegu.
- W v28 zainstalowano `FrontCoverClearance27.FCStd`, usuwając dwa małe
  przenikania osłony z obudowami serw. Zachowane otwory M3; zaliczony test
  22 klatek natywnych i inkrementalna regresja sześciu pozycji. To nadal nie
  jest pełny ciągły test kolizji całego chodu ani walidacja wytrzymałości.
- Odrzucono podcinanie WConnector, które osłabiałoby okolice otworów M2.
- Przeszło 581 dotychczasowych testów ROS i 22 testy obliczeń CAD.
- Stare PDF-y i prosty URDF nie są już przedstawiane jako walidacja
  obecnej konstrukcji. PDF-ów nie przebudowano.

## Ustalenia już zamknięte

- Wszystkie części projektowane do druku: PETG. Pole drukarki 256³ mm.
- Robot do domu; spodnia osłona nie jest wanną ani podporą akumulatora.
- Lista `docs/plan-zakupowy.pdf`, strona 1: **2 serwa głowy + 1 ogona**.
  Nie ma zgody ani potrzeby interpretacyjnej na czwarte serwo pomocnicze.
- v28 miało 12 natywnych Revolute nóg i 225 Fixed, w tym 64 tymczasowe
  blokady; v33: 13 Revolute, 275 Fixed, **30 tymczasowych**. Fixed nie
  zastępuje rzeczywistego wspornika, śruby ani łożyska.
- Test natywny v28: 22 klatki ±3°, nie pełny chód ani pełne zakresy serw.

## Blokady wymagające konkretnych części / decyzji zakupowej

1. **3 serwa pomocnicze i orczyki.** Użytkownik zlecił dobór, nie trzeba
   ponownie prosić go o linki. Kandydat: 3 x TowerPro MG92B DNG-24409,
   dostępny w Botlandzie. Jest STEP Adafruit 2307 i karta wymiarowa;
   wysokość całkowita różni się między nimi (36,8 vs 35 mm). Do rozwiązania:
   dopasowanie uchwytów, orczyków, podparcia, bilans momentów i zasilania,
   poziom logiczny PWM oraz kalibracja zakresów. Nie zatwierdzono mechanizmu.
2. **Akumulator** — konkretny model, wymiary z przewodami i złączami.
   Obecne 90 × 43 × 19 mm jest przykładem, nie potwierdzonym zakupem.
   Alternatywne 3000 mAh z PDF nie określa jednoznacznie gabarytów.
   Kandydat Gens Ace GEA223S30X6GT ma według producenta około
   106,5 × 35 × 21,5 mm. Znaleziona szybka oferta jest poza preferowanymi
   sklepami; wyjątek zakupowy pozostaje pytaniem do użytkownika.
3. **Warianty elektroniki**: dokument uzupełniający już określa BNO085
   Adafruit 4754 i VL53L5CX Pololu (3417). Ich STEP-y i otwory są zbadane,
   nie należy dalej przedstawiać ich jako nieznanych wariantów.
   Dla AUX zaproponowano drugie D24V90F5 zamiast nieokreślonego 3 A;
   koszt i wymagane lutowanie są jawnie opisane w raporcie. Nadal nie ma
   zatwierdzonych mocowań i bilansu prądu/termiki. Głośnik, moduł IR,
   wyłącznik i oprawka głównego bezpiecznika wymagają dalszego dopracowania.
4. **Dystrybucja zasilania**: PDF wskazuje KAB-06897; karta sprzedawcy
   podaje 154 × 20,5 × 15 mm, a obecna bryła ma 52 × 64 × 14 mm.
   Nie są tym samym modelem. Wymagana decyzja: zakupiona listwa i jej
   rzeczywisty podział czy zmiana na konkretny kompaktowy element.

## Prace do wykonania po zamknięciu interfejsów

- Uchwyt głowy: 2 osie, podparcie obciążeń, orczyki/śruby, mocowania kamery,
  reszty części twarzy; ToF zamocowany w v32, pyszczek integralny z głową
  w v33. Sprawdzenie przewodów przez całą trajektorię nadal otwarte.
- Ogon v29: rozwiązać sprzęgnięcie z dostarczanym orczykiem MG92B,
  niezależne podparcie i osłonę, sprawdzić narzędzia i próby PETG.
  Segmenty i usunięcie nadmiarowego napędu są już wykonane, nie powtarzać.
- Pozostałe mocowania elektroniki oparte o faktyczne otwory, wtyki,
  miejsca serwisowe; BNO085 w v30, główne Pololu w v31, ToF w v32,
  referencyjny ReSpeaker v1.1 w v33. Kalibracja IMU,
  termika, serwis i testy sprzętowe pozostają otwarte.
  Zweryfikować termikę regulatorów i chłodzenia, nie tylko statyczny obrys.
- Serwis akumulatora: obecna tacka/paski/nakrętki blokują wyjęcie w dół.
  Wąska tacka i mocowania na końcach są kierunkiem do sprawdzenia, nie
  zatwierdzonym rozwiązaniem ani powodem do wycięcia ramy na ślepo.
- Pełne nominalne zakresy ruchu i kolizje, luzy na wiązki i narzędzia.
- Ocena cienkich płyt ramy PETG, masa, obciążenia i próbny montaż.
- Komplet STL/3MF, pozycje na stole, BOM śrub i instrukcja kolejności składania.

## Kryterium „skończone”

Brak niejawnych obwiedni zakupowych i tymczasowych blokad w mechanizmach,
każda część zamocowana fizycznie, odtwarzalny raport geometrii i ruchu,
wyjmowanie akumulatora oraz dostęp do elektroniki bez kolizji, drukowalne
części 256³ i instrukcja montażu. Wyniki CAD nie zastępują wydruku próbek,
prób obciążenia PETG, rzeczywistych tolerancji ani pomiarów temperatur.
