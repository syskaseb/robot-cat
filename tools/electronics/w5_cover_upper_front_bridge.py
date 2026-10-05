"""Join the detached west Cover wall at its upper FRONT end, not rear rim.

Receive CoverFourBays and the two existing hood bridges. The two rear bridges
cross stationary Deck uprights and are removed from the construction. One
upper saddle links the west wall to the existing hood bridge, entirely above
the current Deck. Check actual material and actual root contact before native
recompute. No Deck cut, moved wire, extra printed part or new fastener.
"""
from pathlib import Path
from datetime import datetime,timezone
import json,sys
import w5_remote_end_layout as R
from servo_fuse_inputs_r1 import sha,save
ROOT=R.ROOT;BASE=R.BASE;OUT=BASE/'w5-cover-upper-front-bridge-r1'
sys.path.insert(0,str(ROOT/'tools/cad'))
from check_main_p0_placement import SavedShapes

ADDED={
    'WestFrontSaddle':[-91,-47,173,-84,-37,177],
    'WestFrontUpright':[-90,-47,173,-86,-37,189.5],
    'WestFrontTopBridge':[-90,-47,185,-72,-37,189.5]}

def main():
    import FreeCAD as A,Part
    start=datetime.now(timezone.utc);assert not (OUT/'checks.json').exists()
    OUT.mkdir(parents=True,exist_ok=True);reader=SavedShapes();pins={}
    master=ROOT/'hardware/cad/studies/w5-side-retention-native-r1/WholeHarnessSideRetention.FCStd'
    base=reader.shape(master,'CoverFourBays');assert base.isValid() and len(base.Solids)==3
    pieces=sorted(base.Solids,key=lambda s:s.Volume,reverse=True)
    assert pieces[1].BoundBox.XMax<-82 and pieces[1].BoundBox.ZMax<179
    bp_path=BASE/'w5-side-retention-received-r2/native-blueprint.json'
    bp=json.loads(bp_path.read_text(encoding='utf-8'));pins[bp_path.relative_to(ROOT).as_posix()]=sha(bp_path)
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    oldhood={k:reader.shape(master,k) for k in ('HoodPostOutboardFoot','HoodPostOverSideBay')}
    added={k:box(b) for k,b in ADDED.items()}
    saddle_contact=added['WestFrontSaddle'].common(pieces[1]).Volume
    hood_contact=added['WestFrontTopBridge'].common(oldhood['HoodPostOverSideBay']).Volume
    current,received,_,_=R.current(A,Part);pins.update(received);current.pop('SourceCover')
    def load(p):pins[p.relative_to(ROOT).as_posix()]=sha(p);return Part.read(str(p))
    deck=load(ROOT/'hardware/cad/studies/w5-remote-end-native-r1/CompleteDeck_CANDIDATE_WORLD.brep')
    current['CompleteDeck']=deck
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
                            path=OUT/('HIT_'+str(len(hits)+1)+'.brep');c.exportBrep(str(path))
                            hits.append(dict(part=name,owner=owner,mm3=c.Volume,witness=path.relative_to(ROOT).as_posix()))
                    except Exception as e:errors.append(dict(part=name,owner=owner,error=str(e)))
    connected=saddle_contact>1 and hood_contact>1
    clear=not hits and not errors and connected
    minimum=min(b[2] for b in ADDED.values());assert minimum>deck.BoundBox.ZMax
    finish=datetime.now(timezone.utc)
    save(OUT/'checks.json',dict(status='UPPER_FRONT_CONNECTION_STATIC_CLEAR_NATIVE_PENDING' if clear else 'UPPER_FRONT_CONNECTION_REJECTED',
        received_native_master=master.relative_to(ROOT).as_posix(),received_base_object='CoverFourBays',
        keep_original_bridges=list(oldhood),remove_original_bridges=['SouthRimWest','SouthRimSteppedEnd'],
        added_boxes_mm=ADDED,saddle_west_wall_contact_mm3=saddle_contact,bridge_hood_contact_mm3=hood_contact,
        continuous_new_bridge_Deck_lift_clearance_bound_mm=minimum-deck.BoundBox.ZMax,
        no_Deck_cut=True,no_wire_paths_changed=True,new_print_jobs=0,new_screws=0,
        pairs=pairs,hits=hits,errors=errors,native_complete=False,shared_service_complete=False,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        source_sha256={**reader.hashes,**pins,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        files={p.relative_to(ROOT).as_posix():sha(p) for p in OUT.glob('HIT_*.brep')},
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds()))
    print('UPPER_FRONT_CONNECTION',saddle_contact,hood_contact,pairs,len(hits),len(errors),flush=True)

if __name__=='__main__':main()
