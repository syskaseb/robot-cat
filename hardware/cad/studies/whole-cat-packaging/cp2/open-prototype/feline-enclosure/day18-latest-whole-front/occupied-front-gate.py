"""First finite material witnesses for the proposed allocations, before design review."""
from pathlib import Path
import datetime, json, math
import FreeCAD as A
import Part
import numpy as np

D=A.ActiveDocument
P=Path(__file__).parent
assert Path(D.FileName).resolve()==(P/"whole-front.FCStd").resolve()
fs=json.loads((P/"front-flex.json").read_bytes())
jrs=json.loads((P/"JR-space-plan.json").read_bytes())["units"]
V=A.Vector
members={
    "fixed":["FRONT18_LOWER_BEARING_FRAME","YAW_FIXED_OUTER_RACE_CAP","Pi_components_and_cooling","Pi4B_actual_PCB",
             "PBAY_F_AUX","PBAY_P_REAR","ReSpeakerLite_on_REMOVABLE_back","Speaker","F2_COMMON_PI_BUS_PCA_RECEIVER",
             "F3_BODY_FORE_POS","F3_BODY_FORE_NEG","FRONT18_FORE_POS_PANEL","FRONT18_FORE_NEG_PANEL",
             "Motor_ATO4A_1_0","Motor_ATO4A_1_3","MG92B_Head_yaw"],
    "yaw":["HEAD_YAW_FORK_FIXED_PITCH_HOUSING","MG92B_Head_pitch","YAW_SHAFT_FORK_POSITIVE_CROSSPIN_full_screw",
           "YAW_SHAFT_FORK_POSITIVE_CROSSPIN_fullnut","YAW_SHAFT_FORK_POSITIVE_CROSSPIN_headwasher",
           "YAW_SHAFT_FORK_POSITIVE_CROSSPIN_nutwasher"],
    "pitch":["F3_HEAD_FRONT","F3_HEAD_BACK","D18C_TRUE_PITCH_OPTICAL_RECEIVER"]}
cache={}
for group,names in members.items():
    for n in names:
        sh=D.getObject(n).Shape
        b=sh.BoundBox
        cache[n]=(sh,np.array([b.XMin,b.YMin,b.ZMin]),np.array([b.XMax,b.YMax,b.ZMax]))
res=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
         method="Sampled full rectangular profiles vs actual CAD material. One inside witness rejects this placement. A miss is inconclusive. Pi cooling is conservative reserved space. JR engagement/storage and optical datums are provisional.",
         pose_results=[],fork_and_full_pin=[],physical_PASS=False)
def save():
    tmp=P/"occupied-front-gate.partial"
    tmp.write_bytes((json.dumps(res,indent=1)+"\n").encode())
    tmp.replace(P/"occupied-front-gate.json")
def matrix(y,p):
    a,b=map(math.radians,(y,p))
    rz=np.array([[math.cos(a),-math.sin(a),0],[math.sin(a),math.cos(a),0],[0,0,1.]])
    ry=np.array([[math.cos(b),0,math.sin(b)],[0,1,0],[-math.sin(b),0,math.cos(b)]])
    cy=np.array([-130.,0,127.]);cp=np.array([-159.,0,121.])
    return {"fixed":(np.eye(3),np.zeros(3)),"yaw":(rz,cy-rz@cy),"pitch":(rz@ry,cy+rz@(cp-ry@cp-cy))}
def test(tag,pts,pose,own):
    hits=[]
    for group,names in members.items():
        R,T=pose[group]
        local=(pts-T)@R
        for n in names:
            shape,low,high=cache[n]
            mask=np.flatnonzero(np.all((local>=low)&(local<=high),axis=1))
            for i in mask:
                if shape.isInside(V(*local[i]),1e-6,False):
                    hits.append(dict(part=n,point=pts[i].tolist(),motion_owner=group))
                    break
    return dict(group=tag,ownership=own,points=len(pts),penetration_witnesses=hits)
frame=cache["FRONT18_LOWER_BEARING_FRAME"][0]
for yaw in [-20,0,20]:
    for n in members["yaw"]:
        if n=="MG92B_Head_pitch":continue
        shape=cache[n][0].copy();shape.rotate(V(-130,0,127),V(0,0,1),yaw)
        common=shape.common(frame)
        res["fork_and_full_pin"].append(dict(yaw=yaw,part=n,common=common.Volume,valid=common.isValid(),gap=shape.distToShape(frame)[0]))
save()
for yaw,pitch in [(0,0),(-20,-10),(20,10),(-20,10),(20,-10)]:
    pose=matrix(yaw,pitch)
    f=next(q for q in fs["FFC"] if (q["yaw"],q["pitch"])==(yaw,pitch))
    # Limit the first test to neck/shoulder section, away from mating contact faces.
    pts=np.array(f["corners"])[::5].reshape(-1,3)
    pts=pts[(pts[:,0]>-185)&(pts[:,0]<-78)]
    row=[test("FFC200",pts,pose,"changes shape at each pose")]
    t=next(q for q in fs["ToF"] if (q["yaw"],q["pitch"])==(yaw,pitch))
    centers=np.array(t["centreline"])
    h=centers[-1]-centers[0];h[2]=0;h/=np.linalg.norm(h)
    n=np.array([-h[1],h[0],0])
    # Include inside both long straight segments, rather than only their endpoints.
    stations=np.vstack([np.linspace(centers[0],centers[1],14),centers[1:-1:5],np.linspace(centers[-2],centers[-1],12)])
    pts=np.vstack([stations+5.2*a*n+np.array([0,0,1.45*b]) for a in [-1,1] for b in [-1,1]])
    row.append(test("ToF4 moving span",pts,pose,"four HELU conductors in the moving group"))
    for j in jrs:
        c=np.array(j["center"])
        axis=np.array(j["normal"]);along=np.array([1.,0,0]);across=np.cross(axis,along)
        phases=np.arange(0,2*math.pi,math.pi/12)
        radii=np.array([math.cos(a)*along+math.sin(a)*across for a in phases])
        # Width across the loop plane, thickness radially: inner radius 22.6.
        pts=np.vstack([c+(23.5+a*.9)*radii+b*1.75*axis for a in (-1,1) for b in (-1,1)])
        if j["motion"]=="yaw":
            R,T=pose["yaw"];pts=pts@R.T+T
        row.append(test(j["name"],pts,pose,j["motion"]))
    res["pose_results"].append(dict(yaw=yaw,pitch=pitch,groups=row))
    save()
print("FIRST OCCUPIED GATE",[(r["yaw"],r["pitch"],[len(g["penetration_witnesses"]) for g in r["groups"]]) for r in res["pose_results"]])
