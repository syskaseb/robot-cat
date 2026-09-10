"""Validate the native FreeCAD face revision, not print/optical certification."""
import json
from pathlib import Path
import FreeCAD as App
import Part

ROOT = Path(__file__).resolve().parents[2]


def check(doc):
    assert doc.Name == 'WAVEGO_cat_mechanical'
    result = {'geometry': {}, 'face_screw_axes': [], 'limits': [
        'Sensor envelopes are not exact purchased-part optics.',
        'Open bores do not certify full camera/ToF field of view.',
        'Head/tail actuators, screw lengths, print supports and loads remain pending.',
    ]}
    shapes = {}
    for name in ('CAT_Head_Shell', 'CAT_Face_Mask'):
        obj = doc.getObject(name)
        shape = obj.Shape.copy()
        shape.Placement = obj.getGlobalPlacement()
        assert shape.isValid() and len(shape.Solids) == 1, name
        shapes[name] = shape
        result['geometry'][name] = dict(valid=True, solids=1, volume_mm3=shape.Volume)
    for y in (-47, 47):
        for z in (166, 194):
            shaft = Part.makeCylinder(1.5, 32, App.Vector(-206, y, z), App.Vector(1, 0, 0))
            for name, shape in shapes.items():
                assert shaft.common(shape).Volume < 0.001, (name, y, z)
            result['face_screw_axes'].append([y, z])
    dome = doc.getObject('FelineFaceDome')
    assert dome.Placement.Base.Length < 1e-8 and dome.Placement.Rotation.Angle < 1e-8, \
        'Nested Boolean operand must use parent-local placement'
    assert abs(doc.getObject('Dome_PETG_2_4mm').Value.Value - 2.4) < 0.001
    result['dome_thickness_setting_mm'] = 2.4
    result['mask_head_intersection_mm3'] = shapes['CAT_Face_Mask'].common(shapes['CAT_Head_Shell']).Volume
    assert result['mask_head_intersection_mm3'] < 0.001
    # These probes check open centres, not off-axis rays or sensor dimensions.
    result['open_optical_centres'] = []
    for label, y, z in [('Camera', 18, 187), ('IR', -22, 190), ('ToF', 0, 157)]:
        ray = Part.makeCylinder(1, 26, App.Vector(-206, y, z), App.Vector(1, 0, 0))
        assert ray.common(shapes['CAT_Face_Mask']).Volume < 0.001, label
        result['open_optical_centres'].append(label)
    (ROOT / 'hardware/wavego/mechanics/cute-face-validation.json').write_text(
        json.dumps(result, indent=2), encoding='utf-8')
    return result
