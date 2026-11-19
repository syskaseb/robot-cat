from pathlib import Path
import runpy,json,numpy as np,ast,math
P=Path(__file__).parent;C=P.parent/"day19-closed-head-neck-and-module-interfaces"
src=(C/"shoulder-sections.py").read_text()
exec(src[:src.index("lay=json.loads")].replace("whole-cat19C.FCStd","whole-cat19D.FCStd"))
lay=json.loads((P/"whole-lay.json").read_bytes());ffc=json.loads((P.parent/"day18-open-front-assembly/occupied-layout.json").read_bytes())["FFC"]
groups=[("bark / podłoga",["D19D_FrontFloor","D19D_Shoulder","D19D_RearShell"],"#187461"),("czaszka / nośnik pitch",["D19D_Face","D19D_PitchBack","D19D_OpticsCarrier"],"#50515c"),("osłona i siodło yaw",["D19D_YawHood","D19D_YawSaddle"],"#205fa7"),("pełne części i mocowania",["MG92B_Head_yaw","MG92B_Head_pitch","PITCH_SHAFT_FRAME_POSITIVE_CROSSPIN_full_screw","YAW_SHAFT_FORK_POSITIVE_CROSSPIN_full_screw","BR_FLANK_HP_PAIR","D19D_YawMatedPair","PBAY_F_HY","Pi4B_actual_PCB","BUS25514_installed","Camera3_NoIR_Wide","VL53L5CX"],"#9b3c50")]
pitch=json.loads((P.parent/"day18-body-reception-and-closed-fit/yaw-laid-factory.json").read_bytes())["rows"]
lines=[("ToF Ø2,1 · 4 żyły / 9 póz",[c for q in lay["motion"] for c in q["cores"]]+lay["head"]+[f["centreline"] for f in lay["fixed"]],"#de8c17"),("FFC190",[q["corners"] for q in ffc],"#8452ab"),("MG250 / JR300",[lay["yaw_factory"]["centreline"]]+[q["centreline"] for q in pitch]+[j["centreline"] for j in lay["jr"]]+[f["centreline"] for j in lay["jr"] for f in j["fans"]],"#ce4636")]
fig,axs=plt.subplots(2,2,figsize=(13,9))
for ax,x in zip(axs.flat,[-146,-129,-106,-56]):
    for title,ns,col in groups:
        paths=[]
        for n in ns:
            b=D.bounds(n)
            if b[0]-1e-6<=x<=b[3]+1e-6:paths+=sections(n,0,x)
        if paths:ax.add_collection(LineCollection(paths,colors=col,linewidths=1))
    for title,paths,col in lines:
        for path in paths:
            pts=np.asarray(path).reshape(-1,3);hit=pts[np.abs(pts[:,0]-x)<1.3]
            if len(hit):ax.scatter(hit[:,1],hit[:,2],s=3,c=col,alpha=.62)
    ax.set(xlim=(-117,117),ylim=(26,241),xlabel="Y [mm]",ylabel="Z [mm]",title=f"X = {x} mm");ax.set_aspect("equal");ax.grid(lw=.28)
fig.legend([plt.Line2D([0],[0],color=g[2]) for g in groups+lines],[g[0] for g in groups+lines],loc="lower center",ncol=4)
fig.tight_layout(rect=(0,.063,1,1));fig.savefig(P/"critical-sections.png",dpi=145)

