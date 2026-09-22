# Robot-cat — mechanika i elektronika

Aktualny stan konstrukcji opisuje [STATUS mechaniki](skorupa/STATUS.md).
Punktem odniesienia jest **v35**, nadal prototyp, nie komplet zatwierdzony do
druku. Wyniki symulacji mają własny [opis i ograniczenia](simulation/README.md).

Przyjęty kierunek dalszego porządkowania repo opisuje
[plan modułowych masterów CAD](MODULAR_DESIGN.md): osobne edytowalne podzespoły,
wspólne interfejsy montażowe, złożenie korzystające z odnośników oraz
kontrolowane wydania. **Wdrożono [pierwszy pilot AUX](cad/README.md): 18 elementów
na odnośnikach; pozostałe 302 części pozostają snapshotami.** To nie migracja
całego robota ani naprawa otwartych problemów mechaniki.

[Skille projektu](../.agents/skills/), [PETG](manufacturing/PETG.md),
[elektronika](electronics/README.md), [częściowy BOM](bom/README.md) i
[kontrola wydań](releases/README.md) ujednolicają dalszą pracę Codexa i Claude'a.

Obecne katalogi pozostają na miejscu:

- `skorupa/` — historyczne checkpointy, mastery podzespołów, złożenia i audyty;
- `reference/` — dokumentacja i modele części handlowych;
- `simulation/` — modele pochodne CAD, bilanse i wyniki prób;
- `wavego/` — materiały bazowego robota.

Wszystkie projektowane części drukowane mają być z PETG, dla pola roboczego
256 × 256 × 256 mm. To nie zastępuje doboru orientacji druku, prób pasowania,
oceny wytrzymałości ani weryfikacji konkretnego profilu materiału.
