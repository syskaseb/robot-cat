"""Read supplier STEP files without touching the robot or a running GUI.

Run with FreeCAD's bundled Python. Writes only derived inspection metadata.
This verifies import/geometry, NOT fit, part revision, loads, or print readiness.
"""

import hashlib
import json
from pathlib import Path

import FreeCAD
import Part


root = Path(__file__).resolve().parent
results = []
for path in sorted(root.glob("*.step")):
    shape = Part.Shape()
    shape.read(str(path))
    bbox = shape.BoundBox
    results.append(
        {
            "file": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "solids": len(shape.Solids),
            "valid": shape.isValid(),
            "size_xyz_mm": [bbox.XLength, bbox.YLength, bbox.ZLength],
            "minimum_xyz_mm": [bbox.XMin, bbox.YMin, bbox.ZMin],
            "maximum_xyz_mm": [bbox.XMax, bbox.YMax, bbox.ZMax],
        }
    )
if len(results) != 4:
    raise RuntimeError("Expected four supplier STEP files; unpack sources.zip first")
if not all(row["valid"] and row["solids"] for row in results):
    raise RuntimeError("At least one supplier STEP failed geometry validation")
report = {
    "freecad_version": FreeCAD.Version(),
    "scope": "STEP import and validity only; no robot fit or manufacturing approval",
    "models": results,
}
target = root / "step-inspection.json"
target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
