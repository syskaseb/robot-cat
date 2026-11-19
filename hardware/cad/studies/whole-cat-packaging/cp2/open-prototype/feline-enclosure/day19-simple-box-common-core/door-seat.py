"""Finish the common stepped seat after the full rigid door/installed switch test."""
from pathlib import Path
P=Path(__file__).parent
exec((P/'core.py').read_text().split('# Each board/power cluster')[0])
d=sh('E19_BatteryDoor');checks={}
for key,x0,x1 in [('Fore',-14.4,19.85),('Rear',20.15,97.0)]:
    o=D.getObject('E19_'+key+'Base');s=o.Shape
    # The steady inner shoulder carries the panel behind the 1.55 skin.
    # The former front extension of both rim rails occupied the door face.
    for z in [48.3,74.3]:
        s=s.fuse(box(x0,99.2,z,x1-x0,2.2,2.05))
    s=s.cut(box(x0-.05,101.16,49.69,x1-x0+.1,3.5,26.14))
    # Cut only the five tab plinths relative to the actual printed door. Local
    # 0.18 side clearance allows seating while the outer lip remains for capture.
    for x in [-8,39,87,-6,86]:
        top=x in [-6,86];w=5.6 if top else 4.8;z=73.2 if top else 47.9;h=3.7 if top else 3.65
        if not x0-2<x<x1:continue
        s=s.cut(box(x-.18,98.72,z,w+.36,3.2,h))
    # Allow the door shelf rungs to enter across the frame edge at the end of insertion.
    s=s.cut(d)
    if key=='Rear':s=s.cut(sh('S0_body'))
    s=s.removeSplitter();o.Shape=s
    checks[key]=dict(solids=len(s.Solids),valid=s.isValid(),common_door=s.common(d).Volume,common_S0=s.common(sh('S0_body')).Volume if key=='Rear' else None)
wr('door-seat.json',checks);D.recompute();D.save()
