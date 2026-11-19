from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
driver=sh('B19_ToolEightAnchors');result={}
for n in ['H19_FrontFrame','E19_RearBase']:
 orig=sh(n).Solids[0];s=orig
 if n=='H19_FrontFrame':
    # Side bearing beside the positive HY arm. Keep the fuse housing underside at Z76.
    # The 4.2 mm inboard return spans both sides of the existing driver path.
    s=s.fuse(box(-66.35,12.7,73.45,4.2,17.8,2.55),.000001)
 cutters=[]
 for x in ([-70] if n=='H19_FrontFrame' else [112,122]):
    for y in ([-22.5,22.5] if n=='H19_FrontFrame' else [22.5]):
        cutters.append(cyl(x,y,70 if n=='H19_FrontFrame' else 48.52,2.82,18 if n=='H19_FrontFrame' else 38.04))
 for tool in cutters:s=s.cut(tool,.000001)
 s=s.removeSplitter();assert len(s.Solids)==1 and s.isValid(),n
 result[n]=dict(driver_before=orig.common(driver).Volume,driver_after=s.common(driver).Volume,solids=1,valid=True,volume=s.Volume,retained_extent=bounds(s))
 assert abs(result[n]['driver_after'])<.001
 D.getObject(n).Shape=s
wr('anchor-access.json',result);D.recompute()
s=(P/'views-and-runs.py').read_text();exec(s[s.index('skins='):s.index('D.recompute();D.save()')])
# Leave the user on the assembled view. Save from the GUI once after the timer returns.
from PySide import QtCore
QtCore.QTimer.singleShot(300,lambda: G.runCommand('Std_Save',0))
