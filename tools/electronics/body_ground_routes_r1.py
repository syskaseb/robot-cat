"""Five stationary ground returns, sourced TKD R21 and selected R37 body.

Save complete intent before geometry. Cage centres are explicit prototype
datums, not measured housing dimensions. One potential per WAGO; physical
cages can be labelled without changing electrical roles. Never power hardware.
"""
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "hardware/electronics/full-cat/body-ground-routes-r1"
R = 21.0
OD = 4.2
STRAIGHT = 3.5
# Endpoints are outside the two entry faces, not a route through a WAGO.
# G1 physical +X labels [.5,.2,.3,.4,.1]; keep existing Pi cage .2.
# FR_G/RR_G physical +X labels [.2,.1,.3,.4,.5]; others unchanged.
SPECS = {
    "W025": ("G1.3", [66,-11,113.5], -1, "FL_G.1", [-46.5,30.5,113.5], -1, 129.5, -79),
    "W036": ("G1.4", [73.5,11,113.5], 1, "FR_G.1", [-39.75,-30.5,113.5], 1, 129.5, 79),
    "W061": ("G1.5", [51,-11,113.5], -1, "G2.1", [97.5,-9.5,113.5], -1, 123.5, -65),
    "W062": ("G2.2", [104.25,-9.5,113.5], -1, "RL_G.1", [61.5,30.5,113.5], -1, 135.5, -82),
    "W063": ("G2.3", [111,9.5,113.5], 1, "RR_G.1", [68.25,-30.5,113.5], 1, 135.5, 82),
}

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8", newline="\n")

def elevated_start(point, direction, height):
    """Two opposing R21 arcs lift a straight Y lead without a sharp corner."""
    import FreeCAD as A
    import Part
    start = A.Vector(*point)
    first = start + A.Vector(0, direction*STRAIGHT, 0)
    rise = height-start.z
    assert 0 < rise < 2*R
    angle = math.acos(1-rise/(2*R))
    run = 2*R*math.sin(angle)
    def p(t):
        if t <= angle:
            return first + A.Vector(0, direction*R*math.sin(t), R*(1-math.cos(t)))
        q = t-angle
        y = R*math.sin(angle) + R*(math.sin(angle)-math.sin(angle-q))
        z = R*(1-math.cos(angle)) + R*(math.cos(angle-q)-math.cos(angle))
        return first + A.Vector(0, direction*y, z)
    edges = [Part.makeLine(start,first), Part.Arc(p(0),p(angle/2),p(angle)).toShape(),
             Part.Arc(p(angle),p(1.5*angle),p(2*angle)).toShape()]
    end = first+A.Vector(0,direction*run,rise)
    assert (p(2*angle)-end).Length < 1e-8
    return edges,end

def route(spec):
    import FreeCAD as A
    import Part
    from xb11_upstream_route import rounded
    _,a,da,_,b,db,z,lane=spec
    assert da==db and abs(a[0]-b[0])>=2*R
    ea,pa=elevated_start(a,da,z)
    eb,pb=elevated_start(b,db,z)
    middle=rounded([pa,A.Vector(pa.x,lane,z),A.Vector(pb.x,lane,z),pb],R)
    reverse=[]
    for e in reversed(eb):
        end=e.valueAt(e.LastParameter);start=e.valueAt(e.FirstParameter)
        if hasattr(e.Curve,"Radius"):
            reverse.append(Part.Arc(end,e.valueAt((e.FirstParameter+e.LastParameter)/2),start).toShape())
        else:
            reverse.append(Part.makeLine(end,start))
    wire=Part.Wire(ea+middle.Edges+reverse)
    assert wire.isValid()
    for p,q in zip(wire.Edges,wire.Edges[1:]):
        assert (p.valueAt(p.LastParameter)-q.valueAt(q.FirstParameter)).Length<1e-7
        assert (p.tangentAt(p.LastParameter)-q.tangentAt(q.FirstParameter)).Length<1e-7
    radii=[e.Curve.Radius for e in wire.Edges if hasattr(e.Curve,"Radius")]
    assert min(radii)>=R-1e-7
    return wire

def body_owners():
    """Reuse pinned current owners; no recompute of the full legacy robot."""
    import FreeCAD as A
    import Part
    from check_main_p0_placement import SavedShapes,prop
    from check_p0_leg_geometry import world_shape
    baseline=ROOT/"hardware/electronics/full-cat/body-data-bridges-r7/current-body-checks.json"
    meta=json.loads(baseline.read_text(encoding="utf-8"))
    core=json.loads((baseline.parent/"checks.json").read_text(encoding="utf-8"))
    owners={};hashes={baseline.relative_to(ROOT).as_posix():sha(baseline)}
    def load(rel):
        p=ROOT/rel;hashes[rel]=sha(p);s=Part.Shape();s.read(str(p));return s
    replaced=set(meta["replaced_cache_owners"])
    for rel,h in {**core["sources"],**meta["source_sha256"]}.items():
        assert sha(ROOT/rel)==h,rel
        hashes[rel]=h
        if rel.endswith(".brep") and rel not in replaced:owners[rel]=load(rel)
    owners["Deck_R37"]=load("hardware/cad/studies/body-data-bridges-r7/Deck_WORLD.brep")
    for n in ("W007","W011","W012"):
        for p in sorted((ROOT/"hardware/electronics/full-cat/body-data-bridges-r3").glob(n+"_*_DESIGN.brep")):
            owners["DATA/"+p.stem]=load(p.relative_to(ROOT).as_posix())
    def box(b):
        return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
    for n,b in meta["owner_boxes_mm"].items():
        if n.endswith("_design") or n.endswith("_raised_design"):
            owners[n]=box(b)
    r=SavedShapes();entry=ROOT/"hardware/cad/assembly/RobotCatNarrowRimEars.FCStd";obj=r.doc(entry)
    members={x.get("value") for x in prop(obj["RobotCatAssembly24"],"Group").findall(".//Link")}
    retained=[n for n in meta["owner_boxes_mm"] if n in obj and (n.startswith("Part__Feature") or n.startswith(("Frame","Side","Belly","Battery","Mount","NutShoe")))]
    for n in retained:owners[n]=world_shape(r,entry,obj,n,members)
    cooling=world_shape(r,entry,obj,"PiHatCooling",members);cooling.translate(A.Vector(0,0,7));owners["PiHatCooling_rise7"]=cooling
    supports=ROOT/"hardware/cad/studies/open-deck-p0/r3/OpenDeckSupports.FCStd"
    for i in range(4):owners[f"P0Support{i}"]=r.shape(supports,f"Support{i}")
    clamps=ROOT/"hardware/cad/studies/pi4-tray-body-mount-r1/PiTrayClampAssembly.FCStd"
    for n in r.doc(clamps):
        if n.startswith(("View_upper_","View_lower_")):owners[n]=r.shape(clamps,n)
    owners["Selected_tail_support"]=load("hardware/cad/studies/tail-local-finish-r2/TailLocalCompleteSupportR2.brep")
    # Include selected DATA restraint envelopes, not just the conductors.
    import body_data_bridges_r7 as D
    for n,end,x,y in D.M.ANCHORS:
        z=113.5+D.M.OD/2
        bands=[box([dx-.6,-1.25,103.8,dx+.6,1.25,z+1.2]) for dx in (-5.5,5.5)]
        bands += [box([-6.1,-1.25,z,6.1,1.25,z+1.2]),box([-6.1,-1.25,103.8,6.1,1.25,105]),box([4.5,-2.5,100.1,10.5,2.5,104.1])]
        for i,s in enumerate(bands):
            s.rotate(A.Vector(),A.Vector(0,0,1),D.M.ANCHOR_ROTATIONS.get((n,end),0));s.translate(A.Vector(x,y,0))
            owners[f"DATA_tie/{n}/{end}/{i}"]=s
    hashes.update(r.hashes)
    return owners,hashes

def main():
    import FreeCAD as A
    import Part
    sys.path.insert(0,str(ROOT/"tools/cad"))
    OUT.mkdir(parents=True,exist_ok=True)
    assert not (OUT/"checks.json").exists(),"Preserve trials; use a new revision"
    started=datetime.now(timezone.utc)
    save(OUT/"intent.json",dict(parent="one-batch-prototype-r37",specs=SPECS,
        sourced_static_radius_mm=R,wire_OD_mm=OD,wire_SKU="TKD2500125",
        straight_insulated_exit_mm=STRAIGHT,prototype_entry_height_mm=4.5,
        prototype_615_cage_pitch_mm=7.5,prototype_415_pitch_mm=6.75,
        cage_labels={"G1":[".5",".2",".3",".4",".1"],"FR_G":[".2",".1",".3",".4",".5"],"RR_G":[".2",".1",".3",".4",".5"]},
        remap_rule="Electrical graph unchanged: all cages in each WAGO are a single potential. Pi G1.2 retained; not a delivered port measurement.",
        physical_pass=False,selected=False,restraints_complete=False,W5_complete=False,
        source="POWER-WIRE-P0.md exact TKD2500125 4mm2: OD4.2; stationary R5xOD=21. Manufacturer PDF cached.",
        started_utc=started.isoformat()))
    paths={};pieces={};lengths={};preview=[]
    for n,spec in SPECS.items():
        w=route(spec);paths[n]=w;pieces[n]=[]
        for i,e in enumerate(w.Edges):
            section=Part.Wire([Part.makeCircle(OD/2,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])
            s=Part.Wire([e]).makePipeShell([section],True,False)
            assert s.isValid() and len(s.Solids)==1
            pieces[n].append(s);s.exportBrep(str(OUT/f"{n}_{i}_DESIGN.brep"))
            e.exportBrep(str(OUT/f"{n}_{i}_CENTERLINE.brep"))
        lengths[n]=dict(external_length_mm=w.Length,nominal_strip_each_mm=14,
            trim_and_rework_mm=30,provisional_blank_mm=math.ceil((w.Length+58)/10)*10,
            actual_strip="Read delivered housing; never tin WAGO wire ends")
        preview.append(dict(name=n,points=[list(p) for e in w.Edges for p in e.discretize(Deflection=.2)]))
    save(OUT/"lengths.json",lengths)
    owners,hashes=body_owners();rows=[]
    for n,parts in pieces.items():
        for owner,s in owners.items():
            for i,p in enumerate(parts):
                for j,q in enumerate(s.Solids):
                    if not p.BoundBox.intersect(q.BoundBox):continue
                    v=p.common(q).Volume
                    rows.append(dict(wire=n,segment=i,owner=owner,solid=j,intersection_mm3=v))
        print(n+" checked against current body",flush=True)
    for n,parts in pieces.items():
        for other,qq in pieces.items():
            if n>=other:continue
            for i,p in enumerate(parts):
                for j,q in enumerate(qq):
                    if p.BoundBox.intersect(q.BoundBox):rows.append(dict(wire=n,segment=i,owner=other,solid=j,intersection_mm3=p.common(q).Volume))
    hits=[r for r in rows if r["intersection_mm3"]>1e-5]
    ended=datetime.now(timezone.utc)
    save(OUT/"checks.json",dict(status="GROUND_ROUTES_REJECTED" if hits else "GROUND_ROUTES_CLEAR_NEED_RESTRAINTS",
        hits=hits,rows=rows,lengths=lengths,source_sha256=hashes,script_sha256=sha(Path(__file__)),
        physical_pass=False,selected=False,W5_complete=False,
        started_utc=started.isoformat(),finished_utc=ended.isoformat(),worker_wall_seconds=(ended-started).total_seconds()))
    save(OUT/"preview-lines.json",preview)
    print(json.dumps(dict(hits=hits,pairs=len(rows),status="REJECTED" if hits else "CLEAR")),flush=True)

if __name__=="__main__":main()
