from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
d=json.loads((P/'well-sections.json').read_bytes());xs=d['x'];ys=d['y']
def roof(x,row,role):
 a=[V(x,y,z) for y,z in zip(ys,row)]
 b=([V(x,ys[-1],8),V(x,ys[0],8)] if role=='void' else [V(x,y,z+2.4) for y,z in reversed(list(zip(ys,row)))])
 return Part.makePolygon(a+b+[a[0]])
loft=lambda role:Part.makeLoft([roof(x,row,role) for x,row in zip(xs,d['underside'])],True,True)
cavity=loft('void');panel=loft('sheet');assert panel.isValid() and cavity.isValid()
n='H19_FrontFrame';s=sh(n).Solids[0];initial=s.Volume
# Two inline bodies share a shelf just inboard of the repaired lower skin. The
# factory end axes remain parallel to X; slide both in before the cable bank.
names=['NIGHT_INLINE_FL_W026','NIGHT_INLINE_FL_W041'];tabs=[]
for name in names:
 b=sh(name).BoundBox;dy=b.YMin
 for t in [.19,.76]:
    x=-104+b.XLength*t
    s=s.cut(box(x-.02,b.YMin-1.12,45.48,3.44,b.YLength+2.24,8.27),.00001)
 o=D.getObject(name);o.Placement=A.Placement(V(-111-b.XMin,0,69.2-b.ZMin),A.Rotation()).multiply(o.Placement)
 b=sh(name).BoundBox
 for t in [.19,.76]:
    x=b.XMin+b.XLength*t
    tabs.extend([box(x,b.YMin-1,66.45,3.4,b.YLength+2,2.75),box(x,b.YMin-1.2,66.7,3.4,1,5.1),box(x,b.YMax+.2,66.7,3.4,1,5.1)])
    for y in [b.YMin+.75,b.YMax-3.2]:tabs.append(box(x+.3,y,40.9,2.8,2.6,26.9))
# Reuse exactly the original outer wall before its lower exit was cut.
import zipfile
from xml.etree import ElementTree as ET
with zipfile.ZipFile(P.parent/'day19-real-terminations-and-assembly/whole-cat19G.FCStd') as f:
 prop=ET.fromstring(f.read('Document.xml')).find("./ObjectData/Object[@name='E19_ForeBase']/Properties/Property[@name='Shape']/Part");orig=Part.Shape();orig.importBrepFromString(f.read(prop.get('file')).decode())
plug=orig.common(box(-64,-104.2,60.1,26,5.8,15.5))
s=s.fuse(plug,.00001).fuse(join(tabs),.00001).cut(cavity,.00001).fuse(panel,.00001).removeSplitter()
x=-51;z=93.0;slot=box(x-6.5,-105,z-5.25,13,7,10.5)
for xx in [x-6.5,x+6.5]:
 slot=slot.fuse(cyl(xx,-105,z,5.25,7,(0,1,0)))
 for y,a,b in [(-103.15,6.05,5.25),(-102.1,5.25,6.05)]:slot=slot.fuse(Part.makeCone(a,b,1,V(xx,y,z),V(0,1,0)))
s=s.cut(slot,.00001).removeSplitter()
r=dict(rail_and_floor_before=initial,after=s.Volume,slot=[x,-102,z],transferred_whole_inline=names,changed_pose=[-7,0,18],legs=['RR'],panel_volume=panel.Volume,void_bounds=bounds(cavity),members=[dict(volume=v.Volume,bounds=bounds(v)) for v in s.Solids],valid=s.isValid())
wr('well-material.json',r);assert r['valid'] and len(s.Solids)==1,r
D.getObject(n).Shape=s
# Carry the aft side of the JPWM shelf OUTSIDE the entire two-housing field.
n='E19_RearLid';s=sh(n).Solids[0]
s=s.fuse(box(59.7,-17.75,117.5,2.7,2.6,55.48),.00001).fuse(box(58.6,-21.5,117.4,4.75,6.35,2.59),.00001)
s=s.cut(box(59.64,-20.95,119.995,2.82,2.67,51.6),.00001).removeSplitter()
assert len(s.Solids)==1 and s.isValid();D.getObject(n).Shape=s
# HP keeper goes over the other original rung, away from the AUX outbound lead.
n='I19_FuseBand_HP';o=D.getObject(n);o.Placement=A.Placement(V(51*(.76-.19),0,0),A.Rotation()).multiply(o.Placement)
D.recompute();D.save()
