# Pi i wspólny carrier — dwie małe próbki, montaż nadal otwarty

Otwórz `pi-battery-carrier.FCStd`. P12, wszystkie kupne części i ich pozycje są **niezmienione**. Cztery pełne zestawy Pi są oddzielną grupą STAGED, nie gotowym montażem. `COUPON_*` to osobne próbki na stół, nie drugie części robota. Referencje dziewięciu istniejących STL/BOM są przypięte SHA, bez ponownych kopii.

## Pi: zrobiony jeden rzeczywisty coupon połączenia

Pełne 4×M2,5×12: łebØ4,5/h2,5/HEX2, dwie podkładki **Ø6/ID2,7/h0,5**, pełna nakrętka AF5/h2, wał12 od spodu łba. Stos10,6 i tip1,4 poza pełną nakrętkę; obecny słupek3mm pozostaje jedynym standoffem. Nominalne śruby/podkładki mają podstawę w kartach Bossard; nakrętka ma nominalny mały DIN934, nie deklarację najnowszego zakresu ISO4032. Zapas/wybrany dostawca/tolerancje NIEPOTWIERDZONE.

Wszystkie16 brył metalu mają common0 z rzeczywistą źródłową płytką Pi/jej4otworami. Nominalny model korpusu BNO ma minimum4,02mm. **Pierwszy otwarty interfejs: łeb/wał zestawu PI0 wchodzi w BNO_INSTALLATION_COVER**, którego rzeczywistego headera/komponentów brak. Nie jest to zmierzony kontakt z BNO ani pozwolenie pominąć miejsce na końcówki. Zatrzymano kwalifikację montażu w robocie przed wycięciem P12; pozostałe globalne relacje/3feed są nieodebrane. Nie zrobiono drugiej rodziny śrub.

`Pi-one-corner-coupon.stl` jest samodzielną próbką **12×14×10,6**, z tacą3mm, słupkiem3mm, pełną kieszenią i bocznym wejściem nakrętki+podkładki. Floor2mm, rzeczywisty sufit pod podkładką Z92,52 / roof3mm; zero sztucznej szczeliny pod łożem. AF5,2 prowadzi AF5 i blokuje pełny obrót; podkładka zachowuje pełneØ6. Cztery bryły metalu nie przenikają próbki, **cała ciągła droga obu elementów** ma common0, HEX2 jest dostępny od góry na stole. Każdy zamierzony człon ma0missing, zakresy zachowane, pojedynczy poprawny druk, wspólny pierścieniowy przekrój słupka i dodatnie połączenie cage/tacy. To nie test siły/pełzania ani pasowania realnego druku.

Najpierw podkładka przez jej górny feed, potem nakrętka niższym feedem od−Y; następnie rzeczywisty pad Pi lub próbkaPCB, podkładka górna i śruba. Klucz **przed** wpięciem GPIO1992/BUS/mikrofonu. Nominalny obszar chłodzenia Pi nie jest fizycznym elementem w udowodnionym otworze, lecz rzeczywiste komponenty i header BNO muszą być obejrzane. Nie montować większego P12 na podstawie samego couponu.

## Carrier: jeden konkretny plan, zatrzymany na pierwszym polu pasków

Aktualne BRep czterech MTA0100335 ma **Zmin67**, X−96/−51/−6/39; stary tekst Z64/X−90 nie jest datumem. Pełne4niezależne220 i oba końce zachowane. Nie zadeklarowano docisku do metalu TE ani potwierdzonego plastikowego konturu na podstawie pudełka.

Jedna planowana część łączy tacę, dwa crossarms/4stopy do decku i otwartą lewą szynę MTA. Kotwy: rzeczywiste ściany P10/P11 oraz szeroko rozstawione stopy (dwie współosiowe śruby same nie dają antyobrotu). Pełne przyszłe zestawy M3 są rozliczone liczbowo w `carrier-premise.json`, ale **nie zbudowane/nie przyjęte** po zatrzymaniu hipotezy. Nie udawano odpięcia lub sklejenia dotychczasowego integralnego druku.

Pod tacą: WAGOtop59,52 +1,25 daje minimum60,77; propozycja podłogi60,8 zostawia1,28 i **2mm floor** pod top-open kanałem2,2. Bateria nadal Z65, nie podniesiona do ramy. Dwa wybrane całe paski **15×200**, opis210z metalową sprzączką nie jest dodatkową zakładką. Sprzączka/szew poza feedem; rzeczywista grubość i wymagane zakładanie nieznane. Pętla/pozostały odcinek200 jest jedynie warunkowym planem: zamknięcie/cały ogon i parkowanie **nieodebrane po pierwszym gate**, bez wymyślonego25mm pull.

**Gate:** pełne pole górnego odcinka15×2,2 przecina rzeczywisty P12: validcommon105mm³. To HOLD tej pojemności, nie kontakt dostarczonej tkaniny. Bateriatop86,5, szynabottom88 i zachowane1,25 zostawiają w tym przejściu **0,25mm na grubość**. Nie założono, że pasek jest tak cienki; nie przycięto szyny ani nie przesunięto baterii. Nie ma STL carriera. Następna decyzja musi dotyczyć rzeczywistej tkaniny/zapięcia i całego przejścia pasków/warstwy nośnej, nie drugiego lokalnego offsetu.

`strap-open-channel-coupon.stl`: **24×24×4,2**, kanał top-open16,2×2,2/floor2, sprzączka poza wejściem. To tylko próbka istniejącego nominalnego paska, nie dowód całej200mm jednostki. Obie siatki zamknięte/dodatnie, orientacja płaską podłogą Z0/post w górę, <256mm. PETG, drukarka/dysza/warstwa/profil nieprzypięte; most feedu~6,2mm wymaga próby, bez slicera/drukowania.

## Dwie osoby / granice wyniku

A podtrzymuje PCB lub próbkę, B ładuje pełną stal i sprawdza feed/antyobrót/HEX2 na stole. Nie dokręcać nieobejrzanych komponentów. Paski układać w otwartym carrierze przed baterią i późnymi osłonami, całe fabryczne końce MTA przed keeperem. W robocie nadal MICUSB/P15→BUS/P13→XT60+balance→bateria; P14/E1solder nie są odpinane wirtualnie. F0 realmouth/zakręt/W075≤50 pozostaje FIT2, bez kolejnej krzywej w tej porcji.

Zapisano dwa użyteczne drukowane **coupony warunkowej przymiarki**, nie gotowy kit Pi/carriera. Physicalfit/cut/slack=NULL, brak zasilania/zakupu/cięcia/drukowania. Source8osi/gwint/masa/ruch i bezpieczne PCB/speaker/mic obrzeża nadal FIT. Inne wspólne chwyty oraz Zeno neckblend/policzki/dółboków i rzeczywisty pitch-sensorroot pozostająNEXT; bez wydłużania ogona.
