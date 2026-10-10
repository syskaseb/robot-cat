# Bieżące mocowania płytek CP2, M5

Jeden aktualny zestaw nominalny, nie fizyczny PASS. CurrentBoardMounts.FCStd
zawiera natywne edytowalne podpory oraz referencje kupnych płytek. Aktualna
dolna płyta jest tą samą fizyczną częścią co w M3; górna odpowiada DataShelf.
Nie drukować równolegle starych LowerCarrierIntegrated/UpperCarrierRetention.
Zestaw:20wydruków/8geometrii,27śrub. Margines5mm na stronę do256³.

Montaż bez źródła zasilania:

1. Goła rama P0 i szyja/MAIN zgodnie z M2. Główne elementy pozostają na
   worldZ46,52; nie przenosić ich przez kopiowanie starego mastera.
2. Nakrętki Pi/BUS wprowadzić od dołu płyty. Założyć cztery dolne szczęki
   i górne podkładki zacisków, potem dolną płytę i4M3x14/8podkładek/4nuts.
   Bez wiercenia ramy; docisk i pełzanie PETG wymagają próby fazy2.
3. Pi/BUS osadzić na istniejących17łącznie osiach płytek, dolne8M2x12.
   Monitor i jego dwie opaski są już w M3, nie dodawać drugiego kompletu.
4. Górne płytki PWM9685/AUX4092/PWM1608 montować na stole,9M2x14.
   Zachować dwie płaskie drukowane podkładki izolacyjne PWM1608, zamiast
   metalowej podkładki na miedzi. Solder/populację sprawdzić po dostawie.
5. U1: najpierw rzeczywisty pomiar otworów, obu stron padów i grubości.
   Dopasować parametry lokalnego wymiennego uchwytu PRZED jego drukiem.
   Dwie dolne podpory, dwa górne izolatory i2M2x10; bez ściskania padów,
   bez wiercenia płytki i bez wymyślania zewnętrznego pinoutu.
6. Górną płytę osadzić na4dystansach32mm,4M3x45/8podkładkach/4nuts.
   Tylne nakrętki obsłużyć zachowanym bocznym dojściem klucza AF5,5,
   przed złączami i przewodami. U1 musi być gotowe przed modułem MTA nad nim.
7. Dalsze MTA/bank/wiązka należą do osobnego aktualnego wyboru. Do pełnego
   wyjęcia U1 najpierw zdjąć MTA nad nim; przy demontażu dolnych płytek
   najpierw górną płytę. Brak obietnicy niezależnego serwisu z wiązką.

To M5 mocowań płytek, nie E1/E2/W1/W5 ani globalne K2/K3. Historyczne
pozycje WAGO/source są ukryte i niewybrane. Klej nie jest odciążeniem żył.
Stałe kryterium M5 pochodzi z R31/README: komplet mocowania Pi/tacki/
zacisków i dostęp po zdjęciu BUS; przewody Pi pozostawiono W5. Bieżący
zestaw odtwarza tę całą funkcję CP2 i mocowania płytek współdzielonych.
Nie rozszerzać M5 do całej wiązki ani nie uznawać tego za wybór podpór WAGO.
Katalogowe osie Pi/BUS/PWM/AUX zachowane, U1 jawnie prowizoryczne.
Wykorzystano przypięte dawne dowody, sprawdzając tylko dodany materiał
aktualnych płyt i zachowane powierzchnie podparcia17otworów. Nie powtarzać
odrzuconego pionowego klucza do dwóch tylnych nakrętek. Rzeczywisty klucz,
PETG, izolacja, moment i obciążenia to jawne bramki fazy2.
