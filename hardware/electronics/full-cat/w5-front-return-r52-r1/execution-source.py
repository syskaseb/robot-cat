"""One new W036 corridor on installed R52; no old rejected route rerun.

Z128.5/Y80 clears the previously witnessed XB22 crossing and avoids its
middle restraint corridor. Keep endpoints, TKD4mm2/OD4.2/R21 unchanged.
Only W036 changed geometry is checked against installed owners. This is a
construction preflight, not selection or complete W5.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/electronics"))
sys.path.insert(0, str(ROOT / "tools/cad"))
from servo_fuse_inputs_r1 import sha, save


def main():
    import FreeCAD as A
    import Part
    from w5_selected_owners_r52 import cached
    import body_ground_routes_r1 as geometry
    from xb11_upstream_route import rounded
    start = datetime.now(timezone.utc)
    out = ROOT / "hardware/electronics/full-cat/w5-front-return-r52-r1"
    out.mkdir(parents=True, exist_ok=True)
    assert not (out / "checks.json").exists()
    geometry.R = 21; geometry.STRAIGHT = 2
    a, b = [73.5, 11, 113.5], [-46.5, -30.5, 113.5]
    height, lane = 128.5, 80
    intent = dict(wire="W036", endpoints={"G1.4": a, "FR_G.1": b},
                  material="TKD2500125", diameter_mm=4.2, radius_mm=21,
                  corridor_height_mm=height, corridor_y_mm=lane,
                  selected=False, physical_pass=False, W5_complete=False,
                  parent_selection="one-batch-prototype-r52",
                  reason="New whole corridor above witnessed XB22 intersections; no R5 seat reuse",
                  next="After clear complete path, add endpoint and middle restraints on current Deck, then native/export/selection")
    save(out / "intent.json", intent)
    ea, pa = geometry.elevated_start(a, 1, height)
    eb, pb = geometry.elevated_start(b, 1, height)
    middle = rounded([pa, A.Vector(pa.x, lane, height), A.Vector(pb.x, lane, height), pb], 21)
    back = []
    for e in reversed(eb):
        p, q = e.valueAt(e.LastParameter), e.valueAt(e.FirstParameter)
        back.append(Part.Arc(p, e.valueAt((e.FirstParameter+e.LastParameter)/2), q).toShape()
                    if hasattr(e.Curve, "Radius") else Part.makeLine(p, q))
    route = Part.Wire(ea + middle.Edges + back)
    assert route.isValid()
    assert all((p.valueAt(p.LastParameter)-q.valueAt(q.FirstParameter)).Length < 1e-7
               and (p.tangentAt(p.LastParameter)-q.tangentAt(q.FirstParameter)).Length < 1e-7
               for p, q in zip(route.Edges, route.Edges[1:]))
    assert min(e.Curve.Radius for e in route.Edges if hasattr(e.Curve, "Radius")) >= 21-1e-7
    pieces = [Part.Wire([e]).makePipeShell([Part.Wire([Part.makeCircle(
        2.1, e.valueAt(e.FirstParameter), e.tangentAt(e.FirstParameter))])], True, False)
        for e in route.Edges]
    assert all(s.isValid() and len(s.Solids) == 1 for s in pieces)
    Part.makeCompound(pieces).exportBrep(str(out / "W036_DESIGN.brep"))
    route.exportBrep(str(out / "W036_CENTERLINE.brep"))
    owners, receipt = cached()
    hits, errors, pairs = [], [], 0
    for i, s in enumerate(pieces):
        for key, owner in owners.items():
            if not s.BoundBox.intersect(owner.BoundBox):
                continue
            for j, solid in enumerate(owner.Solids):
                if not s.BoundBox.intersect(solid.BoundBox):
                    continue
                pairs += 1
                try:
                    witness = s.common(solid)
                    if witness.Volume > 1e-5:
                        hits.append(dict(segment=i, owner=key, owner_solid=j,
                                         mm3=witness.Volume,
                                         bounds_mm=[getattr(witness.BoundBox, n) for n in
                                                    ("XMin", "YMin", "ZMin", "XMax", "YMax", "ZMax")]))
                except Exception as exc:
                    errors.append(dict(segment=i, owner=key, error=str(exc)))
        print("W036_SEGMENT", i, "hits", len(hits), "errors", len(errors), flush=True)
    end = datetime.now(timezone.utc)
    save(out / "checks.json", dict(status="NEW_W036_CORRIDOR_CONFLICTS" if hits or errors else "NEW_W036_CORRIDOR_CLEAR_RESTRAINTS_PENDING",
        hits=hits, errors=errors, pairs=pairs, route_length_mm=route.Length,
        nominal_blank_mm=math.ceil((route.Length+58)/10)*10,
        source_sha256={"hardware/electronics/full-cat/w5-installed-r52/owners.json": sha(ROOT / "hardware/electronics/full-cat/w5-installed-r52/owners.json"),
                       "hardware/electronics/full-cat/w5-installed-r52/installed.brep": receipt["geometry_sha256"],
                       Path(__file__).relative_to(ROOT).as_posix(): sha(Path(__file__))},
        worker_started_utc=start.isoformat(), worker_finished_utc=end.isoformat(),
        worker_wall_seconds=(end-start).total_seconds(),
        selected=False, restraints_complete=False, W5_complete=False, physical_pass=False))
    print(json.dumps(dict(hits=len(hits), errors=len(errors), pairs=pairs, length_mm=route.Length)), flush=True)


if __name__ == "__main__":
    main()
