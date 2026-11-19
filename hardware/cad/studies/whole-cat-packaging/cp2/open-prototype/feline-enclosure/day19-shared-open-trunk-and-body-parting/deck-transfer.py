from pathlib import Path
import json
P=Path(__file__).parent
s=(P/'body-and-channel.py').read_text();exec(s[:s.index('# Start at F')])
wr('wide-deck-rejection.json',json.loads((P/'new-members.json').read_bytes()))
# The roof is two intact load-sharing U decks. Access is through ONE open mouth where they meet.
# The long trunk lies ABOVE or BELOW the original intact webs and only dives at their common split.
ap=box(-2,-54,170.72,36,24,3.38)
for n in ['E19_ForeLid','E19_RearLid']:
 t=original(G0/'whole-cat19G.FCStd',n);t=t.cut(ap)
 if n=='E19_ForeLid':
    for i,side in [(0,1),(1,-1)]:
        z=sh('HB_MIC_'+str(i)+'_headwasher').BoundBox
        x,y=z.Center.x,z.Center.y
        t=t.cut(box(x-3.65,y-8.7,152.49,7.3,12.35,18.95))
        # Load enters the underside of the board through the washer-aligned shoulder.
        # Both outboard returns are outside the supplier board, leaving its components free.
        land=cyl(x,y,152.5,2.68,6.585).cut(cyl(x,y,152.45,1.16,6.7))
        cy=y+side*8.8;cx=x+(6 if i==0 else 0)
        bar=box(x-1.65,min(y,cy)-1.2,153.1,3.3,abs(cy-y)+2.4,2.25).cut(cyl(x,y,152.9,1.16,3))
        beam=box(min(x,cx)-1.65,cy-1.65,153.1,abs(cx-x)+3.3,3.3,2.25)
        post=box(cx-1.65,cy-1.65,153.1,3.3,3.3,18.95)
        t=t.multiFuse([land,bar,beam,post])
 upd(n,t)
wr('new-members.json',{n:dict(valid=sh(n).isValid(),members=[dict(volume=v.Volume,bounds=bounds(v)) for v in sh(n).Solids]) for n in ['H19_FrontFrame','E19_ForeLid','E19_RearLid']})
wr('deck-transfer.json',dict(split=[-2,-54,170.72,34,-30,174.1],accessible_clear_area_mm2=36*24,reason='preserve the two JR saddles and media/speaker underside hangers by transferring all drops at the end of each deck',mic_fasteners=[a for a in group('HB_MIC_')],installed_board_standoff_height=6.585))
D.recompute();D.save()
