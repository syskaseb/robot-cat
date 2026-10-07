# Otwarty prototyp — plan wykonawczy, 07.10.2026

## Zamknięty etap 1: wspólny plan i granice kwalifikacji

Aktualne współrzędne modułów, przypisanie wszystkich80żył, brakujące38końców,
korytarze, kolejność montażu i rozdzielenie20rezultatów zapisano w
`execution-plan.json`. Aktualną kopią odniesienia planu jest
`OpenPrototypePlan.FCStd`; poprzedni `OpenPrototype.FCStd` i źródła zachowano.
Nie jest to wybrany komplet wydruków ani zakwalifikowana pełna wiązka.

Wykryto przyczynę błędu odniesienia MAIN: wyrażenie `MainGap-4` nadpisało
absolutne położenie Z w zapisanym modelu, choć wcześniejszy raport kontaktów
sprawdzał osobną poprawną bryłę. Tylko kopię odniesienia podniesiono o46,52mm.
Nie zmieniono mocowań ani przewodów. Zapis/reopen potwierdza cztery nominalne
pady i zachowanie położeń/struktury BRep pozostałych362obiektów.41różnic
tekstowego zapisu to zaokrąglenia maksymalnie2,22e-16, nie zmienione części.
Przed regeneracją historycznego mastera w etapie2 trzeba poprawić jego
wyrażenie o absolutną bazę świata; nie kopiować ponownie błędnego odniesienia.

E3 pozostaje otwarte: brak gwarantowanej granicy prądu zwarcia źródła,
danych fabrycznych przewodów serw, uzgodnienia F0 z cieńszymi odcinkami
przed bezpiecznikami oraz danych DC/inrush/prądów awaryjnych przetwornic.
Nie zamyka się tych braków obrysem CAD ani obietnicą próby fizycznej.
Nie prowadzono kolejnej bezowocnej pętli kwerend producentów.

Pozostałe przygotowanie fazy1: **12–24h pracy** (9–16h etapów +3–8h rezerwy
integracyjnej), bez czasu oczekiwania na dane E3. To estymacja, nie termin
gwarantowanego100%. Następny checkpoint: jedna wspólna paczka mocowań,
podpór i izolacji,3–5h; pełne trasy/odciążenia i stock są kolejnym etapem.
Minimum nadal **3/20=15%, zmiana0**. Nie zaliczono W1/W5 ani fizycznegoPASS.

Hook ograniczono do etapu1/maksymalnie2h i wyłączono po zapisaniu planu.
14testów izolowanych przypadków hooka PASS;14testów kontraktu starego pakietu
i obie kontrole integralności PASS. Nie zaobserwowano rzeczywistej nowej
kontynuacji Stop: etap ukończono w inicjującym turnie użytkownika.
Etap2 wymaga nowej zgody; bez harmonogramu ani zmiany ustawień modelu.
Przypięte źródła sprawdza `tools/cad/verify_open_prototype_execution_plan.py`.
Czas do zapisania i weryfikacji etapu1:18:16:21..18:57:33UTC=41min12s;
samo okno hooka18:25:05..18:57:33UTC=32min28s. To czas zegarowy pracy,
nie ciągłeCPU. Limit18:57:33UTC:2%użyto,98%pozostało; bez resetów/zakupów.
Reguły skilla planowania CAD zastosowano do wspólnej przestrzeni i kolejności
montażu, a błąd odniesienia usunięto u źródła rozbieżności, nie przesuwaniem tras.

## Zachowany pierwszy checkpoint

`OpenPrototype.FCStd` jest jedną roboczą kopią aktualnego wnętrza CP2,
z nową lewą podporą szyi/MAIN i zachowaną prawą. Źródła pozostają bez zmian.
To kandydat planu przestrzeni, **nie wybrany komplet wydruków ani gotowa wiązka**.
Szare elementy pokazują zachowaną mechanikę; niebieskie — rezerwacje modułów,
nie wszystkie dokładne bryły dostarczonych SKU. Różowe punkty są nazwanymi
zakończeniami prototypu. Widoki PNG pomijają obrys kosmetycznego tułowia,
przekroje oraz budżety dostępu; sam plik zachowuje te pomocnicze obiekty.

## Uproszczenie montażu

- Pierwsze próby bez górnej osłony ciała; proporcje 325×200×160 pozostają bazą
  późniejszej obudowy. Nie poszerzamy boków. Korytarze nad kosmetycznym dachem
  wolno wykorzystać tylko w otwartym prototypie.
- Płytki: znane mocowania zachować; pozostałe przykręcić przez rzeczywiste otwory
  na izolujących dystansach. Nie opierać śrub na samym prostokącie rezerwacji.
- WAGO, oprawki i wiązki: proste przykręcane listwy pod opaski. Nie wymagamy
  wyjmowania całej kasety ani osobnego bezkolizyjnego demontażu każdego modułu.
- Akumulator: podparta tacka P0 i dwa pasy; górna obudowa nie jest jego mocowaniem.
- Serwis po odłączeniu źródła: wolno zdjąć sąsiedni moduł lub wymienić opaski.
  Dostęp ATO można uzyskać taką kolejnością; 74 rutynowe rozłączenia nie są celem.
- Izolacja, zabezpieczenia, chłodzenie, ochrona krawędzi i luz przy ruchomych
  przegubach pozostają wymagane. Lut i krótki odkryty koniec NIE są odciążeniem.

## Jeden podział przestrzeni całej wiązki

`layout.json` przypisuje każdy z 80 przewodów korpusu dokładnie jednej grupie;
zachowuje też 80 par granicy dystrybucji, w tym 22 pary spoza korpusu.
To dwa różne przekroje połączeń, nie 160 dodatkowych przewodów.
Wszystkie przestrzenie mają jawne współrzędne; są rezerwacjami do uzgodnienia
z końcami i uchwytami, nie dowodem braku kolizji wszystkich tras.

| Grupa | Przewody korpusu | Pary granicy | Montaż/obszar |
|---|---:|---:|---|
| FL / FR | 17 / 16 | 15 / 14 | Osobne przednie wiązki, podparte nad bankami |
| RL / RR | 16 / 15 | 14 / 13 | Osobne tylne wiązki, poza ruchem nóg |
| MAIN_PI | 5 | 1 | Dolny pas zasilania i osobny lut F_PI |
| SOURCE_SWITCH | 8 | 6 | Źródło, F0, S0 i ręczny S1; zachowane krótkie odcinki |
| AUX_BRANCHES | 1 | 5 | Gałęzie bezpieczników; oprawki podparte, nie na przewodach |
| LOGIC_AUX | 1 | 5 | Górny pas sterowania; chłodzenie i złącza dostępne |
| USB_BUS | 1 | 1 | Kabel fabryczny bez cięcia, nadmiar podparty osobno |
| HEAD / TAIL | 0 / 0 | 2 / 4 | Wyjścia poza korpus z zapasem na ruch, nie sztywnym mostem |

122/160 końców korpusu ma teraz jawne punkty nominalne. Pozostałe 38:
36 końców serw nóg i BUS.D/BUS.G. Nie uznajemy środka obrysu za terminal.
Zakończenia przy serwach trzeba związać z ich fabrycznymi przewodami i ruchem;
budżet nominalny do przymiarki nie zastępuje rzeczywistego pomiaru.

## Zamknięty lokalny wynik

- Ustalono trzy brakujące role zasilania MAIN: lut W078 oraz końce USB W079/W080.
  Położenie USB wyprowadzono z zachowanej recepty kabla i aktualnego datum Pi,
  nie ze środka jego obrysu. Rozmieszczenie pól MAIN nadal jest prowizoryczne.
- Obie nazwy SPLICE_PI oznaczają jeden izolowany lut, nie dodatkowe WAGO.
- W077: 67,472 mm nominalnej linii, 75,472 mm z 8 mm odizolowania;
  wobec minimum fabrycznego 84,5 mm pozostaje 9,028 mm. OD/R są założeniami
  projektu; ciąć dopiero po przymiarce. Dwa sprawdzone kandydaty par brył,
  zero przecięć i błędów Boolean. Uchwyty, tuleja i pełna droga MAIN nadal otwarte.
- 14 testów kontraktu PASS; zapis i ponowne otwarcie modelu PASS.
  Brak nowych drukowanych części w tym checkpoincie.

## Następna bramka, bez pętli mikroprzesunięć

1. Związać 38 pozostałych końców z fabrycznymi przewodami/portami, zachowując
   polaryzację, promienie i luz ruchu. Dokończyć cztery odciążenia przy MAIN.
2. Jedna wspólna paczka mocowań: rzeczywiste otwory płyt, listwy/opaski
   dystrybucji i podparcie izolowanego lutu. Śruby i punkty zaczepu uzgodnić
   względem P0, nie zawieszać uchwytów w powietrzu.
3. Sprawdzić tylko zmienione styki/ruch/montaż; po dwóch nieudanych próbach
   tego samego interfejsu zmienić przyczynę lub układ, nie kolejne przesunięcie.
4. Jeden zestaw wydruków z marginesem do 256³, osprzęt, nominalne długości
   i stock całej wiązki, kolejność montażu oraz lokalny commit.

Nie zamknięto W1/W5, wyboru wydruków ani E3. Minimum potwierdzonego przeniesienia
wynosi nadal **M1/E4/A1 = 3/20 = 15%**; historyczne R53/70% nie jest wynikiem
nowego wnętrza. To licznik pełnych rezultatów, nie procent wykonanej pracy.
Hook wyłączony; bez harmonogramu, zakupów, zasilania, pushów i fizycznego PASS.

Czas do zapisania checkpointu: 08:38:01..09:00:52 UTC = 22 min 51 s;
sam builder 30,312 s. Limit o 08:59:48 UTC: 1% wykorzystane, 99% pozostałe.
Źródła/model sprawdza `tools/cad/verify_open_prototype_layout.py`; 14 testów
uruchamia `python -B tools/cad/test_open_prototype_layout.py`, bez instalacji
dodatkowych bibliotek. Zapis aktualnego planu pozostaje poza commitem,
żeby nie włączać wcześniejszych cudzych zmian.
