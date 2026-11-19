from pathlib import Path
import runpy,json,FreeCAD as A,Part
P=Path(__file__).parent;D=A.ActiveDocument
assert Path(D.FileName).resolve()==(P/"whole-cat19C.FCStd").resolve()
rows=json.loads((P/"two-head-jr-units.json").read_bytes())
lines=[q for r in rows for q in [r["centreline"]]+[a["centreline"] for a in r["fans"]]]
o=D.getObject("C19_JR300HeadPair") or D.addObject("Part::Feature","C19_JR300HeadPair")
o.Shape=Part.makeCompound([Part.makePolygon([A.Vector(*p) for p in path]) for path in lines])
o.ViewObject.LineColor=(.82,.27,.19);o.ViewObject.LineWidth=3;o.ViewObject.Visibility=False
runpy.run_path(str(P/"views.py"))

