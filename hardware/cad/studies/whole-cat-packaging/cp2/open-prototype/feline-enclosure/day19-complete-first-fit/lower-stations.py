from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
n='H19_FrontFrame';front=sh(n);rear=sh('E19_RearBase');new=[];old=[]
def rib(poly,y,width):
 pts=[V(x,y,z) for x,z in poly];return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,width,0))
def knee(poly,x,width):
 pts=[V(x,y,z) for y,z in poly];return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(width,0,0))
def demount(name):
 b=sh(name).BoundBox;x,y,z=b.XMin,b.YMin,b.ZMin
 for t in [.19,.76]:
    xx=x+b.XLength*t
    old.append(box(xx-.006,y-1.106,45.5,3.412,b.YLength+2.212,z+2.51-45.5))
demount('WAGO615_power_0_0');demount('PBAY_F_HY')
# replace the offset diagonal leaf before relieving its inboard edge
new.append(rib([(-121,65),(-117,74),(-108,73),(-75,45),(-65,45),(-65,41),(-108,41)],-28.9,4.4).cut(sh('B19_ToolEightAnchors')))
# central HY bearer from the original transverse lower floor to two open cantilevers
new.extend([box(-71,5.2,41.2,18.6,9,3.8),box(-69.35,-22.9,41.2,3.5,46.3,3.8)])
for x in [-69.32,-56.78]:
 new.extend([box(x,5.4,43.8,3.4,8.4,31.5),box(x,-19.85,74.7,3.4,52.2,1.3),knee([(-18.8,74.7),(5.6,70.6),(13.7,70.6),(31.6,74.7),(31.6,75.4),(-18.8,75.4)],x,3.4)])
 for y in [-20.05,32.15]:new.append(box(x,y,74.8,3.4,.9,3.5))
# Pi upper bridge with full-thickness return outside the fuse's long edge
new.extend([box(-77,32.7,94.8,28,2.5,3.15),box(-77,26.1,95,2.7,8.6,2.95),box(-50.9,26.1,95,2.7,8.6,2.95)])
# G1 outward-facing five openings and two shelf brackets rooted in the negative wall
for x in [-35.4,-7.8]:
 new.extend([box(x,-102,49.3,3.5,43.6,2.7),knee([(-102,41.3),(-100.8,41.3),(-68,49.5),(-59.4,49.5),(-59.4,50.4),(-102,50.4)],x,3.5),box(x,-59.35,50.4,3.5,1.1,4.5)])
# End spring rails on the short sides leave the entire terminal face and levers open.
for x,tip in [(-40.15,-40.15),(-1.34,-2.12)]:
 new += [box(x,-72.25,49.6,1.47,8.2,14.3),box(tip,-72.25,63.18,2.26,8.2,1.25)]
new.append(box(-40.15,-72.25,49.6,40.28,8.2,2.4))
changes=[]
def change(s,tool,op,tag):
 assert not tool.isNull(),tag
 s=s.Solids[0] if len(s.Solids)==1 else s
 if len(tool.Solids)==1:tool=tool.Solids[0]
 try:result=getattr(s,op)(tool,.00001)
 except Exception as e:
    wr('boolean-diagnostic.json',dict(tag=tag,op=op,s_valid=s.isValid(),tool_valid=tool.isValid(),s_bounds=bounds(s),tool_bounds=bounds(tool),error=str(e)))
    raise
 if result.isNull() or result.Volume<.8*s.Volume:
    raise ValueError((tag,op,'failed',s.Volume,tool.Volume))
 changes.append([tag,op,len(result.Solids),result.Volume])
 wr('material-operations.json',changes)
 return result
for i,a in enumerate(old):front=change(front,a,'cut','old'+str(i))
# Combine the small replacement brackets separately before joining to the large frame.
for i,a in enumerate(new):front=change(front,a,'fuse','support'+str(i))
# Named inboard corner of diagonal and lower Pi crossbar only
front=front.cut(box(-93.24,-23.24,53.635,9,2.22,7.1)).cut(box(-73.74,25.88,94.94,22.48,2,1.55))
rear=join([rear,box(109,37.7,41.3,3.3,3.1,32.3),box(109,37.7,72.5,6.6,3.1,2.9)])
rear=rear.cut(box(113.76,37.7,51.635,1.84,3,20.73))
move('WAGO615_power_0_0',[],[-38.5,-81.5,52],90)
def record(s):return dict(valid=s.isValid(),solids=[dict(volume=round(a.Volume,3),bounds=bounds(a)) for a in s.Solids])
res={}
for name,s in [('H19_FrontFrame',front),('E19_RearBase',rear)]:
 s=s.removeSplitter();res[name]=record(s)
wr('revised-material.json',res)
for name,s in [('H19_FrontFrame',front),('E19_RearBase',rear)]:
 D.getObject(name).Shape=s.removeSplitter()
D.recompute();D.save()
