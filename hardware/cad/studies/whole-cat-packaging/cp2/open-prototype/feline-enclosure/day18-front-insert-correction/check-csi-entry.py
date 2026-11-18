"""Bound only the part of the existing ribbon approaching the fixed CSI port."""
import json
import runpy
from pathlib import Path
import numpy as np

p = Path(__file__).parent
model = runpy.run_path(str(p / "saved-front.py"))["Saved"](p / "front-insert-current.FCStd")
routes = json.loads((p / "insert-regions.json").read_bytes())["FFC"]
reserve = model.bounds("Pi_components_and_cooling")
cells = []
for route in routes:
    corners = np.array(route["corners"])
    for a, b in zip(corners, corners[1:]):
        vertices = np.vstack([a, b])
        lo = np.maximum(reserve[:3], vertices.min(axis=0))
        hi = np.minimum(reserve[3:], vertices.max(axis=0))
        if np.all(hi >= lo):
            cells.append(np.r_[lo, hi])
cells = np.array(cells)
channel = np.r_[cells[:,:3].min(axis=0), cells[:,3:].max(axis=0)]
neighbors = ["Pi4B_actual_PCB", "Pi_USB_DATA_Delock_mating", "CF17_POL1992_FULL_MATED_BODY",
             "CF17_POWER_K1474_SEALED_BOOT_FULL"] + sorted(n for n in model.members if n.startswith("CF17_PI_PRIMARY_"))
gaps = {}
for name in neighbors:
    b = model.bounds(name)
    gap = np.maximum(0, np.maximum(b[:3] - channel[3:], channel[:3] - b[3:]))
    gaps[name] = round(float(np.linalg.norm(gap)),5)
result = dict(poses=len(routes), free_profile=[16.8,1.8], source_air_field_mm=reserve.tolist(),
    sampled_CSI_ribbon_channel_bbox_mm=channel.tolist(), scope="Union bound of ribbon cell boxes clipped to the existing components/cooling reservation. Nine given poses. Bounds have no extra allowance for latch operation, physical clearance, twist spring-back or continuous motion.",
    endpoint=routes[0]["centreline"][-1], gap_lower_bounds_to_named_model_boxes_mm=gaps,
    physical_unknowns=["real cooler and air path","latch travel and access with cable inserted","ribbon twist and slack"],physical_PASS=False)
(p / "csi-entry.json").write_bytes((json.dumps(result,indent=1)+"\n").encode())
print(channel, gaps)
