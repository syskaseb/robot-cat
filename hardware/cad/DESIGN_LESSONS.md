# Wnioski z projektowania 3D robot-cat

Aktualizacja: 06.10.2026. Krótka pamięć projektowa, nie dziennik wykonanych prób.
Czytać przed zmianą układu robota, planowaniem dłuższego etapu lub po dwóch
nieudanych próbach tego samego interfejsu. Dopisywać tylko nowe wnioski,
które zmieniają sposób pracy. Bieżący stan pozostaje w HOBBY_COMPLETION_PLAN.md.

## Co się nie sprawdziło

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
