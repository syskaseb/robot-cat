"""Reject a changed middle seat before expensive full-history recompute."""
import json
from pathlib import Path
import body_ground_routes_r1 as M
ROOT=M.ROOT
OUT=ROOT/"hardware/electronics/full-cat/body-ground-bridge-finish-r5"
ROUTE=ROOT/"hardware/electronics/full-cat/body-ground-bridge-r5"
def main():
    import FreeCAD as A
    import Part
    def box(x,y,z,w,h,t):return Part.makeBox(w,h,t,A.Vector(x,y,z))
    post=box(78,58,108.8,4,4,29.4)
    beam=box(78,60,132,12,22.5,6.2)
    for y in (69.5,80.5):beam=beam.cut(box(82.4,y-1,131.9,3.2,2,6.4))
    groove=Part.makeCylinder(2.3,12.2,A.Vector(77.9,75,136.5),A.Vector(1,0,0))
    seat=post.fuse(beam).cut(groove)
    assert seat.isValid() and len(seat.Solids)==1 and not seat.check(True)
    rows=[]
    for p in ROUTE.glob("W061_*_DESIGN.brep"):
        s=Part.Shape();s.read(str(p))
        if s.BoundBox.intersect(seat.BoundBox):rows.append(dict(wire=p.stem,hit_mm3=s.common(seat).Volume))
    assert not [r for r in rows if r["hit_mm3"]>1e-5],rows
    OUT.mkdir(exist_ok=True)
    M.save(OUT/"seat-preflight.json",dict(rows=rows,hits=[],minimum_groove_floor_mm=2.2,
        seat_volume_mm3=seat.Volume,source_script_sha256=M.sha(Path(__file__)),physical_pass=False,
        scope="Changed middle seat/route before full native build, not the full current-body check"))
    print(json.dumps(dict(status="MIDDLE_SEAT_ROUTE_CLEAR",pairs=len(rows))),flush=True)
if __name__=="__main__":main()
