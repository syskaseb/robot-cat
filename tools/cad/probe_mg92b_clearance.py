"""Conditional clearance study; a community envelope is NOT a measured horn."""
from pathlib import Path
import json
import pilot
from probe_mg92b_reference import OUT, sha


def main():
    import FreeCAD as A
    assert not A.GuiUp and not A.listDocuments()
    reference = OUT / "MG92BCommunityReference.FCStd"
    measurements = json.loads((OUT / "measurements.json").read_text())
    assert sha(reference) == measurements["reference_sha256"]
    main_files = [pilot.PARAMS, pilot.TARGET] + [pilot.CAD / "modules" / (n + ".FCStd") for n in pilot.MODULES]
    hashes = {p.relative_to(pilot.ROOT).as_posix(): sha(p) for p in main_files}
    assert hashes["hardware/cad/assembly/RobotCat.FCStd"] == "c8ee1484a1679b2dba4fae267e840a995bdba21719fb495ec324251b059490c7"
    assert hashes["hardware/cad/modules/tail/TailSupport.FCStd"] == "3397a14c969def1eb622b034f51e51f9706f138a8f235b24524522a5c5bfa78c"
    report = {"reference_sha256": sha(reference), "tool_sha256": sha(Path(__file__)),
              "unchanged_robot_files": hashes, "installed_in_robot": False,
              "print_ready": False, "proves_actual_horn_fit": False,
              "source_axis_point_mm": [6, 33.4, 6],
              "target_axis_point_mm": [171, -6, 91],
              "alignment": "ASSUMPTION: align community shaft tip to Adafruit shaft tip; cyclic XYZ -> YZX. Not a measured installed horn height.",
              "height_offsets_mm": [-1.8, 0, 1.8],
              "height_offset_basis": "Sensitivity scenarios, not tolerance bounds; 1.8 mm is the existing 36.8 vs 35 mm discrepancy between servo CAD and datasheet.",
              "scope": "Only seven PETG tail support parts; 24 clocking samples, not a sweep or whole-robot clearance proof.",
              "rows": []}
    try:
        ref = A.openDocument(str(reference))
        horn = ref.getObject("Fusion105").Shape.copy()
        horn.check(True)
        module = pilot.document(A, pilot.CAD / "modules/tail/TailSupport.FCStd")
        names = ["ServoSupport34", "SupportedRoot34", "UpperHousing34", "BearingCap34",
                 "OuterSpacer34", "InnerSpacer34", "SpindleCap34"]
        shapes = {name: pilot.global_shape(module.getObject(name)) for name in names}
        for shape in shapes.values():
            shape.check(True)
        base_rot = A.Rotation(A.Vector(1, 1, 1), 120)
        center = A.Vector(6, 33.4, 6)
        nominal = None
        for dz in report["height_offsets_mm"]:
            for angle in range(0, 360, 15):
                rotation = A.Rotation(A.Vector(0, 0, 1), angle) * base_rot
                placement = A.Placement(A.Vector(171, -6, 91 + dz) - rotation.multVec(center), rotation)
                moved = horn.copy()
                moved.Placement = placement * horn.Placement
                if dz == 0 and angle == 0:
                    nominal = moved.copy()
                intersections = {}
                for name, shape in shapes.items():
                    if moved.BoundBox.intersect(shape.BoundBox):
                        common = moved.common(shape)
                        # An empty/tangent intersection has no solid to BOP-check.
                        if common.Solids:
                            common.check(True)
                        if common.Solids and common.Volume > 0.001:
                            intersections[name] = common.Volume
                report["rows"].append({"height_offset_mm": dz, "clocking_deg": angle,
                                       "intersections_mm3": intersections})
        # Save only a small, isolated diagnostic copy; never the loaded modules.
        diagnostic = A.newDocument("MG92BClearanceReference")
        diagnostic.Label = "MG92B hypothetical horn clearance - NOT INSTALLED"
        for name, shape in {"CommunityHornEnvelope": nominal, **shapes}.items():
            obj = diagnostic.addObject("Part::Feature", name)
            obj.Shape = shape
            obj.addProperty("App::PropertyString", "Status", "Provenance")
            obj.Status = "Conditional reference only. Community horn envelope CC-BY-SA-4.0, Alberto / otrebla333."
        diagnostic.recompute()
        target = OUT / "MG92BClearanceReference.FCStd"
        assert not target.exists(), "Preserve previous diagnostic"
        diagnostic.saveAs(str(target))
        report["diagnostic_sha256"] = sha(target)
    finally:
        for name in list(A.listDocuments()):
            A.closeDocument(name)
    for path, digest in hashes.items():
        assert sha(pilot.ROOT / path) == digest, path
    report["summary"] = [{"height_offset_mm": dz,
                          "samples": 24,
                          "samples_with_intersection": sum(bool(r["intersections_mm3"]) for r in report["rows"] if r["height_offset_mm"] == dz),
                          "max_overlap_mm3": max((v for r in report["rows"] if r["height_offset_mm"] == dz for v in r["intersections_mm3"].values()), default=0)}
                         for dz in report["height_offsets_mm"]]
    (OUT / "conditional-clearance.json").write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(report["summary"]), flush=True)


if __name__ == "__main__":
    main()
