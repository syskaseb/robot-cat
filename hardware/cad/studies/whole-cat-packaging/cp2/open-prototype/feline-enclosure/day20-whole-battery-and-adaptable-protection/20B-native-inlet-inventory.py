"""Extract world BRep bounds for the altered 20B battery bay and MTA stations."""
import json
import os
import re
from pathlib import Path
from runpy import run_path
from xml.etree import ElementTree as ET

from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box

folder = Path(__file__).resolve().parent
reader_path = folder.parent / "day18-front-insert-correction" / "saved-front.py"
Saved = run_path(str(reader_path))["Saved"]
source = Saved(folder / "whole-cat20A.FCStd")
frame = ET.fromstring(source.zip.read("GuiDocument.xml"))
visible = {vp.get("name"): vp.find('./Properties/Property[@name="Visibility"]/Bool').get("value") == "true"
           for vp in frame.findall("./ViewProviderData/ViewProvider")
           if vp.find('./Properties/Property[@name="Visibility"]/Bool') is not None}
names = re.compile(
    r"Battery|XT60|F0|^S0_(body|neck|key|ring)|^NIGHT_(MTA0100335|INLINE_)"
    r"|^I19_FuseBand|^H19_(FrontFrame|MainTrunk|TailSideTransfer|PowerBranch)"
    r"|^E19_(RearBase|BatteryDoor|ForeBase|ForeLid|RearLid|MTA_sample_land|Wago|BUS)"
    r"|^F19_(ForeCap|RearCap)|Pi_components|^Pi4B_actual_PCB|^B19_ToolEightAnchors|^WAGO615_power_0_0"
    r"|^PBAY_|^G19_(Group|Lay)|^D19_(BODY|SIDE|DATA|JR)"
    r"|^PCA9685_Adafruit815_PCB|^E1_populated|^BNO085$|^MAX98357"
    r"|^MAIN_Pololu|^AUX_Pololu|^Monitor_|^OP_S1_PRIMARY|^R7|^Motor_ATO|^E19_FieldAxial"
    r"|^MG92B_Tail|^D19D_YawMatedPair|^H19_DATA_A_Boot|^G19_PiAudioBoot"
)
rows = {}
for name in source.members:
    if not names.search(name):
        continue
    shape = source.shape(name)
    if shape.IsNull():
        continue
    box = source.bounds(name)
    rows[name] = {"bounds": box.round(4).tolist(), "visible": visible.get(name)}
    if name in {"XT60H_mated_with_boots", "E19_BatteryDoor", "E19_MTA_sample_land",
                "Battery_GEA223S30X6GT", "F0_FHAC0002_30A", "PBAY_POST_F0"}:
        solids = []
        it = TopExp_Explorer(shape, TopAbs_SOLID)
        while it.More():
            b = Bnd_Box()
            BRepBndLib.AddOptimal_s(it.Current(), b, False, False)
            solids.append([round(v, 4) for v in (*b.CornerMin().Coord(), *b.CornerMax().Coord())])
            it.Next()
        rows[name]["solid_bounds"] = solids

result = folder / "20B-native-inlet-inventory.json"
temp = result.with_suffix(".tmp")
with temp.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump({"source": "whole-cat20A.FCStd", "scope": "named interfaces", "members": rows}, stream, indent=2)
    stream.write("\n")
os.rename(temp, result)
for name, row in rows.items():
    print(name, row["bounds"], "visible" if row["visible"] else "", row.get("solid_bounds", []))