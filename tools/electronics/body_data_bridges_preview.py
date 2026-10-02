"""Actual saved Deck tessellation and DATA centerlines; no fabricated render."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"hardware/electronics/full-cat/body-data-bridges-r7"

def main():
    data=json.loads((OUT/"preview-geometry.json").read_text(encoding="utf-8"))
    image=Image.new("RGB",(1320,1040),"white");d=ImageDraw.Draw(image)
    font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",22)
    small=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",17)
    def xy(p):return (110+(p[0]+94)*4.5,170+(95-p[1])*3.7)
    v=data["deck"]["vertices"]
    for tri in sorted(data["deck"]["triangles"],key=lambda t:sum(v[i][2] for i in t)):
        pts=[v[i] for i in tri]
        shade=tuple(int(c) for c in (225,230,235))
        d.polygon([xy(p) for p in pts],fill=shade,outline=(191,199,207))
    colors={"W007":(23,101,173),"W011":(144,63,168),"W012":(6,135,105)}
    for row in data["routes"]:
        pts=[xy(p) for p in row["centerline"]];color=colors[row["name"]]
        d.line(pts,fill=color,width=5)
        for q in (pts[0],pts[-1]):d.ellipse((q[0]-5,q[1]-5,q[0]+5,q[1]+5),fill=color)
        middle=pts[len(pts)//2];d.text((middle[0]+5,middle[1]-25),row["name"],font=font,fill=color)
    for n,e,x,y in data["anchors"]:
        xx,yy=xy([x,y,0]);d.ellipse((xx-9,yy-9,xx+9,yy+9),outline=(214,102,16),width=3)
        d.text((xx+12,yy+3),f"{n}/{e}",font=small,fill=(133,62,0))
    for x,y,w,h in data["slots"]:
        a=xy([x-w/2,y+h/2,0]);b=xy([x+w/2,y-h/2,0])
        d.rectangle((*a,*b),fill="white",outline=(214,102,16),width=2)
    for y,text in [(20,"R37 candidate: 3 fixed DATA bridges, 6 insulation restraints, 12 through-slots"),
        (55,"Top view of actual Deck tessellation. Coloured paths are saved exact centerlines."),
        (90,"Raised crossings: W007/W012 Z126; W011 S-bends Z118.5 over XA05. Radius >=5.2 mm."),
        (930,"Pi fan window preserved. Orange: six tie locations; two ties rotated onto straight X lanes."),
        (965,"Provisional cage datums and tie-head reservations. PETG, delivered fit and signal tests: phase 2."),
        (1000,"Three 200mm blanks from the existing DATA wire stock. W5 remains OPEN; no physical PASS.")]:
        d.text((25,y),text,font=font,fill="black")
    image.save(OUT/"preview.png")

if __name__=="__main__":main()
