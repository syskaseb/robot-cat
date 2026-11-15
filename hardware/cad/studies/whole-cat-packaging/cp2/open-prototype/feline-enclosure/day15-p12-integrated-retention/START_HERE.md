# Wewnętrzne mocowania Pi i prowadzenia pasków — carrier HOLD

Otwórz `p12-integrated.FCStd`. To **jeden zapisany kandydat**, nie nowy przyjęty układ ani gotowy kit. Pozycje kupnych części/baterii i wszystkie fabryczne końce są zachowane. Tylko `internal-Pi-coupon.stl` wydano jako izolowaną próbkę bez zasilania. Duży P12/carrier mają wyłącznie native+BRep do kontynuacji; nie są wariantem do wybrania do druku.

## Co zamknięto w zakresie CAD

- Cztery pełne standardowe M2,5×8 +górna podkładkaØ6/h0,5 +pełna nakrętkaAF5/h2. Stos6,1/tip1,9; nie cięto śrub. Dolne4podkładki jawnie zastępuje **2mm integralnego roofu**. Oryginalny standoff3 i datumPCB98,52 bez zmian. Floor2, nutslot2,1, roof2; rozszerzona stopkaØ9/taper do staregoØ5 przy PCB. Nie naciska większą stopką nieobejrzanych komponentów.
- Cała12brył stali przechodzi PCB, nominalny BNO i **pełny istniejący BNO_INSTALLATION_COVER** (36relacji). Nie pominięto obwiedni. Wszystkie4nakrętki mają **pełną pionową drogę przez topwell, następnie8mm sidefeed** do antyobrotu, przed instalacją Pi. W aktualnym podziale **pierwszy słupek należy do P10, trzy do P12**; nie sklejono fikcyjnie dwóch wydruków. Nowy materiał stopek przeszedł kontrolę aktualnych sąsiadów, reszta dawnych dowodów przez identity/subset.
- Jedna zaktualizowana próbka **12×22×6,1**, poprawny pojedynczy solid, zachowany każdy zamierzony człon/extent, pełna3brył stalcommon0. STL zamknięty; PETG, płaskim spodemZ0, roof2 nad kanałemAF5,2 i otwarty topwell wymagają fizycznej próby. Profil/dysza/drukarka nieprzypięte. Próbka najpierw, nie dużyP12. Nie dodano drugiego dystansu ani pozornej nakrętki/gwintu.
- Dwie stacje pasków **29,5 i52,5** wyprowadzono z wolnego pola pomiędzy prawdziwymi kotwami BUS, nie z dawnego15/80,5. Wykonano zaokrąglone, otwarte od dołu prowadzenia16,2×5,2 dla pełnych **dwóch warstw2×2,2**: własny luz0,6/0,4, ciągła pozostała szyna4,7mm, minimalny przekrój18,8mm² — bez strengthPASS. CSseaty/BUSroot nie przesunięte; dodatnie człony/oryginalny materiał poza deklarowanymi otworami i prowadzeniami0missing.
- Model zawiera **każdy cały wybrany pasek200**: pętlę, projektową rezerwę20 na closure (NIE wymagane25pull), pełną pozostałą część49,35 i headfield; rzeczywiste BRepfields są autorytatywne w `actual-stock-fields-and-effectivity.json`, a nie starszy rozmiar pudełka w planie. 210inclbuckle nie dodatkowa zakładka. Deklarowane gabaryty sprzączki/tkaniny/lapu nadal FIT. Wszystkie pola przeszły pierwszą kontrolę modelowanego voidu/P13/carriera/baterii; pełna pozostała kontrola całego układu została zatrzymana na śrubie S0 — nie ma stockfit/closurePASS.

## Co zatrzymało CAŁY wariant

Rzeczywiste4stopy mają kontakt z deckiem, carrier nie przenika P10/P11/P12 w pierwszej bramce. Jednak **tylna pełna śrubaM3 carriera przecina kupny `S0_body`: validcommon60,309861mm³**. Nie jest to obwiednia przewodu. S0Xmin107,122, a łeb zajmujeX107,5..110,5: tylna powierzchnia mocowania konkuruje z korpusem S0. Nie skrócono tipa, nie przesunięto łba, S0 ani drugiej rodziny osi; wcześniejszy montaż nie usuwa stałej kolizji.

Surowe pierwsze0,610071mm³ podkładka/frontpad zachowano w `C0-uncut-front-access-raw.json`. Był to brak realizacji gniazda w tej samej konstrukcji: wykonano pełne miejsce washer/nut/socket R4,2 od płaszczyzny łożyska, zachowany kołnierz i lokalny dolny przekrój1,8mm. Stal/osi/typy nie zmienione. Powtórzono tylko zmienioną parę i odebrano wcześniej brakujące klucze, bez894bounds/9pozytywnych exact od nowa. **Nowy fizyczny rear/S0HOLD kończy tę hipotezę.** Brak kwalifikacji pozostałychrootstock/tool/montażu i brak STL carriera.

## Montaż i granice

Dwie osoby: na stole A podtrzymuje próbkę/PCB, B wpuszcza pełną nakrętkę przez topwell i przesuwa pod roof, potem Pi/górna podkładka/śrubaHEX2. Przed GPIO1992/BUS/mikrofonem; nie udawać rozpięcia lutowanego E1. Paski i wszystkie pełne końce4niezależnych220/MTA układać przed zamknięciem carriera. MTA aktualneBRepminZ67, pressure wyłącznie po potwierdzeniu bezpiecznego plastiku, nigdy TE; części/sourcefunctions nie usunięto. Taca, stopy i MTArail są rzeczywiście zbudowane jako jeden candidateprint, lecz po rearHOLD nie zwolnione.

NEXT techniczny dla tej zależności: **inna cała droga tylnego mocowania poza zajętym przez S0 tyłem bramy**, bez ślepego offsetu/zmiany długości. Nie kontynuować w tej porcji. Priorytet kolejnej porcji zgodnie z bieżącą kartą: **wholehead sensor-loadroot + Ola neck/cheek/lowerbody i rzeczywisty opaqueview do Zeno**, nie następna godzina lokalnych śrub. Nie wydłużać trafionego ogona. F0realmouth/bend/W075≤50 nadalFIT2, brak pracy krzywych.

Fizyczne gwinty/8osi/masa/ruch/pady/cooling/stock/buckle pozostają FIT; actualcut/fit/slack=NULL. 57+extras/ochrona/electrical4DATA5plus7G/factoryends/MIC→BUS→XT60+balance→battery zachowane. Brak zakupu, zasilania, druku, slicera, fizycznego odbioru lub wholecatGO.
