# Osłony tułowia i wspólny mostek BUS–MIC — 17 listopada

**Model roboczy, nie kompletny zestaw do druku.** Baza, elektronika, ochrona,
fabryczne końce i mechanizmy pozostają. Nie wykonano wydruku, cięcia przewodów,
próby pod napięciem ani fizycznej przymiarki.

Otwórz `body-closure-interface.FCStd`. Cztery części `HB_*` są rzeczywistymi
pustymi osłonami, ale pozostają **HOLD / NIE DRUKOWAĆ**. Poprawna bryła nie
oznacza poprawnego montażu. Sprawdzenie całego nowego dołu wykazało trzy
powiązane grupy problemów: przejście przy rzeczywistej bazie WAVEGO,
przy wspólnych podporach/pokładach oraz przy niskich końcach i chłodzeniu Pi.
Nie są to braki długości przewodów. Zachowano wyniki przed korektą; nie
uznano błędnego obliczenia odsunięcia powierzchni za prześwit. Część tylna
dodatnia po dopasowaniu ma dwa osobne fragmenty — nie usunięto żadnego dla
pozornego zamknięcia siatki. Niezbędne jest dokończenie całego dolnego
interfejsu, a nie kolejna mała zmiana wysokości osłony.

## Jedyny nowy kandydat do niezależnej przymiarki

`N2_BUS_E1_MIC_common_bridge.stl` wolno użyć **tylko jeśli** plik
`independent-MIC-export-gate.json` ma
`conditional_nominal_dryfit_release: true`. To wspólny zdejmowany mostek
BUS, górnego trzymania E1 i mikrofonu, nie osobna obudowa każdego modułu.
Indeks zawiera ilość, wymiary i orientację. Zastosowano dwa ukośne otwory
mikrofonu z odebranego źródła. Populowany spód ma nominalnie 1,5 mm wolnej
przestrzeni nad półką; nie opiera się na układach scalonych. Dolne nogi
mostka pozostają na rzeczywistej tylnej belce, a ramiona zaczynają się
powyżej pełnego S0. Dwa komplety M2×12 są nowym **niepotwierdzonym
zapotrzebowaniem**, bez twierdzenia o posiadanym zapasie.

Najpierw sprawdzić rewizję płytki, dwa otwory, bezpieczne pierścienie
podparcia i rzeczywiste elementy spodu. Nie dociskać płytki, jeśli podpory
trafiają w element, mikrofon, przycisk lub złącze. To nominalna przymiarka
mechaniczna, nie cyfrowy dowód bezpiecznego nacisku.

## Kolejność dla dwóch osób

1. Na otwartej bazie zachować już przyjęte źródłowe szyny, pokłady i podpory.
   Nowych osłon `HB_*` na razie nie montować. Pozostałe sprawdzone części
   są wskazane przez SHA źródłowego pakietu, bez kopiowania ich siatek.
2. Na stole włożyć pełne śruby i podkładki BUS oraz MIC od spodu mostka.
   Ustawić właściwą płytkę MIC na dwóch podparciach, założyć górne
   podkładki i pełne nakrętki. Druga osoba podtrzymuje płytkę.
3. Wstawić mostek na istniejące dwa połączenia M3. E1 pozostaje całym
   lutowanym zespołem; nie zakłada się jego rozłączenia. Sprawdzić realny
   dostęp klucza i przewodów przed bankami oraz osłonami.
4. Ręcznie ułożyć całe właściwe jednostki przewodów i wtyki przy otwartej
   konstrukcji. Fabryczne FFC200, cztery E2/JPWM, FHAC, JR/Molex i dwa
   tekstylne pasy nie otrzymują dodatkowej długości ani zgody na cięcie.
   Po zamknięciu opaski człowiek może obciąć wyłącznie jej nieużywany
   plastikowy ogon zgodnie z wcześniejszą decyzją.
5. Osłony dopiero po rozwiązaniu ich dolnego interfejsu i rzeczywistym
   ułożeniu wiązek. Rzadki serwis baterii nadal może wymagać częściowego
   demontażu; nie zakłada się przejścia ogniwa 35 mm przez otwór 30 mm.

## Co jest wykonane, a co pozostaje otwarte

| Grupa | Stan |
|---|---|
| Cztery ściany tułowia | Materiał BRep, podział X=10 i Y=0, klucze przy grzbiecie; **HOLD dolnego montażu**, bez STL |
| Sześć połączeń osłon z bazą | Źródłowe połączenia zachowane; przeniesienie na nowe osłony **nieprzyjęte** |
| Mostek BUS–MIC/E1 | Zrealizowany nominalnie; niezależny wynik eksportu w bramce |
| N1 wspólny przedni frame | Źródłowy BRep zachowany; siatka nadal otwarta, **bez STL** |
| S0 | Całe 11 części i źródłowe podparcie; okrągły dostęp w osłonie, montaż całej nowej osłony nadal HOLD |
| Monitor i S1 | Otwory dostępu w osłonie; rzeczywiste wspólne trzymanie **niezrealizowane**, nie „FIT” zamiast brakującego mocowania |
| Głośnik | Dwa okrągłe otwory akustyczne dla całej nominalnej instalacji; nie oznaczają dwóch głośników. Trzymanie kosza/kołnierza **otwarte** |
| TTP | Zachowana płytka i funkcja; bezpieczne wspólne trzymanie **otwarte** |
| Szyja i ogon Y | Otwory funkcjonalne; końcowy kołnierz/ochrona, zamknięcie i montaż nieprzyjęte |
| Wiązka ruchomej głowy | Wybrana wcześniejsza recepta FFC 226,2 > 200 mm nadal HOLD, nie dowód braku wszystkich dróg |
| 4×MTA0100335 | Wymagane; pełna geometria, klapka, smycz i dwa końce UNBOUND. Zależne zamknięcie pozostaje otwarte |

Źródłowa instrukcja NKK pokazuje M12×1, otwór Ø12,5 i maksymalnie 4,5 mm
panelu, lecz aktualne pole S1 22×22×40 jest założeniem instalacji z dźwignią,
nie pełną geometrią korpusu. Nie wykorzystano jego narożników jako datumu
otworu ani nie ogłoszono gotowego mocowania. Dostarczona sztuka i przypisanie
orientacji są konieczne przed tym mocowaniem, bez ponownego audytu katalogu.

## Masa i obrazy

`actual-candidate-print-material.json` liczy faktyczny materiał każdej nowej
bryły przy PETG **1,27 g/cm³**, także niepołączony fragment. To równoważnik
pełnego materiału CAD; nie wynik ważenia ani oszacowanie całej masy kota.
Nie liczono pełnej bryły obwiedni jako wydruku i nie poprawiano wyniku zmianą
wypełnienia. Ściana ma konstrukcyjne odsunięcie promieniowe 2 mm, nie
potwierdzoną wszędzie stałą grubość normalną. Nowe wymiary nie są przyjęciem
proporcji Oli. Widoki pokazują rzeczywisty stan roboczy, z wystającymi
częściami, brakami i otworami. Głowa nie została w tej porcji poprawiona.

Cały zestaw, wygląd, trasy/cięcia/luz i fizyczny PASS pozostają nieprzyjęte.
