"""Small orthographic inspection of saved native W060 interfaces."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]

def main():
    out=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'hardware/electronics/full-cat/main-input-return-finish-r1')
    data=json.loads((out/'preview-geometry.json').read_text(encoding='utf-8'))
    im=Image.new('RGB',(1400,960),'white');d=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',21)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    panels=[('Deck top / XY',(30,90,880,570),(0,1),(-100,-96,142,100)),
            ('MAIN input / XZ',(930,90,1365,570),(0,2),(100,50,144,98)),
            ('Whole W060 / XZ',(30,640,1365,895),(0,2),(74,50,145,143))]
    for title,rect,axes,limits in panels:
        x0,y0,x1,y1=rect;a,b=axes;lo1,lo2,hi1,hi2=limits
        def point(p):return (x0+(p[a]-lo1)*(x1-x0)/(hi1-lo1),y1-(p[b]-lo2)*(y1-y0)/(hi2-lo2))
        d.text((x0,y0-28),title,font=font,fill='black')
        d.rectangle(rect,outline=(190,190,190))
        def color(n):
            n=n.lower()
            if n in ('deck','mainmount'):return (222,226,231)
            if 'tie' in n:return (226,145,55)
            if 'seat' in n:return (97,155,182)
            if 'boot' in n or 'inner' in n:return (60,135,96)
            return (30,39,49)
        # Draw background first, then the changed local interfaces/wire.
        ordered=sorted(data,key=lambda r:0 if r['name'] in ('Deck','MAINMount') else 1 if 'seat' in r['name'].lower() else 2)
        for row in ordered:
            vs=row['vertices'];n=row['name']
            for tri in row['triangles']:
                p=[vs[i] for i in tri]
                if all(lo1<=q[a]<=hi1 and lo2<=q[b]<=hi2 for q in p):
                    d.polygon([point(q) for q in p],fill=color(n))
        if title.startswith('Deck'):
            for p,label in [([81,13,0],'G1.2'),([132.5,0,0],'Input portal')]:
                x,y=point(p);d.text((x+8,y+8),label,font=small,fill=(140,40,20))
    d.text((25,18),'W060: shared K-1474 black input return. Native Deck + MAIN support; P0 unchanged.',font=font,fill='black')
    d.text((25,923),'CAD preview only. Black: conductor; green: insulation; blue: seats; orange: three ties. No physical PASS.',font=font,fill='black')
    im.save(out/'preview.png')

if __name__=='__main__':main()
