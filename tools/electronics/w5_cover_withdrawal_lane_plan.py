"""Allocate the whole rear-rim service lane before another native change.

Rail lies2.5mm outside the actual complete Deck bounding extent, so every
vertical rail pose is disjoint. Three fixed X lanes join the received rim;
their actual material is checked against current installed and swept Deck
height. No complete Cover Boolean is built until these interfaces pass.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import w5_cover_withdrawal_bridge as B
from servo_fuse_inputs_r1 import sha,save
ROOT=B.ROOT;BASE=B.BASE;OUT=BASE/'w5-cover-withdrawal-lane-plan-r1'

def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'plan.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);current,pins,_,_=B.R.current(A,Part)
    def load(p):pins[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    prior=BASE/'w5-cover-withdrawal-bridge-r1/checks.json'
    r=json.loads(prior.read_text(encoding='utf-8'));pins[prior.relative_to(ROOT).as_posix()]=sha(prior)
    assert r['hits'] and not r['errors'] and all(x['owner']=='CompleteDeck' for x in r['hits'])
    deck=load(ROOT/'hardware/cad/studies/w5-remote-end-native-r1/CompleteDeck_CANDIDATE_WORLD.brep')
    current['CompleteDeck']=deck;current.pop('SourceCover')
    current['Fixed/Source/Bridge']=load(ROOT/'hardware/cad/studies/w5-remote-end-native-r1/SourceBridge_CANDIDATE_WORLD.brep')
    inner=deck.BoundBox.YMin-2.5;outer=inner-2.5
    boxes={k:list(b) for k,b in B.ADDED.items()}
    boxes['RearOutboardRail'][1]=outer;boxes['RearOutboardRail'][4]=inner
    for k in boxes:
        if k!='RearOutboardRail':boxes[k][1]=outer
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    added={k:box(b) for k,b in boxes.items()};hits=[];errors=[];pairs=0
    def check(phase,name,s,targets):
        nonlocal pairs
        for owner,t in targets.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            for a in s.Solids:
                for b in t.Solids:
                    if not a.BoundBox.intersect(b.BoundBox):continue
                    pairs+=1
                    try:
                        c=a.common(b)
                        if c.Volume>1e-5:
                            p=OUT/('HIT_'+str(len(hits)+1)+'.brep');c.exportBrep(str(p))
                            hits.append(dict(phase=phase,part=name,owner=owner,mm3=c.Volume,witness=p.relative_to(ROOT).as_posix()))
                    except Exception as e:errors.append(dict(phase=phase,part=name,owner=owner,error=str(e)))
    for name,s in added.items():check('static_full_current',name,s,current)
    for name,b in boxes.items():
        if name=='RearOutboardRail':continue
        # Continuous vertical prism of one web. Actual Common proves its
        # sweep, not an occupied bbox declared to be a collision.
        sweep=box([*b[:3],b[3],b[4],b[5]+100]);check('continuous_web_Deck_0_to100',name,sweep,{'CompleteDeck':deck})
    finish=datetime.now(timezone.utc)
    save(OUT/'plan.json',dict(status='ONE_OUTBOARD_SERVICE_LANE_ALLOCATED_CLEAR' if not hits and not errors else 'OUTBOARD_SERVICE_LANE_REQUIRES_DIFFERENT_WEB_OWNERSHIP',
        cuts=B.CUTS,added=boxes,actual_Deck_Ymin_mm=deck.BoundBox.YMin,rail_Ymax_mm=inner,
        continuous_rail_Deck_clearance_bound_mm=2.5,continuous_web_Deck_sweeps_mm=[0,100],
        all_current_static_owner_count=len(current),pairs=pairs,hits=hits,errors=errors,
        new_screws=0,new_print_jobs=0,native_pending=True,selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
            'tools/electronics/w5_cover_withdrawal_bridge.py':sha(ROOT/'tools/electronics/w5_cover_withdrawal_bridge.py')},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in OUT.glob('HIT_*.brep')},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('COVER_SERVICE_LANE',outer,inner,pairs,len(hits),len(errors),flush=True)

if __name__=='__main__':main()
