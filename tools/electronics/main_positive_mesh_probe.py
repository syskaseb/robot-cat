"""Diagnose tessellation of already verified native solids, no CAD rebuild."""
from pathlib import Path
import json
from collections import Counter
import FreeCAD,Part,MeshPart
ROOT=Path(__file__).resolve().parents[2]
CAD=ROOT/'hardware/cad/studies/main-positive-native-r1'
for key in ('Deck','MAIN'):
    s=Part.Shape();s.read(str(CAD/(key+'_WORLD.brep')))
    for lin,ang in ((.08,.25),(.04,.15)):
        shape=s
        m=MeshPart.meshFromShape(Shape=shape,LinearDeflection=lin,AngularDeflection=ang,Relative=False)
        pts,faces=m.Topology
        edges=Counter(tuple(sorted((t[i],t[(i+1)%3]))) for t in faces for i in range(3))
        bad=[dict(incidence=n,points=[list(pts[v]) for v in edge]) for edge,n in edges.items() if n!=2]
        print(json.dumps(dict(key=key,linear=lin,angular=ang,closed=m.isSolid(),components=m.countComponents(),facets=m.CountFacets,bad_edges=bad)),flush=True)
        if m.isSolid() and m.countComponents()==1:break
