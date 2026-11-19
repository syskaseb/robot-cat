"""Recheck the three distinct yaw and tail poses against final stationary members."""
from pathlib import Path
import json,runpy,math
import numpy as np
P=Path(__file__).parent
src=(P.parent/'day19-whole-appearance-and-moving-neck-correction/moving-seam-screen.py').read_text()
exec(src[:src.index('pairs=')].replace('whole-cat19D.FCStd','whole-cat19E.FCStd'))
pairs=[('E19_KeyedTail',['E19_RearBase','E19_RearLid','S0_body','B19_TailMatedPair'],[140,0,130],[-15,0,15]),('E19_UpperYawCover',['E19_ForeBase','E19_FrontShroud','E19_ForeLid'],[-130,0,127],[-20,0,20])]
cache={n:mesh(n) for a,ns,c,angles in pairs for n in [a]+ns};rows=[]
for a,ns,c,angles in pairs:
    for deg in angles:
        rad=math.radians(deg);sn,cs=math.sin(rad),math.cos(rad)
        R=np.array([[cs,0,sn],[0,1,0],[-sn,0,cs]]) if a=='E19_KeyedTail' else np.array([[cs,-sn,0],[sn,cs,0],[0,0,1]])
        h=np.eye(4);h[:3,:3]=R;h[:3,3]=np.array(c)-R@c
        for n in ns:
            op=vtk.vtkCollisionDetectionFilter();identity=vtk.vtkMatrix4x4();m=vtk.vtkMatrix4x4();m.DeepCopy(h.ravel())
            for i,name,tx in [(0,a,m),(1,n,identity)]:op.SetInputData(i,cache[name]);op.SetMatrix(i,tx)
            op.SetCollisionModeToFirstContact();op.SetBoxTolerance(.0001);op.SetCellTolerance(.0001);op.Update()
            rows.append(dict(moving=a,fixed=n,angle_deg=deg,surface_hit=bool(op.GetNumberOfContacts())))
(P/'final-motion.json').write_text(json.dumps(dict(rows=rows,native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),continuous_proof=None,physical_PASS=False),indent=1)+'\n');print([r for r in rows if r['surface_hit']])
