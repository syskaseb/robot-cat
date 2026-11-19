"""Two critical current sections and bounded changed-interface witnesses."""
from pathlib import Path
import runpy,json,numpy as np,hashlib
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
Saved=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"]
D=Saved(P/"whole-cat19.FCStd")
actors=json.loads((P/"corrected-low-actors.json").read_bytes());names={q["name"] for q in actors}
old=json.loads((P/"first-occupied-gate.json").read_bytes())
exact=[dict(a=q["a"],b=q["b"],result=D.common(q["a"],q["b"])) for q in old["exact"]]
# Distinguish project capacity from purchased material at the new port interface.
port_pairs=[("D19_DATA_STORAGE_LAYER","MAIN_Pololu4853"),("D19_DATA_STORAGE_LAYER","AUX_Pololu4092"),("D19_DATA_STORAGE_LAYER","PBAY_F_PI"),("D18C_DATA_BUS_FULL26_PROJECT_BOOT","PCA9685_Adafruit815_PCB"),("D19_JR300_TAIL_RESERVE","MG92B_Tail"),("D19_JR300_TAIL_RESERVE","MAX98357A_amp")]
local=[dict(a=a,b=b,result=D.common(a,b)) for a,b in port_pairs]
former=json.loads((P.parent/"day18-body-reception-and-closed-fit"/"frozen-field-check.json").read_bytes())["rows"]
head=[]
for q in former:
    for h in q["exact_witness"]:
        if h["part"]=="BR_PARTED_SKULL_BACK":
            hit=D.inside("D19_BROAD_SKULL_BACK",[h["source_frame"]])
            head.append(dict(yaw=q["yaw"],pitch=q["pitch"],former_witness_in_current_back=hit is not None,point=h["source_frame"]))
groups={
"skorupy":(["D19_ROUNDED_FORE_COWL","D19_ROUNDED_REAR_COWL","D19_BROAD_SKULL_BACK","BR_COMMON_OPTICAL_MASK","D19_FIXED_INNER_NECK"],"#282d35"),
"podpory":(["D19_LOW_FORE_CARRIER","D19_LOW_REAR_CARRIER","D19_OPEN_GIMBAL_LOAD_PORTAL","BR_FINISHED_YAW_SADDLE","D18C_TRUE_PITCH_OPTICAL_RECEIVER"],"#468585"),
"moduly":([q["name"] for q in actors if q["name"].startswith(("Motor_ATO","WAGO","PBAY_"))]+["Pi4B_actual_PCB","PCA9685_Adafruit815_PCB","E1_populated_prototype_board","Speaker","ReSpeakerLite_on_REMOVABLE_back","S0_body","MG92B_Head_yaw","MG92B_Head_pitch","BR_PAIR_HY","BR_FLANK_HP_PAIR"],"#416b9b"),
"pelny metal":([q["name"] for q in actors if q["name"].startswith("YAW_SHAFT_FORK_POSITIVE_CROSSPIN")],"#aa7c39"),
"zajete regiony warunkowe":(["D19_DATA_STORAGE_LAYER","D18C_DATA_BUS_FULL26_PROJECT_BOOT","D19_JR300_YAW_RESERVE","D19_JR300_PITCH_RESERVE","D19_JR300_TAIL_RESERVE"],"#d78c23")}
def section(n,x):
    s=BRepAlgoAPI_Section(D.shape(n),gp_Pln(gp_Pnt(x,0,0),gp_Dir(1,0,0)),True)
    exp=TopExp_Explorer(s.Shape(),TopAbs_EDGE);curves=[]
    while exp.More():
        c=BRepAdaptor_Curve(TopoDS.Edge(exp.Current()))
        ts=np.linspace(c.FirstParameter(),c.LastParameter(),2 if c.GetType()==GeomAbs_Line else 25)
        curves.append(np.array([c.Value(t).Coord() for t in ts])[:,1:])
        exp.Next()
    return curves
fig,axes=plt.subplots(1,2,figsize=(12,7))
for ax,x in zip(axes,(-128.371686,90)):
    for label,(ns,color) in groups.items():
        lines=[]
        for n in ns:
            if n not in names:continue
            b=D.bounds(n)
            if b[0]-1e-5<=x<=b[3]+1e-5:lines+=section(n,x)
        if lines:ax.add_collection(LineCollection(lines,colors=color,linewidths=1,label=label))
    ax.set_title(f"X = {x:.2f} mm");ax.set_xlim(-116,116);ax.set_ylim(-10,240);ax.set_aspect("equal");ax.grid(True,lw=.3);ax.set_xlabel("Y [mm]");ax.set_ylabel("Z [mm]")
handles,labels=axes[1].get_legend_handles_labels();fig.legend(handles,labels,loc="lower center",ncol=3);fig.tight_layout(rect=(0,.07,1,1));fig.savefig(P/"critical-sections.png",dpi=150)
res=dict(native_sha256=hashlib.sha256((P/"whole-cat19.FCStd").read_bytes()).hexdigest(),prior_six=exact,port_space=local,former_head_witnesses=head,
         scope="Changed pairs and former four ToF witnesses only; continuous motion, full new ToF fan and all unit approaches remain open.",physical_PASS=False,whole_accepted=False)
(P/"current-whole-gate.json").write_bytes((json.dumps(res,indent=1)+"\n").encode())
print(json.dumps(res,indent=1))
