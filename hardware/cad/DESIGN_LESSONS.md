# Wnioski z projektowania 3D robot-cat

## 30.10 — feedback z całego frontu, przed kolejną próbą

- Zadziałało odczytanie funkcji geometrii: scalonyBankBed zawiera grzebień,
  podpory i stare mocowania; S0 jest rezerwą rodziny, invalidBUS błędem źródła.
  Pełny poprawny cover może dowieść separacji; jego overlap nie dowodzi kontaktu.
- Cztery niezależne jednostki220mm muszą mieć równocześnie aktualne porty,
  prefiksy, allowance i chwyt. Długość ani1solid osobno nie kwalifikują układu.
  Prawdziwy kupny port jest stały; cap po projektowym chwycie niekoniecznie.
  F_PWM już używa9mm po łuku, więc nie odzyskiwać fikcyjnych kolejnych9mm.
- Rozdziel długość jednostki magazynowej, odcinek instalowany i odpad po
  dopuszczonej przymiarce. plan_fixed_head_jr_terminations.py:41–42/62/67
  przewiduje cięcie dalszego końca jednej przedłużki JR300 po przymiarce,
  przy zachowaniu keyed factory plug, JR mating plug i pełnego factory250.
  Nie wymuszaj schowania całego odpadu JR w robocie. Zachowaj prefiksy,
  allowances i bramkę fizycznego cięcia fazy2; nie rozszerzaj tego wyjątku
  na cztery chronione jednostki MTA ani inne fabryczne przewody.
- Rejestr compose_body36_fit_contribution.py definiuje dla jednostek900mm
  nominalny fit_blank z20mm rezerwą i zaokrągleniem do5mm, ograniczony900.
  Trzy żyły kabla pobierają MAX(blank), nie trzy oddzielne kable. Nie wymuszaj
  instalacji całej niewykorzystanej reszty w robocie i nie licz jej jako nowej
  jednostki. To wkład nominalnej przymiarki, nie wybór stockuN10 ani polecenie
  cięcia; zachowaj źródłowe złącza, bramki fazy2 i rozlicz source-owned splices
  wszędzie, gdzie korzystasz z ich budżetu; kandydat nie staje się stałym wymogiem.
- Rzeczywista szczelina5.120847mm odrzucała koło6.1mm, ale mieści płaski
  przekrój6.1x2.1 dwóch pełnych profili2.1mm. Zmiana kształtu obsady jest
  uzasadniona transportem obu żył/R/długością, nie zmniejszeniem ich średnic.
- Przed budową podpory wskazać rzeczywistą CAŁĄ powierzchnię kotwy i drogę
  do ramy oraz P0/GPIO/Pi/stock. Błędny root do niewłaściwego banku był
  odsunięty49.394mm. Późniejszy dodatni root nie zastępuje kontroli sąsiadów.
- Lista wycofanych aktorów jest częścią wspólnego planu. DAY18 XP02band/head
  były zastąpionym chwytem tego samego wyjścia, a W044 nadal pełnym stockiem.
  Klasyfikację opieraj na konstruktorze, nie na wygodnym wyniku testu.
- Scalona część nadrzędna nie jest niezależnym elementem chronionym, jeśli
  zawiera wycofywaną gałąź. Input:PowerParent zawierał cały staryXP02;
  ochrona jego sumy blokowała usunięcie zastąpionego chwytu. Wskaż rzeczywiste
  pozostające podpory i ich połączenia; po usunięciu gałęzi sprawdź ich materiał
  oraz ciągłość ramy. Nie dopasowuj przewodu do pozostałości starego mocowania.
- Koniec ścieżki ruchu musi wynikać z aktualnego kontaktu podpór z podłożem,
  nie z liczby pozycji w skrypcie. Zachowaj źródła i zakres takiego uzasadnienia.
- Zachować own→changedforeign→assembly/ATO/motion/outline;204zielonych/liczonych
  par z7HOLD nie daje punktu. Po dwóch przyczynowych odrzuceniach następna
  propozycja zmienia cały zależny interfejs, a nie przesuwa pojedynczą krzywą.
- Uwagi recenzenta przypisuj do stałego kryterium bieżącego punktu. N01
  wymaga wybranego konstruktywnego CAŁEGO układu i usunięcia znanych blockerów;
  sama lista/tekst nie wystarcza. Pełna kwalifikacja serwisuN08 i trajektoriiN09
  nie jest dodatkową bramkąN01. Nie przenoś tam rzeczywistych kolizji ani nie
  zmieniaj akceptacji/licznika; rozdziel plan wykonalności od szczegółowego odbioru.
- Rozróżniaj fizyczny port/splice/koniec ruchomego odcinka, pośredni zaczep
  prowadzący i umowną granicę regionu/porcji. Ta ostatnia potrzebuje ciągłości
  przestrzeni, nie dodatkowego terminala, 9mm prostego ani nowego chwytu.
  Wspólny zaczep pośredni może prowadzić luźną wiązkę; właściwe odciążenia
  rzeczywistych końców i ochrona przy przegubach/krawędziach pozostają wymagane.
- Kierunek łuku z projektowego source_recipe nie jest automatycznie kierunkiem
  producenta. U1 source_basis=selected local departure wymaga odróżnienia
  actualpad/parts od przeprojektowywalnego zewnętrznego wachlarza, bez zgadywania
  pinoutu i bez dziedziczenia dowodów zmienionego interfejsu.
- Konstruktor split_cap_exterior oraz band_budget/head_budget opisuje projektowy
  chwyt i przestrzeń jego opaski T18I, nie trzy niezależne kupne moduły.
  Po konflikcie wielu takich uchwytów rozważ wspólną retencję i kolejność
  montażu, zamiast objazdów każdej żyły. Wycofanie wymaga wskazania tej samej
  zastępczej funkcji, pełnego stocku i odciążenia. Rzeczywiste podpory obudów,
  filary oraz stosy śrubowe zachowują funkcję i drogę obciążenia.
- Hook wymaga jednej krótkiej aktualnej karty, a nie wielu chronologicznych
  NEXTów przed historią. Na górze: aktywny wykonawca, frozenpakiet, negatywy,
  konkretna następna decyzja, wynik i rzeczywisty czas. Starsze stany do historii.
- Windowsowy nativeFreeCAD wymaga jawnego UTF-8 przy KAŻDYM odczycie i zapisie
  metadanych. Odczyt locale-cp1252 i zapisUTF8 rozdymał polskie znaki do4.36GB,
  kończąc proces brakiem pamięci. Używaj encoding="utf-8", zapisu atomowego
  i bramki rozmiaru; geometrię zapisuj przed zależnym odczytem/zapisem stanu.
- Nie uzależniać wznowienia od żywegoRAM. Przed zależną próbą zapisz aktualne
  aktory, SHA i strict-reopen. Po przerwaniu potwierdź brak staregoPID/sesji,
  uruchom jeden zastępczy proces i odtwórz nazwane pakiety bez ponawiania kontroli.
  Proces należący bezpośrednio do workera upraszcza sterowanie, ale nie gwarantuje
  przeżycia każdego przerwania. To instrukcyjny feedback loop, nie trening modelu.


### 26.10 wieczór — przestrzeń wiązki musi obejmować cały zespół

- housing_bounds źródła serwa opisywał tylko połowę obudowy. Odrzucone
  regiony Hip przecinały drugą połowę/link/Knee. Przed rodziną czterech
  krzywych pokaż jeden CAŁY człon: wszystkie9Hip/14Knee, nie sam bbox źródła.
- Niewidoczny budżet zamontowanej opaski/główki nadal zajmuje przestrzeń.
  Wyklucz tylko jawnie wycofane elementy;135obrysów nie znaczy135opasek.
  Samonakładający Compound z poprawnych pudełek zastąp ich dokładną sumą,
  zachowując materiał. Nie wycinaj takiego ograniczenia z kontroli.
- Native recompute może normalizować kierunki BRep o1e−16. Bajtowy hash
  wtedy nie dowodzi ruchu. Zachowaj oryginał, porównaj wszystkie parametry
  i topologię z jawną tolerancją, dopiero potem przyjmij zapis/reopen.
- Jedna spójna wolna bryła i dobry przekrój nie kwalifikują całej wiązki.
  Osobno domknij rozgałęzienia, skręty, długości, luz ruchu i montaż.
  Zakres długości0.069mm nie jest tolerancją ręcznego prototypu.

### 26.10 — zachowaj zespoły i izoluj operandy kernela

- Pełne przypisanie123połączeń ujawniło, że jednolita galeria19×7 i przejście
  wszystkiego przez jeden węzeł tworzyły sztuczną kumulację oraz objazdy.
  Lokalna obsada wyznacza połączone komory; nie przesuwaj kompletnych modułów
  tylko po to, by obronić ten sam prostokątny kanał w każdym przekroju.
- Przed podnoszeniem kolejnej bryły nazwanej „wire” sprawdź typ/proweniencję.
  RRFlatResource/FullBody/received_nominal_wire to referencje przewodów;
  RRFlatGuide/Band/Head i bare zostają ograniczeniami. Aktualny wspólny helper:
  tools/cad/feline_prototype_space_classification.py. Klasyfikacja nie kwalifikuje
  automatycznie przewodu przy porcie lub przegubie.
- Zaobserwowano: używany w RAM Frame605faces stał się Unorientable; ten sam
  zamrożony BRep po sprawdzeniu SHA i świeżym imporcie był strictBOP poprawny
  (0.953s). Scalenia na starej kopii odrzucono. Na osobnych instancjach
  zaimportowanych z BRep scalenie z MAIN dało poprawną1bryłę638faces w1.484s;
  kanoniczna świeża kopia pozostała poprawna. To wskazuje na problem stanu
  współdzielonej geometrii w pamięci; nie udowadnia nowej kolizji projektu.
  Do operacji zmieniających topologię izoluj OBA operandy przez eksport/import,
  zachowaj źródło i sprawdź wynik przed podmianą. Nie naprawiaj tego offsetami
  rzeczywistych części ani trzecim identycznym Booleanem na tym samym cache.
- Przy odczycie długości korzystaj z konstruktora: solid.Length sumuje krawędzie.
  Dla potwierdzonego stałego kołowego profilu długość osi toV/(pi*r²).
  Aktualne8MTA różnią się od dawnych wpisów246; ich rozbieżność nie jest
  koniecznością wydłużenia zakupionych przewodów.
- Nie dodawaj2piR do pełnej sumy odcinków prostopadłych: zaokrąglenie narożnika
  zastępuje2R przezpiR/2. Odczytaj terminal/lap w istniejącym budżecie przed
  ponownym dodaniem allowance. Dla źródłowych donorów odczytaj konkretny
  source-owned staggered join; minimum starego kawałka SOURCE nie jest długością
  całego prefiksu. Nie przemieniaj2×900 w dowolną wspólną pulę bez tej decyzji.
- Wielominutowe rozważania bez odczytu geometrii też zużywają limit. Gdy istnieje
  pytanie o konkretną bryłę/interfejs, najpierw wykonaj jeden krótki odczyt,
  potem podejmij decyzję. Licznik czasu/usage dotyczy również tego czasu.

## 26.10 — wiązki prototypu: obowiązujący poziom szczegółowości

**Aktualizacja26.10: plan wiązki prototypu nie jest rysunkiem produkcyjnym każdej żyły.**
Wcześniejsza ogólna rada nie wystarczyła: wykonanie nadal wracało do pełnych
pipe/łuków i traktowało ich zapisany przebieg jako sztywną przeszkodę. Zmieniamy
konkretną bramkę pracy, a nie tylko słownictwo w raporcie.

- Domyślny wynik N01: zamocowane moduły, połączone dostępne obszary wiązek,
  lokalna obsada/przekrój z profili i jawnego zapasu, budżety długości,
  rozgałęzienia, proste opaski i wykonalny montaż. Zachować123tożsamości/246końców;
  nie wymagać123indywidualnych brył ani dokładnych osi jako warunku tego planu.
- Obszar wiązki musi mieć rzeczywistą ciągłość i miejsce na jej lokalną obsadę.
  Sam pusty bbox albo opis „ułożyć później” nie jest odbiorem. Własne drukowane
  mocowanie lub położenie modułu można przeprojektować wspólnie, zamiast
  projektować ciasne przejście i dopasowywać do niego każdy kabel.
- Przed nowym dokładnym modelem/testem zapisać w bieżącej karcie: **konkretne
  zagrożenie lokalne, decyzję fizyczną i dlaczego korytarz jej nie rozstrzygnie**.
  Przegub, zajęte złącze, ostra krawędź lub przygniecenie uzasadniają lokalny
  model; nie uzasadniają automatycznie dokładnego trasowania całego przewodu.
- Scena kontroli części sztywnych obejmuje rzeczywiste moduły, złącza, mocowania
  i mechanizmy. Poglądowe swobodne odcinki kabli nie są nieruchomymi przeszkodami.
  Krzyżowanie ich narysowanych osi nie dowodzi braku miejsca na ręcznie ułożoną
  wiązkę. Zachować dowody prawdziwego kontaktu z częścią sztywną/przegubem;
  kontakt izolacji w zamierzonej wiązce nie jest automatycznie zwarciem ani kolizją.
- Przy ruchu ocenić przestrzeń wiązki i dostępny luz w wymaganych położeniach.
  Nie wymagać, by jedna niezmienna sztywna bryła przewodu pasowała do każdej pozy.
  Koniec swobodnego modelu/chwytu drukowanego nie jest automatycznie stałym
  kupnym złączem. Mocowanie i ostatni łuk to też zmienne projektowe.
- Fabryczne długości, izolacja, końcówki i odciążenie nadal obowiązują.
  Średnica nominalna, rezerwa miejsca i dane producenta mają różne znaczenie;
  nie wymyślać cieńszego kabla ani mniejszego promienia dla zielonego testu.
  Ostateczne ręczne ułożenie/docięcie dopuszczonych odcinków i przymiarkę zapisać
  jako czynność montażową; do druku trafiają części mechaniczne, nie przewody.

Podstawa narzędziowa sprawdzona26.10: Autodesk [harness segments](https://help.autodesk.com/cloudhelp/2024/ENU/Inventor-Help/files/GUID-60FCFDE3-6170-4C7A-881B-90D4CB1733E5.htm)
opisuje wspólne wirtualne wiązki, rezerwowane ścieżki i nieliczne punkty sterujące;
SOLIDWORKS [cable routing](https://help.solidworks.com/2024/english/swelec/r_swelec_routing_cables.htm?id=0.35.5.5)
rozróżnia pełne trasy od szybszego szkicu roboczego. Nasz wybór poziomu
szczegółowości to decyzja dla ręcznie składanego prototypu, nie uniwersalny wymóg
producenta ani deklaracja fizycznego PASS. Uproszczenie samo nie daje punktów.
Procedura: skill cad-layout-planning, Choose and verify proportionately.

Przy odbiorze N01 sprawdzać wykonalną kolejność instalacji oraz wymagany dostęp
rutynowy. Rzadka naprawa może wymagać opisanego częściowego demontażu; nie dodawać
szybkiego serwisu, osobnego sztywnego uchwytu każdej żyły ani dokumentacji
produkcyjnej wiązki. Końcowe ręczne ułożenie jest bramką montażową. Nadal potrzebny
jest wykonalny plan przestrzeni, lokalnej obsady, długości i luzu, a nie samo
założenie „zmieści się”. Recenzja dotyczy tego wyniku i nie dopisuje wymagań.


### Sprawdzone porównanie z działającymi projektami — 26.10

- [Stanford Pupper 2021, Lab6, kroki2/4/5](https://pupper-independent-study.readthedocs.io/en/latest/course-material/lab-6-spr22.html): owinięte wiązki przez szczeliny, wspólne opaski, przykręcone Pi i złącza. To dowód sposobu montażu, nie dowód braku kabli w źródłowym CAD.
- [Petoi Nybble, 4.4 Wiring](https://nybble.petoi.com/chapter5): końcowe ułożenie po kalibracji i złożeniu, szczeliny ramy jako organizery, dopuszczalne własne ułożenie; przewody mają nie przeszkadzać serwom.
- [Mini Pupper2, kroki2–5 i Cover Assembly](https://mangdangroboticsclub.github.io/MiniPupperDocs/en/guide/Assembly/MiniPupper2.html): nogi/płytki mocowane śrubami, wiązki podłączane podczas montażu, przewód przez otwór, osłony później.

**Zastosowanie:** najpierw stabilne moduły i fizycznie dostępne wspólne przejścia z prostymi opaskami; elastyczne ułożenie końcowe jest czynnością montażową. Precyzyjny model zachować lokalnie dla rzeczywistego ryzyka przegubu/złącza/krawędzi. Dokumentacja montażowa nie rozstrzyga, czy autorzy kiedykolwiek modelowali każdą żyłę; nie wyciągać tego z braku ilustracji. Ich zintegrowane PCB upraszczają wiązkę — nie przenosić automatycznie ich wymiarów ani liczby przewodów do naszych wybranych modułów/WAGO. Żadna z tych obserwacji nie wymaga zmiany wybranych części ani nie zalicza N01.

## 25.10 — prawdziwy koniec i prawdziwy chwyt przed trasą

Stary wolny cap po umownym wachlarzu NIE jest automatycznie stałym kupnym
złączem. Odczytaj konstruktor: D_RL ma prawdziwe9 i wspólny cap przy case,
a dalszy łuk30/linia9 były swobodną referencją. Dwie odrzucone trasy wokół
niepotrzebnie zamrożonego cap nie uzasadniają trzeciej; zmień wolny wachlarz
za zachowanym chwytem, nie pozostałe moduły. Uniwersalna opaska z otworem2.5
nie dowodzi retencji przewodu r.925. Modeluj prostą podpórkę dla rzeczywistego
profilu i jawne zaciskanie/zakres rezerwy, zachowując wymiary kupnej opaski.
Dodatni styk0.259 przy rogu nie uzasadnia delikatnego podcięcia starego korzenia:
wybierz jedną prostą drogę nowego drukowanego korzenia i zachowaj pełny rdzeń.
Fizyczna przymiarka, pociągnięcie i pełzanie pozostają niezweryfikowane.

## 25.10 — korekta setupu po nocnym oknie

Za mało było decyzji dotyczących całego układu przed zależnym modelowaniem.
Przykład BD/BE: generator uruchomiono przed odbiorem wymaganej bramki; późniejsze
notatki tego nie naprawiają. Procedura bez dowodu zastosowania nie chroni przed pętlą.
Pierwsza krótka karta ma być jedynym bieżącym wejściem. Historia z dawnym „ON”
nie daje zgody na pracę. Po zamknięciu nie przywracać dawnego workera ani limitu.

Wspólna wiązka nie oznacza wszystkich przewodów w każdym przekroju: licz lokalną
obsadę między rzeczywistymi rozgałęzieniami. Nie podtrzymuj arbitralnego przebiegu
przez powiększanie wspólnego kanału. Chronić korzenie, a zmieniać drukowane podpory
z drogą obciążenia zanim powstanie kolejny objazd. Przy dwóch porażkach zapisuj
jedną zmianę decyzji konstrukcyjnej, nie kolejną nazwę strategii. Zachowane odbiory
W078 splice-side/BL/BP muszą mieć stronę/zakres; ogólny HOLD powoduje ich ponawianie.
Recenzent dostaje jeden aktualny układ z widokiem i zamrożonym wejściem, nie serię
pojedynczych offsetów. Gdy użytkownik zakazał wiadomości, hook pomija instrukcję
wysyłania recenzji; nie dokleja sprzecznych nakazów. Cisza nie oznacza odbioru.
Jedyny oficjalny wynik pozostaje0/10 do pełnegoN01; lokalne wyniki opisuj rzeczowo.

## 25.10 — przyczyna zamiast kolejnej osi

Odczytaj faktyczna dlugosc chronionego chwytu: stary cap nie dowodzi wolnych
15mm, jezeli9mm chwytu przesunieto wglab. Sprawdz CALY wspolny comb/opaski/
glowki i droge obciazenia; pozornie arbitralny stagger12mm chronil przed
sasiednia glowka. Rzeczywiste zajete wyjscia maja pierwszenstwo przed bbox
samego case. Dwie dodatnie proste nie kwalifikuja reszty lukow; odbierz CALA
bramke przed generowaniem zaleznej trasy. BD/BE naruszylo te kolejnosc i
zostalo odrzucone. Jezeli wlasny print zweza korytarz, podciecie z dowodem
zachowania rzeczywistych stykow moze usunac przyczyne bez objazdu przewodem.
Usuniecie materialu (scisly podzbior) reuzywa niezmienione obce pary, lecz
wymaga ponownego sprawdzenia korzeni i wytrzymalosci. Nie zakladaj poziomej
pelnej stopy na podstawie bbox pochylonej polki. Zachowawczy poprawny
axis+pelny promien daje dolna granice odstepu; HOLD nie dowodzi kontaktu.

## Brama wykonania prototypu — 24.10.2026

Ta sekcja określa bieżące wykonanie; historyczne dłuższe interwały niżej nie
zastępują przeglądu20–30min. Szczegółowa procedura: cad-layout-planning.

1. Najpierw wspólny układ modułów, mocowań, korytarzy wiązek i montażu.
   Przed nową dokładną trasą wskaż konkretne złącze/ruch/krawędź/przewężenie
   i dlaczego wspólny korytarz nie wystarczy. Bez takiej przyczyny zostań przy
   przestrzeni całej grupy; nie generuj kolejnych pojedynczych objazdów.
2. Przed obchodzeniem przeszkody odczytaj jej konstruktor i funkcję: dokładna
   bryła, nominalny model/rezerwa, obsadzone złącze, stały chwyt, elastyczny środek
   albo niepoprawna geometria. BOP-valid nie oznacza dokładnej bryły producenta.
3. Co20–30min dopisz w istniejącej karcie zamknięty problem ALBO nowy istotny
   fakt i jego konsekwencję. Brak obu wymaga zmiany przyczyny/poziomu próby;
   nie kolejnego raportera, audytu, większego skanu ani zatrzymania okna.
4. Przed detalami istniejący recenzent ocenia jedną wspólną propozycję, jej
   montaż i niewiadome, najlepiej z widokiem/przekrojem. Recenzja tekstu nie
   odbiera geometrii. Nie dodawaj agentów ani recenzji każdego parametru.

Dowód z ostatniej próby: F_PI_new jest W.box(F_PI.casing_mm), rezerwą obudowy
51×22×20.25mm, nie dokładnym modelem producenta. Nie zamieniaj przecięcia tej
rezerwy w dowód realnego kontaktu ani nie pomniejszaj jej dla zielonego wyniku.
Galeria plusY8×10 przecinała bazyU1; płaska14×4 przeszła pod nimi. Istniejące
prefiksy/opaska nadal zajmują tę przestrzeń; kilka przekrojów nie dowodzi pełnej
drożności. To przykład decyzji o wspólnej przestrzeni przed szczegółowymi osiami.
Nie zmieniaj wymagań, fabrycznych długości, zakupionych części ani licznika N01.

20.10, MTA: wysokość koszyka od samej pokrywki pomija niższy korpus
kupnego złącza. Najpierw domena CAŁYCH szyn względem wszystkich stałych
części/36ruchów; dopiero potem cięcie. Dwa koszyki wymagały tylko5
rzeczywistychclipów/57,610s do wspólnej granicyZ. Bbox pustego środka
koszyka nie jest materiałem. Nie zastępuj brakującego kontraktu własnego
korzenia przesuwaniem go: źródłoweRoot0+ForePanel po udowodnieniu1Solid
to jedna planowana część, ale kupne złącze/podłoga nadal mają swój luz.
Odbiór kompletnej krzywej WYJŚCIOWEJ do portalu nie jest odbiorem całego
przewodu między dwoma urządzeniami ani wszystkich123odcinków.

20.10: BoundBox bryły po Boolean common może nadal obejmować bieguny
nieprzyciętej powierzchni krzywej. Konserwatywna projekcja wtedy blokuje
nieistniejący kontakt. Do domen przekrojów używaj optimalBoundingBox(False,
False), ograniczonego do UDOWODNIONYCH płaszczyzn regionuBoolean. Testuj
taką własność na4rzeczywistych rurach przed drogą analizą. Pusta domena
z luźnychobwiedni nie oznacza braku miejsca ani podstawy do zmianySKU.

20.10: statyczna scena przewodów pomijała ruchome nogi. Dlatego zielona
statyka nie chroniła nawet pozy0: realne przecięcia bioder327..445mm3.
Przed drogą całej rodziny uwzględnij WSZYSTKIE rzeczywiste części także
w spoczynku; dopiero potem próbki ruchu. Po znalezieniu jednej przyczyny
nie kończ pozostałych setek kontroli odrzuconego wariantu. Zachowaj
obserwacje/niepromowany wynik; zmień wspólny korytarz przed mocowaniami.

20.10: wolny przedział po samym ruchu i długości NIE jest wspólnym planem:
przeniesiony pełny chwyt zderzył się ze stałą podporą brzucha. Przed CAD
w domenie pozycji uwzględniaj również WSZYSTKIE stałe części, oba końce
i pełne opaski. ProstaUP118,5 trafiała w P0; po obejściu ramy pokazały
się F_AUX i główki istniejących opasek. Nie projektuj uchwytów zanim cała
rodzina wyjść nie ma korytarza. Przy coplanarnym nylonie common.Area=0
nie dowodzi rozłączenia: sprawdź prawdziwe proste ściany/plane gap oraz
poprawny1Solidfuse, zachowując zerowy wynik kernela w raporcie.

20.10, MTA: liczyć trasę+strip+rework przed CAD. Korekta dwóch CAŁYCH
złączy o wyliczony deficyt daje tor z pełnym zapasem; nie usuwać rework,
nie ogłaszać katalogowego140L jako dwóch gwarantowanych ogonów140mm.
Po2nieskutecznych zmianachstóp zmienić poziom decyzji: całe złącze/M2/
chwyt w przedziale wynikającym z CAŁEGO ruchu i długości. Nie trzeciafaza.
Różne interfejsy wymagają różnych dowodów: istniejąca obudowa dotykająca
własnej izolującejpodłogi nie jest obcąkolizją; odziedziczony styk zachować
tylko po dowodzie niezmienionejpodłogi/podzbioru materiału. Ujemne wyniki
ruchu pozostają ujemne. Nie tworzyć przyszłego current-provider przed
odbiorem jego źródła; skasowano3własne nieużywane szkielety takiejwarstwy.

20.10: przed geometrią powiąż WSZYSTKIE fizyczne odcinki z wybraną tabelą
materiałów i ich rolą. Większy budżetcap nie jest średnicą żyły, materiał
fabrycznego ogona nie opisuje jego przedłużenia, SOURCE/DONOR nie mnoży
zakupów. Spięcie123ról z bazowymK3 ujawniło32rozbieżności profilu/promieni,
których kolejne lokalneprzesunięcia nie rozwiążą. Dla4wejśćMTA wspólny
plan3D zR25,2 i pełnymi9mmchwytami po łuku dał dodatnie wzajemneodstępy
w1,172s bez zmiany kupnychczęści. To tylko bramka wzajemna: nadal trzeba
sprawdzić obce bryły/pełne chwyty/korzenie/montaż. Nie importuj starychcięć.

20.10, MAIN: przed chwytami przewodów sprawdź REALNE płaszczyzny PCB i
cały stos śrub. Compounddostawcy miał komponentniżejPCB; bboxZMin niebył
spodemPCB, a stary trzpieńnie dochodził dootworu. Własne sposoby montażu
muszą być jawnie inne niżobcy luz1,25. Źródłowy nominalK1474OD2,1 teżnie
jest większymbudżetemcapPiR1,55; nie kopiuj budżetu jakośrednicyprzewodu.

20.10, MAIN/ATO: planuj CAŁYchwyt z przestrzenią wyjmowania bezpieczników,
nie samą obudowąbanku. Wspólny zestaw8,3mm mieści się międzyrzeczywistymi
korytarzami12mm. Po kontakciePi zmierz rzeczywisty normalnywitness i zatokę
całejpłytki, nie przesuwaj końcówek. WycięciePi odrzucono zaubytekstarego
PWMroot; podwieszonyROOT doistniejącego korzenia i środekzatoki rozwiązały
interfejs bezcięciakupnychczęści. Zwykłyfuse jest tu poprawny1Solid, ale
removeSplitter go psuje. Zachowuj poprawnywynikBoolean; ciągłośćmateriału
potwierdzaj różnicami zbiorów, nie równością liczbintegracji objętości.

20.10, RR_P: po usunięciu Pi z toru3żyły weszły w zachowanyUSB. Nie ruszaj
USB ani nie przeszukuj kolejnych kątów: z jego rzeczywistego materiału i
spodu Pi wyznacz WSPÓLNY przedział całego najgrubszego przewodu. Tu środek
Z93,804538..94,25 dał4krzywe i cały chwyt bez wskazań. Zachowano pierwszy
pełny9mm chwyt po łuku i4bryły grzebienia/opaski,18par reużyto. BRep po
ponownym import/export nie musi mieć tych samych bajtów: niezmienione wpisy
kopiuj wprost z przypiętego archiwum. Nadal potrzebny korzeń i montaż.

20.10, granice PRZED obliczeniami: nie utożsamiaj punktu elektrycznego,
wlotu istniejącego9mm odcinka i jego wylotu. Nie zakładaj, że36granic
kinematycznych ma36brył: aktualnie nazwanych prefiksów FR jest9. Czytaj
nazwane archiwum i producenta datumu, nie całą scenę ani najbliższy cap.
Po dwóch błędnych założeniach zmiana tej metody dała atlas w0,172s.
Własny rowek0,15 i obcy materiał1,25 to różne kontrakty: wyjątek przypisz
konkretnej żyle i konstruktorowi; nie zwalniaj sąsiednich pokryw/grup.
Zniknięcie negatywnego dowodu koniecznego NIE jest odbiorem trasy.

20.10, kontrola KONIECZNA przed trasowaniem: zielony prefiks9mm i montaż
modułu nie dowodzą, że przewód może opuścić jego cap. Dla curvature<=1/R,
przed pierwszym przecięciem płaszczyzny odległej osiowo o L<R odchylenie
poprzeczne nie przekroczy R-sqrt(R^2-L^2), niezależnie od skręcania3D.
Z rzeczywistym signed-distance materiału dało to dowody braku prześwitu
przy BankPier4 i kolizji nominalnego RR_P z budżetem PiAdapter. Wtedy
zmień źródłowy chwyt/podporę, nie próbuj kolejnych środkowych łuków.
Stosuj tę bramkę CAŁEJ wiązki przed następnym wspólnym układem CAD;
brak negatywnego dowodu nie jest dowodem istnienia trasy ani punktemN01.

20.10, wyjścia4MTA: dodatkowe9mm PRZED każdym łukiem było własnym
ograniczeniem, nie wymiarem producenta. Pełny niezależny chwyt ZA pierwszym
łukiem pozwolił zachować HELUR25,2, krótkie fabryczne ogony i obrys.
Planuj korzeń RAZEM z łukiem oraz CAŁĄ opaską/główką: słupek za siodłem
przecinał łuk i pętlę; słupek z boku +mostek przy końcu chwytu rozwiązał
to bez ruszania kupnych części. Po odbiorze aktualizuj mały overlay
rzeczywistychcapów, nie trasuj dalej ze starego first9. Dla delty2pokryw
zachowano58identycznychBRep/286par; nie powtarzać całej odebranej sceny.

20.10, ważna korekta wcześniejszego wnioskuW066: rzeczywisty CADcapR1,55
NIE oznacza poprawnego profilu wybranego przewodu. W066 pozostajeHELU23802
4mm2 z zachowanym projektowymOD4,2/R25,2; mniejszycap był błędem modelu.
Skorygowano tylko ten przewód i własny rowekPETG:40,469s/8kontroli/0wskazań,
ten sam tor/first9/końce/kupne części. Kontrakt wybranego materiału PRZED CAD.
Cała tabela elektrycznaW026 opisywała fabryczny ogon, NIE jego osobny
odcinek /custom: rolę przedłużenia odczytać z jawnej alokacjiHELU, nie
z początku etykiety CSV. Oba odcinki tego samego netu nie muszą mieć tego
samego materiału/promienia. Guard ma sprawdzać fizyczną rolę przed geometrią.

20.10, bramka długości to nie sama długość krzywej. Jedna wspólna propozycja
czterech złączy skierowanych do środka zmieściła bryły w prawdziwym obrysie,
ale97,906mm toru +11strip +10zachowanego rework przekracza100mm. Odrzucona
na preflight6,156s, BEZ uruchamiania macierzy świata i bez cichego usuwania
zapasów. Aktualne przednie wyjścia też mają konieczny konflikt kierunku:
first9,25+R25,2 wymusza środekX-149,2 poza dozwolonym-136,15. Sam najbliższy
węzeł/łuk tego nie naprawi. Następna decyzja musi objąć cały układ obu
końców/fabrycznych długości/chwytów, nie trzeci lokalny łącznik.

20.10: najbliższy węzeł nawet stycznego grafu nie jest wejściem przewodu.
Jedna hipoteza wszystkich216dojść dała162za małe promienie i44braki
przedniego biarc. Nie poprawiać kolejno punktów: dobierać portal wspólnie
z kierunkiem i promieniem już na etapie alokacji. Reużycie istniejących
biarc dało208konstrukcji bez ruszania części, lecz tylko10dodatnich dowodów
konserwatywnej mapy. Pozostałe NIE są ani PASS, ani potwierdzoną kolizją;
wymagają rzeczywistej bryły. Liczyć domknięte bramki, nie linie kontrolera.

19.10, wspólny węzeł P_SYS: łuki dopisane do arbitralnego tipa po dodatkowych
9mm trafiały w bank/ramę. Chwyt był JUŻ przed łukiem. Pomogła jednoczesna
alokacja ogonów po zachowanymfirst9, pełnego rzędu chwytówFL_P, orientacji
tej samej główkiG2, przelotów opaski i drogi obciążenia. Nie ponawiać
odrzuconegoG2lane1. Miejsce zakotwienia wybierać z faktycznej zachowanej
sekcji: bbox żebra sięgał40,52, lecz miejscowo materiał kończył39,909.
Guard dodatniego wspólnego materiału musi poprzedzać odbiór świata.
Po przecięciu szyny sprawdzić KAŻDĄSolid, nie tylko jedną nazwę obiektu.

19.10, sąsiednie wyjścia jednej WAGO nie gwarantują tego samego przekroju:
P_SYS.1 maRizolacji1,55, P_SYS.2/.3 po2,1. Wyprowadzać profil kontynuacji
z rzeczywistej powierzchni końca, a promień gięcia osobno z kontraktu.
Kontakt powiększonej rezerwy nie jest kontaktem rzeczywistego przewodu;
przy ważnym innym świadku odrzucenia nie ponawiać całej złej topologii.

19.10, połączony graf punktowy nie planuje promieni ani wspólnych wiązek:
CAŁY test108guides odrzucił wszystkie schodkowe łuki. Korytarze planować
z prostych i rzeczywistych stycznych łuków, przekrój wiązki od początku;
nie dodawać kolejnych lokalnych wygładzeń. Wspólny komponent nadal NIE
kwalifikuje łącznika od rzeczywistego źródła (bywał41,925mm) ani pakowania.

19.10, granica trasowania nie zawsze jest końcem chwytu: W080 zachowuje
12mm prostej ZA pełnym9mmchwytem. Nową trasę zaczynać na rzeczywistej
końcowej powierzchni prefiksu. Aktualizować mały overlay przy zachowaniu
identyfikatorów/None, nie kopiować całego246-końcowego rejestru. Niezmienione
komórki siatki i odebrany ruch reużywać tylko z przypiętymi źródłami;
zawarty w mapie graf nie jest jeszcze dowodem promieni ani pojemności.

19.10, odbiór całego układu: cache dokładnych BoundBox175niezmienianych
aktorów/1176stałych/3888pozycji kosztował0,516s; pozostały odbiór zakończył
się w43,578s. Nie wyliczać granic CSG od nowa dla każdej pary. Zachować
dokładną geometrię w narrowphase i aktualizować cache przy transformacji.
Zawierający CAŁY moduł prostopadłościan wewnątrz prawdziwego obrysu
z wymaganym marginesem jest dodatnim dowodem przestrzeni dla modułu;
nakładanie bboxów nadal nie dowodzi kolizji. Nie mylić tych dwóch reguł.

19.10, odbiór geometrii: BRep po imporcie/eksporcie nie musi zachować
identycznych bajtów, także przy ponownym zapisie tym samym API. Nie
normalizować kolejno zapisu aż SHA pasuje. Niezmienionych aktorów nie
reserializować: przenosić dokładne przypięte bajty rodzica i zmieniać tylko
nową część. Historyczny dowód wejścia przewodu zachować z rodzica; bieżący
przewód nie może być własną bazą porównawczą. Dwa null-fuse przy nowych
współpowierzchniowych szynach rozwiązało odejmowanie od już odebranej,
połączonej bryły, nie kolejny ofset albo zmniejszenie marginesu.

19.10, wspólną scenę odzyskiwać z CAŁEJ przypiętej receptury, nie ręcznej
listy grup. Pominięcie9częściP_REAR tworzyło pozorne nowe problemy z Pi.
Test ma odrzucać brak dowolnej części, nie tylko sprawdzać licznik grup.
Minimum chwytu3+9 nie jest maksymalną prostą: pełny boot USB wchodził
w inny zwój kabla mimo poprawnych452mm/R30 i samokontaktu samej żyły.
Przydzielenie30mm i ponowne rozwiązanie całej długości usunęło ten
konflikt własny. Najpierw pełny kabel vs pełny własny zespół/boot, dopiero
świat; nie kupować kolejnego kabla ani przemieszczać losowo modułów.

19.10, rzeczywisty błąd polityki odbioru: zatrzymanie po pierwszej złej
parze ukrywa pozostałe konflikty tej samej hipotezy. Trzy kolejne takie
przebiegi ujawniły kolejno H5, zasilaniePi i GPIO; wspólny przebieg pokazał
równocześnie wnętrzePi, bank, obrys i ramęBUS. Po poprawnym konstruktorze
zbierać wszystkie konflikty zamrożonej hipotezy w jednym ograniczonym
odbiorze, zapisywać i wznawiać ukończone pary. Błąd bryły nadal blokuje
dowód. Zmiana krzywej unieważnia jej wewnętrzne pary we własnym module,
nie wolno odziedziczyć ich przez samą nazwę grupy. Nie wycinać nowego
materiału ramy z testu tylko dlatego, że wcześniej stykała się z backplate.

19.10, retrospekcja N01 po rozroście kontrolerów: centrum grupy NIE jest
płaszczyzną PCB. W hipotezie coupled-two-level opisano PCB BUS jako X131,
lecz przypięta rzeczywista bryła BUSsupplier0 ma X125,7..127,3, a Pi
X41..126. To wykrywalne nakładanie przed macierzą całego świata. Przed
kolejnym wariantem odczytać powierzchnie/otwory/rzeczywiste zajęte końce
aktywnego blokera i dopiero wyprowadzić położenie grupy. Nie planować
ze środka obwiedni ani z nazwy parametru. Brak kolizji samych korpusów
nie obejmuje pełnych obsadzonych złączy i narzędzi.

Nie tworzyć następnego ogólnego solvera, aby uzasadnić następną ręcznie
zgadniętą pozycję. Najpierw jeden wspólny przekrój i rejestr ograniczeń
aktualnych blokujących interfejsów Pi/BUS/USB/bank/rama/ruch. Rozdzielić
kupną bryłę, konserwatywny budżet oraz niepotwierdzone założenie projektu;
odrzucenie PiBudget nie dowodzi kontaktu producentowskiej części. Nie
zmniejszać promieni/izolacji/obwiedni dla wyniku. Uzupełniać dane tylko
aktywnego blokera, nie robić kolejnego audytu całego robota.

N01 ma kończyć konstruktywny wspólny PLAN, nie uprzednio wykonywać
produkcyjne N03 ani pełne indywidualne trasowanie N04-N05. Wykorzystać
odebrane JR/bank/źródła/fabryczne krzywe. Na wejściu sprawdzić tanią
poprawność konstruktora i podstawowe sprzeczności wymiarowe; dopiero
potem jeden odbiór zmienionych interfejsów. Zakończone pary reużywać po
geometrii/źródłach, nie mnożyć kontroli przez zmianę etykiety kontrolera.
Raportować zamknięte decyzje i blokery; linie kodu, JSON-próbki i liczba
odrzuconych prób nie są ukończonym wynikiem ani dodatkowym procentem.

18.10, zaciski źródła: przed obliczaniem pełnych wachlarzy i całego świata
sprawdzić niezmienny wewnętrzny fit WSZYSTKICH kupnych oczek na rzeczywistych
osiach śrub. Założenie okrągłego obrysu końcówki nie wystarcza: rzeczywisty
kształt oczka ogranicza orientacje. Odebrany wspólny pinwheel daje sześć
rzeczywistych luzów >=1,6745mm; dopiero ten układ przenosić sztywno z całym
źródłem i dołączać chwyty/trasy. Ruch całego źródła nie naprawia błędu
wewnętrznego. Nie obniżać marginesu, żeby uratować odrzuconą rodzinę.

18.10, wejście wymiarowe przed następną geometrią: FHAC miał w wybranym
szablonie51×20,25×22mm, nie założone15,5mm przekroju. Monitor41×25×12,
nie21×15×4. Przekrój po obrocie liczyć z pełnego źródła. Źródło oznaczone
supplier815revCpad jest punktem lutowniczym, nie wyjściem płaszcza przewodu.
Najpierw PAD→bare/izolacja→jacket/grip i źródłoweOD/R, potem trasa. Błąd
semantyki nie jest usuwany przesunięciem płytki ani kolejnym mocowaniem.
Po odejściu od przedniegoPi nie dziedziczyć automatycznie Head+35.

18.10, wspólne właścicielstwo: nie próbować trzeciej pozycji samegoPi,
gdy oba odrzucenia wskazują PWM/pełne złącza i kanały MAIN. Alokować
Pi/PWM/WSZYSTKIE20stacji z fabrycznymi końcami równocześnie. Zachowana
belka z wyciętym kanałem nie może zostać zastąpiona pełnym prostopadłościanem.
Odwrócone śruby/nakrętki wymagają ponownego stosu i spacerów, nie tylko
braku kolizji. Sleeve20mm z14mm przed końcem factory wymaga co najmniej
14mm prostej PO łuku; wcześniejsze10mm zostawiało4mm na łuku.

18.10, ramy źródeł: nie wyciągać układu z nazwy folderu. Wybrane W3yaw
GUIDE już miały CP2SHIFT, tak jak zapisane W2local. Dodanie go drugi raz
dało błąd(−42,0,+25)mm i pozorny problem odbiornika. Przed transformacją
porównać punkt z zapisanym natywnym sąsiadem i przypiętym boundary-check;
test z samą wpisaną na sztywno współrzędną nie weryfikuje jej pochodzenia.
Granica ciągłego przewodu nie wymaga wymyślonego złącza ani ściany wtyku.
Przy ruchu całej głowy jej zachowane lokale jadą w tej samej grupie rigid;
nie powtarzać jej styków własnych. W bramce powietrznego prześwitu dokładny
dystans odrzuca konflikt bez kosztownego common; zerowy dystans nie jest
automatycznie dowodem dodatniej objętości kolizji. Zapisywać ukończone pary.

18.10, N01: analiza całych fabrycznych przewodów i zakończeń PRZED szkieletem.
Samo rozmieszczenie oprawek/płytek i bezkontaktowy wspornik nie stanowią
wspólnego układu. F_PI/P_SYS/MAIN/splice analizować jako jeden tor, z obiema
stronami oprawki, termokurczem20mm, bare overlap8mm i dwoma9mm chwytami
POZA termokurczem. Odległość prosta jest dolną granicą, nie trasą.
Cztery pozorne kandydaty przeszły tę granicę i rozłączne obwiednie, lecz
odpadły już na kierunkach/R6/końcach, bez kolejnej operacji CAD.

Nie wstawiać generycznych słupków przez istniejące nakrętki i podkładki.
Najpierw ich rzeczywiste poziomy, potem jeden nośnik z drogą do ramy.
Czysty test kolizji nie wykrywa braku połączenia: most nad szyną wymaga
korzenia, a celowy kontakt z podporą wymaga faktycznego osprzętu.

Kierunek starego prefiksu może być sprzed motion_receiving_changes, gdy
punkt jest już w nowym native. Przeliczać te ramy osobno, raz. Dawny GUIDE
nie jest automatycznie pinem ani wyjściem wtyku producenta; BUS H5 mówi
to wprost. Zachować źródło i bramkę, nie dopisywać nowej pewności.

Pamiętać obwiednie stałych brył w pętli par. W tym bloku10pozycji zajęło
183s; po wznowieniu z cache pozostałe39 wraz z odczytem trwało99,859s,
bez ponownego sprawdzania gotowych10. Dodatkowe pozycje poza przyjętymi
0..35 opisywać oddzielnie; nie rozszerzać z nich po cichu zakresu kładzenia.
Nie wszystkie9mm chwyty są przy ustach złącza: zatwierdzona recepta może
mieć chwyt na prostej PO łuku. Pełną rezerwację przenosić wraz z nim.

15.10: etykieta `Band` nie dowodzi kontaktu główki opaski. Najpierw
rozdzielić pętlę/główkę i wskazać rzeczywistą parę; w CP2 kontakt był
w pętli, więc zmiana strony zamknięcia nie mogła pomóc. Limit pozycji
wyznaczony z jednego wyjścia/promienia nie kwalifikuje pełnego chwytu:
uwzględnić także jego kolumnę, ramię i wszystkie ruchome sąsiednie bryły
przed kolejnym wyborem położenia. Lokalny RR-only ekran nie może być
bramką do budowy ramion przecinających zachowane serwo lub własny kabel.

Aktualizacja: 06.10.2026. Krótka pamięć projektowa, nie dziennik wykonanych prób.
Czytać przed zmianą układu robota, planowaniem dłuższego etapu lub po dwóch
nieudanych próbach tego samego interfejsu. Dopisywać tylko nowe wnioski,
które zmieniają sposób pracy. Bieżący stan pozostaje w HOBBY_COMPLETION_PLAN.md.

## Krótka procedura następnej sesji (13.10)

1. Czytać aktualny wynik/licznik i NEXT, nie cały historyczny dziennik.
   Ustalić jeden cel dostarczenia, przypięte wejścia i warunek zakończenia.
   Procent ukończenia nie jest procentem czasu. Nie powtarzać dawnych estymat
   po zmianie zakresu; nie obiecywać pełnegoW5 na podstawie jednego uchwytu.
2. Przed detalami połączyć w jednej rezerwacji części stare ORAZ wszystkie
   nowe podpory, przewody i ich ruch. Rozwiązać montaż. Zwykły serwis prototypu
   może wymagać zdjęcia sąsiada; nie dopisywać szybkiej wymiany jako wymogu.
3. Zamrozić przyjęte końce/położenia. Kontrola wskazuje konkretną parę,
   pozę i materiał konfliktu; dopiero wtedy zmienić całą wadliwą gałąź.
   Po dwóch niepowodzeniach tej samej przyczyny zmienić układ, nie offset.
4. Budować natywny detal raz, po akceptacji wspólnego materiału. Przeniesiony
   zapis, zmiana/cofnięcie parametru i właściwy eksport kończą podzespół.
   Test kolizji nie dowodzi drogi obciążenia, wytrzymałości ani montażu.
5. Przed długim procesem zapisać wejście i wznowienie. Zmiana wyboru pliku/
   komunikatu nie unieważnia brył, jeśli kod geometrii i wszystkie wejścia
   są dowodowo identyczne. Zmieniona bryła/promień/algorytm unieważniają
   właściwe pary. Nie naprawiać wydajności przez pomijanie trudnych par.

## Co się nie sprawdziło

- **Osobne trasy nowych wsporników, choć każda omija stare części.**
  13.10 wspólny test12podpór wykrył3skrzyżowania ich ramion w ruchu.
  Włączenie pełnych nowych podpór do przestrzeni planowania pozwoliło
  zmienić tylko2gałęzie stałe, zachować34drogi i końce;50sprawdzeń
  rzeczywistych nowych interfejsów bez kontaktów. To nadal nie test
  całej wiązki. Najpierw wspólne zajętości ruchu, potem konkretne ramiona.
  Mierz koszt kontroli: dla kryterium objętości twardych części wystarcza
  dokładne przecięcie; odległość zachowaj tam, gdzie wymaga jej luz kabla.
  OperacjeOCC wykonuj na kopiach, jeśli zmieniają serializowane flagi
  wejść. Zapisuj bryły i wyniki par, również negatywne, przed wznowieniem.

- **Dopisanie wygody serwisowej do kryterium prototypu.** Plan CP2 przewiduje
  montaż płytek na stole i głębszą naprawę przez odwrócenie etapów montażu.
  Wymaganie wymiany U1 z zachowaniem całej otaczającej wiązki wywołało serię
  niepotrzebnych prób parkingu BUS. Przed nimi porównać cel z zatwierdzonym
  kryterium. Nie przebudowywać prototypu dla szybkiej rzadkiej naprawy.
  Nadal trzeba wykazać montaż i opisać rzeczywiste rozłączenia; nie przenosić
  tego uproszczenia na rutynową wymianę bezpiecznika ani udawać zaliczonego
  serwisu całego robota. A2/W5 pozostają odrębnymi rezultatami.

- **Trasy sprawdzone bez ich rzeczywistych podpór.** Dowód wolnej przestrzeni,
  który wyłącza `replaceable_support`, nie kwalifikuje obecnego złożenia.
  Przed projektowaniem chwytów związać aktualne pozycje modułów z natywnymi
  płytami, kolumnami i mocowaniami obu stron. Jawnie wskazać części zastępowane.
  Nie dopasowywać chwytów do trasy przecinającej zachowaną kolumnę ramy ani
  usuwać kolumny, żeby otrzymać zielony wynik. Najpierw uzgodnić ten interfejs.
- **Dopasowywanie wnętrza do odziedziczonej skorupy.** Powstawały kolejne
  wycięcia, podpory i trudne trasy. Najpierw zestawić rzeczywiste moduły,
  przewody, narzędzia i ruch w jednym układzie. Dopiero potem ustalić obrys
  tułowia. Powiększenie obudowy może pomóc, ale samo nie naprawi kolejności
  montażu ani dostępu do śrub.
- **Seria lokalnych poprawek bez wspólnej geometrii.** Usunięcie jednego
  kontaktu potrafiło stworzyć następny. Planować cały związany interfejs:
  obie strony złącza, wszystkie wyjścia, izolację, opaski, sąsiednie przewody
  i podpory. Po dwóch nieudanych próbach wrócić do przyczyny i układu;
  kolejna próba wymaga nowego założenia, nie samej zmiany przesunięcia.
- **Demontaż zaczynający się od podzespołu już na stole.** Górny moduł dawał
  się unosić w próbach, ale śruby wyjmowania całej kasety były zasłonięte.
  Rozpisać drogę od zmontowanego kota do stołu, z dostępem do każdego
  mocowania i rozłączeniem przewodów. Zależność kołowa zatrzymuje ten układ.
- **Mieszanie wersji.** Widok E6 miał właściwe uszy, lecz starszy tułów;
  wybór R53 i późniejsze kandydaty W1/W5 nie tworzyły jednego aktualnego
  złożenia. Każdy podgląd musi wskazywać źródła, zastąpione części i status.
  Nie pokazywać historycznego kota jako aktualnego projektu całości.
- **Zbyt optymistyczne estymaty.** Kolejne poprawki geometrii wydłużały etap
  poza zapowiedziane godziny. Estymować do konkretnego wyniku, oddzielać
  czas obliczeń od pracy i przerw. Po nieudanej bramce aktualizować estymatę.
  Procent ukończenia nie jest procentem czasu.
- **Nadmiar raportów i wariantów zamiast wybranego wyniku.** Zachowanie
  odrzuconej próby może być użyteczne, ale nie jest ukończonym podzespołem.
  Używać jednego katalogu bieżącej pracy, krótkiego zestawienia wyników
  i jednego wybranego eksportu. Nie ponawiać zamkniętych kontroli bez zmiany.

## Co się sprawdziło i warto powtarzać

- **Zachowanie gotowych modułów i ich interfejsów.** Traktować ukończony
  podzespół jako całość, dopóki wspólny układ nie wymaga jego zmiany.
  Własność części oraz punkty mocowania muszą być jawne.
- **Czytanie zapisanych brył bez przebudowy całego złożenia.** Do pomiarów
  i planowania używać istniejących źródeł, sprawdzonych położeń i dowodów.
  Ciężkie obliczenia prowadzić w jednym osobnym procesie, odbierać jego
  wynik przed następnym startem i zachowywać źródła bez nadpisania.
- **Sprawdzenie przestrzeni przed tworzeniem szczegółowego CAD.** Wspólny
  układ i rezerwacje wykrywają niewykonalne kierunki taniej niż budowa
  pełnych historii operacji. Rezerwacja ma podaną podstawę i zapas;
  nie udaje wymiaru producenta ani sprawdzonego ruchu.
- **Rozróżnienie obwiedni, bryły i siatki.** Przecięcie bbox wybiera parę
  do kontroli, nie dowodzi kolizji. Bbox splajnu może być konserwatywny.
  Rzeczywisty kontakt sprawdzać na poprawnych BRep; obraz, tessellacja
  i próbki ruchu mają ograniczony zakres. Zachować błędy obliczeń jako błędy.
- **Jeden układ współrzędnych.** Przed łączeniem źródeł ustalić, czy bryła
  jest lokalna czy już zapisana w położeniu całego robota. Sprawdzić znany
  punkt lub oś po transformacji; nie nakładać położenia rodzica drugi raz.
  Gabaryty obejmują także integralne podpory i wyjścia, nie tylko główny korpus.
- **Natywna historia i próba parametru.** Nowy detal powinien mieć użyteczne
  szkice/operacje. Zmienić istotny parametr, sprawdzić współpracujące części,
  przywrócić go i potwierdzić zapis oraz ponowne otwarcie. STL jest eksportem.
- **Weryfikacja proporcjonalna do zmiany.** Korzystać z dotychczasowych
  wyników niezmienionych interfejsów. Sprawdzać nowe i naruszone połączenia,
  a pełne uzgodnienie wykonać przy wyborze kompletu. Lokalny sukces nie
  zamyka całej wiązki, montażu ani fazy 1.

## Przed rozpoczęciem etapu

1. Nazwać wynik i kryterium ukończenia. Wskazać jeden zestaw źródeł.
2. Ustalić obrys modułów, ruch, wyjścia kabli, narzędzia i drogę montażu.
3. Sprawdzić wspólny układ, a następnie budować szczegóły CAD.
4. Przy niepowodzeniu zmienić przyczynę; zapisać, czego nie ponawiać.
5. Zakończyć etap wybranym wynikiem, istotną kontrolą i krótkim checkpointem.

Faza 1 przygotowuje kompletny prototyp do montażu. Pasowania MG92B pozostają
wymienne i prowizoryczne do pomiaru dostarczonych serw. Próby wydruku,
materiału i sprzętu należą do fazy 2; nie są powodem do bezterminowego
polerowania projektu ani podstawą do deklarowania fizycznego PASS.

To lokalne wnioski z tego projektu, nie uniwersalny regulamin CAD. Aktualizować
je po nowym sprawdzonym doświadczeniu, nie dopisywać historii każdego testu.

Przed długą kontrolą sprawdzić zawartość przypiętej sceny: aktualny archiwalny
korpus CP2 nie zawiera52 osobno ładowanych części głowy. Brak kontaktów z
korpusem nie kwalifikuje brakującego interfejsu. Niezmienione dokładne pary
można ponownie wykorzystać tylko po kluczu pełnych brył w world-placement,
promieni i wersji algorytmu. Zachować również ujemne wyniki; zmiana etykiety
ani skryptu otaczającego nie może zamienić kolizji w prześwit.

Przed rezerwacją przestrzeni przypisać każdą kupną część do obwodu i odróżnić
ilość zamontowaną od zapasu. R53 ma5 zamontowanych221-412 +1 zapas; cztery
zamontowane to już wyjściowe złącza MTA. Dodanie ich ponownie wraz z zapasem
tworzy fałszywy problem przestrzeni. Nowe wyjścia mają zastępować te role,
nie mnożyć anonimowe prostokąty. Po zapisaniu FreeCAD może renormalizować
kierunki o około1e-16: identyczność tekstu BRep nie jest konieczna do zachowania
geometrii; porównać pełną strukturę i parametry z jawną małą tolerancją.
Nie uznawać nieprawidłowego odejmowania nakładających się brył za dowód zmiany.

Przed generowaniem przewodów uzgodnić ID z końcami i siecią w wybranej wiązce,
nie z kolejnością numerów. W025/W036 są masami, wejścia MTA FL/FR to W041/W042.
Przy podmianie fizycznego odcinka użyć istniejącej nazwy natywnej: logiczne
W076_EXT zastępuje W076_EXTENSION_CP2, nie tworzy drugiego przewodu.
Blokadę ponownej próby wiązać z geometrią przepisu, nie czasem raportu lub
hashem całego skryptu; zmiana metadanych nie uzasadnia ponownego CAD.
Po zamianie portów receptę generować z bieżącego rejestru obu końców,
nie z lokalnej starej tabeli połączeń. Potwierdzić jednoznaczność zajętych
zacisków przed oceną przestrzeni; poprawne obwody nie naprawiają błędnego
celu fizycznego przewodu (W065/P_REAR w etapie3).

Przy rozszerzaniu zapisanej historii PartDesign jawnie aktualizować Tip.
W wyrażeniach długości dodawać jednostki stałym (`4 mm + Parameters.Gap`).
Sprawdzać stan operacji, jej rzeczywistą bryłę i obliczony wymiar, nie tylko
Body.Shape: cache ostatniego poprawnego wyniku może zasłonić nieprzeliczoną
operację. Próba parametru musi przesunąć również współpracującą referencję.

Sprawdzić rzeczywiste world-Z obrysu, nie dodawać do jego wysokości poziomu
płyty montażowej. Otwarty prototyp nie wymaga górnej osłony, ale lokalne
0kontaktów nie dowodzi zmieszczenia w zaakceptowanym tułowiu. Wspólny plan
poziomów ma uwzględniać średnicę całej upakowanej wiązki i zapas, nie tylko
odległość osi. Wyjścia do głowy/ogona jawnie oddzielić od tras wewnętrznych.

Akceptacja lokalnych mocowań nie kwalifikuje ich zachowanych położeń wobec
nowego obrysu. Przed trasami zmienionej wiązki sprawdzić wspólnie wpisanie
kupnych rezerwacji w rzeczywistą bryłę tułowia, nie tylko wysokość Z. W CP2
08.10 osiem z20 rezerwacji WAGO przekraczało obrys; dalsze chronienie ich
współrzędnych wymuszałoby kolejne obejścia. Zachować obwody/liczby części,
a naruszone położenia i mocowania ponownie uzgodnić w jednym układzie.

Minimalny prosty odcinek pod chwyt nie jest sztywną współrzędną końca łuku.
Przed detalami sprawdzić wspólnie pełne trasy lekkim ekranem wzajemnych
odległości; dopiero kandydat bez znanych przecięć przechodzi do brył.
Ekran próbek nie jest certyfikatem prześwitu. Wysokość przy zakrzywionym
dachu wyznaczać dla całego obrysu części i zapasu, a następnie przeliczyć
wszystkie jej podejścia razem, nie przesuwać pojedynczego końca.

Przed nowym podejściem sprawdzić sam wymagany punkt odbioru wobec innych
tras. Jeżeli punkt stacji jest zajęty, przesunięcia wcześniejszych łuków
nie rozwiążą przyczyny. W zmianie orientacji źródła przenosić cały korpus,
wszystkie rzeczywiste płaszczyzny zacisków, sterowanie i narzędzia razem.
Sam brak kontaktów korpusu nie kwalifikuje dostępności ani pełnej wiązki.

Przy wachlarzu przewodów nie wystarcza zwiększyć odstępu poziomów: kolejność
poziomów musi odpowiadać kierunkowi rozchodzenia. Przewód po stronie odbioru
zgina się wcześniej, a wcześniejsze w kolejności zacisków przechodzą ponad
nim. Sprawdzić wszystkie gałęzie razem tanim ekranem, następnie bryłami.

Nie omijać przewodem pozostałości NIEAKTUALNEJ funkcji. W CP2 starych20
mocowań WAGO nie wybieramy ponownie, ale skopiowane ramiona SideArms/Ribs/Feet
wciąż były rzeczywistym materiałem LowerCarrier i blokowały5wejść nowego
banku. Usunięcie tylko ich zewnętrznych występów przeszło wspólną kontrolę
12wejść; rdzeń płyty zachowany objętościowo,1bryła/BOP0. To dopiero kandydat:
przed wyborem trzeba odtworzyć odejmowanie natywnie i sprawdzić aktualne
drogi obciążeń/mocowania. Nie mylić usunięcia starego uchwytu z pozwoleniem
na wycięcie aktywnej podpory, płytki lub zmienienie zachowanej części w ciszy.

Pełny wachlarz zaczyna się przed wyborem punktu rozdzielenia wiązki: zarezerwować
wszystkie sąsiednie podejścia zacisków oraz OBA przewody BUS, nie dodawać ich
dopiero po znalezieniu wolnej pętli. Przy rzędzie portów w osiX zakręt wzdłużX
może przecinać sąsiednie identyczne łuki; prowadzić osobnymi pasami w poprzek
rzędu i sprawdzić cały wachlarz. Wirtualny podział płaszcza nie jest uchwytem.
Nie wymuszać przy nim nieistniejącego odcinka pod opaskę ani nawrotuUP.

Nie bronić arbitralnie długości odziedziczonego kabla kosztem setek obejść.
Najpierw ustalić dostępny rzeczywisty dłuższy kompletny element, zachować
promień i zapas cięcia, a krótszy wybrać tylko gdy wszystkie trzy pełne żyły
się mieszczą. Dłuższy kabel nie dowodzi obciążalności, pinoutu ani pasowania.

Przewodu przekraczającego kilka przegubów nie traktować automatycznie jako
jednej swobodnej pętli od serwa aż do rozdzielni. W CP2 taki model wymuszał
wysokie łuki przez głowę i źródła, mimo dłuższego kabla. Najpierw wskazać
odciążenia na sztywnych członach i oddzielne sekcje luzu przy przekraczanych
osiach. To nadal jeden ciągły przewód, nie powód do dodawania złączy.
Płaszczyznę odciążenia wyznaczać z całego członu, także LegLink i osłony,
nie tylko z obrysu kupnego serwa. Matematyczny lokalny pilot nie kwalifikuje
brakujących podpór, odcinków między nimi ani całej wiązki.

15.10, wspólne źródłaHip1: nie przenosić ograniczenia płaskiej konstrukcji
na układ przestrzenny. Warunek dużej rozpiętościY, choć łuki były3D,
przeniósł korzenie na przeciwną stronę i poprowadził kable przez drugą
nogę. Sprawdzać rzeczywisty zasięgXY i stronę nogi, a potem całe bryły.
Zmiana wszystkich czterech korzeni na właściwe strony jest zmianą przyczyny,
nie serią mikroprzesunięć. Matematyka takiego układu nadal nie jestPASS.

Przed usuwaniem fragmentu podpory odtworzyć OSTATNIĄ receptę, nie pierwszą:
tu brak późniejszych BelowBandBridge usuwał także cudze gałęzie. Dowód ma
wykazać podzbiór aktualnej bryły i brak usuniętego materiału poza zakresem
zmienianej gałęzi. Sprawdzone podzbiory zapisywać natychmiast, per właściciel,
z pinami wejść i kodu; następna trasa nie uzasadnia kolejnego liczenia tych
samych drogich union/common. RejestrOPEN nie oznacza braku gotowej trasy:
19prowadzeń istniało już w późniejszych dowodach. Najpierw uzgodnić aktualne
końce i jawne zamiany zacisków tej samej szyny, zamiast trasować je od nowa.

15.10, odciążenia odbiorników: wolne9mm samej żyły nie rezerwuje miejsca
na siodło, główkę opaski i wejście ramienia. Najpierw rozmieścić te pełne
elementy wspólnie, potem prowadzić środek przewodu.19 istniejących tras
i18 dobrych domen chwytów zachowano; zmianaW074 korzysta z wcześniejszej
prostej bez reroutingu, aW024 wymagał nowego podejścia razem z uchwytem.
Wspólna alokacja20 uchwytów/podejścia:2368par,25węzłów,238,078s.
To nadal nie kwalifikuje brakujących ramion ani pełnego środka przewodu.

W pętli planera najpierw sprawdzić wszystkie położenia, zapas długości,
samokontakt i prześwit, dopiero potem kosztowne bryły świata. Samokontakt
najkrótszej matematycznej próby nie odrzuca całego kierunku; szukać pierwszej
poprawnej matematycznie długości. Po odrzuceniu jej rzeczywistą przeszkodą
zmieniać kierunek/rodzinę, nie dokładać kolejnych wariantów luzu.

Nie utożsamiać etykiety całej wiązki z jej pętlą przy biodrze. Jedna
lokalizacja rzeczywistej pary0,391s wykazała konflikt z odcinkiem FABRYCZNYM
RL3, nie z jego Hipflex. Zachowanie źródłowej osi wyjścia i zmiana kierunku
wejścia stałego chwytu może rozwiązać przyczynę bez zmniejszaniaR31,5.
Nowa rodzina powrotu osiowego dała trzecią alokację źródła; pełny komplet,
ramiona i fizyczne pasowanie pozostają osobnymi bramkami.

15.10, pełne36 odbiorników: nie zamrażać pierwszych20 orientacji chwytów,
gdy pozostałe16 nie weszło jeszcze do wspólnego planu. Próba ze stałymi20
dała W013/W069 bez opcji, a W047/W071 miały7/8 dobrych opcji. Przerwano
dalsze liczenie po zapisanym wyniku192,437s, zamiast obrabiać znany martwy
układ. Wspólny wybór36 zachowuje20 CAŁYCH tras, lecz dopuszcza inne
wcześniej poprawne orientacje chwytów. W013/W069 dostały7/6 opcji bez
mikroprzesunięć przewodów; to jeszcze nie dowód wspólnego rozwiązania.
Pozytywne domeny z bardziej restrykcyjnej sceny można odzyskać po
sprawdzeniu pinów, ale końcowy wybór nadal wymaga kontroli wzajemnej.

Ramiona: dokładne CSG na każdym węźle siatki było zbyt kosztowne.
Planowanie na powierzchniach RZECZYWISTYCH brył oraz próbkach przewodów,
a potem dokładna kontrola CAŁYCH segmentów, domknęło8 ramion źródeł:
1145 par,569,781s. Powierzchnia styczna nie jest objętościową kolizją;
mesh może odrzucić/proponować, nigdy sam zaakceptować materiału.

15.10: przed projektowaniem wspólnego docisku odczytać WSZYSTKIE zajęte
porty szyny, także dwa feedy i różne promienie izolacji. NC nie zgadywać.
Błąd jądra CAD nie dowodzi kolizji. Konserwatywny analityczny dowód
separacji działa tylko dla przypiętej rzeczywistej receptury CSG; brak
dowodu nadal blokuje akceptację. Testy muszą zawierać rzeczywisty kontakt.
Natywne ramiona źródeł powstały zanim uzgodniono wszystkie opaski
odbiorników i wiązkę głowy, przez co zostały konflikty RR_G/FL_G.
Następny plan obejmuje jednocześnie ramiona, opaski, dociski i całe kable.
Sześć dodatnich domen na osiem nie jest wspólnym rozwiązaniem ani punktem.
Długie spekulacyjne rozważania też są kosztem: ograniczać je do wyboru
jednej sprawdzalnej zmiany przyczyny; nie zastępować nimi wyniku.


## 29.10 — najpierw własne interfejsy mocowania

Przed kontrolą mocowania do reszty robota sprawdź cały własny prefiks
przewodów, pełne opaski/główki oraz dodatnie połączenia drukowanych elementów.
614 zielonych par z modułami nie wykryło HipRoot→własny płaszcz34.399mm³.
Stronę integralnego łoża wybieraj od case, a zdejmowany cap po przeciwnej;
nie prowadź struta przez przewody. Projektuj otwarte przejścia dla opasek.
Na pochylonym członie stopy i belt muszą używać tego samego datumu panelu;
worldY75 nie był płaszczyzną środka case. Nie dobieraj offsetów próbami.
BOP/isValid/1solid nie wystarczą dla union: sprawdź obecność każdego członu.
Odebrany wariant fuses łączy od seat przez połączone człony do gripów,
bezRefine; stary wynik potrafił zgubić ramiona mimo1solid.
Każdy zmieniony root/cap/belt traci stare zewnętrzne potwierdzenie.
Lokalny odbiór nie daje punktu N01 ani fizycznego PASS.


## 30.10 — datum symetrycznej PCB i zachowanie komórek ramy

- Samo pokrycie symetrycznej płytki nie ustala kierunku portów. W tej próbie
  błędny obrót dawał obustronne difference0 dla PCB; dopiero adapter/J5/C1
  wskazały inną właściwą ramę. Przed transformacją końców użyj asymetrycznych
  nazwanych świadków. Aktualny dowód: day30-outboard-U1-space.json.
- W tej sesji GFA nie mapował Compound self ani rozłącznego tylnego solidu.
  Nie usuwać pustego mapowania jako odpadu. Zachowano tylną1763.305mm³,
  a przednie komórki zweryfikowano osobno i bilansem objętości. Zwykły Cut
  zwracał strict-invalid faces mimo poprawnego źródła; nie robić tej samej próby
  ponownie. Gdy dotyczy naszego prostego uchwytu, zmień jego przekrój wokół
  istniejącej ramy zamiast seryjnie podcinać złożoną starą szynę.
- Nowe dwa dociski adaptera nie dziedziczą dziewięciu chwytów przewodów ze
  starych AnchorLeft/Right. Osobno rozlicz role14końców i dostępne opaski.
  Retencja adaptera i odciążenie przewodów są różnymi funkcjami.
