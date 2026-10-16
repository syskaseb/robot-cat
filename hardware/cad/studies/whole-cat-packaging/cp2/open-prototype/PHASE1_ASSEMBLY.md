# Jeden montaż otwartego prototypu, bez zasilania

Źródła wykonawcze: aktualny K1 (`phase1-current-print-selection.json`),
K2 (`phase1-current-purchased-selection-r2.json`) oraz W5
(`body-harness-checkpoint/w5-selection.json`). Nie używać starego koszyka R53
jako drugiego zestawu. To instrukcja nominalna fazy1, nie fizyczna próba.
P0/E6, 15napędów, wymienne trzy MG92B i MAIN Z46,52 pozostają zachowane.
Brak zewnętrznej kosmetycznej obudowy jest zamierzony.

## Kolejność i dostęp

1. **Próbki i dostawa.** Oddzielić baterię, USB i wszystkie źródła. Sprawdzić
   rzeczywiste śruby/orczyki ST3215, MG92B, otwory, zatrzaski, Cu/OD i długości.
   Przymierzyć PETG, klej i izolację na próbkach. Nie wymuszać zer serw.
   Przymiarka może wstrzymać odpowiedni moduł, nie wymaga niszczenia innych.
2. **Pusty szkielet P0.** Złożyć ramy czterema M2,5x12/nakrętkami. Pokrywy
   końcowe i ich cztery M3x16 odłożyć do końca. Przygotować R6 i nakrętki
   baterii na pustych ramach; utwardzać klej bez baterii i elektroniki.
3. **Dolne osie i stopy.** Zamontować cztery aktualne stopy FixedCarrier
   M3x16 z podkładką/nakrętką na istniejących bossach. Dostęp od spodu musi
   pozostać wolny przed kasetą baterii. Przygotować Foundation i zaciski ramy,
   cztery M3x14 z kompletem podkładek/nakrętek; dokręcić przed zasłonięciem Pi.
4. **Szyja/MAIN i dolna płyta.** Dolne cztery przednie M2x10 z P0 są jednym
   zestawem szyi, nie drugim kompletem. Zamontować LeftRiser/RightRiser oraz
   mocowanie MAIN przed przewodami i głową. MAIN ma osobne dwa M2x12,
   dwie dolne podkładki; górne zastąpiły integralne stopy E1. Zachować Z46,52.
   Nie zakładać jeszcze górnej płyty ani 12 końcówek wejść banku.
5. **Nogi.** Na stole złożyć cztery jednakowe łańcuchy ST3215, po trzy napędy,
   zachowując P0/E6. Osadzić niezmienione orczyki/cięgna/stopy dopiero po
   sprawdzeniu akcesoriów z pudełek. Zamocować aktualne HipExtension i KneeCarrier
   na przypisanych obudowach, nie przez ich szwy. Klej nie przejmuje sił kabla;
   odciążenia i pętle wykonać według W5. Nie sklejać ruchomych członów ze sobą.
6. **Głowa i ogon na stole.** Wykonać wewnętrzną kolejność odpowiednich M2/M3
   README: łożyska, nośniki, MG92B i wymienne orczyki, następnie retencję.
   Nie wciskać JR przez płaskie wyjście. Głowę pozostawić otwartą dla wiązki.
   Tylny wspólny zestaw to cztery M2x30 z czterema nakrętkami i ośmioma
   podkładkami, zamiast starego M2x10/M2x14. Przymocować ogon i monitor,
   przełożyć jego dwie opaski przed zamknięciem dostępu dolnej płyty.
7. **Kaseta baterii, bez pakietu.** Po dokręceniu dolnych stóp zamontować R4
   na ośmiu M2x6/16podkładkach/8nakrętkach R6. Pad107x36 i dwa paski
   pozostają osobnymi elementami. Nie mocować kasety za przewód XT60/balansu.
8. **Elektronika na stole.** Przygotować zmodyfikowane 1608/1208 i wszystkie
   znane elementy według E1: trzy cięcia miedzi, kontrola grafu, 24 piny U1,
   indywidualna izolacja i oznaczenie orientacji. Mapa zewnętrznej dostawy U1
   nie jest zgadywana. Wszystkie luty/grzanie wykonać poza PETG i baterią.
9. **Dolne płytki i źródło.** Pi/BUS na ośmiu M2x12 z nakrętkami uwięzionymi;
   użyć aktualnego overlay20 podkładek DIN433 Ø4,5. GPIO/PCA cztery stare
   górne podkładki zastąpione stopami E1 nie wracają. S0 zamontować i dokręcić
   jego korpus M6 oraz zaciski M10 przed oczkami/przewodami; bez starego
   dodatkowego uchwytu Deck. Miejsca pod F0/MAIN i dolne chwyty przygotować teraz.
10. **Wiązki i wejścia banku.** Na stole przygotować 17 rzeczywistych kabli900,
    w tym czterech donorów i jeden BUS, oraz nominalne przewody W5. Przed
    zaciskiem wejść TE przeprowadzić 12 przewodów przez zapisane przejścia
    Foundation. Zachować rzeczywistą liczbę końców, kolory i D/V/G, nie
    numerację sugerowaną kolorem. Obie strony wszystkich czterech MTA
    przygotować jako osiem osobno podpartych połączeń221-2411, nie jako wiszące oprawki.
11. **Górna płyta na stole.** Założyć PCA/AUX/1608/U1 i retencję, FTY,
    E2Fixture na trzech M3x12, bank12oprawek/24TE oraz indywidualne siodła.
    Śruby i kanały opasek obsłużyć przed przewodami/obudowami, które je zasłonią.
    Posadzić górny zestaw na czterech M3x45/postach. Nie prowadzić zamkniętego
    złącza przez za mały kanał; przeprowadzić luźne końce przed ich zakończeniem.
12. **Wspólne trasy i retencja.** Poprowadzić wszystkie odcinki według W5,
    W1, aktualnego W2/W3, W4 i E1/E2. Na dolnych WAGO najpierw zakończyć
    przewody, potem zasłaniać je górnymi warstwami. Podtrzymywać złączkę przy
    pracy dźwignią; SJ4570/4905 utrzymują obudowy, nie zastępują chwytu żyły.
    Zamknąć przypisane CAP, osobne opaski i sznurowanie dopiero po ułożeniu
    łuków i sprawdzeniu zapasu na ruch. RR CAP ma jeden M2x14/nakrętkę.
    P_SYS zamontować na odłączanej listwie z dwoma M3x8, po przygotowaniu
    czterech oznaczonych końców. Nie zmieniać ich przypisanych komór.
13. **Głowa/ogon i zamknięcia.** Położyć ciągłe odcinki HELU/JR według
    aktualnego fixed-head; stare trzy pętle pitch i HeadFixedAnchor są wycofane.
    Zachować wszystkie fabryczne MG92B250 bez cięcia. Wykonać indywidualne
    izolowane połączenia poza robotem, ostudzić, osadzić i zacisnąć tylko
    izolowane proste poza lutem. Następnie zamknąć funkcjonalną głowę i
    pokrywy końcowe P0. Nie dodawać kosmetycznej skorupy tułowia.
14. **Kontrola kompletności bez energii.** Sprawdzić obecność wszystkich
    wydruków/osprzętu/końców, brak luźnych modułów, podparcie przewodów,
    ręczny dostęp ATO, oznaczenia i ciągłość przy rozłączonych odbiornikach.
    Naddatki ciąć dopiero po przymiarce. Nie traktować prób cyfrowych jako
    kontroli polaryzacji miernikiem, retencji zacisku ani pełnego ruchu.
15. **Bramka E3.** Pakiet zostaje odłączony, aż rzeczywiste źródło/przewody/
    złącza/zabezpieczenia przejdą osobną kwalifikację. Ta sekwencja nie daje
    zgody na zasilanie, kalibrację, ROS ani chód. To faza2/3, nie wykonany PASS.

## Demontaż z kompletnego kota

Najpierw wyłączyć/odłączyć źródło i USB, odłączyć XT60/balans, podeprzeć
wiązkę oraz moduł. ATO wymieniać od góry po podparciu oprawki, z zachowanymi
WAGO. Przed wyjęciem oprawki odłączyć jej oznaczone TE, nie ciągnąć za żyłę.
Głębszy dostęp do górnej/dolnej elektroniki: otworzyć funkcjonalne zamknięcia,
oznaczyć i zwolnić odpowiednie końce, przeciąć wyłącznie wymienne wiązania,
zdjąć górny zestaw wraz z bankiem, następnie obsłużyć dolne śruby i złącza.
Nie zakładać jednoczesnego wyciągania TE przez backery ani podnoszenia
oddzielnej starej osłony. P_SYS zdejmować dopiero po zwolnieniu czterech żył.
Do kasety R4 dostęp od spodu: podeprzeć, odkręcić8M2x6 i opuścić40mm
po odłączeniu pakietu; nie odkręcać stóp wiązki pod obciążeniem.
Głowę/ogon zdejmować po rozłączeniu JR, z odciążoną wiązką i podparciem
mechanicznym; ponowny montaż w odwrotnej kolejności z nowymi uszkodzonymi
opaskami/koszulkami. Dopuszczalne jest wcześniejsze zdjęcie sąsiedniej płyty
lub modułu. Nie obiecujemy hot-swap, szybkiej kasety ani serwisu bez rozłączeń.

Przymiarki, próby kleju/PETG, docisk, rzeczywiste narzędzia i pełny ruch
pozostają bramkami fizycznej fazy2. Narzędzia i materiały wskazuje K3.
