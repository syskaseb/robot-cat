"""Finish the door web, AUX bearing and the real 484-solid microphone mounting plane."""
from pathlib import Path
P=Path(__file__).parent
exec((P/'core.py').read_text().split('# Each board/power cluster')[0])
b=sh('E19_RearBase')
# This rear AUX foot must support the converter ABOVE the cell withdrawal path.
bridge=box(89.4,36.75,78.3,12.5,3,3)
foot=box(99.3,36.8,41.0,3.4,3.1,39.7)
D.E19_RearBase.Shape=join([b,bridge,foot])
door=sh('E19_BatteryDoor');items=[door]
for k in ['NIGHT_INLINE_RR_W052','NIGHT_INLINE_RR_W053']:
    b=sh(k).BoundBox
    for x in [b.XMin+3,b.XMax-7]:
        items.append(box(x,99.8,58.2,4.4,2.6,2.5))
        # Overhang captures the two outside walls of the through connector.
        for y in [b.YMin-.95,b.YMax+.14]:
            items.append(box(x,y,59.5,4.4,.85,b.ZMax-59.0))
        for y in [b.YMin-.95,b.YMax-.5]:
            items.append(box(x,y,b.ZMax+.1,4.4,1.5,.75))
D.E19_BatteryDoor.Shape=join(items)
# With both hole axes aligned the supplier STEP projects beyond the cached
# 86 x 35 field. Translate the WHOLE mic, steel, and its two bearing stations.
delta=V(0,-23,0);lid=sh('E19_ForeLid');supports=[]
for n in group('HB_MIC_'):
    if not n.endswith('headwasher'):continue
    b=sh(n).BoundBox;x=b.Center.x;y=b.Center.y;z=b.ZMax
    w=box(x-3.55,y-3.55,z-.15,12.2,7.1,171.45-z)
    supports.append(lid.common(w));lid=lid.cut(w)
for n in ['E19_ReSpeakerSource','ReSpeakerLite_on_REMOVABLE_back','D19_MIC_FULL_HEIGHT_RESERVE']+group('HB_MIC_'):D.getObject(n).Placement.Base+=delta
for s in supports:s.translate(delta)
lid=join([lid]+supports)
for n in group('HB_MIC_'):
    if not n.endswith('headwasher'):continue
    b=sh(n).BoundBox
    lid=lid.fuse(box(b.Center.x+3.9,b.Center.y-2,169.65,4.6,4.1,2.4))
# Break out to the microphone board through a pair of small aperture arrays.
for x in [-48,-27]:
    for y in [18,35,59,83]:lid=lid.cut(cyl(x,y,170.9,1.8,3.1))
D.E19_ForeLid.Shape=lid.removeSplitter()
wr('finished-panels.json',dict(mic_delta=list(delta),supplier_bounds=bounds(sh('E19_ReSpeakerSource')),parts={n:dict(valid=sh(n).isValid(),members=[dict(volume=s.Volume,bounds=bounds(s)) for s in sh(n).Solids]) for n in ['E19_ForeLid','E19_RearBase','E19_BatteryDoor']}))
D.recompute();D.save()
