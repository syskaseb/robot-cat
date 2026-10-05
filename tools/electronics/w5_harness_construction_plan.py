"""One shared PETG construction scope for the received whole harness.

Map actual common solids, not conservative boxes, before constructing a
combined Deck/Carrier/cover variant. No existing circuit/route is changed.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import w5_received_central_scope as received
import w5_central_shared_routes as scope
from servo_fuse_inputs_r1 import save,sha

ROOT=scope.ROOT;BASE=ROOT/'hardware/electronics/full-cat'
OUT=BASE/'w5-harness-construction-plan-r1'
RECEIPT=BASE/'w5-central-received-joint-r2/received.json'


def bounds(shape):
    return [getattr(shape.BoundBox,k) for k in ('XMin','YMin','ZMin','XMax','YMax','ZMax')]


def main():
    import FreeCAD as A,Part
    from w5_exact_separation import separated
    start=datetime.now(timezone.utc);assert not (OUT/'plan.json').exists()
    fixed,printed,ends,family,rows,pins,reused,replaced=received.load(A,Part)
    receipt=json.loads(RECEIPT.read_text(encoding='utf-8'));assert receipt['complete']
    for rel,digest in receipt['source_sha256'].items():
        assert sha(ROOT/rel)==digest,rel;pins.append(ROOT/rel)
    routes={wire:fixed[wire] for wire in reused}
    for wire,row in receipt['routes'].items():
        p=ROOT/row['geometry'];routes[wire]=Part.read(str(p));pins.append(p)
    assert len(routes)==37
    routes.update({k:fixed[k] for k in ('G1_NEW_BODY','G2_NEW_BODY')})
    hits=[];errors=[];tested=0
    OUT.mkdir(parents=True,exist_ok=True)
    for wire,shape in routes.items():
        for owner,obstacle in printed.items():
            if not shape.BoundBox.intersect(obstacle.BoundBox):continue
            try:
                common=[]
                for a in shape.Solids:
                    for b in obstacle.Solids:
                        if not a.BoundBox.intersect(b.BoundBox):continue
                        tested+=1
                        if separated(a,b):continue
                        x=a.common(b)
                        if x.Volume>1e-6:common.append(x)
                if common:
                    witness=Part.makeCompound(common)
                    hits.append(dict(wire=wire,owner=owner,mm3=sum(x.Volume for x in common),bounds_mm=bounds(witness)))
            except Exception as e:errors.append(dict(wire=wire,owner=owner,error=str(e)))
        print('HARNESS_PETG_SCOPE',wire,len(hits),len(errors),flush=True)
        save(OUT/'progress.json',dict(tested=tested,hits=hits,errors=errors))
    pins += [Path(__file__),RECEIPT,Path(scope.__file__),Path(received.__file__),ROOT/'tools/electronics/w5_exact_separation.py']
    finish=datetime.now(timezone.utc)
    save(OUT/'plan.json',dict(status='ONE_WHOLE_HARNESS_NATIVE_CONSTRUCTION_SCOPE',wire_count=37,
        registered_blocks=['G1_NEW_BODY','G2_NEW_BODY'],changed_material_pairs=tested,
        actual_contacts=hits,errors=errors,printed_owner_bounds={k:bounds(s) for k,s in printed.items()},
        ordered_construction=[
            'Preserve all37 received whole wire shapes and registeredG1/G2 positions.',
            'Rebuild displaced ground-block retention and obsolete W001/W060 insulation restraints.',
            'Create ONE linked editable Deck/Carrier variant resolving the actual material contact map; preserve bankR47 and source interfaces.',
            'Add open insulation seats/through tie slots for changed endpoints and supported flights, qualify bands against all real owners.',
            'Resolve necessary cover passages without duplicating separate print variants.',
            'Verify only changed parts: continuity, tool access, assembly/removal, wire motion and combined stock.',
            'Export/reopen the single chosen native set; select only after W1/W5 evidence is complete.'],
        replacement_obligations=replaced,phase_completed_count=14,phase_total=20,
        W1_complete=False,W5_complete=False,selected=False,physical_pass=False,
        started_utc=start.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-start).total_seconds(),
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)}))
    print('HARNESS_CONSTRUCTION_PLAN_DONE',len(hits),len(errors),flush=True)


if __name__=='__main__':main()
