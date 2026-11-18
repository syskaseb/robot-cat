"""Seat the two fixed JR interfaces against installed hardware in the final saved model."""
import json
import runpy
from pathlib import Path
import numpy as np
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir

folder = Path(__file__).parent
model = runpy.run_path(str(folder / "saved-front.py"))["Saved"](folder / "front-insert-current.FCStd")
routes = json.loads((folder / "insert-regions.json").read_bytes())
yaw = routes["JR_factory"][0]
tip = np.array(yaw["key_tip"])
axis = np.array(yaw["key_axis"])
axis /= np.linalg.norm(axis)
width = np.cross(axis, [0, 0, 1])
width /= np.linalg.norm(width)
up = np.cross(axis, width)
# The factory-key tip is the mating plane. Each half of the project bound
# extends 15 mm along its own side of that plane.
corner = tip - 15 * axis - 7 * width - 5 * up
reference = gp_Ax2(gp_Pnt(*corner), gp_Dir(*up), gp_Dir(*axis))
model.shapes["C_HY_full_pair"] = BRepPrimAPI_MakeBox(reference, 30, 14, 10).Shape()
joins = json.loads((folder / "connected-JR300.json").read_bytes())["poses"][0]["three_lap_centers"]
fields = ["C_HY_full_pair"]
for number, (x, y, z) in enumerate(joins, 1):
    name = "fixed_lap_" + str(number)
    # Each lane reserves 6 mm width/height on 6 mm centers. Its 26 mm
    # length covers the 8 mm lap plus intact 9 mm insulation at both ends.
    model.shapes[name] = BRepPrimAPI_MakeBox(gp_Pnt(x - 13, y - 3, z - 3), 26, 6, 6).Shape()
    fields.append(name)
neighbors = ["Pi4B_actual_PCB","Pi_components_and_cooling","PCA9685_Adafruit815_PCB","E1_populated_prototype_board",
             "F2_COMMON_PI_BUS_PCA_RECEIVER","FRONT18_LOWER_BEARING_FRAME","FRONT18_FORE_NEG_PANEL","FRONT18_FORE_POS_PANEL",
             "MG92B_Head_yaw","HEAD_YAW_FORK_FIXED_PITCH_HOUSING","INSERT_HEAD_BACK","INSERT_FRONT_NEG","INSERT_FRONT_POS",
             "BUS25514_installed","CF17_POL1992_FULL_MATED_BODY","TTP223_touch"]
neighbors += [n for n in model.members if n.startswith(("WAGO415_data","Motor_ATO4A_"))]
results = []
for reference_name in fields:
    for neighbor in neighbors:
        result = model.common(reference_name, neighbor)
        if result.get("bounds_separation_mm", 0) <= 2:
            results.append(dict(field=reference_name, neighbor=neighbor, **result))
evidence = dict(yaw_tip=tip.tolist(), yaw_mated_field_mm=[30,14,10], yaw_source_connections=["XB12 F_HY.out to C_HY.V+",
    "XB13 C_HY.GND to G_AUX.4", "XS13 R1.2 to C_HY.PWM"], pitch_far_end_existing=["XB23","XB22","XS23"],
    three_lap_centers=joins, lane_bounds_mm=[26,6,6], lap_mm=8, sleeve_mm=20, insulated_lands_mm=[9,9],
    near=results, scope="Current neutral fixed receiver fields. 6 mm is the proposed allocation per sleeve, not a measured heat-shrink OD. Fan-out, opposite board wires and holding are open.",
    physical_PASS=False)
(folder / "fixed-ends.json").write_bytes((json.dumps(evidence, indent=2)+"\n").encode())
print([r for r in results if r.get("common_mm3",0) > .001])
