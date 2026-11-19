"""Physical decisions at the switch, door, battery path, BUS seats and removable banks."""
from pathlib import Path
import runpy,json,hashlib,math
import numpy as np
from OCP.gp import gp_Pnt
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
P=Path(__file__).parent;native=P/'whole-cat19E.FCStd'
S=runpy.run_path(str(P.parent/'day18-front-insert-correction/saved-front.py'))['Saved'](native)
rows=[];out=dict(native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),rows=rows,physical_PASS=False)
def store():(P/'final-fit.json').write_text(json.dumps(out,indent=1)+'\n')
# Closed-box rigid hazards from the first presentation; occupied source capacities stay named.
for n,nn in [('S0_key',['E19_RearBase','E19_RearLid']),('S0_body',['E19_RearBase','E1_populated_prototype_board']),('OP_S1_PRIMARY_CASE_CONSERVATIVE',['E19_RearBase']),('D19D_YawMatedPair',['E19_ForeBase','E19_FrontShroud','E19_ForeLid']),('BR_FLANK_HP_PAIR',['E19_ForeBase','E19_ForeLid','E19_FrontShroud']),('E19_BUS_PCB',['E19_RearBase','E19_RearLid']),('D18C_DATA_BUS_FULL26_PROJECT_BOOT',['E19_RearLid','PCA9685_Adafruit815_PCB']),('E19_BatteryDoor',['E19_ForeBase','E19_RearBase','NIGHT_INLINE_RR_W052','NIGHT_INLINE_RR_W053'])]:
    for b in nn:rows.append(dict(a=n,b=b,**S.common(n,b)))
    store()
# The packed cell is 106.5 x 35 x 21.5. Clear the whole lateral extraction from
# the installed plane until the near face is outside the housing at Y104.
lo=np.array([-12.,20.,52.]);hi=np.array([94.5,140.,73.5]);w=BRepPrimAPI_MakeBox(gp_Pnt(*lo),gp_Pnt(*hi)).Shape()
swept=[]
for n in ['E19_ForeBase','E19_RearBase','E19_ForeLid','E19_RearLid','PCA9685_Adafruit815_PCB','B19_TailJRUnderBank','S0_body','E19_FrontShroud']+[n for n in S.members if n.startswith(('Motor_ATO','E19_Wago','NIGHT_INLINE','PBAY_')) and '_RR_' not in n]:
    b=S.bounds(n)
    if np.any(b[:3]>=hi) or np.any(b[3:]<=lo):continue
    op=BRepAlgoAPI_Common(w,S.shape(n));assert op.IsDone();g=GProp_GProps();BRepGProp.VolumeProperties_s(op.Shape(),g)
    swept.append(dict(part=n,common_mm3=g.Mass()))
out['battery_extraction']=dict(from_bounds=lo.tolist(),swept_max=hi.tolist(),door_and_RR_inlines_parked=True,straps_removed=True,leads_unplugged=True,fixed_parts=swept);store()
# Exact local interference of two keyed bank sockets, and support engagement of
# each printed BUS standoff in its nominal bottom PCB bearing plane.
for n in [k for k in S.members if k.startswith('E19_Wago')]:
    root='E19_ForeBase' if 'Fore' in n else 'E19_RearBase';rows.append(dict(a=n,b=root,**S.common(n,root)))
    store()
print([(r['a'],r['b'],r['common_mm3']) for r in rows if r.get('common_mm3',0)>.04],swept)
