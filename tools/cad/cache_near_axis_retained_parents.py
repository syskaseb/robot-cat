"""Persist proven retained geometry once, independently of source candidates."""
import json,time
import check_near_axis_hip_sources as C

if __name__=='__main__':
    tick=time.monotonic();targets,_,_=C.load()
    family=json.loads((C.P.OUT/'leg-source-near-member-plan.json').read_text())
    roots=json.loads((C.P.OUT/'remaining-loom-roots-plan.json').read_text())
    shapes,receipts,files=C.retained_hip_parents(targets,family,roots)
    print(json.dumps(dict(retained=len(shapes),receipts=receipts,worker_seconds=round(time.monotonic()-tick,3))),flush=True)
