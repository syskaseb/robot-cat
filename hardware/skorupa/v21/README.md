# v21 — pogrubione środkowe odcinki boków ramy PETG

**Prototyp dwóch części, nie komplet robota zatwierdzony do druku.**

Złożenie: [Kot_v21_BOKI_PETG.FCStd](Kot_v21_BOKI_PETG.FCStd).
Źródłowe v20 zachowano bez zmian. Nadal głowa −X, ogon +X.

## Zmiana

`SideLeft21` i `SideRight21` zastępują panele boczne v20. W środkowej
części ich pionowa ścianka i dwa skośne pasy mają **3 mm zamiast 1,5 mm**.
Materiał dodano do wnętrza, jako integralną część każdego wydruku — to nie
osobna nakładka do przyklejenia. Nie dochodzą nowe śruby.

- Pełna grubość: X od −50 do 92 mm, czyli 142 mm długości.
- Stopniowe przejścia: od −60 do −50 i od 92 do 102 mm.
- Odcinki końcowe po 25 mm pozostają niezmienione, razem z otworami.
- Górne i dolne płaszczyzny styku pozostają na swoich miejscach.
- Osie serw, łapy, elementy handlowe, mocowania skorupy v20 i tacka Pi
  nie zostały przesunięte ani przebudowane.
- Dodano około 10,02 cm³ PETG do każdego boku. Kolor produkcyjny: czarny.

To **częściowe wzmocnienie**, nie konwersja całej ramy na grubość 3 mm.
Płaskie kołnierze, końce paneli i dwie ramy poprzeczne nadal wymagają
oceny pod obciążeniem i dalszego opracowania.

## Sprawdzone

- Dwie poprawne, pojedyncze bryły o dodatniej objętości; również kontrola
  geometrii BOP po ponownym otwarciu pliku.
- Pomiar trzech przekrojów normalnych w środku każdego boku: 3,000 mm.
- Brak usunięcia materiału starego panelu; brak dodatków w chronionych
  strefach końcowych i poza płaszczyznami przylegania kołnierzy.
- Brak **nowych** statycznych kolizji dodanego materiału z widocznymi
  częściami złożenia. Najmniejszy sprawdzony odstęp w zestawie sąsiednich
  części: około 2,16 mm od osłony brzucha.
- Zachowane geometrie i położenia 239 obiektów źródłowych. Stare boki
  są ukryte, nie skasowane; pozostałe widoczności z v20 zachowano.
- Dwie zamknięte siatki STL bez krawędzi niemanifoldowych.
  Gabaryt wydruku: około **212 × 39,73 × 22,34 mm**, mieści się w 256³ mm,
  także z brimem 8 mm. Orientacja eksportu: obrót X o 90°, przesunięcie na stół.

Nie wykonano FEA, prób obciążenia, analizy pełzania PETG, próby ruchu nóg ani
fizycznego wydruku. Należy sprawdzić warstwy, podpory i pasowania w slicerze
oraz na prototypie. Samo podwojenie grubości nie jest deklaracją nośności.

## Ważna starsza wada: brzuch przecina podwozie

Audyt wykrył poniższe przecięcia już w **źródłowym v20**, przed dodaniem
wzmocnień. Nie zostały ukryte przez automatyczne wycięcie otworów w brzuchu:

| para z `BellyPod` | wspólna objętość, mm³ |
|---|---:|
| przednia rama `FrameFront20` | 2367,94 |
| tylna rama `FrameRear20` | 30,12 |
| lewy bok `SideLeft20` | 330,34 |
| prawy bok `SideRight20` | 330,34 |

**Nie drukuj tego złożenia jako gotowego kompletu do montażu.**
Osłona brzucha wymaga przeprojektowania wokół ram i ich mocowań.
Bez tego nie można po prostu pogrubić obu ram poprzecznych do wnętrza.
Pogrubienie na zewnątrz koliduje natomiast z orczykami/łącznikami łap
i nasadą ogona. Rozpoznanie jest zapisane w `candidate-audit.json` oraz
`local-candidate-audit.json`. To nie pełny audyt kolizji wszystkich par robota.

Kolejny etap: rozwiązać te styki, zachowując osie serw, zaprojektować połączenia
brzucha i ramy, następnie kontynuować uchwyty elektroniki i przewody.
Nadal obowiązuje wcześniejsza niezgodność liczby mikroserw głowy/ogona
(BOM 3, odziedziczony model 4) oraz brak potwierdzonego modelu/orczyka.

## Pliki i podgląd

`stl-prototype/` zawiera tylko dwa zmienione boki. To zamienniki odpowiednich
paneli v20, nie dodatki do nich. Reszty robota nie eksportowano ponownie.

- [Wzmocnienie — pomarańczowy oznacza dodany materiał](bok-v21-wzmocnienie.png).
- [Rzeczywisty przekrój CAD w środku boku](bok-v21-przekroj.png): szary to
  odziedziczony materiał, pomarańczowy to jego pogrubienie. Wydruk jest jedną bryłą.
- [Cały kot](kot-v21-zlozony.png) — również końcowy widok w FreeCADzie.

W złożeniu zaznacz `ShellMounted20` i naciśnij Spację, aby odsłonić wnętrze;
ponowne naciśnięcie przywraca pokrywę. To ukrycie pokrywy, nie przekrój.
`tools/freecad/skorupa/V21_Views.FCMacro` wykonuje takie samo przełączenie.
`Detail21.FCMacro` odtwarza pokazane obrazy detalu i przekroju na kopiach,
następnie przywraca widok całego kota bez zmiany geometrii złożenia.
`SideLeft21Added.brep` to pomocnicza bryła dodanego materiału dla tego podglądu,
**nie dodatkowa część do wydrukowania**. Pozwala uniknąć niestabilnego odejmowania
prawie pokrywających się powierzchni po ponownym wczytaniu importowanych brył.

Raporty: `validation.json`, `print-validation.json`, `saved-document-validation.json`.
Źródła: `probe21.py`, `probe21_local.py`, `build21.py`, `export21.py`,
`Apply21.FCMacro`, `verify21.py` w `tools/freecad/skorupa/`.
Skrypty geometrii uruchamiano Pythonem dostarczonym z FreeCAD; makra GUI przez MCP.
To generowany wariant BRep, nie pełna parametryczna przebudowa wszystkich części.
