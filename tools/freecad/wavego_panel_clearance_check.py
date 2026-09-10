"""Check the raised PETG floor over the unmodified WAVEGO side panels.

Run inside FreeCAD through MCP. Measurements are nominal CAD dimensions,
not a slicer or strength certification. Does not save or edit the model.
"""
import json
from pathlib import Path

import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[2]


def check(doc):
    assert doc.Name == "WAVEGO_cat_mechanical"
    body = doc.getObject("CAT_Base_Chassis_Tray")
    shape = body.Shape.copy()
    shape.Placement = body.getGlobalPlacement()
    assert shape.isValid() and len(shape.Solids) == 1
    panels = []
    for label in ("SidePanel", "SidePanel001"):
        obj = doc.getObjectsByLabel(label)[0]
        panel = obj.Shape.copy()
        panel.Placement = obj.getGlobalPlacement()
        volume = shape.common(panel).Volume
        gap = shape.distToShape(panel)[0]
        assert volume < 0.001, (label, volume)
        assert gap >= 0.499, (label, gap)
        panels.append(dict(label=label, overlap_mm3=volume, gap_mm=gap))

    # Test the continuous roof material, not just the total bounding box.
    roof = []
    for x in (-84, -40, 0, 40, 80, 126):
        for y in (-48, -38, -28, 28, 38, 48):
            probe = Part.makeLine(App.Vector(x, y, 36), App.Vector(x, y, 42))
            edges = probe.common(shape).Edges
            assert len(edges) == 1, (x, y, len(edges))
            box = edges[0].BoundBox
            assert abs(box.ZMin - 39.02) < 0.001, (x, y, box)
            assert abs(box.ZMax - 41.42) < 0.001, (x, y, box)
            roof.append(dict(x=x, y=y, thickness_mm=edges[0].Length))

    # The eight chassis fasteners retain the original measured XY axes.
    axes = [(x, y) for x in (-80, -70, 112, 122) for y in (-22.5, 22.5)]
    for x, y in axes:
        shaft = Part.makeCylinder(1.25, 10.0, App.Vector(x, y, 37.02))
        assert shaft.common(shape).Volume < 0.001, (x, y)
        mount_name = "CAT_Neck_Load_Frame" if x < 0 else "CAT_Tail_Mount"
        mount = doc.getObject(mount_name).Shape
        assert shaft.common(mount).Volume < 0.001, (mount_name, x, y)

    mount_reliefs = []
    for name, sample_x in (("CAT_Neck_Load_Frame", -84), ("CAT_Tail_Mount", 126)):
        mount = doc.getObject(name).Shape
        assert mount.isValid() and len(mount.Solids) == 1
        assert mount.common(shape).Volume < 0.001, name
        for y in (-28, 28):
            probe = Part.makeLine(App.Vector(sample_x, y, 39), App.Vector(sample_x, y, 45.7))
            edges = probe.common(mount).Edges
            assert len(edges) == 1, (name, y, len(edges))
            box = edges[0].BoundBox
            assert abs(box.ZMin - 41.62) < 0.001, (name, y, box)
            assert abs(box.ZMax - 45.62) < 0.001, (name, y, box)
            mount_reliefs.append(dict(part=name, y=y, thickness_mm=edges[0].Length,
                                      floor_gap_mm=box.ZMin - 41.42))

    result = dict(
        panels=panels, roof_probes=roof, mount_reliefs=mount_reliefs,
        nominal_roof_thickness_mm=2.4,
        nominal_panel_clearance_mm=0.5, chassis_axes_unchanged=axes,
        valid=True, solids=1,
        limits=["36 sampled roof lines, not a global minimum-wall analysis.",
                "CAD clearance only; PETG shrinkage and strength need testing.",
                "Head/tail actuation and other reported collisions remain open."],
    )
    destination = ROOT / "hardware/wavego/mechanics/panel-clearance-validation.json"
    destination.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
