"""Tail support migration, not a geometry generator or a horn design.

Copy the saved v34 histories into owners, bind bearing-seat sketches with MCP,
then integrate into the validated AUX assembly. Existing v29 segments/servo
remain snapshots. Signed historical documents are never written.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "hardware/skorupa/v34/TailSupport34.FCStd"
SOURCE_SHA = "8d0ab83d3394a19e9d99115eaad3d2e0c0a8742269fde98fcd116da385376c39"
PREVIOUS_ASSEMBLY_SHA = "1a2e15163bbd7f5f86347e0211a053b680541c0868e2068ba0ba6cd43c9f8b41"
MODULES = {
    "tail/TailSupport": ["ServoSupport34", "SupportedRoot34", "UpperHousing34",
                         "BearingCap34", "OuterSpacer34", "InnerSpacer34", "SpindleCap34"],
    "tail/TailPurchased": ["Bearing608Lower34", "Bearing608Lower001", "BoltM3x16",
                           "BoltM3x30", "NutM3Hex34", "BoltM2x12", "NutM2", "BoltM3x12"],
}
VARIABLE_SET = "Tail_bearing_interface"


def mappings():
    sys.path.insert(0, str(ROOT / "tools/freecad/skorupa"))
    from support34 import REPLACEMENTS, ADDITIONS
    owners = {name: module for module, names in MODULES.items() for name in names}
    result = {n: (owners[src], src, xyz) for n, (src, xyz) in REPLACEMENTS.items()}
    result.update({n: (owners[src], src, xyz) for n, (src, _, _, _, xyz) in ADDITIONS.items()})
    assert len(result) == 27
    return result


def prepare():
    """GUI required for appearance. Read an independent saved source snapshot."""
    import shutil
    import tempfile
    import FreeCAD as A
    import pilot as p
    assert A.GuiUp
    p.check_baseline()
    assert p.sha(SOURCE) == SOURCE_SHA
    targets = [p.CAD / "modules" / (m + ".FCStd") for m in MODULES]
    assert all(not f.exists() for f in targets), "Do not overwrite existing owner documents"
    with tempfile.TemporaryDirectory(prefix="robot-cat-tail-source-") as tmp:
        saved = Path(tmp) / "TailMigrationSource.FCStd"
        shutil.copy2(SOURCE, saved)
        source = A.openDocument(str(saved), hidden=True)
        try:
            for module, names in MODULES.items():
                path = p.CAD / "modules" / (module + ".FCStd")
                path.parent.mkdir(parents=True, exist_ok=True)
                doc = A.newDocument(path.stem)
                for name in names:
                    obj = doc.copyObject(source.getObject(name), True)
                    assert obj.Name == name, (name, obj.Name)
                    obj.addProperty("App::PropertyString", "MigrationSource", "Traceability")
                    obj.MigrationSource = "v34/TailSupport34.FCStd#" + name
                doc.recompute()
                doc.Label = path.stem + " - inherited v34, PROTOTYPE"
                doc.saveAs(str(path))
        finally:
            A.closeDocument(source.Name)
    assert p.sha(SOURCE) == SOURCE_SHA
    print("Prepared two tail-support owner documents; assembly unchanged.")


def bind_interfaces():
    """Cross-document links are not exposed by structured MCP tools."""
    import FreeCAD as A
    import pilot as p
    var = p.document(A, p.PARAMS).getObject(VARIABLE_SET)
    assert var is not None, "Create the shared VarSet through MCP first"
    doc = p.document(A, p.CAD / "modules/tail/TailSupport.FCStd")
    link = doc.getObject("BearingInterface") or doc.addObject("App::Link", "BearingInterface")
    link.setLink(var)
    link.Visibility = False
    doc.recompute()
    doc.save()
    var.Document.save()


def integrate():
    import FreeCAD as A
    import pilot as p
    assert A.GuiUp
    p.check_baseline()
    assert p.sha(SOURCE) == SOURCE_SHA
    assert p.sha(p.TARGET) == PREVIOUS_ASSEMBLY_SHA, "Expected the validated AUX checkpoint"
    preflight = json.loads((p.CAD / "validation/tail-owners.json").read_text())
    assert preflight["source_sha256"] == SOURCE_SHA
    for module, digest in preflight["module_sha256"].items():
        assert p.sha(p.CAD / "modules" / (module + ".FCStd")) == digest
    modules = p.load_modules(A)
    d = p.document(A, p.TARGET)
    assert all(d.getObject(n).TypeId != "App::Link" for n in mappings()), "Already migrated or interrupted; inspect before retry"
    var = p.document(A, p.PARAMS).getObject(VARIABLE_SET)
    assert var is not None
    anchor = d.addObject("App::Link", "TailParameters")
    anchor.setLink(var)
    anchor.Label = "Tail bearing fit parameter (not a physical component)"
    anchor.Visibility = False
    for n, (owner, source, _) in mappings().items():
        p.replace_with_link(A, d, modules, n, owner, source)
        print("Linked " + n, flush=True)
    p.body_display({m: modules[m] for m in MODULES})
    # This Body is a Boolean input, not an additional physical component.
    modules["tail/TailSupport"].getObject("BearingSupport34").Visibility = False
    for m in MODULES:
        modules[m].save()
    d.recompute()
    assert d.getObject("RobotCatAssembly24").solve() == 0
    d.Label = "Robot cat - modular AUX and tail support - PROTOTYPE"
    d.save()
    rows = [{"component": n, "module": m, "object": d.getObject(n).LinkedObject.Name}
            for n, (m, _, _) in p.mappings().items()]
    p.write_report("link-map.json", {"baseline_sha256": p.BASE_HASH, "links": rows})
    print(json.dumps({"linked_components": len(rows), "tail_added": 27}))


def check_owners():
    """Before integration, compare every migrated source including its history."""
    import FreeCAD as A
    import pilot as p
    sys.path.insert(0, str(ROOT / "tools/freecad/skorupa"))
    from inheritance30 import compare_text
    assert p.sha(SOURCE) == SOURCE_SHA
    source = p.document(A, SOURCE)
    rows, sketches = [], []
    for module, names in MODULES.items():
        doc = p.document(A, p.CAD / "modules" / (module + ".FCStd"))
        doc.recompute()
        assert not any("Invalid" in obj.State for obj in doc.Objects)
        for name in names:
            obj = doc.getObject(name)
            original = source.getObject(name)
            assert obj.TypeId == original.TypeId
            old_shape, new_shape = p.global_shape(original), p.global_shape(obj)
            try:
                result = compare_text(old_shape.cleaned().exportBrepToString(), new_shape.cleaned().exportBrepToString())
                result["comparison_method"] = "BRep token equivalence"
            except AssertionError:
                assert name in MODULES["tail/TailSupport"], name
                result = compare_boolean_history(old_shape, new_shape)
            rows.append({"module": module, "object": name, **result})
        for obj in doc.Objects:
            if obj.TypeId == "Sketcher::SketchObject":
                assert obj.FullyConstrained and obj.solve() == 0, obj.Name
                sketches.append({"module": module, "sketch": obj.Name, "fully_constrained": True})
    p.write_report("tail-owners.json", {"source_sha256": SOURCE_SHA,
        "module_sha256": {n: p.sha(p.CAD / "modules" / (n + ".FCStd")) for n in MODULES},
        "objects": rows, "sketches": sketches, "passed": True})
    print(json.dumps({"owner_objects": len(rows), "constrained_sketches": len(sketches)}))


def compare_boolean_history(before, after):
    """Copied printable v34 histories can change BRep ordering on recompute.

    No alignment/healing; require strict valid solids and empty bidirectional
    differences. Never apply this fallback to the known-invalid old shells.
    """
    before.check(True)
    after.check(True)
    assert before.isValid() and after.isValid()
    assert len(before.Solids) == len(after.Solids) == 1
    forward, reverse = before.cut(after), after.cut(before)
    assert not forward.Solids and not reverse.Solids
    assert abs(forward.Volume) < 1e-10 and abs(reverse.Volume) < 1e-10
    bbox_error = max(abs(getattr(before.BoundBox, p) - getattr(after.BoundBox, p))
                     for p in ["XMin", "XMax", "YMin", "YMax", "ZMin", "ZMax"])
    volume_error = abs(before.Volume - after.Volume)
    area_error = abs(before.Area - after.Area)
    centre_error = (before.Solids[0].CenterOfMass - after.Solids[0].CenterOfMass).Length
    assert bbox_error < 1e-8 and volume_error < 1e-7 and area_error < 1e-6 and centre_error < 1e-8
    return {"comparison_method": "Strict-valid solid, empty bidirectional Boolean difference; no healing/alignment",
            "brep_token_equivalent": False, "difference_volumes_mm3": [forward.Volume, reverse.Volume],
            "bbox_error_mm": bbox_error, "volume_error_mm3": volume_error,
            "area_error_mm2": area_error, "centroid_error_mm": centre_error}


def perturb_bearings(parameter, assembly):
    """Both 608 seats are in UpperHousing34. The lower servo base must not change."""
    import FreeCAD as A
    import Part
    old = parameter.BearingSeatDiameter
    assert abs(float(old) - 22.2) < 1e-8
    names = ["MG92BMount29", "UpperHousing34"]
    parts = [assembly.getObject(n) for n in names]
    before = [o.Shape.Volume for o in parts]
    modules = {o.LinkedObject.Document for o in parts}
    sketches = [next(iter(modules)).getObject(n) for n in ["BearingSeat34", "UpperSeat34"]]
    changes = []
    annuli = [Part.makeCylinder(11.18, .2, A.Vector(171, -6, z - .1)).cut(
              Part.makeCylinder(11.12, .2, A.Vector(171, -6, z - .1))) for z in [106.5, 119.5]]
    upper = assembly.getObject("UpperHousing34")
    initial_wall = [upper.Shape.common(ring).Volume for ring in annuli]
    assert all(v > .01 for v in initial_wall), initial_wall

    def recompute():
        parameter.Document.recompute()
        for doc in modules:
            doc.recompute()
        assembly.recompute()

    try:
        parameter.BearingSeatDiameter = 22.4
        recompute()
        for sk in sketches:
            assert sk.FullyConstrained and sk.solve() == 0
            assert abs(sk.Geometry[0].Radius - 11.2) < 1e-8
        for obj, vol in zip(parts, before):
            delta = vol - obj.Shape.Volume
            if obj.Name == "UpperHousing34":
                assert delta > .01, (obj.Name, delta)
                # A thin annulus occupies the old wall at BOTH bearing midplanes;
                # after the diameter change it must be entirely in the clearance.
                for ring in annuli:
                    assert obj.Shape.common(ring).Volume < 1e-8
            else:
                assert abs(delta) < 1e-6, (obj.Name, delta)
            assert obj.Shape.isValid(), obj.Name
            changes.append({"component": obj.Name, "removed_volume_mm3": delta})
    finally:
        parameter.BearingSeatDiameter = old
        recompute()
    for obj, vol in zip(parts, before):
        assert abs(obj.Shape.Volume - vol) < 1e-6, obj.Name
    assert all(abs(upper.Shape.common(ring).Volume - vol) < 1e-8 for ring, vol in zip(annuli, initial_wall))
    return changes


def parameter_test():
    import FreeCAD as A
    import pilot as p
    p.load_modules(A)
    d = p.document(A, p.TARGET)
    var = p.document(A, p.PARAMS).getObject(VARIABLE_SET)
    changes = perturb_bearings(var, d)
    p.write_report("tail-parameter-update.json", {
        "assembly_sha256": p.sha(p.TARGET), "parameter_sha256": p.sha(p.PARAMS),
        "module_sha256": {n: p.sha(p.CAD / "modules" / (n + ".FCStd")) for n in MODULES},
        "parameter": "BearingSeatDiameter", "baseline_mm": 22.2, "test_mm": 22.4,
        "changes": changes, "restored": True, "cad_saved": False,
        "scope": "Both bearing seats in UpperHousing34 change; servo base stays unchanged. Not bearing size/axis/journal redesign or physical fit approval."})
    print(json.dumps({"checked_bodies": len(changes), "changed_bodies": 1, "restored": True}))


if __name__ == "__main__":
    {"parameter-test": parameter_test, "check-owners": check_owners}[sys.argv[1]]()
