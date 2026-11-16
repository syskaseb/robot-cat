# Dolny receiver i osłonięty ogon — jedna spójna korekta16Nov

**base-receiver-tail.FCStd: sześć rzeczywistych połączeń osłony z podstawą i przejście ogona±20°, lokalnie sprawdzone. Bez STL i bez fizycznego PASS całego kota.** Pakiety4e567/dd5/6c6a/4f9 pozostają zamrożone.

## Połączenie i ochrona

P02/P03 w NOWEJ drukowanej wersji mają sześć otwartych gniazd: X−70/70/145, Y±72, kontaktZ46,02; zachowany pokład do48,52 daje2,5mm użytecznej warstwy nad gniazdem. Osłony mają dopasowane zakładki2,4mm, oparcia132–135mm² i boczne prowadzenie przeciwobrotowe. Górna krawędź obrzeża omija WSZYSTKIE czteryP05 i całeH03; dno/pokład zamykają środek. Kupnej ramy/P01/osi nie cięto. Zachowany centralny rdzeń obciążenia obu pokładów ma0utraconego materiału; wszystkie6zmienionych druków pozostają pojedynczymi poprawnymi bryłami. Nie deklarujemy wytrzymałości ani dopasowania gwintu.

Sześć kompletnych M3x10 z łbem SZEŚCIOKĄTNYM AF5,5/k2, dwiema podkładkami i pełną nakrętką. Stare nowe zapotrzebowanie na sockethead zostało zastąpione; nie usunięto żadnego kupnego elementu. Łeb41,12..43,12; podkładka43,12..43,62; zakładka43,62..46,02; pokład46,02..48,52; podkładka48,52..49,02; nakrętka49,02..51,42; pełny koniec śruby53,12. Śruby i narzędzie są zapotrzebowaniem NIEPOTWIERDZONYM.

Prawdziwe integralne kieszenie utrzymują nakrętki przeciw obrotowi, mają otwarty podajnik nakrętki i pełnej podkładki. Stary prosty klucz od dołu kolidował z tylnymi napędami — surowy wynik zachowany. Dostęp odbywa się płaskim kluczem5,5mm/grubości2mm od ZEWNĘTRZNEGO BOKU, przez rzeczywiste dolne kanały, z zachowaniem zakładki2,4mm nad nimi. Nie zmieniono osi śrub ani napędów. Zadeklarowana obwiednia narzędzia±15° mieści się w32,4mm szerokości: nearjaw korzysta z otwartego gniazda, handle z dolnego portu; pełne narzędzie/stock należy przymierzyć fizycznie.

## Ogon i montaż przez dwie osoby

Przyjęta ośZ przez(185,0), początkowy ruch±20° jest odwracalną decyzją projektu, nie parametrem dostawcy/odziedziczonym URDF. Ciągły obszar powstał z sektora Minkowskiego rzeczywistego kształtu i osobnego lokalnego pola przy dolnym pierścieniu; nie z trzech pozycji ani wielkiego pustego pudełka. Dolna osłona/chute oddziela elektronikę od ogona; otwór pozostaje funkcjonalnym przejściem ruchowym. Actual±20/0 mają co najmniej1,5516mm. Róg/sprzęgło/osiowe zatrzymanie i realny przewód pozostająFIT3, nie są wymazane.

1. Na otwartej podstawie założyć NOWE P02/P03 i zachowane P01/P05/H03/P07. Przed bankami włożyć pełne podkładki/nakrętki od zewnątrz w otwarte kieszenie; rama pozostaje pozioma, druga osoba pomaga przy prezaładunku.
2. Ustawić realne połówki osłony zakładkami w gniazdach. Śruby wkładać od dołu i dokręcać OD BOKU. Nakrętki łapią własne kieszenie; nie wymaga to rozcinania belki, odpinania lutów ani demontażu nóg.
3. Całe MTA/TE/ATO, cztery niezależne E2/JPWM225(min220),4MTA0100335 i wybrane WAGO/ochrona pozostają. Wiązki ułożyć otwarcie przed ostatecznym zamknięciem. Retencje modułów są dalszym zadaniem, nie wynikają z zamocowanej ramy.
4. Tylne połówki oraz kołnierz są rzeczywiście rozdzielone wY10; można je zestawić wokół pozostawionego ogona, nie przeciągać go przez nierozbieralny pierścień. Do rogu/retencji zdjąć tylne połówki. Pełna kolejność domknięcia wszystkich pokryw i przewodów nadal wymaga dalszego montażu.

Budowniczy: najpierw przypięty model4e567 i jednorazowe build-interface.py na jego źródłach, potem realize-side-tool.py. Autorytatywny zapisFCStd zawiera stan końcowy; nie uruchamiać historycznych generatorów zbiorczo. Native i widoki są propozycją, nie gotowym robotem. wholekit_ready=false/physical_pass=false/fit-cut-slackNULL. Nie wykonano zakupów, zasilania, druku, slicingu ani ROS.
