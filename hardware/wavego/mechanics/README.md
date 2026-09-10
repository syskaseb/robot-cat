# WAVEGO CAT — roboczy prototyp mechaniki

Checkpoint na branchu `codex/wavego-component-layout`, 2026-09-09.
Model: [WAVEGO_cat_mechanical.FCStd](../WAVEGO_cat_mechanical.FCStd).
**Nie jest jeszcze gotowy do druku ani montażu.**

[Przekroje i warstwy elektroniki](SECTIONS.md) są dostępne w osobnym pliku
podglądowym i jako opisane zrzuty. Nie zmieniają modelu konstrukcyjnego.

## Zapisany zakres

Osiem nowych brył: podstawa/nadbudowa korpusu, pokrywa grzbietu,
skorupa głowy, wspornik szyi, maska pyska, wspornik ogona, ogon
i uchwyt kamery. Korpus ma zaokrąglone narożniki i łukowy grzbiet;
dalsze zmiękczenie sylwetki, szczególnie końcówek uszu i głowy,
pozostaje do wykonania zgodnie z uwagami użytkownika.

Materiał projektowy: PETG; nominalna grubość skorup 2,4 mm.
Kolory drukowanych części są propozycją grafitowo-kremową, nie numerem
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
- przecięcie dna nadbudowy z oboma oryginalnymi panelami bocznymi;
- kolizje z rezerwą tylnego rozłączenia przewodów i serwa obrotu głowy.

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
