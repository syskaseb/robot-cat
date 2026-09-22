# v31 — główna przetwornica na rzeczywistych mocowaniach

**Checkpoint rozwojowy, nie wydanie do druku.** Dotyczy głównego Pololu
D24V90F5, nie proponowanej dodatkowej przetwornicy AUX. AUX ani zakupów
nie zmieniono. Poprzedni [v30](../v30/README.md) jest zachowany.

- [Kot_v31_ZASILANIE.FCStd](Kot_v31_ZASILANIE.FCStd): pełne złożenie.
- [PowerDesign31.FCStd](PowerDesign31.FCStd): edytowalny master PartDesign.
- [Zbliżenie mocowania](power-mount.png), [cały kot](whole-cat.png).
- [Plan połączeń](assembly-plan.json), [test natywny](assembly-validation.json),
  [dopasowanie i serwis](fit-audit.json), [dziedziczenie](inheritance-check.json).

Kształty w złożeniu są kopiami mastera, nie live-link. Zmiany mastera
wymagają odświeżenia złożenia oraz wszystkich raportów i prób.

## Co powstało

Stary prostopadłościan Pololu zastąpiono źródłowym STEP producenta
z zachowanego [pakietu referencyjnego](../../reference/component-selection-2026-09-22/README.md).
PCB ma 40,64×20,32 mm, grubość laminatu 1,5748 mm, najwyższe elementy
7,6748 mm nad spodem. Otwory narożne Ø2,1844, raster 35,56×15,24 mm.
Otworów zasilania o podobnej średnicy nie pomylono z montażowymi.

Nowa baza PCB w CAD: **[85,5; −2; 52] mm**, bez obrotu. Układ przesunięto
od wcześniejszej obwiedni, by uniknąć ramy, tacki Pi i mocowań ogona.
Pierwszy kandydat kolidował ze starym krążkiem `Part__Feature105`;
nie wycinano go ani nie przesuwano. Wstępny audyt nowej pozycji przeszedł.

| Osie M2 [mm] | Podpora | Dystans górny | Dystans pod mostkiem |
|---|---|---:|---:|
| X=88,04; Y=0,54 / 15,78 | płyta ramy Z=38,52 | 13,48 mm | nie dotyczy |
| X=123,60; Y=0,54 / 15,78 | mostek ogona Z=44 | 8,00 mm | 2,48 mm |

Wszystkie sześć dystansów: **PETG, Ø6, otwór Ø2,4 mm**. Krótkie dystanse
wypełniają przestrzeń od płyty Z=38,52 do spodu mostka Z=41: dokręcanie
nie ma ściskać pustej szczeliny ani odginać mostka. Płyta ma cztery otwory,
mostek dwa, skorupa cztery niezależne przepusty Ø6,8 mm.
Otwory wykonano natywnie według skillu `fastener-hole`, a nie samym
połączeniem Fixed lub pozornym zetknięciem brył.

Cztery **M2×19** przechodzą przez cały stos do nakrętek pod płytą.
Stos pod łbem 16,5548 + nakrętka 1,60 mm → wystawanie 0,8452 mm.
Podkładek nie uwzględniono; ich dodanie wymaga ponownego obliczenia.
Zestaw [Botland NSZ-00637](https://botland.com.pl/srubki-i-nakretki/637-zestaw-srubek-podkladek-i-nakretek-330szt-5410329304478.html)
zawiera 20 śrub M2×19. Dostępność 24 h sprawdzono wcześniej tej nocy;
ponowne pobranie strony przy v31 miało timeout, wyszukiwarka potwierdza
zawartość zestawu, lecz nie stan magazynu w chwili zakupu. Nic nie zamówiono.
Modele łbów/nakrętek to nominalne obwiednie; brak pomiaru rzeczywistego zestawu.

## Zaciski i przewody

STEP płytki nie zawiera zacisków. Dodano dwa uproszczone kupne modele
z obwiednią **7,6×10×10 mm**, dwoma pinami Ø1×4 na rastrze 5 mm,
według [rysunku Pololu 2440](https://www.pololu.com/product/2440).
Kopia rysunku: [pololu-terminal-drawing.png](pololu-terminal-drawing.png),
[oryginał](https://a.pololu-files.com/picture/0J3564.600.png).
To elementy dołączane do regulatora zgodnie z [opisem Pololu 2866](https://www.pololu.com/product/2866),
nie nowy zakup innego złącza. Drobnych wypustów łączenia, wnętrza zacisku,
śrub zaciskowych, gwintów i lutowia nie odwzorowano.

Kierunki wejścia przewodów: na zewnątrz obu końców PCB. Piny trafiają
w otwory zasilania, nie w otwory mocujące. Fixed do PCB reprezentuje
docelowe połączenie lutowane, nie automatyczne zalutowanie sprzętu.
Lutowanie, prąd, odciążenie przewodów i rzeczywista dostępność narzędzia
muszą być sprawdzone na egzemplarzu.

W masterze ukryto dwie rezerwy przewodów po 12×10×6 mm; nie są drukowane
ani liczone do masy. To lokalne rezerwy wyjścia, nie cały poprowadzony kabel.
Audyt raportuje też próbę pionowego dojścia śrubokrętem Ø4 na długości 30 mm.
Blokada przez obwiednię `PowerDistribution` oznacza potrzebę jej zdjęcia
przed obsługą zacisków — **nie pełną dostępność serwisową w gotowym robocie**.
Dokładna listwa rozdzielcza nadal wymaga decyzji, więc jej nie przestawiano.
Nakrętki zakładać przy zdjętej płycie; nie ustalono momentu dokręcania PCB/PETG.

## Zakres weryfikacji i pozostałe ryzyka

280 części, 266 Fixed i 13 Revolute; **34 blokady nadal tymczasowe**.
W tej rewizji `Fix_Pololu` ma już fizyczną drogę połączenia przez dystanse,
śruby i nakrętki. 16 nowych części: 6 PETG, 8 śrub/nakrętek, 2 zaciski.
Master ma dziewięć w pełni związanych szkiców. Zmieniono też trzy istniejące
elementy podporowe: płytę, skorupę i mostek; pozostałe 260 części porównano
z v30. Nie badano od nowa każdej dawnej pary ani ciągłego całego chodu.

Audyt v31: **63 pary, zero przecięć >0,01 mm³**; bez kolizji lokalnych rezerw
przewodów. Cztery kontakty dystans–podpora po 23,75 mm² i dystans–PCB
po 21,76 mm²; dwa dolne dystanse kontaktują płytę i mostek po 23,75 mm²
na każdym końcu. Osie śrub drożne, cztery piny zacisków nie przenikają PCB.
Dwa dojścia śrubokręta nad zaciskiem po stronie X=88,04 blokuje obwiednia
rozdziału zasilania; dwa po stronie X=123,6 są wolne w testowanej obwiedni.
To jawna kolejność serwisowa, nie przemilczana kolizja.

Porównanie 260 odziedziczonych BRep: 192 identyczne bajtowo, 68 z różnicami
wyłącznie zapisu liczb/białych znaków, maksymalnie 9,95×10⁻¹³.

Natywny `RobotConnectionTest31` sprawdza 22 klatki ±3° nóg i ±30° ogona,
utrzymanie złączy i nieruchomość IMU/Pololu względem korpusu. Po próbie
zapisano spoczynek. W FreeCAD: `RobotCatAssembly24 → Simulations`, otwórz
ten test, przelicz klatki i odtwórz. To nie sterowanie fizycznym robotem.

PETG: obwiednie mastera mieszczą się w 256³ mm; luzy wymagają próbki.
Regulator może być bardzo gorący. Odstęp geometryczny i kolor materiału
**nie potwierdzają bezpieczeństwa cieplnego PETG**, pełzania, wytrzymałości
cienkiej płyty ramy ani chłodzenia. Wydajność regulatora zależy od
chłodzenia/obciążenia; nie zatwierdzono zamkniętej instalacji „9 A”.

[Gazebo v31](../../simulation/v31/README.md) ma pełne nowe masy i siatki;
ogon/głowa są nadal zamrożone w tym eksperymencie. Głowa, orczyk/podparcie
ogona, pozostała elektronika, wiązki oraz serwis akumulatora pozostają otwarte.

## Odtwarzanie

W Pythonie FreeCAD: `cache30.py`, `cache31.py`, `audit31.py` z
`tools/freecad/skorupa/`; potem `inheritance31.py` (także zwykły Python).
Cache BRep jest ignorowany w Git. Audyt działa poza GUI, aby nie blokować
MCP rozbudowanymi booleanami źródłowej płytki.

`Integrate31.FCMacro` buduje nowy v31 z zapisanego mastera i v30; odmawia
nadpisania checkpointu. `Validate31.FCMacro` przelicza istniejący v31,
zapisuje pozycję spoczynkową, SHA, cache i raport. Po zmianie CAD ponowić
audyt i cały eksport/próby fizyki, nie używać starych podpisanych raportów.
