from pathlib import Path
import FreeCAD as A,FreeCADGui as G,json
P=Path(__file__).parent;C=P.parent/"day19-closed-head-neck-and-module-interfaces";D=A.ActiveDocument
assert Path(D.FileName).resolve()==(P/"whole-cat19D.FCStd").resolve()
src=(C/"views.py").read_text()
skins=[o.Name for o in D.Objects if o.Name.startswith("D19D_") and o.Name not in ("D19D_FrontFloor","D19D_OpticsCarrier","D19D_ToF","D19D_HeadServoWires","D19D_YawMatedPair","D19D_YawTieRail","D19D_YawSaddle")]
fields=["C19_FFC190","D19D_ToF","D19D_HeadServoWires","B19_TailJRUnderBank","B19_TailLaps"]
V=A.Vector;v=G.activeDocument().activeView()
for n in ["C19_ToFLeadSet","C19_HeadFactory250Pair","C19_JR300HeadPair"]:D.getObject(n).ViewObject.Visibility=False
exec(src[src.index("air="):src.index("D.recompute()")])
D.recompute();D.save()
(P/"views-receipt.json").write_bytes((json.dumps(dict(objects=len(D.Objects),skins=skins,fields=fields),indent=1)+"\n").encode())

