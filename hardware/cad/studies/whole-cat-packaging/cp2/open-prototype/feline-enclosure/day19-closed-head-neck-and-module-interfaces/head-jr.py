"""Both purchased 300 extensions start at their actual retained keyed mates."""
from pathlib import Path
import json,numpy as np,math
P=Path(__file__).parent
exec((P/"shoulder-layout.py").read_text().split("# Head lead routing")[0])
rows=[]
for role,station,normal,r,nets in [("yaw",[-105.970367,-8.110741,80.5],unit(-.61*Y+.7924*Z),29.5,["F_HY.out","G_AUX.4","R1.2"]),("pitch",[-111.,-51.,80.5],unit(-.25*Y+.968246*Z),26.,["F_HP.out","G_AUX.3","R2.2"])]:
    s=A(station);b=arc(s,-X,normal,r,math.pi);e=b[-1]+(246-math.pi*r)*X
    path=join(b,line(b[-1],e))
    branches=[]
    for offset in [-1,0,1]:
        direction=math.cos(.125*offset)*X+math.sin(.125*offset)*Y
        q=e+25*direction
        branches.append(dict(centreline=pack(join(line(e,q),line(q,q+17*direction))),fan=25,insulated=9,lap=8,sleeve=20,net=nets[offset+1]))
    rows.append(dict(role=role,mated_at=station,centreline=pack(path),fans=branches,raw=300,plug=12,shared=246,transport_positive_X=246-math.pi*r,return_bight=math.pi*r,inner_R=r-math.hypot(1.75,.9),assembly="Place in open shoulder before rear lip/roof and side bank",actual_slack=None))
(P/"two-head-jr-units.json").write_text(json.dumps(rows,separators=(",",":"))+"\n",encoding="utf8")

