# Układanie wiązek przez dwie osoby — referencja do przymiarki

Czytać [POLACZENIA.csv](POLACZENIA.csv) od ID i końców A/B, a potem [MATERIALY.csv](MATERIALY.csv) po jednostce/grupie. CSV: UTF-8, separator średnik, poprawne cytowanie pól; `NULL` oznacza brak ustalonej wartości, nigdy zero. Numery H to fizyczne piny Pi, BCM to numery GPIO. **Nie podłączać zasilania na podstawie tej referencji.** To mapa do ręcznego układania, nie odebrana trasa, rysunek produkcyjny ani instrukcja uruchomienia.

## Dwa źródła i zakres

- Baza: [design.json](../../../kicad-current/design.json), SHA256 `7be7baa6913fdfa7fe306ef5c33cb3185efd2628ed4001a85acf352ab651ff01`. Zachowane dokładnie 134 ID i pary A/B. To wybrany graf P0/E6, nie ukończony zamknięty kot.
- Bieżący ADD7: [connections.json](../connections.json), SHA256 `c9f6687e6a4419749781f4c7f57ef5b9895cc3a05064fa33b14e1ae0390c6553`, źródło commit`4f325e568ac7157e6b099085212e099b4cd9b35e`. Siedem już wybranych modułów, 26 dodatkowych par, 9 deklarowanych grup. Starszy452cc jest historią. Nie wybieramy części ponownie i nie zmieniamy przypisania pinów.
- W mapie jest 160 wierszy: 134 baza + 26 propozycja ADD7. USB_AUDIO i CSI_CAM to całe interfejsy, nie pojedyncze piny ani 26 osobnych kupnych kabli. `Jednostka_fizyczna_bazy` jest kopiowana ze źródła; `Grupa_deklarowana` nie potwierdza dostarczonego kabla.
- W materiale jest 101 źródłowych porcji korpusu obejmujących 67 unikalnych nazw jednostek, 45 jawnych luk pokrycia bazy oraz 9 grup ADD7. Wiersze luk/grup nie są dodatkowymi jednostkami ani nowym zapotrzebowaniem. Wszystkie rzeczywiste długości zamontowane, cięcia i luzy są`NULL`. Kolumna zapisanej granicy zachowuje wyłącznie ograniczenie ze źródła: nie wolno odjąć od niej starego guide/minimum blank ani uznać różnicy za wolny materiał. Dawny limit250 paryK1474 nie jest aktualną zgodą cięcia ani budżetem nowej trasy.
- Dla kitów nóg SOURCE/DONOR zachowano nazwę i własność źródła; SKU/metraż/końce niepodane w 101 porcjach pozostają NIEUSTALONE. Połączenia fabryczne i lokalne poza body nie otrzymują wymyślonego materiału ani debetu. MG92B250/JR300 to zachowane niezależne jednostki; nie jedna wspólna pula.

## Jedna kolejność ręcznego układania, bez zasilania

1. Osoba A wskazuje ID/koniec A, osoba B identyfikuje koniec B na rzeczywistym module i etykiecie. Najpierw odłączona bateria, rzeczywiste końce, polaryzacja i niezgodności rewizji. Element z nieustalonym końcem zostaje oznaczony OPEN. Zachować ochronę, wszystkie kupne części i fabryczne styki.
2. Ułożyć bazę przy otwartych pokrywach zgodnie z bieżącą kolejnością konstrukcji: dolne nakrętki/korzenie i dostęp przed bankami/P11; cała paraK1474, BUS i pełne zestawy preterminowane/lutowane pozostają razem. Nie odłączać fikcyjnie E1. Wspólne korytarze i kotwy wystarczają; nie trzeba osi każdej żyły.
3. Ułożyć po dwa inline221-2411 przy rzeczywistych MTA0100335: **FL W026/W041; FR W037/W042; RL W044/W045; RR W052/W053**. Fabryczne odcinki są źródłowo84,5mm KAŻDY, custom osobno. To osiem już wybranych inline, nie wymóg pojedynczej listwy8 zaS0. Późniejsze położenie/kotwa i dostęp nadal wymagają rzeczywistej przymiarki. Cztery E2/JPWM225/min220mm KAŻDY są osobnymi precrimped jednostkami XP02.source/module, XP03.source/module, nie wiązkami nóg.
4. Przy nieruchomej części ułożyć IMU, lokalne P0/P1 oraz AMP/SPK przed zamknięciem szyn. Nazwane stałe odgałęzienia3V3/GND i SDA/SCL przyPCA.JP3.3/.4 są propozycją; pola lutowania, izolacja i odciążenie pozostają FIT2. Nie wkładać drugiej żyły w zajętą komorę WAGO. AMP ma osobną parę MAIN5V1, nie6V; zachować W079/W080. Żaden koniec BTL głośnika nie jest GND. Osobny USB_AUDIO ma własny kabel danych; BUS_USB500 bez zmian.
5. Ułożyć cały CSI15↔15 i4 żyły ToF przez yaw/pitch; ustalić rzeczywisty luz/ruch, kotwy, krawędzie i stronę styków. Zachować źródłowe minimum gięcia31,5mm wybranego ToF, bez wymyślonego mniejszego promienia. TTP naH13/BCM27, OE zostajeH11/BCM17; Grove cały, czwarta żyła NC. Przy podnoszeniu ramki MIC/TTP pozostają podłączone z rzeczywistym odciążeniem. A prowadzi końce, B sprawdza ruch/otwieranie i brak przycięcia. Dopiero po zgodności całej trasy/retencji przymierzyć zamknięcie osłon; wynik nie daje zgody na zasilanie ani cięcie przewodów.

## Pięć zapasowych600 → dziesięć końców Pi, warunkowo

Pięć bazowych Pololu1871 female-female600 zostaje bez zmian. ADD7 proponuje użyć obu oryginalnych styków każdej z pięciu zapasowych jednostek; nie powstaje dziesięć niezależnych600. Nie przyjmować300/300. Przed późniejszym ludzkim podziałem w fazie2 suma **OBU tras + zakończeń + potrzebnego luzu + straty cięcia/odizolowania ≤ zweryfikowana długość rodzica600**. Oba styki fabryczne zostają przy Pi, nowe gołe końce przy modułach. Brak pool/pożyczania odpadów/przedłużania. Aktualne cięcia i budżety nadal`NULL`; niespełniona para pozostaje OPEN, bez automatycznego zakupu.

| Rodzic z bieżącego ADD7 | Dwa końce fizyczne Pi |
|---|---|
| GPIO_SPARE_1 | H23 + H24 |
| GPIO_SPARE_2 | H19 + H21 |
| GPIO_SPARE_3 | H16 + H18 |
| GPIO_SPARE_4 | H12 + H35 |
| GPIO_SPARE_5 | H40 + H13 |

## Nazwane przymiarki i otwarte granice

**FIT2 — końce i trasa:** cały rzeczywisty MTA/inline84,5, E2 cztery niezależne jednostki, nierozłączane E1, miejsca lutowania/izolacja/odciążenie, każda para rodzica GPIO, Grove/USB_AUDIO/CSI i dostęp do baterii/wyłączników. Nie używać przydzielonych tulejek FL3 drugi raz. **FIT3 — ruch i styki:** rzeczywiste wtyki/stronaCSI, końceToF, zakres głowy i krawędzie oraz próba jednego MTA+TE/ATO/WAGO; źródłowy model nie potwierdza dostarczonego zatrzasku. Bazowe [FIT_CHECKS](../../../../first-fit-2026-11-15/FIT_CHECKS.md) pozostają zadaniami do wykonania, nie wynikami.

Ochrona nowego odgałęzienia MAIN i wspólny budżet Pi+BUS+kamera+USB_AUDIO+AMP oraz3V3 nadal wymagają osobnych pomiarów napięć/prądu/temperatury przed późniejszą próbą zasilania. F_PI na wejściu nie jest limitem wyjścia5V. Nie wykonano lutowania/cięcia, zasilania, druków ani ruchu. `physical_pass=false`, ADD7 `power.authorized=false`. To referencja montażowa z bieżących danych, bez zmiany źródeł/CAD i bez ponownego audytu160 sieci.
