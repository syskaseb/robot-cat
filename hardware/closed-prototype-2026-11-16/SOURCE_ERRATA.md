# Aktualna errata źródłowa — MTA0100335 i granice dawnych kopii

**Ta errata ma pierwszeństwo przy czytaniu bieżącego przewodnika oraz historycznych kopii bazy/ADD7/mapy160 w `reference/`.** Nie zmienia ID ani końców połączeń. Unieważnia nieudowodnione gabaryty i długości MTA0100335, nie wybiera nowych części.

## Co zostało sprostowane

Cztery `Leg_protected_MTA0100335_0..3` powstały przez `assumed(...)` jako **BOX35,5 × 8,1 × 8,9 mm**, bez źródłowego powiązania obrysu i bez osobnego aktora wkładki MINIVAL. To nie jest zatwierdzony korpus oprawki. Konstruktor: `hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day14-fasttrack-first-fit/day14-firstfit-build.py`, SHA256 `f1b1deba2c9a00f5ad87dcce666d9694d2eda10c834fc342b64eba1836a79bbf`.

**Ani220 mm, ani84,5 mm KAŻDEGO końca nie zostało źródłowo związane z MTA0100335.** Liczba84,5 mm należy do konserwatywnego planowania wybranego FHAC0001ZXJ; nie wolno przenosić jej na oprawki MTA nóg. Cztery niezależne precrimped przewody E2/JPWM225/min220 pozostają osobnymi jednostkami; nie są wiązkami MTA.

- [Katalog producenta MTA, strona75](https://www.mta.it/flex/TemplatesUSR/assets/pdf/MtaCatalogo_Product_Catalogue.pdf):0100335, „WP MINIVAL FUSEHOLDER WITH CABLE 4mm² L=140 mm”. SHA odczytanego PDF przypięty w receipcie Lorentza: `1df52bc9a5c2f172cc0fac8c700db506e27fbb07da9f18c68d4d132ca219df54`. Katalog pokazuje korpus, pokrywkę/więzidło, wyjścia i osobną wkładkę, nie wymiaruje kompletnego obrysu ani bezpiecznego docisku.
- [Starszy katalog MTA, strona58](https://www.mta.it/flex/TemplatesUSR/assets/pdf/1500000115000001Cat_AM.pdf) podaje L120. Rewizja dostarczonego wyrobu, datum długości i długość KAŻDEGO przewodu pozostają **UNKNOWN**. Nie przyznajemy140 ani120 każdemu końcowi jako budżetu.
- [Rysunek podlinkowany przez TME](https://www.tme.eu/Document/c5516727ef4ab9c31542efe67a3aa5dc/0100335.pdf) opisuje **CHE YEN201-101**, bez potwierdzonego cross-reference do wybranego MTA0100335. Nie stosować jego gabarytów ani długości do tego projektu.

Źródło korekty: odebrany przez mastera readonly receipt Lorentz308, input `01a1e308-6c7a-76c0-9e55-427db95560ed`, `2026-11-16T06:30:00Z`, stan `RECEIVED_SOURCE_ONLY_NO_GEOMETRY_PASS`; porównano SHA lokalnego konstruktora. Tutaj przeniesiono konkretną erratę z odbioru, nie wykonano nowego audytu elektryki ani katalogu.

## Jedna rzeczywista próbka nogi, osobno od próbki banku

**MTA0100335 + wybrana MINIVAL10A (noga):** na JEDNYM egzemplarzu zmierzyć zamknięty korpus z pokrywką/więzidłem i wkładką, dwa wyjścia/odciążenia, długość każdego przewodu od jawnie zapisanego datum oraz bezpieczne miejsce oparcia/kotwy. Zachować oba pełne fabryczne końce. Zdjęcie z linijką i zapis interfejsu wystarczą do związania danych; nie mierzyć produkcyjnie wszystkich czterech.

**MTA0300330 + obie TE + ATO (bank serw):** to INNA oprawka i inna próbka panelu/zatrzasku; sprawdzić kolejność housing → żeńskieTE → ATO. Jej dopasowanie nie kwalifikuje0100335/MINIVAL.

## Konsekwencja dla tego snapshotu

Dopasowanie czterech oprawek nóg, regionów ośmiu inline i P_AUX względem powyższego BOX pozostaje **UNBOUND**. Mapa przypisań FL W026/W041, FR W037/W042, RL W044/W045, RR W052/W053 zachowuje znaczenie logiczne, lecz nie dowodzi odległości, kotew ani dostępnej długości przewodów MTA. Nie ma wymogu pojedynczej listwy8 zaS0 i nie ma zgody przesunięcia/zwolnienia całego kitu na podstawie placeholdera.

Znana kolizja, brak fizycznego korzenia/mocowania albo niewłaściwy model źródłowy nie jest tolerancją do odłożenia jako późny FIT. Rzeczywista rewizja, wymiary i bezpieczne pola docisku są zadaniem konkretnej przymiarki. POWER/P11 kończy się w swoim zakresie; nie dodawać nowej architektury sprzęgieł/kosmetyki dla obejścia tego braku.

Wszystkie pliki pod `reference/` są dokładnymi, niezmienionymi kopiami historycznych źródeł. Pozostawione tam wartości35,5/220/84,5 dotyczące MTA nie otrzymują aktualnego kredytu. Surowe SHA pozostają zachowane; bieżące przewodniki czytać razem z tą erratą. Nadal **PARTIAL_CONDITIONAL_FIRST_FIT_NOT_WHOLECAT**, bez physical PASS, cięcia, zasilania i nowego źródłowego debetu.

## Jeden bieżący indeks kuracji

W tym pakiecie aktywny jest WYŁĄCZNIE główny `PRINT_INDEX.csv`. Surowe `dowody/eksport-88297036/PRINT_INDEX.csv`, `START_HERE.md` i `HOLD_NOT_FOR_PRINT.json` pozostają bajtowo niezmienionymi źródłami tej odebranej porcji. Nie drukować ich łącznie jako kolejnych zestawów. PróbyP01 i MG_HALF mają tylko jawny zakres z głównego indeksu, nie wydanie całego robota. **Dodatek1462284aa4747e595b182de71efdf2aba370a47d został odebrany.** Jego aktualneP02/P03 zastępują szerszy HOLD tych DWÓCH części z8829 **wyłącznie jako OPTIONAL_CONDITIONAL_STRUCTURAL_DRYFIT_AFTER_P00, EMPTY_BASE_ONLY**. Źródłowe82e8 wskazuje sześć lokalnie zamkniętych interfejsów podstawy/core0missing i dostęp metalu;5e504 nie zmienił tych decków. Nie wykazano konkretnej wady SAMEJ pustej podstawy ani automatycznej zależności jej przymiarki odMTA. Nie jest to odbiór materiału, gwintu, obciążonego robota, PCB lub kabli.

P04 jest świadomie dołączonym niezmienionym łącznikiem qty2 z frozen15Nov: SHA256 `7cfe30c82bdfeefae9d54f990edae33b7727f72cacf6105bb8ca5bb414d695bb`. Źródłowe82e8 `source-pins.json` potwierdza niezmienioną geometrię/pozę obuP04 (jedynie flagaOCCTFree; obiekty nie należą do changed_only), a nie tylko podobny BBox. NoweP02/P03 nie są zastępowane starymi STL.

HOLD P19/MTA, całegoPOWER/W043, nowychP11/P10/keeperów/tool/retencji i pozostałych nieukończonych modułów pozostaje. Ta errata nie rozstrzyga nowej trasyW043 i nie awansuje pozytywnych lokalnych wyników do wholekitPASS.
