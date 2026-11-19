"""Section the saved native shapes at the two changed interfaces and eight anchor axes."""
from pathlib import Path
import runpy, numpy as np
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
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"whole-cat19B.FCStd")
groups={"podłoga":(["B19_FrontFloor","B19_RearFloor"],"#146963"),
"kotwy, śruby i narzędzie":([n for n in D.members if n.startswith(("H01_source","YAW_SHAFT_FORK_POSITIVE","TAIL_CARTRIDGE_CAP","TAIL_SADDLE_ROOT","B19_Tool"))],"#ae641d"),
"serwo, łożysko, złącze":(["MG92B_Head_yaw","MG92B_Tail","TAIL_FIXED_BEARING_CARTRIDGE","TAIL_REAL_REMOVABLE_SERVO_SADDLE","Yaw608_120","Yaw608_134","BR_FLANK_HP_PAIR","MAX98357A_amp","B19_TailMatedPair","BR_PAIR_HY","PCA9685_Adafruit815_PCB","E1_populated_prototype_board"],"#94435c"),
"przestrzeń kabli":(["B19_TailJRUnderBank","B19_TailLaps","D19_DATA_STORAGE_LAYER","BR_YAW_STATIC"],"#2581bc"),
"obudowa":(["D19_BROAD_SKULL_BACK","D19_ROUNDED_FORE_COWL","D19_ROUNDED_REAR_COWL"],"#51535a")}
def sections(n,axis,t):
    normal=np.eye(3)[axis]; loc=t*normal
    op=BRepAlgoAPI_Section(D.shape(n),gp_Pln(gp_Pnt(*loc),gp_Dir(*normal)),True)
    exp=TopExp_Explorer(op.Shape(),TopAbs_EDGE);lines=[]
    while exp.More():
        c=BRepAdaptor_Curve(TopoDS.Edge(exp.Current()))
        pts=[c.Value(k).Coord() for k in np.linspace(c.FirstParameter(),c.LastParameter(),2 if c.GetType()==GeomAbs_Line else 28)]
        lines.append(np.delete(pts,axis,axis=1));exp.Next()
    return lines
fig,axs=plt.subplots(2,2,figsize=(12,8))
for ax,(axis,t,title,limits) in zip(axs.flat,[(1,22.5,"Podparcie i cztery prawe kotwy",[-155,173,30,130]),(1,-22.5,"Podparcie i cztery lewe kotwy",[-155,173,30,130]),(0,-130,"Gimbal w osi łożysk",[-60,60,37,150]),(0,140,"Serwo ogona i dojścia pod bankiem",[-104,63,36,160])]):
    for label,(names,color) in groups.items():
        lines=[]
        for n in names:
            if n not in D.members:continue
            b=D.bounds(n)
            if b[axis]-.0001<=t<=b[axis+3]+.0001:lines.extend(sections(n,axis,t))
        if lines:ax.add_collection(LineCollection(lines,colors=color,linewidths=1.25,label=label))
    ax.axis(limits);ax.set_aspect("equal");ax.set_title(title);ax.set_xlabel(("Y" if axis==0 else "X")+" [mm]");ax.set_ylabel("Z [mm]");ax.grid(lw=.3)
fig.legend([plt.Line2D([0],[0],color=c) for _,c in groups.values()],list(groups),loc="lower center",ncol=5)
fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(P/"critical-sections.png",dpi=150)

