"""Verify six constraints and reconcile final R5 ground cage/assembly recipe."""
from datetime import datetime,timezone
import json
from pathlib import Path
import body_ground_routes_r1 as M
ROOT=M.ROOT
OUT=ROOT/"hardware/electronics/full-cat/body-ground-bridge-finish-r5"
CAD=ROOT/"hardware/cad/studies/body-ground-bridge-finish-r5"
ROUTE=ROOT/"hardware/electronics/full-cat/body-ground-bridge-r5"

def main():
    import FreeCAD as A
    import Part
    start=datetime.now(timezone.utc)
    c=json.loads((OUT/"checks.json").read_text(encoding="utf-8"))
    assert c["status"]=="SUPPORTED_GROUND_BRIDGE_COMPLETE" and not c["hits"]
    i=json.loads((OUT/"interface.json").read_text(encoding="utf-8"))
    d=A.openDocument(str(CAD/"DeckGroundBridgeSupported.FCStd"))
    try:
        names=["GroundTieSlots","MiddleTieSlots","GroundSeatFoot0","GroundSeatFoot1","GroundSeatFoot2","MiddleBeamFoot"]
        assert all(d.getObject(n).FullyConstrained and d.getObject(n).solve()==0 for n in names)
        assert len(d.GroundSupportedDeck.Shape.Solids)==1
    finally:A.closeDocument(d.Name)
    def load(p):
        s=Part.Shape();s.read(str(p));return s
    changed={p.stem:load(p) for p in CAD.glob("Seat*_WORLD.brep")}
    changed.update({p.stem:load(p) for p in ROUTE.glob("W061_*_DESIGN.brep")})
    cases={"F_AUX_case":[51,11.6,122,72.2,23.6,142],"F_PWM_case":[67.5,-17.91,127.49,75.9,-14.89,130.51]}
    rows=[]
    for name,s in changed.items():
        for owner,b in cases.items():
            t=Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
            if s.BoundBox.intersect(t.BoundBox):rows.append(dict(part=name,owner=owner,hit_mm3=s.common(t).Volume))
    assert not [r for r in rows if r["hit_mm3"]>1e-5],rows
    i["assembly"][0]="Before populated electronics, thread two endpoint T18I through four Deck passages and the middle T18I through two elevated beam passages; heads underneath their supporting surfaces."
    i["restraints"]["passages"]="Four through Deck105..109, two through middle beam132..138.2; existing open window retained."
    i["restraints"]["middle_post_root_xy_mm"]=[78,58,82,62]
    i["restraints"]["middle_beam_xy_mm"]=[78,60,90,82.5]
    # Retain the already-selected XA05 mouth at X123,+Y, not the unused
    # five-route draft's 6.75mm pitch. W061 itself still uses central X111.
    i["prototype_415_pitch_mm"]=6
    i["cage_x_mm"]={"G1":[51,58.5,66,73.5,81],"G2":[99,105,111,117,123]}
    i["entry_face"]={"G1":"+Y11; all five mouths share this face","G2":"+Y9.5; retained XA05 atX123"}
    i["cage_datum_note"]="Prototype registration, not measured WAGO pitch. Selected XA05 G2.5 coordinate retained; only same-potential cage labels changed. Do not reuse rejected drafts' opposite entry faces."
    assert c["source_script_sha256"]==M.sha(Path(__file__).with_name("body_ground_bridge_finish_r1.py"))
    c["rerunnable_builder_sha256"]=c["source_script_sha256"]
    c["supplemental_changed_owner_checks"]=rows
    c["supplement_script_sha256"]=M.sha(Path(__file__))
    c["fully_constrained_added_sketches"]=len(names)
    c["supplement_start_utc"]=start.isoformat();c["supplement_end_utc"]=datetime.now(timezone.utc).isoformat()
    M.save(OUT/"checks.json",c);M.save(OUT/"interface.json",i)
    print(json.dumps(dict(supplemental_pairs=len(rows),hits=0,constrained_sketches=len(names))),flush=True)
if __name__=="__main__":main()
