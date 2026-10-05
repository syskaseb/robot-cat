"""Receive the already computed/saved native set without repeating cuts.

The builder stopped while formatting a successful check(True) returning
None. Cached results are inspected, not recomputed and not selected.
"""
from pathlib import Path
from datetime import datetime,timezone
import json
import w5_harness_passages_native as N
from servo_fuse_inputs_r1 import sha,save


def main():
    import FreeCAD as A
    begin=datetime.now(timezone.utc)
    target=N.CAD/'WholeHarnessPassages.FCStd';assert target.exists()
    assert not (N.OUT/'checks.json').exists()
    plan=json.loads(N.PLAN.read_text(encoding='utf-8'))
    affected={N.root_owner(h['owner']) for h in plan['actual_contacts']}
    d=A.openDocument(str(target));rows=[];files=[target];pins=[Path(__file__),Path(N.__file__),N.PLAN,N.CENTRAL]
    for owner in sorted(affected):
        final=d.getObject(owner+'HarnessFinished');assert final is not None
        shape=final.Shape;errors=[]
        valid=not shape.isNull() and shape.isValid()
        if valid:
            try:shape.check(True)
            except Exception as e:errors.append(str(e))
        else:errors.append('Null/invalid saved native result')
        original=d.getObject(owner+'ReceivedPart').Shape
        row=dict(owner=owner,valid=valid,solids=len(shape.Solids),BOP_errors=errors,
            original_mm3=original.Volume,remaining_mm3=shape.Volume,
            dimensions_mm=[shape.BoundBox.XLength,shape.BoundBox.YLength,shape.BoundBox.ZLength])
        rows.append(row)
        p=N.CAD/(owner+'_CANDIDATE_WORLD.brep');shape.exportBrep(str(p));files.append(p)
        print('RECEIVED_NATIVE_PASSAGE',owner,valid,len(shape.Solids),len(errors),flush=True)
    pins += [Path(q.FileName) for q in A.listDocuments().values() if q.FileName and Path(q.FileName)!=target]
    finish=datetime.now(timezone.utc)
    save(N.OUT/'checks.json',dict(status='SAVED_NATIVE_PASSAGES_RECEIVED',parts=rows,
        geometry_valid=all(r['valid'] and r['solids']==1 and not r['BOP_errors'] for r in rows),
        inherited_builder_exception='Formatting check(True) None result; CAD saved after recompute, no repeated booleans.',
        received_without_recompute=True,radial_allowance_mm=.4,parameter_probe_pending=True,
        wall_continuity_review_pending=True,registered_block_retention_pending=True,
        restraints_complete=False,closed_STL=False,relocated_reopen=False,
        selected=False,W1_complete=False,W5_complete=False,physical_pass=False,
        started_utc=begin.isoformat(),finished_utc=finish.isoformat(),worker_wall_seconds=(finish-begin).total_seconds(),
        source_sha256={p.relative_to(N.ROOT).as_posix():sha(p) for p in dict.fromkeys(pins)},
        files={p.relative_to(N.ROOT).as_posix():sha(p) for p in files}))


if __name__=='__main__':main()
