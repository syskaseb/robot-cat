"""Isolated legacy shell topology investigation; never overwrites robot CAD."""
from pathlib import Path
import json
import sys
import time

import pilot

ROOT = pilot.ROOT
OUT = pilot.CAD / "studies/shell-repair"
SOURCE = pilot.CAD / "modules/shell/Shell.FCStd"
SOURCE_SHA = "20d7a1a5058cbe03e0c748938533b0cb58b2fb17159c11dd79533b8bf1e1a9d7"


def describe(shape):
    started = time.monotonic()
    errors = []
    try:
        shape.check(True)
    except Exception as exc:
        errors.append(str(exc))
    b = shape.BoundBox
    return {"valid": shape.isValid(), "strict_bop_errors": errors,
            "elapsed_seconds": time.monotonic() - started,
            "volume_mm3": shape.Volume, "area_mm2": shape.Area,
            "solids": len(shape.Solids), "faces": len(shape.Faces),
            "bbox_mm": [b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax]}


def scan():
    import FreeCAD as A
    import Part
    assert pilot.sha(SOURCE) == SOURCE_SHA
    OUT.mkdir(parents=True, exist_ok=True)
    doc = pilot.document(A, SOURCE)
    report = {"source_sha256": SOURCE_SHA, "freecad": list(A.Version()),
              "occt": Part.OCC_VERSION, "cad_saved": False, "objects": []}
    for name in ["Shell35Source", "Shell35"]:
        shape = doc.getObject(name).Shape.copy()
        print("Inspect", name, flush=True)
        info = describe(shape)
        info["name"] = name
        info["spline_faces"] = []
        for index, face in enumerate(shape.Faces, 1):
            surface = face.Surface
            if isinstance(surface, Part.BSplineSurface):
                info["spline_faces"].append({"face": index,
                    "continuity": str(surface.Continuity), "u_degree": surface.UDegree,
                    "v_degree": surface.VDegree, "u_multiplicities": surface.getUMultiplicities(),
                    "v_multiplicities": surface.getVMultiplicities(), "area_mm2": face.Area})
        path = OUT / (name + ".brep")
        shape.exportBrep(str(path))
        info["brep_sha256"] = pilot.sha(path)
        report["objects"].append(info)
        print(json.dumps({k: v for k, v in info.items() if k != "spline_faces"}), flush=True)
    assert pilot.sha(SOURCE) == SOURCE_SHA
    (OUT / "baseline.json").write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")


def native_trials():
    import FreeCAD as A
    import Part
    report = []
    for name in ["Shell35Source", "Shell35"]:
        source = Part.Shape()
        source.read(str(OUT / (name + ".brep")))
        for mode in ["fix", "same-parameter"]:
            shape = source.copy()
            print("Native trial", name, mode, flush=True)
            if mode == "fix":
                shape.fix(1e-7, 1e-7, 1e-5)
            else:
                Part.ShapeFix.sameParameter(shape, True, 1e-7)
            info = describe(shape)
            info.update(source=name, mode=mode)
            report.append(info)
            print(json.dumps(info), flush=True)
    (OUT / "native-trials.json").write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")


def continuity_trial():
    # Runs in isolated cadquery-ocp 7.8.1.1 Python, NEVER in the FreeCAD process:
    # both bind OCCT DLLs and must exchange BRep files, not loaded libraries.
    from importlib.metadata import version
    from OCP.BRep import BRep_Builder
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape
    from OCP.GeomAbs import GeomAbs_C1
    from OCP.ShapeUpgrade import ShapeUpgrade_ShapeDivideContinuity
    from OCP.ShapeFix import ShapeFix_Shape
    from OCP.ShapeExtend import ShapeExtend_DONE, ShapeExtend_FAIL
    assert version("cadquery-ocp") == "7.8.1.1"
    baseline = json.loads((OUT / "baseline.json").read_text())
    assert pilot.sha(SOURCE) == baseline["source_sha256"] == SOURCE_SHA
    rows = []
    for name in ["Shell35Source", "Shell35"]:
        path = OUT / (name + ".brep")
        assert pilot.sha(path) == next(r["brep_sha256"] for r in baseline["objects"] if r["name"] == name)
        shape = TopoDS_Shape()
        assert BRepTools.Read_s(shape, str(path), BRep_Builder())
        print("Divide C0 geometry", name, flush=True)
        tool = ShapeUpgrade_ShapeDivideContinuity(shape)
        tool.SetBoundaryCriterion(GeomAbs_C1)
        tool.SetPCurveCriterion(GeomAbs_C1)
        tool.SetSurfaceCriterion(GeomAbs_C1)
        tool.SetTolerance(1e-7)
        tool.SetTolerance2d(1e-9)
        tool.SetPrecision(1e-7)
        tool.SetMinTolerance(1e-7)
        tool.SetMaxTolerance(1e-5)
        performed = tool.Perform()
        result = tool.Result()
        assert not result.IsNull()
        split_path = OUT / (name + "-c1.brep")
        assert BRepTools.Write_s(result, str(split_path))
        print("ShapeFix", name, flush=True)
        fixer = ShapeFix_Shape(result)
        fixer.SetPrecision(1e-7)
        fixer.SetMinTolerance(1e-7)
        fixer.SetMaxTolerance(1e-5)
        fixed = fixer.Perform()
        fixed_path = OUT / (name + "-c1-fixed.brep")
        assert BRepTools.Write_s(fixer.Shape(), str(fixed_path))
        rows.append({"source": name, "input_sha256": pilot.sha(path),
                     "performed": performed, "done": tool.Status(ShapeExtend_DONE),
                     "failed": tool.Status(ShapeExtend_FAIL), "fix_performed": fixed,
                     "split_sha256": pilot.sha(split_path), "fixed_sha256": pilot.sha(fixed_path)})
    report = {"cadquery_ocp": version("cadquery-ocp"), "vtk": version("vtk"),
              "spatial_tolerance_mm": 1e-7, "max_tolerance_mm": 1e-5,
              "pcurve_tolerance": 1e-9, "rows": rows, "accepted": False,
              "note": "Candidates only; FreeCAD strict-BOP and geometry comparisons required"}
    (OUT / "continuity-trial.json").write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(report), flush=True)


def candidate_audit():
    """Check each candidate in FreeCAD; never install an unvalidated repair."""
    import FreeCAD as A
    import Part
    assert not A.listDocuments(), "Run candidate audit in a fresh FreeCAD Python process"
    assert pilot.sha(SOURCE) == SOURCE_SHA
    trial = json.loads((OUT / "continuity-trial.json").read_text())
    baseline = json.loads((OUT / "baseline.json").read_text())
    report = {"source_sha256": SOURCE_SHA, "freecad": list(A.Version()),
              "occt": Part.OCC_VERSION, "rows": [], "installed": False,
              "print_ready": False, "complete": False}
    mode = sys.argv[2] if len(sys.argv) > 2 else "fixed"
    assert mode in {"fixed", "split"}
    suffix = "-c1-fixed" if mode == "fixed" else "-c1"
    output = OUT / ("audit-" + mode + ".json")
    for row in trial["rows"]:
        name = row["source"]
        path = OUT / (name + suffix + ".brep")
        assert pilot.sha(path) == row[mode + "_sha256"]
        shape = Part.Shape()
        shape.read(str(path))
        print("FreeCAD strict BOP", path.name, flush=True)
        info = describe(shape)
        old = next(r for r in baseline["objects"] if r["name"] == name)
        info.update(source=name, candidate=path.name, candidate_sha256=pilot.sha(path),
                    volume_delta_mm3=shape.Volume-old["volume_mm3"],
                    area_delta_mm2=shape.Area-old["area_mm2"],
                    max_bbox_delta_mm=max(abs(a-b) for a,b in zip(info["bbox_mm"],old["bbox_mm"])))
        # This is only a topology gate, not surface equivalence or fit approval.
        info["topology_passed"] = info["valid"] and not info["strict_bop_errors"] and info["solids"] == 1
        report["rows"].append(info)
        output.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
        print(json.dumps(info), flush=True)
    assert pilot.sha(SOURCE) == SOURCE_SHA
    report["complete"] = True
    output.write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")


def locate_faults():
    """Localize continuity/curve faults only, NOT a full Boolean safety audit."""
    from OCP.BRep import BRep_Builder
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape
    from OCP.TopExp import TopExp
    from OCP.TopTools import TopTools_IndexedMapOfShape
    from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE
    from OCP.BOPAlgo import BOPAlgo_ArgumentAnalyzer
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    from importlib.metadata import version

    assert version("cadquery-ocp") == "7.8.1.1"
    baseline = json.loads((OUT / "baseline.json").read_text())
    assert pilot.sha(SOURCE) == baseline["source_sha256"] == SOURCE_SHA
    report = {"source_sha256": SOURCE_SHA, "cadquery_ocp": version("cadquery-ocp"),
              "scope": "Only continuity and curve-on-surface localization; not full BOP",
              "rows": [], "installed": False, "print_ready": False}
    for old in baseline["objects"]:
        path = OUT / (old["name"] + ".brep")
        assert pilot.sha(path) == old["brep_sha256"]
        shape = TopoDS_Shape()
        assert BRepTools.Read_s(shape, str(path), BRep_Builder())
        faces, edges = TopTools_IndexedMapOfShape(), TopTools_IndexedMapOfShape()
        TopExp.MapShapes_s(shape, TopAbs_FACE, faces)
        TopExp.MapShapes_s(shape, TopAbs_EDGE, edges)
        analyzer = BOPAlgo_ArgumentAnalyzer()
        analyzer.SetShape1(shape)
        for mode in ("ArgumentTypeMode", "SelfInterMode", "SmallEdgeMode",
                     "RebuildFaceMode", "TangentMode", "MergeVertexMode", "MergeEdgeMode"):
            setattr(analyzer, mode, False)
        analyzer.ContinuityMode = True
        analyzer.CurveOnSurfaceMode = True
        analyzer.StopOnFirstFaulty = False
        analyzer.SetRunParallel(False)
        print("Localize", old["name"], flush=True)
        analyzer.Perform()
        assert not analyzer.HasErrors(), "OCCT analyzer execution error"
        faults = []
        for result in analyzer.GetCheckResult():
            items = []
            for faulty in result.GetFaultyShapes1():
                box = Bnd_Box()
                BRepBndLib.AddOptimal_s(faulty, box, False, False)
                items.append({"shape_type": str(faulty.ShapeType()),
                              "face_index": faces.FindIndex(faulty) or None,
                              "edge_index": edges.FindIndex(faulty) or None,
                              "bbox_xyz_min_max_mm": list(box.Get())})
            faults.append({"status": str(result.GetCheckStatus()), "subshapes": items})
        report["rows"].append({"source": old["name"], "brep_sha256": pilot.sha(path),
                               "faults": faults})
        print(old["name"], len(faults), "localized faults", flush=True)
    assert pilot.sha(SOURCE) == SOURCE_SHA
    (OUT / "fault-locations.json").write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")


def package_report():
    """Freeze rejected evidence, not a CAD/print release."""
    from release_check import verify, REQUIRED_GATES
    assert pilot.sha(SOURCE) == SOURCE_SHA
    names = ["baseline.json", "continuity-trial.json", "audit-split.json",
             "audit-fixed.json", "fault-locations.json", "README.md"]
    for mode in ("split", "fixed"):
        report = json.loads((OUT / ("audit-" + mode + ".json")).read_text())
        assert report["complete"] and not report["installed"] and not report["print_ready"]
        assert len(report["rows"]) == 2 and all(not r["topology_passed"] for r in report["rows"])
    files = [OUT / name for name in names] + [SOURCE, pilot.TARGET]
    files += [ROOT / "tools/cad" / name for name in (
        "shell_repair_study.py", "test_shell_repair_study.py", "pilot.py", "tail_module.py", "release_check.py")]
    manifest = {
        "schema_version": 1, "checkpoint": "shell-repair-rejected-c1-study",
        "readiness": "concept", "scope": "Diagnostic evidence only; all four candidates rejected; no CAD installed.",
        "toolchain": {"freecad": "1.1.3", "occt": "7.8.1", "cadquery-ocp": "7.8.1.1", "vtk": "9.3.1"},
        "derived_files_not_shipped": "Six ignored BReps; regenerate from pinned Shell.FCStd with scan and continuity-trial. Hashes are in reports.",
        "files": [{"path": p.relative_to(ROOT).as_posix(), "sha256": pilot.sha(p)} for p in files],
        "gates": {gate: {"status": "fail" if gate == "geometry" else "open",
                         "reason": "Strict BOP failed; all candidates rejected." if gate == "geometry"
                         else "Not validated by this isolated topology study."} for gate in sorted(REQUIRED_GATES)},
    }
    assert verify(ROOT, manifest)["integrity_ok"]
    assert not verify(ROOT, manifest, True)["integrity_ok"]
    (OUT / "study-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps({"files": len(files), "readiness": "concept", "geometry": "fail"}), flush=True)


if __name__ == "__main__":
    commands = {"scan": scan, "native-trials": native_trials, "continuity-trial": continuity_trial,
                "candidate-audit": candidate_audit, "locate-faults": locate_faults,
                "package-report": package_report}
    command = sys.argv[1]
    if command in {"scan", "native-trials", "candidate-audit"}:
        import FreeCAD as A
        if A.GuiUp or A.listDocuments():
            raise RuntimeError("Use a fresh headless FreeCAD Python worker, not the interactive session")
        try:
            commands[command]()
        finally:
            for name in list(A.listDocuments()):
                A.closeDocument(name)
    else:
        commands[command]()
