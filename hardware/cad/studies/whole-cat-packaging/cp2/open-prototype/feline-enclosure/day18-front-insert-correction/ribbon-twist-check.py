"""Measure the two straight twists actually encoded in the nine FFC ribbon profiles."""
from pathlib import Path
import json
import math
import numpy as np

folder = Path(__file__).parent
poses = json.loads((folder / "insert-regions.json").read_bytes())["FFC"]
out = []
for row in poses:
    points = np.array(row["centreline"])
    corners = np.array(row["corners"])
    wide = (corners[:, 1] - corners[:, 0]) / 16.8
    thick = (corners[:, 2] - corners[:, 1]) / 1.8
    tangent = np.cross(wide, thick)
    runs = []
    current = None
    for i, length in enumerate(np.linalg.norm(np.diff(points, axis=0), axis=1)):
        twist = math.atan2(np.cross(wide[i], wide[i+1]) @ tangent[i], wide[i] @ wide[i+1])
        if abs(twist) < 1e-7 or np.linalg.norm(tangent[i]-tangent[i+1]) > 1e-7:
            current = None
            continue
        if current is None:
            current = dict(length_mm=0., turn_deg=0., start=points[i].tolist())
            runs.append(current)
        current["length_mm"] += length
        current["turn_deg"] += math.degrees(twist)
        current["end"] = points[i+1].tolist()
    out.append(dict(yaw=row["yaw"], pitch=row["pitch"], straight_twist_runs=runs,
        source_direction=tangent[0].tolist(), source_width=wide[0].tolist(),
        fixed_direction=tangent[-1].tolist(), fixed_width=wide[-1].tolist()))
result = dict(poses=out, scope="Rotation of the model's 16.8 mm profile about each straight centerline. Geometry only. Physical installed twist capacity and 190 mm usable stock require the actual ribbon.")
(folder / "ribbon-twist.json").write_bytes((json.dumps(result, indent=1)+"\n").encode())
print([(p["yaw"],p["pitch"],[(round(r["length_mm"],2),round(r["turn_deg"],2)) for r in p["straight_twist_runs"]]) for p in out])
