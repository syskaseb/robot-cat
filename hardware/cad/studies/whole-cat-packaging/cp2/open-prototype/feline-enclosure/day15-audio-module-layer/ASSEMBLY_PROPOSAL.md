# Cała warstwa audio + wspólne podparcie — jeden układ, HOLD pola zawrotu

**Bieżący model:** `audio-layer-proposal.FCStd`, widokcałości i lokalnyPNG. To nie zwolnienie druku ani zasilonego robota. Zachowano pełne części, podstawę,4mocowania z całym metalem i31mm rezerwyPi/BUS. Nie uruchomiono nowej rodziny po wyniku.

## Wspólna decyzja przestrzenna i źródła

- Głośnik100×45×21: X−113..−13/Y−19,5..25,5/Z65,5..86,5, w całości, bez skalowania. Wspólna półka63..65,5 leży nad WAGOdo61,52; korpus pod belkąod88 ma1,5mm. Przesunięcie całego modułu wynika z warstwy nad rozdziałem i bocznego pełnegoBNO, nie z ułamkowego przesuwania belki.
- MAX98357A27×24×13 z terminalami obrócono jako CAŁOŚĆ do pionowej pozyX−62..−35/Y21..34/Z96..120. Podparcie krawędzi na wspólnej płycie; pełne8424mm³ zachowane. Retencja rzeczywistej wersji płytki jest nadal essentialNEXT, nie potwierdzono otworów fabrycznych.
- ReSpeakerLite pozostaje86×35×10 pod grzbietem; zachowane źródło projektu zawiera pełną rezerwę94×43×16 zUSB, X−9..85/Y±21,5/Z140..156. To projektowe założenie komponentów/wtyku, nie dokładny model dostawcy. ReSpeaker iTTP223 są na jednej zdejmowanej górnej ramce opartej na4rzeczywistych portalach; TTPpozostajeX5..30/Y45..65/Z141..149.
- BNO zachowano razem z30×28×10 rezerwą złącza ze źródła, nie tylko25,6×22,7×4,6 gołegoPCB. Głośnik ma do tej rezerwy3,15mm wY. Pełny mikrofon/USB/touch i pozostałe wymagane rozszerzenia nie zniknęły przez brak w57CSV.

Źródłem tych nominalnych profili jest istniejące `robot-cat/hardware/wavego/layout/components.json` — historyczne studium, nie printPASS/nowy wybór katalogowy. Przypięto użyte5rekordów i plik. Z archiwalnego kontraktu interfejsów użyto wyłącznie faktów: AMP=I2S, ReSpeaker=osobnyUSB, para głośnikaBTL — żaden przewód nie jest masą. Nie zmieniano grafu ani aktualnego pinoutu ochrony.

## Materiał, prowadzenie i montaż

Wspólny nośny model dostał półkę głośnika i jej przednią poprzeczkę/tylne podwieszenia, dwa podparciaAMP oraz celowy otwarty kanał w płycie logiki X−75..−63/Y23..43/Z90..94. Nie jest to przycięcie belki pod dawnymAMP: AMPprzeniesiono w całości, a kanał służy układaniu przewodów przed pionowąPCA. Zachowano pozostałe korzenie/belki; rzeczywiste zamierzone składniki bez braków, wspólny materiał1validSolid. Górna ramka mikrofon/dotyk jest osobna, bez wspólnej objętości z dolną konstrukcją. Podział na płaskie wydruki, pełne łączniki, dociskiPCB/obudowy głośnika i dostęp narzędzi pozostają do zaprojektowania po rozwiązaniuHOLD.

Dwa połączone obszary robocze miały poprowadzić5sygnałów/zasilaniaI2S oraz parę głośnika: w kanale7profilów (5×Ø1,6 i2×Ø2,1/.2odstępy/.4zewnętrzny margines), pakowanie7,8×4,7 w8×5; dalej otwarte pole nadPi i pole zawrotu przyAMP. Promienie6,4/8,4 to własne założenia do przymiarki, nie producent ani dawneR35,1. Faktyczne pady/kierunki i długości nie są z tego powodu przyjęte.

**Pierwszy nowy HOLD:** pole `AL_AMP_FREE_TURN_BAY` X−77..−63,25/Y21..34/Z95,25..134,25 dochodzi do krawędzi tackiPi. Poprawne pełne operandy: gap0/common0, próg1,25. To konflikt przydzielonego pola, nie kontakt fizycznego przewodu ani dowód niemożliwości wszystkich przebiegów. OperandyBRep i lokalnyPNG zachowane. Nie wykonano kolejnego wariantu wysokości/roll/cięcia. Ciągłość tego pola i końcowe promienie pozostająnieodebrane.

Zmieszczono w badanym sąsiedztwie zmienione pełneAMP/głośnik, nowe podparcia i rezerwyBNO/ReSpeakerUSB. Dokończono11wcześniej nieodebranych modułów/łożysk.4rooty/BUS i fabryczne źródło są bajtowo identycznymiBRep wworldframe; po serializacjiMCP pointerIsSame nie wystarczał, użyto SHA256 tych samych geometrii. Nie ponawiano pierwszej bramki ani61starych par.

## Kolejność dwóch osób — ta sama konfiguracja, warunkowa

1. A: zachowanyP00/rewizja/8osi/gwint; B: odłączona bateria, przygotowanie E1/MODULE i końców na stole pozaPETG. Nie rozłączać wirtualnie lutów.
2. Banki/WAGO/pełne końce układać przed wspólnym szkieletem i głośnikiem. A podtrzymuje konstrukcję, B montuje4zachowane zaciski/metal. Rzeczywiste związane zestawy i długości muszą pozwolić na tę kolejność; nie usztywniać ilustracyjnych krzywych.
3. Głośnik na dolnej półce, AMPna wspólnej płycie, pozostałe PCBna właściwych izolujących podporach. Parę głośnika iI2S układać w otwartym kanale PRZED założeniem pionowejPCA/docisków. Nie przeciągać dużych fabrycznych końców przez zamknięty otwór.
4. Górny mikrofon/dotyk zamykać po ułożeniu przewodów i potwierdzeniu pełnychUSB. Przed baterią: rozłączyć istniejącyUSB_AUDIO, zdjąć górną ramkę; następnie rzeczywiste rozłączne końceUSB/zasilaniaBUS i mostekBUS; dopiero odłączona bateria. To plan, nie odebrana trajektoria całego przewodowego zestawu ani szybki serwis.

USB_AUDIO jest OSOBNYM wymaganym przewodem, jegoSKU/długość/matingPi nieodebrane. Nie używać drugi raz dedykowanegoUSB500DelockBUS. Wszystkie4niezależne220/obaMTA, FHACminimum84,5, K1474właściwe de-bity i fabryczne końce pozostają. Actualinstalledlength/fit/cut/slackNULL, bez wymyślonego zapasu/cięcia/przedłużania. Bieżące57części, S0pełne11, S1 i ochrona zachowane.

**Następna decyzja przed detalami:** adekwatne ciągłe pole skrętu/układania z pełnym lokalnym pakowaniem i promieniami względem tackiPi; nie ogłaszaćWholePASS na podstawie wolnych modułów. Nadal potrzebne essential: faktyczny podział i połączenia wspólnej podpory, pełne łączniki/narzędzia/dociskiPCB iretencja banków/baterii, rzeczywiste końce. FIT1rama/masa/ruch,FIT2końce/S0/chłodzenie/stock,FIT3obrysOli/głowaogon nie zostały fizycznie wykonane. BezSTL/slicera/druku/zasilania/zakupu/nowej recenzji.
