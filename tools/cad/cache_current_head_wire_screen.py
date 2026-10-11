"""Reuse qualified actual head-wire geometry in cheap shared planning.

This is a sampled proximity cache, NOT a new head qualification or BRep pass.
Exact reader inputs are pinned; no invalid supplier PCB compound is used.
"""
import json,time,math
from pathlib import Path
from current_complete_harness_context import context
from plan_current_moving_looms import ROOT,OUT,SHA
from plan_current_mta_interfaces import line

def run():
    tick=time.monotonic();reader,pins,targets,old=context();rows=[]
    for name,(shape,radius) in old.items():
        if not name.startswith('head/'):continue
        parts=[]
        for edge in shape.Edges:
            points=edge.discretize(Distance=.5)
            parts.extend(line(list(a),list(b)) for a,b in zip(points,points[1:]) if (b-a).Length>1e-8)
        rows.append(dict(wire=name,OD_mm=2*radius,segments=parts))
    assert rows
    pins.add(Path(__file__))
    report=dict(status='HEAD_REFERENCE_SAMPLED_CENTRELINES_ONLY',rows=rows,
        source_sha256={**reader.hashes,**{f.relative_to(ROOT).as_posix():SHA(f) for f in pins}},
        not_a_material_or_continuous_motion_pass=True,
        worker_seconds=time.monotonic()-tick)
    (OUT/'head-wire-screen-reference.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(status=report['status'],rows=len(rows),seconds=report['worker_seconds'])))

if __name__=='__main__':run()
