"""Exact distances for the two named receiver witnesses, no layout mutation."""
import json
import time
import sys
from pathlib import Path
import FreeCAD as A
import build_complete_source_carriers as B
from plan_body_fanout_layout import prepared_rows,AXES
from plan_current_moving_looms import exact_quarter,add,mul
from plan_current_mta_interfaces import line

P=B.P


def run():
    tick=time.monotonic();cf=P.OUT/'body-fanout-work-contract.json'
    rows=prepared_rows(json.loads(cf.read_text()))
    targets,wires,archive,sf,hw=B.current_scene(B.H.P.SavedShapes())
    report=[]
    moved='--land-after-turn' in sys.argv
    for name,target,kind in (('W024','wire/W078','wire'),('W033','F0_CP2','material')):
        row=next(r for r in rows if r['wire']==name)
        for direction in AXES:
            if sum(a*b for a,b in zip(direction,row['receiver_outward_axis'])):continue
            begin=add(row['receiver_point_mm'],mul(row['receiver_outward_axis'],3)) if moved else row['free_end']
            recipe=exact_quarter(begin,row['receiver_outward_axis'],direction,10)
            parts=[recipe]
            if moved:parts.append(line(recipe['end'],add(recipe['end'],mul(direction,9))))
            w=P.wire(parts)
            other,radius=wires[target] if kind=='wire' else (targets[target],0)
            assert w.isValid() and other.isValid(),target
            gap=w.copy().distToShape(other.copy())[0];required=radius+1.25
            report.append(dict(wire=name,target=target,kind=kind,direction=list(direction),
                gap_mm=gap,required_project_mm=required,violates_project_clearance=gap<required-1e-6,
                approach_parts=parts,entry_straight_project_mm=3 if moved else 9,
                receiving_grip_straight_mm=9,grip_after_turn=moved))
    files=(cf,archive,sf,hw,B.H.HEAD,Path(__file__),Path(B.__file__))
    result=dict(status='EXACT_RECEIVER_APPROACH_WITNESSES_NOT_WHOLE_HARNESS',rows=report,
        physical_pass=False,W5_complete=False,
        source_sha256={f.relative_to(P.ROOT).as_posix():P.SHA(f) for f in files},
        worker_seconds=round(time.monotonic()-tick,3))
    (P.OUT/('body-fanout-receiver-grip-space.json' if moved else 'body-fanout-receiver-witnesses.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':run()
