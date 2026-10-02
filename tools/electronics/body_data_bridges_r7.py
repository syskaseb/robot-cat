"""Keep P0 intact: shorten only the DRR-side seat and restore its tie lane.

R6's source tie hit P0Support2 below Deck. At the original Y=-29 the
2.5mm-wide strap clears that support; a matching 2.5mm-long insulation
seat also clears the WAGO mouth. No changed wire, cage or electrical role.
"""
import json,shutil,tempfile,sys
from pathlib import Path
import body_data_bridges_r6 as R6
M=R6.M
OUT=M.ROOT/"hardware/electronics/full-cat/body-data-bridges-r7"
CAD=M.ROOT/"hardware/cad/studies/body-data-bridges-r7"
PRIOR=R6.PRIOR
M.ANCHORS=[(n,e,x,-29.0 if n=="W012" and e==0 else y) for n,e,x,y in M.ANCHORS]

def main():
    import FreeCAD as A
    import Part
    OUT.mkdir(exist_ok=True);CAD.mkdir(exist_ok=True)
    assert not (OUT/"checks.json").exists()
    prior=json.loads((R6.OUT/"checks.json").read_text(encoding="utf-8"))
    rejected=json.loads((R6.OUT/"current-body-checks.json").read_text(encoding="utf-8"))
    assert {r["owner"] for r in rejected["hits"]}=={"P0Support2"}
    plan=json.loads((R6.OUT/"interface.json").read_text(encoding="utf-8"))
    plan.update(anchors=M.ANCHORS,selected_recipe="R7: unchanged three routes/cages, DRR-side seat2.5mm long at originalY-29; north tieY24. R1-R6 diagnostic only.")
    plan["datum_overrides"]["R7_anchor_changes"]="DRR source tie restoredY-29 to clear P0Support2. Its seat alone shortened from4 to2.5mm along the straight wire, clearing the WAGO mouth. Other five seats unchanged."
    plan["restraints"]["supported_seats"].update(base_xy_mm="Five6x4; W012/end0 only6x2.5",individual_override={"W012:0":dict(base_xy_mm=[6,2.5],center_xy_mm=[124.5,-29],groove_length_mm=2.7)})
    M.save(OUT/"interface.json",plan)
    d=A.openDocument(str(R6.CAD/"DeckDataBridgesSupported.FCStd"))
    dest=CAD/"DeckDataBridgesSupported.FCStd"
    try:
        d.saveAs(str(dest));slots=d.SixDataRestraintPairs
        def move_y(sk,geos,delta):
            count=0
            for i,k in enumerate(sk.Constraints):
                if k.Type=="DistanceY" and k.FirstPos==1 and k.Second==-2000 and k.First in geos:
                    sk.setDatum(i,A.Units.Quantity(f"{k.Value+delta} mm"));count+=1
            assert count==len(geos) and sk.FullyConstrained and sk.solve()==0
        move_y(slots,{32,36},-1.2)
        foot=d.SaddleFoot4;move_y(foot,{0},-.45)
        dimensions=[i for i,k in enumerate(foot.Constraints) if k.Type=="DistanceY" and k.First==1 and k.FirstPos==1 and k.Second==1 and k.SecondPos==2]
        assert len(dimensions)==1
        foot.setDatum(dimensions[0],A.Units.Quantity("2.5 mm"));assert foot.FullyConstrained and foot.solve()==0
        groove=d.SaddleGroove4;groove.Height=2.7;groove.Placement.Base.y=-30.35
        d.save();d.recompute();shape=d.SupportedDeck.Shape.copy()
        assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
        removed=d.PinnedR36Deck.Shape.cut(d.FinishedDeck.Shape).Volume
        assert abs(removed-307.2)<1e-4
        intended=list(prior["slots"]);intended[8:10]=[[119,-29,2,3.2],[130,-29,2,3.2]]
        actual=[w.BoundBox for w in slots.Shape.Wires];assert len(actual)==12
        for x,y,w,h in intended:
            assert any(abs(b.XMin-(x-w/2))<1e-6 and abs(b.XMax-(x+w/2))<1e-6 and abs(b.YMin-(y-h/2))<1e-6 and abs(b.YMax-(y+h/2))<1e-6 for b in actual)
        b=d.DataSaddle4.Shape.BoundBox
        assert abs(b.YMin+30.25)<1e-6 and abs(b.YMax+27.75)<1e-6
        volume=shape.Volume;added=shape.cut(d.FinishedDeck.Shape).Volume
        d.save();shape.exportBrep(str(CAD/"Deck_WORLD.brep"))
    finally:A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix="robot-cat-data-supported-") as td:
        p=Path(td)/dest.name;shutil.copy2(dest,p);d=A.openDocument(str(p));d.recompute()
        try:
            s=d.SupportedDeck.Shape;assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-volume)<1e-5
        finally:A.closeDocument(d.Name)
    prior.update(status="SUPPORTED_GEOMETRY_NEEDS_CURRENT_CHECK",hits=[],slots=intended,new_STL=0,
        source_native=dest.relative_to(M.ROOT).as_posix(),added_saddle_mm3=added,
        short_source_saddle_length_mm=2.5,source_tie_y_mm=-29,changed_anchor_y_mm=[0,-2.3],
        final_builder_sha256=M.sha(Path(__file__)),source_native_reopen_recompute=True)
    M.save(OUT/"checks.json",prior)
    print(json.dumps(dict(status=prior["status"],slots=12,new_STL=0)),flush=True)

if __name__=="__main__":
    sys.path.insert(0,str(M.ROOT/"tools/cad"));main()
