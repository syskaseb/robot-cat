"""Inspect cached BReps from Dtto without loading foreign Python proxies.

The upstream arm is a simplified clearance reference, not a horn specification.
"""
from pathlib import Path
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "hardware/cad/_supplier-research-20260923/Dttov2.0.1.FCStd"
OUT = ROOT / "hardware/reference/mg92b-horn-2026-09-23"
UPSTREAM = "https://raw.githubusercontent.com/otrebla333/Dtto-Modular-Robot/b4b97069888079e5726600969b8e0783bfe2514f/3D-printing/Freecad-files/Dttov2.0.1.FCStd"
SOURCE_SHA = "8630500f6c58886f5fd953bc3f3eae5b0fe36cff955ad65be77af65bea2c1cb1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    import FreeCAD as A
    import Part
    if A.GuiUp or A.listDocuments():
        raise RuntimeError("Fresh headless worker required")
    assert sha(SOURCE) == SOURCE_SHA
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"source_url": UPSTREAM, "source_sha256": SOURCE_SHA,
              "author": "Alberto / otrebla333, Dtto Modular Robot",
              "license": "CC-BY-SA-4.0 (upstream README)",
              "freecad": list(A.Version()), "occt": Part.OCC_VERSION,
              "upstream_document_opened": False, "installed_in_robot": False,
              "supplier_certified": False, "print_ready": False, "objects": []}
    doc = A.newDocument("MG92BCommunityReference")
    try:
        with zipfile.ZipFile(SOURCE) as archive:
            tree = ET.fromstring(archive.read("Document.xml"))
            objects = {o.attrib["name"]: o for o in tree.findall("./ObjectData/Object")}
            for name in ("Fusion105", "Cut158"):
                element = objects[name]
                part_file = element.find("./Properties/Property[@name='Shape']/Part").attrib["file"]
                shape = Part.Shape()
                shape.importBrepFromString(archive.read(part_file).decode("utf-8"))
                shape.check(True)
                b = shape.BoundBox
                row = {"source_object": name,
                       "label": element.find("./Properties/Property[@name='Label']/String").attrib["value"],
                       "source_brep_sha256": hashlib.sha256(archive.read(part_file)).hexdigest(),
                       "valid": shape.isValid(), "strict_bop_passed": True,
                       "solids": len(shape.Solids), "volume_mm3": shape.Volume,
                       "bbox_xyz_min_max_mm": [b.XMin, b.YMin, b.ZMin, b.XMax, b.YMax, b.ZMax],
                       "size_xyz_mm": [b.XLength, b.YLength, b.ZLength],
                       "cylinders": [], "primitive_inputs": []}
                for i, face in enumerate(shape.Faces, 1):
                    if isinstance(face.Surface, Part.Cylinder):
                        s = face.Surface
                        row["cylinders"].append({"face": i, "radius_mm": s.Radius,
                                                 "axis": list(s.Axis), "center": list(s.Center)})
                if name == "Fusion105":
                    for link in element.findall("./Properties/Property[@name='Shapes']/LinkList/Link"):
                        primitive = objects[link.attrib["value"]]
                        row["primitive_inputs"].append({"name": primitive.attrib["name"],
                            "properties_xml": ET.tostring(primitive.find("Properties"), encoding="unicode")})
                feature = doc.addObject("Part::Feature", name)
                feature.Label = row["label"] + " - community simplified reference"
                feature.Shape = shape
                feature.addProperty("App::PropertyString", "SourceURL", "Provenance")
                feature.SourceURL = UPSTREAM
                feature.addProperty("App::PropertyString", "Limitations", "Provenance")
                feature.Limitations = "Simplified third-party geometry; not manufacturer tolerance, spline or screw specification."
                report["objects"].append(row)
        doc.recompute()
        target = OUT / "MG92BCommunityReference.FCStd"
        if target.exists():
            raise FileExistsError("Preserve prior reference; do not overwrite")
        doc.saveAs(str(target))
        report["reference_sha256"] = sha(target)
    finally:
        A.closeDocument(doc.Name)
    report["tool_sha256"] = sha(Path(__file__))
    (OUT / "measurements.json").write_text(json.dumps(report, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
