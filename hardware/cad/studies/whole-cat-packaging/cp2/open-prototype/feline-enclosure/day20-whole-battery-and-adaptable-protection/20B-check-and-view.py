"""Length witnesses and cutaway for the 20B pack-side inlet proposal."""
import json
import math
import os
from pathlib import Path
from runpy import run_path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Dir, gp_Pln, gp_Pnt

folder = Path(__file__).resolve().parent
Saved = run_path(str(folder.parent / "day18-front-insert-correction" / "saved-front.py"))["Saved"]
native = Saved(folder / "whole-cat20A.FCStd")
inv = json.loads((folder / "20B-native-inlet-inventory.json").read_bytes())["members"]
screen = json.loads((folder / "20B-inboard-screen.json").read_bytes())
parts = screen["bounds"]
pocket = json.loads((folder / "20B-pocket-screen.json").read_bytes())["bounds"]

def bezier(p):
    p = np.array(p, float)
    t = np.linspace(0, 1, 321)[:, None]
    q = 1-t
    pts = q**3*p[0] + 3*q*q*t*p[1] + 3*q*t*t*p[2] + t**3*p[3]
    d = 3*(q*q*(p[1]-p[0]) + 2*q*t*(p[2]-p[1]) + t*t*(p[3]-p[2]))
    dd = 6*(q*(p[2]-2*p[1]+p[0]) + t*(p[3]-2*p[2]+p[1]))
    speed = np.linalg.norm(d, axis=1)
    length = np.trapezoid(speed, t[:, 0])
    radius = np.min(speed**3 / np.maximum(np.linalg.norm(np.cross(d, dd), axis=1), 1e-8))
    return pts, float(length), float(radius)

def boot_lead(y0, y1):
    start = np.array([86.5, y0, 73.5])
    station = np.array([78.3, y0, 94.0])
    end = np.array([51.0, y1, 121.5])
    dx = start[0] - station[0]
    angle = 2*math.atan2(dx, 20.5)
    r = (dx**2 + 20.5**2)/(2*dx)
    h = 4/3*math.tan(angle/4)*r
    v = np.array([-math.sin(angle), 0, math.cos(angle)])
    a, l0, r0 = bezier([start, start+[0,0,h], station-h*v, station])
    b, l1, r1 = bezier([station, station+14*v, end+[19,0,0], end])
    return np.concatenate([a, b[1:]]), l0+l1, min(r0,r1)

def aux_gap(pts, radius):
    candidates = pts[(pts[:, 2] >= 86) & (pts[:, 2] <= 96)]
    values = []
    aux = native.shape("AUX_Pololu4092")
    for p in candidates[::2]:
        point = BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Shape()
        measure = BRepExtrema_DistShapeShape(point, aux)
        if not measure.IsDone():
            raise RuntimeError("AUX clearance evaluator unresolved")
        values.append(measure.Value() - radius)
    return min(values)

pack = {}
for key, y0, y1 in [("plus",32.65,36.8), ("minus",27.35,24.8)]:
    path, length, radius = boot_lead(y0, y1)
    pack[key] = {"free_parked_and_held_stroke_mm": round(length,2),
                 "project_dressing_mm": 8.0,
                 "target_exposed_exit_to_boot_mm": round(length + 8,2),
                 "min_inside_radius_with_4p8_project_od_mm": round(radius - 2.4,2),
                 "sampled_AUX_PCB_clearance_after_2p4_jacket_radius_mm": round(aux_gap(path, 2.4),2),
                 "points": path[::8].round(4).tolist(),
                 "start": path[0].tolist(), "end": path[-1].tolist()}
w075, w075_l, w075_r = bezier([[1,36.8,121.5],[-7,36.8,121.5],[-11,40,121.5],[-19,40,121.5]])
w001 = [[1,24.8,121.5],[-9,24.8,121.5],[-17,20,135],[5,25,145],
        [5,55,149],[-0.5,61,151],[-0.5,70,151]]
w076c = [[-86,46.5,121.5],[-74,51.5,121.5],[-50,55,122],[-23,57,130],
         [70,56,132],[126,55,133],[143,60,131],[147,74,124],[161.5,74,113.1602]]

def budget(points, end_mm, dress_mm, moving_points):
    def length(rows):
        return float(np.linalg.norm(np.diff(rows, axis=0), axis=1).sum())
    stroke = np.array(points,float)
    stroke[:moving_points, 0] -= 14
    fixed, opened = length(points), length(stroke)
    return {"points_seated":points, "chord_polyline_seated_mm":round(fixed,2),
            "chord_polyline_open_stroke_mm":round(opened,2),
            "terminal_project_allowance_mm":end_mm, "dressing_project_allowance_mm":dress_mm,
            "planning_blank_mm":math.ceil(max(fixed, opened)+end_mm+dress_mm),
            "actual_cut_mm":None}

measurements = {
    "basis": "20A native 19I source; no saved CAD geometry change",
    "window_picked": "open lid and cap, neutral head, hold pack half at its full parked position; move complete protected carrier -X 14 mm",
    "battery": pack,
    "W075_factory_input": {
        "free_mm":round(w075_l,2), "XT60_cup_debit_project_mm":5.0,
        "free_plus_cup_mm":round(w075_l+5,2), "input_limit_mm":50,
        "inner_radius_with_4p8_project_od_mm":round(w075_r-2.4,2),
        "factory_OD_mm":None, "points":w075[::8].round(4).tolist(),
        "actual_cut_mm":None,
    },
    "W076_factory_output": {
        "straight_free_mm":16.0, "post_preparation_project_mm":11.0,
        "minimum_direct_length_mm":27.0, "delivered_length_and_OD_mm":None,
        "retain_factory_lead":True, "slack_reserve_status":"A 34 x 29 x 32 mm region clears named bodies in parked/open poses. Full lead and both transitions remain OPEN.",
    },
    "W001_LAPP_0107001": {**budget(w001,19,15,3),"source_OD_mm":3.1,
                           "project_connector_pocket_OD_mm":4.8},
    "W076_custom_HELU_23802": {**budget(w076c,26,20,2),"source_OD_mm":4.2},
    "stock_delivered":None, "physicalPASS":False, "actualfit":None, "cut":None, "slack":None,
    "avoid": "no inherited 208/138.69/84.5 values; geometry is conditional and polyline lengths are route budgets"
}
out = folder/"20B-dlugosci.json"
tmp = out.with_suffix(".tmp")
tmp.write_bytes((json.dumps(measurements,indent=2,ensure_ascii=False)+"\n").encode())
os.replace(tmp,out)
print(json.dumps({k: (v if k not in ('battery','W075_factory_input','W001_LAPP_0107001','W076_custom_HELU_23802') else {a:x for a,x in v.items() if a not in ('points','points_seated')}) for k,v in measurements.items() if k!='battery'},ensure_ascii=False),flush=True)
print({k:{a:v for a,v in row.items() if a!='points'} for k,row in pack.items()},flush=True)

# Nominal survey dimensions and a true vertical section of the unchanged native
# frame. Electrical components outside the section are projected and identified.
paper="#f5f6f3"; ink="#1a3037"; mta="#7a54a3"; power="#c76137"; ground="#344859"; door="#187f85"
fig=plt.figure(figsize=(15.8,10.0),facecolor=paper)
gs=fig.add_gridspec(2,2,width_ratios=[3.1,1.0],height_ratios=[1.18,1],left=.07,right=.96,
                    top=.84,bottom=.11,wspace=.20,hspace=.37)
ax=fig.add_subplot(gs[0,:])
cut=fig.add_subplot(gs[1,0])
card=fig.add_subplot(gs[1,1])
card.axis("off")
fig.text(.07,.945,"WAVEGO 20B  |  Wejście baterii i cztery oprawy MTA",fontsize=26,weight="bold",color=ink)
fig.text(.07,.902,"Złożenie 19I · widok z góry i przekrój · obwiednie do przymiarki cyfrowej",fontsize=13,color=ink)
def rect(ax,b,axes,ec,fc=None,alpha=1.,ls="-",z=3,lw=1.4):
    i,j=axes
    p=Rectangle((b[i],b[j]),b[i+3]-b[i],b[j+3]-b[j],lw=lw,ec=ec,
                fc=fc or "none",ls=ls,zorder=z,alpha=alpha)
    ax.add_patch(p)
    return p

def section(ax,n,coord,axes,color,lw=1.25):
    i,j=axes
    axis=3-i-j
    pt=[0,0,0]; pt[axis]=coord
    direction=[0,0,0]; direction[axis]=1
    op=BRepAlgoAPI_Section(native.shape(n),gp_Pln(gp_Pnt(*pt),gp_Dir(*direction)),False)
    op.Build()
    if not op.IsDone():
        raise RuntimeError(f"Section could not be built: {n}")
    it=TopExp_Explorer(op.Shape(),TopAbs_EDGE)
    while it.More():
        curve=BRepAdaptor_Curve(TopoDS.Edge(it.Current()))
        points=[curve.Value(float(t)).Coord() for t in np.linspace(curve.FirstParameter(),curve.LastParameter(),12)]
        ax.plot([p[i] for p in points],[p[j] for p in points],color=color,lw=lw,zorder=2)
        it.Next()

def label(ax,x,y,s,**kw):
    ax.text(x,y,s,fontsize=9.4,color=ink,zorder=10,**kw)

def setup(ax,xlim,ylim,ylabel):
    ax.set(xlim=xlim,ylim=ylim,ylabel=ylabel,xlabel="X [mm]  ·  tył po prawej")
    ax.set_aspect("equal",adjustable="box")
    ax.set_facecolor("#ffffff")
    ax.grid(alpha=.15)
    ax.tick_params(labelsize=8)
    ax.spines[['top','right']].set_visible(False)

setup(ax,(-183,214),(-113,113),"Y [mm]")
ax.set_title("Rzut całej ramy przy zdjętych pokrywach",loc="left",fontweight="bold",fontsize=14,color=ink)
for n in ("H19_FrontFrame","E19_RearBase"):
    section(ax,n,123,(0,1),"#a9b5b4",.7)
for n,name in [("Pi4B_actual_PCB","Pi"),("AUX_Pololu4092","AUX"),("MAIN_Pololu4853","MAIN"),
               ("S0_body","S0"),("WAGO615_power_0_0","G1.2"),("BNO085","BNO")]:
    b=inv[n]["bounds"]
    rect(ax,b,(0,1),"#768382","#e8edeb",.82,z=3)
    label(ax,199 if name=="S0" else (b[0]+b[3])/2, 93 if name=="S0" else (b[1]+b[4])/2,name,ha="center",va="center")
b=inv["Battery_GEA223S30X6GT"]["bounds"]
rect(ax,b,(0,1),door,"#dcefed",.78,z=2)
label(ax,72,47,"BAT",weight="bold")
for x in (-80,-70,112,122):
    ax.scatter([x,x],[-22.5,22.5],s=13,c="#637272",zorder=4)
door_b=[-14.1,100,48.1,96.7,103,76.65]
rect(ax,door_b,(0,1),door,door,.88,z=3)
ax.annotate("Drzwi i wyjęcie +Y", xy=(69,102),xytext=(98,91),
            arrowprops=dict(arrowstyle="->",color=door),fontsize=9,color=door)
for key,kind in [("XT60_full_parked","XT60"),("F0_full_closed","F0"),("POST_F0_full_closed","POST")]:
    b=parts[key]
    rect(ax,b,(0,1),power,"#f5d9c8",.88,z=6)
    label(ax,(b[0]+b[3])/2,(b[1]+b[4])/2,kind,ha="center",va="center",weight="bold")
for stem in ("FL","FR","RL","RR"):
    b=parts[f"MTA_{stem}_installed"]
    rect(ax,b,(0,1),mta,"#eae2f2",.94,z=7)
    label(ax,(b[0]+b[3])/2,(b[1]+b[4])/2,"MTA "+stem,ha="center",va="center",weight="bold")
for key,points,color in [("W001",w001,ground),("W076 custom",w076c,power)]:
    a=np.array(points);ax.plot(a[:,0],a[:,1],ls="--",lw=1.6,color=color,zorder=8)
for row in pack.values():
    a=np.array(row["points"]);ax.plot(a[:,0],a[:,1],lw=1.2,c=door,zorder=7)

setup(cut,(-124,102),(45,174),"Z [mm]")
cut.set_title("Przekrój wejścia i rozpięcie przy otwartych pokrywach",loc="left",fontweight="bold",fontsize=14,color=ink)
for n in ("H19_FrontFrame","E19_RearBase"):
    section(cut,n,30.8,(0,2),"#a5b2b0",.9)
for key,name in [("Battery_GEA223S30X6GT","BAT"),("AUX_Pololu4092","AUX"),("BNO085","BNO")]:
    b=inv[key]["bounds"]
    rect(cut,b,(0,2),door if name=="BAT" else "#798482","#dcefed" if name=="BAT" else "#edf0ef",.83,z=3)
    label(cut,(b[0]+b[3])/2,(b[2]+b[5])/2,name,ha="center",va="center")
for key,name in [("XT60_full_parked","XT60H-M + F"),("F0_full_closed","FHAC0002"),("POST_F0_full_closed","POST")]:
    b=parts[key];rect(cut,b,(0,2),power,"#f5d9c8",.93,z=6)
    label(cut,(b[0]+b[3])/2,(b[2]+b[5])/2,name,ha="center",va="center",weight="bold")
rect(cut,parts["F0_lid_tether_and_fuse_access"],(0,2),power,None,.75,"--",4)
rect(cut,pocket["F0_out_pocket_above_features"],(0,2),"#bc4e4e",None,.85,":",4)
for row in pack.values():
    p=np.array(row["points"]);cut.plot(p[:,0],p[:,2],lw=1.8,c=door,zorder=7)
cut.plot(w075[:,0],w075[:,2],lw=1.8,c=power,zorder=8)
cut.plot([-86,-70],[121.5,121.5],lw=1.8,c=power,zorder=8)
cut.add_patch(FancyArrowPatch((26,139),(12,139),arrowstyle="-|>",mutation_scale=17,lw=1.8,color=power,zorder=9))
label(cut,9,143,"Skok instalacji 14 mm")
label(cut,-102,161,"Rezerwa\nW076")
label(cut,68,112,"Żyły\npakietu",ha="center")
label(cut,-20,47,"Cienkie linie • geometria ramy w Y = 30,8 mm",ha="center")
card.text(0,1,"Kolejność",color=ink,fontsize=15,weight="bold",va="top")
card.text(0,.86,"1  Zdejmij pokrywy.\n2  Przytrzymaj wtyk pakietu.\n3  Zwolnij stronę instalacji.\n4  Przesuń ją o 14 mm w −X.\n5  Zwolnij pasy oraz drzwi +Y.",fontsize=11,color=ink,
          linespacing=1.62,va="top")
card.text(0,.36,"Otwarte pomiary",fontsize=13,weight="bold",color=ink)
card.text(0,.30,"Obie żyły BAT, dwa końce F0,\npełne obrysy 4 MTA oraz\nchwyt i położenie klapek.",fontsize=10.5,color=ink,linespacing=1.42,va="top")
fig.text(.07,.038,"BAT i elementy kolorowe pokazano jako obwiednie. Fizyczne dopasowanie, długości dostawy i stan magazynowy wymagają pomiaru.",fontsize=10,color=ink)
fig.savefig(folder/"20B-przekroj.png",dpi=165,facecolor=paper)