# v33 — integralny pyszczek i mocowanie ReSpeaker

**Checkpoint rozwojowy, nie wydanie do druku.** Branch pozostaje
`codex/robot-cat-mechanical` w `syskaseb/robot-cat`. v32 zachowano bez zmian.

- [Kot_v33_GLOWA_MONTAZ.FCStd](Kot_v33_GLOWA_MONTAZ.FCStd): całe złożenie.
- [HeadDesign33.FCStd](HeadDesign33.FCStd): edytowalny master PartDesign.
- [Cały kot](whole-cat.png), [wnętrze przedniej części głowy](inside-head.png).
- [Więzy i test](assembly-validation.json), [kontrola geometrii](fit-audit.json),
  [zachowane części](inheritance-check.json), [Gazebo](../../simulation/v33/README.md).

## Zmiana konstrukcji

Przednia skorupa i pyszczek są **jedną ciągłą bryłą PETG**, z natywnym
Boolean Fuse w historii. Oddzielny komponent `Muzzle` i jego tymczasowy
Fixed usunięto. Wypukły kształt przodu zachowano; nos nadal jest odkręcany.
ToF/nos mają teraz rodzica `HeadFront`, pozostały stos śrubowy v32 bez zmian.
Od środka jest zaokrąglony otwór serwisowy 22×29 mm, R2, na głębokość 40 mm
od lokalnego Z=−5,6 w układzie ToF. Wycinany jest w skorupie PRZED połączeniem
z pyszczkiem. Nie zastępuje pełnego projektu wiązki.

ReSpeaker Lite zastąpił stare pudełko. Użyto nieprzeskalowanego
[STEP Seeed v1.1](../../reference/head-electronics-2026-09-22/README.md).
Płytka jest przesunięta o 5 mm do przodu względem wcześniejszego studium;
spód PCB na CAD Z=139,6 mm, obrót Rz=+90°. Jej dwa otwory Ø2,2 są po
przekątnej, nie w czterech narożnikach. Osie śrub w CAD:

- X=−133,158487; Y=19,19 mm;
- X=−162,078487; Y=−38,52 mm.

Podpory są integralne ze skorupą: belki 8×4 mm, słupki Ø5, otwory Ø2,4.
Dwa M2×12 są wkładane od spodu: łby pod PETG na Z132, nakrętki nad PCB
na Z141,11. Rozstaw wyliczany jest z transformacji otworów STEP, nie przepisywany.
Stos zacisku ma 9,11 mm, nominalna nakrętka 1,6 mm, wystaje 1,29 mm śruby.
Łby/nakrętki są uproszczonymi obwiedniami zakupowymi z v32; wymiary
rzeczywiste, moment dokręcania, pełzanie PETG i orientacja warstw wymagają próby.
Nie zaprojektowano podkładek ani nie dodano ich po cichu do zacisku.

**Ważne:** STEP ma laminat około 82×34 mm, wiki podaje 86×35 mm.
Mocowanie odpowiada konkretnie STEP v1.1; rewizję zakupionej płytki trzeba
potwierdzić przed drukiem. Pozostawiono szacunkowe 20 g masy modułu,
nie liczono całej elektroniki gęstością PETG. Nie zatwierdzono wtyków USB,
dodatkowego XIAO, kanałów mikrofonowych ani przewodów przez ruchomą szyję.

## Zakres kontroli

289 komponentów, 275 Fixed +13 Revolute; **30 mocowań nadal tymczasowych**.
Trzy szkice faktycznie w pełni związane. Master i kot to podpisane kopie,
nie live-link: po zmianie mastera trzeba odświeżyć złożenie i wszystkie raporty.
283 pozostałe komponenty zachowano; porównanie BRep dopuszcza tylko
zaokrąglenia zapisu 10⁻⁹ mm / względnie 10⁻¹², bez zmiany struktury.

`RobotConnectionTest33` ma 22 klatki: nogi ±3°, ogon ±30°. Nos, ToF,
mikrofony i ich śruby pozostają przy przedniej skorupie. **Głowa nadal jest
zablokowana** — ten test nie udaje dwóch gotowych osi jej napędu.

Audyt oddziela nowe podpory/elektronikę od odziedziczonych przenikań
wkładek, pierścieni oczu i szyi. Zlanie dwóch części nie jest dowodem
usunięcia pozostałych konfliktów; są nadal wymienione jako OPEN.
Kontrola narzędzi dotyczy przedniej części głowy zdjętej z kota, z odsłoniętym
tyłem. **Mikrofony trzeba skręcić przed założeniem lewego ucha (`EarL`)**,
które blokuje płaski klucz do nakrętki. Dolne dojścia do łbów są wolne.
Docelowe mocowanie ucha nadal jest tymczasowe, więc nie zatwierdzono serwisu
już złożonego kota. Rezerwy nie są modelem konkretnego zakupionego klucza.

## Wykryta i częściowo naprawiona wada starszej skorupy

Oryginalny przód v31/v32 zwracał `isValid()=True`, choć siatka miała 62
krawędzie non-manifold, a klasyfikacja wnętrza i przecięcia dawały błędne wyniki.
Pierwszy szkic v33 odziedziczył problem; miał też przesunięty o 5 mm drugi
otwór mikrofonów. Zachowano go z raportem błędów w [rejected-initial](rejected-initial/README.md).
Jego wcześniejsze 3 próby Gazebo nie są testami aktualnej geometrii.

[Odzyskanie topologii](recovery/README.md) oraz zmiana kolejności Pocket/Fuse
dają zamkniętą siatkę bez wadliwych krawędzi. [Niezależny audyt siatki](mesh-proof.json)
potwierdza puste rezerwy optyki, przewodów i dostępu do śrub nosa.
Nadal istnieją błędy BOP (samoprzecięcia przy wierzchołkach, krótkie krawędzie,
C0/krzywe na powierzchniach) oraz odziedziczone przenikania wkładek i szyi.
**To poprawiony checkpoint roboczy, nie pełna naprawa
wszystkich powierzchni i nie zatwierdzenie do druku.** Wcześniejsze raporty
kontaktu z tą skorupą nie są dowodem poprawności jej topologii.

## Widoki i odtwarzanie

`tools/freecad/skorupa/View33.FCMacro` przywraca cały widok kota bez zapisu
podpisanego pliku. W FreeCAD można włączyć płaszczyznę przekroju poleceniem
`Std_ToggleClipPlane` (menu Widok / płaszczyzny przycinania). Przycinanie
widoku nie wycina materiału. Można również ukryć `HeadRear` i ustawić
przezroczystość `HeadFront`; zdjęcie wnętrza pokazuje taki widok, nie nową część.

W Pythonie dostarczonym z FreeCAD: `cache33.py`, `audit33.py`,
`inheritance33.py` z `tools/freecad/skorupa/`. Cache BRep jest ignorowany
w Git i odtwarzany z podpisanego pliku. `Validate33.FCMacro` w GUI zapisuje
nowy wynik testu natywnego i zmienia podpis CAD — wtedy trzeba ponowić
także eksport/symulację. `Integrate33.FCMacro` odmawia nadpisania checkpointu.
`Refresh33.FCMacro` jest migracją wyłącznie podpisanego pierwszego szkicu;
odmawia ponownej podmiany innej wersji. Audyt siatki: `mesh_probe_export33.py`
w Pythonie FreeCAD, potem `tools/simulation/mesh_probe33.py` w środowisku
z trimesh5.1/manifold3d3.5. Żaden skrypt nie wypełnia otworów siatki na skróty.

Uwaga dla edycji mastera: ciała użyte przez PartDesign Boolean są zagnieżdżone
w układzie ciała wynikowego. Ich `Placement` jest lokalny, a położenie
w kocie daje `getGlobalPlacement()`. Dwukrotne nałożenie pozycji daje
kilka oddzielnych brył mimo statusu `Valid`; sprawdzamy także liczbę solids.
Ciężkie klasyfikacje/przecięcia uruchamiać poza wątkiem GUI FreeCAD.

## Nadal otwarte

Dwie osie głowy, orczyk i niezależne podparcie ogona, mocowania pozostałych
wkładek i elektroniki, odziedziczone kolizje, przewody/akustyka, serwis
akumulatora oraz próby tolerancji, obciążenia i temperatury PETG/serw.
Nie jest to komplet STL gotowy do produkcji. Pełna lista: [STATUS](../STATUS.md).
