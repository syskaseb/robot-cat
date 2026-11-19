from pathlib import Path
P=Path(__file__).parent
s=(P/'views-and-runs.py').read_text()
exec(s[:s.index("q=read(P/'lower-approaches.json')")])
q=read(P/'lower-approaches.json')
s=(P/'views-and-runs.py').read_text()
s=s[s.index("ss=displaytube(read(H/'battery-leads.json')"):s.index("f=read(P/'shared-fuse-transfer.json')")].replace("read(H/'battery-leads.json')['input']","read(P/'W075-seated.json')")
exec(s)
D.recompute();s=(P/'views-and-runs.py').read_text();exec(s[s.index('skins='):s.index('D.recompute();D.save()')])
from PySide import QtCore
QtCore.QTimer.singleShot(250,lambda g=G:g.runCommand('Std_Save',0))
