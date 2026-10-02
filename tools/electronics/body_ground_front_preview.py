"""Orthographic preview of saved native Deck and W036 CAD centreline."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/body-ground-front-finish-r1'

def main():
    data=json.loads((OUT/'preview-geometry.json').read_text(encoding='utf-8'))
    im=Image.new('RGB',(1500,1150),'white');d=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
    panels=[('Selected Deck / XY',(25,100,900,775),(0,1),(-100,-96,135,98)),
      ('Independent G1 restraints / XY',(950,100,1470,400),(0,1),(50,8,89,19)),
      ('G1 source lift / YZ',(950,460,1470,775),(1,2),(8,98,68,139)),
      ('Middle support / YZ',(25,850,900,1090),(1,2),(47,103,76,130))]
    route=data['route']['points']
    for title,box,axes,limits in panels:
        x0,y0,x1,y1=box;a,b=axes;lo1,lo2,hi1,hi2=limits
        def p(q):return (x0+(q[a]-lo1)*(x1-x0)/(hi1-lo1),y1-(q[b]-lo2)*(y1-y0)/(hi2-lo2))
        d.text((x0,y0-30),title,font=font,fill='black');d.rectangle(box,outline=(150,150,150))
        for row in data['shapes']:
            vs=row['vertices'];n=row['name']
            if title.startswith('G1 source') or title.startswith('Middle'):
                if n=='Deck':continue
            color=(224,229,234) if n=='Deck' else (207,141,56) if 'tie' in n else (73,152,179)
            for tri in sorted(row['triangles'],key=lambda t:sum(vs[i][2] for i in t)):
                pts=[vs[i] for i in tri]
                if title.startswith('Middle') and not n.startswith('Middle'):continue
                if title.startswith('G1') and n!='Deck' and not n.startswith('G1'):continue
                if all(lo1<=q[a]<=hi1 and lo2<=q[b]<=hi2 for q in pts):d.polygon([p(q) for q in pts],fill=color)
        last=None
        for q in route:
            valid=lo1<=q[a]<=hi1 and lo2<=q[b]<=hi2
            if title.startswith('G1 source'):valid=valid and abs(q[0]-73.5)<1e-4
            if title.startswith('Middle'):valid=valid and abs(q[1]-62.5)<1e-4 and -11<=q[0]<=-3
            if valid:
                now=p(q)
                if last:d.line((last,now),fill=(20,35,50),width=4)
                last=now
            else:last=None
        if title.startswith('G1 source'):
            d.ellipse((*p([0,49.25,130.75]),*p([0,46.75,133.25])),outline=(210,50,30),width=2)
            d.text(p([0,49.5,133.5]),'XA02 (OD2.5)',font=font,fill=(160,40,20))
    d.text((25,20),'W036 G1.4 -> FR_G.1: R21, lane Y62.5/Z124.5. Independent narrow G1 restraints.',font=font,fill='black')
    d.text((950,850),'Blue: seats; orange: ties;',font=font,fill='black')
    d.text((950,885),'black: CAD centreline.',font=font,fill='black')
    d.text((950,950),'Saved native geometry,',font=font,fill='black')
    d.text((950,985),'not physical fit or print PASS.',font=font,fill='black')
    im.save(OUT/'preview.png')

if __name__=='__main__':main()
