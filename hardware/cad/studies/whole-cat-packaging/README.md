# Cały kot: checkpoint 1, propozycja układu

06.10.2026. Model do oceny proporcji i przestrzeni, **nie zestaw do druku**.
Wybrany pakiet nadal R53; faza 1 nadal 14/20 = 70%. Ten checkpoint nie zamyka
W1/W5 ani nie zatwierdza montażu, zakresu ruchu czy pasowań fizycznych.

## Co otworzyć

- `WholeCatLayout.FCStd`: samodzielny dokument FreeCAD, bez zewnętrznych linków.
- `feline-overview.png`: bok, przód, góra i widok wnętrza bez objętości tułowia.
  To projekcje rzeczywistej geometrii CAD, nie wygenerowany obraz wyglądu.
- `layout.json`: przesunięcia, wymiary, zakres kontroli i ograniczenia.
- `checks.json`: sprawdzone źródła, zgodność uszu E6, położenia odniesień,
  ponowne otwarcie i działanie czterech parametrów przesunięcia.
- `inventory.json` i `reference-shapes.zip`: źródła i zapisane bryły odniesienia.

191 odniesień w modelu nie oznacza 191 nowych części ani wydruków. To wybrana
część istniejącego złożenia oraz rezerwacje kupnych modułów. Zachowano geometrię
i położenia nóg/ram P0, aktualny front głowy i uszy E6. Źródła są przypięte
sumami kontrolnymi. Późniejsze części kasety i podpory W1/W5 pozostają kandydatami,
nie są nowym wyborem produkcyjnym. Drobne części napędów oraz drukowane orczyki
głowy i ogona wymagają uzgodnienia z wybranym pakietem w kolejnym etapie.

## Propozycja proporcji, mm

Pierwszy pudełkowy obrys356×304×234 został odrzucony przez użytkownika jako
owczy i zbyt szeroki przy nogach. Poniższy model go zastępuje. Kocie proporcje
mają pierwszeństwo; nie zwiększać obrysu, by zachować dawną kasetę.

| Element | Propozycja |
|---|---|
| Rezerwacja tułowia | 325 długości × 200 szerokości × 160 wysokości |
| Tułów w układzie P0 | X −120..205, Y −100..100, Z −2..158 |
| Cała głowa | 42 do przodu (−X), 25 do góry (+Z) |
| Cały ogon i jego mostek | bez przesunięcia X, 15 do góry (+Z) |
| Nogi i osie bioder P0 | bez zmiany |

To wymiary obrysu, nie grubość gotowej skorupy. Tułów jest pełną objętością
planistyczną; przecięcia z wewnętrznymi częściami nie są testem kolizji ścianki.
Należy zaprojektować właściwe ściany, przejścia nóg i dostępy. Bryła szyi tylko
pokazuje kierunek przyszłego podparcia i nie jest gotowym mocowaniem.

Parametry `HeadForward/HeadRaise/TailRearward/TailRaise` mają działające
wyrażenia sterujące odniesieniami. Przekroje tułowia są natywnymi szkicami
o ustalonych współrzędnych, edytowanymi w szkicach; `BodyHalfWidth/BodyFloor/
BodyRoof/WallReservation` dokumentują propozycję, nie sterują wszystkimi szkicami.

## Co zmieniamy dalej, a czego nie udajemy

1. Stara kaseta też nie mieści się w nowym obrysie: np. Cover dochodzi do
   Z219,5, a banki do Y±142. To jawne zadanie CP2: wspólne przełożenie modułów
   i nowych podpór, nie gotowe wnętrze ukryte pod skorupą. Zachowujemy kupne
   części i funkcje; geometria ich starych mocowań nie jest narzucona.
   Cztery podpory wiązki FL/FR/RL/RR dochodzą do Y około ±164 oraz X −196..238.
   Nie mieszczą się w tej propozycji obudowy. Ich dotychczasowy układ trzeba
   zastąpić wspólnie z wyjściami kabli, nie powiększać tułowia po każdym kontakcie.
2. Fork głowy ma zewnętrzne podparcie złącza sięgające Y134. Po przesunięciu
   głowy nie staje się automatycznie poprawnym prowadzeniem przewodów szyi.
3. Nowe podparcie szyi i podniesiony mostek ogona wymagają drogi obciążenia,
   śrub i przestrzeni ruchu; stare mocowania nie są zakwalifikowane po translacji.
4. Kaseta, Pi, bateria i przewody wymagają wspólnego uzgodnienia, dostępu
   od zmontowanego robota i jednej wykonalnej kolejności montażu/demontażu.
   Rezerwacja Pi ma poprawiony ślad85×56 i istniejący datum; wysokość22 pozostaje
   założeniem projektowym, nie kontrolą kompletnej płytki ze złączami.
5. Płyta baterii jest strukturą mocującą. Dawnej osobnej osłony brzucha nie
   kopiowano do tej propozycji: potrzebę dodatkowej osłony rozstrzygniemy po
   projekcie dolnej ścianki, dostępu baterii i prześwitu, bez dublowania funkcji.

Nie przeprowadzono pełnej kontroli kolizji ani obwiedni ruchu. Czerwone części
na podglądzie wnętrza oznaczają wymienione kandydaty do przeprojektowania,
nie automatycznie udowodnione kolizje. Obwiednie pochodzą z próbek tessellacji
i nie stanowią dowodu ciągłego prześwitu. Błędy odziedziczonych brył pozostają
błędami, a nie zaliczeniem całego modelu.

## Następny krok

Ocena proporcji przez użytkownika. Potem CP2: jeden wspólny układ kasety,
przewodów, podpór i serwisu; dopiero następnie szczegółowa skorupa i mocowania.
Nie wracać do wcześniejszych mikroprzesunięć starych podpór. Wymiary pełnego
tułowia przekraczają256mm; późniejsza skorupa będzie dzielona. Slicer i próby
druku należą do fazy2, ROS do fazy3. Hook pozostaje wyłączony.

Odtworzenie: `tools/cad/whole_cat_packaging.py` w Pythonie FreeCAD. Domyślne
wywołanie zbiera źródła, `--build` zapisuje model (odmawia nadpisania istniejącego
  FCStd), `--render` tworzy projekcje, `--verify` sprawdza checkpoint.
`--refine-proportions` aktualizuje wyłącznie tę niewybraną propozycję po ocenie
użytkownika. Przed odtworzeniem zachować checkpoint;
nie uruchamiać zbierania źródeł dla samego oglądania gotowego modelu.
