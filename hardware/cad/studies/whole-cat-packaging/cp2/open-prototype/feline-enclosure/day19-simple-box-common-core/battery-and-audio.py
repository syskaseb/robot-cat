"""Side extraction of the cell with the two RR inline units on its detachable door."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import hashlib
P=Path(__file__).parent
exec((P/'core.py').read_text().split('# Each board/power cluster')[0])
receipt={}
def setpart(n,s):
    s=s.removeSplitter();o=D.getObject(n);o.Shape=s
    receipt[n]=dict(solids=[dict(volume=p.Volume,bounds=bounds(p)) for p in s.Solids],valid=s.isValid())
# The fore shroud's prior useful member predates the transverse pitch-receiver arms.
# Read only that preserved member and verify that every bit is present in current shroud.
ns=Part.Shape();ns.read(str(P/'pre-service-shroud.brp'))
cur=sh('E19_FrontShroud')
diff=cur.Volume-ns.Volume
# Verify restoration actually removes both added transverse arms, not a different generation.
assert 1300<diff<3500 and len(ns.Solids)==1,(diff,bounds(ns))
receipt['removed_transverse_receiver_arms_mm3']=diff
setpart('E19_FrontShroud',ns)
# One cantilever on the lid supports the pair along its length, away from the moving loop.
lid=sh('E19_ForeLid');beam=box(-89,-29,151.2,33,3.2,3.8)
for x in [-87,-65]:beam=beam.fuse(box(x,-31.8,153,3.6,16,2))
beam=beam.fuse(box(-59.5,-29,152,3.5,3.2,20))
lid=lid.fuse(beam)
# Actual supplier PCB mapped by both mounting centres. Bottom of laminate is
# 1.51 below the underside of the source nutwasher. USB and underside parts retained.
root=next(q for q in P.parents if (q/'reference/head-electronics-2026-09-22/ReSpeakerLitev1.1.step').is_file())
step=root/'reference/head-electronics-2026-09-22/ReSpeakerLitev1.1.step';mic=Part.read(str(step))
src=[V(42.73,-76.375,0),V(100.44,-105.295,0)]
bb=[sh('HB_MIC_'+str(i)+'_nutwasher').BoundBox for i in [0,1]]
dst=[V(b.Center.x,b.Center.y,b.ZMin-1.51) for b in bb]
svec=src[1]-src[0];v=dst[1]-dst[0]
ang=math.degrees(math.atan2(v.y,v.x)-math.atan2(svec.y,svec.x))
rot=A.Rotation(V(0,0,1),ang);tr=A.Placement(dst[0]-rot.multVec(src[0]),rot);mic.Placement=tr.multiply(mic.Placement)
add('E19_ReSpeakerSource',mic,(.20,.47,.35),'Seeed v1.1 supplier full assembly via 2 source holes on the actual steel axes')
hide('ReSpeakerLite_on_REMOVABLE_back')
receipt['mic']=dict(source_sha=hashlib.sha256(step.read_bytes()).hexdigest(),count=len(mic.Solids),bounds=bounds(mic),hole_residual=[(tr.multVec(a)-b).Length for a,b in zip(src,dst)],source_revision_physical=None)
for i,v in enumerate(dst):
    hb=sh('HB_MIC_'+str(i)+'_headwasher').BoundBox
    boss=cyl(v.x,v.y,hb.ZMax,3.2,v.z-hb.ZMax).cut(cyl(v.x,v.y,hb.ZMax-.1,1.2,v.z-hb.ZMax+.2))
    lid=lid.fuse(boss)
setpart('E19_ForeLid',lid)
battery=sh('Battery_GEA223S30X6GT').BoundBox
# Gap panel and parked RR inline units allow sideways extraction once straps are undone.
# The fixed upper bridge replaces low posts in the access window while retaining the slat/fuse row.
win=box(-12.8,19.35,51.35,108.1,86.5,22.8)
door=box(-14.1,101.45,49.95,110.8,1.55,25.6)
for key,x0,x1 in [('Fore',-16.4,19.85),('Rear',20.15,98.3)]:
    base=sh('E19_'+key+'Base')
    # The closed upper band connects each cut post to its own independently mounted wall.
    bridges=[box(x0,97.5,74.2,x1-x0,4.7,3.8)]
    for x in [-8,13,27,38.3,62.6,77,94]:
        if x0<x<x1-3:
            # Under the bank roof; board/fuse seats remain at the established z=77.
            bridges.append(box(x,57.3,74.25,3.2,43.6,2.7))
    s=join([base]+bridges).cut(win)
    s=s.cut(box(-14.4,101.15,49.65,111.4,3.5,26.2))
    # Half-lap rim along the long edges and two ends. Slot-and-tab removable
    # from outside; full battery can pass the inner frame with the cover off.
    for z in [48.3,74.3]:s=s.fuse(box(x0,100.2,z,x1-x0,2.8,2.2))
    setpart('E19_'+key+'Base',s)
# Two RR through connectors clip to a horizontal inward shelf on the removable
# door. Their old floor seats end below the 51.35 opening; relocate as whole units.
for i,n in enumerate(['NIGHT_INLINE_RR_W052','NIGHT_INLINE_RR_W053']):
    move(n,[],[53+i*0.2,78+i*10.3,60.8])
    b=sh(n).BoundBox
    for xx in [b.XMin+3,b.XMax-7]:
        door=door.fuse(box(xx,b.YMin-.8,58.1,4.4,102.2-b.YMin,2.7))
        door=door.fuse(box(xx,b.YMin-1.1,59,4.4,1,4.4))
# Three fixed lower hooks and two upper flexible buttons retain the cover independently of wiring.
for x in [-8,39,87]:
    door=door.fuse(box(x,99.1,49.98,4.8,3.3,1.3)).fuse(box(x,98.9,48.1,4.8,1.2,3.1))
for x in [-6,86]:
    door=door.fuse(box(x,99.3,73.4,5.6,3.2,1.6)).fuse(box(x,99.1,74.5,5.6,1.35,2.15))
    base=D.E19_ForeBase if x<0 else D.E19_RearBase
    base.Shape=base.Shape.cut(box(x-.2,98.8,74.15,6,1.9,2.9)).removeSplitter()
add('E19_BatteryDoor',door.removeSplitter(),(.28,.40,.40),'side pull cover with parked RR through connectors and upper snap/lower hooks')
receipt['door']=dict(solids=len(door.Solids),valid=door.isValid(),battery_sweep=bounds(win),moved= moves)
wr('battery-side-access.json',receipt);D.recompute();D.save()
