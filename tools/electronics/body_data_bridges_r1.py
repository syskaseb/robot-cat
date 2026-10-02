"""Three stationary P0 data bridges on the selected R36 Deck.

Whole routes, six insulated restraints and one editable Deck replacement.
Port pitch/height are explicit prototype datums, not delivered measurements.
No hardware access. Save intent and native source before expensive checks.
"""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "hardware/electronics/full-cat/body-data-bridges-r1"
CAD = ROOT / "hardware/cad/studies/body-data-bridges-r1"
START = "2026-10-01T22:59:16+00:00"
RADIUS = 5.2
OD = 1.3
ROUTES = {
    "W007": [[15,30.5,113.5],[15,17.5,113.5],[-9,17.5,113.5],
             [-9,17.5,126],[-9,-17.5,126],[-9,-17.5,113.5],[-9,-30.5,113.5]],
    "W011": [[15,-30.5,113.5],[15,-17.5,113.5],[99,-17.5,113.5],[99,-30.5,113.5]],
    "W012": [[123,-30.5,113.5],[123,-17.5,113.5],[135,-17.5,113.5],
             [135,-17.5,126],[135,17.5,126],[99,17.5,126],[99,17.5,113.5],[99,30.5,113.5]],
}
ENDS = {"W007": ["D_FL.5", "D_FR.1"], "W011": ["D_FR.5", "D_RR.1"],
        "W012": ["D_RR.5", "D_RL.1"]}
ANCHORS = [(name, end, p[0], math.copysign(26.3, p[1]))
           for name, points in ROUTES.items() for end,p in enumerate((points[0],points[-1]))]
PATH_BUILDER = None
DATUM_OVERRIDES = {}
ANCHOR_ROTATIONS = {}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")


def specifications():
    return dict(status="SAVED_INTENT_BEFORE_GEOMETRY", parent="one-batch-prototype-r36",
        wire_sku="LAPP4126002S", wire_mm2=.25, nominal_OD_mm=OD,
        static_radius_mm=RADIUS, routes=ROUTES, ends=ENDS, anchors=ANCHORS,
        connector_datums=dict(depth_face_y_mm=30.5, port_pitch_assumption_mm=6,
            entry_height_assumption_mm=4.5, block_floor_mm=109,
            port_order="Design left-to-right when looking at the entry face; label equal-potential cages on assembly",
            evidence="221-415 supplier dimensions29.8x18.3x8.15; rounded30x19x9 reservation. Cage centres provisional, not supplier-certified."),
        restraints=dict(sku="Hellermann111-02370 T18I", quantity=6,
            slot_size_xy_mm=[2,3.2], slot_offset_x_mm=5.5,
            strap_design_width_mm=2.5, strap_thickness_assumption_mm=.9,
            head_design_box_mm=[6,5,4],
            method="One tie on intact insulation at EACH endpoint, supported by the Deck; not bare copper, not the lever, not the electrical contact.",
            install="Thread loose ties through the bare Deck before electronics. Add wires after all WAGO bodies are restrained. Cut/replace ties for removal."),
        assembly=["Install Deck and route six loose ties before populated carrier/cassette.",
            "Place DATA WAGO blocks at their existing paired slots, mouths towards centre (+Y for south row, -Y for north row).",
            "Form blue stationary bridges, mark both ends W007/W011/W012, preserve port roles; route above P_FRONT/G2 only at specified raised lanes.",
            "Dry-fit insulated lengths plus two actual housing strip lengths. Fit one bare untinned strand bundle per cage and close levers.",
            "Tighten six ties on insulation only, retain broad bends; excess purchase stock stays outside robot. Test continuity and 12 IDs in phase2."],
        stock="Existing7m purchase minimum; three blanks provisionally200mm each. Trim on unpowered dry fit, never coil unused metres inside the body.",
        datum_overrides=DATUM_OVERRIDES,
        anchor_rotations_deg={f"{n}:{e}":a for (n,e),a in ANCHOR_ROTATIONS.items()},
        physical_pass=False, W5_complete=False, new_STL=0,
        phase2=["Delivered cage height/pitch/order, housing strips, actual tie heads and retention",
                "PVC forming/print slot fit, signal integrity1Mbaud and full leg harness integration"],
        scope="Changed three stationary bridges and their restraints; no moving leg approval, no whole robot certification.")


def main():
    import FreeCAD as A
    import Part
    import MeshPart
    import Sketcher
    sys.path.insert(0, str(ROOT / "tools/cad"))
    from check_main_p0_placement import SavedShapes, prop
    from check_p0_leg_geometry import world_shape
    from xb11_upstream_route import rounded
    from open_deck_p0_plate import rect
    OUT.mkdir(parents=True, exist_ok=True)
    CAD.mkdir(parents=True, exist_ok=True)
    assert not (OUT/"checks.json").exists(), "Preserve evidence; use a new revision"
    plan=specifications()
    save(OUT/"plan.json",plan)
    sources={}
    def load(rel):
        p=ROOT/rel; sources[rel]=sha(p); s=Part.Shape(); s.read(str(p)); return s
    def box(b):
        return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    deck_rel="hardware/cad/studies/pi-complete-native-r2/Deck_WORLD.brep"
    owners={"Deck":load(deck_rel),
        "Carrier":load("hardware/cad/studies/pi-complete-native-r2/Carrier_WORLD.brep"),
        "Cover":load("hardware/cad/studies/head-yaw-end-restraints-r1/CoverYawEndSeat.brep"),
        "Shelf":load("hardware/cad/studies/pwm-branch-restraints-r4/ShelfPWMGroundTerminal.brep")}
    for n in ("PiTray","BUSBracket"):
        owners[n]=load(f"hardware/cad/studies/pi-complete-native-r2/{n}_WORLD.brep")
    p=ROOT/"hardware/electronics/power-platform/open-deck-p0/layout.json"
    layout=json.loads(p.read_text(encoding="utf-8"));sources[p.relative_to(ROOT).as_posix()]=sha(p)
    for c in layout["components"]:
        if c["kind"]!="WAGO" or c["id"]=="P_REAR": continue
        x0,y0,x1,y1=c["footprint_xyxy_mm"]
        owners[c["id"]+"_design"]=box([x0+21,y0,109,x1+21,y1,109+c["planning_height_mm"]])
    owners["P_REAR_design"]=box([10,-18.5,124,32,18.5,135])
    for folder in ("pi-wiring-complete-r13", "pi-power-usb-r4", "head-connected-feeds-r8",
                   "tail-ground-direct-r1", "tail-central-routes-r3", "aux-converter-routes-r5",
                   "xa05-main-aux-return-r2", "xa06-ground-bridge-r1", "xb11-upstream-route-r3",
                   "pwm-fused-pigtail-r1"):
        for p in sorted((ROOT/"hardware/electronics/full-cat"/folder).glob("*.brep")):
            if p.name.endswith("_CENTERLINE.brep"): continue
            # This cache includes the historical Speaker, expressly excluded
            # from the current hobby scope. Geometry owners are loaded separately.
            if p.name.startswith("obstacle_"): continue
            if folder=="pi-wiring-complete-r13" and not p.name.endswith("_DESIGN.brep"): continue
            rel=p.relative_to(ROOT).as_posix();owners[folder+"/"+p.stem]=load(rel)
    routes={}; rows=[]; lengths={}
    for name, points in ROUTES.items():
        path=PATH_BUILDER(name,points) if PATH_BUILDER else rounded([A.Vector(*p) for p in points],RADIUS)
        pieces=[]
        for i,e in enumerate(path.Edges):
            profile=Part.Wire([Part.makeCircle(OD/2,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])
            s=Part.Wire([e]).makePipeShell([profile],True,False)
            assert s.isValid() and len(s.Solids)==1
            pieces.append(s);s.exportBrep(str(OUT/f"{name}_{i}_DESIGN.brep"))
            e.exportBrep(str(OUT/f"{name}_{i}_CENTERLINE.brep"))
        routes[name]=pieces
        # Strip reserve28 covers two nominal221-615 maxima, deliberately wider
        # than the unconfirmed221-415 delivered marking. It is a CUT allowance,
        # not an instruction to strip14mm on221-415.
        lengths[name]=dict(external_length_mm=path.Length, copper_trim_allowance_mm=28,
            rework_allowance_mm=30, proposed_blank_mm=200,
            blank_margin_mm=200-path.Length-28-30, actual_strip_mm=None)
        assert lengths[name]["blank_margin_mm"]>=0, (name,lengths[name])
    def check(label, pieces, targets):
        for name,t in targets.items():
            for i,s in enumerate(pieces):
                for j,q in enumerate(t.Solids):
                    if not s.BoundBox.intersect(q.BoundBox): continue
                    v=s.common(q).Volume
                    rows.append(dict(part=label,segment=i,owner=name,owner_solid=j,hit_mm3=v))
    for n,s in routes.items(): check(n,s,owners)
    for a,aa in routes.items():
        for b,bb in routes.items():
            if a<b: check(a,aa,{b:Part.makeCompound(bb)})
    hits=[r for r in rows if r["hit_mm3"]>1e-5]
    save(OUT/"route-checks.json",dict(rows=rows,hits=hits,lengths=lengths,physical_pass=False))
    if hits:
        save(OUT/"checks.json",dict(status="ROUTES_REJECTED",hits=hits,new_STL=0,sources=sources))
        print(json.dumps(dict(status="ROUTES_REJECTED",hits=hits)),flush=True);return
    d=A.newDocument("BodyDataBridgesR1")
    try:
        v=d.addObject("App::VarSet","Parameters")
        for n,value in (("SlotWidth",2),("SlotLength",3.2),("DeckThickness",4)):
            v.addProperty("App::PropertyLength",n);setattr(v,n,value)
        parent=d.addObject("PartDesign::Feature","PinnedR36Deck");parent.Shape=owners["Deck"]
        parent.Label="Selected R36 Deck [unchanged inherited geometry]"
        sk=d.addObject("Sketcher::SketchObject","SixDataRestraintPairs")
        sk.Placement.Base.z=105
        def slot_locations(n,e,x,y):
            turn=ANCHOR_ROTATIONS.get((n,e),0)
            assert turn in (0,90)
            return [(x+dx,y,2,3.2) if turn==0 else (x,y+dx,3.2,2)
                    for dx in (-5.5,5.5)]
        for n,e,x,y in ANCHORS:
            for xx,yy,w,h in slot_locations(n,e,x,y):rect(sk,xx-w/2,yy-h/2,w,h)
        assert sk.FullyConstrained and sk.solve()==0
        cutter=d.addObject("Part::Extrusion","DataTieThroughTool")
        cutter.Base=sk;cutter.Dir=A.Vector(0,0,4);cutter.Solid=True
        final=d.addObject("Part::Cut","FinishedDeck");final.Base=parent;final.Tool=cutter;final.Refine=False
        # Source precedes recompute/BOP/mesh.
        dest=CAD/"DeckDataBridges.FCStd";d.saveAs(str(dest));d.recompute()
        shape=final.Shape.copy();assert shape.isValid() and len(shape.Solids)==1 and not shape.check(True)
        added=shape.cut(owners["Deck"]).Volume;removed=owners["Deck"].cut(shape).Volume
        expected=12*2*3.2*4
        assert added<1e-5 and abs(removed-expected)<1e-4,(added,removed,expected)
        before=shape.Volume;cutter.Dir=A.Vector(0,0,3.8);d.recompute()
        altered=final.Shape.Volume;assert abs(altered-before)>1e-5
        cutter.Dir=A.Vector(0,0,4);d.recompute();assert abs(final.Shape.Volume-before)<1e-5
        bands=[];slot_probes=[]
        for n,e,x,y in ANCHORS:
            z=113.5+OD/2
            b=[box([dx-.45,-1.25,104.1,dx+.45,1.25,z+.9]) for dx in (-5.5,5.5)]
            b.extend([box([-5.95,-1.25,z,5.95,1.25,z+.9]),
                      box([-5.95,-1.25,104.1,5.95,1.25,105]),
                      box([4.5,-2.5,100.1,10.5,2.5,104.1])])
            for s in b:
                s.rotate(A.Vector(),A.Vector(0,0,1),ANCHOR_ROTATIONS.get((n,e),0))
                s.translate(A.Vector(x,y,0))
            label=f"{n}_end{e}_tie"
            bands.extend([(label+i.__str__(),s) for i,s in enumerate(b)])
            for xx,yy,w,h in slot_locations(n,e,x,y):
                probe=box([xx-w/2+.01,yy-h/2+.01,104.9,xx+w/2-.01,yy+h/2-.01,109.1])
                assert probe.common(shape).Volume<1e-5
                slot_probes.append([xx,yy,w,h])
            targets=dict(owners);targets["Deck"]=shape
            targets.update({k:Part.makeCompound(v) for k,v in routes.items()})
            check(label,b,targets)
        for i,(a,s) in enumerate(bands):
            check(a,[s],{b:t for b,t in bands[i+1:] if b[:-1]!=a[:-1]})
        hits=[r for r in rows if r["hit_mm3"]>1e-5]
        d.save();shape.exportBrep(str(CAD/"Deck_WORLD.brep"))
        result=dict(status="RESTRAINTS_REJECTED" if hits else "THREE_DATA_BRIDGES_NOMINAL_COMPLETE",
            hits=hits,checked_overlapping_pairs=len(rows),rows=rows,lengths=lengths,
            slots=slot_probes,removed_mm3=removed,added_mm3=added,strict_BOP_errors=0,
            source_saved_before_BOP=True,fully_constrained_sketches=1,
            depth_probe_volumes_mm3=[before,altered,final.Shape.Volume],
            physical_pass=False,W5_complete=False,new_STL=0,sources=sources)
        if not hits:
            mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
            assert mesh.isSolid() and mesh.countComponents()==1
            bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
            dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength]
            assert max(dims)+10<=256
            mesh.write(str(CAD/"Deck_x1.stl"));result.update(new_STL=1,closed=True,components=1,
                dimensions_mm=dims,orientation="Original lower Deck base on bed;5mm brim fits256, actual supports/slicer phase2")
    finally:
        A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix="robot-cat-data-deck-") as td:
        p=Path(td)/dest.name;shutil.copy2(dest,p)
        d=A.openDocument(str(p));d.recompute()
        try:
            s=d.FinishedDeck.Shape
            assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-before)<1e-5
            result["relocated_reopen_recompute"]=True
        finally:A.closeDocument(d.Name)
    result["source_scripts"]={p.relative_to(ROOT).as_posix():sha(p)
        for p in (Path(__file__),Path(sys.argv[0]).resolve())}
    save(OUT/"checks.json",result)
    end=datetime.now(timezone.utc)
    save(OUT/"work-time.json",dict(start_utc=START,end_utc=end.isoformat(),
        wall_seconds=(end-datetime.fromisoformat(START)).total_seconds(),
        work="Instructions, sources, full three-data-bridge construction and geometry; packaging later",
        result=result["status"],new_STL=result["new_STL"]))
    print(json.dumps({k:result[k] for k in ("status","hits","new_STL","lengths","removed_mm3")}),flush=True)


if __name__=="__main__":main()
