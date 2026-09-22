"""Quasi-static stance search. Candidates must still pass CAD collision checks."""
from copy import deepcopy
import json
import numpy as np
from cad_model import OUT,combine,static_report
from cad_kinematics import inverse,stage_transforms


def displaced(model,feet,dx,dz):
    result=deepcopy(model);newfeet={};angles={}
    for code,foot in feet.items():
        chain=[j for j in model['joints'] if j['cad_code']==code]
        target=np.array(foot)+[dx,0,dz]
        q=inverse(chain,foot,target)
        newfeet[code]=target.tolist()
        for j,angle,(R,t,p,a) in zip(chain,q,stage_transforms(chain,q)):
            angles[j['name']]=float(angle)
            for part in result['components']:
                if part['stage']==j['stage']:
                    part['com_m']=(R@part['com_m']+t).tolist()
                    part['inertia_kg_m2']=(R@part['inertia_kg_m2']@R.T).tolist()
            jj=next(row for row in result['joints'] if row['name']==j['name'])
            jj['origin_m']=p.tolist();jj['axis']=a.tolist()
    result['total']=combine(result['components'])
    return result,newfeet,angles


def main():
    model=json.loads((OUT/'model.json').read_text(encoding='utf8'))
    feet=json.loads((OUT/'feet.json').read_text())
    candidates=[]
    for dx in np.arange(-.04,.011,.005):
        for dz in [-.005,0,.005,.01]:
            try:m,f,q=displaced(model,feet,dx,dz)
            except ValueError:continue
            stat=static_report(m,f)
            if not stat['four_foot_equilibrium']:continue
            candidates.append(dict(dx_m=float(dx),dz_m=dz,peak_static_nm=max(abs(j['torque_nm']) for j in stat['joint_torques']),
                                   angles=q,static=stat,feet=f))
    candidates.sort(key=lambda c:c['peak_static_nm'])
    report=dict(scope='Vertical-reaction static estimate only; geometry collision audit required. NOT a released stance.',
                candidates=candidates)
    (OUT/'stance-search.json').write_text(json.dumps(report,indent=2),encoding='utf8')
    print([(round(c['dx_m'],3),c['dz_m'],round(c['peak_static_nm'],3)) for c in candidates[:8]])


if __name__=='__main__':main()
