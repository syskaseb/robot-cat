"""One exact batch for all named shared-breakout preflight rejections."""
import json
import time
from pathlib import Path
import current_body_fanout_material as M

P=M.P


def run():
    tick=time.monotonic();f=P.OUT/'body-fanout-radial-sources.json';lf=P.OUT/'body-fanout-layout.json'
    plan=json.loads(f.read_text());layout=json.loads(lf.read_text())
    targets,old,pins=M.load()
    new={'new/'+n:(P.wire(r['parts']),1) for n,r in layout['routes'].items()}
    new.update({'new/'+r['wire']+'/source':(P.wire(r['parts']),1) for r in plan['rows']})
    report=[]
    for r in plan['rejected']:
        block=r['blocker'];target=block['name'];curve=P.wire(r['parts'][1:])
        if block['kind']=='surface_reservation':other=targets[target];radius=0
        else:other,radius=({**old,**new})[target]
        assert curve.isValid() and other.isValid(),target
        gap=curve.copy().distToShape(other.copy())[0];required=radius+1.25
        report.append(dict(wire=r['wire'],loom=r['loom'],target=target,parts=r['parts'][1:],
            gap_mm=gap,required_project_mm=required,violates_project_clearance=gap<required-1e-6))
    result=dict(status='EXACT_SOURCE_BREAKOUT_WITNESSES_NO_LAYOUT_ACCEPTANCE',rows=report,
        source_sha256={**pins,**{p.relative_to(P.ROOT).as_posix():P.SHA(p) for p in (f,lf,Path(__file__))}},
        worker_seconds=round(time.monotonic()-tick,3),physical_pass=False,W5_complete=False)
    (P.OUT/'body-fanout-radial-source-witnesses.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(rows=[{k:r[k] for k in ('wire','target','gap_mm','required_project_mm','violates_project_clearance')} for r in report],worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
