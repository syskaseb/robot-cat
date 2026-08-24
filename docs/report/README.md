# Dokumenty projektowe

Dwa PDF-y w `../`, oba generowane z tych skryptów:

| plik | co zawiera |
|---|---|
| `napedy-v4.pdf` | analiza techniczna: rozmiar, masa, moment, dobór napędu |
| `plan-zakupowy.pdf` | lista zakupów w dwóch wariantach i decyzja |

Wszystkie liczby pochodzą z pomiarów w symulacji albo ze sprawdzenia ofert —
skrypty ich nie liczą, tylko składają w dokument. Po nowej serii pomiarów
trzeba je nanieść ręcznie.

## Odbudowa

Z katalogu głównego repozytorium:

```bash
python docs/report/charts.py
python docs/report/chart_decision.py
python docs/report/make_pdf.py docs/napedy-v4.pdf
python docs/report/make_plan.py docs/plan-zakupowy.pdf
```

`make_plan.py` nie używa wykresów, więc można go uruchomić samodzielnie.

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
