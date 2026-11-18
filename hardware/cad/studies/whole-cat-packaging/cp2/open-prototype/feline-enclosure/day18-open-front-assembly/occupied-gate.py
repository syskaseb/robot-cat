"""Sample named full cable profiles against the saved common front; retain positive witnesses."""
import math,json,runpy
from pathlib import Path
import numpy as np
P=Path(__file__).parent
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"open-front.FCStd")
assert "OPEN_HANDLAY_OVER_FLOOR" in D.members
data=json.loads((P/"occupied-layout.json").read_bytes())
def unit(x):return x/np.linalg.norm(x)
def profile(line,w,t):
    pts=np.array(line);pts=pts[np.r_[True,np.linalg.norm(np.diff(pts,axis=0),axis=1)>1e-6]]
    tang=np.array([unit(q) for q in np.gradient(pts,axis=0)])
    v=np.eye(3)[np.argmin(abs(tang[0]))];out=[]
    for p,u in zip(pts,tang):
        v=unit(v-u*(v@u));h=np.cross(u,v)
        out.append([p,p-w/2*v-t/2*h,p+w/2*v-t/2*h,p+w/2*v+t/2*h,p-w/2*v+t/2*h])
    return np.array(out)
def transforms(y,p):
    a,b=map(math.radians,(y,p));yc=np.array([-130,0,127]);pc=np.array([-159,0,121])
    rz=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    ry=np.array([[math.cos(b),0,math.sin(b)],[0,1,0],[-math.sin(b),0,math.cos(b)]])
    return dict(fixed=(np.eye(3),np.zeros(3)),yaw=(rz,yc-rz@yc),pitch=(rz@ry,yc+rz@(pc-ry@pc-yc)))
members=dict(fixed=["OPEN_PORTAL_MATERIAL_SUBSET","D18C_P02_THREE_ROOT_THROUGH_VERSION","OPEN_FRONT_COWL","OPEN_AFT_COWL","OPEN_FORE_BANK_AND_DATA_FRAME",
    "Pi4B_actual_PCB","F2_COMMON_PI_BUS_PCA_RECEIVER","CF17_POWER_K1474_SEALED_BOOT_FULL","CF17_POL1992_FULL_MATED_BODY","E1_populated_prototype_board",
    "PCA9685_Adafruit815_PCB","PBAY_P_REAR","PBAY_F_AUX","PBAY_P_AUX","TTP223_touch","ReSpeakerLite_on_REMOVABLE_back","Speaker","MAX98357A_amp",
    "WAGO415_data__1_1","WAGO415_data__1_5","Motor_ATO4A_1_0","Motor_ATO4A__1_0","Motor_ATO4A_1_3","MG92B_Head_yaw","Monitor_MOD05015"],
    yaw=["HEAD_YAW_FORK_FIXED_PITCH_HOUSING","MG92B_Head_pitch"]+[n for n in D.members if n.startswith("YAW_SHAFT_FORK_POSITIVE_CROSSPIN")],
    pitch=["OPEN_SKULL_BACK","D18C_TRUE_PITCH_OPTICAL_RECEIVER","INSERT_OPTICAL_FACE"])
def test(name,pts,m):
    hits=[];pts=np.asarray(pts).reshape(-1,3)
    for k,parts in members.items():
        r,t=m[k];local=(pts-t)@r
        for part in parts:
            idx=D.inside(part,local)
            if idx is not None:hits.append(dict(part=part,point=pts[idx].tolist()))
    return dict(group=name,hits=hits)
def pair(j):
    u=unit(np.array(j["key_axis"]));b=unit(np.cross(u,[0.,0.,1.]));n=np.cross(u,b)
    return np.array([np.array(j["key_tip"])+u*x+b*y+n*z for x in [-15,-7.5,0,7.5,15] for y in [-7,0,7] for z in [-5,0,5]])
rows=[]
for y,p in [(0,0),(-20,-10),(20,10),(20,-10),(-20,10)]:
    m=transforms(y,p);R,T=m["yaw"];Q,U=m["pitch"];checks=[]
    for k in ("FFC","ToF_moving"):
        q=next(q for q in data[k] if (q["yaw"],q["pitch"])==(y,p))
        v=np.array(q["corners"]);idx=np.unique(np.linspace(0,len(v)-1,31).astype(int));checks.append(test(k,v[idx],m))
    for i,j in enumerate(data["JR_factory"]):
        pts=profile(j["centreline"],3.5,1.8)[::4].reshape(-1,3);key=pair(j)
        if i:pts=pts@R.T+T;key=key@R.T+T
        checks.append(test(j["name"],pts,m));checks.append(test(j["name"]+"_mated_pair",key,m))
    ext=next(q for q in data["extension"] if q["yaw"]==y)
    checks.append(test("JR300",profile(ext["centreline"],3.5,1.8)[::5],m))
    if y==p==0:
        for q in data["ToF_fixed"]:checks.append(test(q["wire"],profile(q["centreline"],2.1,2.1)[::4],m))
        for i,c in enumerate(ext["three_lap_centers"]):
            pts=[np.array(c)+[x,h,v] for x in [-13,-10,-4,0,4,10,13] for h in [-3,0,3] for v in [-3,0,3]]
            checks.append(test("insulated_fixed_lap_"+str(i+1),pts,m))
    for i,q in enumerate(data["ToF_header"]):
        pts=profile(q["centreline"],2.1,2.1)[::6].reshape(-1,3)
        checks.append(test("header_bound_"+str(i),pts@Q.T+U,m))
    rows.append(dict(yaw=y,pitch=p,checks=checks))
    (P/"occupied-gate.json").write_bytes((json.dumps(dict(poses=rows,scope="Five sampled configurations and named full-profile witnesses. Unsampled clearance, continuously moving free stock and source exit remain unqualified.",physical_PASS=False),indent=1)+"\n").encode())
print([(q["group"],[a["part"] for a in q["hits"]]) for q in rows[0]["checks"] if q["hits"]])
