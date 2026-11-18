"""Read the affected rigid groups and installed neighbors from the active 98 copy."""
import json
from pathlib import Path
import FreeCAD as App

doc = App.ActiveDocument
out = Path(__file__).parent
assert Path(doc.FileName).resolve() == (out / "whole-front.FCStd").resolve()
prefixes = ("Yaw", "MG92", "P01_", "P02_", "F2_", "F3_", "HEAD_", "D18C_", "PBAY_", "S0_", "CF17_", "OP_", "Battery", "Speaker", "Pi", "PCA", "BUS255", "E1_", "Monitor", "BNO085", "MAX98", "ReSpeaker", "TTP", "Camera3", "VL53", "WAGO", "Motor_ATO", "NIGHT_INLINE", "YAW_FIXED", "YAW_REAL", "H01_", "HN_", "D18B_INLINE", "BASE0_", "F0_", "MAIN_", "AUX_", "RG_", "CONTINUOUS", "POWER_", "STRUCTURAL", "P03_", "Tail608", "TAIL_")
rows = {}
for obj in doc.Objects:
    if not obj.Name.startswith(prefixes) or not obj.ViewObject.Visibility or not hasattr(obj, "Shape"):
        continue
    box = obj.Shape.BoundBox
    if box.isValid():
        rows[obj.Name] = [round(x, 4) for x in (box.XMin, box.YMin, box.ZMin, box.XMax, box.YMax, box.ZMax)]
(out / "front-source.json").write_bytes((json.dumps(rows, indent=1) + "\n").encode())
print(len(rows))
