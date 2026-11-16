"""Read-only measurement card from frozen nominal case positions; no CAD edits."""
from pathlib import Path
import hashlib
import json
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure/day16-functional-power-bay/proposal-geometry-map.json'
rows = json.loads(SOURCE.read_text(encoding='utf-8'))
names = ['PBAY_P_SYS', 'PBAY_P_REAR', 'PBAY_F_PI', 'PBAY_F_AUX']
rows = [next(r for r in rows if r['name'] == n) for n in names]
meta = {
    'purpose': 'UNPOWERED_MEASUREMENT_CARD_NOT_MOUNT_DRAWING_OR_ROUTE_ACCEPTANCE',
    'position_source_commit': 'd0757ee5debb3b4e30ed4872758267624b1e6d07',
    'same_position_material_snapshot_commit': '5e504127',
    'source_path': str(SOURCE),
    'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'cases': rows,
    'whole_cat_accepted': False,
    'actual_wire_cut_slack': None,
    'note': 'Nominal allocation footprints only. Actual mouths, levers, strain exits and delivered wire lengths require one physical unit check. A failed CAD curve does not reject all manual paths.',
}
(HERE / 'W043_SOURCE.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')

plt.rcParams.update({'font.family': 'DejaVu Sans', 'svg.fonttype': 'none'})
fig = plt.figure(figsize=(210 / 25.4, 297 / 25.4), facecolor='white')
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 210)
ax.set_ylim(297, 0)
ax.axis('off')

def text(x, y, s, size=9, color='#172436', weight='normal', **kw):
    ax.text(x, y, s, fontsize=size, color=color, weight=weight, va='top', **kw)

text(18, 15, 'Krótki przewód: sprawdź na częściach', 15, weight='bold')
text(18, 25, 'W043 / F_PI - P_SYS   |   BEZ ZASILANIA   |   karta pomiaru A4, skala 1:1', 8.5)
text(18, 34, 'To nie jest szablon mocowania ani potwierdzona trasa kabla.', 10, '#a03824', 'bold')
text(18, 43, 'Pola poniżej pokazują obecną propozycję obudów, bez przewodów i mocowań.', 8.3)

for x in range(35, 171, 5):
    ax.plot([x, x], [57, 111], color='#e8edf1', lw=.35, zorder=0)
for y in range(57, 112, 5):
    ax.plot([35, 170], [y, y], color='#e8edf1', lw=.35, zorder=0)
for r in rows:
    x0, y0, z0, x1, y1, z1 = r['bounds']
    x, y = 35 + x0 - 55, 57 + 100 - y1
    color = '#dce9f7' if r['function'] == 'F_PI' else '#f9e5d6' if r['function'] == 'F_AUX' else '#e9edf1'
    ax.add_patch(Rectangle((x, y), x1-x0, y1-y0, facecolor=color, edgecolor='#2f4458', lw=.8, linestyle=(0, (4, 2))))
    text(x + (x1-x0)/2, y + 2.2, r['function'], 8.7, weight='bold', ha='center')
    if r['function'].startswith('F_'):
        text(x + (x1-x0)/2, y + 10.3, 'FHAC: 3 A' if r['function'] == 'F_PI' else 'FHAC: 4 A', 8.2, ha='center')
    else:
        text(x + (x1-x0)/2, y + 6.8, '615', 7, ha='center')
text(35, 105, 'Połóż całe korpusy. Zaznacz prawdziwe wyjścia, dźwignie i końce ręcznie.', 8)
ax.annotate('', xy=(183, 64), xytext=(183, 80), arrowprops={'arrowstyle': '->', 'lw': .8})
text(180, 58, '+Y', 8)
ax.annotate('', xy=(194, 88), xytext=(178, 88), arrowprops={'arrowstyle': '->', 'lw': .8})
text(190, 91, '+X', 8)
ax.plot([35, 135], [121, 121], color='black', lw=1)
for x in (35, 135):
    ax.plot([x, x], [119.5, 122.5], color='black', lw=1)
text(85, 125, '100 mm - sprawdź linijką po wydruku; bez dopasowania do strony', 8, ha='center')

text(18, 138, 'Wysokości propozycji - widok z góry nie pokazuje kolizji w 3D', 10, weight='bold')
text(18, 147, 'Części', 9, weight='bold')
text(93, 147, 'Spód nad poziomem FHAC', 8.5, weight='bold')
text(163, 147, 'Wysokość', 8.5, weight='bold')
ax.plot([18, 192], [153, 153], color='#9ba9b5', lw=.5)
text(18, 156, 'F_PI i F_AUX', 9)
text(108, 156, '0 mm', 9)
text(166, 156, '20,25 mm', 9)
text(18, 164, 'P_SYS i P_REAR (pionowo)', 9)
text(108, 164, '5 mm', 9)
text(166, 164, '37 mm', 9)
text(18, 174, 'To wymiary pól modelu, nie pomiar dostarczonych części.', 8.5, '#a03824')

steps = [
    '1. Porównaj korpusy i pokrywki z polami. Zmierz oba fabryczne odcinki jednego FHAC od tego samego, zapisanego miejsca. Nic nie obcinaj.',
    '2. Przy otwartym układzie sprawdź całe zakończenia i dostęp do dźwigni. Przewód ułóż swobodnie, bez naprężania obudowy i ostrego załamania.',
    '3. Zapisz długości i to, co przeszkadza; zrób zdjęcie z linijką. Brak miejsca nie jest zgodą na przedłużkę ani na przesunięcie kupnych części na siłę.',
]
y = 185
for s in steps:
    lines = textwrap.wrap(s, width=94)
    text(18, y, '\n'.join(lines), 9.1, linespacing=1.4)
    y += len(lines)*5 + 6
text(18, 251, 'Zapis: odcinek A ______ mm   B ______ mm   wyjścia / przeszkoda __________________', 8.7)
text(18, 263, 'W modelu odrzucono JEDEN łuk przy F_AUX. Nie dowodzi to braku każdej trasy.', 8.2, '#a03824')
text(18, 270, 'Próba tej jednostki nie sprawdza pozostałych modułów, podpór ani zamknięcia kota.', 8.2)
text(18, 283, 'Źródło: nominalna alokacja d0757ee5, zachowana w 5e504127. 16 XI 2026.', 7.1, '#536273')
text(18, 288, 'Rzeczywiste długości / cięcia / luz: nieustalone. Pełne instrukcje w pakiecie START_HERE.', 7.1, '#536273')

fig.savefig(HERE / 'W043_LAYOUT_WORKSHEET.svg', format='svg')
svg = HERE / 'W043_LAYOUT_WORKSHEET.svg'
svg.write_bytes(svg.read_bytes().replace(b'\r\n', b'\n'))
fig.savefig(HERE / 'W043_LAYOUT_WORKSHEET.png', dpi=140)
plt.close(fig)
(HERE / 'W043_LAYOUT_WORKSHEET.html').write_text('''<!doctype html>
<html lang="pl"><meta charset="utf-8"><title>W043 - karta pomiaru</title>
<style>@page{size:A4 portrait;margin:0}html,body{margin:0;background:#eef1f5}img{display:block;width:210mm;height:297mm;margin:auto;background:white}@media print{html,body{background:white}img{margin:0;page-break-after:avoid}}</style>
<img src="W043_LAYOUT_WORKSHEET.svg" alt="Karta pomiaru czterech obudów przy krótkim W043. Wydruk A4, 100 procent, bez dopasowania; zweryfikuj podziałkę100mm.">
</html>\n''', encoding='utf-8', newline='\n')
print('W043 worksheet: SVG / PNG / HTML / pinned source JSON; no CAD changes.')
