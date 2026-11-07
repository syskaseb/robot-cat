from pathlib import Path
import json,html,math
from PIL import Image,ImageDraw,ImageFont
o=Path('C:/Users/Sysq/PycharmProjects/robot-cat-mechanical/hardware/cad/studies/whole-cat-packaging/cp2/open-prototype/feline-enclosure');d=json.loads((o/'day07-whole-SOURCE-Knee-link-proposal-view.json').read_bytes());c=json.loads((o/'day07-SOURCE-holder-base-casing-conflict-and-length-boundaries.json').read_bytes());im=Image.new('RGB',(1480,950),'#f7f8fa');draw=ImageDraw.Draw(im);font=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n);svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="950"><rect width="1480" height="950" fill="#f7f8fa"/>']
def txt(x,y,s,n=19,color='#26384a'):
 draw.text((x,y),s,font=font(n),fill=color);svg.append(f'<text x="{x}" y="{y+n}" font-family="Arial" font-size="{n}" fill="{color}">{html.escape(s)}</text>')
def line(ps,color,width=2):draw.line(ps,fill=color,width=width);svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in ps)+f'" stroke="{color}" stroke-width="{width}" fill="none"/>')
def rect(x0,y0,x1,y1,color,width=2):draw.rectangle([x0,y0,x1,y1],outline=color,width=width);svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" stroke="{color}" stroke-width="{width}" fill="none"/>')
txt(28,20,'SOURCE C0 — actual contact available / solid base versus Knee casing HOLD',26,'#ad263b');txt(28,61,'Actual source face + cached Boolean intersection projected in the holder plane. Not wire-contact evidence.',19)
point=lambda q:(740+q[0]*12,350-q[1]*8)
for q in d['actual_face_curves_axis_transverse_mm']:line([point(p) for p in q],'#667d8f')
a=point([-43,7]);b=point([43,-7]);rect(a[0],a[1],b[0],b[1],'#dc8a1a')
for q in c['local_common_projection_curves']:line([point(p) for p in q],'#cf2b41',3)
for x in [-15,15]:
 a=point([x-2,2]);b=point([x+2,-2]);rect(a[0],a[1],b[0],b[1],'#238c72',3)
txt(80,117,'Grey: actual Link117 face / orange: 86 x 14 holder footprint',19);txt(80,148,'Green: contact sites, actual areas 15.666835 and 16 mm2; no fusion to the link',19,'#238c72');txt(80,181,'Red: actual retained case / proposed solid base common = 44.884383 mm3',19,'#ad263b')
txt(30,535,'Normal to the link: case intrusion 0..0.4 mm; proposed solid base 0..2; wire channel 2..6; cap 6..8.',20)
txt(30,575,'FIRST GATE: 2/10 holder-neighbour pairs received, 8 unreceived. No detailed holder, body landing or motion built.',19)
txt(30,620,'Whole source graph retained: FL1 continuous3 + FL2 continuous3 + FL3 original3 / donor3 → frame landing9',19)
txt(30,652,'→ V3 (7.2 x 2.8), D3 (10.5 x 3.9), G3 (10.5 x 3.9). All 9 IDs / 12 portions / 4 physical MAX3 units.',19)
txt(30,700,'Next causal interface: OPEN LADDER carrying the same sleeves, independent 9 mm lands and contact feet.',20,'#a05d16')
txt(30,732,'Keep the joint/frame/ports; bridge above the measured case lip. No holder pose offset and no V3 rib.',19,'#a05d16')
txt(30,776,'NOT BUILT / NOT ACCEPTED: useful sections, actual distances, selected tie feed paths and full neighbours still required.',18)
txt(30,825,'All source A/U, actual minimum lengths, fit blanks and usable slack remain NULL.',22,'#ad263b')
txt(30,865,'850 project rule, 900 per-unit MAX3, source factory plug, 3 x 8 laps, 3 x 20 sleeves and both 9 mm lands retained.',18)
txt(30,905,'Current 1292 / effective 1311 unchanged. N01 = 0/10. No physical cut, new splice, purchased part or geometry PASS.',18)
svg.append('</svg>');(o/'day07-SOURCE-Knee-holder-first-gate-view.svg').write_bytes(('\n'.join(svg)+'\n').encode());im.save(o/'day07-SOURCE-Knee-holder-first-gate-view.png');print('FIRST_GATE_VIEW_SAVED')
