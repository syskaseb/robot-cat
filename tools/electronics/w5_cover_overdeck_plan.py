"""Allocate one high rear arch, not another horizontal rim microshift.

The failed outboard lane proves three web X lanes clear the complete Deck
continuously. Put the joining rail above the full current Deck height and
inside the existing Cover height, then check actual added material against
all current installed owners. Subtraction and native rebuild follow only if
this complete layout is clear. Original Deck, bank and routes are unchanged.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import w5_cover_withdrawal_bridge as B
from servo_fuse_inputs_r1 import sha,save
ROOT=B.ROOT;BASE=B.BASE;OUT=BASE/'w5-cover-overdeck-plan-r1'

def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'plan.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);current,pins,_,_=B.R.current(A,Part)
    def load(p):pins[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    lane=BASE/'w5-cover-withdrawal-lane-plan-r1/plan.json'
    prior=json.loads(lane.read_text(encoding='utf-8'));pins[lane.relative_to(ROOT).as_posix()]=sha(lane)
    assert not prior['errors'] and all(h['phase']=='static_full_current' for h in prior['hits'])
    assert prior['continuous_web_Deck_sweeps_mm']==[0,100]
    deck=load(ROOT/'hardware/cad/studies/w5-remote-end-native-r1/CompleteDeck_CANDIDATE_WORLD.brep')
    cover=current.pop('SourceCover');current['CompleteDeck']=deck
    current['Fixed/Source/Bridge']=load(ROOT/'hardware/cad/studies/w5-remote-end-native-r1/SourceBridge_CANDIDATE_WORLD.brep')
    bottom=deck.BoundBox.ZMax+2.5;top=bottom+4
    assert top<cover.BoundBox.ZMax
    boxes={
        'RearHighRail':[-91,-98, bottom,-42,-93,top],
        'RearWestPost':[-90,-98,130,-87,-93,top],
        'RearMiddlePost':[-56,-98,130,-53,-93,top],
        'RearEastPost':[-45,-96.5,130,-42,-93,top]}
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    added={k:box(b) for k,b in boxes.items()};hits=[];errors=[];pairs=0
    for name,s in added.items():
        for owner,t in current.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            for a in s.Solids:
                for b in t.Solids:
                    if not a.BoundBox.intersect(b.BoundBox):continue
                    pairs+=1
                    try:
                        c=a.common(b)
                        if c.Volume>1e-5:
                            p=OUT/('HIT_'+str(len(hits)+1)+'.brep');c.exportBrep(str(p))
                            hits.append(dict(part=name,owner=owner,mm3=c.Volume,witness=p.relative_to(ROOT).as_posix()))
                    except Exception as e:errors.append(dict(part=name,owner=owner,error=str(e)))
    finish=datetime.now(timezone.utc)
    save(OUT/'plan.json',dict(status='ONE_HIGH_ARCH_ALLOCATED_STATIC_CLEAR' if not hits and not errors else 'HIGH_ARCH_LAYOUT_REJECTED',
        cuts=B.CUTS,added=boxes,actual_Deck_Zmax_mm=deck.BoundBox.ZMax,rail_Zmin_mm=bottom,
        continuous_rail_Deck_clearance_bound_mm=2.5,posts_Deck_continuous_clear_received_from=lane.relative_to(ROOT).as_posix(),
        within_original_Cover_height=True,wire_paths_changed=False,new_screws=0,new_print_jobs=0,
        current_owner_count=len(current),pairs=pairs,hits=hits,errors=errors,native_pending=True,
        shared_service_pending=True,selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in OUT.glob('HIT_*.brep')},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('OVERDECK_ARCH',pairs,len(hits),len(errors),flush=True)

if __name__=='__main__':main()
