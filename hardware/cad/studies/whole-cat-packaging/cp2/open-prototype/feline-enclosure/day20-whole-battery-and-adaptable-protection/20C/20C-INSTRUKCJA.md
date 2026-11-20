# 20C | Wymiana baterii, ochrona wejścia i cztery MTA

**Wybór układu.** Stały XT60H-M po stronie robota znajduje się nad wnęką. Fabryczna połówka F z odgiętką odsuwa się o 14 mm w +Y. Pakiet jest wtedy podparty w gnieździe. Luźne fabryczne żyły pozostają z pakietem. Oddzielny górny próg odtwarza podparcie banku po zamknięciu. Model zachowuje osiem kotew, wybrane moduły i zabezpieczenia, nogi, dwa ruchy głowy, ogon wokół Y i skrzynkową obudowę. [Korekta układu](20C-dry-gate.json) · [Propozycja wyjściowa 20B](../20B-PROPOZYCJA.md)

## Części objęte zmianą

| Nowa część | Ilość | Montaż i efekt |
|---|---:|---|
| C20_FrontFrame | 1 | Zastępuje H19_FrontFrame. Stałe gniazdo małego wspornika F0 łączy się z oryginalną podporą. |
| C20_RearBase | 1 | Zastępuje E19_RearBase. Ma stałe lądowanie XT60 i oparcia zdejmowanego górnego progu. |
| C20_BatteryUpperBridge | 1 | Górny próg wkładany od góry. Dwie półki podpierają końce poprzecznych żeber banku przy X77 i X94. Zewnętrzne uszy opierają się na stałych półkach na Z82. Dwa punkty mocowania i boczne ściany kieszeni utrzymują orientację progu. |
| C20_F0_OpenMount | 1 | Osobny, otwarty wspornik z pozycjami dwóch opasek dla pełnego FHAC0002. Regulacja lądowania i klapki w małym wydruku. |
| C20_Post_OpenSlottedMount | 1 | Otwarta szyna z dwiema szczelinami i podparciem na zachowanym ujemnym banku. Pozwala ustawić pełny WAGO POST_F0 według pomierzonej żyły wyjściowej F0. |
| C20_MTA_FL, FR, RL, RR | po 1 | Cztery oddzielne otwarte uchwyty na istniejących oparciach. Przymiarka korpusu, klapki, uwięzi i obu fabrycznych końców przed zamknięciem. |

Drzwi dolne `E19_BatteryDoor` zachowują swoją geometrię i miejsca połączeń RR. Górny próg zamyka drogę obciążenia z dwóch żeber banku przez podparcia i kieszenie do tylnej podstawy. Model zawiera dwie śruby DIN912 M3 × 12 i dwie nakrętki M3 nominalnej roli zdejmowanej płyty R2. Sprawdzić dostępność tej stali i osadzenie nakrętek. Osiem śrub kotew M2,5 × 16 pozostaje przy kotwach. Wybrać opaski zgodne ze szczelinami o szerokości 3,35–3,5 mm, przygotować po dwie do zaciśnięcia próbki F0 i każdego MTA oraz osobne opaski do punktów odciążenia i podtrzymania uchwytów. Plan wykorzystuje 19 opasek w istniejących rolach. Po trzy na każde z czterech MTA, trzy dla F0 z jego wspornikiem oraz po dwie przy XT60 i POST_F0. Potwierdzić faktyczny rozmiar i dostępność przed montażem. [Indeks części, orientacje i piny](20C-manifest.json)

## Bilans i granice przymiarki

- **XT60.** Pełna para 50 × 22 × 16,5 mm jako wspierany gabaryt wraz z osłonami. Pomiary rzeczywistej połówki F i odgiętki pozostają otwarte. W gnieździe użyć kupionego XT60H-M. Fabryczny F jest po stronie pakietu, a dodatkowa połówka F z zestawu zostaje zapasem.
- **Bateria.** Oba końce fabryczne pozostają z pakietem. Ułożenie od założonego wyjścia do odgiętki wymaga projektowo ok. **169 mm (+)** i **179 mm (−)** razem z zapasem ułożenia. Gdy pomiar obejmuje przewód do końca elektrycznego, odrębnie uwzględnić rzeczywiste odcinki w odgiętce i przy wyjściu z pakietu. Modele rozpięcia i postoju utrzymują tę samą długość dzięki przesunięciu górnego łuku o połowę skoku połówki. Test narożników AUX/BNO obejmuje nominalne wyjście i profil Ø4,8 mm w konkretnym przebiegu.
- **W075.** Oryginalna żyła wejściowa FHAC0002 po stronie robota. **43,57 mm** z projektowym końcem przy limicie 50 mm. Źródło przewiduje przygotowanie końca po faktycznym pomiarze przy zacisku XT60 po stronie robota. Zachować odgiętkę F0, izolację i pełną osłonę. F0 ma założenie 21,5 mm dla zamkniętego korpusu. Wymiar zamkniętej klapki, uwięź i obie odgiętki sprawdzić na FHAC0002.
- **W076/factory.** Cała fabryczna żyła wyjściowa pozostaje od F0 do POST_F0. Dla ruchu po niewielkim łuku w dostępnej przestrzeni pozycje wejścia X58…84 obsługują projektowo ok. **73–103 mm** z końcem. Ostatnie milimetry przewidziano na łagodne ułożenie w otwartej przestrzeni. Ustawić po pomiarze obu fabrycznych końców i wszystkiego, co zajmuje miejsce przy wyjściach. W modelu przed szyną POST żyła unosi się nad jej powierzchnią, z zapasem 2,6 mm dla obwiedni Ø4,8 mm. W dłuższym ustawieniu modelowany promień wewnętrzny wynosi 10,82 mm. Profil, dopuszczalne zgięcie i długość konkretnej sztuki pozostają otwarte. [Próba miejscowa W076](20C-W076-local.json)
- **Stałe odcinki własne.** W001 to LAPP 0107001 Ø3,1 mm z rezerwą Ø4,8 mm przy złączu. W076/custom to HELU 23802 Ø4,2 mm. Projektowe zapotrzebowanie wynosi **139 mm LAPP** oraz ok. **280 mm HELU**, po jednym doliczeniu końców i zapasu ułożenia. Dostępne długości pozostają `UNKNOWN`.
- **MTA.** Części wymagają porównania z czterema pełnymi sztukami 0100335. Próbka obwiedni obejmuje 32 × 18 × 18 mm razem z zamkniętą klapką. FR ma dostęp do klapki w polu o szerokości 35 mm w X. Pomiary pozycji klapki, obu długości, odgiętek i promieni mogą zmienić rozstaw opaski lub mały nośnik. Zwykłe banki z dwunastoma MTA0300330 oraz ich końce pozostają na swoich miejscach.

## Montaż we dwie osoby, bez zasilania

1. Osadzić dwie części ramy i skontrolować osiem istniejących kotew. Przymierzyć wkładany próg, oba jego uszy i obie półki pod żebrami. Zacząć od otwartej podstawy, by mieć dostęp do kieszeni nakrętek. Zweryfikować w rzeczywistym wydruku docisk i brak kołysania.
2. Umieścić wspornik F0 w stałym gnieździe, oprzeć pełne F0 z klapką, zamocować stałe XT60H-M i ustawić POST_F0. Przytrzymać obudowy i sprawdzić odciążenie obu żył F0. Połączyć już wybrane jednostki według źródłowego schematu. Ułożyć W001, HELU i pełną wyjściową żyłę F0 przy otwartych pokrywach. Zachować krótkie przejście przed F0 i dostęp do klapki.
3. Osadzić każdy mały MTA na jego oparciu. Przymierzyć opaski i poprzednio wybrane oba fabryczne końce. Sprawdzić wspólną przestrzeń wiązek przy niewielkich podparciach uchwytu, zwłaszcza przy FL i FR. Dopiero wtedy zamknąć pokrywy.
4. Do baterii otworzyć górne pokrywy i podeprzeć ich wyposażenie, ustawić głowę neutralnie, przytrzymać korpusy XT60. Przesunąć połówkę pakietu o 14 mm w +Y. Odłożyć ją do ręki drugiej osoby. Zwolnić dolne drzwi i górny próg oraz pasy. Osobno przeprowadzić fabryczną połówkę z odgiętką przez górną część otworu i prowadzić żyły podczas ruchu pakietu. Instalacja biegnie w odwrotnej kolejności.
5. Przymiarkę wykonać w obu kierunkach na wyłączonym robocie. Próba cyfrowa sprawdza osobny przejazd korpusu pakietu i przejazd pełnej połówki przez sam otwór po zdjęciu progu. Krytyczny dalszy pomiar obejmuje faktycznie sztywny odcinek wyjścia pakietu w przejściu pod bankiem ATO podczas wyjmowania, ręczne doprowadzenie połówki do otworu oraz utrzymanie izolacji. Próba +Y ze sztywnym przesunięciem przykładowego wyjścia 6 mm weszła w bank ATO, więc zmierzona pozycja i ruchoma część żył są konieczne przed odbiorem całości.

**Stan przymiarki.** Projektowy zakres kończy się na cyfrowym modelu i zmienionych eksportach. `physicalPASS=false`, `actualfit=null`, `cut=null`, `slack=null`.
