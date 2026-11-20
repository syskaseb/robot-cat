"""Build and save the 20C inlet and MTA assembly changes in FreeCAD."""
from pathlib import Path
from runpy import run_path
import hashlib
import json
import math
import os

import FreeCAD as App
import FreeCADGui as Gui
import Part

folder=Path(__file__).resolve().parent
root=folder.parent
native=folder/"whole-cat20C.FCStd"
g=run_path(str(folder/"geometry.py"))
l=run_path(str(folder/"layout.py"))
box,fuse,bbox,overlap=[g[k] for k in ("box","fuse","bbox","overlap")]
V=App.Vector

def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()

def add(name,label,shape,color,visible=True):
    obj=doc.addObject("Part::Feature",name)
    obj.Label=label;obj.Shape=shape
    obj.ViewObject.ShapeColor=color
    obj.ViewObject.LineColor=(.16,.19,.21)
    obj.ViewObject.Visibility=visible
    return obj

def replace(name,shape,label=None):
    obj=doc.getObject(name)
    obj.Shape=shape
    if label:
        obj.Label=label
    assert max(abs(x-y) for x,y in zip(bbox(obj.Shape),bbox(shape)))<.001,(name,bbox(obj.Shape),bbox(shape))
    return obj

def geometry_check(name,shape):
    if shape.isNull() or not shape.isValid() or len(shape.Solids)!=1:
        raise RuntimeError(f"{name}: expected one valid solid")

doc=App.ActiveDocument
assert doc is not None and Path(doc.FileName).resolve()==(root/"whole-cat20A.FCStd").resolve()
assert len(doc.Objects)==551 and not doc.isTouched()
assert digest(root/"whole-cat20A.FCStd")==digest(root.parent/"day19-complete-first-fit"/"whole-cat19I.FCStd")
assert not native.exists()
gate=json.loads((folder/"20C-dry-gate.json").read_bytes())
check_gate=("pack_body_both_directions","stationary_XT60_M","pack_F_14mm_positive_Y",
            "full_unmated_F_boot_wall_throat","two_jacket_exit_wall_throat","whole_F0_assumed_21p5")
for key in check_gate:
    if gate["gate"][key]["common_mm3"]:
        raise RuntimeError(f"Clearance gate unresolved for {key}: {gate['gate'][key]}")
if gate["bridge_vs_door_and_neighbors"] or gate["bridge_fixed_base_overlap"]>.03:
    raise RuntimeError("Bridge partition has retained solid interference")
for key,value in gate["named_pack_corners"].items():
    if min(value.values())<1.25:
        raise RuntimeError(f"PCB exit clearance below planning witness for {key}: {value}")
for key in ("f0_mount_neighbor_overlap","post_mount_neighbor_overlap"):
    if gate[key]:
        raise RuntimeError(f"Rigid/occupied-area support gate {key}: {gate[key]}")

prior=json.loads((root/"20B-dlugosci.json").read_bytes())
wires=l["wire_budgets"](prior)
# Save the clean copy before new surface operations. The source file remains pinned.
doc.saveAs(str(native))
doc.Label="whole-cat20C"
q=g["collect"](doc)
front,f0,f0_socket,f0_mm3=l["f0_prints"](doc,g)
post=l["post_print"](doc,g)
parts=[
    ("C20_FrontFrame", "H19_FrontFrame", front, "Z, bazą w dół", "H19_FrontFrame"),
    ("C20_RearBase", "E19_RearBase", q["rear"], "Z, bazą w dół", "E19_RearBase"),
    ("C20_BatteryUpperBridge", "C20_BatteryUpperBridge", q["bridge"], "zewnętrzną powierzchnią +Y do stołu", ""),
    ("C20_F0_OpenMount", "C20_F0_OpenMount", f0, "długim bokiem +X do stołu", ""),
    ("C20_Post_OpenSlottedMount", "C20_Post_OpenSlottedMount", post, "platformą do stołu", ""),
]
for n,(shape,actor,z,site,sample) in q["mta"].items():
    parts.append(("C20_"+n,"C20_"+n,shape,"długim bokiem +Y do stołu",""))
for filename,name,s,pose,replaces in parts:
    geometry_check(filename,s)

doc.openTransaction("20C fixed inlet and upper door bridge")
color=(.53,.64,.61)
mount_color=(.42,.55,.57)
replace("H19_FrontFrame",front,"C20 FrontFrame | fixed F0 mount seat")
replace("E19_RearBase",q["rear"],"C20 RearBase | fixed XT60 and upper door receivers")
bridge=add("C20_BatteryUpperBridge","C20 zdejmowany górny próg +Y",q["bridge"],color)
for name,label,shape in [("C20_F0_OpenMount","C20 otwarty regulowany uchwyt F0",f0),
                         ("C20_Post_OpenSlottedMount","C20 podłużny uchwyt POST_F0",post)]:
    add(name,label,shape,mount_color)
for i,bolt in enumerate(q["bolts"],1):
    add(f"C20_Bridge_M3x12_{i}",f"M3 × 12 próg, strona {i}",bolt,(.61,.63,.66))
    x=(67.8,104.2)[i-1]; y=99.1; z=76.25
    vs=[V(x+3.18*math.cos(j*math.pi/3),
          y+3.18*math.sin(j*math.pi/3),z) for j in range(6)]
    nut=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,0,2.5))
    nut=nut.cut(g["bore"](x,y,z-.1,1.26,2.8))
    add(f"C20_Bridge_M3_Nut_{i}",f"M3 nakrętka progu {i}",nut,(.58,.59,.62))
for i,(key,(shape,actor,z,site,sample)) in enumerate(q["mta"].items()):
    add("C20_"+key,"C20 mały uchwyt "+key,shape,(.58,.38,.70))
    marker=replace("NIGHT_MTA0100335_UNKNOWN_"+str(i),box(*sample),
                   key+" | 32 × 18 × 18 mm PRÓBKA PROJEKTOWA, DOSTAWA UNKNOWN")
    marker.ViewObject.ShapeColor=(.75,.58,.82)
    marker.ViewObject.Transparency=48

f0body=replace("F0_FHAC0002_30A",box(*l["FUSE_FULL"]),"FHAC0002ZXJ | pełna projektowa obwiednia 21,5 mm, klapka do przymiarki")
f0body.ViewObject.ShapeColor=(.84,.35,.15)
postbody=replace("PBAY_POST_F0",box(*l["POST_FULL"]),"POST_F0 WAGO 221-412 | pełna obwiednia projektowa, zakres regulacji X58–84")
postbody.ViewObject.ShapeColor=(.31,.57,.44)
xt=replace("XT60H_mated_with_boots",box(*l["ACTIVE_M"]),"XT60H-M z osłoną | stała strona instalacji")
xt.ViewObject.ShapeColor=(.95,.65,.22);xt.ViewObject.Visibility=True
pack=add("C20_Pack_XT60_F","Fabryczna połówka F z odgiętką | obwiednia projektowa",box(*l["PACK_F"]),(.95,.67,.28))
ghost=add("C20_Pack_XT60_Stroke","Fabryczna F | skok 14 mm w +Y",box(14.25,57,132.25,36.25,82,148.75),(.95,.67,.28),False)
ghost.ViewObject.Transparency=68

def wire_object(name,label,paths,color):
    comp=Part.makeCompound([Part.makePolygon([V(*row) for row in points]) for points in paths])
    obj=add(name,label,comp,color,False)
    obj.ViewObject.LineColor=color;obj.ViewObject.LineWidth=3.4
    return obj

wire_objects=[
    wire_object("C20_BAT_Leads_Indicative","BAT obie fabryczne żyły | rejon zajęty",
                [x["states"]["seated"]["points"] for x in wires["battery_factory"].values()],(.81,.45,.18)),
    wire_object("C20_Inlet_W075","Przed ochroną W075 | oryginalna żyła F0",
                [wires["W075_factory_trim_at_robot_cup"]["points"]],(.68,.27,.14)),
    wire_object("C20_F0_Outlet_Ideal","Za F0 | pełna oryginalna żyła do POST_F0",
           [[[8,-66,141.25],[11,-76,141.25],[20,-83,141.25],[28,-86,141.25],[41,-86,144.12],[54,-86,147],[81,-86,147]]],(.78,.30,.17)),
    wire_object("C20_Protected_and_Return","Chroniony HELU i W001 | wejścia do wspólnej przestrzeni",
           [wires["W001_black_LAPP"]["points"],wires["W076_custom_HELU"]["points"]],(.18,.45,.55))
]
for name in ("H19_Wires_battery","I19_FiveGroundApproaches"):
    doc.getObject(name).ViewObject.Visibility=False
doc.recompute()
doc.commitTransaction()
doc.save()
print("20C native saved",doc.FileName,len(doc.Objects),flush=True)
