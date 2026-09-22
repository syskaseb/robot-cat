"""Isolated tail spindle-nut service study; NEVER integrates or approves a horn.

The pocket is authored with structured FreeCAD MCP. This file copies histories,
checks the resulting cut and tests a sampled nut-only insertion corridor.
"""
from pathlib import Path
import json
import shutil
import sys
import tempfile

import pilot

ROOT = pilot.ROOT
OUT = pilot.CAD / "studies/tail-coupling"
STUDY = OUT / "TailCouplingService.FCStd"
SOURCE = pilot.CAD / "modules/tail/TailSupport.FCStd"
SOURCE_SHA = "3397a14c969def1eb622b034f51e51f9706f138a8f235b24524522a5c5bfa78c"
ASSEMBLY_SHA = "c8ee1484a1679b2dba4fae267e840a995bdba21719fb495ec324251b059490c7"


def prepare():
    import FreeCAD as A
    assert A.GuiUp
    assert pilot.sha(SOURCE) == SOURCE_SHA
    assert not STUDY.exists(), "Do not overwrite a study"
    doc = A.listDocuments().get("TailCouplingService")
    if doc is None:
        doc = A.newDocument("TailCouplingService")
    assert not doc.Objects and not doc.FileName, "Only reuse the empty failed copy attempt"
    OUT.mkdir(parents=True, exist_ok=True)
    # Required by copyObject for source documents with external dependencies.
    doc.saveAs(str(STUDY))
    source = pilot.document(A, SOURCE)
    obj = doc.copyObject(source.getObject("SupportedRoot34"), True)
    assert obj.Name == "SupportedRoot34"
    for key, value in {
        "DesignStatus": "SERVICE STUDY ONLY, not installed; horn unmeasured; no print approval",
        "MaterialSpec": "PETG",
        "StudySourceSHA256": SOURCE_SHA,
    }.items():
        if key not in obj.PropertiesList:
            obj.addProperty("App::PropertyString", key, "Traceability")
        setattr(obj, key, value)
    obj.ViewObject.DisplayModeBody = "Tip"
    obj.ViewObject.ShapeColor = (.18, .21, .25)
    doc.Label = "Tail spindle nut service study - NOT INSTALLED"
    doc.recompute()
    doc.save()
    print("Independent root history saved; create the service pocket with MCP.")


def audit():
    import FreeCAD as A
    import Part
    from tail_module import compare_boolean_history
    assert not A.GuiUp and not A.listDocuments(), "Audit in a fresh headless FreeCAD Python process"
    assert pilot.sha(SOURCE) == SOURCE_SHA
    assert pilot.sha(pilot.TARGET) == ASSEMBLY_SHA
    main_files = [pilot.PARAMS, pilot.TARGET] + [pilot.CAD / "modules" / (n + ".FCStd") for n in pilot.MODULES]
    hashes = {p.relative_to(ROOT).as_posix(): pilot.sha(p) for p in main_files}
    print("Checking isolated relocation...", flush=True)
    # Open only the copied file before any source document can satisfy a stale
    # external reference through FreeCAD's document cache. Never save CAD here.
    with tempfile.TemporaryDirectory(prefix="robot-cat-tail-service-") as folder:
        relocated = Path(folder) / STUDY.name
        shutil.copy2(STUDY, relocated)
        copied = A.openDocument(str(relocated))
        copied.recompute()
        assert len(A.listDocuments()) == 1, "Study must not auto-load external CAD"
        assert all(o.TypeId != "App::Link" for o in copied.Objects)
        relocated_shape = pilot.global_shape(copied.getObject("SupportedRoot34"))
        assert relocated_shape.isValid() and len(relocated_shape.Solids) == 1
        assert all(o.FullyConstrained and o.solve() == 0 for o in copied.Objects
                   if o.TypeId == "Sketcher::SketchObject")
        A.closeDocument(copied.Name)
        assert pilot.sha(relocated) == pilot.sha(STUDY), "Relocation test cannot save CAD"
    source = pilot.document(A, SOURCE)
    doc = pilot.document(A, STUDY)
    doc.recompute()
    body = doc.getObject("SupportedRoot34")
    before = pilot.global_shape(source.getObject("SupportedRoot34"))
    after = pilot.global_shape(body)
    relocation_comparison = compare_boolean_history(relocated_shape, after)
    cutter = Part.makeBox(8, 5.7, 2.5, A.Vector(171, -8.85, 95.9))
    intended = before.cut(cutter)
    equivalence = compare_boolean_history(intended, after)
    after.check(True)
    assert after.isValid() and len(after.Solids) == 1
    assert not after.cut(before).Solids, "No added material is allowed in this study"
    removed = before.Volume - after.Volume
    assert .01 < removed < cutter.Volume
    sketches = [o for o in doc.Objects if o.TypeId == "Sketcher::SketchObject"]
    assert all(o.FullyConstrained and o.solve() == 0 for o in sketches)

    print("Loading unchanged robot and its 320 physical components...", flush=True)
    assembly = pilot.document(A, pilot.TARGET)
    plan = json.loads((pilot.BASE / "assembly-plan.json").read_text())
    shapes = {r["name"]: pilot.global_shape(assembly.getObject(r["name"])) for r in plan["components"]}
    nut = shapes["SpindleNut34"]
    new_shapes = dict(shapes, TailRoot29=after)
    # Remove only the service nut itself and the explicitly withdrawn axial bolt.
    ignored = {"SpindleNut34", "SpindleBolt34"}

    def common(a, b):
        if not a.BoundBox.intersect(b.BoundBox):
            return 0.0
        assert a.isValid() and b.isValid(), "Cannot clear an invalid intersecting solid"
        return abs(a.common(b).Volume)

    rows, checked = [], set()
    old_peak = retained_bolt_peak = 0.0
    print("Checking 39 nut insertion samples...", flush=True)
    for i in range(39):
        dx = 9.5 - .25 * i
        moved = nut.copy()
        moved.translate(A.Vector(dx, 0, 0))
        old_overlap = common(moved, before)
        bolt_overlap = common(moved, shapes["SpindleBolt34"])
        old_peak = max(old_peak, old_overlap)
        retained_bolt_peak = max(retained_bolt_peak, bolt_overlap)
        collisions = []
        for name, shape in new_shapes.items():
            if name in ignored or not moved.BoundBox.intersect(shape.BoundBox):
                continue
            checked.add(name)
            overlap = common(moved, shape)
            if overlap > .001:
                collisions.append({"component": name, "overlap_mm3": overlap})
        assert not collisions, (dx, collisions)
        rows.append({"nut_shift_x_mm": dx, "collisions": collisions,
                     "old_root_overlap_mm3": old_overlap,
                     "retained_axial_bolt_overlap_mm3": bolt_overlap})
        if i % 10 == 0:
            print(f"  {i + 1}/39 samples checked", flush=True)
    assert old_peak > 1, "The original root must reject this side-loading path"
    assert retained_bolt_peak > 1, "The installed axial bolt must reject nut removal"
    def seat_contact(shape):
        def top_planes(s):
            return [f for f in s.Faces if isinstance(f.Surface, Part.Plane)
                    and abs(f.CenterOfMass.z - 98.4) < 1e-7
                    and abs(f.normalAt(0, 0).z) > .999999]
        return sum(f.common(g).Area for f in top_planes(shape) for g in top_planes(nut))
    original_contact, new_contact = seat_contact(before), seat_contact(after)
    assert original_contact > 5 and abs(original_contact - new_contact) < 1e-6
    box = after.BoundBox
    assert max(box.XLength, box.YLength, box.ZLength) < 256
    assert all(pilot.sha(ROOT / p) == digest for p, digest in hashes.items())
    report = {
        "scope": "Standalone PETG side-loading nut study; not installed in the robot; no horn created or approved",
        "study_sha256": pilot.sha(STUDY), "tool_sha256": pilot.sha(Path(__file__)),
        "unchanged_robot_files": hashes, "cad_saved_by_audit": False,
        "relocation": {"fresh_process": True, "documents_loaded": 1,
                       "external_links": 0, "comparison": relocation_comparison},
        "expected_cut_comparison": equivalence, "removed_volume_mm3": removed,
        "solid_count": len(after.Solids), "strict_bop_passed": True,
        "fully_constrained_sketches": [o.Name for o in sketches],
        "envelope_mm": [box.XLength, box.YLength, box.ZLength],
        "nut_seat_contact_mm2": {"baseline": original_contact, "study": new_contact,
                                 "top_z_mm": 98.4, "preserved": True},
        "nut_path": {"method": "39 samples at 0.25 mm along X; not swept-volume/tool/hand proof",
                     "required_removed_components": ["SpindleBolt34"],
                     "narrow_phase_components": sorted(checked), "samples": rows,
                     "original_root_rejects_path": True, "retained_bolt_rejects_path": True},
        "remaining": ["Measured MG92B horn and screw", "Weakened collar load/creep assessment", "PETG proof test",
                      "Tool and cable envelopes", "Integration and new native/dynamic tests"],
        "print_release": False,
    }
    (OUT / "service-audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps({"removed_mm3": removed, "nut_path_samples": len(rows), "standalone_only": True}))


def package():
    """Pin this isolated study without changing the robot's declared readiness."""
    from release_check import verify
    report = json.loads((OUT / "service-audit.json").read_text())
    assert report["study_sha256"] == pilot.sha(STUDY)
    assert report["tool_sha256"] == pilot.sha(Path(__file__))
    assert not report["print_release"]
    assert report["relocation"]["documents_loaded"] == 1
    for name, digest in report["unchanged_robot_files"].items():
        assert pilot.sha(ROOT / name) == digest, name
    paths = [ROOT / name for name in report["unchanged_robot_files"]]
    paths += [STUDY, OUT / "service-audit.json", OUT / "README.md", OUT / "service-root.png",
              pilot.CAD / "validation/before-tail-coupling.png", pilot.CAD / "toolchain.json",
              pilot.BASE / "assembly-plan.json", ROOT / ".gitattributes"]
    paths += [ROOT / "tools/cad" / name for name in
              ["tail_service_study.py", "pilot.py", "tail_module.py", "release_check.py", "test_tail_service_study.py"]]
    assert len(paths) == len(set(paths))
    audit_path = (OUT / "service-audit.json").relative_to(ROOT).as_posix()
    manifest = {
        "schema_version": 1, "checkpoint": "tail-spindle-nut-service-study", "readiness": "concept",
        "baseline_commit": "98f466ef5628614f0e66a8cec9990869e173a9a5",
        "scope": "Standalone modified root only, NOT integrated; robot CAD unchanged; no physical horn approval",
        "files": [{"path": p.relative_to(ROOT).as_posix(), "sha256": pilot.sha(p)} for p in paths],
        "gates": {
            "geometry": {"status": "pass", "reason": "Study root only: one strict-valid solid, intended subtraction, standalone reopen. Not the robot shell.", "evidence": [audit_path]},
            "assembly": {"status": "open", "reason": "Not installed. Measured horn and new native joint/motion checks missing."},
            "fit": {"status": "open", "reason": "Nominal M3 nut and 0.25 mm sampled path only; physical nut/PETG fit unmeasured."},
            "petg": {"status": "open", "reason": "Printer profile, supports, slot bridging and orientation trials missing."},
            "loads": {"status": "open", "reason": "Side slot weakens collar; layer strength and creep not approved."},
            "electrical": {"status": "open", "reason": "Servo/horn/screw and cable service envelopes incomplete."},
            "service": {"status": "open", "reason": "Nut-only path, axial bolt removed; no tool/hand/swept-volume/full assembly proof."}
        }
    }
    assert verify(ROOT, manifest)["integrity_ok"]
    assert not verify(ROOT, manifest, True)["integrity_ok"]
    output = ROOT / "hardware/releases/tail-service-study.json"
    output.write_text(json.dumps(manifest, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps({"manifest": str(output), "files": len(paths), "readiness": "concept"}))


if __name__ == "__main__":
    {"audit": audit, "package": package}[sys.argv[1]]()
