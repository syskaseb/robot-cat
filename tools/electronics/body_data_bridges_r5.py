"""Resolve sourced-thickness tie conflict by the next equivalent DATA cage.

Move D_RL logical1 into physical second cage, logical2 into first (all DATA).
Move its one saddle/slot pair with the actual path; unchanged P0 station body.
"""
import copy,json,sys,shutil,tempfile
from pathlib import Path
import body_data_bridges_r4 as R4
M=R4.M
OUT=M.ROOT/"hardware/electronics/full-cat/body-data-bridges-r5"
CAD=M.ROOT/"hardware/cad/studies/body-data-bridges-r5"
PRIOR=R4.PRIOR
M.ROUTES=copy.deepcopy(M.ROUTES)
for p in M.ROUTES["W012"][-3:]:p[0]=104.25
M.ANCHORS=[(n,e,104.25 if n=="W012" and e==1 else x,y) for n,e,x,y in M.ANCHORS]

def main():
    import FreeCAD as A
    import Part
    OUT.mkdir(exist_ok=True);CAD.mkdir(exist_ok=True)
    assert not (OUT/"checks.json").exists()
    c=json.loads((R4.OUT/"checks.json").read_text(encoding="utf-8"))
    failure=json.loads((R4.OUT/"current-body-checks.json").read_text(encoding="utf-8"))
    assert len(failure["hits"])==1 and failure["hits"][0]["part"]=="W012_end1_tie"
    plan=json.loads((R4.OUT/"interface.json").read_text(encoding="utf-8"))
    plan.update(routes=M.ROUTES,anchors=M.ANCHORS,
        route_geometry_source=dict(W007=PRIOR.relative_to(M.ROOT).as_posix(),W011=PRIOR.relative_to(M.ROOT).as_posix(),W012=OUT.relative_to(M.ROOT).as_posix()),
        selected_recipe="R5 supported DATA interface; R1-R4 diagnostic only. Same three logical nets, one right-north equivalent cage permutation.")
    plan["connector_datums"]["port_order"]="Global +X left-to-right design labels on both rows; not manufacturer cage numbering and not viewer-relative. Mark the logical labels physically at assembly."
    plan["datum_overrides"]["D_RL_physical_cages_left_to_right"]=["D_RL.2","D_RL.1","D_RL.3","D_RL.4","D_RL.5"]
    plan["datum_overrides"]["R4_rejected_tie_hit_mm3"]=failure["hits"][0]["hit_mm3"]
    plan["restraints"].pop("verified_utc",None)
    plan["restraints"]["manufacturer_verification_date_utc"]="2026-10-01"
    M.save(OUT/"interface.json",plan)
    path=M.PATH_BUILDER("W012",M.ROUTES["W012"])
    for i,e in enumerate(path.Edges):
        profile=Part.Wire([Part.makeCircle(M.OD/2,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])
        shape=Part.Wire([e]).makePipeShell([profile],True,False);assert shape.isValid() and len(shape.Solids)==1
        shape.exportBrep(str(OUT/f"W012_{i}_DESIGN.brep"));e.exportBrep(str(OUT/f"W012_{i}_CENTERLINE.brep"))
    d=A.openDocument(str(R4.CAD/"DeckDataBridgesSupported.FCStd"));dest=CAD/"DeckDataBridgesSupported.FCStd"
    try:
        d.saveAs(str(dest));slots=d.SixDataRestraintPairs
        assert slots.GeometryCount==48
        changed=0
        for i,k in enumerate(slots.Constraints):
            if k.Type=="DistanceX" and k.First in (40,44):
                slots.setDatum(i,A.Units.Quantity(k.Value+6.75));changed+=1
        assert changed==2 and slots.FullyConstrained and slots.solve()==0
        seat=d.SaddleFoot5
        for i,k in enumerate(seat.Constraints):
            if k.Type=="DistanceX":seat.setDatum(i,A.Units.Quantity(k.Value+6.75))
        assert seat.FullyConstrained and seat.solve()==0
        d.SaddleGroove5.Placement.Base.x+=6.75
        d.save();d.recompute();shape=d.SupportedDeck.Shape.copy()
        assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
        pinned=d.PinnedR36Deck.Shape
        removed=pinned.cut(d.FinishedDeck.Shape).Volume
        assert abs(removed-307.2)<1e-4,removed
        shape.exportBrep(str(CAD/"Deck_WORLD.brep"));before=shape.Volume;d.save()
    finally:A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix="robot-cat-data-cage-") as td:
        target=Path(td)/dest.name;shutil.copy2(dest,target);d=A.openDocument(str(target));d.recompute()
        try:
            s=d.SupportedDeck.Shape;assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-before)<1e-5
        finally:A.closeDocument(d.Name)
    c.update(status="SUPPORTED_GEOMETRY_NEEDS_CURRENT_CHECK",hits=[],new_STL=0,
        source_native=dest.relative_to(M.ROOT).as_posix(),
        actual_one_anchor_shift_mm=6.75,
        sources_at_final_build={Path(__file__).relative_to(M.ROOT).as_posix():M.sha(Path(__file__))})
    c["lengths"]["W012"].update(external_length_mm=path.Length,blank_margin_mm=200-path.Length-28-30)
    c["slots"][-2][0]+=6.75;c["slots"][-1][0]+=6.75
    M.save(OUT/"checks.json",c)
    print(json.dumps(dict(status=c["status"],length_mm=path.Length,new_STL=0)),flush=True)

if __name__=="__main__":
    sys.path.insert(0,str(M.ROOT/"tools/cad"));main()
