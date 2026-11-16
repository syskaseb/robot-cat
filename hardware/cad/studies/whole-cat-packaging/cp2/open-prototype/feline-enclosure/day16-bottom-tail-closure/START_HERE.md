# Dół korpusu i przejście ogona — jedna korekta16Nov

**HOLD — nowe obrzeże przecina rzeczywisty P05_spacer_instance3:14,4mm³, ważny common. Nie eksportować do druku. Nie wykonano drugiego wariantu. Dodatkowo common nie zwrócił dodatnich powierzchni styku z pokładem: oparcie/retencja obrzeża nie zostały przyjęte. To konieczna decyzja całego dolnego interfejsu przy zachowanych wszystkich słupkach, nie małe kolejne podcięcie.**

**Bieżący model: bottom-tail-closure.FCStd. Propozycja, bez STL i bez fizycznego PASS.** Zamrożony model4e567a69 pozostaje wejściem. Nie zastępuje to odebranego warunkowego pakietu przymiarkowego.

## Co zmieniono

Pierwotne dno rzeczywiście przecinało obie P01: po2634,444mm³ w przednich oraz1900,554mm³ w tylnych częściach. Środkową podłogą są teraz rzeczywiste P02/P03. Nowa, nieprzyjęta osłona ma proponowane ciągłe obrzeże z pionowym powrotem i górnym kołnierzem przeznaczonym do oparcia na pokładzie (kontakt nieudowodniony); kupnej ramy, szyn, pokładu i ich obciążeń nie przycinano. Płaski nadmiar dna nad pokładem został jawnie zastąpiony tą funkcją, nie usunięty jako „kolizja Own”. Cztery części korpusu pozostają oddzielne, po jednej poprawnej bryle. Konkretne styki i nowe szczeliny zapisano w closure-result.json i receiver-contact-and-local-delta.json; kontakt nie dowodzi wytrzymałości ani zamocowania pokrywy.

Otwór ogona: X174..246/Y−28..28/Z135..223, przecięty w OBU tylnych połówkach. Zachowano rzeczywisty ogon, MG92B,608,P07 i pełną stal. Neutralny ogon nie przecina już osłon. Podział otwiera przejście na linii rozdziału, więc nie wymaga przeciągania całego zakrzywionego ogona przez zamknięty otwór.

## Montaż — dwie osoby, bez pozornego odpinania

1. Rama z P01/P02/P03 i korzenie P07/P10/P11 pozostają całością. Nakrętki i narzędzia podstawy przed bankami; nowy podział P11 zachowuje odebraną kolejność root→MAIN/AUX→górna belka. Nie powtarzano tego dowodu.
2. Wiązki i całe końce fabryczne układane otwarcie. Dolne obrzeża są osłoną, nie nową podporą modułów ani prowadzeniem dociskającym przewód.
3. Tylne połówki osłony domykać jako prawdziwe części wokół pozostawionego ogona; nie wirtualnie rozcinać P07 ani odpinać lutowanych modułów. Przejście ma być otwarte podczas układania przewodu napędu. Mocowania pokryw i pełna kolejność domknięcia przy studniach S0/S1 pozostają następnym zadaniem — nie przyznano jeszcze kompletnego dowodu montażu osłon.
4. Do dostępu do retencji korzenia ogona zdjąć tylne osłony; rzeczywiste P07 i komplet śrub pozostają widoczne w modelu. Brak deklaracji szybkiego serwisu.

## Konkretny brak ruchowy

Rzeczywiste łożysko Tail608 wyznacza obecnie oś Z przez(185,0); historyczny URDF opisuje inną lokalną ośY i nie wiąże obecnego WAVEGO. Dla zachowanego kształtu ogona analityczny pełny przedział odchylenia wokół Z mieszczący się w wybranym otworze z1,25mm wynosi co najmniej±22,749°. To **pojemność geometryczna**, a nie zaakceptowany wymagany zakres ani zmiana sterowania. Wymagana oś/zakres, fabryczny róg, sprzęgło i pełne zatrzymanie osi nadal OPEN/FIT3. Nie wykonano siatki pozycji ani drugiej rodziny.

## Dalej

Domknąć wymagany mechaniczny zakres ogona przy realizacji ciągłego napędu głowy/ogona. Następny już uzgodniony zakres to wspólne retencje modułów i kompletne połączenia ramy, następnie korzeń głowy, potem rzeczywiste zamki i montaż osłon. Optyka/twarz, zakresy i długości kabli, chłodzenie, masa/ruch oraz wszystkie FIT1/2/3 pozostają jawne. wholekit_ready=false, physical_pass=false, actual_fit_cut_slack=null. Nie wykonano zakupów, cięć, zasilania, druku ani slicingu.
