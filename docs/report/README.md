# Raport o doborze napędów

`../napedy-v4.pdf` powstaje z tych trzech skryptów. Wszystkie liczby w
dokumencie pochodzą z pomiarów w symulacji — skrypty ich nie liczą, tylko
składają w dokument, więc po nowej serii pomiarów trzeba je nanieść ręcznie.

## Odbudowa

Z katalogu głównego repozytorium:

```bash
python docs/report/charts.py
python docs/report/chart_decision.py
python docs/report/make_pdf.py docs/napedy-v4.pdf
```

Wymaga `reportlab`, `matplotlib` i `pillow`, oraz czcionki Calibri — czyli
uruchamia się na Windowsie, nie w kontenerze ROS. Calibri, a nie wbudowane
Helvetica, bo to drugie nie ma polskich znaków i renderuje każde `ł`, `ą`
i `ę` jako czarny prostokąt.

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
