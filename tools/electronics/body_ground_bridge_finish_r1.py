"""Finish W061 with three integral Deck seats and six actual tie passages.

Preserve selected R37 source/history. Append editable features; save before
recompute. Check the changed interfaces, current routes and conservative fuse
caps. This is a single prototype bridge, not whole W5 or physical approval.
"""
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import sys
import tempfile
import body_ground_routes_r1 as M

ROOT=M.ROOT
OUT=ROOT/"hardware/electronics/full-cat/body-ground-bridge-finish-r5"
CAD=ROOT/"hardware/cad/studies/body-ground-bridge-finish-r5"
ROUTES=ROOT/"hardware/electronics/full-cat/body-ground-bridge-r5"
ANCHORS=[dict(id="G1_end",x=58.5,y=12.5,z=113.5,rotation=0,width=8,length=2.5),
         dict(id="G2_end",x=111,y=11,z=113.5,rotation=0,width=8,length=2.5),
         dict(id="Middle",x=84,y=75,z=136.5,rotation=90,width=12,length=22.5)]

def main():
    import FreeCAD as A
    import Part
    import MeshPart
    import Sketcher
    sys.path.insert(0,str(ROOT/"tools/cad"))
    from open_deck_p0_plate import rect
    OUT.mkdir(exist_ok=True);CAD.mkdir(exist_ok=True)
    assert not (OUT/"checks.json").exists()
    start=datetime.now(timezone.utc)
    c=json.loads((ROUTES/"checks.json").read_text(encoding="utf-8"))
    assert c["status"]=="GROUND_ROUTES_CLEAR_NEED_RESTRAINTS" and not c["hits"]
    interface=json.loads((ROUTES/"intent.json").read_text(encoding="utf-8"))
    interface.update(status="SAVED_BEFORE_NATIVE_GROUND_RESTRAINTS",route_source=ROUTES.relative_to(ROOT).as_posix(),
        anchors=ANCHORS,groove_radius_mm=2.3,radial_prototype_play_mm=.2,
        restraints=dict(sku="Hellermann111-02370 T18I",quantity=3,width_mm=2.5,thickness_mm=1.2,
            head_design_box_mm=[6,5,4],new_separate_parts=0,integral_Deck_seats=3,
            strip_rule="G1 221-61512-14mm; G2 221-41511mm. Confirm delivered markings; reserve28 is NOT a strip length."),
        assembly=["Before populated electronics, thread the two endpoint T18I through four Deck passages and the middle T18I through two elevated beam passages; heads underneath each supporting surface.",
            "Place MTA holders/fuses before W061 loop; retain the original BAT-side G1.1 cage. Label equal-potential cages according to this interface.",
            "Form one TKD2500125 blank using at least R21, no loop kink. Insert one untinned conductor per G1.5/G2.1 cage and seat insulation in all three grooves.",
            "Tighten ties by hand without crushing silicone. Keep elevated U loop above the capped fuses and below Carrier; do not coil unused stock inside robot.",
            "For obstructed fuse removal: battery disconnected first, remove upper Carrier as prescribed, cut/replace these three ties, unlatch both W061 ends and lift the loop before extracting a fuse. Do not yank through the installed wire."],
        source_time_utc=start.isoformat(),physical_pass=False,W5_complete=False,selected=False,new_STL=0,
        pending="Native, passages, parameter probe/reopen, changed-body collisions, export and one selected package")
    M.save(OUT/"interface.json",interface)
    source=ROOT/"hardware/cad/studies/body-data-bridges-r7/DeckDataBridgesSupported.FCStd"
    d=A.openDocument(str(source));dest=CAD/"DeckGroundBridgeSupported.FCStd"
    try:
        d.saveAs(str(dest));old=d.SupportedDeck;before=old.Shape.copy()
        p=d.addObject("App::VarSet","GroundSeatParameters")
        for n,v in (("GrooveRadius",2.3),("ExitSeatHeight",6.4),("MiddleSeatHeight",29.4),("MiddleBeamThickness",6.2)):
            p.addProperty("App::PropertyLength",n);setattr(p,n,v)
        slots=d.addObject("Sketcher::SketchObject","GroundTieSlots")
        slots.AttacherEngine="Engine Plane"
        slots.Placement=A.Placement(A.Vector(0,0,105),A.Rotation())
        centres=[];pads=[];feet=[];middle_centres=[]
        mid_slots=d.addObject("Sketcher::SketchObject","MiddleTieSlots")
        mid_slots.AttacherEngine="Engine Plane"
        mid_slots.Placement=A.Placement(A.Vector(0,0,132),A.Rotation())
        for i,a in enumerate(ANCHORS):
            x,y,z,turn=a["x"],a["y"],a["z"],a["rotation"]
            for dx in (-5.5,5.5):
                xx,yy,w,h=(x+dx,y,2,3.2) if turn==0 else (x,y+dx,3.2,2)
                rect(mid_slots if turn else slots,xx-w/2,yy-h/2,w,h)
                centres.append([xx,yy,w,h])
                if turn:middle_centres.append([xx,yy,w,h])
            foot=d.addObject("Sketcher::SketchObject",f"GroundSeatFoot{i}")
            foot.AttacherEngine="Engine Plane"
            foot.Placement=A.Placement(A.Vector(0,0,108.8),A.Rotation())
            feet.append(foot)
            if turn:rect(foot,78,58,4,4)
            else:rect(foot,x-a["width"]/2,y-a["length"]/2,a["width"],a["length"])
            assert foot.FullyConstrained and foot.solve()==0
            pad=d.addObject("Part::Extrusion",f"GroundSeatPad{i}");pad.Base=foot;pad.Dir=A.Vector(0,0,29.4 if turn else 6.4);pad.Solid=True
            pad.setExpression("Dir.z","GroundSeatParameters.MiddleSeatHeight" if turn else "GroundSeatParameters.ExitSeatHeight")
            groove=d.addObject("Part::Cylinder",f"GroundSeatGroove{i}");groove.Radius=2.3
            groove.setExpression("Radius","GroundSeatParameters.GrooveRadius")
            groove.Height=(a["width"] if turn else a["length"])+.2
            direction=A.Vector(1,0,0) if turn else A.Vector(0,1,0)
            origin=A.Vector(x-a["width"]/2-.1,y,z) if turn else A.Vector(x,y-a["length"]/2-.1,z)
            groove.Placement=A.Placement(origin,A.Rotation(A.Vector(0,0,1),direction))
            raw=pad
            if turn:
                beamfoot=d.addObject("Sketcher::SketchObject","MiddleBeamFoot")
                beamfoot.AttacherEngine="Engine Plane"
                beamfoot.Placement=A.Placement(A.Vector(0,0,132),A.Rotation())
                rect(beamfoot,78,60,12,22.5);feet.append(beamfoot)
                beam=d.addObject("Part::Extrusion","MiddleBeamPad");beam.Base=beamfoot;beam.Dir=A.Vector(0,0,6.2);beam.Solid=True
                beam.setExpression("Dir.z","GroundSeatParameters.MiddleBeamThickness")
                midtool=d.addObject("Part::Extrusion","MiddleTieThroughTool");midtool.Base=mid_slots;midtool.Dir=A.Vector(0,0,6.2);midtool.Solid=True
                midtool.setExpression("Dir.z","GroundSeatParameters.MiddleBeamThickness")
                midbase=d.addObject("Part::Cut","MiddleSlottedBeam");midbase.Base=beam;midbase.Tool=midtool;midbase.Refine=False
                raw=d.addObject("Part::MultiFuse","MiddleSeatRaw");raw.Shapes=[pad,midbase];raw.Refine=False
            seat=d.addObject("Part::Cut",f"GroundSeat{i}");seat.Base=raw;seat.Tool=groove;seat.Refine=False;pads.append(seat)
        assert slots.FullyConstrained and slots.solve()==0
        tool=d.addObject("Part::Extrusion","GroundTieThroughTool");tool.Base=slots;tool.Dir=A.Vector(0,0,4);tool.Solid=True
        base=d.addObject("Part::Cut","GroundSlottedDeck");base.Base=old;base.Tool=tool;base.Refine=False
        final=d.addObject("Part::MultiFuse","GroundSupportedDeck");final.Shapes=[base]+pads;final.Refine=False
        # Initialize new restored-document sketches before the full Boolean
        # recompute. Failed finish-r1 retained the pre-recompute planes in XML
        # but recomputed them at z=0, leaving four disconnected solids.
        assert all(f.FullyConstrained and f.solve()==0 for f in [slots,mid_slots]+feet)
        d.recompute([slots,mid_slots]+feet)
        assert abs(slots.Shape.BoundBox.ZMin-105)<1e-6
        assert all(abs(f.Shape.BoundBox.ZMin-(132 if f.Name=="MiddleBeamFoot" else 108.8))<1e-6 for f in feet)
        d.save();d.recompute();shape=final.Shape.copy()
        print("FULL_RECOMPUTE",[(f.Name,f.Placement.Base.z) for f in [slots]+feet],len(shape.Solids),flush=True)
        if not shape.isValid() or len(shape.Solids)!=1:
            d.save()
            M.save(OUT/"native-failure.json",dict(status="REJECTED",solids=len(shape.Solids),valid=shape.isValid(),physical_pass=False))
            raise AssertionError("Invalid or disconnected native Deck; failure source retained")
        assert not shape.check(True)
        removed=before.cut(base.Shape).Volume;assert abs(removed-102.4)<1e-4,removed
        middle_removed=beam.Shape.cut(midbase.Shape).Volume
        assert abs(middle_removed-79.36)<1e-4,middle_removed
        added=shape.cut(base.Shape).Volume
        volume=shape.Volume;p.MiddleSeatHeight=29.3;d.recompute();probe=final.Shape.Volume
        assert abs(probe-volume)>1e-5
        p.MiddleSeatHeight=29.4;d.recompute();assert abs(final.Shape.Volume-volume)<1e-5
        for x,y,w,h in [q for q in centres if q not in middle_centres]:
            q=Part.makeBox(w-.02,h-.02,4.2,A.Vector(x-w/2+.01,y-h/2+.01,104.9))
            assert q.common(shape).Volume<1e-5,(x,y)
        for x,y,w,h in middle_centres:
            q=Part.makeBox(w-.02,h-.02,6.4,A.Vector(x-w/2+.01,y-h/2+.01,131.9))
            assert q.common(shape).Volume<1e-5,(x,y)
        seats={f"Seat{i}":seat.Shape.copy() for i,seat in enumerate(pads)}
        for name,s in seats.items():
            assert s.isValid() and len(s.Solids)==1 and not s.check(True)
            s.exportBrep(str(CAD/(name+"_WORLD.brep")))
        d.save();shape.exportBrep(str(CAD/"Deck_WORLD.brep"))
    finally:A.closeDocument(d.Name)
    with tempfile.TemporaryDirectory(prefix="robot-cat-ground-native-") as td:
        q=Path(td)/dest.name;shutil.copy2(dest,q);d=A.openDocument(str(q));d.recompute()
        try:
            s=d.GroundSupportedDeck.Shape
            assert s.isValid() and len(s.Solids)==1 and not s.check(True) and abs(s.Volume-volume)<1e-5
        finally:A.closeDocument(d.Name)
    owners,hashes=M.body_owners();owners.pop("Deck_R37")
    route={p.stem:None for p in ROUTES.glob("W061_*_DESIGN.brep")}
    for name in route:
        q=Part.Shape();q.read(str(ROUTES/(name+".brep")));route[name]=q
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    owners["F_AUX_conservative_case"]=box([51,11.6,122,72.2,23.6,142])
    owners["F_PWM_conservative_case"]=box([67.5,-17.91,127.49,75.9,-14.89,130.51])
    # Whole fuse ABOVE flange (deliberately over-conservative), not unknown
    # seating depth borrowed from a photo. Housing/projection XY also reserved.
    layout=json.loads((ROOT/"hardware/electronics/power-platform/open-deck-p0/layout.json").read_text(encoding="utf-8"))
    for component in layout["components"]:
        if component["kind"]!="servo_fuse":continue
        x,y=component["center_xy_mm"];x+=21
        owners[component["id"]+"_MTA_conservative_housing"]=box([x-7.75,y-14.25,82.5,x+7.75,y+14.25,111])
        owners[component["id"]+"_287_entire_height_above_flange"]=box([x-2.55,y-9.55,111,x+2.55,y+9.55,129.8])
    bands={}
    for a in ANCHORS:
        x,y,z,turn=a["x"],a["y"],a["z"],a["rotation"]
        upper=z+2.2;bottom=130.8 if turn else 103.8;head=127.1 if turn else 100.1
        bb=[box([dx-.6,-1.25,bottom,dx+.6,1.25,upper+1.2]) for dx in (-5.5,5.5)]
        bb += [box([-6.1,-1.25,upper,6.1,1.25,upper+1.2]),box([-6.1,-1.25,bottom,6.1,1.25,bottom+1.2]),box([4.5,-2.5,head,10.5,2.5,head+4])]
        for i,s in enumerate(bb):
            s.rotate(A.Vector(),A.Vector(0,0,1),turn);s.translate(A.Vector(x,y,0));bands[f"{a['id']}_tie_{i}"]=s
    rows=[]
    def check(n,s,m,t):
        for i,q in enumerate(s.Solids):
            for j,r in enumerate(t.Solids):
                if q.BoundBox.intersect(r.BoundBox):
                    rows.append(dict(part=n,owner=m,solid=i,owner_solid=j,hit_mm3=q.common(r).Volume))
    for n,s in {**route,**seats,**bands}.items():
        for m,t in owners.items():check(n,s,m,t)
    for n,s in {**route,**bands}.items():check(n,s,"CURRENT_GROUND_DECK",shape)
    for n,s in bands.items():
        for m,t in route.items():check(n,s,m,t)
    for n,s in seats.items():
        for m,t in route.items():check(n,s,m,t)
    items=list(bands.items())
    for i,(n,s) in enumerate(items):
        for m,t in items[i+1:]:
            if n.rsplit("_",1)[0]!=m.rsplit("_",1)[0]:check(n,s,m,t)
    hits=[r for r in rows if r["hit_mm3"]>1e-5]
    end=datetime.now(timezone.utc)
    result=dict(status="SUPPORTED_GROUND_BRIDGE_REJECTED" if hits else "SUPPORTED_GROUND_BRIDGE_COMPLETE",
        hits=hits,rows=rows,route_parent_checks_sha256=M.sha(ROUTES/"checks.json"),
        strict_BOP_errors=0,native_saved_before_recompute=True,relocated_reopen_recompute=True,
        fully_constrained_added_sketches=6,parameter_probe_volumes_mm3=[volume,probe,volume],
        removed_slot_mm3=removed,middle_removed_slot_mm3=middle_removed,added_seat_mm3=added,slots=centres,
        passage_planes_mm=[105,132],middle_slot_sidewall_mm=4.4,middle_groove_floor_mm=2.2,middle_post_root_xy=[78,58,82,62],
        source_native=dest.relative_to(ROOT).as_posix(),source_sha256={**hashes,source.relative_to(ROOT).as_posix():M.sha(source)},
        source_script_sha256=M.sha(Path(__file__)),physical_pass=False,W5_complete=False,new_STL=0,
        worker_start_utc=start.isoformat(),worker_end_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds())
    if not hits:
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
        assert mesh.isSolid() and mesh.countComponents()==1
        bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
        dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength]
        assert max(dims)+10<=256
        mesh.write(str(CAD/"Deck_x1.stl"));result.update(new_STL=1,closed=True,components=1,dimensions_mm=dims)
    M.save(OUT/"checks.json",result)
    interface.update(status=result["status"],new_STL=result["new_STL"],restraints_complete=not hits,
        lengths=c["lengths"],native=result["source_native"],pending="Selection/package after inspected preview" if not hits else "Actual hits retained; no selection")
    M.save(OUT/"interface.json",interface)
    vertices,triangles=shape.tessellate(.6)
    lines=json.loads((ROUTES/"preview-lines.json").read_text(encoding="utf-8"))
    M.save(OUT/"preview-geometry.json",dict(deck=dict(vertices=[list(v) for v in vertices],triangles=triangles),routes=lines,anchors=ANCHORS,slots=centres))
    print(json.dumps(dict(status=result["status"],hits=hits,pairs=len(rows),new_STL=result["new_STL"])),flush=True)

if __name__=="__main__":main()
