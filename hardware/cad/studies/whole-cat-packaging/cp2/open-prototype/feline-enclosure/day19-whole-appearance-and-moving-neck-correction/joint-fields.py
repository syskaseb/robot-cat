"""Sample material of four round jackets in the two guides and crossing the moving shell seams."""
from pathlib import Path
import numpy as np,json,ast,math,hashlib
import runpy
P=Path(__file__).parent;C=P.parent/"day19-closed-head-neck-and-module-interfaces"
src=(C/"changed-seam.py").read_text()
exec(src[:src.index("lay=json.loads")].replace('P/"whole-cat19C.FCStd"','P/"whole-cat19D.FCStd"'))
lay=json.loads((P/"whole-lay.json").read_bytes())
ffc=json.loads((source/"occupied-layout.json").read_bytes())["FFC"]
p250=json.loads((old/"yaw-laid-factory.json").read_bytes())["rows"]
parts={"fixed":["D19D_FrontFloor","D19D_Shoulder","D19D_RearShell","D19D_YawMatedPair","Pi4B_actual_PCB","BUS25514_installed","Speaker","ReSpeakerLite_on_REMOVABLE_back","BR_FLANK_THREE_LAPS","PBAY_F_HY","PBAY_F_TY","MG92B_Head_yaw","BR_FLANK_HP_PAIR"],"yaw":["D19D_YawHood","D19D_YawSaddle","MG92B_Head_pitch","YAW_SHAFT_FORK_POSITIVE_CROSSPIN_full_screw"],"pitch":["D19D_OpticsCarrier","D19D_Face","D19D_PitchBack","PITCH_SHAFT_FRAME_POSITIVE_CROSSPIN_full_screw"]}
exec(src[src.index("meshcache="):src.index("for y in (-20")])
def circle(path):
    c=np.array(path);u=np.gradient(c,axis=0);u/=np.linalg.norm(u,axis=1)[:,None]
    v=np.eye(3)[np.argmin(abs(u),axis=1)];v-=u*(v*u).sum(axis=1)[:,None];v/=np.linalg.norm(v,axis=1)[:,None];w=np.cross(u,v)
    return np.array([c]+[c+1.05*(math.cos(a)*v+math.sin(a)*w) for a in np.arange(12)*math.tau/12]).reshape(-1,3)
radii=[]
def radius(path):
    pts=np.asarray(path);d=np.diff(pts,axis=0);pts=pts[np.r_[True,np.linalg.norm(d,axis=1)>.008]]
    # Circumradius of each consecutive non-collinear triple, minus jacket radius.
    a,b=np.diff(pts,axis=0)[:-1],np.diff(pts,axis=0)[1:];cross=np.linalg.norm(np.cross(a,b),axis=1)
    k=cross>1e-5
    return float(min(np.linalg.norm(a[k],axis=1)*np.linalg.norm(b[k],axis=1)*np.linalg.norm(a[k]+b[k],axis=1)/(2*cross[k]))-1.05)
for q in lay["motion"]:
    y,p=q["yaw"],q["pitch"];R,T=transforms(y,p)["pitch"]
    for i,cc in enumerate(q["cores"]):
        screen("moving "+str(i),y,p,circle(cc));radii.append(dict(yaw=y,pitch=p,core=i+1,inner_R=radius(cc),head_join=float(np.linalg.norm(np.asarray(cc[0])-R@np.asarray(lay["head"][i][-1])-T)),body_join=float(np.linalg.norm(np.asarray(cc[-1])-lay["fixed"][i]["centreline"][0]))))
        screen("head "+str(i),y,p,circle(lay["head"][i][2:])@R.T+T)
        screen("body "+str(i),y,p,circle(lay["fixed"][i]["centreline"][:-2]))
    screen("FFC190",y,p,next(q["corners"] for q in ffc if q["yaw"]==y and q["pitch"]==p))
    screen("pitch MG250",y,p,profile(next(q["centreline"] for q in p250 if q["yaw"]==y),3.5,1.8))
    screen("yaw MG250",y,p,profile(lay["yaw_factory"]["centreline"],3.5,1.8))
    for jr in lay["jr"]:
        screen(jr["role"]+" JR300",y,p,profile(jr["centreline"],3.5,1.8))
        for i,f in enumerate(jr["fans"]):screen(jr["role"]+" fan "+str(i),y,p,profile(f["centreline"],1.8,1.8))
out=dict(native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),rows=rows,radii=radii,fixed_inner_R=[radius(f["centreline"]) for f in lay["fixed"]],head_inner_R=[radius(q) for q in lay["head"]],physical_PASS=False)
(P/"joint-fields.json").write_bytes((json.dumps(out,indent=1)+"\n").encode())
from collections import Counter
print(Counter((r["field"],h["part"]) for r in rows for h in r["hits"]).most_common(35))

