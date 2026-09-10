"""Reshape existing native muzzle lofts; run through FreeCAD MCP.

Ellipse editing uses the Python fallback because MCP sketch tools expose
circles/arcs/lines but no ellipse geometry. No mesh or frozen BRep replacement.
"""
import FreeCAD as App
import Part
import Sketcher


def reshape(doc):
    assert doc.Name == 'WAVEGO_cat_mechanical'
    assert doc.getObject('CAT_Face_Mask').Tip.Name == 'All_face_ports_and_screw_access'
    assert abs(doc.getObject('All_face_ports_and_screw_access').Length.Value - 42) < 0.001
    for side, cx in [('Left', -25.0), ('Right', 25.0)]:
        for suffix, depth, major, minor in [
            ('root', -188.8, 20.0, 13.0),
            ('tip', -210.0, 18.0, 11.7),
            ('round_end', -225.0, 0.8, 0.52),
        ]:
            sketch = doc.getObject(side + '_muzzle_' + suffix)
            for index in reversed(range(sketch.ConstraintCount)):
                sketch.delConstraint(index)
            for index in reversed(range(sketch.GeometryCount)):
                sketch.delGeometry(index)
            index = sketch.addGeometry(Part.Ellipse(App.Vector(cx, 155, 0), major, minor), False)
            sketch.addConstraint(Sketcher.Constraint('Block', index))
            offset = sketch.AttachmentOffset
            offset.Base.z = depth
            sketch.AttachmentOffset = offset
    # Extend the existing aperture operation forward as well, without moving
    # or resizing its sensor windows or screw axes. Pocket length is set by
    # MCP modify_property before this function is run.
    port = doc.getObject('Final_face_sensor_and_M3_axes')
    offset = port.AttachmentOffset
    offset.Base.z = -228
    port.AttachmentOffset = offset
    doc.recompute()
    mask = doc.getObject('CAT_Face_Mask')
    assert mask.Shape.isValid() and len(mask.Shape.Solids) == 1
    assert mask.Shape.BoundBox.XMin < -224
    return dict(valid=mask.Shape.isValid(), solids=len(mask.Shape.Solids),
                xmin=mask.Shape.BoundBox.XMin, volume=mask.Shape.Volume)
