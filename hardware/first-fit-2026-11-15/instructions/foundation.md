# START HERE — WAVEGO: pierwsza przymiarka podstawy BEZ ZASILANIA

**Bieżący zestaw:** tylko ten katalog `fit-kit-ready`, model `fit-assembly.FCStd`, 8 różnych STL/13 sztuk. Poprzednie katalogi `foundation-fit-kit` i `fit-kit-final` zachowują dowody HOLD; nie są alternatywnymi instrukcjami montażu. To warunkowe zwolnienie do przymiarki podstawy, nie gotowy zasilony kot ani odbiór całej ramy elektroniki.

## 1. Najpierw jedna mała próba

**P00: 214×55×1,2 mm, 1 szt.** Przyłożyć do posiadanej bazy bez przerabiania metalu. Osiem otworów pochodzi z zachowanego źródła WAVEGO. Potwierdzić rewizję, osie, faktyczny gwint i długość chwytu. Ø2,05 w modelu nie dowodzi gwintu M2.5. Jeżeli nie pasuje — zatrzymać montaż; nie wiercić i nie gwintować ramy.

Po zgodnej przymiarce podstawy: P01×2, P02×1, P03×1, P04×2. Tył: P05×4, P06×1, P07×1. Szczegóły ilości i rozmiary są w `print-parts.csv`; wyłącznie te druki są eksportowane, bez przewodów/śrub/kupnych modułów.

## 2. Co rzeczywiście zamknięto w CAD

Wszystkie cztery pełne nakrętki i podkładki mają ciągłą drogę załadunku do miejsca pracy. Dwa wejścia są od wolnego bokuY−: początekY−87 poza krawędzią−82. Dwa są od spodu: (99,15) i (164,27). Nowy portØ9 przy(99,15) dochodzi doZ46,52; nad nim pozostaje rzeczywisty2mmweb do48,52. Nie wystarczyło samo wolne końcowe gniazdo. Zweryfikowano pełne pola ruchu, poprawne bryły i zerowe przenikanie; stary wynik13,550718mm³ pozostaje w zamrożonym pakiecie.

Cztery **M3×50**, boss**1mm**, pełna nakrętka2,4mm/podkładka0,5mm. Cały stos48,9mm, koniec1,1mm za nakrętką; poprzednio odebrany odstęp całej śruby do rzeczywistej pokrywy min4mm i oparcia podkładek29,931524mm² zachowano bez zmian. Nie ciąć śrub. Stare identyfikatory wewnętrzne `H03_panel_M3x55_*` oznaczają teraz nominalne **M3×50** — właściwy opis i BOM są tutaj.

P06 jest jedną rzeczywistą częścią: panelS0 + tylny mostek + dwa zamknięte gniazda wspólnej półki. Zastępuje funkcję starej NIEZBUDOWANEJ `Upper_frame_end_105`; nie ma dwóch nakładających się belek. Odebrano zachowanie8zamierzonych składników/zakresu, dwa oparcia szyn52,8mm², dwa oparcia słupków9mm², ciągłe wsunięcie końców10mm i brak przenikania osobnych druków. Końce przyszłych szyn6×1,5mm zachowują przekrój9mm² dawnego3×3; gniazdo ma nominalnie.15boki/.2dach/.2koniec. Są to referencje przyszłej ramy, nie dodatkowe eksporty produkcyjne.

Nowy materiał szyny jest2,5mm od AUX. Na zachowanym odcinku starej niewydrukowanej szyny jest1,0mm — **otwarte pasowanie makiety elektroniki**, bez waiver1,25 i bez odbioru kompletnej górnej ramy. To ograniczenie nie znika przez nazwę wspólnej podpory. Nie obciążać niezakończonej półki elektroniką bez jej rzeczywistej przymiarki.

Szeroki dawny prostokąt `Rear_aux_open` nie był bryłą przewodów:1725mm³ z panelem zachowano jako wynik rezerwy, nie fizyczny kontakt. Przy panelu wykazano ciągłe boczne okno ręcznego układania25×19,75mm, X130..155/Y20,25..40/Z80..100, z rzeczywistymi sąsiadami. Pełne wtyki, odciążenia, długości i promienie nadal sprawdzane na stole wFIT2 — wolne okno nie dowodzi całej wiązki.

## 3. Kolejność dla dwóch osób

1. A przykłada P00 i sprawdza rzeczywiste mocowania; B porównuje komplet z listą i utrzymuje baterię odłączoną. Dopiero zgodne osie/gwint pozwalają przejść do podstawy.
2. **Na stole, przed osadzeniem P03 na bazie:** B wkłada pełne nakrętki z podkładkami przez cztery opisane wejścia; A prowadzi je do gniazd i sprawdza antyobrót. Nie liczyć na włożenie przez sam otwór śruby. Kieszenie mają podparcie/ścianki; zachować pełne podkładki.
3. Ułożyć dwie listwyP01 i połówkiP02/P03, połączyć dwiemaP04. Osiem nominalnych M2.5 tylko po potwierdzeniu gwintu/chwytu; najpierw lekko, bez wymuszania. M3splices/nakrętki i narzędzie przed elektroniką/baterią. Kupna rama pozostaje cała.
4. Ustawić czteryP05 i P06 na rzeczywistych płaszczyznach. S0ma zachowane11części, a dwa otworyM6/rozstaw38 to tylko nominalna rodzina do przymiarki — nie dowód dostarczonego mocowania. Dopasować bez wiercenia obudowy. CzteryM3×50 z pełnym stosem; potwierdzić brak naprężenia i dostęp klucza przed wiązkami. Sam CAD nie ustala momentu dokręcania/nośności PETG.
5. Referencyjny montaż wspólnej półki: wsunąć dwa luźne końce szyn w P06, zanim zamknie się ich przednie połączenie i założy PCB. Nie odrywać wirtualnie integralnego druku. Półka/AUX/Pi/BUS pozostają próbą regulowaną; nie drukować sztywnego produkcyjnego mocowania według starej makiety.
6. P07na rzeczywistym tylnym padzie, cztery nominalneM3×20. To otwarty korzeń do przymiarki, nie odebrany napęd ogona. Wszystkie kupne części/pozy nóg i źródłowe osie pozostają.
7. Otwarta próba końców na stole według grafu: **16WAGO415 =4DATA/5plus/7masa**. Mapa1:1 wCSV, bez zmiany połączeń. Cztery niezależne220 i oba końce/MTA zachować osobno; moduły lutowane nie są rozpinane. KrótkieFHAC, pełnyUSB500+Delock, K1474 i chłodzeniePi/BUS sprawdzić na prawdziwych częściach. Łączniki/stock NIEPOTWIERDZONE; brak zakupu/cięcia/podłączania zasilania.
8. Ręcznie przeprowadzić pełny zakres nóg z odłączonym zasilaniem i sprawdzić masę/luz/pinch. Bateria/paski i kosmetyczne osłony na końcu. Skorupa i napędy głowy/ogona nie są zwolnione tym zestawem.

## 4. Druk i trzy nazwane FIT

Wszystkie STL wmm, dodatnimXYZ iZ0, zamknięte/dodatnie, każdywymiar<256mm. Duża płaska dolna powierzchnia na stole, bez skalowania. Propozycja PETG: warstwa0,2mm/4obrysy/5góra-dół/35%wypełnienia; to nie zatwierdzony profil ani test wytrzymałości. Dachy kanałów/mały mostek gniazda6,3mm i szczeliny wymagają próbki pasowania; podpory tak, by dało się je wyjąć. Nie wykonano slicingu ani druku.

- **FIT1:** P00, rzeczywista rewizja/gwint/osiem mocowań, masa i ręczny ruch12napędów. Żadnej kwalifikacji udźwigu z pola kontaktu.
- **FIT2:** prawdziwe końce/fabryczne długości/odciążenia, ochrona iS0M6, USB/Delock, cztery220, chłodzeniePi/BUS oraz wspólna makieta logiki/AUX1mm. Bez skracania/łączenia wirtualnie, bez uznania1mm za spełnienie1,25. Aktualne długości/cięcia/luz nieudowodnione pozostająNULL.
- **FIT3:** kartonowy cały obrys Oli z portami/pełnym panelem doX177, głowa/ogon/łożyska i realne proporcje/masa. Nie finalna skorupa ani mechanizm produkcyjny.

Źródła i odebrane granice w `manifest.json`. Pozostałe6STL są bajtowo takie same jak zamrożone źródło; P06identyczny z ostatnim pakietemHOLD, zmieniono tylko P03port. Żadnego starego globalnego exact126/nowej recenzji/nowej rodziny układu. Brak fizycznegoPASS, zakupu, zasilania i druku.
