"""Retain a measured portion of the intact factory lead on the yaw owner before the moving span."""
from pathlib import Path
import json,math,ast
import numpy as np
P=Path(__file__).parent;r=json.loads((P/"flank-reception.json").read_bytes())
X,Y,Z=np.eye(3);C=np.array([-130.,0,127]);PC=np.array([-159.,0,121.])
for f in ast.parse((P/"flank-reception.py").read_bytes()).body:
    if isinstance(f,ast.FunctionDef) and f.name in {"unit","arc","line","join","pack","pose","reach"}:exec(compile(ast.Module([f],type_ignores=[]),str(P),"exec"))
a=5*np.pi/6;rr=25.;S=np.array([-159.,-43.8,131.5])
# Seat the arc on the existing lower flank of the fork. Its outlet is
# coplanar with a 127.3 mm saddle plus 2.05 mm of field and lay allowance.
clock=math.asin((131.5-129.35)/(rr*(1-np.cos(a))))
direction=np.cos(clock)*X-np.sin(clock)*Z
fixed=arc(S,-Y,direction,rr,a);t=-np.cos(a)*Y+np.sin(a)*direction
B=np.array([-81.,-51.,80.5]);key=B-15*X
rows=[]
for y in (-20,-10,0,10,20):
    R,T=pose(y,0);q=fixed@R.T+T;v=R@t
    angle=math.acos(X@v);first=arc(q[-1],v,unit(X-v*(X@v)),rr,angle)
    wire,rb,la,lb=reach(join(q,first),B,223.55,rr*(a+angle))
    rows.append(dict(yaw=y,centreline=pack(wire),body_pair=pack(key),case_free_stub=11.45,case_to_yaw_grip=rr*a,yaw_grip_to_body=223.55-rr*a,proper_key=15,total=250.,
        grip_center=pack(q[-1]),tangent=pack(v),minimum_inner_R=min(rr,rb)-math.hypot(1.75,.9),straight_legs=[la,lb]))
(P/"yaw-laid-factory.json").write_bytes((json.dumps(dict(rows=rows,neutral_arc=pack(fixed),neutral_tangent=pack(t),unchanged_body_HP=pack(key),physical_PASS=False),separators=(",",":"))+"\n").encode())
