"""Box, split carrier base and removable covers, around the placed full modules."""
from pathlib import Path
P=Path(__file__).parent
exec((P/'core.py').read_text().split('# Each board/power cluster')[0])
# Four matching perimeter curves connect the inherited chin to the flat enclosure.
csrc=(P.parent/'day19-closed-head-neck-and-module-interfaces/head-and-shoulder.py').read_text()
exec(csrc[csrc.index('def ring('):csrc.index('def skin(')])
def rectwire(x,d):
    w=103-d;b=40+d;t=173-d;m=(b+t)/2
    return Part.Wire(Part.makePolygon([V(x,y,z) for y,z in [(0,t),(w,t),(w,m),(w,b),(0,b),(-w,b),(-w,m),(-w,t),(0,t)]]).Edges)
def adapter(d):
    return Part.makeLoft([ring((-77,104,18,211),d,.64),rectwire(-64,d)],True,True)
adapt=adapter(0).cut(adapter(1.6))
for y in [-125,38]:adapt=adapt.cut(box(-108,y,-12,68,87,54))
# A continuous upper opening at the split lets each half lift over its equipment.
walls=box(-64,-103,40,273,206,133).cut(box(-64.05,-101.4,41.6,271.45,202.8,129.8))
# The S0 neck starts at Y99, passes through 3mm of fascia. S1's two washers
# occupy Y-98.5 to -98 and -101 to -100.5 after its full-body relocation.
walls=walls.cut(cyl(178.5,97,104.5,11.5,10,(0,1,0)))
walls=walls.cut(box(155,-104,82,34,7,36))
s1panel=box(155,-100.5,82,34,2,36).cut(cyl(172,-101,101,6.25,4,(0,1,0)))
for x in [155,185]:s1panel=s1panel.fuse(box(x,-103,82,4,4.5,36))
walls=walls.fuse(s1panel)
# Tail opening spans the actual shaft at the roof and rear wall throughout pitch.
walls=walls.cut(box(150,-2,169,62,25,10)).cut(box(206,-2,145,6,25,33))
# Vertical vents on both sides and perforations above speaker & microphone.
for x in [-48,-40,-32,-24,-16,-8,0,8]:
    for y in [-104,100.8]:walls=walls.cut(box(x,y,134,3,4.2,18))
holes=[cyl(x,y,170.8,2.3,4) for x in range(20,106,9) for y in range(-19,21,9)]
for x in [4,72]:
    for y in [-9,5]:holes.append(cyl(x,y,170.8,2.2,4))
walls=walls.cut(Part.makeCompound(holes))
# A second rear-side access brings the monitor connector and viewing/actuation side to the lid.
# Full monitor stays on its own removable bridge, accessible at lift-off.
# Floor and box are a single print per half. Local access windows preserve all anchor screws.
def footprint(x0,x1,axes):
    b=box(x0,-98,39.95,x1-x0,196,1.6)
    for x in axes:
        for y in [-22.5,22.5]: b=b.cut(cyl(x,y,38,3.25,6))
    return b
f=D.D19D_FrontFloor.Shape;r=D.B19_RearFloor.Shape
# Join dependent walls to the eight-anchor load structure only below the lid edge.
lower=walls.common(box(-80,-108,35,310,216,108))
# Create lower bays before bank & lid attachment. No fusion of steel or left/right halves.
fore=join([f,footprint(-106,19.85,[-80,-70]),lower.common(box(-76,-110,35,95.85,220,111))])
rear=join([r,footprint(20.15,208,[112,122]),lower.common(box(20.15,-110,35,190,220,111))])
# At the opposed seam there is 0.30 mm between parts. Original individual
# anchor footprints remain authoritative; do not fill source screw throats.
for key,s,axes in [('Fore',fore,[-80,-70]),('Rear',rear,[112,122])]:
    for x in axes:
        for y in [-22.5,22.5]:
            s=s.cut(cyl(x,y,39.9,2.9,1.75).cut((f if key=='Fore' else r)))
    add('E19_'+key+'Base',s.removeSplitter(),(.24,.37,.39),'independent anchored floor with integral side and end walls')
hide('D19D_FrontFloor','B19_RearFloor')
# Keyed cap with four sprung side fingers; small through-windows in lower walls
# accept wedges and give a flat pick access. No extra purchased fasteners.
def latch(x,sg):
    pts=[(100.9,148),(100.9,137.5),(102.55,138.7),(102.55,139.8),(101.75,139.9),(101.75,148)]
    w=Part.makePolygon([V(x,sg*y,z) for y,z in pts+[pts[0]]])
    return Part.Face(w).extrude(V(8,0,0))
for key,xa,xb,xx in [('Fore',-64,19.85,[-53,8]),('Rear',20.15,209,[31,193])]:
    lid=walls.common(box(xa,-110,143.22,xb-xa,220,36))
    base=D.getObject('E19_'+key+'Base');baseS=base.Shape
    for x in xx:
        for sg in [-1,1]:
            lid=lid.fuse(latch(x,sg)).fuse(box(x,100.8 if sg==1 else -102.2,145,8,1.4,3))
            baseS=baseS.cut(box(x-.25,100.6 if sg==1 else -104,137.15,8.5,3.4,3.05))
    base.Shape=baseS.removeSplitter()
    add('E19_'+key+'Lid',lid.removeSplitter(),(.23,.265,.28),'lift-off four tab lid, vents and port openings')
# Chin transitions at a defined plane. Print as its own part with internal ears
# resting on the base. Fusing to the fore lid would prevent separate installation.
nose=sh('D19D_Shoulder').common(box(-180,-120,0,103.04,240,240))
adapterpart=nose.fuse(adapt).removeSplitter()
add('E19_FrontShroud',adapterpart,(.23,.265,.28),'front-to-box shroud; fixed chin and open rear mounting face')
# S0 positive panel face needs a seating boss where the key neck crosses from 99 to 102.
rear=D.E19_RearBase
sx=178.5;sz=104.5
seat=cyl(sx,99,sz,18,2.7,(0,1,0)).cut(cyl(sx,98.8,sz,11.4,3.2,(0,1,0)))
rear.Shape=rear.Shape.fuse(seat).removeSplitter()
D.recompute();D.save()
wr('case-sections.json',{n:dict(solids=len(sh(n).Solids),valid=sh(n).isValid(),bounds=bounds(sh(n)),volume=sh(n).Volume) for n in group('E19_') if n not in ['E19_BUS_population']})
