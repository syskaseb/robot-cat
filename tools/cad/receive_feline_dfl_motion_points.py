"""Two named changed-interface closest-point receipts, no geometry retry."""
import hashlib
import json
import time
import zipfile
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from check_main_p0_placement import ROOT,SavedShapes,sha
from plan_feline_layout import OUT,MODEL,STAGES,transforms
from receive_feline_global_case_candidates import placement


def main():
    tick=time.monotonic();proof=OUT/'n01-fore-service-macro.json';m=json.loads(proof.read_text())
    for n,h in m['source_sha256'].items():assert sha(ROOT/n)==h,n
    bundle=ROOT/m['bundle'];assert sha(bundle)==m['bundle_sha256']
    motionfile=OUT/'motion-layout.json';axisfile=ROOT/'hardware/simulation/p0/e6-leg-compatibility.json'
    motion=json.loads(motionfile.read_text());axes=json.loads(axisfile.read_text())['axes']
    reader=SavedShapes();receipts=[]
    targets=[f for f in m['failures'] if f['kind']=='actual_sampled_motion_gap']
    assert len(targets)==2
    with zipfile.ZipFile(bundle) as z:
        for t in targets:
            row=next(r for r in m['parts'] if r['name']==t['part']);raw=z.read(row['entry'])
            assert hashlib.sha256(raw).hexdigest()==row['sha256']
            candidate=Part.Shape();candidate.importBrepFromString(raw.decode('utf-8'))
            membership=[(code,stage) for code,groups in motion['membership'].items() for stage,names in groups.items() if t['source'] in names]
            assert len(membership)==1;code,stage=membership[0]
            aa=[next(a for a in axes if a['code']==code and a['stage']==s) for s in STAGES]
            r,v=transforms(aa,motion['poses'][t['pose']]['legs'][code]['angles_delta_degrees'])[STAGES.index(stage)]
            source=reader.shape(MODEL,t['source']);posed=source.copy()
            if np.linalg.norm(r-np.eye(3))>1e-12 or np.linalg.norm(v)>1e-7:posed.Placement=placement(r,v)*posed.Placement
            assert candidate.isValid() and posed.isValid() and candidate.Solids and posed.Solids
            closest=None
            for a in candidate.Solids:
                for b in posed.Solids:
                    gap,points,info=a.distToShape(b)
                    if closest is None or gap<closest['actual_gap_mm']:
                        closest=dict(actual_gap_mm=gap,points_mm=[dict(candidate=list(p),moving_leg=list(q)) for p,q in points][:8])
            assert abs(closest['actual_gap_mm']-t['gap_mm'])<1e-5
            receipts.append(dict(part=t['part'],source=t['source'],leg=code,stage=stage,pose=t['pose'],
                old_gap_mm=t['gap_mm'],candidate_bounds_mm=[[candidate.BoundBox.XMin,candidate.BoundBox.YMin,candidate.BoundBox.ZMin],
                    [candidate.BoundBox.XMax,candidate.BoundBox.YMax,candidate.BoundBox.ZMax]],**closest))
    result=dict(status='TWO_CURRENT_DFL_MOTION_POINT_WITNESSES_RECEIVED',receipts=receipts,
        selected=False,N01_complete=False,physical_pass=False,geometry_changed=False,
        source_sha256={f.relative_to(ROOT).as_posix():sha(f) for f in (proof,bundle,motionfile,axisfile,MODEL,Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3));result['source_sha256'].update(reader.hashes)
    dest=OUT/'n01-dfl-current-motion-points.json';assert not dest.exists()
    dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result['receipts']),flush=True);print('Seconds',result['worker_seconds'],flush=True)


if __name__=='__main__':main()
