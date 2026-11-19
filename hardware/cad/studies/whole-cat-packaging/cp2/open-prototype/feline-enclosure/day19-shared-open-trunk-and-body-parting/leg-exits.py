from pathlib import Path
import json
P=Path(__file__).parent;s=(P/'body-and-channel.py').read_text();exec(s[:s.index('# Start at F')])
# One rounded window per complete leg branch. Only remove existing side wall;
# each factory end can be threaded independently before the bank and covers go on.
report=[]
for n,x in [('H19_FrontFrame',-51),('E19_RearBase',112)]:
 s0=sh(n)
 for sy in [-1,1]:
    y=-105 if sy==-1 else 98;z=67.8
    slot=box(x-6.5,y,z-5.25,13,7,10.5)
    for xx in [x-6.5,x+6.5]:slot=slot.fuse(cyl(xx,y,z,5.25,7,(0,1,0)))
    # A flared entry on BOTH sides reduces the knife edge presented to the jackets.
    for yy,rr,rr2 in [(sy*101.3-0.65,6.05,5.25),(sy*102.45-.12,5.25,6.05)]:
        for xx in [x-6.5,x+6.5]:slot=slot.fuse(Part.makeCone(rr,rr2,1,V(xx,yy,z),V(0,1,0)))
    old=s0.Volume;s0=s0.cut(slot)
    report.append(dict(host=n,side=sy,centre=[x,sy*102,z],clear_size=[23.5,10.5],original_removed_mm3=old-s0.Volume,area_mm2=13*10.5+3.14159*5.25**2,full_plug_go_no_go='compare largest delivered intact 5264 with end-on window, one at a time; prelay before closing banks and covers'))
 upd(n,s0)
wr('leg-mouths.json',report)
changed=['H19_FrontFrame','E19_ForeLid','E19_RearLid','E19_RearBase']
wr('new-members.json',{n:dict(valid=sh(n).isValid(),members=[dict(volume=v.Volume,bounds=bounds(v)) for v in sh(n).Solids]) for n in changed})
D.recompute();D.save()
