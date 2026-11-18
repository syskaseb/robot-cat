"""Plot true sections from selected saved solids plus labeled offset equipment sections."""
import json, math, runpy
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
import numpy as np
from scipy.spatial import ConvexHull
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Line
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pln,gp_Pnt,gp_Dir
P=Path(__file__).parent
src=P/"open-front.FCStd"
prior=P.parent/"day18-front-insert-correction"
D=runpy.run_path(str(prior/"saved-front.py"))["Saved"](src)
rd=json.loads((P/"occupied-layout.json").read_bytes())
ex={"poses":rd["extension"]}
datum={"section_x":-113.0,"witness":None}
sections={"shell":["OPEN_FRONT_COWL","OPEN_AFT_COWL","OPEN_BATTERY_DOOR","INSERT_OPTICAL_FACE","OPEN_SKULL_BACK"],
          "structure":["OPEN_SINGLE_FRONT_FLOOR","P03_rear_deck_integrated_load_yoke","F2_COMMON_PI_BUS_PCA_RECEIVER","FRONT18_REAR_NEG_PANEL","FRONT18_REAR_POS_PANEL"],
          "gimbal":[n for n in D.members if n.startswith(("YAW_SHAFT_FORK_POSITIVE_CROSSPIN","YAW_HORN_KEY_HALF","YAW_HORN_ROOF","YAW_OUTER_RACE_SPACER","YAW_FIXED_OUTER_RACE_CAP","Yaw608_","HEAD_YAW_FORK_FIXED_", "MG92B_Head", "PITCH_HORN_ROOF","D18C_TRUE_PITCH_"))],
          "modules":["Pi4B_actual_PCB","Pi_components_and_cooling","PCA9685_Adafruit815_PCB","E1_populated_prototype_board","BUS25514_installed","PBAY_P_REAR","PBAY_F_AUX","Battery_GEA223S30X6GT","Monitor_MOD05015","VL53L5CX","Camera3_NoIR_Wide","CF17_POL1992_FULL_MATED_BODY"]+[n for n in D.members if n.startswith("Motor_ATO4A_")],
          "audio":["Speaker","ReSpeakerLite_on_REMOVABLE_back","MAX98357A_amp","INSERT_AUDIO_USB_A_FULL_MATE_FIELD","INSERT_AUDIO_USB_C_FULL_MATE_FIELD","INSERT_SPEAKER_TWO_BTL_TABS_FIELD"]}
palette=dict(shell="#30363e",structure="#527171",gimbal="#82462e",modules="#88909e",audio="#126a94",FFC="#bc7252",ToF="#32843a",JR="#a167a2")
def cut(n,axis,pos):
    b=D.bounds(n)
    if pos<b[axis]-1e-6 or pos>b[axis+3]+1e-6:return []
    origin=np.zeros(3);origin[axis]=pos
    normal=np.eye(3)[axis]
    op=BRepAlgoAPI_Section(D.shape(n),gp_Pln(gp_Pnt(*origin),gp_Dir(*normal)),True)
    ee=TopExp_Explorer(op.Shape(),TopAbs_EDGE);segs=[]
    while ee.More():
        cv=BRepAdaptor_Curve(TopoDS.Edge(ee.Current()))
        sz=2 if cv.GetType()==GeomAbs_Line else 22
        xyz=np.array([cv.Value(float(u)).Coord() for u in np.linspace(cv.FirstParameter(),cv.LastParameter(),sz)])
        segs.append(xyz[:,[0,2] if axis==1 else [1,2]])
        ee.Next()
    return segs
def contour(ax,segments,color,width,alpha=1,style="solid"):
    if segments:ax.add_collection(LineCollection(segments,colors=color,linewidths=width,alpha=alpha,linestyles=style))
tracks=[("FFC",next(q for q in rd["FFC"] if q["yaw"]==q["pitch"]==0)["centreline"]),
        ("ToF",next(q for q in rd["ToF_moving"] if q["yaw"]==q["pitch"]==0)["centreline"])]
tracks += [("ToF",q["centreline"]) for q in rd["ToF_fixed"]+rd["ToF_header"]]
tracks += [("JR",q["centreline"]) for q in rd["JR_factory"]]+[("JR",next(q for q in ex["poses"] if q["yaw"]==0)["centreline"])]
labels={"shell":"powłoki","structure":"podparcie","gimbal":"mechanizm i śruba","modules":"moduły","audio":"audio i pola portów","FFC":"FFC","ToF":"ToF","JR":"JR"}
def tube(ps,w,t):
    ps=np.array(ps);ps=ps[np.r_[True,np.linalg.norm(np.diff(ps,axis=0),axis=1)>1e-5]]
    tang=np.gradient(ps,axis=0);tang/=np.linalg.norm(tang,axis=1)[:,None]
    width=np.eye(3)[np.argmin(np.abs(tang[0]))];rows=[]
    for p,u in zip(ps,tang):
        width=width-u*(width@u);width/=np.linalg.norm(width);normal=np.cross(u,width)
        rows.append([p+i*w/2*width+j*t/2*normal for i,j in [(-1,-1),(-1,1),(1,1),(1,-1)]])
    return np.array(rows)
tubes=[("FFC",np.array(next(q for q in rd["FFC"] if q["yaw"]==q["pitch"]==0)["corners"])),
       ("ToF",np.array(next(q for q in rd["ToF_moving"] if q["yaw"]==q["pitch"]==0)["corners"]))]
tubes += [("ToF",tube(q["centreline"],2.1,2.1)) for q in rd["ToF_fixed"]+rd["ToF_header"]]
tubes += [("JR",tube(q["centreline"],3.5,1.8)) for q in rd["JR_factory"]+[next(q for q in ex["poses"] if q["yaw"]==0)]]
def occupied_slices(ax,pos):
    # Take the planar hull of every crossing chord of the local convex cell.
    # This bounds the section for either ordering of the two four-corner ends.
    edges=[(i,j) for i in range(8) for j in range(i+1,8)]
    for group,c in tubes:
        for a,b in zip(c,c[1:]):
            v=np.vstack([a,b]);pts=[]
            if v[:,0].min()>pos or v[:,0].max()<pos:continue
            for i,j in edges:
                u,w=v[i],v[j]
                if (u[0]-pos)*(w[0]-pos)>0 or abs(w[0]-u[0])<1e-8:continue
                pts.append((u+(pos-u[0])/(w[0]-u[0])*(w-u))[1:])
            pts=np.unique(np.round(pts,6),axis=0)
            if len(pts)>2 and np.linalg.matrix_rank(pts-pts[0])==2:
                hull=pts[ConvexHull(pts).vertices];ax.fill(hull[:,0],hull[:,1],color=palette[group],alpha=.55)
for axis,pos,name,title in [(1,0.03,"longitudinal","Przekrój podłużny przez wkład, górny powrót DATA i audio"),(0,datum["section_x"],"throat","Przekrój poprzeczny przez dwie stopy i otwarte wyjście MG")]:
    fig,ax=plt.subplots(figsize=(13,6) if axis==1 else (9,7))
    for group,names in sections.items():
        for n in names:
            boundary=cut(n,axis,pos)
            contour(ax,boundary,palette[group],1.2 if group in ("shell","audio","gimbal") else .8)
            if axis==1 and group in ("audio","modules","gimbal") and not boundary:
                bb=D.bounds(n);sample=(bb[1]+bb[4])/2
                contour(ax,cut(n,1,sample),palette[group],.75,.72,"dashed")
    for key,line in tracks:
        q=np.array(line)
        if axis==1:
            ax.plot(q[:,0],q[:,2],color=palette[key],lw=1,alpha=.72)
        else:
            for a,b in zip(q,q[1:]):
                if (a[0]-pos)*(b[0]-pos)>0 or abs(b[0]-a[0])<1e-8:continue
                y,z=(a+(pos-a[0])/(b[0]-a[0])*(b-a))[1:]
                ax.scatter(y,z,s=11,color=palette[key],zorder=5)
    if axis==0:
        occupied_slices(ax,pos)
        contour(ax,cut("OPEN_HANDLAY_OVER_FLOOR",axis,pos),"#bc7c13",1.1,1,"dashed")
    else:
        explorer=TopExp_Explorer(D.shape("F3_DATA500_HORIZONTAL_COMPLETE_UNIT"),TopAbs_EDGE)
        while explorer.More():
            curve=BRepAdaptor_Curve(TopoDS.Edge(explorer.Current()))
            xyz=np.array([curve.Value(float(u)).Coord() for u in np.linspace(curve.FirstParameter(),curve.LastParameter(),35)])
            ax.plot(xyz[:,0],xyz[:,2],color="#d19014",lw=2.4)
            explorer.Next()
    w=datum["witness"]
    if w:
        xx=w[0] if axis==1 else w[1]
        ax.scatter(xx,w[2],s=55,marker="x",c="#be212b",zorder=7)
        ax.annotate("JR yaw w kolumnie",(xx,w[2]),xytext=(10,-16),textcoords="offset points",fontsize=9,color="#9c1c23")
    ax.set_title(title,loc="left",fontweight="bold")
    ax.set_xlabel(("X" if axis==1 else "Y")+" [mm]");ax.set_ylabel("Z [mm]");ax.set_aspect("equal")
    ax.set_xlim((-232,190) if axis==1 else (-104,104));ax.set_ylim(0,226 if axis==1 else 215)
    ax.grid(True,lw=.35,color="#d3d9db")
    sub=("Y = 0,03 mm. Kreskowane obrysy pokazują równoległe przekroje wyposażenia poza osią. Złota linia to DATA500. Pozostałe kolory pokazują rzut torów neutralnych." if axis==1 else
         f"X = {pos:.2f} mm. Kolorowe pola pokazują zajęte przekroje wiązek w pozycji neutralnej. Złota linia przerywana wyznacza projektowe pole dojścia przy serwie.")
    fig.text(.055,.065,sub,fontsize=9)
    fig.legend([Line2D([0],[0],color=v,lw=2) for v in palette.values()],[labels[k] for k in palette],loc="lower center",ncol=8,frameon=False,fontsize=8)
    fig.tight_layout(rect=[.015,.11,.99,.97]);fig.savefig(P/("section-"+name+".png"),dpi=140);plt.close(fig)
print("Longitudinal and open bridge sections",src.name)
