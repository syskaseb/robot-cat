from pathlib import Path
P=Path(__file__).parent
src=(P/"seat-and-close.py").read_text()
exec(src[:src.index("# Fit both actual")])
src=(P/"seat-and-close.py").read_text()
back=sh("D19D_PitchBack")
part=src[src.index("face=sh("):src.index('face=face.cut(back);')]
# Already installed both hollow pupils before the single-member check failed.
begin=part.index('    p=sh("D19D_Pupil_');end=part.index('    # Retain a curved',begin)
part=part[:begin]+'    p=sh("D19D_Pupil_"+suf)\n'+part[end:]
exec(part)
pieces=sorted(face.cut(back).removeSplitter().Solids,key=lambda s:s.Volume,reverse=True)
def boxdata(s):
    b=s.BoundBox;return dict(volume=s.Volume,bounds=[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax])
write("face-fragments.json",[boxdata(s) for s in pieces])
assert pieces[0].Volume>35000 and sum(s.Volume for s in pieces[1:])<850, [s.Volume for s in pieces]
update("D19D_Face",pieces[0]);exec(src[src.index("D.recompute();D.save()"):])

