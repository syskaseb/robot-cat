"""One complete ownership change: side channel stays on Deck, not bank.

Use the existing two M3x8/nuts horizontally at the front closed end.
Remove obsolete bank/tab bearing, retain the exact channel/output cage and
all wires. Preflight changed fixture, bank subtraction and actual owners
before doing any expensive native Deck union. No service PASS inferred.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys,math,os
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
from servo_fuse_bank_current_owner_receive import receive
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-guard-fixed-deck-r1'
STOCKS=[('GuardFixedFoot',[-113.5,82,109,-94,88,113]),
        ('GuardFixedFrontPost',[-113.5,85,111,-101,88,159])]
OLD_TAB=[-97.1,-97.1,146.5,-84.9,-90.9,149.6]
AXES=[(-110.25,155),(-104.25,155)]
def main():
    import FreeCAD as A
    import Part
    t=datetime.now(timezone.utc);OUT.mkdir(parents=True,exist_ok=True);assert not (OUT/'checks.json').exists()
    print('GUARD_FIXED_DECK_PREFLIGHT',os.getpid(),flush=True)
    owners,module,pins=receive(False)
    def load(rel):pins[rel]=sha(ROOT/rel);return Part.read(str(ROOT/rel))
    V=A.Vector
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],V(*b[:3]))
    deck=load('hardware/cad/studies/servo-fuse-fr-source-fixed-deck-native-r2/Deck_WORLD.brep')
    bank=load('hardware/cad/studies/servo-fuse-fr-source-fixed-deck-native-r2/BankRight_WORLD.brep')
    cover=load('hardware/cad/studies/servo-fuse-cover-main-service-r6/Cover_WORLD.brep')
    guard=load('hardware/cad/studies/servo-fuse-fr-output-station-native-r5/Guard_WORLD.brep')
    for key in list(owners):
        if key=='CandidateDeck' or key.startswith('FRHardware/'):del owners[key]
    owners['CurrentBankLeft']=module['BankLeft'];owners['CurrentCover']=cover
    tabtool=box(OLD_TAB);guardbase=guard.cut(tabtool);bankbase=bank.cut(tabtool)
    fixture=box(STOCKS[0][1]).fuse(box(STOCKS[1][1]));holes=[];hardware={};bearings=[]
    for i,(x,z) in enumerate(AXES):
        holes.append(Part.makeCylinder(1.7,10,V(x,82,z),V(0,1,0)))
        hardware['Screw'+str(i)]=Part.makeCylinder(1.5,8,V(x,83,z),V(0,1,0)).fuse(Part.makeCylinder(2.75,3,V(x,80,z),V(0,1,0)))
        rad=5.5/math.sqrt(3);vs=[V(x+rad*math.cos(math.pi/6+k*math.pi/3),88,z+rad*math.sin(math.pi/6+k*math.pi/3)) for k in range(6)]
        hardware['Nut'+str(i)]=Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(V(0,2.4,0)).cut(Part.makeCylinder(1.5,2.6,V(x,87.9,z),V(0,1,0)))
        ring=Part.makeCylinder(2.75,.1,V(x,82.9,z),V(0,1,0)).cut(Part.makeCylinder(1.7,.2,V(x,82.85,z),V(0,1,0)))
        backring=ring.copy();backring.translate(V(0,5.1,0))
        bearings.append(dict(axis_xz=[x,z],guard_head_ring_mm3=guardbase.common(ring).Volume,post_nut_ring_mm3=fixture.common(backring).Volume,ring_mm3=ring.Volume))
    drill=Part.makeCompound(holes);newguard=guardbase.cut(drill);fixture=fixture.cut(drill)
    changed=dict(hardware,FixedFixture=fixture,Guard=newguard)
    # Fixture embeds into Deck only at the integral foot, not a free-floating
    # support. Check its actual footprint below the parent top surface.
    embed=box([-98,82,109,-94,88,110]);common=deck.common(embed)
    # Actual unchanged hardware/wires are checked, not just a bbox sketch.
    owners['CurrentBankRight']=bankbase
    pairs=0;hits=[];errors=[]
    for n,s in changed.items():
        for k,q in owners.items():
            if not s.BoundBox.intersect(q.BoundBox):continue
            pairs+=1
            try:
                h=s.common(q)
                if h.Volume>1e-5:
                    hits.append(dict(part=n,owner=k,mm3=h.Volume,bounds_mm=[h.BoundBox.XMin,h.BoundBox.YMin,h.BoundBox.ZMin,h.BoundBox.XMax,h.BoundBox.YMax,h.BoundBox.ZMax]))
            except Exception as e:errors.append(dict(part=n,owner=k,error=str(e)))
    for n,s in changed.items():
        for k,q in changed.items():
            if k<=n or not s.BoundBox.intersect(q.BoundBox):continue
            h=s.common(q);pairs+=1
            if h.Volume>1e-5:hits.append(dict(part=n,owner=k,mm3=h.Volume))
    states={k:dict(valid=s.isValid(),solids=len(s.Solids),BOP=[str(v) for v in (s.check(True) or [])]) for k,s in dict(changed,BankRight=bankbase).items()}
    valid=not hits and not errors and common.Volume>1e-5 and all(v['valid'] and v['solids']==1 and not v['BOP'] for v in states.values())
    for k,s in dict(changed,BankRight=bankbase).items():s.exportBrep(str(OUT/(k+'_CANDIDATE.brep')))
    end=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='GUARD_FIXED_DECK_PREFLIGHT_CLEAR' if valid else 'GUARD_FIXED_DECK_PREFLIGHT_REJECTED',selected=False,physical_pass=False,pairs=pairs,hits=hits,errors=errors,states=states,
        native_stocks=[dict(name=n,box_mm=b) for n,b in STOCKS],old_tab_tool_mm=OLD_TAB,axes_xz_mm=AXES,bearings=bearings,embed_mm3=common.Volume,
        stock_delta=dict(new_prints=0,new_fasteners=0,new_ties=0,unchanged_M3x8=2,unchanged_M3nuts=2),
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=t.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-t).total_seconds()))
    print('GUARD_FIXED_DECK_RESULT',json.dumps(dict(valid=valid,pairs=pairs,hits=hits,embed_mm3=common.Volume,bearings=bearings)),flush=True)
if __name__=='__main__':main()
