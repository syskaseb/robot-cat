"""Current retained body owners and actual route continuity, one bounded pass.

No legacy speaker/camera/head/PWM obstacles: their selected replacements are
checked by the construction recipe. Rest body/legs are not a motion approval.
"""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tools/cad"))

def main():
    import FreeCAD as A
    import Part
    import body_data_bridges_r7 as R4
    from check_main_p0_placement import SavedShapes,prop
    from check_p0_leg_geometry import world_shape
    M=R4.M;M.OUT=R4.OUT;M.CAD=R4.CAD
    baseline_path=ROOT/"hardware/electronics/full-cat/body-data-bridges-r4/current-body-checks.json"
    baseline=json.loads(baseline_path.read_text(encoding="utf-8"))
    for path,digest in baseline["source_sha256"].items():assert M.sha(ROOT/path)==digest,path
    assert not (M.OUT/"current-body-checks.json").exists()
    core=json.loads((M.OUT/"checks.json").read_text(encoding="utf-8"))
    assert core["status"]=="SUPPORTED_GEOMETRY_NEEDS_CURRENT_CHECK"
    shapes={}; paths={}; arc_checks={}; preview=[]
    def load(p):
        s=Part.Shape();s.read(str(p));return s
    for name,points in M.ROUTES.items():
        path=M.PATH_BUILDER(name,points);paths[name]=path
        radii=[e.Curve.Radius for e in path.Edges if hasattr(e.Curve,"Radius")]
        assert radii and min(radii)>=M.RADIUS-1e-7
        joints=[]
        for a,b in zip(path.Edges,path.Edges[1:]):
            gap=(a.valueAt(a.LastParameter)-b.valueAt(b.FirstParameter)).Length
            tangent=(a.tangentAt(a.LastParameter)-b.tangentAt(b.FirstParameter)).Length
            assert gap<1e-7 and tangent<1e-7,(name,gap,tangent)
            joints.append(dict(gap_mm=gap,tangent_difference=tangent))
        assert (path.Edges[0].valueAt(path.Edges[0].FirstParameter)-A.Vector(*points[0])).Length<1e-7
        assert (path.Edges[-1].valueAt(path.Edges[-1].LastParameter)-A.Vector(*points[-1])).Length<1e-7
        arc_checks[name]=dict(radii_mm=radii,joints=joints,length_mm=path.Length)
        source=R4.PRIOR
        shapes[name]=[load(p) for p in sorted(source.glob(name+"_*_DESIGN.brep"))]
        samples=[list(v) for e in path.Edges for v in e.discretize(Deflection=.15)]
        preview.append(dict(name=name,centerline=samples))
    # Exact same design envelopes as the construction; rotated bands on two
    # straight X lanes, six distinct anchors, all new wires also checked.
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    for n,e,x,y in M.ANCHORS:
        z=113.5+M.OD/2
        bands=[box([dx-.6,-1.25,103.8,dx+.6,1.25,z+1.2]) for dx in (-5.5,5.5)]
        bands += [box([-6.1,-1.25,z,6.1,1.25,z+1.2]),box([-6.1,-1.25,103.8,6.1,1.25,105]),box([4.5,-2.5,100.1,10.5,2.5,104.1])]
        for s in bands:
            s.rotate(A.Vector(),A.Vector(0,0,1),M.ANCHOR_ROTATIONS.get((n,e),0));s.translate(A.Vector(x,y,0))
        shapes[f"{n}_end{e}_tie"]=bands
    r=SavedShapes();entry=ROOT/"hardware/cad/assembly/RobotCatNarrowRimEars.FCStd";o=r.doc(entry)
    native=M.CAD/"DeckDataBridgesSupported.FCStd"
    for i in range(6):shapes[f"Integral_saddle{i}"]=[r.shape(native,f"DataSaddle{i}")]
    assert r.placement(o["RobotCatAssembly24"]).isIdentity()
    members={x.get("value") for x in prop(o["RobotCatAssembly24"],"Group").findall(".//Link")}
    physical=[prop(o[w],"Group").findall(".//Link")[0].get("value") for w in sorted(members) if w.startswith("Rigid_")]
    retained=[n for n in physical if (n.startswith("Part__Feature") and n!="Part__Feature038") or n in
        {"FrameFront20","FrameRear20","SideLeft22","SideRight22","Belly22","BatteryCarrier23","BatteryLiner23","BatteryStrap123","BatteryStrap223"}
        or n.startswith(("MountFront","MountRear","NutShoe","FrameScrew","FrameNut","BellyScrew","BellyNut","BatteryScrew","BatteryNut"))]
    # R4 tested the unchanged routes/bands against these exact frozen body
    # sources. Repeat only the moved W012/end tie and ALL new saddle solids.
    # The current Deck is still checked against every wire/band; slots cannot
    # borrow clearance from an obsolete uncut Deck cache.
    rows=[x for x in baseline["rows"] if not x["part"].startswith("W012") and x["owner"]!="CURRENT_SUPPORTED_DECK"]
    owner_boxes={};active={k:v for k,v in shapes.items() if k.startswith(("W012","Integral_saddle"))}
    def check(name,s):
        assert s.isValid() and s.Solids,name
        bb=s.BoundBox;owner_boxes[name]=[getattr(bb,k) for k in ("XMin","YMin","ZMin","XMax","YMax","ZMax")]
        candidates={k:v for k,v in shapes.items() if not k.startswith("Integral_saddle")} if name=="CURRENT_SUPPORTED_DECK" else active
        for label,pieces in candidates.items():
            for i,p in enumerate(pieces):
                for j,q in enumerate(s.Solids):
                    if not p.BoundBox.intersect(q.BoundBox):continue
                    rows.append(dict(part=label,segment=i,owner=name,solid=j,hit_mm3=p.common(q).Volume))
    replaced_cache={"hardware/cad/studies/pi-complete-native-r2/Deck_WORLD.brep",
        "hardware/electronics/full-cat/pi-wiring-complete-r13/Deck_DESIGN.brep",
        "hardware/electronics/full-cat/pi-wiring-complete-r13/Carrier_DESIGN.brep",
        "hardware/electronics/full-cat/pi-wiring-complete-r13/PiTray_DESIGN.brep"}
    for path,digest in core["sources"].items():
        assert M.sha(ROOT/path)==digest,path
        if path.endswith(".brep") and path not in replaced_cache:check(path,load(ROOT/path))
    deck=load(M.CAD/"Deck_WORLD.brep");check("CURRENT_SUPPORTED_DECK",deck)
    layout=json.loads((ROOT/"hardware/electronics/power-platform/open-deck-p0/layout.json").read_text(encoding="utf-8"))
    for c in layout["components"]:
        if c["kind"]!="WAGO" or c["id"]=="P_REAR":continue
        x0,y0,x1,y1=c["footprint_xyxy_mm"]
        check(c["id"]+"_design",box([x0+21,y0,109,x1+21,y1,109+c["planning_height_mm"]]))
    check("P_REAR_selected_raised_design",box([10,-18.5,124,32,18.5,135]))
    for i,(label,pieces) in enumerate(shapes.items()):
        for other,parts in list(shapes.items())[i+1:]:
            for j,piece in enumerate(pieces):
                for k,q in enumerate(parts):
                    if piece.BoundBox.intersect(q.BoundBox):rows.append(dict(part=label,segment=j,owner=other,solid=k,hit_mm3=piece.common(q).Volume))
    for i,n in enumerate(retained):
        box_prior=baseline["owner_boxes_mm"][n]
        def broad_overlap(b,p):
            q=p.BoundBox
            return b[0]<=q.XMax and b[3]>=q.XMin and b[1]<=q.YMax and b[4]>=q.YMin and b[2]<=q.ZMax and b[5]>=q.ZMin
        if not any(broad_overlap(box_prior,p) for pieces in active.values() for p in pieces):
            owner_boxes[n]=box_prior;continue
        check(n,world_shape(r,entry,o,n,members))
        if i%25==0:print(f"retained body {i+1}/{len(retained)}",flush=True)
    cooling=world_shape(r,entry,o,"PiHatCooling",members);cooling.translate(A.Vector(0,0,7))
    check("PiHatCooling_selected_rise7mm",cooling)
    supports=ROOT/"hardware/cad/studies/open-deck-p0/r3/OpenDeckSupports.FCStd"
    for i in range(4):check(f"P0Support{i}",r.shape(supports,f"Support{i}"))
    clamps=ROOT/"hardware/cad/studies/pi4-tray-body-mount-r1/PiTrayClampAssembly.FCStd"
    for n in r.doc(clamps):
        if n.startswith(("View_upper_","View_lower_")):check(n,r.shape(clamps,n))
    tail=ROOT/"hardware/cad/studies/tail-local-finish-r2/TailLocalCompleteSupportR2.brep"
    check("Selected_tail_support",load(tail))
    for n,b in {"P_AUX":[.5,57,109,19.5,87,118],"G_TAIL":[.5,-87,109,19.5,-57,118],"G_AUX":[110.5,-84,109,129.5,-54,118]}.items():check(n+"_design",box(b))
    assert all(M.sha(ROOT/p)==h for p,h in r.hashes.items())
    hits=[x for x in rows if x["hit_mm3"]>1e-5]
    result=dict(status="CURRENT_BODY_CLEAR" if not hits else "CURRENT_BODY_REJECTED",hits=hits,rows=rows,
        retained_rest_body_owners=len(retained),owner_boxes_mm=owner_boxes,arc_checks=arc_checks,
        source_sha256={**baseline["source_sha256"],**r.hashes,tail.relative_to(ROOT).as_posix():M.sha(tail)},
        script_sha256=M.sha(Path(__file__)),physical_pass=False,W5_complete=False,
        sourced_T18I_thickness_mm=1.2,replaced_cache_owners=sorted(replaced_cache),
        baseline_reuse=dict(path=baseline_path.relative_to(ROOT).as_posix(),sha256=M.sha(baseline_path),
            reason="Unchanged W007/W011/bands and frozen body sources retained. New W012/end1 tie and all six actual native saddle solids checked; new Deck checked against all wires/bands. Prior W012 collision not reused as a clear row."),
        scope="Three fixed DATA bridges and six ties versus retained saved rest body/legs, current Pi cooling rise/supports/clamps and selected tail support. Not moving leg cables, not whole head motion.",
        replaced_owners="Legacy upperplate/shell/PiTray/BUS/Deck/Carrier/Shelf/PWM/head/audio removed from this pass: current selected owners checked in construction. Speaker is absent by scope, not waived as installed.")
    M.save(M.OUT/"current-body-checks.json",result)
    assert not hits,hits
    import MeshPart
    mesh=MeshPart.meshFromShape(Shape=deck,LinearDeflection=.08,AngularDeflection=.15,Relative=False)
    assert mesh.isSolid() and mesh.countComponents()==1
    bb=mesh.BoundBox;mesh.translate(-bb.XMin,-bb.YMin,-bb.ZMin)
    dims=[mesh.BoundBox.XLength,mesh.BoundBox.YLength,mesh.BoundBox.ZLength]
    assert max(dims)+10<=256
    mesh.write(str(M.CAD/"Deck_x1.stl"))
    core.update(status="THREE_DATA_BRIDGES_NOMINAL_COMPLETE",rows=rows,hits=[],
        checked_overlapping_pairs=len(rows),new_STL=1,closed=True,components=1,
        sourced_T18I_thickness_mm=1.2,dimensions_mm=dims)
    M.save(M.OUT/"checks.json",core)
    interface=json.loads((M.OUT/"interface.json").read_text(encoding="utf-8"))
    interface["restraints"].pop("verified_utc",None)
    interface["restraints"]["manufacturer_verification_date_utc"]="2026-10-01"
    interface.update(new_STL=1,geometry_nominal_clear=True,selected=False,
        lengths=core["lengths"],new_native=core["source_native"])
    M.save(M.OUT/"interface.json",interface)
    vertices,triangles=deck.tessellate(.6)
    M.save(M.OUT/"preview-geometry.json",dict(deck=dict(vertices=[list(v) for v in vertices],triangles=triangles),
        routes=preview,anchors=M.ANCHORS,slots=core["slots"]))
    print(json.dumps(dict(status=result["status"],rest_owners=len(retained),exact_pairs=len(rows),minimum_radius_mm=5.2)),flush=True)

if __name__=="__main__":main()
