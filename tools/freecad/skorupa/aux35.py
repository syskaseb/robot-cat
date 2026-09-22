"""v35 signed inputs and instance map; no generated printable geometry."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'hardware/skorupa/v34'
SOURCE_SHA = 'b3b342604b649bde0f2224462c6ea8d241b0b2a4d46479756a4aad8877da7182'
OUT = ROOT / 'hardware/skorupa/v35'
MASTER = OUT / 'AuxPower35.FCStd'
TARGET = OUT / 'Kot_v35_ZASILANIE_AUX.FCStd'
HOLES = [(x, y) for x in (91.74, 127.3) for y in (-21.46, -6.22)]
REPLACEMENTS = {'AuxBuck': ('AuxReference35', None),
                'Part__Feature038': ('Deck35', None),
                'ShellMounted20': ('Shell35', None),
                'TailBridge29': ('TailBridge35', None)}
# master object, parent, material, translation
ADDITIONS = {}
for i, (x, y) in enumerate(HOLES):
    parent = 'Part__Feature038' if i < 2 else 'TailBridge29'
    ADDITIONS['AuxPost35_' + str(i)] = ('Post35_' + str(i), parent, 'PETG', None)
    ADDITIONS['AuxBolt35_' + str(i)] = ('BoltM2x19', 'AuxBuck' if i<2 else 'TailBridge29', 'STEEL M2x19 nominal', (x,y,53.5748) if i<2 else (x,y,41,'up'))
    ADDITIONS['AuxNut35_' + str(i)] = ('NutM2', 'Part__Feature038' if i<2 else 'AuxBuck', 'STEEL M2 nut nominal', (x,y,37.02) if i<2 else (x,y,53.5748,'up'))
for i in range(2):
    ADDITIONS['AuxTerminal35_' + str(i)] = ('AuxTerminal35_' + str(i), 'AuxBuck', 'PURCHASED terminal envelope', None)


def instance(doc, name, xyz=None):
    import FreeCAD as A
    o = doc.getObject(name)
    if o is None:
        matches = doc.getObjectsByLabel(name)
        assert len(matches) == 1, name
        o = matches[0]
    s = o.Shape.copy()
    s.Placement = o.getGlobalPlacement() * o.Placement.inverse() * s.Placement
    if xyz:
        rotation=A.Rotation(A.Vector(1,0,0),180) if len(xyz)==4 and xyz[3]=='up' else A.Rotation()
        s.Placement=A.Placement(A.Vector(*xyz[:3]),rotation)*s.Placement
    return s
