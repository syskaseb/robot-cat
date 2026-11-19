from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
orig=sh('H19_FrontFrame').Solids[0];s=orig;res={}
for prefix in ['YAW_SOURCE_EAR_19','YAW_SOURCE_EAR__8_5']:
 screw=sh(prefix+'_full_screw');bb=screw.BoundBox;washer=sh(prefix+'_headwasher');w=washer.BoundBox
 assert bb.ZLength>2*max(bb.XLength,bb.YLength) and w.ZMax>bb.Center.z
 x,y=w.Center.x,w.Center.y;tool=cyl(x,y,w.ZMax+.001,max(bb.XLength,bb.YLength)/2+.26,52)
 before=s.common(screw).Volume;t=s.cut(tool,.000001).removeSplitter()
 assert t.isValid() and len(t.Solids)==1 and abs(t.Volume-s.Volume)<95
 res[prefix]=dict(steel_before=before,steel_after=t.common(screw).Volume,washer_after=t.common(washer).Volume,tool_before=s.common(tool).Volume,tool_after=t.common(tool).Volume,centre=[x,y],start_z=w.ZMax+.001,driver_length=52,removed_mm3=s.Volume-t.Volume)
 assert abs(res[prefix]['steel_after'])<.00001 and abs(res[prefix]['tool_after'])<.00001;s=t.Solids[0]
wr('gimbal-steel-access.json',res);D.H19_FrontFrame.Shape=s;D.recompute()
s=(P/'views-and-runs.py').read_text();exec(s[s.index('skins='):s.index('D.recompute();D.save()')])
from PySide import QtCore
QtCore.QTimer.singleShot(250,lambda g=G:g.runCommand('Std_Save',0))
