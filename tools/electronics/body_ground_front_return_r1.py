"""W036 on selected R38; check real changed interfaces before native seats.

One-sided WAGO entries, sourced TKD R21. No change to pinned R38 helpers.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import body_ground_routes_r1 as M

ROOT = M.ROOT
OUT = ROOT / "hardware/electronics/full-cat/body-ground-front-return-r1"
SPEC = ("G1.4", [73.5, 11, 113.5], 1, "FR_G.1", [-33, -30.5, 113.5], 1, 128, 88)

def current_owners():
    import FreeCAD as A
    import Part
    sys.path.insert(0, str(ROOT / "tools/cad"))
    owners, hashes = M.body_owners()
    owners.pop("Deck_R37")
    def load(rel):
        p = ROOT / rel
        hashes[rel] = M.sha(p)
        s = Part.Shape(); s.read(str(p))
        return s
    def box(b):
        return Part.makeBox(b[3]-b[0], b[4]-b[1], b[5]-b[2], A.Vector(*b[:3]))
    owners["Deck_R38"] = load("hardware/cad/studies/body-ground-bridge-finish-r5/Deck_WORLD.brep")
    for p in sorted((ROOT / "hardware/electronics/full-cat/body-ground-bridge-r5").glob("W061_*_DESIGN.brep")):
        owners[p.stem] = load(p.relative_to(ROOT).as_posix())
    interface = json.loads((ROOT / "hardware/electronics/full-cat/body-ground-bridge-finish-r5/interface.json").read_text(encoding="utf-8"))
    for a in interface["anchors"]:
        turn = a["rotation"]; z = a["z"]; upper = z+2.2
        bottom = 130.8 if turn else 103.8
        head = 127.1 if turn else 100.1
        bands = [box([dx-.6,-1.25,bottom,dx+.6,1.25,upper+1.2]) for dx in (-5.5,5.5)]
        bands += [box([-6.1,-1.25,upper,6.1,1.25,upper+1.2]), box([-6.1,-1.25,bottom,6.1,1.25,bottom+1.2]), box([4.5,-2.5,head,10.5,2.5,head+4])]
        for i,s in enumerate(bands):
            s.rotate(A.Vector(),A.Vector(0,0,1),turn); s.translate(A.Vector(a["x"],a["y"],0))
            owners[f"W061_tie/{a['id']}/{i}"] = s
    layout = json.loads((ROOT / "hardware/electronics/power-platform/open-deck-p0/layout.json").read_text(encoding="utf-8"))
    for c in layout["components"]:
        if c["kind"] != "servo_fuse": continue
        x,y = c["center_xy_mm"]; x += 21
        owners[c["id"]+"_MTA_conservative_housing"] = box([x-7.75,y-14.25,82.5,x+7.75,y+14.25,111])
        owners[c["id"]+"_287_entire_height"] = box([x-2.55,y-9.55,111,x+2.55,y+9.55,129.8])
    owners["F_AUX_conservative_case"] = box([51,11.6,122,72.2,23.6,142])
    owners["F_PWM_conservative_case"] = box([67.5,-17.91,127.49,75.9,-14.89,130.51])
    return owners, hashes

def main():
    import FreeCAD as A
    import Part
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT / "checks.json").exists(), "Preserve failed trial"
    start = datetime.now(timezone.utc)
    M.save(OUT / "intent.json", dict(parent="one-batch-prototype-r38",wire="W036",spec=SPEC,
        wire_SKU="TKD2500125",OD_mm=4.2,static_radius_mm=21,
        prototype_FR_G_cage_pitch_mm=6.75,FR_G_positive_X_labels=[".2",".3",".1",".4",".5"],
        remap="FR_G ground-only cage .1 moves to centre X-33; one entry face +Y-30.5. Other still-open returns must adopt these datums.",
        strip_by_end_mm={"G1.4":[12,14],"FR_G.1":11},physical_pass=False,selected=False,W5_complete=False,
        started_utc=start.isoformat()))
    M.STRAIGHT = 2.0
    wire = M.route(SPEC)
    pieces = []
    for i,e in enumerate(wire.Edges):
        section = Part.Wire([Part.makeCircle(M.OD/2,e.valueAt(e.FirstParameter),e.tangentAt(e.FirstParameter))])
        s = Part.Wire([e]).makePipeShell([section],True,False)
        assert s.isValid() and len(s.Solids)==1
        s.exportBrep(str(OUT/f"W036_{i}_DESIGN.brep")); e.exportBrep(str(OUT/f"W036_{i}_CENTERLINE.brep"))
        pieces.append(s)
    owners, hashes = current_owners()
    rows=[]
    for i,p in enumerate(pieces):
        for name,s in owners.items():
            for j,q in enumerate(s.Solids):
                if p.BoundBox.intersect(q.BoundBox):
                    rows.append(dict(segment=i,owner=name,solid=j,hit_mm3=p.common(q).Volume))
    hits=[r for r in rows if r["hit_mm3"]>1e-5]
    end=datetime.now(timezone.utc)
    M.save(OUT/"checks.json",dict(status="REJECTED" if hits else "ROUTE_CLEAR_NEEDS_RESTRAINTS",hits=hits,rows=rows,
        source_sha256=hashes,script_sha256=M.sha(Path(__file__)),external_length_mm=wire.Length,
        provisional_blank_mm=__import__("math").ceil((wire.Length+58)/10)*10,
        physical_pass=False,selected=False,W5_complete=False,
        started_utc=start.isoformat(),finished_utc=end.isoformat(),worker_wall_seconds=(end-start).total_seconds()))
    M.save(OUT/"preview-lines.json",[dict(name="W036",points=[list(p) for e in wire.Edges for p in e.discretize(Deflection=.2)])])
    print(json.dumps(dict(status="REJECTED" if hits else "CLEAR",hits=hits,pairs=len(rows))),flush=True)

if __name__=="__main__": main()
