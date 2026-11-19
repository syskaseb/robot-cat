from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
src=(P/'gallery.py').read_text();exec(src[:src.index('bp=transform')])
# Filling the old touch opening intruded into the existing raised yaw latch hood.
# Restore the same internal recess through the fill; its outside roof remains 2.05 mm thick.
s=sh('F19_ForeCap');b=sh('D19D_YawMatedPair').BoundBox
s=s.cut(box(b.XMin+1.8,b.YMin-2,198.5,26.4,18,2.65)).removeSplitter();D.F19_ForeCap.Shape=s
rec=json.loads((P/'new-members.json').read_bytes());rec['F19_ForeCap']=dict(valid=s.isValid(),members=[dict(mm3=v.Volume,bounds=bounds(v)) for v in s.Solids]);wr('new-members.json',rec)
D.recompute();D.save()
