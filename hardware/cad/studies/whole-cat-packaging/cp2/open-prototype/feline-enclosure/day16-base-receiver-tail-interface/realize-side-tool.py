"""Apply once AFTER build-interface.py on its own source-derived model. Same six joints; no new layout.
Final saved FCStd is authoritative. Do not run on an unrelated document.
"""
import FreeCAD as A,Part,math
V=A.Vector;D=A.ActiveDocument;ports=[]
for i,(x,y) in enumerate([(x,y) for x in [-70,70,145] for y in [-72,72]]):
 ports.append(Part.makeBox(32.4,45,2.75,V(x-16.2,70 if y>0 else -115,40.87)))
 r=5.5/math.sqrt(3);vs=[V(x+r*math.cos(math.pi/6+k*math.pi/3),y+r*math.sin(math.pi/6+k*math.pi/3),41.12) for k in range(6)]
 head=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,2));o=D.getObject('BASE'+str(i)+'_M3x10_FULL');o.Shape=head.fuse(Part.makeCylinder(1.5,10,V(x,y,43.12)));o.Label='ISO4017 M3x10 FULL HEX AF5.5 k2 NEEDED_UNCONFIRMED'
cut=ports[0]
for p in ports[1:]:cut=cut.fuse(p)
for o in D.Objects:
 if o.Name.startswith('CLOSED_BODY_') or o.Name in ['P02_front_deck','P03_rear_deck_integrated_load_yoke']:o.Shape=o.Shape.cut(cut)
D.recompute()
