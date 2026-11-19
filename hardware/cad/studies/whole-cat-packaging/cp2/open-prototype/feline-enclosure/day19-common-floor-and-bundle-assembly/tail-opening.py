"""Extend only the aft end of the Y-swing opening at the measured interference."""
from pathlib import Path
import FreeCAD as A,FreeCADGui as G,Part
P=Path(__file__).parent;D=A.ActiveDocument;V=A.Vector
assert Path(D.FileName).resolve()==(P/"whole-cat19B.FCStd").resolve()
skin=D.D19_ROUNDED_REAR_COWL
skin.Shape=skin.Shape.cut(Part.makeBox(22,19,30,V(174.5,1,144))).removeSplitter()
assert len(skin.Shape.Solids)==1 and skin.Shape.isValid()
D.recompute()
closure=(P/"close-shared-interface.py").read_text(encoding="utf8")
exec(closure[closure.index("v=G.activeDocument()"):closure.index("D.recompute();D.save()",closure.index("v=G.activeDocument()"))])
G.runCommand("Std_Save")

