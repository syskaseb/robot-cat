"""Actual saved Deck tessellation, elevated W061 and three tie seats."""
import json
from pathlib import Path
import sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]

def main():
    out=ROOT/(sys.argv[1] if len(sys.argv)>1 else "hardware/electronics/full-cat/body-ground-bridge-finish-r5")
    data=json.loads((out/"preview-geometry.json").read_text(encoding="utf-8"))
    image=Image.new("RGB",(1340,1040),"white");d=ImageDraw.Draw(image)
    font=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",22)
    small=ImageFont.truetype("C:/Windows/Fonts/arial.ttf",17)
    def xy(p):return (110+(p[0]+94)*4.5,170+(95-p[1])*3.7)
    vs=data["deck"]["vertices"]
    for tri in sorted(data["deck"]["triangles"],key=lambda t:sum(vs[i][2] for i in t)):
        d.polygon([xy(vs[i]) for i in tri],fill=(225,230,235),outline=(191,199,207))
    for row in data["routes"]:
        pts=[xy(p) for p in row["points"]]
        d.line(pts,fill=(29,63,120),width=7)
        for q in (pts[0],pts[-1]):d.ellipse((q[0]-5,q[1]-5,q[0]+5,q[1]+5),fill=(29,63,120))
    for a in data["anchors"]:
        x,y=xy([a["x"],a["y"],0]);d.ellipse((x-10,y-10,x+10,y+10),outline=(215,106,20),width=3)
        d.text((x+15,y+5),a["id"],font=small,fill=(130,64,0))
    for x,y,w,h in data["slots"]:
        d.rectangle((*xy([x-w/2,y+h/2,0]),*xy([x+w/2,y-h/2,0])),fill="white",outline=(215,106,20),width=2)
    for y,text in [(20,"W061 G1-G2: three seats; four Deck passages and two cantilever-beam passages"),
        (55,"Actual saved Deck tessellation and CAD centreline. R>=21mm, OD4.2mm, top loopZ136.5."),
        (90,"Conservative fuse topZ129.8; wire bottomZ134.4. Carrier/fuse fit and PETG checks: phase2."),
        (930,"One240mm blank from shared2m TKD2500125. Three T18I from shared stock; no added print jobs."),
        (965,"G1+X labels .1,.5,.3,.4,.2; G2+X .2,.3,.1,.4,.5. All cages in each block share one potential."),
        (1000,"Four other ground returns, other body/source leads and moving leg harnesses remain OPEN.")]:
        d.text((25,y),text,font=font,fill="black")
    image.save(out/"preview.png")

if __name__=="__main__":main()
