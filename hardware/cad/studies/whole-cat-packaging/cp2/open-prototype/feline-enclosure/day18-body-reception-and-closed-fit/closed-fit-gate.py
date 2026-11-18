"""Check the revised aperture, fixed throat and actual body fields in the affected interfaces."""
from pathlib import Path
import json,runpy,ast,math
import numpy as np
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
P=Path(__file__).parent;D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"body-reception.FCStd")
lib=P.parent/"day18-open-front-assembly"/"occupied-gate.py"
for f in ast.parse(lib.read_bytes()).body:
    if isinstance(f,ast.FunctionDef) and f.name in ("unit","profile","transforms"):exec(compile(ast.Module([f],type_ignores=[]),str(lib),"exec"))
chest="BR_CLOSED_CHEST_LIP";back="BR_PARTED_SKULL_BACK";mask="BR_COMMON_OPTICAL_MASK"
r=json.loads((P/"flank-reception.json").read_bytes());ffc=json.loads((lib.parent/"occupied-layout.json").read_bytes())["FFC"]
fan=json.loads((P/"jp3-shared-fan.json").read_bytes())["rows"]
res=dict(poses=[],static=[],regional=[],physical_PASS=False)
def save():(P/"closed-fit-gate.json").write_bytes((json.dumps(res,indent=1)+"\n").encode())
def probe(tag,pts,y,p,dk):
    pts=np.asarray(pts).reshape(-1,3);mov=transforms(y,p);hits={}
    for owner,ns in dk.items():
        R,T=mov[owner];local=(pts-T)@R
        for n in ns:
            i=D.inside(n,local)
            if i is not None:hits[n]=dict(point=pts[i].tolist(),sample=int(i))
    return dict(name=tag,hits=hits)
changed=dict(fixed=[chest,"BR_FLANK_SUPPORT_SUBSET"],pitch=[back,"BR_PITCH_RECEIVER_AND_GRIP"])
for y,p in [(0,0),(-20,-10),(20,10),(-20,10),(20,-10)]:
    m=transforms(y,p);rows=[]
    fi=next(q for q in ffc if q["yaw"]==y and q["pitch"]==p);t=next(q for q in r["ToF_move"] if q["yaw"]==y and q["pitch"]==p)
    for n,pts in [("FFC200 full corners",np.array(fi["corners"])[::4]),("ToF moving",profile(t["centreline"],4.9,4.9)[::4]),
                  ("pitch250",profile(next(q for q in r["pitch"] if q["yaw"]==y)["centreline"],3.5,1.8)[::4])]:
        rows.append(probe(n,pts,y,p,changed))
    res["poses"].append(dict(yaw=y,pitch=p,fields=rows));save()
for n,path,w,h in [("static300",r["extension"]["centreline"],3.5,1.8)]+[(j["wire"],j["centreline"],2.1,2.1) for j in fan]:
    res["regional"].append(probe(n,profile(path,w,h)[::4],0,0,changed));save()
# Full rigid source parts against the changed stationary and moving covers,
# independently of the terminal distinction and the flexible field sampling.
for a,b in [(mask,"Camera3_NoIR_Wide"),(mask,"VL53L5CX"),(mask,"BR_PITCH_RECEIVER_AND_GRIP"),(chest,"MG92B_Head_yaw"),(chest,"HEAD_YAW_FORK_FIXED_PITCH_HOUSING"),
            (chest,"BR_FLANK_HP_PAIR"),(chest,"BR_FLANK_SUPPORT_SUBSET"),(back,"BR_PITCH_RECEIVER_AND_GRIP"),("BR_ROUNDED_RUMP","Speaker"),("BR_ROUNDED_RUMP","ReSpeakerLite_on_REMOVABLE_back"),("BR_ROUNDED_RUMP","INSERT_AUDIO_USB_C_FULL_MATE_FIELD")]:
    res["static"].append(dict(a=a,b=b,**D.common(a,b)));save()
