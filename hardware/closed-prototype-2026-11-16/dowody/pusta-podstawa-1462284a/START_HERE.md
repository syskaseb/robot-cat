# DODATEK: bieżące P02/P03 do opcjonalnej przymiarki pustej konstrukcji

**Ten dodatek koryguje zakres poprzedniego HOLD tylko dla P02/P03.** DwaSTL CURRENT są z faktycznego bieżącego native5e504127, nie ze starych15NovSTL. Zamrożone88297036 i5e504 pozostają bajtowo identyczne. Nie zmieniono CAD, podziału ani obrysu.

Odbiór mastera/Beauvoir338: sześć niezależnych interfejsów podstawy82e8 ma źródłowe core0missing i odebrany lokalnie dostęp metalu. Brak pełnego związania MTA nie jest wykazanym defektem SAMEJpustej konstrukcji P02/P03. Dlatego wolno rozważyć te dwa większe wydruki jako OPTIONAL_CONDITIONAL_STRUCTURAL_DRYFIT_AFTER_P00, nie jako odebrane mocowania modułów.

1. Najpierw P00 oraz rzeczywista rewizja/8osi/gwint/chwyt WAVEGO muszą się zgadzać. Bez siły, wiercenia, gwintowania ani cięcia kupnej ramy. Jedna osoba ustawia pustą konstrukcję, druga sprawdza połączenia i dostęp. Brak wykonanych fizycznych testów/obciążenia.
2. Dopiero potem opcjonalnie dwaP02/P03 CURRENT z tego folderu. Łączyć z właściwymi źródłowymi szynami/splice według zamrożonych źródeł, nie zamieniać ich na starsze deckSTL o innym receiverze. Nie przyjmować zgodności materiału/PCB/MTA z samej przymiarki pustej podstawy.
3. Ułożenie: +Z w górę, najniższe rzeczywiste powierzchnie na stole; STL wyłącznie przesunięte do dodatnichXYZ/Z0. Płyta nad dolnymi receiverami wymaga usuwalnych podpór ODSPODU w rzucie części. Nie zalewać podporem kanałów nakrętek ani otworów; zachować boczny dostęp.5mmbrim z każdej strony i podpory mieszczące się w rzucie dają obszary około179×174×26,48 oraz178×174×27,48mm, pod256. To plan orientacji, NIE wynik slicera/drukowania.
4. Ponowny odczyt mesh: zamknięte/1komponent/poprawny winding/dodatnia objętość, błąd objętości względem źródła zapisany. To kontrola eksportu, nie materiału/wytrzymałości/warping.

**NADAL HOLD:** P19/MTA0100335pełneMINIVALpockets, POWER/W043-F_AUX, nowe P11/P10/keeper i zależne stock/tools, PCB/audio/inline/S1monitor, okablowanie, headmotion/dekoracje/osłony i obciążony cały kot. Nie drukować tych grup z tego dodatku. Nie zmienia on 4zamrożonych próbek ani indeksu8829; kurator master łączy je z tym jawnie ograniczonym dodatkiem.

Hardware tylko znany nominalny: zamrożonyHARDWARE.md wymienia8×M2.5×16 dla źródłowych osi i4×M3×10/4nakrętki/4podkładki dla łączenia decków; to zapotrzebowanie UNCONFIRMED, nie potwierdzenie gwintów/zapasu ani nowa lista zakupów. Dla samej pustej przymiarki nie dokładamy P19/PCB/bodycovermetalu. Źródłowych sześciu odbiorów nie awansujemy do physicalPASS. wholekit=false/physical=false/cut-fit-slackNULL.
