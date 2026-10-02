"""Finish three DATA bridges: supported insulation, sourced T18I thickness.

Reuse proven R3 slots/native source and unchanged R2 routes. Add six integral
saddles. Replace the old cached Deck owner by the actual new Deck, not a waiver.
"""
import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime,timezone
import body_data_bridges_r3 as R3
M=R3.M
OUT=M.ROOT/"hardware/electronics/full-cat/body-data-bridges-r4"
CAD=M.ROOT/"hardware/cad/studies/body-data-bridges-r4"
PRIOR=M.OUT
PRIOR_CAD=M.CAD

def main():
    import FreeCAD as A
    import Part
    import MeshPart
    import Sketcher
    from open_deck_p0_plate import rect
    OUT.mkdir(exist_ok=True);CAD.mkdir(exist_ok=True)
    assert not (OUT/"checks.json").exists()
    old=json.loads((PRIOR/"checks.json").read_text(encoding="utf-8"))
    assert old["relocated_reopen_recompute"] and old["removed_mm3"]==307.20000000000005
    assert all(r["owner"]=="pi-wiring-complete-r13/Deck_DESIGN" for r in old["hits"])
    p=json.loads((PRIOR/"plan.json").read_text(encoding="utf-8"))
    p.update(status="THREE_DATA_BRIDGES_SUPPORTED_CONDITIONAL_PROTOTYPE",route_geometry_source=PRIOR.relative_to(M.ROOT).as_posix(),
        selected_recipe="This interface supersedes the early plan's .9mm strap assumption and6mm pitch. R3 diagnostic is NOT a selected current Deck collision.")
    p["connector_datums"]["port_pitch_assumption_mm"]=6.75
    p["restraints"].update(strap_thickness_mm=1.2,strap_thickness_assumption_mm=None,
        manufacturer_url="https://www.hellermanntyton.com/products/cable-ties-inside-serrated/t18i/111-02370",
        verified_utc="2026-10-01T23:34:00Z",manufacturer_dimensions_mm=dict(length=145,width=2.5,thickness=1.2,head_length=4.8,head_width=4.5,head_height=3.5),
        supported_seats=dict(quantity=6,integral_with_Deck=True,base_xy_mm=[6,4],bottom_z_mm=108.8,top_z_mm=113.6,
            groove_radius_mm=.75,wire_radius_mm=.65,nominal_groove_radial_play_mm=.1,
            rule="Tighten by hand only to seat intact PVC in the printed groove; do not crush insulation. Do not use the electrical cage as the strain anchor. Verify actual PVC/print fit phase2."))
    p["assembly"].insert(3,"Seat the insulation at all six integral saddles; upper routes stay above their specified crossings. Thread T18I width2.5/thickness1.2 through both slots; lock head underneath Deck.")
    M.save(OUT/"interface.json",p)
    d=A.openDocument(str(PRIOR_CAD/"DeckDataBridges.FCStd"));dest=CAD/"DeckDataBridgesSupported.FCStd"
    try:
        d.saveAs(str(dest));base=d.FinishedDeck;base_shape=base.Shape.copy();pads=[]
        parameters=d.addObject("App::VarSet","DataSaddleParameters")
        parameters.addProperty("App::PropertyLength","Height");parameters.Height=4.8
        parameters.addProperty("App::PropertyLength","GrooveRadius");parameters.GrooveRadius=.75
        for i,(n,e,x,y) in enumerate(M.ANCHORS):
            turn=M.ANCHOR_ROTATIONS.get((n,e),0)
            sk=d.addObject("Sketcher::SketchObject",f"SaddleFoot{i}");sk.Placement.Base.z=108.8
            w,h=(6,4) if turn==0 else (4,6)
            rect(sk,x-w/2,y-h/2,w,h);assert sk.FullyConstrained and sk.solve()==0
            pad=d.addObject("Part::Extrusion",f"SaddlePad{i}");pad.Base=sk;pad.Dir=A.Vector(0,0,4.8);pad.Solid=True
            pad.setExpression("Dir.z","DataSaddleParameters.Height")
            groove=d.addObject("Part::Cylinder",f"SaddleGroove{i}");groove.Radius=.75;groove.Height=4.2
            groove.setExpression("Radius","DataSaddleParameters.GrooveRadius")
            direction=A.Vector(0,1,0) if turn==0 else A.Vector(1,0,0)
            start=A.Vector(x,y-2.1,113.5) if turn==0 else A.Vector(x-2.1,y,113.5)
            groove.Placement=A.Placement(start,A.Rotation(A.Vector(0,0,1),direction))
            seat=d.addObject("Part::Cut",f"DataSaddle{i}");seat.Base=pad;seat.Tool=groove;seat.Refine=False;pads.append(seat)
        final=d.addObject("Part::MultiFuse","SupportedDeck");final.Shapes=[base]+pads;final.Refine=False
        d.save();d.recompute();shape=final.Shape.copy()
        assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
        assert base_shape.cut(shape).Volume<1e-5
        added=shape.cut(base_shape).Volume
        assert 400<added<650,added
        before=shape.Volume;parameters.Height=4.7;d.recompute();altered=final.Shape.Volume
        assert abs(before-altered)>1e-5
        parameters.Height=4.8;d.recompute();assert abs(final.Shape.Volume-before)<1e-5
        d.save();shape.exportBrep(str(CAD/"Deck_WORLD.brep"))
    finally:A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix="robot-cat-supported-data-") as td:
        target=Path(td)/dest.name;shutil.copy2(dest,target);d=A.openDocument(str(target));d.recompute()
        try:
            s=d.SupportedDeck.Shape
            assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-before)<1e-5
        finally:A.closeDocument(d.Name)
    checks=dict(old,status="SUPPORTED_GEOMETRY_NEEDS_CURRENT_CHECK",hits=[],
        removed_mm3=old["removed_mm3"],added_saddle_mm3=added,new_STL=0,
        source_native=dest.relative_to(M.ROOT).as_posix(),source_script=M.sha(Path(__file__)),
        supported_native_reopen_recompute=True,fully_constrained_added_saddle_sketches=6,
        saddle_height_probe_volumes_mm3=[before,altered,before],physical_pass=False,W5_complete=False,
        old_cache_hits="R3 hit only the old uncut pi-wiring Deck_DESIGN; replace that owner with SupportedDeck in the fresh check, not an ignored physical collision.",
        construction_scripts={p.relative_to(M.ROOT).as_posix():M.sha(p) for p in (Path(__file__),Path(__file__).with_name("body_data_bridges_r1.py"),Path(__file__).with_name("body_data_bridges_r2.py"),Path(__file__).with_name("body_data_bridges_r3.py"))})
    M.save(OUT/"checks.json",checks)
    print(json.dumps(dict(status=checks["status"],added_saddle_mm3=added)),flush=True)

if __name__=="__main__":
    import sys
    sys.path.insert(0,str(M.ROOT/"tools/cad"))
    main()
