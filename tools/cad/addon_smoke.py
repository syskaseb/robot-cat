"""Verify the pinned Fasteners API without modifying the robot document."""
from pathlib import Path
import sys


def run():
    import FreeCAD as A
    addon = Path(A.getUserAppDataDir()) / "Mod/fasteners"
    sys.path.insert(0, str(addon))
    import FastenersCmd
    import pilot
    d = A.newDocument("RobotCatFastenersSmoke")
    try:
        obj = d.addObject("PartDesign::FeaturePython", "SmokeM2x12")
        FastenersCmd.FSScrewObject(obj, "ISO4762", None)
        obj.Diameter = "M2"
        d.recompute()
        obj.Length = "12"
        obj.Thread = False
        d.recompute()
        assert obj.Shape.isValid() and len(obj.Shape.Solids) == 1
        assert obj.Diameter == "M2" and obj.Length == "12"
        report = {"addon": "Fasteners", "shape": "ISO4762 M2x12", "valid": True,
                  "solids": len(obj.Shape.Solids), "volume_mm3": obj.Shape.Volume,
                  "FreeCAD": A.Version()[:3], "robot_changed": False}
        pilot.write_report("fasteners-smoke.json", report)
        print(report)
    finally:
        A.closeDocument(d.Name)


if __name__ == "__main__":
    run()
