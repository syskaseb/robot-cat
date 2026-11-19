from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
exec((E/'core.py').read_text().split('# Each board/power cluster')[0].replace('19E.FCStd','19I.FCStd'))
s=sh('H19_FrontFrame').Solids[0]
# The lower field leaves a 0.575 mm separation to the top rail. Recess only the
# underside of the two replacement cantilevers across the short end of this case.
for x in [-69.32,-56.78]:
 s=s.cut(box(x-.05,-19.05,70.65,3.5,18.32,3.75),.00001)
s=s.removeSplitter();assert len(s.Solids)==1 and s.isValid()
D.getObject('H19_FrontFrame').Shape=s
D.recompute();D.save()
