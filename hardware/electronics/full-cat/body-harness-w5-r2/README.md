# Bieżąca karta wykonawcza wiązki P0 — R45

R45 zachowuje wszystkie 71 zadań wydruku i 115 pozycji ilościowych R44.
`wire-cuts.csv` zawiera 80 fizycznych przewodów, nie wiersze grafu elektrycznego.
Dziesięć ma wybrane nominalne blanki; pozostałe są jawnie puste. To pokrycie
tej karty, nie licznik całej fazy ani pominięcie osobnych kart głowy i kasetki.
Rzeczywiste cięcie dopiero po beznapięciowej przymiarce w fazie 2.

Aktualne blanki: W007/W011/W012 po 200 mm; W061 240 mm; W060 220 mm;
W043 40 mm; W077 80 mm; W078 210 mm. W079/W080 to jeden kabel Pi
z rezerwą 290,249 mm na każdą żyłę. K-1474 pozostaje jednym przewodem
1000 mm: czerwonego zostaje nominalnie 499,751 mm, czarnego 489,751 mm.
Nie sumować równoległych żył jako zakupionej długości kabla.

Jedna próba pełnych dwunastu wejść oprawek z 24 zakończeniami została
odrzucona: 81 przecięć w 293 porównaniach oraz blanki 190/190/200 mm
na każdą nogę. Przy tej NIEwybranej trasie potrzeba 2320 mm LAPP na
wejścia; z historyczną rezerwą minusa 150 mm przekraczałoby to 2 m
o 470 mm. Nie zwiększono zamówienia ani nie wybrano tych długości.
To nie dowód, że każda możliwa trasa musi być tak długa.

Nasunięcie e=0 i osie końcówek ±7 mm to jawne parametry prototypu,
nie pomiary ani katalogowa geometria MTA. Należy zaprojektować krótszy,
wykonalny interfejs oprawek i odciążenia, zamiast ponawiać tę drogę przez
tackę Pi/podpory lub traktować dawny limit 100 mm jako gotowe cięcie.

W5/K3/E3 i cała faza 1 pozostają otwarte. Bez fizycznego PASS, zakupów,
zasilania, slicera i zmian ROS. Szczegółowe źródła i hash są w kartach JSON.
