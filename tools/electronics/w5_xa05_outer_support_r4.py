"""Whole outer power-ground corridor, real supports and mounting hardware.

All inner flights conflicted with existing centre equipment. One east U-turn
leaves the G2 mouth, an R15 S-rise clears rear bodies, and the west approach
descends into the same G_AUX mouth. A small separate outrigger avoids making
the whole Deck exceed256mm. P0/blocks/old bank stay fixed. Never select a wire
alone or silently waive contacts with the existing Cover or native Deck.
"""
from datetime import datetime,timezone
from pathlib import Path
import sys,json,math
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/electronics'),str(ROOT/'tools/cad')]
from servo_fuse_inputs_r1 import save,sha
from w5_xa05_joint_repair_r1 import Path15
from w5_s1_source_layout_r1 import X,Y,Z,mul
OUT=ROOT/'hardware/electronics/full-cat/w5-xa05-outer-support-r4'


def layout():
    c=Path15([123,9.5,113.5],Y);c.line([123,12,113.5]);c.arc(X,math.pi)
    c.shift([0,0,7.5]);c.line([153,-12,121]);c.arc(mul(X,-1))
    c.line([90.5,-27,121]);c.arc(mul(Y,-1));c.arc(X)
    c.shift([0,0,-7.5]);c.line([110.5,-57,113.5])
    assert math.dist(c.p,[110.5,-57,113.5])<1e-7
    length=sum(e['length_mm'] for e in c.edges)
    return dict(wire='XA05',a='P0G2.5',b='G_AUX.1',edges=c.edges,wire_SKU='HELU23501',
        OD_mm=2.5,min_fixed_R_mm=15,path_mm=length,nominal_trial_blank_mm=math.ceil((length+82)/10)*10,
        actual_cut_mm=None,new_electrical_SKUs=0,changed_bought_blocks=0,selected=False,physical_pass=False)


def main():
    import FreeCAD as A
    import Part
    from w5_r53_owners import installed
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);intent=layout();save(OUT/'intent.json',intent)
    owners,pins,omitted=installed(A,Part)
    owners.pop('hardware/electronics/full-cat/xa05-main-aux-return-r2/XA05_DESIGN.brep')
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    def cyl(p,r,h,axis=(0,0,1)):return Part.makeCylinder(r,h,A.Vector(*p),A.Vector(*axis))
    # One seat attached to current Deck, axisX. Two shoulders stay1.7mm
    # beside the through tunnel; no floating block above a full-width cut.
    raw=box([116.7,-30.3,108.8,123.3,-23.7,121.7])
    groove=cyl([116.6,-27,121],1.5,6.8,(1,0,0))
    slots=[box([118.4,y-.8,108.8,121.6,y+.8,123.6]) for y in (-31.1,-22.9)]
    tunnel=box([118.4,-32.1,109.4,121.6,-21.9,110.8]);slots.append(tunnel)
    seat=raw.cut(groove).cut(Part.makeCompound(slots))
    # Outrigger foot has two M3x12 through holes, same selected DIN hardware.
    # Foot/bridge are a separate small printable part, not an oversized Deck.
    foot=box([126.5,-17,109,135.5,-1,112])
    stem=box([132.5,-13.4,111.8,135.5,-6.4,119])
    bridge=box([133,-13.4,116,156.3,-6.4,119.8])
    outer_seat=box([149.7,-13.2,119.5,156.3,-6.6,121.7])
    bracket=foot.fuse(stem).fuse(bridge).fuse(outer_seat)
    outside_tools=[cyl([131,y,108.9],1.7,3.2) for y in (-5,-13)]
    outside_tools += [cyl([153,-13.3,121],1.5,6.8,(0,1,0)),
        box([147.9,-11.5,116.3,158.1,-8.3,117.7])]
    outside_tools += [box([x-.8,-11.5,115.9,x+.8,-8.3,123.6]) for x in (148.9,157.1)]
    bracket=bracket.cut(Part.makeCompound(outside_tools))
    assert bracket.isValid() and len(bracket.Solids)==1
    deck=owners.pop('CandidateDeck').fuse(seat).cut(Part.makeCompound(slots))
    deck_tools=[cyl([131,y,104.9],1.7,4.2) for y in (-5,-13)]
    deck=deck.cut(Part.makeCompound(deck_tools));assert deck.isValid() and len(deck.Solids)==1
    owners['NewDeckXA05']=deck
    def band_xz(cx,y,top,bottom):
        left,right=cx-4.1,cx+4.1
        return Part.makeCompound([box([x-.6,y-1.25,bottom,x+.6,y+1.25,top+1.2]) for x in (left,right)]+
            [box([left-.6,y-1.25,top,right+.6,y+1.25,top+1.2]),
             box([left-.6,y-1.25,bottom,right+.6,y+1.25,bottom+1.2]),
             box([right+.1,y-2.5,bottom-.1,right+5.1,y+2.5,bottom+3.9])])
    inner=band_xz(0,0,122.25,109.5)
    inner.rotate(A.Vector(),A.Vector(0,0,1),90);inner.translate(A.Vector(120,-27,0))
    outer=band_xz(153,-9.9,122.25,116.4)
    changed={'DeckSeat':seat,'OuterBracket':bracket,'InnerTie':inner,'OuterTie':outer}
    for i,y in enumerate((-5,-13)):
        changed['M3bolt'+str(i)]=cyl([131,y,100.5],1.5,12).fuse(cyl([131,y,112.5],2.75,3))
        changed['M3washers'+str(i)]=cyl([131,y,112],3.5,.5).cut(cyl([131,y,111.9],1.6,.7)).fuse(
            cyl([131,y,104.5],3.5,.5).cut(cyl([131,y,104.4],1.6,.7)))
        corners=[A.Vector(131+3.1754*math.cos(math.pi*k/3),y+3.1754*math.sin(math.pi*k/3),102.1) for k in range(6)]
        changed['M3nut'+str(i)]=Part.Face(Part.makePolygon(corners+[corners[0]])).extrude(A.Vector(0,0,2.4)).cut(cyl([131,y,102],1.5,2.6))
    pieces=[];edges=[];hits=[];errors=[];pairs=0
    def check(name,s,key,t):
        nonlocal pairs
        if not s.BoundBox.intersect(t.BoundBox):return
        pairs+=1
        try:
            common=s.common(t)
            if common.Volume>1e-5:
                b=common.BoundBox
                hits.append(dict(part=name,owner=key,mm3=common.Volume,
                    bounds_mm=[getattr(b,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]))
        except Exception as ex:errors.append(dict(part=name,owner=key,error=str(ex)))
    for e in intent['edges']:
        edge=Part.makeLine(A.Vector(*e['start']),A.Vector(*e['end'])) if e['kind']=='line' else Part.Arc(A.Vector(*e['start']),A.Vector(*e['mid']),A.Vector(*e['end'])).toShape()
        profile=Part.Wire([Part.makeCircle(1.25,edge.valueAt(edge.FirstParameter),edge.tangentAt(edge.FirstParameter))])
        s=Part.Wire([edge]).makePipeShell([profile],True,False);assert s.isValid()
        pieces.append(s);edges.append(edge)
    wire=Part.makeCompound(pieces)
    for key,t in {**owners,**changed}.items():check('XA05',wire,key,t)
    for name,s in changed.items():
        for key,t in owners.items():
            if name=='DeckSeat' and key=='NewDeckXA05':continue
            check(name,s,key,t)
        if name.endswith('Tie'):
            for key in ('DeckSeat','OuterBracket'):check(name,s,key,changed[key])
    # Own bolt/thread/nut and seating faces intentionally meet, not foreign
    # clash waivers. Exact tools/lever access/end-strap actions remain open.
    files=[]
    groups=[('XA05_WORLD.brep',wire),('CENTERLINE_WORLD.brep',Part.Wire(edges)),('DECK_CANDIDATE_WORLD.brep',deck),
        ('OUTRIGGER_WORLD.brep',bracket),('ADDITIONS_WORLD.brep',Part.makeCompound(list(changed.values())))]
    for name,s in groups:
        p=OUT/name;s.exportBrep(str(p));files.append(p)
    finish=datetime.now(timezone.utc)
    pins += [Path(__file__),ROOT/'tools/electronics/w5_xa05_joint_repair_r1.py',ROOT/'tools/electronics/w5_s1_source_layout_r2.py',
        ROOT/'tools/electronics/w5_s1_source_layout_r1.py',ROOT/'hardware/electronics/full-cat/w5-xa05-joint-repair-r3/checks.json']
    save(OUT/'checks.json',dict(status='XA05_OUTER_JOINT_REJECTED' if hits or errors else 'XA05_OUTER_JOINT_CLEAR_NATIVE_AND_ACCESS_OPEN',
        hits=hits,errors=errors,pairs=pairs,source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in pins},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in [OUT/'intent.json',*files]},
        new_ties=2,tie_SKU='111-02370 T18I-PA66-BK',new_M3x12=2,new_M3_nuts=2,new_M3_washers=4,
        new_prints=1,one_replacement_Deck=True,hardware_stack_mm=dict(Deck=4,foot=3,top_washer=.5,under_washer=.5,nut=2.4,nominal_thread_protrusion=1.6),
        omitted_retired_carrier_aliases=omitted,native_ready=False,selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        open=['Qualify both endpoint restraints and WAGO lever/driver sequence.',
              'Native Deck/Outrigger/any necessary Cover port, closed STL and retained mounting access.',
              'One package and stock reconciliation;5m HELU23501 remains planning allowance, not a cut list.'],
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('XA05_OUTER_JOINT',pairs,len(hits),len(errors),flush=True)


if __name__=='__main__':main()
