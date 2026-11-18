"""Pin the effective native roles, unit budgets and the scoped hardware checks in the frozen assembly."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json,hashlib,runpy
import numpy as np
P=Path(__file__).parent;D=runpy.run_path(str(P.parent/"day18-front-insert-correction"/"saved-front.py"))["Saved"](P/"body-reception.FCStd")
H=next(d for d in P.parents if d.name=="hardware")
active=["BR_COMMON_OPTICAL_MASK","BR_PARTED_SKULL_BACK","BR_CHEST_EXTENSION_ENTRY","BR_ROUNDED_RUMP","BR_FINISHED_YAW_SADDLE","BR_FORE_ROOT_PI_CARRIER","BR_BODY_FLOOR_OUTER_TOWER","BR_PITCH_RECEIVER_OPEN_ENTRY"]
gui=ET.fromstring(D.zip.read("GuiDocument.xml"))
def visible(n):return gui.find(f".//ViewProvider[@name='{n}']/Properties/Property[@name='Visibility']/Bool").get("value")=="true"
assert all(visible(n) for n in active)
dims={}
for n in active:
    b=D.bounds(n);size=b[3:]-b[:3];envelope=size+np.array([16,16,4])
    dims[n]=dict(box_mm=size.tolist(),native_axes_with_8mm_brim_each_side_and_4mm_Z_allowance=envelope.tolist(),box_screen=bool(np.max(envelope)<=256))
r=json.loads((P/"flank-reception.json").read_bytes());jr=json.loads((P/"yaw-laid-factory.json").read_bytes())["rows"];fan=json.loads((P/"jp3-shared-fan.json").read_bytes())["rows"]
ffc=json.loads((P.parent/"day18-open-front-assembly"/"occupied-layout.json").read_bytes())["FFC"]
src=H/"electronics/full-cat/closed-prototype-add7-2026-11-16/assembly-reference/POLACZENIA.csv"
old=P.parent/"n01-shared-routing-boundaries.json"
bounds=json.loads(old.read_bytes())["endpoints"]
legs=[]
for i,(wire,endpoint,entry,stock,capacity) in enumerate([("XB23","G_AUX.3","WAGO415_data_1_6","HELU23301",2.1),("XB22","F_HP.out","PBAY_F_HP","HELU23302",1.05),("XS23","R2.2","E1_populated_prototype_board","HELU23308",1.05)]):
    row=next(line for line in src.read_text(encoding="utf-8-sig").splitlines() if ";"+wire+";" in line)
    assert endpoint in row
    q=next(v for v in bounds if v.get("endpoint")==endpoint);clip=r["extension"]["fans"][i]
    land=np.array(clip["lap_center"])+13*np.eye(3)[1];b=D.bounds(entry)
    distance=float(np.linalg.norm(np.maximum(0,np.maximum(b[:3]-land,land-b[3:]))))
    legs.append(dict(wire=wire,from_body_land=land.tolist(),existing_end=endpoint,existing_function_group=q["group"],selected_body_unit_or_E1_allocation=entry,body_box=b.tolist(),bulk_stock=stock,capacity_radius_mm=capacity,
        lower_bound_to_body_box_mm=distance,lower_bound_scope="Distance to the selected housing or E1 regional allocation only. R2.2 source group PWM1608_U1 still needs its particular mounted endpoint. The FHAC exit side and the physical cavity mouth are not frozen by the box.",
        proper_HELU_land=9,proper_HELU_lap=8,body_blank_rule="ceil5(L to proper end + 30) after continuous actual body allocation",planned_body_blank=None,actual_cut=None))
ends=dict(yaw_JR=dict(full=250,case_stub=11.45,static_free=223.55,plug=15,body_pair="C_HY",far_ends=["XB12 F_HY.out","XB13 G_AUX.4","XS13 R1.2"]),
    pitch_JR=dict(full=250,case_stub=11.45,on_yaw_saddle=jr[2]["case_to_yaw_grip"],moving=jr[2]["yaw_grip_to_body"],plug=15,body_pair="C_HP",minimum_inner_R=min(v["minimum_inner_R"] for v in jr)),
    static_JR300=dict(full=300,plug=12,shared_free=246,individual_fan=25,insulated_land=9,lap=8,three_sleeves_mm=[20,20,20],body_continuations=legs),
    FFC=dict(raw=200,proper_ends_once=10,nominal_free=190,sampled_free=[v["free_length"] for v in ffc],source_contacts="unchanged"),
    ToF=dict(moving_free=r["ToF_move"][0]["free"],minimum_inner_R=min(v["inner_R"] for v in r["ToF_move"]),stationary_fan=[{k:v[k] for k in ("wire","JP3","fixed_length","minimum_fixed_inner_R","budget","planned_each")} for v in fan]),
    DATA500=dict(raw=500,fixed_boot_debits=[26,26],free=448,stored=253.3744407846,transport=194.6255592154),
    USB_AUDIO=dict(measured_length=None,illustrative_free_polyline=json.loads((P/"station-facts.json").read_bytes())["USB"]["rectilinear_audio_mm"],condition="Seat both delivered plugs together in the diagonal Pi USB-A ports and confirm the jacket and supplied length to ReSpeaker; BTL stays AMP-to-speaker."))
out=dict(source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),archived_ends_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),print_envelopes=dims,
         active_roles=active,unit_budgets=ends,local=[],print_status="Dimensional screen only; slicing and actual support/brim remain unverified.",physical_PASS=False,actual_cuts=None,installed_slack=None)
def save():(P/"frozen-unit-receipt.json").write_bytes((json.dumps(out,indent=1)+"\n").encode())
save()
for a,b in [("BR_CHEST_EXTENSION_ENTRY","BR_FLANK_HP_PAIR"),("BR_CHEST_EXTENSION_ENTRY","BR_FLANK_THREE_LAPS"),("BR_COMMON_OPTICAL_MASK","BR_PITCH_RECEIVER_OPEN_ENTRY")]+[("BR_FINISHED_YAW_SADDLE",n) for n in D.members if n.startswith("YAW_SHAFT_FORK_POSITIVE_CROSSPIN") and "space" not in n]+[("BR_FINISHED_YAW_SADDLE","MG92B_Head_pitch")]:
    out["local"].append(dict(a=a,b=b,**D.common(a,b)));save()
