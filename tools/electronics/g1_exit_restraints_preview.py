"""Inspect actual saved Deck and the two independent G1 restraints."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'hardware/electronics/full-cat/g1-exit-restraints-finish-r1'

def main():
    data=json.loads((OUT/'preview-geometry.json').read_text(encoding='utf-8'))
    im=Image.new('RGB',(1400,1000),'white');d=ImageDraw.Draw(im)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
    panels=[('Saved Deck / XY',(25,100,875,800),(0,1),(-100,-96,135,98)),
      ('G1 mouths / XY',(930,100,1370,395),(0,1),(47,8,90,19)),
      ('Independent cradles / XZ',(930,465,1370,800),(0,2),(47,98,90,118))]
    for title,box,axes,limits in panels:
        x0,y0,x1,y1=box;a,b=axes;lo1,lo2,hi1,hi2=limits
        def p(q):return (x0+(q[a]-lo1)*(x1-x0)/(hi1-lo1),y1-(q[b]-lo2)*(y1-y0)/(hi2-lo2))
        d.text((x0,y0-30),title,font=font,fill='black');d.rectangle(box,outline=(150,150,150))
        for row in data:
            vs=row['vertices'];n=row['name']
            if title.startswith('Independent') and n=='Deck':continue
            color=(223,229,233) if n=='Deck' else (219,149,56) if 'tie' in n else (75,153,180)
            for tri in sorted(row['triangles'],key=lambda t:sum(vs[i][2] for i in t)):
                pts=[vs[i] for i in tri]
                if all(lo1<=q[a]<=hi1 and lo2<=q[b]<=hi2 for q in pts):d.polygon([p(q) for q in pts],fill=color)
        if title.startswith(('G1','Independent')):
            for x,label,r in [(51,'BAT',1.55),(58.5,'W061',2.1),(66,'W025',2.1),(73.5,'W036',2.1),(81,'W060',1.5)]:
                if a==0 and b==1:
                    q=p([x,11,113.5]);d.line((q,p([x,13,113.5])),fill=(30,45,60),width=4)
                    d.text((q[0]-18,y1-30),label,font=font,fill='black')
                else:
                    q=p([x,12.5,113.5]);scale=(x1-x0)/(hi1-lo1)
                    d.ellipse((q[0]-r*scale,q[1]-r*scale,q[0]+r*scale,q[1]+r*scale),outline=(20,35,50),width=2)
    d.text((25,20),'G1: two independent narrow cradles. W060/W061 routes and quantities unchanged.',font=font,fill='black')
    d.text((25,855),'Blue: integral cradles; orange: two T18I loops, with heads centred underneath.',font=font,fill='black')
    d.text((25,890),'Four new full Deck passages; historical wider passages unused. No new print jobs or ties.',font=font,fill='black')
    d.text((25,925),'BAT/W025/W036 shown only as reserved exit stubs, NOT selected full routes. Physical checks: phase2.',font=font,fill='black')
    im.save(OUT/'preview.png')

if __name__=='__main__':main()
