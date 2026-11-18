"""Sections through the bought equipment, floor and receiver at the front stations."""
from pathlib import Path
import json,runpy,sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.GeomAbs import GeomAbs_Line
from OCP.gp import gp_Pln,gp_Pnt,gp_Dir
P=Path(__file__).parent
trial="--trial" in sys.argv
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"body-reception.FCStd" if trial else P.parent/"day18-open-front-assembly"/"open-front.FCStd")
groups={"powłoka":(["FIT_FRONT_COWL","FIT_AFT_COWL","OPEN_SKULL_BACK","INSERT_OPTICAL_FACE"],"#82858c"),
    "podłoga / bank":(["FIT_FLOOR_AND_BATTERY_MONITOR"],"#467777"),
    "nośnik Pi–PCA":(["F2_COMMON_PI_BUS_PCA_RECEIVER"],"#be4538"),
    "gimbal i stal":([n for n in D.members if n.startswith(("MG92B_Head_","YAW_SHAFT_FORK_POSITIVE_CROSSPIN","HEAD_YAW_FORK_FIXED","Yaw608_","YAW_HORN_")) and "space" not in n],"#945b2c"),
    "wyposażenie":(["Pi4B_actual_PCB","PCA9685_Adafruit815_PCB","E1_populated_prototype_board","CF17_POL1992_FULL_MATED_BODY","PBAY_P_REAR","PBAY_F_AUX","PBAY_P_AUX","TTP223_touch","Battery_GEA223S30X6GT","F0_FHAC0002_30A","BUS25514_installed"]+[n for n in D.members if n.startswith(("Motor_ATO4A_","WAGO415_data"))],"#424958")}
if trial:
    groups["gniazda i złącza"]=(["BR_PAIR_HY","BR_PAIR_HP","BR_LAPS","BR_RECEIVER_HARD_MATERIAL","BR_PITCH_RECEIVER_AND_GRIP"],"#a15696")
    data=json.loads((P/"reception-layout.json").read_bytes())
    old=json.loads((P.parent/"day18-open-front-assembly"/"occupied-layout.json").read_bytes())
    select=lambda rows:next(q for q in rows if q.get("yaw",0)==q.get("pitch",0)==0)
    flex={"JR 250 + 250 + 300":([data["yaw"]["centreline"],select(data["pitch"])["centreline"],data["extension"]["centreline"]]+[q["centreline"] for q in data["extension"]["fans"]],3.5,"#d87d12"),
          "ToF 2×2 / odnogi":([select(data["ToF_move"])["centreline"]]+[q["centreline"] for q in data["ToF_fixed"]+data["ToF_head"]],4.9,"#359048"),
          "FFC 16,8 × 1,8":([np.array(select(old["FFC"])["corners"]).mean(axis=1)],16.8,"#3762b5")}
def section(n,axis,pos):
    b=D.bounds(n)
    if pos<b[axis] or pos>b[axis+3]:return []
    p=np.zeros(3);p[axis]=pos;dim=[i for i in range(3) if i!=axis]
    pl=gp_Pln(gp_Pnt(*p),gp_Dir(*np.eye(3)[axis]))
    cut=BRepAlgoAPI_Section(D.shape(n),pl,True)
    edges=TopExp_Explorer(cut.Shape(),TopAbs_EDGE);out=[]
    while edges.More():
        c=BRepAdaptor_Curve(TopoDS.Edge(edges.Current()))
        pts=[c.Value(t).Coord() for t in np.linspace(c.FirstParameter(),c.LastParameter(),2 if c.GetType()==GeomAbs_Line else 23)]
        out.append(np.array(pts)[:,dim]);edges.Next()
    return out
fig,axes=plt.subplots(2,2,figsize=(12,8))
for ax,(axis,pos) in zip(axes.flat,[(2,131.5),(2,153.7),(0,-91),(0,-51)]):
    for names,color in groups.values():
        for n in names:
            lines=section(n,axis,pos)
            if lines:ax.add_collection(LineCollection(lines,colors=color,linewidths=.85))
    if trial:
        dims=[i for i in range(3) if i!=axis]
        for paths,width,color in flex.values():
            for path in paths:
                pts=np.array(path)
                for u,v in zip(pts,pts[1:]):
                    if min(u[axis],v[axis])-width/2<=pos<=max(u[axis],v[axis])+width/2:
                        ax.plot([u[dims[0]],v[dims[0]]],[u[dims[1]],v[dims[1]]],c=color,lw=1.45)
    ax.set_title(("Z" if axis==2 else "X")+f" = {pos} mm",loc="left");ax.set_xlabel("X [mm]" if axis==2 else "Y [mm]");ax.set_ylabel("Y [mm]" if axis==2 else "Z [mm]")
    ax.set_xlim((-180,70) if axis==2 else (-98,98));ax.set_ylim((-100,100) if axis==2 else (33,199));ax.set_aspect("equal");ax.grid(True,lw=.3)
colors={name:entry[-1] for name,entry in groups.items()}
if trial:colors.update({n:q[-1] for n,q in flex.items()})
fig.legend([Line2D([],[],color=c) for c in colors.values()],list(colors),loc="lower center",ncol=4)
fig.tight_layout(rect=(0,.07,1,1));fig.savefig(P/("reception-sections.png" if trial else "source-sections.png"),dpi=140)
