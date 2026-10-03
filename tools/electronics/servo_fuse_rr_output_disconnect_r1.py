"""One outward-facing RR output disconnect corridor, before bank removal.

Keep the two same-face wire ports and all routes. Install the rolled 221-412
with its levers facing negative Y (outside), not toward the other wiring.
Pivot/radius/open angle are explicit prototype allowances, NOT manufacturer
hinge dimensions. Physical fit/tool action remains a phase2 trial.
Only three RR output ties are removed before using these two cages.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, math, sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/electronics'))
from servo_fuse_inputs_r1 import sha,save
OUT=ROOT/'hardware/electronics/full-cat/servo-fuse-rr-output-disconnect-r1'

def main():
    import FreeCAD as A
    import Part
    start=datetime.now(timezone.utc)
    # Reuse exactly the current four-parent owner loader, not an old Deck.
    source=ROOT/'tools/electronics/servo_fuse_rr_clip_approach_r1.py'
    code=source.read_text(encoding='utf-8')
    code=code[:code.index('    # These boxes are exactly')]
    code=code.replace('servo-fuse-rr-clip-approach-r1','servo-fuse-rr-output-disconnect-r1')
    code+='    return owners,pins,final\n'
    ns=dict(__file__=str(source),__name__='owner_loader_only')
    exec(compile(code,str(source),'exec'),ns)
    owners,pins,native=ns['main']()
    pins[source.relative_to(ROOT).as_posix()]=sha(source)
    V=A.Vector
    def box(b):return Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],V(*b[:3]))
    def bounds(s):return [getattr(s.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]
    removed=[]
    for key in list(owners):
        if key.startswith('CurrentRear/RR'):
            removed.append(key);del owners[key]
    assert len(removed)==15,removed # three bands of four faces plus their heads
    body=owners['W053/221412'];bb=body.BoundBox
    assert abs(bb.XMin+67.3)<1e-7 and abs(bb.YMin+95)<1e-7
    assumptions=dict(lever_face='negativeY/outside; assign factory upper and extension lower by project slot, not moulded numbering',
        pivot_X_from_back_mm=4,pivot_Y=bb.YMin,sector_radius_mm=14,
        width_per_lever_mm=5,opening_degrees=110,blade_thickness_mm=1,blade_width_mm=5,
        basis='PROJECT prototype clearance allowances only; no measured hinge or physical action')
    probes=[]
    for z in (115,121.5):
        pivot=V(bb.XMin+4,bb.YMin,z-2.5)
        def point(deg):
            t=math.radians(deg);return pivot+V(14*math.cos(t),-14*math.sin(t),0)
        a,m,b=point(0),point(55),point(110)
        face=Part.Face(Part.Wire([Part.makeLine(pivot,a),Part.Arc(a,m,b).toShape(),Part.makeLine(b,pivot)]))
        sector=face.extrude(V(0,0,5))
        # A flat1x5 blade reaches the free tip from the outside. Full blade
        # shank remains outside the body, not a guessed finger envelope.
        blade=box([bb.XMin+17.5,-120,z-2.5,bb.XMin+18.5,bb.YMin,z+2.5])
        for name,s in [('lever',sector),('blade',blade)]:
            assert s.isValid() and len(s.Solids)==1
            label=f'RR_{z:g}_{name}';s.exportBrep(str(OUT/(label+'.brep')))
            probes.append((label,s))
    hits=[];errors=[];pairs=0
    for label,s in probes:
        for key,t in owners.items():
            if key=='W053/221412':continue # only the intentional own hinge/body
            if not s.BoundBox.intersect(t.BoundBox):continue
            pairs+=1
            try:
                c=s.common(t)
                if c.Volume>1e-5:
                    hits.append(dict(probe=label,owner=key,mm3=c.Volume,bounds_mm=bounds(c)))
                    c.exportBrep(str(OUT/f'HIT_{len(hits)}.brep'))
            except Exception as e:errors.append(dict(probe=label,owner=key,error=str(e)))
        print('RR_OUTPUT_DISCONNECT',label,flush=True)
    save(OUT/'checks.json',dict(status='PROJECT_RR_LEVER_CORRIDOR_CONFLICTS' if hits or errors else 'PROJECT_RR_LEVER_CORRIDOR_CLEAR_PHASE2_ACTION',
        selected=False,physical_pass=False,W5_complete=False,fixture_change=False,
        assumptions=assumptions,removed_strap_shapes=removed,removed_installed_ties=3,
        sequence='Battery absent, cut/release three RR output ties, open two outward-facing cages, withdraw wires along their actual X entry axes. Parking/bank lift is separate.',
        probes=[dict(id=n,bounds_mm=bounds(s)) for n,s in probes],hits=hits,errors=errors,pairs=pairs,
        actual_manufacturer_lever_motion_qualified=False,wire_withdrawal_qualified=False,
        source_sha256=pins,script_sha256=sha(Path(__file__)),started_utc=start.isoformat(),
        finished_utc=datetime.now(timezone.utc).isoformat(),worker_wall_seconds=(datetime.now(timezone.utc)-start).total_seconds()))
    print(json.dumps(dict(pairs=pairs,hits=hits,errors=errors)),flush=True)

if __name__=='__main__':main()
