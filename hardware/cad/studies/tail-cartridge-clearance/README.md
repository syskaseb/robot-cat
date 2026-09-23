# Adapter ogona R4 — przegrody i montaż górnego bloku

23.09.2026. **Osobne studium PETG, NIE zamontowane i NIE zatwierdzone do druku.**
[Model](TailCartridgeClearance.FCStd), [widok od spodu bez dolnej płytki](underside-clearance.png).
[Pokrywa z dostępem serwisowym](TailBearingLidService.FCStd), [widok pokrywy](lid-service-ports.png).
Pochodna [R3](../tail-cartridge-integrated/README.md), bez nadpisania poprzednika
ani dziewięciu głównych dokumentów kota. Dziedziczone nazwy cech i etykiety
części pochodzą z R3; rewizję studium określają ten dokument i manifest R4.

Wynik: wszystkie opisane nominalne próby geometryczne zaliczone; **61 testów
narzędzi CAD**. Adapter: 13 kątów, 13 wysokości nasuwania i 73 pozycje nakrętki.
Skręcony blok: cztery etapy / 56 pozycji. Składanie na stole: siedem etapów /
91 pozycji. Obwiednie Ø6 nad śrubami i pod nakrętkami bez kolizji w tych stanach;
kontrole ze starą pokrywą i przesuniętym łożyskiem wykrywają przeszkody.
Natywny solver sprawdzono dla 9 Fixed adaptera, nie dla nowej integracji całego
napędu. Te wyniki nie zastępują fizycznego montażu ani zatwierdzenia PETG.

## Zmiana mechaniczna

Zmniejszono promień czterech dolnych słupków z 3,1 do **2,6 mm**, a ich gniazd
z 3,3 do **2,8 mm**. Dzięki temu przegroda między gniazdem i długim ramieniem
orczyka ma **1,4 zamiast 0,9 mm**, bez przesuwania śrub. Luz promieniowy
słupek–gniazdo pozostaje 0,2 mm (nominalny, nie zmierzony na wydruku).

Nowy `BossInterface` wiąże wszystkie osiem promieni szkiców: `BossRadius=2.6`
i `RadialClearance=0.2`. Parametry i powiązania utworzono przez FreeCAD MCP.
Pozostałe wymiary R3, kieszenie łbów, czop, kanał M3 i wysokości montażowe
pozostają niezmienione. Dwa wydruki PETG i cztery nominalne komplety M2×10
z nakrętkami nadal tworzą rozbieralny adapter.

Zysk ma cenę: przekrój pierścieniowy każdego słupka nad płytą maleje
z około 25,67 do **16,71 mm²**. Nominalny łeb o promieniu 2,1 mm nadal
ma całe oparcie poza otworem R1,2, około **9,33 mm²** na śrubę. Nie wolno
z tego wyciągać wniosku o dopuszczalnym momencie dokręcania ani nośności PETG.
Ścianka słupka wokół otworu ma nominalnie 1,4 mm; przegroda przy krótkim
ramieniu 1,575 mm. To lokalne wartości, nie globalny audyt grubości całej nasady.
Małe krawędzie/lipy kanału, pionowy czop, kierunki warstw, podpory, docisk
i pełzanie nadal wymagają oceny w slicerze oraz prób fizycznych.

## Geometria i połączenia

[Audyt R4](audit.json) wiąże sumami SHA model, poprzednik i narzędzie.
Sprawdza dwa pojedyncze solids w ścisłym BOP, 22 w pełni związane szkice,
otwarcie z innego katalogu oraz niezależną różnicę pierścieni względem R3.
Mierzy wszystkie cztery przegrody i oparcia łbów. Zmiany `HoleRadius`
oraz `BossRadius` mają kontrolowany wpływ na obie części i są dokładnie cofane.

Zachowane 9 natywnych Fixed / 10 fizycznych części przechodzi test kolejnego
przesunięcia i obrotu każdego nieuziemionego członu z odtworzeniem przez solver.
Orczyk nadal stanowi niepołączoną referencję bez otworu wieloklinu — nie jest
to natywny test napędu ogona. 13 kątów ±30°, 13 wysokości nasuwania,
73 pozycje nakrętki i obwiednie narzędzi powtarzają zakres kontroli R3.
Odrzucony krótki kanał R3 pozostaje kontrolą dodatnią, nie podstawą zaliczenia.

## Pokrywa i kolejność montażu górnego bloku

Próba wykazała pułapkę: gniazda nakrętek pokrywy są otwarte od spodu bloku,
więc nakrętki trzeba przytrzymać podczas skręcania poza robotem. Przykręcona
stara pokrywa blokuje natomiast dostęp od góry do śrub mocujących blok.
Stary raport samej drogi części zachowano w
[archiwum kolejności](superseded-open-lid-sequence/housing-installation.json);
nie dowodził dostępu narzędzia ani przytrzymania nakrętek.

W osobnej kopii edytowalnej pokrywy dodano szkic dwóch okręgów R3,3 i kieszeń
5 mm na osiach X153 / Y−10,0. Na krawędzi tworzą się otwarte wybrania Ø6,6,
przez które można nominalnie włożyć śruby i trzpień narzędzia Ø6. Wspólny
`LidServiceParameters.AccessRadius` steruje obydwoma. Zachowano istniejące
otwory pokrywy, podparcia śrub i położenie części; usunięto tylko zamierzone
wybrania. To zmiana istniejącego wydruku, nie dodanie czwartej części robota.
Zmienione są więc dwa wydruki adaptera i jedna pokrywa; nie zintegrowano ich
jeszcze w głównym złożeniu. Dodatkowy ubytek osłabia krawędź i wymaga próby PETG.

Pokrywa ma jedną bryłę poprawną w ścisłym BOP, trzy związane szkice i historię
operacji. Audyt sprawdza niezależne odejmowanie walców od starej części,
otwarcie z nowego katalogu oraz zmianę promienia z przywróceniem geometrii.

[Osobny raport](housing-installation.json) bada tylko nominalną drogę części
przy nieruchomym adapterze R4. Nie zakłada, że brak kolizji w położeniu końcowym
wystarcza. Pozycje są próbkowane co 2 mm; nie jest to ciągła obwiednia.

Stan początkowy: adapter z referencyjnym orczykiem na serwie, nakrętka M3
czopa włożona bokiem, dwie nakrętki mocujące blok wcześniej umieszczone
w dolnym wsporniku. Górny blok, jego potomkowie oraz dalszy ogon są nieobecne;
wałek MG92B pozostaje na miejscu. Reszta geometrii bazowego kota jest przeszkodą.

1. Opuścić górny blok już skręcony na stole: dwa 608ZZ, oba dystanse,
   poprawiona pokrywa, dwie śruby i dwie nakrętki pokrywy: +32…0 mm.
2. Włożyć dwie śruby mocujące blok przez wybrania pokrywy: +20…0 mm.
3. Założyć pokrywkę czopa: +20…0 mm.
4. Włożyć śrubę osi M3: +32…0 mm.

Osobne cylindry Ø6 sprawdzają pionową przestrzeń nad łbami obu śrub mocujących
blok. Stara pokrywa pozostaje kontrolą dodatnią kolizji. Nie jest to dobór
konkretnego gniazda śruby, model rękojeści ani dowód rzeczywistego dokręcenia.

Każdy etap uwzględnia części już założone w poprzednich. Jeżeli etap zawodzi,
wyniki dalszych są wyłącznie hipotetyczne; raport nie może zaliczyć całej sekwencji.
Złożenie wstępne bloku na stole sprawdzono osobno poniżej. Rzeczywiste
pasowania łożysk, gwinty, końcówki narzędzi, dłonie i przewody nie są dowiedzione tym testem.
Nie montuje on też segmentów ogona ani nie domyka 29 TEMP całego robota.

### Składanie bloku na stole

[Dodatkowy raport](bearing-preassembly.json) sprawdza wstępne wkładanie części
do pustego `UpperHousing34`, bez przeszkód należących do reszty kota:
dolne łożysko, dystans wewnętrzny, dystans zewnętrzny, górne łożysko,
poprawiona pokrywa, jej śruby od góry, następnie nakrętki od spodu.
Siedem etapów po 13 wysokości co 2 mm: +24…0 mm, a nakrętki −24…0 mm.
Obwiednie Ø6 od spodu badają miejsce na przytrzymanie nakrętek. Jawnie wyłączone
są własna nakrętka i śruba wewnątrz obwiedni nasadki; rzeczywista geometria
nasadki, dopasowanie do sześciokąta i możliwość przeniesienia momentu nie są potwierdzone.
Kontrola dodatnia przesuwa dolne łożysko o 1 mm w bok i ma wykryć kolizję
z gniazdem. Używane są niezmienione moduły i opublikowane transformacje części,
bez tworzenia nowej geometrii czy zapisywania źródłowych dokumentów.

To test drogi nominalnej, nie siły wcisku, samoczynnego centrowania, stabilnego
utrzymania części przed przykręceniem pokrywy ani fizycznej próby montażu.

## PETG i dalsze bramki

Orientacje i warunki z R3 pozostają kandydatami: dolna płyta Z88 na stole,
nasada Z90 na stole z pionowym czopem. Poprawiona pokrywa: płaską podstawą
Z123,2 na stole, słupkami ku górze. Gabaryty mieszczą się w 256³ mm
z zapasem na brim; profil, dysza, warstwa i skuteczność podpór niepotwierdzone.
Próbki gniazd, test skręcenia i długotrwałego docisku są nadal wymagane.

Rzeczywisty orczyk/śruba/wieloklin, połączenie z serwem, górny blok i jego
nakrętki podczas wstępnego składania, termika oraz wiązka pozostają otwarte.
Badania Gazebo nie zostały zmienione. Błędy BOP starej skorupy nie zostały naprawione.

Źródło referencji orczyka i licencja pozostają jak w R1/R3: Alberto / otrebla333,
Dtto v2.0.1, CC BY-SA 4.0. Nie pobrano nowej obcej geometrii.

## Powtórzenie kontroli

Python FreeCAD 1.1.3 z korzenia repo, jedna ciężka próba naraz:

```text
python tools/cad/tail_cartridge_clearance.py audit
python tools/cad/tail_housing_installation.py
python tools/cad/tail_bearing_preassembly.py
python tools/cad/package_tail_cartridge_clearance.py
python -m unittest discover -s tools/cad -p "test_*.py"
python tools/cad/release_check.py hardware/releases/tail-cartridge-clearance.json
```

Audyt nie zapisuje CAD. `--require-print-ready` ma odmówić wydania do druku.
