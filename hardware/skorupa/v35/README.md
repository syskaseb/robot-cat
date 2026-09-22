# v35 — rzeczywiste mocowanie zasilania AUX

**Prototyp rozwojowy, nie wydanie do druku ani zatwierdzenie elektryczne.**
Branch `codex/robot-cat-mechanical`, repo `syskaseb/robot-cat`. v34 zachowane.

`AuxPower35.FCStd` zawiera edytowalną historię PartDesign utworzoną przez MCP
FreeCAD. Docelowe złożenie: `Kot_v35_ZASILANIE_AUX.FCStd`. Kopie geometrii
w złożeniu nie są live-link; zmiana mastera wymaga ponownego audytu i eksportu.

## Wynik sprawdzeń CAD

320 części, **306 Fixed +13 Revolute**,29 blokad nadal tymczasowych.
Natywny solver zakończył22 klatki testu nóg ±3° i ogona ±30° bez otwarcia
złączy, po czym przywrócił i zapisał spoczynek. Głowa nie była napędzana.
302 części v34 zachowano;18 kopii nowych/zmienionych sprawdzono z masterem
(największa różnica numeryczna poniżej1e−14, tolerancja bezwzględna1e−9).

Master ma11 w pełni związanych szkiców i9 Bodies, z czego dwa to jawnie
odrzucone studia, a siedem jest użytych w złożeniu: trzy zmodyfikowane
podpory/skorupy i cztery nowe słupki. 51 par spoczynkowych bez nowych
przecięć ponad0,01 mm³;11 próbek nasuwania płytki na zdjętym podzespole
bez przecięć. Nie jest to ciągła analiza całej drogi montażu ani pełnych
zakresów wszystkich przegubów.

639 testów ROS/CAD/narzędzi dla v35 zaliczono w Dockerze. Przed integracją
zaliczono też632 testy wcześniejszego v34; trzy ostrzeżenia dotyczą deprecacji
protobuf, nie geometrii. Bilans nominalny v35 to2,503128 kg, warianty
2,220387–2,967567 kg, wzrost1,390 g względem v34. Wyniki fizyki są osobno
w [Gazebo v35](../../simulation/v35/README.md).

**Pełny audyt BOP nadal nie przechodzi.** Stara skorupa ma błędy krawędzi
i powierzchni; test globalnej różnicy jej siatek również nie osiągnął
limitu. Ograniczoną integrację prototypu oparto na osobnych sprawdzeniach
prześwitów, ubytku materiału i podpór, bez uznawania tych błędów za naprawione.

## Mechanika

Druga Pololu D24V90F5 (2866) zastępuje starą obwiednię AUX. To wcześniej
udokumentowany [kandydat](../../reference/component-selection-2026-09-22/README.md),
nie nowy, zamówiony zakup ani potwierdzenie zapotrzebowania wszystkich serw.
Oryginalny STEP płytki jest kopią tej samej geometrii, która została użyta
w v31. Zaciski to nominalne obwiednie według rysunku Pololu 2440, nie model
ich wnętrza, gwintów lub lutowia.

PCB ma bazę **[89,2; −24; 52] mm**, bez obrotu, rozmiar 40,64×20,32 mm
i grubość 1,5748 mm. Otwory narożne Ø2,1844 mają raster 35,56×15,24 mm.
W PETG przeloty M2 są **Ø2,4 mm** według skillu FreeCAD `fastener-hole`.

| Osie śrub [mm] | Podpora | Dystans PETG nad podporą |
|---|---|---:|
| X91,74; Y−21,46 / −6,22 | płyta ramy Z38,52 | 13,48 mm |
| X127,30; Y−21,46 / −6,22 | mostek ogona Z44 | 8 mm |

Cztery słupki Ø6 — **cztery nowe wydruki PETG**. Przedni `Post35_1` ma
od spodu podcięcie R7,7 o głębokości1,2 mm, omijające stary krążek
`Part__Feature106`: X98,7,Y0,R7,5,Z38,52–39,52. Luz nominalny0,2 mm.
Podcięcie przy montażu skierować ku temu krążkowi. Nie jest niezależnym
zabezpieczeniem obrotu — słupek utrzymuje docisk śruby.

Dwa krótkie `Gap35_3` i `Gap35_001` w masterze są **ukrytymi, odrzuconymi
studiami**. Nie ma ich w złożeniu, masie ani liczbie wydruków. Nowe tylne
śruby ściskają PCB i mostek, nie szczelinę pomiędzy mostkiem a płytą ramy.

Pierwsza pozycja PCB [85,5; −24; 52] kolidowała z `TailFrameBolt29_2`
i podporą mostka. `probe35.py` zachowuje ten odrzucony wariant diagnostyczny.
Przesunięcie o3,7 mm w X usuwa ten konflikt. Kolejna próba z długimi tylnymi
śrubami do płyty ramy kolidowała z `FrameRear20`; zachowano ją w `rejected/`
z raportem. Ostatecznie tylne śruby idą od spodu samego mostka, a jego
dotychczasowe śruby przenoszą obciążenie dalej do ramy. Nie przesuwano
istniejącej głównej przetwornicy ani elektroniki.

Modyfikacje istniejących części: dwa otwory w płycie ramy, dwa w mostku,
przepusty Ø6,8 w skorupie (dwie z czterech osi szkicu faktycznie trafiają
w materiał). Ostatnia część pochodzi ze starego modelu i ma
**odziedziczone błędy BOP** — patrz zakres dowodów poniżej.

Przednie dwa M2×19 od góry: łby nad Z53,5748, nakrętki pod płytą
Z35,42–37,02. Stos16,5548 mm + nakrętka1,6 mm → wystawanie0,8452 mm.
Tylne dwa M2×19 **od dołu mostka**: łby Z39–41, nakrętki nad PCB
Z53,5748–55,1748. Stos12,5748 mm + nakrętka1,6 mm → wystawanie4,8252 mm
do Z60. W szczelinie pod mostkiem jest nominalnie0,48 mm pod łbem;
nie zaciska się w niej żadnej drukowanej podpory.
Nominalna obwiednia łba Ø4,2×2 mm, nakrętki Ø4,8×1,6 (uproszczona),
bez gwintu i gniazda narzędzia. **Podkładek nie ma w tym stosie**; dodanie
ich wymaga zmiany długości lub ponownego przeliczenia. Moment dokręcania,
naprężenia PCB i wytrzymałość cienkiej płyty nie są zatwierdzone.

## Montaż i serwis

Podzespół składać na **zdjętej płycie ramy**, przed elementami położonymi
nad regulatorami. Najpierw włożyć dwie tylne śruby M2 od spodu mostka,
**przed przykręceniem mostka do ramy**. Potem dotychczasowe śruby mostka,
cztery słupki, płytkę z wcześniej wlutowanymi zaciskami nasunąć na dwa
wystające trzpienie, dodać przednie śruby i nakrętki.
Nakrętki nie są uwięzione w gniazdach — wymagają przytrzymania narzędziem.
Raport zachowuje blokady prostych dojść w kompletnym kocie; nie jest to
deklaracja wymiany regulatora bez demontażu. Okrągła nasadka przy tylnych
nakrętkach może zahaczać o zacisk; właściwy klucz/wąskie szczypce wymagają
przymiarki. Nie oznaczamy tego jako zatwierdzonego dostępu dowolnym narzędziem.

Po obu końcach regulatora badane są lokalne rezerwy przewodów 12×10×6 mm.
Nie są pełną wiązką ani potwierdzeniem promienia gięcia, przekroju przewodu,
odciążenia lub wpiętej końcówki. Piny zacisków są na rastrze 5 mm i trafiają
w otwory zasilania, a nie otwory montażowe.

## Zakres dowodów

- `fit-audit.json`: dokładne przecięcia, kontakty i dojścia oraz **surowy
  wynik BOP**. Pełne `geometric_checks_passed` pozostaje fałszywe, jeżeli
  stara skorupa nie jest BOP-clean — tego wyniku nie przemianowujemy na sukces.
- `shell-source-bop.json`: osobny odczyt błędów skorupy z podpisanego v34.
- `mesh-proof.json`: niezależne sprawdzenie siatek i prześwitów, bez łatania
  otworów lub naprawiania siatki. Nie zastępuje poprawnego BRep.
- `mesh-proof-coarse.json`: zachowana wcześniejsza siatka diagnostyczna;
  jej próba różnicowa nie spełniła limitu, więc nie służy do zatwierdzania.
- Globalna różnica siatek skorupy ma osobny wynik, oddzielony od lokalnych
  prześwitów. Próba gęstego remeshu całej starej skorupy0,005 mm została
  zatrzymana z powodu kosztu czasu/pamięci; nie deklarujemy jej ukończenia.
  Dla skorupy wymagamy ponadto osobnego różnicowania BRep. Dla płaskiej
  płyty ramy OCCT zwrócił niemożliwą objętość różnicy współpłaszczyznowych
  brył: zachowano ten wynik, a zmianę sprawdzamy niezależnym Manifold
  i analityczną objętością dwóch otworów, nie fałszywym zerem z OCCT.
- `prototype-scope.json`: wyłącznie decyzja o włączeniu podzespołu do
  **prototypu**. Zgodność klas błędów nie dowodzi identycznych lokalizacji
  błędów; nie jest naprawą skorupy ani pozwoleniem na produkcję.
- `assembly-validation.json`: natywny test utrzymania złączy FreeCAD.
- `inheritance-check.json`: zachowane części v34 i kopie nowej geometrii.

Głowa, orczyk ogona, termika, fizyczne pasowania PETG, pozostała elektronika
i wiązka pozostają otwarte. Widok/animacja nie są testem rzeczywistego montażu.

## Zakupy i termika

Dodatkowo względem v34: **4×M2×19 i 4 nakrętki M2** oraz druga Pololu
w miejsce dawnej niesprecyzowanej przetwornicy AUX. Dwa zaciski są dostarczane
z regulatorem według [Pololu](https://www.pololu.com/product/2866).
Wymaga to lutowania. Wyjść obu regulatorów **nie łączyć równolegle**.

[NSZ-00637 w Botland](https://botland.com.pl/srubki-i-nakretki/637-zestaw-srubek-podkladek-i-nakretek-330szt-5410329304478.html)
odczytany 22.09.2026: dostępny, wysyłka24 h,12,90 zł; zawiera20 M2×19
i40 nakrętek M2. To deklaracja wysyłki, nie gwarancja daty doręczenia.
Uwaga ilościowa: częściowy bilans wszystkich dotychczasowych nowych mocowań
zawiera już **22×M2×12, 8×M2×19 i 30 nakrętek M2**. Jeden ten zestaw ma
tylko20 M2×12, więc od zera potrzeba co najmniej dwóch zestawów albo dwóch
dodatkowych M2×12 z innego źródła. To nadal nie BOM całego kota; M3×16
i M3×30 podpory ogona mają osobne oferty opisane w v34.
[Oferta regulatora](https://botland.com.pl/przetwornice-step-down/2580-d24v90f5-przetwornica-step-down-5v-9a-pololu-2866-5904422372118.html)
przy dwóch nowych odczytach miała timeout. Zachowany wcześniejszy odczyt
tego dnia (17 szt.,149 zł,24 h) **nie jest ponownym potwierdzeniem stanu**.
Niczego nie zamówiono; przed zakupem sprawdzić dostępność ponownie.

Nazwa handlowa „9 A” nie gwarantuje9 A w zamkniętej skorupie. Producent
uzależnia prąd od warunków cieplnych i ostrzega przed bardzo gorącą płytką.
Odstęp od PETG nie jest testem temperatury ani odporności na pełzanie.
Zabezpieczenia, bilans prądu szczytowego/rozruchowego i chłodzenie nadal OPEN.

## Odtwarzanie

Python FreeCAD: `cache34.py`, `mesh35.py`, `shell_scope35.py --baseline`,
`audit35.py`. `mesh35.py --check` wymaga środowiska z trimesh/manifold.
Następnie `shell_scope35.py` ocenia ograniczony zakres prototypu. Audyt BOP
zwraca błąd przy starej skorupie; zachować raport, nie pomijać pozostałych testów.

`Integrate35.FCMacro` importuje podpisanego mastera do nowej kopii v34
i odmawia nadpisania istniejącego checkpointu. `Validate35.FCMacro` sprawdza
złącza, przywraca spoczynek, zapisuje i podpisuje raport/cache. `cache35.py`
odtwarza cache bez modyfikacji pliku CAD; `inheritance35.py` porównuje geometrię.
`View35.FCMacro` przywraca widok całego kota bez zapisywania CAD.

## Oglądanie wnętrza

[Cały kot](whole-cat.png) · [zbliżenie mocowania AUX](aux-mount.png).

Otwórz `Kot_v35_ZASILANIE_AUX.FCStd`. Makro `ViewAux35.FCMacro` ukrywa
osłony i pozostałe podzespoły, zostawiając płytę, mostek ogona i mocowanie
AUX. To widok montażowy przez zmianę widoczności, **nie geometryczny przekrój**.
Powrót: `View35.FCMacro`. Makra nie zapisują pliku, więc nie zmieniają
podpisanego checkpointu.

W Assembly można wybrać `RobotConnectionTest35` w grupie symulacji i
uruchomić odtwarzanie. Jest to test kinematyczny nóg ±3° i ogona ±30°;
głowa pozostaje zablokowana. Nie stanowi testu pełnych zakresów ruchu,
kolizji, obciążenia silników ani fizycznego połączenia orczyka.
