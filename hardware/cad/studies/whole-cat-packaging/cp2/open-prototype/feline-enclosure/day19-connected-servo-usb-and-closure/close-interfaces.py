"""Finish real attachment, open laying entrances and the two roof interfaces."""
from pathlib import Path
P=Path(__file__).parent;E=P.parent/'day19-simple-box-common-core'
src=(P/'gallery.py').read_text();exec(src[:src.index('bp=transform')])
l=json.loads((P/'service-lay.json').read_bytes())
def repl(n,s):D.getObject(n).Shape=s.removeSplitter()
base=sh('E19_ForeBase')
# Actual fixed yaw lead exits the servo+original floor. An open lateral departure
# is restricted to this short non-anchor length, with the original bridge above and floor below.
port=box(-108.3,-12.8,53.8,13.1,12,16.2)
old=base.Volume;repl('E19_ForeBase',base.cut(port))
receipt=dict(fixed_departure=dict(removed_mm3=old-sh('E19_ForeBase').Volume,bounds=bounds(port),anchor_X=[-80,-70,112,122]))
s=sh('E19_FrontShroud')
s=s.cut(box(-65,-114.2,166,3.3,13.1,33))
extension=[box(-66,-114,163.7,50.5,1.55,35.9),box(-66,-113.8,198,50.5,12,1.6),box(-17.2,-113.7,163.8,1.7,12,35.1),box(-65.7,-113.7,163.5,50,12,1.6)]
repl('E19_FrontShroud',join([s]+extension))
n='F19_ForeCap';s=max(sh(n).Solids,key=lambda v:v.Volume)
s=s.cut(box(-65,-104,172.8,49,4.1,17.2))
# The former floating forward latch belongs to the opened loop entrance. Replace it
# at the intact side-wall station beyond the opening and cut its matching seat below.
x=-12;y=-100.8
s=join([s,box(x,-102,173.05,6,3.5,2.2),box(x,y,169.3,6,1.9,5.8),box(x,y-.5,169.35,6,1.9,1.25)])
# Finger well allows direct access to the original thin touch membrane from above.
well=box(-15,-36,173.65,17.4,14.4,26.2)
s=s.fuse(well).cut(box(-13.6,-34.6,173.45,14.6,11.6,29))
for xx in [-48,-27]:
    for yy in [18,35,59,83]:s=s.cut(cyl(xx,yy,198.8,1.9,3))
for xx in [-52,-34,-16,2]:s=s.cut(box(xx,100.9,179,12,3,4.5))
repl(n,s)
n='E19_ForeLid';s=sh(n).cut(box(x-.3,y-.3,170.7,6.6,2.8,3.4))
# Keep the yaw seat above the rolling JR transfer; support it from its opposite side.
b=sh('D19D_YawMatedPair').BoundBox
for xx in [b.XMin+3,b.XMax-7]:
    s=s.cut(box(xx-.08,b.YMin-1.68,173.005,4.16,2.58,b.ZMin-174.58))
    s=s.fuse(box(xx,b.YMax-.75,172.35,4,2.3,b.ZMin-173.7))
repl(n,s)
n='E19_RearLid';s=sh(n)
# D flat on one outer edge of BUS seat gives the actual full project boot a straight approach.
s=s.cut(box(139.7,54.2,174.7,26.6,26.6,7.2));repl(n,s)
n='F19_RearCap';s=sh(n).cut(box(194.75,98.5,175.02,6.25,2.65,.47))
# Buzzer/monitor and opposite rear vents, kept separate from accessible DATA.
for xx in [158,164,170,176,182,188]:s=s.cut(box(xx,-71,198.8,2.2,16,3))
repl(n,s)
# Tool-free hooks on two separated pairs of compliant fingers. Each bears on the connector
# housing, with a free mating/unmating axis, never on conductor insulation.
for n,target in [('E19_ForeLid','D19D_YawMatedPair'),('E19_RearLid','B19_TailMatedPair'),('E19_UpperYawCover','BR_FLANK_HP_PAIR')]:
    b=sh(target).BoundBox;s=sh(n);pieces=[s]
    for xx in [b.XMin+3,b.XMax-7]:
        for sg in [-1,1]:
            yy=b.YMin-1.6 if sg<0 else b.YMax+.2
            pieces.append(box(xx,yy,b.ZMin+.5,4,1.4,b.ZLength+.5))
            pieces.append(box(xx,yy if sg<0 else b.YMax-.55,b.ZMax+.17,4,2.15,.85))
    repl(n,join(pieces))
# Fore yaw stack now comes just above 199.5. A local closed raised roof over its
# latch heads maintains 0.9 mm min headroom without lowering the pair into the JR transfer.
n='F19_ForeCap';s=sh(n);b=sh('D19D_YawMatedPair').BoundBox
s=s.fuse(box(b.XMin+.5,b.YMin-3,199.65,29,20,3.55)).cut(box(b.XMin+1.8,b.YMin-2,198.5,26.4,18,2.65));repl(n,s)
changed=list(json.loads((P/'new-members.json').read_bytes()))
changed.append('E19_ForeBase')
wr('new-members.json',{n:dict(valid=sh(n).isValid(),members=[dict(mm3=v.Volume,bounds=bounds(v)) for v in sh(n).Solids]) for n in changed})
wr('closure-details.json',receipt)
D.recompute();D.save()
exec(src[src.index('view=(E/'):])
