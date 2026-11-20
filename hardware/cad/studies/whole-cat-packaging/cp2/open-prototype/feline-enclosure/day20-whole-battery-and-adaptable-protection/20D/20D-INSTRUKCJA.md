# Wejście baterii 20D do przymiarki

Połówka instalacji XT60H-M jest stała. Pełną fabryczną połówkę F z odgiętką przesuwa się ręcznie o 14 mm w +X, gdy bateria jest podparta w swoim gnieździe. Zasilanie dochodzi z krótkiego boku pakietu GEA223S30X6GT, omija dalszą krawędź AUX i wchodzi łagodnym łukiem od +X. Zdjęcie tej dokładnej wersji pokazuje krótki bok i dodatkową fabryczną wtyczkę. Współrzędne samych wyjść, kierunek po usztywnieniu przez odgiętkę i wolna długość obu żył pozostają parametrami próbki. [Zdjęcie producenta](../../../../../../../../reference/battery-exit-2026-11-20/manufacturer-view-1.jpg)

## Montaż dwóch osób

1. Zamocować trzy małe adaptery przed założeniem górnych pokryw. Na podstawie tylnej wsunąć klucz adaptera XT60 w istniejącą kieszeń i przeprowadzić opaskę pod półką oraz przez zagłębienie u góry. Druga opaska stabilizuje korpus i odgiętkę robotowej połówki. Oba oparcia adaptera dają łącznie około 102 mm² nominalnego styku.
2. Przewlec ogon opaski przez przelotową szczelinę 3,4 × 2,2 mm w dodatnim żebrze ramy. Wsunąć adapter F0 na wargę żebra od strony środka i zamknąć opaskę mocującą. Otwarta półka ma dwa stanowiska opasek, które trzeba ustawić poza klapką i uwięzią. Sprawdzić pełny skok klapki wraz z chwytaniem bezpiecznika i odciążeniem obu fabrycznych wyjść.
3. Włożyć nakrętkę M3 w boczny zacisk wspornika POST, oprzeć go na istniejącym narożniku ramy i docisnąć śrubą DIN912 M3 × 12. Od dołu dostępny jest punkt wsunięcia nakrętki. Od góry pozostaje otwarta listwa z przesuwaną opaską WAGO. Po przymiarce pełnego wyjścia F0 ustawić port POST w zakresie Y −34…−20 mm. Jedna opaska trzyma korpus z dala od dźwigni, druga odciąża ustalone przyłącza na osobnym odcinku podpory.
4. Osoba A utrzymuje pakiet poziomo. Osoba B chwyta oba pełne korpusy, rozłącza w osi X i przejmuje fabryczną F wraz z odgiętką oraz małą wtyczkę. Zdjąć dolne drzwi i górny próg szczeliny. Wypięte końcówki prowadzić przez otwartą gardziel razem z obsługą pakietu, z osobnym ręcznym odłożeniem każdej końcówki poniżej ATO. Sprawdzić wkładanie w odwrotnej kolejności. Górny próg wraca na dwie istniejące półki nośne. Pełną ciągłość ręcznego przełożenia z realną wiązką ocenić na próbce.
5. Zamknąć pokrywy po sprawdzeniu, że główne żyły łagodnie przechodzą po zewnętrznej stronie narożnika AUX, a dodatkowa wtyczka ma miejsce przy zewnętrznej długiej ścianie pakietu. Obwiednia jej parkowania ma 24 × 12 × 14 mm i jest założeniem projektowym. Wtyczka pozostaje wolna i dostępna przez otwartą wnękę.

Liczba opasek w tych rolach wynosi 19. Cztery MTA wykorzystują po trzy, F0 trzy, XT60 dwie, POST dwie. Mocowanie POST dodaje jedną śrubę i nakrętkę M3 istniejącego typu. Górny próg zachowuje swoje dwie śruby M3 × 12 z nakrętkami, a osiem kotew pozostaje przy M2,5 × 16. Sprawdzić dostępność stali i grubość rzeczywistych opasek, zwłaszcza ogon opaski przechodzący przez szczelinę 3,4 × 2,2 mm.

## Długości i rezerwy

| Jednostka | Projektowe zapotrzebowanie |
| --- | --- |
| Oryginalne żyły BAT | Od obudowy pakietu do odgiętki **135,0 mm (+), 131,9 mm (−)** w pokazanym obszarze, po doliczeniu 8 mm na ułożenie każdej żyły. Wartości mierzyć po izolowanej części, pomiędzy rzeczywistymi końcami odniesienia. Fabryczne końce pozostają całe. Próbka wyznacza korektę wobec przyjętego przebiegu. |
| W075 | Oryginalna pomarańczowa żyła wejścia F0. **37,34 mm** łącznie z projektowymi 5 mm na kielich XT60H-M. Tylko strona robota może być przycięta po przymiarce, do dopuszczonych **50 mm**. Bez dodatkowego połączenia przed F0. |
| W076 fabryczne | Całe wyjście FHAC0002. Nastawy nominalne zapewniają **89,67–103,67 mm** łącznie z projektowymi 11 mm na wejście WAGO, łuk R20 mm po osi żyły. Rozstaw osi dwóch wejść WAGO przyjęto jako 5,5 mm. Rozstaw i położenie końcowe dobrać do pomierzonej sztuki. Półka i opaski otwierają się od góry. Dłuższą lub krótszą sztukę ocenić w tej samej wnęce przed ustaleniem małego adaptera POST. |
| W001 | Ciągły, stacjonarny LAPP 0107001 Ø3,1 mm, obwiednia strefy XT60 do Ø4,8 mm. Projektowy blank **89 mm** obejmuje końce i jeden zapas ułożenia. |
| W076 własne | HELU 23802 Ø4,2 mm od POST do S0, po stronie chronionej. Projektowy blank **371 mm** obejmuje końce i jeden zapas ułożenia. |

Nominalny aktualnie wybrany zapas projektowy obejmuje **3 000 mm LAPP** i **9 000 mm HELU** według *phase1-material-selection-r4.json* w zamrożonym pakiecie 19I. W tym zestawieniu W001 obciąża pierwszy zapas o 89 mm, a chroniony W076 drugi o 371 mm. Rzeczywista dostawa i dostępność do cięcia pozostają otwarte.

## Wymiany i sprawdzenia

| Mały wydruk | Zastosowanie |
| --- | --- |
| D20_XT60_Axial_Adapter | Dodawany do istniejącego gniazda w C20_RearBase, ustawia XT60H-M w osi X. |
| D20_F0_Open_Adapter | Zastępuje sam C20_F0_OpenMount. Pełna obwiednia wysokości **21,5 mm** służy do sprawdzenia przestrzeni. Pomiar z zamkniętą klapką, uwięzią i obiema odgiętkami określa dopasowanie małego wydruku. |
| D20_POST_Aft_Slotted | Zastępuje sam C20_Post_OpenSlottedMount. Dolna stopa przenosi obciążenie na ramę, a podniesiona szyna ma miejsce poza siodłem yaw w sprawdzonych pozycjach. |

Przy ponownym montażu użyć wydruków 20C dla ramy, podstawy, obciążonego górnego progu oraz czterech małych uchwytów MTA. Dla każdego MTA utrzymano oddzielne stanowisko z próbką projektową 32 × 18 × 18 mm, obszarem na klapkę i dwa fabryczne końce oraz oknem FR 35 mm. Potwierdzić korpus, klapkę i końce rzeczywistych czterech MTA przed zamykaniem.

Sprawdzian CAD obejmuje pełne obwiednie, chwyty i skok 0/7/14 mm, istniejące sztywne sąsiedztwo oraz przypisane korytarze. Na przedłużeniu przy AUX minimalny modelowy odstęp do płytki wyniósł 1,43 mm, do przyjętej obwiedni wyposażenia 1,20 mm. Przy zmienionych wspornikach sprawdzono tylko dotknięte położenia głowy. Chronione wyjście HELU omija pokrywę i dochodzi do zmierzonej w CAD skrajnej płaszczyzny tulejki S0 `(153,05; 74; 127,80)` mm. Lokalny odstęp izolacji od uchwytu MTA RR wyniósł 0,54 mm, a od wydzielonej wiązki sygnałowej 1,56 mm. Sprawdzić te dwa miejsca przy luźnym montażu. [Próby przy pokrywie, WAGO i S0](20D-local-wires.json)

Próba od górnego założonego wyjścia dawała krótszą trasę, ale została zastąpiona po odczycie zdjęcia dokładnego SKU. Pierwsze przesunięcie złącza o +12 mm dotykało PCA i żebra w końcu skoku. Przesunięcie całej osi 3,2 mm w poprzek uwolniło skok. [Pierwszy sprawdzian](20D-final-gate.json) · [Oparcia i zamocowania](20D-support-fit.json)

- [Zamknięty przód z twarzą](20D-closed-front.png) · [Zamknięty bok](20D-closed-side.png) · [Zamknięty tył](20D-closed.png) · [Zdejmowane pokrywy i dostęp](20D-open-service.png) · [Przekrój strony pakietu i żył](20D-short-end-cutaway.png)
- [FreeCAD 20D](whole-cat20D.FCStd) · [Trzy zestawy STL/STEP z orientacją i brimem 8 mm](20D-print-index.json) · [Manifest i sumy plików](20D-manifest.json)

Fizyczne dopasowanie, rzeczywiste cięcie i luz mają status `NULL`, `physicalPASS=false`.
