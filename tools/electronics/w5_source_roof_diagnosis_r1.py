"""Receive saved failed roof topology without rebuilding it."""
from pathlib import Path
import json
import FreeCAD as A
ROOT=Path(__file__).resolve().parents[2]
d=A.openDocument(str(ROOT/'hardware/cad/studies/w5-source-roof-native-r1/SourceProtectiveHoods.FCStd'))
rows=[]
for name in ['UpperCurvedSkin','ContinuousSourceRoof','WestCurvedHood','EastCurvedHood','FourBoredCoverPosts','SourceRoofCoverFinished','WestHoodFinished','EastHoodFinished']:
    s=d.getObject(name).Shape
    try:errors=str(s.check(True))
    except Exception as exc:errors=str(exc)
    row=dict(name=name,valid=s.isValid(),solids=len(s.Solids),BOP=errors,volumes=[q.Volume for q in s.Solids])
    rows.append(row);print(json.dumps(row),flush=True)
(ROOT/'hardware/electronics/full-cat/w5-source-roof-native-r1/topology-diagnosis.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
