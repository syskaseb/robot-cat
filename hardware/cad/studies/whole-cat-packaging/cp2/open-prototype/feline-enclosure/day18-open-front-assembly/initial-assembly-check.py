"""Check available vertical insertion stroke at the first fore bank and the complete yaw MG approach."""
from pathlib import Path
import json,runpy
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
from OCP.gp import gp_Vec,gp_Trsf
from OCP.TopLoc import TopLoc_Location
P=Path(__file__).parent
D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"open-front.FCStd")
res=dict(bank=[],yaw_case=[],physical_PASS=False)
for n in ["Motor_ATO4A_1_0","Motor_ATO4A__1_0","Motor_ATO4A_1_1","Motor_ATO4A_1_3","Motor_ATO4A__1_3","Motor_ATO4A_1_4"]:
    exp=TopExp_Explorer(D.shape(n),TopAbs_SOLID);b=[]
    while exp.More():
        key=n+"_part_"+str(len(b));D.shapes[key]=exp.Current();b.append(D.bounds(key));exp.Next()
    lift=127.915+1.25-b[0][2]
    locations=[D.bounds("FIT_DATA_SEATS_"+str(i)) for i in (0,1)]
    # Lowest shelf over a flange is the underside of the lip at 162.5.
    # Uprights remain inboard of the case; TE counterparts enter from below.
    res["bank"].append(dict(unit=n,source_solids=len(b),panel_top=127.915,
        holder_bbox=b[0].tolist(),vertical_stroke=lift,highest_during_insertion=b[0][5]+lift,
        remaining_under_lip=162.5-b[0][5]-lift,fuse_bbox=b[1].tolist(),two_TE_bounds=[x.tolist() for x in b[2:]]))
for dx in [-42,-30,-18,-6,0]:
    m=gp_Trsf();m.SetTranslation(gp_Vec(dx,0,0));name="MG_slide_"+str(dx)
    D.shapes[name]=D.shape("MG92B_Head_yaw").Moved(TopLoc_Location(m))
    row=dict(offset_x=dx,portal=D.common("OPEN_PORTAL_MATERIAL_SUBSET",name),source_floor=D.common("D18C_P02_THREE_ROOT_THROUGH_VERSION",name))
    res["yaw_case"].append(row)
res["scope"]="Approach from front with covers and saddle screws out on the bench. Full source case/horn model at five translations, actual tool path and intermediate continuum open. Lift prewired stock only where the selected hardware allows; holder then fuse and full TE units from below."
(P/"initial-assembly.json").write_bytes((json.dumps(res,indent=1)+"\n").encode())
print(res["yaw_case"])
