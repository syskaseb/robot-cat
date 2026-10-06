# CP2: wspólne rozmieszczenie wnętrza

Niewybrana propozycja w zaakceptowanym obrysie CP1, tułów325×200×160mm.
Nie jest zestawem części do druku ani zamknięciem W1/W5. R53 i14/20=70%
pozostają bez zmiany; hook aktywny do06.10.2026 09:00Warszawy, bez harmonogramu.

`WholeCatInterior.FCStd` zawiera zachowane rzeczywiste referencje P0,
przesuniętą głowę/ogon CP1 oraz62 edytowalne rezerwacje modułów i17 dostępu.
Stara kaseta została usunięta z tej propozycji, nie z wybranego robota.
Źródło: `tools/cad/whole_cat_interior.py`; wynik i ograniczenia: `layout.json`;
kontrola nominalnego rozmieszczenia: `checks.json`; wymiary, wyjścia i granica
serwisowa: `interfaces.json`. Wcześniejszy plan61 rezerwacji zastąpiony.

| Warstwa | Rozmieszczenie |
|---|---|
| Dół | Akumulator pozostaje; Pi42..64mm, MAIN obrócony przy przodzie, BUS41..55,6mm, monitor50..62mm; para XT60/F0 w przedniej bocznej strefie i6 splices |
| Środek/boki | Sterowniki78..108mm;12 oprawek70..134mm;4 MTA80..96mm;10 bocznych WAGO56..75mm z wejściami w dół |
| Góra/środek | 8 poziomych centralnych WAGO110..121mm, P_SYS95..117 wejściami w górę, G1 103,5..125,5 wejściami w dół;5 poziomych FHAC125..147mm; ATO nie pod WAGO |
| Źródło/wyłączniki | S0 z kluczem pionowo w przedniej strefie, S1 po prawej stronie ogona; otwory/osprzęt jeszcze do zaprojektowania |

Uwzględniono12 MTA0300330/24 zakończenia,20 bloków WAGO,6 splices,
4 MTA0100335,5 FHAC0001ZXJ i1 F0 FHAC0002ZXJ, XT60, osiowy F_PWM
0242.100UAT1 (bez osobnej oprawki) oraz układy sterowania.
Zgodność dokładnego zestawu20 nazw szyn z istniejącym netlist jest sprawdzana
automatycznie. Nie zmieniono topologii, SKU ani przydziału pinów.

Historycznie pierwsze dwie kontrole wykazały brak wspólnego warunku wysokości nad
mocowaniami nóg. Rozwiązanie: cały poziom oprawek oraz WAGO przesunięty
w górę; boczne listwy zwężone razem. Nie wycinano kolejnych dziur w starej
kasecie. Końcowa kontrola używa operacji na bryłach, a nie samego bbox:
rezerwacje nie przecinają się ani zachowanych części P0/głowy/ogona;
wewnętrzne rezerwacje z dodatkowym marginesem2,4mm mieszczą się w obrysie.
Klucz S0 i sterowanie S1 mają osobny zakres otworów obsługowych, nie zostały
udawane jako zamknięte pod skorupą. Ponowne otwarcie i parametr Pi sprawdzone.

## Uzgodnienie gabarytów i dostępu 06.10.2026

Aktualizacja źródeł: P_SYS wejściami w górę Z95..117, P_FRONT/P_REAR/D_RL
przełożone razem, G1 bliżej przodu. W043 F_PI.in→P_SYS.2 ma dwa dokładne
łuki R6, prosty odciążany koniec12mm i nominalny blank48,850mm obejmujący
14mm odizolowania, poniżej50mm. Wymodelowany przewód ma poprawną bryłę,
nie przecina sąsiadów/rezerw dostępu i mieści się w obrysie. Wyjście oprawki,
OD3,4/R6 i fizyczny punkt portu są prowizoryczne; nie oznacza to pomiaru
pasowania ani bezpiecznej koordynacji F0. Styki wewnątrz docelowych oprawek
wyłączono z kontroli rezerwacji korpusów, bo końcówki należą do tych korpusów.
Sprawdzono zmianę parametru P_SYS, nie ponowiono parametru niezmienionego Pi;
57 niezmienionych modułów korzysta z wcześniejszego dowodu i zgodnych hashy.
Pozostała wiązka nadal OPEN. W043 to jawny snapshot przewodu z buildera,
nie parametryczne zależności całej wiązki. Przebieg CAD35,625s.

Wejście baterii sprawdzono jako wspólny układ: XT60 obrócony90X, F0 wzdłużX,
minus do G1 wejściami w dół, MAIN obrócony obok przodu i dwa przełożone splices.
W075 bez dodatkowej spoiny przed F0: nominalny blank30mm (25mm trasy+5mm
umownego zakończenia lutowanego), <=50mm. W001 LAPP:102,056mm obejmuje
14mm WAGO i5mm lutowania, dwa rzeczywiste łuki R12,4 wg źródła przewodu,
34,1mm prostego odciążanego zakończenia. To długości do przymiarki, NIE
polecenie cięcia przed dostawą. W043 pozostaje48,850mm. Trzy przewody mają
poprawne bryły, nie przecinają sąsiadów ani siebie, rezerw dostępu i obrysu.
55 niezmienionych modułów korzysta z wcześniejszego dowodu, sprawdzono zmianę
G1 i pięć zapisanych brył przewodów/odizolowania. CAD37,688s, reopen G1 5,328s.
Poprzedni F0 wzdłużY odrzucony po przecięciach z S0/mocowaniem nogi/splice.
Rama nieprzerobiona; odrzucona próba nie nadpisała dobrego modelu.
Rozstaw kubków7mm, rzeczywista polaryzacja/położenie kupnego XT60, mated plug,
FHAC grubość/wyjścia oraz pola WAGO nadal do przymiarki. W075 jest fabryczną
żyłą F0, NIE dodatkowym LAPP. G1 nie ma dwóch przewodów w jednym porcie.
Przy wyborze tego układu nowe długości zastąpią dawne W001140/W07540/W04340,
nie są dodatkowymi odcinkami do sumowania. W076/F0→S0 i całe W5 nadal OPEN.

Nowy wspólny układ:10 bocznych WAGO niżej,10 centralnych WAGO pod pięcioma
poziomymi FHAC,12 ATO po bokach. WAGO pozostają podłączone przy nominalnym
dostępie do ATO. Sprawdzono razem12 prostych korytarzy wyciągania/narzędzia
ATO45mm i5 górnych budżetów dostępu FHAC40mm z marginesem2mm wXY.
Nie przecinają modułów ani rzeczywistych zachowanych brył. Reopen/parametr Pi
sprawdzone, końcowy przebieg CAD66,140s. To ZAŁOŻONE przestrzenie dostępu,
nie wymiarowany ruch dźwigni/zawiasu/narzędzia producenta. Boczne WAGO
wymagają zdejmowanych boków, centralne dźwignie i pełny demontaż nadal otwarte.

BUS to Waveshare25514, NIE adapter575070. Pełna obwiednia zapisanego modelu
producenta42,024×33,816×14,6mm obrócona90°; USB wychodzi w+X.
Zapisany compound ma117 brył, ale jedna jest niepoprawna. Nie naprawiono ani
nie pominięto części: do kontroli użyto pełnej prostokątnej rezerwacji,
nie wadliwego BRep. Dokładne pasowanie BUS nie jest zakwalifikowane.
U1/57507030,48×17,78mm należy do sterownika PWM1608; nie jest drugim BUS.

P309 ma41×25×12mm według wskazanego dostawcy, zamiast dawnej rezerwy35×25×11.
FHAC mają51mm maksymalnej długości i20,25mm szerokości. Pięć gałęzi ustawiono
poziomo ponad centralnymi szynami; oba wyjścia zachowane. Grubość22mm, OD3,4/R6 przewodu
pozostają założeniami. Fabryczne89,5±5mm obejmuje odkryty koniec; nie liczyć
go drugi raz jako dodatkowej długości. F0 obrócono poprzecznie w wolnej strefie
przed akumulatorem po wykryciu59,079mm³ kontaktu pierwszej rezerwacji z ramą.
Końcowe rezerwacje bez kontaktów; rama P0 bez zmian.

XT60H-M23,9×16,4×9,2mm dotyczy własnej połówki, NIE całej połączonej pary.
Druga połówka, wyjścia i ruch rozłączenia nadal wymagają przestrzeni.
Źródła i oddzielne założenia zapisane w `interfaces.json`.

## Granice tego wyniku i następny krok

Bryły są jawnie opisanymi rezerwacjami, nie dokładnymi modelami każdego SKU.
Podstawowe wymiary BUS/P309/FHAC/XT60 uzgodniono; pełne wyjścia/maty/obudowy
nie są jeszcze dowodem montażu. Rodzina HELLA, wsunięcie TE i wysokości wyposażonych
PCB są nadal założeniami prototypu. Wynik NIE dowodzi kompletnego montażu.

Proponowany poziom sygnałów Z66..76mm, nad Pi/pod sterownikami, NIE jest
wykonaną wiązką. Boczne WAGO wejściami w dół wymagają prostej9mm i pętli
R12,4 w dolnej strefie. Zakręty R25,2 większych trunków muszą mieć osobne
strefy w X/Z; oba wyjścia4MTA zachować. Złącze źródła
wróciło obok F0 zamiast wędrować na tył; droga przed bezpiecznikiem <=50mm
wymaga jeszcze rzeczywistych osi/pinów i pełnej trasy.

Następny krok: dopasować pełne zakończenia i wspólnie poprowadzić wiązkę
w tych strefach, z podparciami i granicami rozłączania. Dopiero potem
wykonać nośniki/skorupę. Nie projektować podpór pod same prostokąty.
Poprzednie górne WAGO stały nad bezpiecznikami. Policzenie granicy z istniejącego
netlist wykazało74 przewody wychodzące poza płytę i6 wewnętrznych połączeń.
Podwójne aliasy G1.5/G2.1 nie oznaczają dwóch fizycznych przewodów.
Odrzucono rutynową wymianę ATO wymagającą74 rozłączeń. Nowy plan bezpośredniego
dostępu ma17 sprawdzonych rezerwacji, nie gotowy serwis. PRZED podporami
domknąć wspólne przewody/dźwignie, obie strony4MTA oraz krótkie wejścia F0/F_PI;
potem mocowania, stock i jeden wybrany eksport. Nie przesuwać samej płyty.
Ruch/dźwignie/parkowanie końców nie zostały zakwalifikowane. Nie dodano SKU.

Slicer, druk i próby należą do fazy2. Brak fizycznego PASS.
