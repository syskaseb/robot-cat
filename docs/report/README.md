# Dokumenty projektowe

Pięć PDF-ów w `../`, wszystkie generowane z tych skryptów:

| plik | co zawiera |
|---|---|
| `napedy-v4.pdf` | analiza techniczna: rozmiar, masa, moment, dobór napędu — **źródło prawdy dla liczb w pozostałych** |
| `plan-zakupowy.pdf` | pełna lista zakupów z cenami i sumą |
| `montaz.pdf` | brakujące kable i narzędzia, wymiary obudowy, kolejność montażu i uruchamiania |
| `uzupelnienie-elektroniki.pdf` | montaż w stawie vs w brzuchu, jeden kompute vs per-noga, porównanie z QDD, płynność chodu |
| `ekspansja-wizyjna.pdf` | plan dojścia do „idź do pokoju A, zobacz co na stole" — SLAM, Nav2, YOLOv8 na Hailo |

`montaz.pdf` bierze wymiary z `cat.urdf.xacro` przy `scale 1.0`. **Ten plik
jest źródłem prawdy** — po zmianie modelu dokument trzeba wygenerować od nowa,
bo inaczej obudowa przestanie pasować do tego, na czym liczono momenty.

Wszystkie liczby pochodzą z pomiarów w symulacji albo ze sprawdzenia ofert —
skrypty ich nie liczą, tylko składają w dokument. Po nowej serii pomiarów
trzeba je nanieść ręcznie.

Dokumenty opisują **stan obecny, bez historii zmian**. Kiedy jakaś wartość
przestaje obowiązywać, podmienia się ją, a nie dopisuje obok wyjaśnienia, co
było wcześniej — inaczej dokumenty puchną, a czytelnik musi zgadywać, która
liczba jest aktualna. Uzasadnienia zostają tylko wtedy, gdy dotyczą decyzji
wciąż wiążącej.

## Odbudowa

Z katalogu głównego repozytorium:

```bash
python docs/report/charts.py
python docs/report/chart_decision.py
python docs/report/make_pdf.py docs/napedy-v4.pdf
python docs/report/make_plan.py docs/plan-zakupowy.pdf
python docs/report/make_montaz.py docs/montaz.pdf
python docs/report/make_uzupelnienie.py docs/uzupelnienie-elektroniki.pdf
python docs/report/make_wizja.py docs/ekspansja-wizyjna.pdf
```

`make_plan.py` i `make_montaz.py` nie używają wykresów, więc można je
uruchamiać samodzielnie.

Wymaga `reportlab`, `matplotlib` i `pillow` — czyli własnego venva, nie
środowiska ROS, które `reportlaba` nie ma:

```bash
python3 -m venv /tmp/pdfenv && /tmp/pdfenv/bin/pip install reportlab pillow matplotlib
```

Czcionka musi mieć polskie znaki: wbudowana w reportlab Helvetica ich nie ma
i renderuje każde `ł`, `ą` i `ę` jako czarny prostokąt. Skrypty szukają po
kolei **Calibri** (Windows, gdzie te dokumenty powstały), potem **Carlito**,
który ma identyczne metryki — więc dokument złamie się na te same strony
niezależnie od systemu:

```bash
brew install --cask font-carlito          # macOS
apt install fonts-crosextra-carlito       # Debian/Ubuntu
```

`make_uzupelnienie.py` i `make_wizja.py` używają zamiast tego **DejaVu Sans** i
same jej szukają — kolejno w fontach systemowych, a na końcu w tej dołączonej
do matplotliba (czyli w środowisku pixi działa bez instalowania czegokolwiek).
Jeśli nie znajdą, kończą czytelnym komunikatem zamiast rysować czarne prostokąty.
Skutek uboczny: te dwa dokumenty łamią się na inne strony niż pozostałe trzy.

Wykresy używają dołączonej do matplotliba czcionki **DejaVu Sans**. Jedna
rodzina na wszystkich systemach zapobiega znikaniu znaków w tytułach,
legendach i adnotacjach podczas wyboru czcionek zastępczych.

## Wykresy

Zapisywane jako PNG obok skryptów i osadzane w PDF-ie. Po wygenerowaniu warto
je spaletować — to grafika liniowa, więc 64 kolory wystarczą i zbijają rozmiar
z ~35 KB do ~9 KB na wykres:

```python
from PIL import Image
Image.open(p).convert("RGB").quantize(colors=64).save(p, optimize=True)
```

Bez tego PDF ma ~420 KB zamiast ~170 KB, co ma znaczenie przy wysyłaniu go
mailem.
