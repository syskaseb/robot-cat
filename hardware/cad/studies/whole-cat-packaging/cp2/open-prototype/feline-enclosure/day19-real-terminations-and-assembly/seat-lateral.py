from pathlib import Path
import json,math
P=Path(__file__).parent
s=(P/'fit-assembly.py').read_text();exec(s[:s.index("m=json.loads")])
m=json.loads((P/'mic-port.json').read_bytes());c=V(*m['pivot_xy'],0)
def about(deg):
 r=A.Rotation(V(0,0,1),deg);return A.Placement(c-r.multVec(c),r)
lid=sh('E19_ForeLid');supports=[]
for n in group('HB_MIC_'):
 if n.endswith('headwasher'):
    b=sh(n).BoundBox;w=box(b.Center.x-3.6,b.Center.y-3.6,b.ZMax-.16,12.4,7.2,171.46-b.ZMax)
    supports.append(lid.common(w));lid=lid.cut(w)
for k in ['E19_ReSpeakerSource','ReSpeakerLite_on_REMOVABLE_back','D19_MIC_FULL_HEIGHT_RESERVE']:
 o=D.getObject(k);o.Placement=about(90).multiply(o.Placement)
for k in group('HB_MIC_'):
 o=D.getObject(k);o.Placement=about(-90).multiply(o.Placement)
for a in supports:
 a.Placement=about(-90).multiply(a.Placement);lid=lid.fuse(a)
for n in group('HB_MIC_'):
 if n.endswith('headwasher'):
    b=sh(n).BoundBox;lid=lid.fuse(box(b.Center.x-2,b.Center.y-8.5,169.6,4.1,4.8,2.5))
setpart('E19_ForeLid',lid)
for n in ['E19_ForeLid','F19_ForeCap']:
 s0=sh(n);z=170.9 if n=='E19_ForeLid' else 198.7
 for x in [-48,-27]:
    for y in [18,35,59,83]:
        a=about(-90).multVec(V(x,y,z));s0=s0.cut(cyl(a.x,a.y,z,1.8,3.4))
 setpart(n,s0)
q=V(*m['mouth']);D.G19_MIC_C_PlugAllow.Shape=box(q.x,q.y-5.2,q.z-3.5,19,10.4,7)
# The six body groups are replaced from the final complete end-to-end allocations.
exec(s[s.index("t=json.loads"):s.index("pp=[]\nfor b")])
# The 19F AUDIO boot was a textual project field. Materialize it separately and save the completed document.
import runpy
runpy.run_path(str(P/'save-seated.py'))
