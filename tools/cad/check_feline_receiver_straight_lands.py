"""Cheap invariant gate: required straight lands cannot be fixed by bend search.

Actual complete native feet are obstacles, not only newly added bridge material.
Only this changed interface is tested; no full-wiring/motion acceptance follows.
"""
import json,time
from pathlib import Path
import FreeCAD as A
import Part
import numpy as np
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT


def main():
    tick=time.monotonic();reader=SavedShapes()
    receiptfile=OUT/'motion-receivers-checks.json';receipt=json.loads(receiptfile.read_text())
    assert receipt['native_built'] and receipt['fresh_reopen']
    native=ROOT/receipt['native'];assert sha(native)==receipt['native_sha256']
    planfile=ROOT/receipt['module_plan'];plan=json.loads(planfile.read_text())
    oldfile=OUT/'prefix-allocation.json';old=json.loads(oldfile.read_text())
    result=dict(status='CHANGED_STRAIGHT_LAND_GATE_RUNNING',selected=False,physical_pass=False,
        required_straight_mm=9,full_native_feet_used=True,checks=[],invariant_blockers=[],
        bend_solver_run=False,full_wiring_complete=False,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (native,receiptfile,planfile,oldfile,Path(__file__))})
    for spec in old['specifications']:
        if spec['id'] not in ('W044/custom/start','W052/custom/start'):continue
        change=plan['motion_receiving_changes'][spec['role']]
        p=np.array(change['rotation_rows'])@np.array(spec['point'])+change['translation_mm']
        d=np.array(change['rotation_rows'])@np.array(spec['direction']);d/=np.linalg.norm(d)
        land=Part.makeCylinder(spec['radius'],9,A.Vector(*p),A.Vector(*d))
        assert land.isValid()
        for i in range(1,5):
            name=f'BellyFoot{i}';foot=reader.shape(native,name)
            c=land.common(foot);assert c.isNull() or c.isValid()
            row=dict(wire=spec['id'],foot=name,start_mm=p.tolist(),end_mm=(p+9*d).tolist(),
                radius_mm=spec['radius'],intersection_mm3=c.Volume,gap_mm=land.distToShape(foot)[0])
            result['checks'].append(row)
            if c.Volume>1e-5 or row['gap_mm']<1.25-1e-5:result['invariant_blockers'].append(row)
    assert len(result['checks'])==8
    # Close a skipped changed-case pair family using provable disjoint bounds.
    # Bboxes are used ONLY as a separation proof, never as contact evidence.
    groups={g['role']:g for g in plan['groups']};separations=[]
    for a in groups['AUX4092']['objects']:
        sa=reader.shape(native,a)
        for role in ('WAGO:P_SYS_new','WAGO:P_REAR'):
            for b in groups[role]['objects']:
                sb=reader.shape(native,b);gap=sb.BoundBox.XMin-sa.BoundBox.XMax
                assert gap>0,(a,b,gap)
                separations.append(dict(a=a,b=b,proven_x_separation_mm=gap))
    result['previous_static_pair_coverage_completion']=separations
    result.update(status='RECEIVER_LAYOUT_REQUIRED_STRAIGHT_LAND_BLOCKED' if result['invariant_blockers'] else 'TWO_STRAIGHT_LANDS_CLEAR_OTHER_INTERFACES_OPEN',
        native_changed=False,worker_seconds=round(time.monotonic()-tick,3),
        next='Change receiving connector/whole exit topology; no8bend retry can remove a contact on the compulsory first9mm. Keep electrical branches distinct; any compact-connector port positions require real supplier CAD or explicit fit assumptions.')
    result['source_sha256'].update(reader.hashes)
    (OUT/'receiver-straight-land-gate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','invariant_blockers','worker_seconds')}),flush=True)


if __name__=='__main__':main()
