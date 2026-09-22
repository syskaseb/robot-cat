"""Read-only BRep diagnostics for the recovered shell before installation."""
from pathlib import Path
import FreeCAD as A
import Part
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'hardware/skorupa/v33/shape-cache/mesh-proof'
s=Part.Shape();s.read(str(BASE/'maker_volume_all_0.brep'))
try: print('BOP',s.check(True),flush=True)
except Exception as exc:print('BOP',repr(exc),flush=True)
o=A.openDocument(str(ROOT/'hardware/skorupa/v32/OpticsDesign32.FCStd'))
for n in ['OpticalReserve32','ToFWireReserve32']:
    c=s.common(o.getObject(n).Shape)
    print(n,c.isValid(),c.Volume,flush=True)
