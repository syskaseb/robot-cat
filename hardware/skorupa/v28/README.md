# v28 — zainstalowana poprawka osłony PETG

Aktualne złożenie: **`Kot_v28_BIODRA_PETG.FCStd`**.
Poprzednie v25 i v27 pozostają jako oddzielne checkpointy/backupy.
**To nadal prototyp, nie paczka zatwierdzona do druku.**

Zachowano poprawione w [v27](../v27/README.md) przypisanie czterech serw
biodrowych oraz wszystkie natywne więzy: 12 Revolute i 225 Fixed,
w tym 64 jawnie tymczasowe blokady niedokończonych podzespołów.

Podmieniono wyłącznie `Part__Feature` / `FrontRearCover`, korzystając
z edytowalnego wzorca MCP `v27/FrontCoverClearance27.FCStd`. Złożenie zawiera
migawkę jego geometrii i właściwość `ParametricMaster`; po zmianie wzorca
trzeba ponownie przenieść wynik, nie jest to automatyczny link między plikami.
Otwory M3 i otaczający je materiał pozostają bez zmian; masa maleje o 0,76 g.

## Sprawdzenia

- Natywny solver: sukces, **22 klatki ±3°**, wszystkie łączenia zachowane,
  brak wspólnej objętości poprawionej osłony i dwóch kolidujących wcześniej
  obudów serw. Wynik w `assembly-validation.json`.
- Wzorzec osłony: 42 próbki przy ±10°, luz minimum 0,936 mm, poprawna jedna
  bryła i zachowane otoczenie ośmiu otworów M3 — raport w v27.
- Regresja sześciu tych samych pozycji co w v27: brak przenikań osłony
  z ruchomymi częściami powyżej 0,1 mm³. Pozostałe 237 części i osie nie były
  zmieniane; ich pary dziedziczą wcześniejszy audyt. To **inkrementalny test
  sześciu pozycji**, nie nowy pełny przegląd ciągłego chodu ani części
  należących do tego samego ciała sztywnego.
- Nowy eksport 238 BRep/13 siatek i sześć prób **Gazebo v28**:
  stanie, chód przy masie nominalnej i zwiększonej, powtórzone po usunięciu
  sztucznego ogranicznika prędkości. Wszystkie ukończone; wnioski opierają
  się na ostatnich trzech, wcześniejsze są oznaczone jako porównawcze.
- 22 testy obliczeń CAD zaliczone; wcześniejsza regresja 581 testów ROS
  także zaliczona. Nie zmieniono zachowania starego kontrolera ROS.

[Raport symulacji](../../simulation/README.md),
[wyniki v28](../../simulation/v28/RESULTS.md),
[pozostała mechanika i decyzje](../STATUS.md).

W FreeCAD pozostawiono widok całego kota. Cache `shape-cache/` jest
regenerowany bez edycji przez `Cache28.FCMacro` i ignorowany w Git; jego zapis zawiera
hash źródła. Model zapisano po przywróceniu pozycji spoczynkowej.
