from common import *
from importlib.machinery import SourceFileLoader
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
v=SourceFileLoader('sv',str(P/'station-survey.py')).load_module();tests={}
for i,y in enumerate([-52.5,-46,-39.5]):
 p=gp_Pnt(-16.001,y,57.5);s=BRepPrimAPI_MakeCylinder(gp_Ax2(p,gp_Dir(-1,0,0)),2.35,21.5).Shape()
 tests[str(i+1)]=v.screen(np.array([-37.501,y-2.35,55.15,-16.001,y+2.35,59.85]),['WAGO615_power_0_1'],s)
wr('front-mouths.json',dict(used_approach_mm=21.5,diameter=4.7,rows=tests,outer_box='Rejected whole 37 mm planning rectangle extends into P_REAR. Actual mouths lead through 21.5 mm opening and separate lanes beyond.'));print(tests)
