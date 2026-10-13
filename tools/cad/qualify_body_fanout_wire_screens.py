"""Batch exact retained-wire distances for named receiver screen rejections.

No route or native CAD mutation. A clearance witness replaces only the sample
screen on the identical complete curve against the identical named wire.
"""
import json
import time
from pathlib import Path
import FreeCAD as A
import build_complete_source_carriers as B
from plan_body_fanout_layout import prepared_rows,receiving_profiles,AXES
from plan_current_moving_looms import exact_quarter,add,mul
from plan_current_mta_interfaces import line

P=B.P


def run():
    tick=time.monotonic();cf=P.OUT/'body-fanout-work-contract.json'
    tf=P.OUT/'body-fanout-receiving-turns.json'
    contract=json.loads(cf.read_text());turns=json.loads(tf.read_text())
    rows={r['wire']:r for r in prepared_rows(contract)}
    targets,wires,archive,sf,hw=B.current_scene(B.H.P.SavedShapes())
    requests={}
    for blocked in turns['blocked']:
        row=rows[blocked['wire']]
        parts=next(p for p,g,k in receiving_profiles(row,blocked['direction']) if k==blocked['profile'])
        blockers=[(blocked['blocker'],parts)] if 'blocker' in blocked else []
        for entry in blocked.get('exit_blockers',[]):
            v=entry['direction'];u=blocked['direction'];start=parts[-1]['end']
            recipe=line(start,add(start,mul(u,10))) if list(v)==list(u) else exact_quarter(start,u,v,10)
            blockers.append((entry['blocker'],[recipe]))
        for block,curve in blockers:
            if block['kind']!='sampled_wire_reservation' or block['name'] not in wires:continue
            key=json.dumps([blocked['wire'],block['name'],curve],sort_keys=True)
            requests[key]=(blocked['wire'],block['name'],curve)
    report=[]
    for name,target,parts in requests.values():
        w=P.wire(parts);other,radius=wires[target]
        assert w.isValid() and other.isValid(),target
        gap=w.copy().distToShape(other.copy())[0];required=radius+1.25
        report.append(dict(wire=name,target=target,parts=parts,gap_mm=gap,required_project_mm=required,
            violates_project_clearance=gap<required-1e-6))
    files=(cf,tf,archive,sf,hw,B.H.HEAD,Path(__file__),Path(B.__file__))
    result=dict(status='EXACT_NAMED_RECEIVER_WIRE_SCREENS_NOT_WHOLE_HARNESS',rows=report,
        physical_pass=False,W5_complete=False,
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files},
        worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/'body-fanout-wire-screen-witnesses.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(pairs=len(report),clear=sum(not r['violates_project_clearance'] for r in report),
        worker_seconds=result['worker_seconds'],W022=[dict(target=r['target'],gap=r['gap_mm'],clear=not r['violates_project_clearance']) for r in report if r['wire']=='W022'])),flush=True)


if __name__=='__main__':run()
