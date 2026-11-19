from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
report={};pending={};tool=sh('B19_ToolEightAnchors')
for n in ['H19_FrontFrame','E19_RearBase']:
 s=Part.Shape();s.read(str(P/(n+'.anchor.tmp.brep')));assert len(s.Solids)==1 and s.isValid()
 s=s.Solids[0];opt={}
 for name in (['I19_FuseBand_HY','PBAY_F_HY'] if n=='H19_FrontFrame' else ['I19_FuseBand_PI','PBAY_F_PI']):
    o=sh(name);cm=s.common(o).Volume
    if cm>.001 and name.startswith('I19_FuseBand_'):
        s=s.cut(o.makeOffsetShape(.14,.01),.00001).removeSplitter()
    opt[name]=dict(before=cm,after=s.common(o).Volume)
 assert len(s.Solids)==1 and s.isValid() and all(abs(q['after'])<.001 for q in opt.values())
 c=s.common(tool).Volume;assert abs(c)<.001
 report[n]=dict(solids=1,volume=s.Volume,full_driver_common=c,seated=opt,bounds=bounds(s));pending[n]=s
for n,s in pending.items():D.getObject(n).Shape=s
D.Label='WAVEGO 19I';wr('anchor-access.json',report);D.recompute()
s=(P/'views-and-runs.py').read_text();exec(s[s.index('skins='):s.index('D.recompute();D.save()')])
from PySide import QtCore
QtCore.QTimer.singleShot(250,lambda g=G:g.runCommand('Std_Save',0))
