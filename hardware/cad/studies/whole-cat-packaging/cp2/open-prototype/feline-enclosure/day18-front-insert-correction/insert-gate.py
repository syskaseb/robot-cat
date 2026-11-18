"""Bounded occupied-front gate on the saved CAD solids, with exact inside witnesses."""
import json,math,runpy
from pathlib import Path
import numpy as np
P=Path(__file__).parent
D=runpy.run_path(str(P/"saved-front.py"))["Saved"](P/"front-insert.FCStd")
data=json.loads((P/"insert-regions.json").read_bytes())
ext=json.loads((P/"connected-JR300.json").read_bytes())["poses"]
def unit(v):return v/np.linalg.norm(v)
def motion(y,p):
    a,b=map(math.radians,(y,p))
    rz=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1]])
    ry=np.array([[math.cos(b),0,math.sin(b)],[0,1,0],[-math.sin(b),0,math.cos(b)]])
    pc=np.array([-159.,0,121.]);yc=np.array([-130.,0,127.])
    return {"fixed":(np.eye(3),np.zeros(3)),"yaw":(rz,yc-rz@yc),"pitch":(rz@ry,yc+rz@(pc-ry@pc-yc))}
members={"fixed":["INSERT_FRONT_NEG","INSERT_FRONT_POS","FRONT18_LOWER_BEARING_FRAME","MG92B_Head_yaw","Speaker","ReSpeakerLite_on_REMOVABLE_back",
                  "Pi_components_and_cooling","Pi4B_actual_PCB","F2_COMMON_PI_BUS_PCA_RECEIVER","PBAY_P_REAR","PBAY_F_AUX","PBAY_P_AUX",
                  "CF17_POWER_K1474_SEALED_BOOT_FULL","CF17_POL1992_FULL_MATED_BODY","TTP223_touch","PCA9685_Adafruit815_PCB","E1_populated_prototype_board",
                  "Motor_ATO4A_1_3","Motor_ATO4A__1_3","Motor_ATO4A_1_0","FRONT18_FORE_NEG_PANEL","FRONT18_FORE_POS_PANEL",
                  "WAGO415_data__1_1","WAGO415_data__1_5","WAGO415_data__1_6","INSERT_AUDIO_USB_C_FULL_MATE_FIELD"],
         "yaw":["HEAD_YAW_FORK_FIXED_PITCH_HOUSING","MG92B_Head_pitch","YAW_SHAFT_FORK_POSITIVE_CROSSPIN_full_screw",
                "YAW_SHAFT_FORK_POSITIVE_CROSSPIN_fullnut","YAW_SHAFT_FORK_POSITIVE_CROSSPIN_headwasher","YAW_SHAFT_FORK_POSITIVE_CROSSPIN_nutwasher"],
         "pitch":["INSERT_HEAD_BACK","D18C_TRUE_PITCH_OPTICAL_RECEIVER"]}
# The trial profile is flat. Parallel-transport the width plane through the
# bends; this produces one representative lay and does not fix flexible wire
# in space across different poses.
def profile(line,w,t):
    line=np.array(line)
    keep=np.r_[True,np.linalg.norm(np.diff(line,axis=0),axis=1)>1e-5]
    line=line[keep]
    tan=np.array([unit(v) for v in np.gradient(line,axis=0)])
    seed=np.eye(3)[np.argmin(abs(tan[0]))]
    W=unit(seed-tan[0]*(seed@tan[0]))
    corners=[]
    for q,v in zip(line,tan):
        W=unit(W-v*(v@W));N=np.cross(v,W)
        corners.append([q+a*W*w/2+b*N*t/2 for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]])
    return np.array(corners)
def test(name,pts,M):
    pts=np.asarray(pts).reshape(-1,3)
    hits=[]
    for owner,names in members.items():
        r,t=M[owner];local=(pts-t)@r
        for n in names:
            idx=D.inside(n,local)
            if idx is not None:hits.append(dict(part=n,point=pts[idx].tolist()))
    return dict(group=name,points=len(pts),hits=hits)
rows=[]
for y,p in [(0,0),(-20,-10),(20,10),(-20,10),(20,-10)]:
    m=motion(y,p);R,T=m["yaw"];Q,U=m["pitch"]
    fo=next(q for q in data["FFC"] if (q["yaw"],q["pitch"])==(y,p))
    to=next(q for q in data["ToF_moving"] if (q["yaw"],q["pitch"])==(y,p))
    rr=[test("FFC200",np.array(fo["corners"])[::3],m),test("ToF_moving",np.array(to["corners"])[::3],m)]
    for idx,j in enumerate(data["JR_factory"]):
        pts=profile(j["centreline"],3.5,1.8)[::3].reshape(-1,3)
        if idx:pts=pts@R.T+T
        rr.append(test(j["name"],pts,m))
    j=next(q for q in ext if q["yaw"]==y);rr.append(test("extension_300",profile(j["centreline"],3.5,1.8)[::3],m))
    # Include the entire project mating-pair housing, not just the cable point.
    jp=data["JR_factory"][1];axis=np.array(jp["key_axis"]);tip=np.array(jp["key_tip"])
    across=unit(np.cross(axis,[0,0,1]));up=unit(np.cross(across,axis))
    pts=np.array([tip+a*axis+b*across+c*up for a in np.linspace(-15,15,7) for b in [-7,0,7] for c in [-5,0,5]])
    rr.append(test("keyed_pair_30x14x10",pts@R.T+T,m))
    for q in data["ToF_header"]:
        pts=profile(q["centreline"],2.1,2.1)[::4].reshape(-1,3)
        rr.append(test("ToF_header_corner",pts@Q.T+U,m))
    if y==p==0:
        for q in data["ToF_fixed"]:rr.append(test("fixed_"+q["wire"],profile(q["centreline"],2.1,2.1)[::3],m))
    rows.append(dict(yaw=y,pitch=p,groups=rr))
    (P/"occupied-insert-check.json").write_bytes((json.dumps(dict(poses=rows,method="Actual BRep point-in-material or installation-field witnesses on full profiles; misses do not prove clearance. Header-corner samples bound source land choices, not four measured supplier ports.",physical_PASS=False),indent=1)+"\n").encode())
print([(q["group"],[i["part"] for i in q["hits"]]) for q in rows[0]["groups"]])
