# WAVEGO — zestaw płyty do pierwszej przymiarki

**Odbiór cyfrowy dotyczy nowego fundamentu. Nie jest to gotowy do zasilenia kot ani finał skorupy.** Poprzednie 16 plików pozostaje bez zmian; jedynym bieżącym modelem tej korekty jest `foundation-assembly.FCStd`. Zawiera cały układ jako odniesienie, a tylko grupę PRINT_PARTS eksportowano do STL.


**BIEŻĄCA BLOKADA — NIE MONTOWAĆ TYLNEGO MOCOWANIA JAK NA RYSUNKU.** Lokalny pełny test nominalnej śruby `H03_panel_M3x55_1` i rzeczywistej pokrywy źródłowej WAVEGO dał gap≈0 mm (common0), zamiast1,25 mm. Nie jest to stwierdzenie kontaktu dostarczonych części, lecz obalenie narysowanego stosu55 mm. Rysunek śrub i ich lista służą śledzeniu tej wersji, nie są zatwierdzonym doborem do tylnego montażu. Drugi jawny interfejs: panel S0 dzieli310,075352 mm³ ze STARYM NIEZBUDOWANYM projektem tylnej belki półki elektroniki. To zależność druków do integracji, nie kolizja kupnych modułów ani zgoda na usunięcie belki z nazwy.

W tej porcji odzyskano **identyczne osiem STL — każdy SHA zgodny z kopią sprzed restartu**. Nie zmieniono kształtów, nie próbowano kolejnej rodziny. Gotowy użyteczny pierwszy krok to wzornikP00 i przymiarka głównego fundamentuP01–P04 po potwierdzeniu ośmiu rzeczywistych mocowań. P05–P07 pozostają geometrią do przymiarki, bez odbioru obciążonego tylnego zespołu, aż do rozstrzygnięcia powyższych interfejsów. 19 rzeczywistych płaskich powierzchni oparcia jest dodatnich (minimum27,447014 mm²); to dowód materiałowej drogi oparcia, nie pomiar wytrzymałości ani odbiór śrub.

## Co drukujemy

Najpierw **P00, jeden wzornik 214×55×1,2 mm**. Sprawdzić na posiadanej ramie osiem osi: X−80/−70/112/122, Y±22,5. Zapis źródłowy ma Ø2,6 w pokrywie i Ø2,05 w ramie, nie dowodzi gwintu. Jeśli wzornik/śruba nie pasują ręcznie, przerwać przymiarkę; nie wiercić ani gwintować kupnej ramy.

Po zgodności: P01 listwa **2 szt.**, P02 przód **1**, P03 tył z rzeczywistym tylnym węzłem **1**, P04 łącznik spodu **2**, P05 słupek40 mm **4**, P06 panel **1**, P07 otwarty korzeń ogona **1**. Łącznie 12 elementów nośnych i osobny wzornik; 8 unikalnych STL. Wymiary/orientacja i ilości są w `print-list.csv`. Każdy STL jest już ustawiony dodatnio i na Z=0, bez skalowania. PETG, proponowane 0,2 mm / 4 obrysy / 5 warstw góra-dół / 35% wypełnienia. Listwy i płyty płasko, słupki na boku; otwarty korzeń ogona podstawą w dół. Nie wykonano slicingu ani druku.

Tylny deck ma część pełnej szerokości do X177 oraz wąski język ogona do X198. Zintegrowane pogrubienie schodzi do Z41,52 i opiera się na stopniach obu listew. Cztery słupki mają powierzchnię oparcia na Z48,52; panel na Z88,52, zgodnie z rzeczywistą górą nominalnego korpusu S0. Stopa ogona siada na Z52,52. Nie ma dawnych przerw3/7 mm ani słupka poza podparciem. Słupek tylnego prawego naroża jest poza otwartym wspornikiem ogona; żadne dwa zamierzone osobne druki nie dzielą objętości. Te połączenia mają rzeczywiste śruby/nakrętki oraz sprawdzone powierzchnie styku — nie fuzję z kupną ramą i nie pusty opis.

## Kolejność i łączniki

1. Przymierzyć P00 i sprawdzić rzeczywisty typ/zaangażowanie gwintu. Osiem **M2.5×16 łeb stożkowy**, długość całkowita, to zapotrzebowanie nominalne do potwierdzenia, nie stwierdzenie zapasu ani typu fabrycznej śruby. W płytach są własne pogłębienia90° Ø5, z zachowaniem1,9 mm materiału pod łbem. Żadnej zmiany kupnej ramy.
2. Na stole połączyć połówki przez dwa P04: **4×M3×10, 4 nakrętki M3, 4 podkładki0,5 mm od spodu**. Założyć listwy i luźno przykręcić osiem źródłowych punktów, zanim WAGO, bateria lub S0 zasłonią łby. Właściwy gwint i długość potwierdzić bez wymuszania.
3. Korzeń ogona mocować **4×M3×20 +4 nakrętki +4 podkładki od spodu**. Dostęp od góry i boków pozostaje otwarty; to wspornik do przymiarki, bez gotowego sprzęgła/uchwytów serwa.
4. **NIE WYKONYWAĆ w tej wersji — nominalny stos H03 ma HOLD.** Pokazany panel na czterech P05 miał być mocowany **4×M3×55 +4 nakrętki +4 podkładki od spodu**. Dwa milimetry miejscowego pogrubienia pod łbami zapewniają nominalnie pełną nakrętkę. Klucz do nakrętek używać przed bankami/elektroniką; mały dostęp sprawdzić w otwartym montażu. S0 ma wyjmowany klucz w OFF według zachowanej notatki źródłowej: zdjąć go do nałożenia panelu, następnie przywrócić. To plan bez rzeczywistej operacji elektrycznej.
5. **Dwa otwory M6 w rozstawie38 mm są założeniem rodziny projektowej**, nie odebranym gwintem kupnej obudowy. M6×12 to tylko nominalna pozycja do potwierdzenia; nie jest wliczana jako zainstalowana geometria. Dopasować rzeczywisty korpus/neck i mocowanie przed obciążeniem S0. Nie wiercić jego obudowy. Osłona terminali i dwa odciążenia pozostają wymagane przed jakimkolwiek uruchomieniem.

Tylko wymienione łączniki są rozliczone w `used-fasteners.csv`; ich dostępność jest **NIEPOTWIERDZONA**, bez zakupu/nowej inwentaryzacji. Złącza i drobna elektronika nie są nowymi częściami tego wydruku.

## Rozdział przewodów i otwarty montaż

16 sztuk221-415 to **4DATA: D_FL/D_FR/D_RL/D_RR; 5plus: FL_P/FR_P/RL_P/RR_P/P_AUX; 7masa: FL_G/FR_G/RL_G/RR_G/G2/G_AUX/G_TAIL**. Dokładna mapa stacja–sieć–końce jest w CSV/JSON z bieżącego schematu; nie zmieniono ani jednego połączenia elektrycznego. Wewnętrzne dawne nazwy geometrii nie są rolami elektrycznymi. Miejsca oprawek są ustawne, bez16 dedykowanych kaset; odstęp3 mm nie jest dowodem wolnego miejsca na porty/zgięcia.

Przed utrwaleniem chwytów wykonać jeden otwarty bench-fit czterech NIEZALEŻNYCH220 mm z oboma fabrycznymi końcami, krótkich par FHAC≥84,5 mm oraz pełnego USB500 z wybranym Delockiem. Zachować izolację, odciążenia, rzeczywiste promienie i luz; brak cięcia, łączenia zapasów i zmyślonego PASS długości. Pi/BUS pozostaje próbną wspólną półką: rezerwa chłodzenia nakłada się nominalnie3,12 mm, więc nie drukować stałych dystansów przed rzeczywistą przymiarką. Papierowy/kartonowy obrys całego kota ma objąć także panel doX177 i język ogonaX198; dawneX170 nie jest gotową osłoną.

**Najbliższe trzy próby:** osiem mocowań + ręczny ruch nóg/masa; faktyczne końce/ochrona/S0; stos Pi/BUS i kartonowa sylwetka. Nie są pretekstem do pełnego audytu123 żył ani produkcyjnej obsługi serwisowej. Druk fundamentu i wzornik mogą poprzedzać dopracowanie pozostałej elektroniki. Zachowane źródła/negatywy pierwszego układu pozostają w nadrzędnym manifestcie.

Odzyskanie usługi: GUI19584 zakończony dopiero po kopii15źródeł/eksportów oraz10plików temp100,7MB; kod wyjścia nieznany. Jeden nowy GUI8920, bez równoległego CAD. Zapis native nastąpił przed testami. Globalnej dokładnej kontroli126brył nie powtórzono: liczbowy cull i jeden mały lokalny kandydat36ścian ujawniły H03HOLD. Wynik timeoutu nie jest negatywem geometrii.
