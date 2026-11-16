# Wynik okna 16 listopada — lżejszy kandydat, cel całej sylwetki nieosiągnięty

Nie uzyskano zaakceptowanego, zwartego i wykonalnego całego kota odpowiadającego robotowi Oli. Zeno, Beauvoir i master ocenili wygląd negatywnie: zbyt długi rurowy tułów, wystające kołnierze oczu, otwarta szyja i mało widoczny ogon. Zaokrąglenie przekroju i końców nie rozwiązało proporcji. To nie jest wynik gotowy do druku.

## Użyteczny wynik

- Zachowane 12 ST3215, 3 MG92B, długość nóg, funkcje dwóch osi głowy i pionowego ogona oraz wybrane wyposażenie, ochrona i fabryczne końce.
- Niska wspólna konstrukcja zamiast wysokiej klatki. Pi, bateria, banki i logika mają nową organizację warstw; nominalne połączenia rusztów/Pi/podstaw głowy i ogona otrzymały pełniejsze zestawy oraz powierzchnie oparcia. Dwa całe pasy baterii obejmują połączoną platformę. Pasowanie i wytrzymałość fizyczne pozostają niebadane.
- Usunięto konkretną koalokację głośnika z pełnym GPIO: nominalny odstęp 112 mm. Nowe położenie głośnika nadal zajmuje niepowiązaną rezerwę MTA0100335 — nie przyjęto całego przodu.
- To samo PETG 1,27 g/cm3: modelowane druki 1778,501 → 1283,436 g, różnica 495,065 g. Pierwotne 664 g po dodaniu realizacji przestało być aktualne. Pokazany nowy osprzęt stalowy około 39,97 g; stary zastępowany osprzęt i brakujące funkcje nie mają pełnego bilansu.
- Wcześniejsze obniżenie dachu o 40 mm dotyczyło pierwszego konceptu. Aktualny dach powłoki Z157,14 zamiast wcześniejszego Z185,20: około 28 mm niżej. Głowa i cały zespół osi ogona zachowują zmianę odpowiednio −20 i −42 mm. To nie dowodzi lepszych wszystkich proporcji.

## Co blokuje całość i dlaczego dotychczasowa korekta nie wystarczyła

Obniżono wyposażenie, lecz zachowano długie szeregi zacisków i szeroko rozłożone kompletne oprawki. Potem skorupę zaokrąglono wokół tej samej rozległej organizacji. Zmiana przekroju nie mogła usunąć źródła długiej bryły, a dodane kołnierze nie stworzyły zintegrowanej twarzy.

Szyny P01 mają 214 mm, osie bioder w X rozstaw 219,62 mm, własne ruszty 348 mm. Powłoka ma około 396×238 mm. Obecna suma ustawień 12 kompletnych MTA/TE/ATO zajmuje około 250,85×194,16×28 mm; 16 WAGO415 w dwóch rzędach 247×188×9 mm. To bieżące zakresy ustawienia, nie najmniejsze możliwe pakiety ani wymiary wymagane przez zakupną bazę.

Wybrana ciągła taśma CSI trafia w ramkę głowy; pełne schowanie 200 mm i ruch nie zostały wykazane. Pełne MTA0100335/lid/tether/końce niepowiązane; obecna rezerwa jest niepewnością, nie potwierdzoną fizyczną kolizją. Dziesięć pełnych końców FHAC, 25 komór, pozostałe jednostki i ich nadmiary nie mają przyjętej wspólnej zajętej przestrzeni. Pozostałe retencje, całe osłony, ich zamknięcie w ruchu i montaż są nadal otwarte. Nie zostało „tylko CSI”.

## Jedna decyzja przed kolejnym CAD

Przeorganizować całą ochronę i zaciski w krótki podłużny rdzeń między obecnymi biodrami, z krótszymi funkcjonalnymi bankami WAGO i pełnymi MTA ustawionymi po zbadaniu rzeczywistych końców. Niska bateria/Pi są punktem wyjścia; własne półki i pozy nie są wymaganiami. Równocześnie przydzielić pełną kasetę ogona, dwie osie głowy, chłodzenie, porty, stock i otwarty montaż dwóch osób. Dopiero wiarygodne całe rozmieszczenie oraz bok/przód/3q mają poprzedzać następną skorupę i uchwyty.

Nie zaprojektowano ani nie przyjęto jeszcze takiego rdzenia. Arytmetyka pól 4×2/2×3 w START_HERE jest tylko uzasadnieniem badania, nie dowodem zmieszczenia modułów i przewodów. Jedna próbka odpowiedniej oprawki MTA0100335, powiązanie ośmiu inline, przykład właściwych FHAC/WAGO/FFC oraz istniejące próbki podstawy/serwa ograniczą konkretne niepewności; nie potrzeba nowego uniwersalnego audytu.

## Obciążenie obecnych serw

W samym umownym scenariuszu 4 kg minus pełna różnica PETG plus cały nowy pokazany osprzęt, bez kredytu starej stali, otrzymuje się 3,545 kg. To nie jest przewidywanie masy gotowego robota. Przy tym scenariuszu i dotychczasowym ramieniu 75,12 mm reakcja pionowa wynosi około 6,66 kgf·cm na cztery równe podpory lub 13,31 kgf·cm na dwie. Poprzedni scenariusz 4 kg dawał 7,51/15,02. Korzyść jest, ale nadal nie ma wykazanego zapasu do chodzenia wobec źródłowych 10 kgf·cm znamionowych przy 12 V. Nie wykonano zasilania, pomiaru temperatury, udźwigu ani fizycznego ruchu.

coordinator-mass-and-load.json zachowuje założenia i źródła; nie traktować przedziału z wcześniejszymi szerokimi masami zakupnymi jako gwarancji końcowej masy.

## Zapisany stan

- Model i widoki: ../day16-low-light-whole-correction/START_HERE.md, commit 6a4534fabd81e7fa409951e83698ad6e82fbf455; parent 34 pliki, 32 hashe, native 5310 poprawnych wpisów CRC.
- Decyzja wspólnej przestrzeni: START_HERE.md, 244ed4ec/84715e26; parent 13 plików i 11 hashy; wszystkie 32 źródła korekty zachowane bajtowo.
- Pierwszy koncept: e7a96e08; zachowany jako wcześniejsza próba, nie bieżący odbiór.
- Brak nowych wydanych STL i brak gotowości całego zestawu. Fizyczne fit/cut/slack NULL, wholekit=false, appearance=false, physicalPASS=false.
- Jedna zapisana GUI FreeCAD/MCP pozostała otwarta; wykonawca i audytorzy bez aktywnych obliczeń. Okno zamknięte przed buforem zapisu; bez automatycznego kolejnego etapu/przedłużenia.
