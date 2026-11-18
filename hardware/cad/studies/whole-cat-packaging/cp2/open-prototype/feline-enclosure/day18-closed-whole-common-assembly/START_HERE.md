# Aktualne wspólne mocowania i połączenia osłon — wynik roboczy

**Nie jest to cały zamknięty kot ani zestaw do jego wydrukowania.** Model zawiera rzeczywisty wspólny nośnik kilku płytek, dwa połączenia czaszki z osią pitch, zdejmowany tył głowy i połączenia czterech osłon z sześcioma istniejącymi gniazdami podłogi. Źródło638 i wcześniejsze pakiety pozostały niezmienione.

Otwórz `closed-whole-common-assembly.FCStd`. Aktualne widoki to `CURRENT-whole-opaque-front.png`, `CURRENT-whole-opaque-side.png`, `CURRENT-whole-opaque-three-quarter.png` i `CURRENT-whole-interior.png`. Wczesne `WIP-*` są osobnym checkpointem; nie przedstawiają późniejszych połączeń. Pełne części kupne pozostają widoczne.

## Co można przymierzyć

`conditional-current-print-index.json` obejmuje TYLKO dwa małe pliki: aktualny nośnik optyki TRUE PITCH oraz zdejmowany docisk krawędzi E1. Obie siatki są zamknięte po ponownym otwarciu i mieszczą się w256 wraz z8mm rezerwy. To próby pustych interfejsów, bez zasilania; nie automatyczna zgoda na montaż całego robota. Nośnik pitch wymaga aktualnych dwóch połączeń z czaszką zamiast starego wewnętrznego mostka. Docisk E1 wymaga rzeczywistego bezpiecznego pola krawędzi płytki; projektowe pole całego modułu przecina lipę o12,5mm3, co NIE jest potwierdzeniem bezpiecznego docisku komponentów. Najpierw próbka faktycznie obsadzonego E1.

Pozostałe obecne osłony/nośniki NIE mają nowego dopuszczenia STL. Nie zastępuj ich starymi plikami po zgodności nazwy.

## Montaż dwóch osób

1. P00/osie/gwinty i źródłowa podłoga pozostają warunkiem bazowym. Wstępnie włóż pełne nakrętki/podkładki sześciu gniazd podłogi PRZED modułami.
2. Zamontuj wspólny nośnik na dwóch źródłowych bocznych korzeniach P02 i pełne cztery zestawy Pi. BUS mocuj przez pierwotne cztery otwory i pełne łby stożkowe; dopiero potem cały lutowany PCA–E1. E1 nie odłącza się wirtualnie. MAIN/AUX mają pięć pełnych M2x16, BNO/AMP własne pierwotne otwory i pełne zestawy.
3. Przed przewodami załóż przednią czaszkę na prawdziwą część pitch. Dwa M2x12 mają pełną nakrętkę/podkładki i tip0,2mm; rzeczywiste tolerancje muszą zachować pełne zazębienie. Wewnętrzną nakrętkę trzyma druga osoba. Fabryczny stos śruby rogu MG jest nietknięty.
4. Ułóż przewody ręcznie przy OTWARTYM wnętrzu; same zapisane krzywe/510mm planu ToF nie zatwierdzają nieistniejących jeszcze chwytów. Pełne końce i jednostki zachowaj. Dopiero po próbie możliwe jest autoryzowane przycięcie nieużytego PLASTIKOWEGO ogona opaski; nie FFC/JR/elektryki/tekstyliów.
5. Tył czaszki ma dwa rzeczywiste kluczowane połączenia M2x16 i otwory5,5mm na podkładkę/narzędzie. Dostęp do nakrętek od nadal otwartej szyi. Osłony korpusu korzystają z istniejących sześciu pełnych M3x10 HEX oraz rzeczywistych dolnych gniazd. **NIE wykonuj ostatecznego zamknięcia:** znane przenikanie tyłu głowy i osłon musi zostać konstrukcyjnie rozwiązane, podobnie szyja/ogon/spoiny osłon.

## Co pozostaje projektem, a co fizyczną próbą

`whole-result-disposition.json` rozdziela te sprawy. Najważniejszy rzeczywisty problem geometrii: tył głowy przenika przednie ściany już neutralnie194,55/199,84mm3. To nie jest nieznana tolerancja. Surowy wynik pozostaje w `current-head-neck-first-material-gate.json`.

ToF ma pełny plan: rzeczywiste JP3.2VCC /6GND /3SDA /4SCL, cztery oddzielne przewody HELU, plan510mm na rdzeń z końcami/stratą, Rinner>=31,5. Nie jest to Pololu600 ani nowy terminal. Chwyty i lokalne zajęcie pozostają do zbudowania/sprawdzenia. JR i POWER to jeszcze budżety robocze, nie zatwierdzone trasy. DATA500 jest policzone w całości194,626+253,374+52, lecz bez akceptacji nowej szyi/osłony. FFC200 zachowuje wcześniejsze końce/R/zakres; lokalny nowy korzeń ma3,577mm w dziewięciu skorelowanych próbkach, co nie certyfikuje całego ruchu i całej nowej skóry.

Nie zmierzono realnych cięć, dopasowania ani zamontowanego luzu. PhysicalPASS=false. Brak próbki4MTA0100335 nie blokuje niezależnych prac, ale nie daje wymiarów oprawki z innego produktu. Masa w JSON jest tylko modelem wybranych dziewięciu druków przy PETG1,27, z jawnym wzrostem masy sześciu ścian; nie masa całego kota ani udźwig.
