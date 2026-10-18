# Wnioski z projektowania 3D robot-cat

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
