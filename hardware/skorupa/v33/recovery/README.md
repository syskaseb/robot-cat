# Odzyskanie topologii skorupy — nie certyfikat do druku

Źródłowy `HeadFront` v31 (dziedziczony również w v32) miał 62 krawędzie
siatki współdzielone przez cztery trójkąty w okolicy starego nosa. `isValid()`
zwracało True, ale BOP zgłaszał m.in. self-intersection, a `isInside()`
uznawało punkt daleko przed głową za wnętrze. Nie wolno ufać samemu
statusowi Valid ani wcześniejszym testom Boolean tej części.

`probe33_makervolume.py` odtwarza komórki z 47 ścian v31, używając
OCCT 8.0.1 (`cadquery-ocp 8.0.1.0.0`, osobne środowisko diagnostyczne).
MakerVolume: intersect=True, avoidInternalShapes=True, nonDestructive=True,
fuzzy=0,00001 mm. Powstały dwie komórki: 42124,01848 i 673,20731 mm³.
Wybrano główną skorupę; mała komórka leży w obszarze dawnego nosa,
X −191,75…−190,25, Y ±12,5, Z104…122,75. Odtwarzanie tworzy kandydatów
w ignorowanym cache, **nie podmienia automatycznie modelu**.

Wejście `v31/shape-cache/HeadFront.brep` SHA256:
`cf864082464ced13665d4987df0a58e9bac1633f092d09b50cd883566e0e51ac`.
Znormalizowany przez Python FreeCAD `HeadShellRecovered33.brep` SHA256:
`a99b0efdf86847c5cc693815f7d458ea75ec0b0b8f3bcfe19a967fe88c331c70`.
Oryginalne pliki v31/v32 nie zostały zmienione.

`ApplyRecovery33.FCMacro` importuje osobną cechę źródłową. Zachowuje starą
cechę jako dokumentację, ale obliczenia prowadzi przez odzyskaną skorupę,
natywny Pocket 22×29 R2, potem Fuse pyszczka i dwóch podpór. Odwrotna
kolejność Pocket/Fuse dawała błędną geometrię mimo pozornego statusu Valid.
Każdy etap sprawdzamy osobno; nie akceptujemy starej bryły z błędnej cechy.

Historyczny `HeadFrontSource32` wewnątrz mastera nie jest kopią bitową:
nieudane operacje OCCT zmieniły metadane tolerancji jego krawędzi. Nie używamy
go do wyznaczania materiału aktualnej głowy ani jako oryginału archiwalnego.
Oryginałem pozostaje niezmieniony, podpisany plik v32. Audyt porównuje ściśle
zachowany pyszczek oraz aktualną bryłę i PCB między masterem a złożeniem.

Aktualny przód ma zamkniętą, poprawnie zorientowaną siatkę bez krawędzi
non-manifold. Osobny silnik Manifold sprawdza rezerwy nosa/przewodów/narzędzi.
Wyniki i podpis mastera są w `../mesh-proof.json`. BOP finalnej bryły nadal
zgłasza błędy: SelfIntersect przy wierzchołkach, TooSmallEdge oraz C0/krzywe
na powierzchniach. Pozostają otwarte,
nie przemianowano ich na zaliczony audyt produkcyjny. Do dalszych zmian
potrzebne są kontrole operacji oraz niezależna siatka, nie samo `isValid()`.
