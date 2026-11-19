"""Separate material unit accounts and sampled lane-to-lane clearances at the two fans."""
from pathlib import Path
import numpy as np,json,hashlib
from scipy.spatial import cKDTree
P=Path(__file__).parent;C=P.parent/"day19-closed-head-neck-and-module-interfaces";B=P.parent/"day19-common-floor-and-bundle-assembly"
x=json.loads((P/"whole-lay.json").read_bytes());old=json.loads((P.parent/"day18-body-reception-and-closed-fit/typed-jp3.json").read_bytes())
def measure(paths,term):
    qs=[];rows=[]
    for line in paths:
        line=np.array(line);s=np.r_[0,np.cumsum(np.linalg.norm(np.diff(line,axis=0),axis=1))]
        # Exact bare allocation remains unknown. Flag terminal-adjacent witnesses
        # separately so a PVC diameter is not assigned to a soldered landing.
        t=np.linspace(0,s[-1],int(s[-1]/.28)+1);q=np.column_stack([np.interp(t,s,line[:,k]) for k in range(3)]);qs.append((q,cKDTree(q),t))
    for i in range(4):
        for j in range(i):
            d,k=qs[i][1].query(qs[j][0]);a=np.argmin(d);other=k[a]
            dst=min(qs[i][2][other],qs[j][2][a]) if term=="start" else min(qs[i][2][-1]-qs[i][2][other],qs[j][2][-1]-qs[j][2][a])
            rows.append(dict(cores=[i+1,j+1],sampled_gap=float(d[a]-2.1),point=qs[j][0][a].round(3).tolist(),along_wire_from_terminal_mm=float(dst) if term else None))
    return rows
pins=[]
for i,d in enumerate(x["debits"]):
    pins.append(dict(wire=d["wire"],color=["czerwony","czarny","żółty","żółty"][i],stock=["HELU23302","HELU23301","HELU23308","HELU23308"][i],board3417=["VIN","GND","SDA","SCL"][i],pad_center_head=x["head"][i][0],PCA="JP3."+str(d["JP3"]),PCA_pad=x["fixed"][i]["centreline"][-1],terminal="PTH centre, bare solder land, transition to insulation. Exact strip/land length to measure with actual wire.",end_debit_total=12,installed_strip_each=None,**{k:v for k,v in d.items() if k!="wire"}))
unit=dict(stations=pins,stock_consumption_scenario_mm={"HELU23302":pins[0]["planned"],"HELU23301":pins[1]["planned"],"HELU23308_two_labelled_runs":pins[2]["planned"]+pins[3]["planned"]},head_fan=measure(x["head"],"start"),body_fan=measure([f["centreline"] for f in x["fixed"]],"end"),moving_fan=[dict(yaw=m["yaw"],pitch=m["pitch"],lanes=measure(m["cores"],None)) for m in x["motion"]],FFC=dict(stock=200,free=190,both_ends=10),servos=[dict(axis=a,MG=250,case_debit=11.45,free=223.55,key=15,JR=300,plug=12,transport_and_reserve=246,fan=25,insulated=9,lap=8,sleeve=20) for a in ["yaw","pitch","tail"]],E2_220=[["XP02.source","F_PWM.out","JPWM_SOURCE.1"],["XP03.source","G_TAIL.3","JPWM_SOURCE.2"],["XP02.module","JPWM_MODULE.1","U_PWM.3"],["XP03.module","JPWM_MODULE.2","U_PWM.2"]],DATA500=dict(stock=500,OD=6.8,inner_R=30,project_boot_each=26,actual_approach=None),USB_AUDIO_stock=None,POWER_K1474="distinct from Delock POWER and both data leads",MTA0100335=dict(qty=4,full_profile=None,tail_each=None),GTech_map=None,actual_fit_cut_slack=None,physical_PASS=False)
(P/"unit-stations.json").write_bytes((json.dumps(unit,indent=1)+"\n").encode())
print("gaps",[min(r["sampled_gap"] for r in unit[k]) for k in ["head_fan","body_fan"]],min(r["sampled_gap"] for m in unit["moving_fan"] for r in m["lanes"]))

