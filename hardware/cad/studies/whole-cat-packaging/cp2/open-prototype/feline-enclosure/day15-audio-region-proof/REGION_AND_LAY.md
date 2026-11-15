# Region audio — jedna obsadzona alokacja, HOLD odstępu chłodzenia

Bieżący zapis `audio-region-proof.FCStd` zachowuje cały układ i materiał poprzedniego pakietu. Dodane obiekty to wyłącznie lokalne profile przewodów, ich marginesy oraz przekrój pojemności; nie nowe części ani zwolnienie druku.

## Co rozstrzyga odczyt

Pusty narożnik dawnego `AL_AMP_FREE_TURN_BAY` nie jest przewodem. Zastąpiono ten dowód jedną lokalną ciągłą obsadą: 5×Ø1,6 od górnego dojścia Pi do AMP oraz 2×Ø2,1 od głośnika przez otwarty kanał do AMP. Przy AMP dochodzi siedem funkcji, ale tylko para głośnika przechodzi dolny feed. Nie wymuszano siedmiu przewodów na całej długości.

Każdy profil ma zachowany margines zewnętrzny 0,4mm. Pakowanie zakłada 0,2mm między nominalnymi profilami; kompletne sprawdzenie wzajemne jest NIEODEBRANE (0/21), ponieważ zatrzymano pierwszą bramkę przestrzenną. Przekrój siedmiu profili w 12×20mm jest referencją pojemności, a nie dowodem całej drogi ani dodatkową obsadą. Jego bramka pozostaje nieodebrana.

Jedna geometria normalna/Bishop: górny łuk YZ ma promień osi14mm, U=X, V jest normalną promieniową, bez dowolnego world-roll. Indywidualne promienie wynikają z odsadzeń; minimum11,3mm względem własnej zasady4×OD (6,4/8,4mm). To założenie prototypu, nie promień producenta. Ciągłe nominalne rury są valid/1solid, ich objętość odpowiada πr²L, brak nominalnego profilu poza jego marginesem wynosi0. Nie stanowi to jeszcze prześwitu ani akceptacji kabli.

**Wynik:** odebrane4/84 nowe relacje lokalnej obsady do wybranych sąsiadów; po3dodatnich relacjach pierwszy I2S_BCLK+.4 względem `Pi_components_and_cooling`: valid gap1,184264447mm <1,25, common0. Pełny łuk podchodzi do narożnika rezerwy chłodzenia, mimo pozornie wolnego odcinka poziomego. Regionalny rysunek sam nie ujawniał tego miejsca, stąd jeden dokładny test pełnego profilu. Pozostałe80relacji i21pakowania NIEODEBRANE. To HOLD przydziału z marginesem względem nominalnej rezerwy komponentów/chłodzenia, nie dowód kontaktu dostarczonego przewodu, wszystkich tras ani fizycznej niemożliwości.

STOP tej jednej alokacji; bez drugiego łuku/wysokości, przesuwania AMP/głośnika/Pi lub zmiany materiału. Raw gap0/common0 starego pustego pola zachowany w poprzednim pakiecie. Następna decyzja dotyczy rzeczywistego interfejsu chłodzenia/złączy i układania całej warstwy przed retencją; nie automatyczne nowe podpory z powodu pudełka.

## Końce i dwie osoby — warunkowa kolejność

1. Poza PETG przygotować E1/lutowane końce. A podtrzymuje otwartą konstrukcję, B układa parę głośnika w otwartym feed przed pionową PCA i dociskami. Nie przeciągać fabrycznych dużych końców przez zamknięty otwór.
2. Pi5 układać od góry w otwartym obszarze do AMP; zachować rozdział od pary BTL. Żaden przewód BTL nie jest masą. Dopiero po rozwiązaniu obecnego HOLD oraz realnych końców można zamknąć dociski.
3. Górną ramkę ReSpeaker ORAZ TTP223 montować na końcu, z istniejącym przewodem dotyku. Nie wymyślono rozłącznego złącza TTP. Dostęp do baterii może wymagać częściowego demontażu; nie deklarujemy szybkiego serwisu.

AMP: rzeczywiste pady/header/kierunki UNKNOWN; lewa strona jest jawnym nominalnym założeniem dojścia do przymiarki. Pi: końcowy pinout/wyjście przewodów z pełnego GPIO1992 nieodebrane. Głośnik: terminale i długość przewodu UNKNOWN. Lokalne długości w JSON to tylko fragmenty tego modelu, nie długości całych kabli/cięcia/minimum. USB_AUDIO jest osobną pozycją FIT, bez ponownego kredytu USB500/Delock dla BUS. Cztery niezależne220/obaMTA/FHAC84,5/K1474 i istniejące końce zachowane; actualcut/fit/slack NULL.

## Stan i granice

Wszystkie pozy/materiał/root/BUS/11odebranych modułów zachowane; nie powtarzano61/11/root/BUS. `whole-physical-layout-reference-unchanged.png` jest jawnie niezmienionym widokiem fizycznej konfiguracji poprzedniego pakietu; diagram lokalny i nowe BRep/JSON dokumentują obecny odczyt. Brak nowego materiału/STL. Zasilanie/druk/przymiarki FIT1/2/3 nie wykonane. Głośnik/mikrofon: realne strefy chwytu i otwory akustyczne pozostają nazwanym FIT, bez nowej komory.

Techniczne przerwanie MCP po zapisie HOLD nie jest nową kolizją/porzuceniem geometrii. Zabezpieczono zapisany checkpoint przed odzyskaniem jednego GUI; status natywny w osobnym potwierdzeniu jest obowiązujący. Nie używać obsługi SystemExit w dalszych skryptach MCP.
