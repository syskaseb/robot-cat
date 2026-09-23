# Wymienny adapter orczyka — R1, 23.09.2026

**Koncepcja, niezainstalowana w robocie, niezatwierdzona do druku.**
Główne dziewięć dokumentów CAD pozostaje bez zmian. Nie zamknięto TEMP
sprzęgła ogona ani nie dodano wyników Gazebo / natywnego solvera.

[Model FreeCAD](TailHornCartridge.FCStd) · [Złożone części](cartridge-assembled.png)
· [Widok rozłożony](cartridge-exploded.png).

## Części i mocowanie

Trzy edytowalne Bodies: nowa dolna płytka PETG, górna obejma PETG i wariant
istniejącej nasady/czopa. Zachowano historię nasady; nowe szkice, Pad i Pocket
wykonano przez MCP FreeCAD. 17 szkiców ma pełne więzy. Uzupełniono rzeczywiste
braki więzów mimo mylącego komunikatu MCP „Fully constrained”; sprawdzono
`FullyConstrained` i wynik solvera szkicu. Korekta odwróconego podcięcia nasady
była konieczna, bo automatyczny kierunek Pocket przeciął niewłaściwy obszar.

Obejma ma kieszeń krzyżową na **fabryczny orczyk**, nie drukowany wieloklin.
Dolna płytka zatrzymuje ramię od spodu; ściany gniazda mają przenosić moment.
Cztery przelotowe M2×10 z nakrętkami łączą obie płytki z nasadą. Łby są
zagłębione w podwyższonych gniazdach dolnej płytki. To nominalna geometria
łączników, nie dokładny produkt dostawcy ani zweryfikowane połączenie gwintowe.
Główne łożyskowanie 608 i oś X=171, Y=−6 pozostają na miejscu.

| Interfejs | Nominalne wymiary CAD, mm |
| --- | --- |
| Obrys obejmy | dysk R13,5 + przedłużenie 8,2 × 32; wynikowy gabaryt 27 × 32,5 |
| Dolna płytka | Z88…90, cztery gniazda do Z92,2 |
| Górna obejma | Z90…94, kieszeń ramion do Z92,35 |
| Kieszeń długiego / krótkiego ramienia | 4,6 × 28,4 / 17,1 × 4,25 |
| Piasta / dostęp od góry | otwory Ø7,6 / Ø8 |
| Osie czterech M2 | X164,5/177,5, Y−12,5/+0,5; otwory Ø2,4 |
| Zagłębienie łba | Ø4,6, Z88…90,2; nominalny łeb zaczyna się na Z88,2 |
| Kołnierz nasady | R11,8 do Z98; spód podcięty do Z94 |
| Stos nad łbem | 2 + 1,8 + 4 + nakrętka 1,6 = 9,4; śruba 10, wystaje 0,6 |

Wspólny `CartridgeParameters.HoleRadius` steruje otworami wszystkich trzech
części. Próba 1,2 → 1,3 → 1,2 sprawdza ubytek materiału i powrót geometrii.
Pozostałe wymiary są edytowalne w szkicach; nie deklarujemy dowolnych zmian
grubości jako automatycznie bezpiecznych dla wszystkich styków.

## Referencja orczyka i licencja

Zastosowano [referencję Dtto](../../../reference/mg92b-horn-2026-09-23/README.md),
Alberto / otrebla333, Dtto v2.0.1, commit
`b4b97069888079e5726600969b8e0783bfe2514f`, CC BY-SA 4.0.
[Pełny tekst licencji](../../../reference/mg92b-horn-2026-09-23/LICENSE-Dtto.txt).
Zapisana w modelu beżowa bryła została jedynie obrócona/przesunięta; kolor
wyróżnia referencję, nie potwierdza jej materiału. Referencja i jej przekształcona
kopia zachowują CC BY-SA 4.0. Bez zmian części graficznych/modelu źródłowego
poza ustawieniem w układzie robota. Nie używano kodu proxy obcego dokumentu.

To uproszczony krzyż 28 × 16,7, ramiona grubości 1,95, **bez otworów, śruby
i wieloklinu**. Założono zgodność wysokości końca wałka z modelem Adafruit
(Z91). Nie jest to pomiar dostarczonego orczyka. Kieszenie mają luz, nie zacisk
bezluzowy; kontrola względnego obrotu pokazuje geometryczny luz tej referencji,
nie rzeczywisty luz serwa. Nie trzeba zgadywać rozstawu otworów ramienia,
ale rzeczywisty obrys, wysokość osadzenia i śruba nadal muszą być potwierdzone.

## Kontrole i odrzucony wariant

[Audyt](cartridge-audit.json) wiąże wynik z sumami kontrolnymi CAD i skryptu.
Zakres: ścisłe BOP trzech części PETG, jedna bryła na część, pełne więzy,
przeliczenie pliku przeniesionego do pustego katalogu bez innych dokumentów,
zmiana wspólnego parametru, przecięcia wewnętrzne i 13 pozycji ogona
−30…+30° co 5°. Obwiednie 320 części bazowych służą do selekcji par;
zmieniona nasada zastępuje starą tylko w pamięci procesu kontrolnego.
Potomkowie starej nasady są obracani razem z nią. Nie jest to dowód ciągłego
prześwitu ani badanie solvera czy niepoprawnej w ścisłym BOP starej skorupy.

[Kontrola detali](cartridge-details.json) porównuje bryły w obu kierunkach
z niezależnymi oczekiwanymi operacjami, sprawdza referencję/łączniki, luzy i
warunkowy kanał narzędzia. Audyty nie zapisują CAD.

`rejected-r0/` zachowuje pierwszy wariant wraz z raportem, skryptem i widokiem:
kołnierz kolidował ze wspornikiem około 19,52 mm³ w każdej próbce, a nakrętki
przy większym skręcie do około 1,22 mm³. To wynik **odrzucony**, nie alternatywa
do montażu. R1 ma mniejszy kołnierz, bliższy rozstaw i zagłębione łby.

## Otwarte bramki przed instalacją

- Dostęp do śruby serwa jest sprawdzany tylko **przed założeniem nasady**.
  Nasada blokuje przyjętą obwiednię narzędzia Ø6. Trzeba rozwiązać pełną
  kolejność montażu, przytrzymanie łbów M2, demontaż i rzeczywistą końcówkę.
- Nie włączono automatycznie poprzedniej bocznej kieszeni nakrętki M3:
  nowy kołnierz zmienia jej wyjście, więc wcześniejsze wyniki serwisowe nie
  zatwierdzają tego wariantu. Ten dostęp wymaga ponownego projektu i próby.
- Nowe części nie mają jeszcze natywnych jointów. Nie dodano pozornego Fixed
  jako zastępstwa za niepotwierdzony orczyk. Integracja i ruch solvera dopiero
  po zamknięciu dostępu montażowego i ocenie mocowań.
- PETG: lokalnie dach 1,65, mostek 0,9 i ścianka gniazda łba 0,8 mm wymagają
  pogrubienia lub uzasadnionej próby. Podcięcie zmniejsza zewnętrzny pierścień
  nasady do 2 mm. Jedna poprawna bryła nie potwierdza wytrzymałości ani pełzania.
- Płytki mieszczą się z zapasem na stole 256³. Orientacje robocze zapisano
  w raporcie detali; nasada, podpory, dysza, warstwy i profil nadal niezatwierdzone.
- Dokładne śruby, nakrętki, przewód serwa, tolerancje PETG, obciążenia i trwałość
  wymagają dalszych kontroli. Nie aktualizowano bilansu masy całego robota.

Uruchamianie kontroli: Python dostarczony z FreeCAD 1.1.3, najpierw
`tools/cad/tail_cartridge_study.py audit`, potem `tools/cad/tail_cartridge_details.py`.
Procesy osobne, sekwencyjne; główne GUI nie przechowuje kolejnych wersji.
