"""Save an isolated working copy and record visible source actors without interpreting visibility as BOM."""
from pathlib import Path
import json,hashlib,datetime
import FreeCAD as A,FreeCADGui as G
P=Path(__file__).parent
D=A.ActiveDocument
src=P.parent/"day18-body-reception-and-closed-fit"/"body-reception.FCStd"
assert hashlib.sha256(src.read_bytes()).hexdigest()=="486abd0561488c91ea7d09344476c3b63c636c5f785238faa34ac36f7bf910d4"
assert Path(D.FileName).resolve()==src.resolve()
D.saveAs(str(P/"whole19.FCStd"))
rows=[]
for o in D.Objects:
    if not o.ViewObject.Visibility or not hasattr(o,"Shape") or o.Shape.isNull():continue
    b=o.Shape.BoundBox
    rows.append(dict(name=o.Name,label=o.Label,type=o.TypeId,bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],volume=o.Shape.Volume,solids=len(o.Shape.Solids),group=[x.Name for x in getattr(o,"InList",[])]))
(P/"source-visible-actors.json").write_bytes((json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),rows=rows),indent=1)+"\n").encode())
print("SAVED19",len(rows),D.FileName)
