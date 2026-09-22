# Checkpointy i wydania konstrukcji

Numer konstrukcji, rewizja części i gotowość produkcyjna to oddzielne informacje.
Żaden istniejący checkpoint nie uzyskuje tu automatycznie statusu do druku.

`python tools/cad/release_check.py hardware/releases/modular-pilot.json`
sprawdza integralność plików i manifestu. Opcja `--require-print-ready` dodatkowo
wymaga wszystkich bramek gotowości; dla obecnego prototypu ma zwracać błąd.

Manifest używa ścieżek względem korzenia repo, przypina zależności i dowody SHA-256.
Nie zawiera czasu jako substytutu rewizji. Checkpoint może jawnie zawierać OPEN
lub FAIL; wydanie do druku nie może pominąć wymaganej kontroli.

`.gitattributes` zachowuje LF dla haszowanych źródeł tekstowych i traktuje FCStd
jako pliki binarne. Zmiana końców linii przy checkout Windows/Linux nie powinna
unieważniać manifestu. Automatyczne kopie i katalogi scratch nie są pakowane.

Planowane tagi `hw-vX.Y.Z` tworzymy dopiero dla świadomie wybranego wydania.
Zapisanie manifestu nie tworzy tagu, nie publikuje plików i niczego nie zamawia.
