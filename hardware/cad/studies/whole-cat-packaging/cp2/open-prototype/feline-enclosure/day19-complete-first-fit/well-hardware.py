from common import *
from importlib.machinery import SourceFileLoader
sv=SourceFileLoader('survey',str(P/'station-survey.py')).load_module();d=sv.D
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.gp import gp_Pnt
q=rd(P/'well-sections.json');loft=BRepOffsetAPI_ThruSections(True,True)
for x,row in zip(q['x'],q['underside']):
 w=BRepBuilderAPI_MakePolygon()
 for y,z in [*zip(q['y'],row),*reversed(list(zip(q['y'],np.array(row)+2.4)))]:w.Add(gp_Pnt(x,y,z))
 w.Close();loft.AddWire(w.Wire())
loft.Build();a=sv.screen(np.array([-111.95,-103.1,40.44,13,-65,99]),['H19_FrontFrame','E19_ForeBase','E19_FrontShroud'],loft.Shape())
r={}
for n in ['NIGHT_INLINE_FL_W026','NIGHT_INLINE_FL_W041','I19_FuseBand_HP']:
 r[n]=sv.screen(d.bounds(n),[n],d.shape(n))
wr('well-stations.json',dict(sheet=a,shifted=r));print({k:[(m,sum(v['volume'] for v in h)) for m,h in j.items()] for k,j in [('sheet',a),*r.items()]})
