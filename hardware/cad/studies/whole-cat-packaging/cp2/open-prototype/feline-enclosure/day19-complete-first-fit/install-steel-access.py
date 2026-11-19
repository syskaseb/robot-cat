from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
s=Part.Shape();s.read(str(P/'steel-clear.tmp.brep'));assert s.isValid() and len(s.Solids)==1
r=json.loads((P/'gimbal-steel-verified.json').read_bytes());assert len(r)==2
for n,q in r.items():
 assert abs(q['steel_after'])<.00001 and abs(q['tool_after'])<.00001
 assert all(70<h['bounds'][2] and h['bounds'][5]<102 for h in q['old_material'])
assert 15 < sh('H19_FrontFrame').Volume-s.Volume < 45
D.H19_FrontFrame.Shape=s.Solids[0];D.recompute();wr('gimbal-steel-access.json',r)
s=(P/'views-and-runs.py').read_text();exec(s[s.index('skins='):s.index('D.recompute();D.save()')])
from PySide import QtCore
QtCore.QTimer.singleShot(250,lambda g=G:g.runCommand('Std_Save',0))
