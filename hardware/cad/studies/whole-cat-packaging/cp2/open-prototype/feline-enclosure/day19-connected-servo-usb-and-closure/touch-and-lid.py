"""Keep the live touch surface on the outer cover. Lay uncut USB and tail laterally."""
from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
src=(P/'gallery.py').read_text();exec(src[:src.index('bp=transform')])
lid=sh('E19_ForeLid');cap=sh('F19_ForeCap');b=sh('TTP223_touch').BoundBox
cap=cap.cut(box(-15.05,-36.05,173.55,17.5,14.5,25.94))
cap=cap.fuse(box(-15.2,-36.2,199.49,17.8,14.8,1.51))
for x in [b.XMin+2,b.XMax-8]:
    for sg,y in [(-1,b.YMin),(1,b.YMax)]:
        lid=lid.cut(box(x-.09,y-1.65,161.5,6.18,3.28,9.9))
        xx=x+8;yy=y+10;z=b.ZMin+28
        cap=cap.fuse(box(xx,yy-1.55 if sg<0 else yy+.17,z-1.45,6,1.38,200.5-z+1.45))
        cap=cap.fuse(box(xx,yy-1.55 if sg<0 else yy-1.2,z-1.45,6,2.75,1.35))
transform(['TTP223_touch'],[0,0,0],[8,10,28],0)
D.E19_ForeLid.Shape=lid.removeSplitter();D.F19_ForeCap.Shape=cap.removeSplitter()
rear=sh('E19_RearLid')
for y,x,w in [(-.66,59,8.4),(-63.8,55,5.4)]:
    rear=rear.cut(box(19.9,y-w/2,170.8,x-19.9,w,3.2))
D.E19_RearLid.Shape=rear.removeSplitter()
changed=list(json.loads((P/'new-members.json').read_bytes()))
wr('new-members.json',{n:dict(valid=sh(n).isValid(),members=[dict(mm3=v.Volume,bounds=bounds(v)) for v in sh(n).Solids]) for n in changed})
D.recompute()
exec(src[src.index('view=(E/'):])
