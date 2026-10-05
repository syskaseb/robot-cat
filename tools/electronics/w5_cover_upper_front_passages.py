"""Complete the allocated upper-front connection with two source passages.

R1 three contacts are only W008/W009. W009 spans the initial post width:
a3mm inner ligament is designed BEFORE cutting both openings. No source
lead/terminal, fixed Deck support or fastener moves. Check the whole changed
connection against current owners once; local root joins must remain real.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import w5_cover_upper_front_bridge as B
from servo_fuse_inputs_r1 import sha,save
ROOT=B.ROOT;BASE=B.BASE;OUT=BASE/'w5-cover-upper-front-passages-r1'

ADDED={k:[*v[:4],-34,v[5]] for k,v in B.ADDED.items()}
# Conservative bounds of actual R1 intersection witnesses plus0.4mm, not
# cable diameter inferred from a photograph or bbox declared as collision.
OPENINGS={
    'W008FrontPassage':[-93.023,-46.353,178.539,-84.421,-43.147,189.901],
    'W009FrontPassage':[-92.957,-47.479,177.897,-84.421,-37.039,181.101]}

def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);pins={};reader=B.SavedShapes()
    prior=BASE/'w5-cover-upper-front-bridge-r1/checks.json'
    proof=json.loads(prior.read_text(encoding='utf-8'));pins[prior.relative_to(ROOT).as_posix()]=sha(prior)
    assert len(proof['hits'])==3 and not proof['errors']
    assert {r['owner'] for r in proof['hits']}=={'W008','W009'}
    for rel,h in {**proof['source_sha256'],**proof['files']}.items():assert sha(ROOT/rel)==h,rel
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    cutters=Part.makeCompound([box(b) for b in OPENINGS.values()])
    added={k:box(b).cut(cutters) for k,b in ADDED.items()}
    # These are features of ONE final Cover, not separate printed parts.
    # A window may split an intermediate post; the top bridge must reconnect
    # it. Validate that real final patch, not an invented per-feature rule.
    assert all(s.isValid() for s in added.values())
    # Continuous inner web is3.039mm at the widest received passage.
    ligament=ADDED['WestFrontUpright'][4]-OPENINGS['W009FrontPassage'][4]
    assert ligament>=3
    master=ROOT/proof['received_native_master'];base=reader.shape(master,'CoverFourBays')
    pieces=sorted(base.Solids,key=lambda s:s.Volume,reverse=True)
    hood={k:reader.shape(master,k) for k in proof['keep_original_bridges']}
    patch=list(added.values())[0].multiFuse([*list(added.values())[1:],*hood.values()])
    assert patch.isValid() and len(patch.Solids)==1 and not (patch.check(True) or [])
    west=patch.common(pieces[1]).Volume;main=patch.common(pieces[0]).Volume;third=patch.common(pieces[2]).Volume
    assert min(west,main,third)>1,(west,main,third)
    current,received,_,_=B.R.current(A,Part);pins.update(received);current.pop('SourceCover')
    def load(p):pins[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    current['CompleteDeck']=load(ROOT/'hardware/cad/studies/w5-remote-end-native-r1/CompleteDeck_CANDIDATE_WORLD.brep')
    current['Fixed/Source/Bridge']=load(ROOT/'hardware/cad/studies/w5-remote-end-native-r1/SourceBridge_CANDIDATE_WORLD.brep')
    hits=[];errors=[];pairs=0
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
    save(OUT/'checks.json',dict(status='UPPER_FRONT_PASSAGES_STATIC_ROOTS_CLEAR_NATIVE_PENDING' if not hits and not errors else 'UPPER_FRONT_PASSAGES_REJECTED',
        received_native_master=proof['received_native_master'],received_base_object='CoverFourBays',
        keep_original_bridges=proof['keep_original_bridges'],remove_original_bridges=proof['remove_original_bridges'],
        added_boxes_mm=ADDED,opening_boxes_mm=OPENINGS,opening_nominal_clearance_mm=.4,
        minimum_inner_ligament_mm=ligament,patch_solids=1,patch_BOP_errors=0,
        intermediate_feature_solids={k:len(s.Solids) for k,s in added.items()},
        actual_patch_contacts_mm3=dict(west_wall=west,main=main,hood_post=third),
        continuous_new_bridge_Deck_lift_clearance_bound_mm=proof['continuous_new_bridge_Deck_lift_clearance_bound_mm'],
        no_Deck_cut=True,no_wire_paths_changed=True,new_print_jobs=0,new_screws=0,
        assembly=['Thread bare W008/W009 source tails through the two upper windows before fitting their terminal rings.',
            'Follow the received source-ring and bank release order. Remove these tails before bank/Cover withdrawal; do not pull wide TE rings through the windows.'],
        pairs=pairs,hits=hits,errors=errors,native_complete=False,shared_service_complete=False,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={**reader.hashes,**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__)),Path(B.__file__).relative_to(ROOT).as_posix():sha(Path(B.__file__))},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in OUT.glob('HIT_*.brep')},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('UPPER_FRONT_PASSAGES',ligament,west,main,third,pairs,len(hits),len(errors),flush=True)

if __name__=='__main__':main()
