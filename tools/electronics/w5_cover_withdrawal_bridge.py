"""One outboard replacement rim around both observed Deck obstructions.

Do not cut the Deck/bank or relocate accepted wires. Two local windows in
the added rear rim plus a2.5x4mm outboard rail preserve a continuous Cover.
Check added material only against the current installed census; subtraction
cannot add a collision. Native construction follows only a clear receipt.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import w5_remote_end_layout as R
from servo_fuse_inputs_r1 import sha,save
ROOT=R.ROOT;BASE=R.BASE;OUT=BASE/'w5-cover-withdrawal-bridge-r1'
CUTS={'RearWestWindow':[-84.1,-98.2,129.8,-78.9,-92.8,134.2],
      'RearEastWindow':[-51.1,-98.2,129.8,-45.4,-92.8,134.2]}
ADDED={'RearOutboardRail':[-91,-101,130,-42,-98.5,134],
       'RearWestWeb':[-90,-101,130,-87,-93,134],
       'RearMiddleWeb':[-56,-101,130,-53,-93,134],
       'RearEastWeb':[-45,-101,130,-42,-93,134]}

def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);pins={}
    def load(p):pins[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    prior=BASE/'w5-shared-retention-service-r2/checks.json'
    p=json.loads(prior.read_text(encoding='utf-8'));pins[prior.relative_to(ROOT).as_posix()]=sha(prior)
    assert len(p['hits'])==2 and not p['errors']
    assert all(x['fixed']=='CandidateDeck' and x['lift_mm']==10 for x in p['hits'])
    parent=ROOT/'hardware/cad/studies/w5-side-retention-native-r1/SourceCover_CANDIDATE_WORLD.brep'
    old=load(parent)
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    additions={k:box(b) for k,b in ADDED.items()}
    candidate=old.cut(Part.makeCompound([box(b) for b in CUTS.values()])).multiFuse(list(additions.values()))
    assert candidate.isValid() and len(candidate.Solids)==1
    assert not (candidate.check(True) or [])
    candidate.exportBrep(str(OUT/'Cover_CANDIDATE_WORLD.brep'))
    current,received,_,_=R.current(A,Part);pins.update(received)
    assert 'SourceCover' in current and 'CompleteDeck' in current
    current.pop('SourceCover')
    current['CompleteDeck']=load(ROOT/'hardware/cad/studies/w5-remote-end-native-r1/CompleteDeck_CANDIDATE_WORLD.brep')
    current['Fixed/Source/Bridge']=load(ROOT/'hardware/cad/studies/w5-remote-end-native-r1/SourceBridge_CANDIDATE_WORLD.brep')
    hits=[];errors=[];pairs=0
    def check(phase,name,s,obstacles):
        nonlocal pairs
        for owner,t in obstacles.items():
            if not s.BoundBox.intersect(t.BoundBox):continue
            for a in s.Solids:
                for b in t.Solids:
                    if not a.BoundBox.intersect(b.BoundBox):continue
                    pairs+=1
                    try:
                        c=a.common(b)
                        if c.Volume>1e-5:
                            witness=OUT/('HIT_'+str(len(hits)+1)+'.brep');c.exportBrep(str(witness))
                            hits.append(dict(phase=phase,part=name,owner=owner,mm3=c.Volume,witness=witness.relative_to(ROOT).as_posix()))
                    except Exception as e:errors.append(dict(phase=phase,part=name,owner=owner,error=str(e)))
    for name,s in additions.items():check('installed_new_material',name,s,current)
    # Entire revised rim, including retained original bridges: check it against
    # current Deck through the same poses, not just at the old10mm witness.
    rim=Part.makeCompound([box(b) for b in ADDED.values()]).fuse(
        Part.makeBox(47,5,4,A.Vector(-90,-98,130)).cut(Part.makeCompound([box(b) for b in CUTS.values()])))
    for dz in (0,2,5,10,30,60,100):
        q=rim.copy();q.translate(A.Vector(0,0,dz));check('rim_Deck_lift_'+str(dz),'CompleteRearRim',q,{'CompleteDeck':current['CompleteDeck']})
    finish=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='ONE_OUTBOARD_REAR_RIM_CLEAR_NATIVE_AND_SHARED_SERVICE_PENDING' if not hits and not errors else 'ONE_OUTBOARD_REAR_RIM_CONFLICT',
        cuts=CUTS,added=ADDED,minimum_new_rail_section_mm=[2.5,4],
        candidate_valid=True,candidate_solids=1,BOP_errors=0,wire_paths_changed=False,new_screws=0,new_print_jobs=0,
        pairs=pairs,hits=hits,errors=errors,native_complete=False,shared_service_complete=False,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),
            'tools/electronics/w5_remote_end_layout.py':sha(ROOT/'tools/electronics/w5_remote_end_layout.py')},
        files={q.relative_to(ROOT).as_posix():sha(q) for q in OUT.glob('*.brep')},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('OUTBOARD_COVER_RIM',pairs,len(hits),len(errors),flush=True)

if __name__=='__main__':main()
