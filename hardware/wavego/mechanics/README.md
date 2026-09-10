# WAVEGO CAT — roboczy prototyp mechaniki

Checkpoint na branchu `codex/wavego-component-layout`, 2026-09-10.
Model: [WAVEGO_cat_mechanical.FCStd](../WAVEGO_cat_mechanical.FCStd).
**Nie jest jeszcze gotowy do druku ani montażu.**

[Przekroje i warstwy elektroniki](SECTIONS.md) są dostępne w osobnym pliku
podglądowym i jako opisane zrzuty. Nie zmieniają modelu konstrukcyjnego.

## Zapisany zakres

Osiem nowych brył: podstawa/nadbudowa korpusu, pokrywa grzbietu,
skorupa głowy, wspornik szyi, maska pyska, wspornik ogona, ogon
i uchwyt kamery. Korpus ma zaokrąglone narożniki i łukowy grzbiet;
głowa ma teraz płynne profile uszu oraz wypukłą maskę z policzkami i małym
nosem, inspirowaną zdjęciem użytkownika. [Podgląd pyska](cute-face-detail.png).
To iteracja stylistyczna, nie dokładna kopia zdjęcia ani gotowy zestaw do druku.

Materiał projektowy: PETG; nominalna grubość skorup 2,4 mm.
Kolory drukowanych części są propozycją grafitową, nie numerem
konkretnego filamentu. W modelu są otwory montażowe, słupki i kieszenie
nakrętek; nominalne przeloty M3 mają Ø3,4 mm. Tolerancje druku,
długości śrub, wkładki/nakrętki i wytrzymałość wymagają weryfikacji.

Przód to **−X**, góra **+Z**. Oryginalne nogi i podwozie nie zostały
obrócone. Pliki źródłowe WAVEGO oraz ich kopie zapasowe pozostają osobne.
[components.json](components.json) opisuje rezerwy montażowe 26 komponentów,
nie dokładne modele kupnych części. Pozycje różnią się od wcześniejszego
[studium rozmieszczenia](../layout/README.md).

## Kontrola i otwarte problemy

[validation.json](validation.json) zapisuje kontrolę geometrii i osi
przelotów wykonaną skryptem
[wavego_mechanics_check.py](../../../tools/freecad/wavego_mechanics_check.py).
Osiem brył jest poprawnych geometrycznie i każda ma jeden solid;
126 elementów źródłowych zachowuje bazowe obrysy, objętości i liczbę brył.
Osiem grup prób przelotów śrub nie wykazuje zablokowanych osi.
To **nie jest test więzów złożenia**, gwintów ani przenoszenia obciążeń.

Raport nadal wykazuje:

- przecięcie głowy ze wspornikiem szyi oraz ogona ze wspornikiem;
- kolizje z rezerwą tylnego rozłączenia przewodów i serwa obrotu głowy.

Kolizję dna z panelami bocznymi usunięto lokalnymi podniesieniami dna,
bez zmiany oryginalnych paneli i osi ośmiu śrub podwozia. Cztery edytowalne
operacje `Panel_Raised_Floor_Left/Right` i `Panel_Clearance_Left/Right`
pozostawiają nominalny luz 0,5 mm nad panelami i dach kanałów o grubości
2,4 mm (Z=39,02–41,42 mm). Wyniki i 36 prób grubości są zapisane w
[panel-clearance-validation.json](panel-clearance-validation.json);
test odtwarza [wavego_panel_clearance_check.py](../../../tools/freecad/wavego_panel_clearance_check.py).
Nie jest to globalna analiza grubości ani potwierdzenie wytrzymałości PETG.
Stopki szyi i ogona mają dopasowane wybrania z luzem 0,2 mm nad
podniesieniami. Ich grubość zwiększono z 4 do 6,2 mm, aby po wybraniu
2,2 mm zostało 4 mm materiału. Przeloty na tych samych osiach M2,5 mają
Ø2,7 mm i przechodzą przez całe pogrubione stopki. Długości śrub należy
dobrać ponownie: grubość zaciskana na osiach zwiększyła się o 2,2 mm.
Rezerwę listwy zaciskowej podniesiono o 1,62 mm, a tylnych rozłączeń
o 2,62 mm (obie zaczynają się na Z=46,62 mm), zapewniając 1 mm nad
pogrubioną stopką ogona. To zmiana rzeczywistego rozmieszczenia rezerw,
nie rozsunięcie elementów tylko do ilustracji; mocowania modułów są nadal
do zaprojektowania.

## Zaokrąglony pysk

Zachowano pierwotny promień 18 mm obrysu montażowego głowy i maski:
zwiększenie go do 35 mm kolidowało z podłogą uchwytu kamery. Zaokrąglony
wygląd zapewnia dodatkowa wypukła skorupa, bez przesuwania tej elektroniki.
Maska pozostaje jedną częścią z czterema przelotami Ø3,4 mm na istniejących
osiach Y=±47 mm, Z=166/194 mm. Zachowano tylną płaszczyznę mocowania,
głowę i maskę można rozdzielić. Nowe czoło powstało z czterech natywnych
szkiców elips, operacji Loft i Thickness 2,4 mm, połączonych natywnym
PartDesign Boolean z maską. `FelineFaceDome` jest ukrytym operandem tej
operacji, nie oddzielną częścią do wydrukowania. Jego Placement musi być
lokalnie zerowy, bo dziedziczy układ współrzędnych maski.

Policzki i nos mają własne szkice i operacje Loft. Uszy mają zamknięte
profile B-spline zamiast prostych trójkątów; wcześniejszy końcowy fillet R3
zastąpiono zaokrągleniem wynikającym bezpośrednio z profilu.
[cute-face-validation.json](cute-face-validation.json) sprawdza spójność
brył, osie śrub, brak przecięcia maski z głową i otwarte środki trzech
portów optycznych. To nie jest sprawdzenie całego pola widzenia:
szczególnie wystający pysk wymaga testu kamery i ToF z wybranymi modułami.
Nie dodano fikcyjnych soczewek ani złotych dekoracyjnych elementów bez
mocowań. Masa, podpory i dostęp narzędziowy pozostają do sprawdzenia.

Nie ukończono więzów nowych części w złożeniu FreeCAD, mocowań wszystkich
modułów, napędów głowy/ogona, prowadzenia przewodów ani analizy cieplnej
i obciążeń. Głowa i ogon są prototypem nieruchomym. Pole `joints` w raporcie
opisuje wyłącznie próby osi otworów, nie istniejące obiekty Assembly Joint.
`gait_phases: 0` oznacza, że nowej mechaniki nie sprawdzono jeszcze w ruchu;
pusta lista `gait_hits` nie jest potwierdzeniem braku kolizji w chodzie.

Nie przenosić wyników 25 faz ruchu wcześniejszego studium obwiedni na tę
nową geometrię. Makro ruchu zachowuje oddzielną nazwę pliku prototypu,
ale nie dodaje brakujących połączeń ani nie certyfikuje jego ruchu.

## Ponowienie kontroli

Zatrzymać animację i przywrócić neutralną pozycję, otworzyć kopię
`WAVEGO_cat_mechanical.FCStd`, następnie załadować skrypt w interpreterze
FreeCAD z ustawionym `__file__` i wywołać `check(doc, gait=False)`.
Opcjonalne `gait=True` bada 25 dyskretnych faz dotychczasowego chodu nóg,
nie ciągły ruch, dynamikę ani nowe napędy. `presentation(doc)` ustawia
widoczność i kolory prezentacyjne. Każdy zapis dotyczy wyłącznie roboczej
kopii, nie zaakceptowanego modelu źródłowego.
