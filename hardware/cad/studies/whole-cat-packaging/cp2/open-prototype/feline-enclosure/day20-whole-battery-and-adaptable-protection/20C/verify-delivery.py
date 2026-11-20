"""Verify the 20C handoff, changed mesh solids, and retained native datums."""
import hashlib
import json
import os
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import FreeCAD as App
import Mesh
import Part
from datetime import datetime as timestamp, timezone as time_zone

folder=Path(__file__).resolve().parent
root=folder.parent
native=folder/"whole-cat20C.FCStd"
manifest=json.loads((folder/"20C-manifest.json").read_bytes())
received=json.loads((root/"20B-RECEIPT.json").read_bytes())
def sha(p):
    with p.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()
for name,pin in received["pins"].items():
    assert sha(root/name)==pin,name
assert sha(root/"20B-RECEIPT.json")==manifest["source"]["received20B_manifest_sha256"]
assert sha(native)==manifest["native"]["sha256"]
assert manifest["native"]["modified"] is False
def shapes(z):
    t=ET.fromstring(z.read("Document.xml"))
    out={}
    for o in t.findall("./ObjectData/Object"):
        r=o.find('./Properties/Property[@name="Shape"]/Part')
        if r is not None:
            out[o.get("name")]=r.get("file")
    return out,t
retained=["Battery_GEA223S30X6GT","B19_ToolEightAnchors","S0_body","S0_neck","S0_key",
          "Pi4B_actual_PCB","Pi_components_and_cooling","AUX_Pololu4092","MAIN_Pololu4853",
          "BNO085","PCA9685_Adafruit815_PCB","E19_BatteryDoor","NIGHT_INLINE_RR_W052",
          "NIGHT_INLINE_RR_W053","E19_KeyedTail","D19D_YawMatedPair","MG92B_Tail"]
with ZipFile(root/"whole-cat20A.FCStd") as z0,ZipFile(native) as z1:
    a,t0=shapes(z0);b,t1=shapes(z1)
    lost=set(x.get("name") for x in t0.findall("./ObjectData/Object"))-set(x.get("name") for x in t1.findall("./ObjectData/Object"))
    assert not lost,lost
    assert len(t1.findall("./ObjectData/Object"))==manifest["native"]["object_count"]
    for n in retained:
        q0=z0.read(a[n]);q1=z1.read(b[n])
        if q0!=q1:
            x0=Part.Shape();x0.importBrepFromString(q0.decode("latin1"))
            x1=Part.Shape();x1.importBrepFromString(q1.decode("latin1"))
            assert abs(x0.Volume-x1.Volume)<1e-6,n
            v0=x0.BoundBox;v1=x1.BoundBox
            assert max(abs(getattr(v0,k)-getattr(v1,k)) for k in ("XMin","XMax","YMin","YMax","ZMin","ZMax"))<1e-6,n
    def solid(name):
        s=Part.Shape()
        s.importBrepFromString(z1.read(b[name]).decode("latin1"))
        return s
    changed_base=solid("E19_RearBase")
    upper_bridge=solid("C20_BatteryUpperBridge")
    def land_area(region,dz):
        V=App.Vector
        x0,y0,z0,x1,y1,z1=region
        clip=Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
        foot=changed_base.common(clip)
        upper=upper_bridge.common(clip)
        upper.translate(V(0,0,dz))
        return round(abs(foot.common(upper).Volume/dz),3)
    contacts={
       "left_bearing":land_area([64.75,95.05,81.5,70.6,102.87,82.5],-.02),
       "right_bearing":land_area([101.5,95.05,81.5,107.32,102.87,82.5],-.02),
       "rib_77_underside":land_area([77,89.8,73.7,80.2,94.45,74.75],.02),
       "rib_94_underside":land_area([94,89.8,73.7,97.2,94.45,74.75],.02)
    }
    assert min(contacts.values())>3,contacts
    print("bearing witness",contacts,flush=True)
    assert z1.testzip() is None
names={row["part"] for row in manifest["changed_prints"]}
assert len(names)==9
checks={}
for part in manifest["changed_prints"]:
    stem=part["part"]
    assert part["qty"]==1
    stl=folder/part["stl"]
    step=folder/part["step"]
    assert sha(stl)==part["stl_sha256"],stem
    assert sha(step)==part["step_sha256"],stem
    body=Part.read(str(step))
    assert len(body.Solids)==1 and body.isValid(),stem
    mesh=Mesh.Mesh(str(stl))
    assert mesh.CountFacets==part["stl_facets"],stem
    assert part['stl_reopened_watertight'] and mesh.CountFacets>4,stem
    dims=[round(mesh.BoundBox.XLength+16,2),round(mesh.BoundBox.YLength+16,2),round(mesh.BoundBox.ZLength+8,2)]
    assert max(abs(a-b) for a,b in zip(dims,part['with_8mm_brim_each_side_8mm_support_z']))<=.03 and max(dims)<=256,(stem,dims)
    checks[stem]={"watertight_stl":True,"valid_step":True,"envelope_mm":dims}
    print(stem,dims,flush=True)
assert {x.stem for x in (folder/"parts").glob("*.stl")}==names
assert {x.stem for x in (folder/"parts").glob("*.step")}==names
for link in re.findall(r"\]\(([^)]+)\)",(folder/"20C-INSTRUKCJA.md").read_text(encoding="utf-8")):
    assert (folder/link).is_file(),link
result={
    "verified_utc":timestamp.now(time_zone.utc).isoformat(),
    "native_sha256":sha(native),"retained_selected_shape_count":len(retained),
    "construction_commit_source":manifest["source"]["commit"],
    "received_20B_pins_verified":len(received["pins"]),
    "contacts_witness_area_mm2":contacts,"print_delta":checks,"native":manifest["native"],
    "actualfit":None,"cut":None,"slack":None,"physicalPASS":False,
}
file=folder/"20C-delivery-verification.json"
stage=file.with_suffix(".tmp")
with stage.open("x",encoding="utf-8",newline="\n") as f:
    json.dump(result,f,ensure_ascii=False,indent=2);f.write("\n")
os.replace(stage,file)
print("20C export and source verification complete",sha(file),flush=True)