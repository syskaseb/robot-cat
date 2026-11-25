# WAVEGO 25 — wyłącznik bez klucza

[Złożenie FreeCAD](whole-cat25-s0-mounted.FCStd) · [Nowa tylna podstawa STL](STL/24S_RearBase_Carling.stl) · [Zbliżenie dźwigni](mounted-switch-close.png) · [Połączenia zasilania i próba bez zasilania](../ZASILANIE.md)

Ten STL zastępuje tylną podstawę z otworem po kluczu oraz pośrednią wersję z pełną ścianką. Drukuj jedną sztukę, główną płaszczyzną podstawy na stole. Do reszty robota użyj [spisu druku pakietu 25](../../PRINT.csv), z pominięciem kuponu kluczykowego FIT_S0 i starej tylnej podstawy. [Sprawdzenie wydruku z rezerwą](rear-mounted-stl.json)

1. Na stole załóż oba zaciśnięte i osłonięte oczka na wyłącznik Carling. Kontrolę wykonaj bez baterii, przewodu balansera i USB.
2. Przy zdjętej tylnej pokrywie i jeszcze nieosadzonej tylnej elektronice wsuń wyłącznik do podpór od wewnątrz z dźwignią wychyloną ku ogonowi. Zamocuj dwiema śrubami #6-32 UNC × 3/8″ z podkładkami 0,52 mm. Sprawdź wkręcenie w obie wkładki oraz oparcie podkładek przed dokręceniem.
3. Przyłóż pokrywę, przymierz obie pozycje dźwigni, sprawdź czy przewody nie są przycięte i czy XT60 można rozłączyć przy wyjmowaniu baterii. Dopiero wtedy ustal długości do cięcia. [Sprawdzone pozycje montażu](printed-mount-gate.json) · [Droga przewodów](mechanical-gate.json)

Projekt jest do przymiarki bez zasilania. Najciaśniejsze miejsce to osłona zacisku LINE przy zespole E1. Projektowe obrysy mijają się o ok. 0,24 mm. Na egzemplarzu sprawdź, czy osłona nie naciska na E1 i zostaje izolacja w każdym położeniu przewodu. Dostępność wyłącznika i rzeczywiste długości żył pozostają do potwierdzenia. [Odstępy przy zaciskach](terminal-minimum-gaps.json)
