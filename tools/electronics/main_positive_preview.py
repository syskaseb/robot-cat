"""Orthographic drawing of saved geometry, never an imagined CAD rendering."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/main-positive-native-r2'

def main():
    data=json.loads((OUT/'preview-geometry.json').read_text(encoding='utf-8'))
    im=Image.new('RGB',(1500,1000),'white');draw=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
    panels=[('Cały interfejs / XZ',(30,85,1460,430),(0,2),(-92,58,144,143)),
            ('Oprawka i łączenie / XY',(30,515,770,900),(0,1),(-90,-45,55,-8)),
            ('Dwa wejścia MAIN / YZ',(835,515,1460,900),(1,2),(-20,56,22,126))]
    for title,bounds,axes,limits in panels:
        x0,y0,x1,y1=bounds;a,b=axes;lo1,lo2,hi1,hi2=limits
        def point(v):return(x0+(v[a]-lo1)*(x1-x0)/(hi1-lo1),y1-(v[b]-lo2)*(y1-y0)/(hi2-lo2))
        draw.text((x0,y0-30),title,font=font,fill='black');draw.rectangle(bounds,outline='grey')
        for row in sorted(data,key=lambda r:0 if r['name'] in ('Deck','MAIN') else 1 if 'seat' in r['name'] else 2):
            n=row['name'];vs=row['vertices']
            color=(221,226,231) if n in ('Deck','MAIN') else (230,147,55) if 'tie' in n else (57,130,96) if any(k in n for k in ('boot','sleeve')) else (97,156,180) if 'seat' in n else (161,48,48) if n.startswith('W078') else (43,52,61)
            for triangle in row['triangles']:
                pts=[vs[i] for i in triangle]
                if all(lo1<=p[a]<=hi1 and lo2<=p[b]<=hi2 for p in pts):draw.polygon([point(p) for p in pts],fill=color)
    draw.text((30,20),'F_PI → MAIN: rzeczywista zapisana geometria. P0/E6 zachowane; przymiarka w fazie 2.',font=font,fill='black')
    draw.text((30,940),'Szary: części PETG. Pomarańczowy: opaski. Zielony: izolacja. Czerwony: W078. Bez fizycznego PASS.',font=font,fill='black')
    im.save(OUT/'preview.png')

if __name__=='__main__':main()
