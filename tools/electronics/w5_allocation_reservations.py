"""Resolve the joint planning contract against cached material geometry.

No new routing or selection. Proposed block bounding boxes are conservative
envelopes, so contacts mean occupied reserved space, not final body collision.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
from servo_fuse_inputs_r1 import save, sha

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'hardware/electronics/full-cat/w5-space-plan-inputs-r1'

def main():
    import FreeCAD as A, Part
    from w5_ground_entries_r1 import owners, RECEIVED
    started = datetime.now(timezone.utc)
    target = OUT / 'reservations.json'
    assert not target.exists(), 'Preserve received evidence'
    contract_path = OUT / 'allocation.json'
    contract = json.loads(contract_path.read_text(encoding='utf-8'))
    installed, pins = owners(A, Part, json.loads(RECEIVED.read_text(encoding='utf-8')))
    fanouts = ROOT / 'hardware/electronics/full-cat/w5-leg-joint-source-layout-r1'
    receipt = json.loads((fanouts / 'checks.json').read_text(encoding='utf-8'))
    shapes = Part.read(str(fanouts / 'FANOUTS_WORLD.brep')).childShapes()
    assert len(shapes) == len(receipt['routes']) == 36
    coupled = []
    for row, shape in zip(receipt['routes'], shapes):
        bb = shape.BoundBox
        coupled.append(dict(wire=row['wire'], role=row['role'],
            bounds_mm=[getattr(bb,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')],
            selected=False))
        if row['role']=='D': installed['ReceivedD/'+row['wire']]=shape
    result=[]
    for row in contract['bounds_reservations_to_review']:
        b=contract['planned_bodies_mm'][row['block']]
        envelope=Part.makeBox(b[3]-b[0],b[4]-b[1],b[5]-b[2],A.Vector(*b[:3]))
        obstacle=installed[row['owner']]
        try:
            common=envelope.common(obstacle)
            bb=common.BoundBox
            volume=common.Volume
            hit=dict(block=row['block'],owner=row['owner'], common_mm3=volume,
                occupied_reservation=volume>1e-7,
                occupied_bounds_mm=[getattr(bb,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')] if volume>1e-7 else None)
        except Exception as exc:
            hit=dict(block=row['block'],owner=row['owner'],error=str(exc))
        result.append(hit)
        print('RESERVATION',hit,flush=True)
    pins.extend((contract_path, Path(__file__), fanouts/'checks.json',fanouts/'FANOUTS_WORLD.brep'))
    finished=datetime.now(timezone.utc)
    save(target,dict(status='PLANNING_RESERVATIONS_NOT_FINAL_BODY_PASS',
        rows=result, coupled_leg_conductors=coupled, candidate_leg_count=12,
        role_counts={r:sum(x['role']==r for x in coupled) for r in ('D','V','G')},
        occupied_count=sum(x.get('occupied_reservation',False) for x in result),
        errors=[x for x in result if 'error' in x],
        selected=False, W5_complete=False, physical_pass=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        started_utc=started.isoformat(),finished_utc=finished.isoformat(),
        worker_wall_seconds=(finished-started).total_seconds()))
    print('PLANNING_RESERVATIONS_COMPLETE',flush=True)

if __name__=='__main__': main()
