"""Keep R3 wires/cages; move two restraints along straight insulation lanes.

R4 north tie grazed the XA05 elbow. R5 equivalent-cage shift hit P0Support3;
unsigned rectangle lengths also inverted one slot when translated. Preserve
those failures. This source gives every rectangle positive signed dimensions.
"""
import copy,json,sys,shutil,tempfile
from pathlib import Path
import body_data_bridges_r4 as R4
M=R4.M
OUT=M.ROOT/"hardware/electronics/full-cat/body-data-bridges-r6"
CAD=M.ROOT/"hardware/cad/studies/body-data-bridges-r6"
PRIOR=R4.PRIOR
M.ANCHORS=[(n,e,x,(-27.8 if n=="W012" and e==0 else 24.0 if n=="W012" and e==1 else y))
           for n,e,x,y in M.ANCHORS]

def main():
    import FreeCAD as A
    import Part
    import Sketcher
    OUT.mkdir(exist_ok=True);CAD.mkdir(exist_ok=True);assert not (OUT/"checks.json").exists()
    old=json.loads((R4.OUT/"checks.json").read_text(encoding="utf-8"))
    plan=json.loads((R4.OUT/"interface.json").read_text(encoding="utf-8"))
    plan.update(anchors=M.ANCHORS,route_geometry_source={n:PRIOR.relative_to(M.ROOT).as_posix() for n in M.ROUTES},
        selected_recipe="R6 supported DATA interface: unchanged R3 paths, two longitudinal anchor moves. R1-R5 unselected diagnostics.")
    plan["connector_datums"]["port_order"]="Global +X left-to-right design labels on both rows; not manufacturer numbers or viewer-relative. Mark logical roles at assembly."
    plan["datum_overrides"]["D_RL_physical_cages_left_to_right"]=[f"D_RL.{i}" for i in range(1,6)]
    plan["datum_overrides"]["R6_anchor_changes"]="W012 southY-29→-27.8 clears DRR housing; northY26.3→24 keeps the entire tie before the XA05 R15 elbow atY25. P0Support3 and DATA cages unchanged."
    plan["restraints"].pop("verified_utc",None)
    plan["restraints"]["manufacturer_verification_date_utc"]="2026-10-01"
    M.save(OUT/"interface.json",plan)
    d=A.openDocument(str(R4.CAD/"DeckDataBridgesSupported.FCStd"));dest=CAD/"DeckDataBridgesSupported.FCStd"
    def signed_rectangles(sk):
        dimensions=[]
        for i,k in enumerate(sk.Constraints):
            if k.Type=="Distance" and k.FirstPos==0 and k.Second==-2000:
                assert k.First%4 in (0,1)
                dimensions.append((i,k.First,"DistanceX" if k.First%4==0 else "DistanceY",k.Value))
        assert len(dimensions)==sk.GeometryCount//2
        for i,_,_,_ in reversed(dimensions):sk.delConstraint(i)
        for _,geo,kind,value in dimensions:sk.addConstraint(Sketcher.Constraint(kind,geo,1,geo,2,value))
        assert sk.FullyConstrained and sk.solve()==0
    def move_y(sk,first_set,dy):
        changed=0
        for i,k in enumerate(sk.Constraints):
            if k.Type=="DistanceY" and k.FirstPos==1 and k.Second==-2000 and k.First in first_set:
                sk.setDatum(i,A.Units.Quantity(f"{k.Value+dy} mm"));changed+=1
        assert changed==len(first_set) and sk.FullyConstrained and sk.solve()==0
    try:
        d.saveAs(str(dest));slots=d.SixDataRestraintPairs;signed_rectangles(slots)
        for i in range(6):signed_rectangles(d.getObject(f"SaddleFoot{i}"))
        move_y(slots,{32,36},1.2);move_y(slots,{40,44},-2.3)
        move_y(d.SaddleFoot4,{0},1.2);move_y(d.SaddleFoot5,{0},-2.3)
        d.SaddleGroove4.Placement.Base.y+=1.2;d.SaddleGroove5.Placement.Base.y-=2.3
        d.save();d.recompute();shape=d.SupportedDeck.Shape.copy()
        assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
        removed=d.PinnedR36Deck.Shape.cut(d.FinishedDeck.Shape).Volume
        assert abs(removed-307.2)<1e-4,removed
        # Do not rely on solver status alone: all 12 physical slot bounds must
        # have the expected positive-size rectangles after longitudinal edits.
        intended=list(old["slots"])
        intended[-4:]=[[119,-27.8,2,3.2],[130,-27.8,2,3.2],[92,24,2,3.2],[103,24,2,3.2]]
        actual=[w.BoundBox for w in slots.Shape.Wires]
        assert len(actual)==12
        for x,y,w,h in intended:
            assert any(abs(b.XMin-(x-w/2))<1e-6 and abs(b.XMax-(x+w/2))<1e-6
                and abs(b.YMin-(y-h/2))<1e-6 and abs(b.YMax-(y+h/2))<1e-6 for b in actual),(x,y,w,h)
        before=shape.Volume;shape.exportBrep(str(CAD/"Deck_WORLD.brep"));d.save()
    finally:A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix="robot-cat-data-longitudinal-") as td:
        target=Path(td)/dest.name;shutil.copy2(dest,target);d=A.openDocument(str(target));d.recompute()
        try:
            s=d.SupportedDeck.Shape;assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-before)<1e-5
        finally:A.closeDocument(d.Name)
    old.update(status="SUPPORTED_GEOMETRY_NEEDS_CURRENT_CHECK",hits=[],slots=intended,new_STL=0,
        source_native=dest.relative_to(M.ROOT).as_posix(),signed_rectangle_directions=True,
        all_actual_slot_bounds_checked=True,changed_anchor_y_mm=[1.2,-2.3],
        final_builder_sha256=M.sha(Path(__file__)),source_native_reopen_recompute=True)
    M.save(OUT/"checks.json",old)
    print(json.dumps(dict(status=old["status"],slots=12,new_STL=0)),flush=True)

if __name__=="__main__":
    sys.path.insert(0,str(M.ROOT/"tools/cad"));main()
