"""Shared v34 instance map. Geometry is authored with structured FreeCAD MCP.

No printable geometry is generated here. Units: millimetres in the CAD frame.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'hardware/skorupa/v34'
SOURCE = ROOT / 'hardware/skorupa/v33'
SOURCE_SHA = '8a6056496a2e4aeb1ad7b7887c94a9a9f4b9419e202aa05c7d2888851dbe07a4'
MASTER = OUT / 'TailSupport34.FCStd'
TARGET = OUT / 'Kot_v34_PODPARCIE_OGONA.FCStd'
PIVOT = [171., -6., 113.]
CAP_HOLES = [(158., 7.), (184., -19.)]
FOOT_HOLES = [(x, y) for x in (155., 187.) for y in (-16., 16.)]
HOUSING_HOLES = [(153., -10.), (153., 0.)]
# name: master, parent, moving, material, optional downward fastener placement
ADDITIONS = {
    'UpperHousing34': ('UpperHousing34', 'MG92BMount29', False, 'PETG', None),
    'BearingCap34': ('BearingCap34', 'UpperHousing34', False, 'PETG', None),
    'BearingLower34': ('Bearing608Lower34', 'UpperHousing34', False, '608ZZ envelope', None),
    'BearingUpper34': ('Bearing608Lower001', 'UpperHousing34', False, '608ZZ envelope', None),
    'OuterSpacer34': ('OuterSpacer34', 'UpperHousing34', False, 'PETG', None),
    'InnerSpacer34': ('InnerSpacer34', 'TailRoot29', True, 'PETG', None),
    'SpindleCap34': ('SpindleCap34', 'TailRoot29', True, 'PETG', None),
    'SpindleBolt34': ('BoltM3x30', 'TailRoot29', True, 'STEEL nominal fastener', (171., -6., 125.)),
    'SpindleNut34': ('NutM3Hex34', 'TailRoot29', True, 'STEEL nominal fastener', (171., -6., 98.4)),
}
for i, (x, y) in enumerate(CAP_HOLES):
    ADDITIONS[f'BearingCapBolt34_{i}'] = ('BoltM2x12', 'BearingCap34', False, 'STEEL nominal fastener', (x, y, 128.2))
    ADDITIONS[f'BearingCapNut34_{i}'] = ('NutM2', 'UpperHousing34', False, 'STEEL nominal fastener', (x, y, 119.2))
for i, (x, y) in enumerate(HOUSING_HOLES):
    ADDITIONS[f'HousingJointBolt34_{i}'] = ('BoltM3x12', 'UpperHousing34', False, 'STEEL nominal fastener', (x, y, 105.))
    ADDITIONS[f'HousingJointNut34_{i}'] = ('NutM3Hex34', 'MG92BMount29', False, 'STEEL nominal fastener', (x, y, 97.))
REPLACEMENTS = {'TailRoot29': ('SupportedRoot34', None), 'MG92BMount29': ('ServoSupport34', None)}
for i, (x, y) in enumerate(FOOT_HOLES):
    REPLACEMENTS[f'TailMountBolt29_{i}'] = ('BoltM3x16', (x, y, 41., 'up'))
    REPLACEMENTS[f'TailMountNut29_{i}'] = ('NutM3Hex34', (x, y, 53.))


def instance(master, source, xyz=None):
    import FreeCAD as A
    obj = master.getObject(source)
    shape = obj.Shape.copy()
    shape.Placement = obj.getGlobalPlacement() * obj.Placement.inverse() * shape.Placement
    if xyz:
        rotation = A.Rotation() if len(xyz) == 4 and xyz[3] == 'up' else A.Rotation(A.Vector(1, 0, 0), 180)
        shape.Placement = A.Placement(A.Vector(*xyz[:3]), rotation) * shape.Placement
    return shape
