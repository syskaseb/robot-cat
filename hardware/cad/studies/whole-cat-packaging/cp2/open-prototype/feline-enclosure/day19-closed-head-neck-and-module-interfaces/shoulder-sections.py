"""Native sections and sampled occupied wire layers in the moving and stationary receiver planes."""
from pathlib import Path
import runpy,json,numpy as np,ast,math
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pnt,gp_Dir,gp_Pln
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Line
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
P=Path(__file__).parent
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"whole-cat19C.FCStd")
source=P.parent/"day19-common-floor-and-bundle-assembly"/"sections.py"
for fn in ast.parse(source.read_bytes()).body:
    if isinstance(fn,ast.FunctionDef) and fn.name=="sections":exec(compile(ast.Module([fn],type_ignores=[]),str(source),"exec"))
lay=json.loads((P/"side-return.json").read_bytes())
ffc=json.loads((P.parent/"day18-open-front-assembly/occupied-layout.json").read_bytes())["FFC"]
groups=[("stałe podparcie / osłona",["C19_ShoulderFloor","C19_FixedShoulderShell"],"#186e65"),("ruchoma głowa",["C19_FaceAndEars","C19_OpenRearHelmet","C19_MovingOpticsCarrier","C19_Ear_1","C19_Ear_2"],"#58585f"),("pełny mechanizm / moduły",["BR_FINISHED_YAW_SADDLE","MG92B_Head_yaw","MG92B_Head_pitch","Pi4B_actual_PCB","PITCH_SHAFT_FRAME_POSITIVE_CROSSPIN_full_screw","YAW_SHAFT_FORK_POSITIVE_CROSSPIN_full_screw","BR_PAIR_HY","BR_FLANK_HP_PAIR","BR_FLANK_THREE_LAPS","PCA9685_Adafruit815_PCB"],"#98435c")]
fig,axs=plt.subplots(2,2,figsize=(12.5,9))
for ax,x in zip(axs.flat,[-146,-130,-100,-56]):
    for title,ns,col in groups:
        lines=[]
        for n in ns:
            b=D.bounds(n)
            if b[0]-1e-6<=x<=b[3]+1e-6:lines+=sections(n,0,x)
        if lines:ax.add_collection(LineCollection(lines,colors=col,linewidths=1.1))
    for q in lay["motion"]:
        ps=np.array(q["centreline"]);ss=ps[np.abs(ps[:,0]-x)<=1.2]
        ax.scatter(ss[:,1],ss[:,2],s=6,c="#e89c26",alpha=.55)
    for q in ffc:
        ps=np.array(q["corners"]).reshape(-1,3);ss=ps[np.abs(ps[:,0]-x)<=1.5]
        ax.scatter(ss[:,1],ss[:,2],s=4,c="#7150a4",alpha=.55)
    if x in [-146,-56]:
        g=lay["head_receiver" if x==-146 else "fixed_receiver"];ax.plot(g[1],g[2],"k+",ms=12,mew=1.4)
    ax.set(xlim=(-116,116),ylim=(36,234),xlabel="Y [mm]",ylabel="Z [mm]",title=f"X = {x} mm");ax.set_aspect("equal");ax.grid(lw=.3)
fig.legend([plt.Line2D([0],[0],color=c) for c in [g[2] for g in groups]+["#e89c26","#7150a4"]],[g[0] for g in groups]+["ToF · 9 póz","FFC · profile taśmy"],loc="lower center",ncol=5)
fig.tight_layout(rect=(0,.045,1,1));fig.savefig(P/"critical-sections.png",dpi=145)

