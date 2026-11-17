# Wspólne mocowania wykonane nominalnie; wiązka głowy nadal HOLD

Aktualny model: `front-rear-assembly-completion.FCStd`. To rzeczywista geometria wspólnego odbiornika Pi i tylnej podpory zasilania, **nie przyjęty cały robot ani gotowy zestaw przewodowy**.

Pi pozostaje stałe. Pełne porty skierowano do dostępnej zewnętrznej zatoki korpusu, bez skalowania lub odpinania części. Cztery śruby M2,5×12 z dwiema pełnymi podkładkami i nakrętką każda przechodzą przez otwory rzeczywistej bryły PCB Ø2,75/pitch58×49. Dystans3mm i otwarta ramka3mm są rzeczywistym drukiem połączonym z rusztem. Dawne współrzędne w nazwach śrub są aliasami — bieżące pozycje wynikają z cylindrów PCB. Pełny stos ma10,6mm pod łbem i1,4mm końca za nakrętką. Bezpieczne pola na dostarczonej PCB wymagają jednej przymiarki, nie są udowodnione uproszczoną kopertą komponentów.

Tylny ruszt, kołyska F0/POST i **stały** korzeń ogona są teraz naprawdę jednym drukiem. Przed połączeniem istniało745,572mm³ wspólnego użytecznego materiału; po integracji nie ma dwóch przenikających się druków. Serwo, łożyska, pokrywy i część obrotowa pozostają oddzielne. Kanał F0 zachowuje7mm środnika i dolne oparcie. Otwarte okna pod FHAC/GPIO i obniżenie górnej powierzchni szyn pod baterią są jawną zmianą funkcjonalną otwartego rusztu, nie skasowaniem ochronnej podłogi ani części kupnych. Główne szyny/kotwy P01 i podział złącza rusztu pozostają.

350 bieżących relacji nie wykazało nowego obcego konfliktu. Dziewięć próbek głowy nie stanowi dowodu ciągłego ruchu. Dodatnie objętości w gniazdach F0/POST35,44/40mm³ nie zostały uznane za OWN: wykonano rzeczywiste wybrania. Aktualnie common=0 na obu nominalnych powierzchniach odbiorczych. Uproszczone koperty nie potwierdzają bezpiecznego docisku dostarczonego plastiku. POST ma wykonane oparcie, ale niezależny keeper pozostaje niewykonany; pełna pętla/zamek/stock opasek F0 także wymaga kwalifikacji.

## Zasadniczy wynik przewodowy

Jedna ciągła recepta łuków R13,5 zachowuje projektowe minimum R12,5 dla pełnego profilu FFC16,8×1,8. Długość środka z końcami10mm raz wynosi182,256..226,208mm w dziewięciu pozycjach. **Ta recepta odpada dla jednostki200mm przed uwzględnieniem skręcenia i użytecznego nadmiaru**. To nie minimum wszystkich tras ani dowód niedoboru zakupionego przewodu. Nie pożyczono innego kabla i nie obniżono R/zakresu/końców. FFC, ToF4×OD2,1/R31,5 i JR nadal wymagają realnego połączonego prowadzenia i rezerwy ruchowej. Nie oznaczono ich jako „tylko pomiar fizyczny”.

## Dwie osoby — kolejność początkowa

1. Najpierw próbka P00 i pusta baza; pełne śruby/nakrętki rusztu przed bankami.
2. Jedna osoba trzyma Pi i pełne nakrętki, druga dokręca od otwartej strony korpusu. Pi przed dwoma inline FL i późnymi pokrywami; E1 pozostaje całym lutowanym zespołem.
3. Stały kartridż ogona/serwo/łożyska i realne pokrywy zamontować na integralnym korzeniu przed F0/S0/bankami. Nie odpinać wirtualnie integralnego druku.
4. F0/POST: najpierw przymiarka właściwych obudów i wybranych opasek przez rzeczywiste szczeliny, potem całe końce fabryczne. Opaski mają chwytać plastik, nie przewody. Kwalifikacja zamka/stock i keepera POST jest OPEN.
5. Wszystkie wiązki i późniejsze pokrywy dopiero po domknięciu wskazanych problemów. To nie instrukcja uruchomienia/zasilania.

**Jedyny STL**: `Pi-primary49-fit-coupon.stl`, 1szt,12×56×6mm, lokalne Z0, płasko płytą do stołu, słupki w górę; z4mm brimu każdą stroną20×64×6mm<256. Zamkniętą siatkę odczytano ponownie z dysku. MEASURE_ONLY: sprawdza pitch49, słupki, pełny stos i bezpieczne pola kontaktu. Nie drukować całego robota z tego pakietu. Główne części przekazano w native i BRep, bez STL-release.

Obejrzane whole-front/side/three-quarter i wnętrze pokazują te same części; obwiednia Oli pozostaje wcześniejszą nieprodukcyjną propozycją, bez kosmetycznego awansu. `local-Pi-primary-support-and-fullsteel.png` jest jawnie izolowanym widokiem mocowania. Starsze tabele w tym folderze są rawcheckpointami, nie alternatywnymi wersjami do montażu. Autorytatywne: `current-disposition.json`, końcowe350relacji i końcowe conforming-completion. Cztery MTA0100335 nadal wymagane/UNBOUND; ich pełne końce nie otrzymały kredytu z błędnych pudełek. Actual fit/cut/slack=NULL; wholekit=false/physicalPASS=false. FIRST/runtime/currentassembly nieedytowane.
