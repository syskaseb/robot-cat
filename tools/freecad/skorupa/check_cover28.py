"""Incremental cover regression on the SAME six v27 sampled joint poses.

Unchanged-part pairs inherit v27's audit; this is not a new exhaustive or
continuous gait check. Shape geometry and assembly axes except the cover
are unchanged by Apply28; check volume/COM/inertia/bounds as an extra guard.
"""
from pathlib import Path
import json,sys,hashlib
import FreeCAD as A
import Part
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/simulation'))
from cad_kinematics import stage_transforms,stepping_targets
from stance_search import displaced
from check_dynamics_clearance import placement
OUT=ROOT/'hardware/simulation/v28'


def read(p):return json.loads(p.read_text(encoding='utf8'))


def main():
    previous=read(ROOT/'hardware/simulation/v27/geometry.json')
    current=read(OUT/'geometry.json')
    old={p['name']:p for p in previous['components']};new={p['name']:p for p in current['components']}
    assert old.keys()==new.keys()
    for n in old:
        assert old[n]['stage']==new[n]['stage']
        if n=='Part__Feature':continue
        for key in ['volume_mm3','com_mm','bbox_mm','inertia_volume_mm5']:
            assert np.allclose(old[n][key],new[n][key],atol=1e-5,rtol=1e-8),(n,key)
    assert previous['axes']==current['axes']
    model=read(ROOT/'hardware/simulation/v27/model.json');feet=read(ROOT/'hardware/simulation/v27/feet.json')
    posed,_,neutral=displaced(model,feet,-.03,-.005)
    poses=[('cad_rest',{j['name']:0. for j in model['joints']}),('candidate_stand',neutral)]
    poses += [(f'lift_{t}',stepping_targets(model,feet,t,offset=[-.03,0,-.005],support_com=posed['total']['com_m'])) for t in [1.5,4.5,7.5,10.5]]
    cache=ROOT/'hardware/skorupa/v28/shape-cache';shapes={}
    for n,p in new.items():
        if p['stage']=='Chassis' and n!='Part__Feature':continue
        if p['label'].startswith(('MOTOR-','PCB-CHAZUO_','GE_')):continue
        s=Part.Shape();s.read(str(cache/(n+'.brep')));shapes[n]=s
    cover=shapes.pop('Part__Feature');rows=[]
    for label,q in poses:
        transforms={}
        for code in feet:
            chain=[j for j in model['joints'] if j['cad_code']==code]
            for j,(Q,t,_,_) in zip(chain,stage_transforms(chain,[q[j['name']] for j in chain])):
                transforms[j['stage']]=placement(Q,t)
        checks=0;hits=[]
        for n,s in shapes.items():
            s=s.copy();s.Placement=transforms[new[n]['stage']]*s.Placement
            if not s.BoundBox.intersect(cover.BoundBox):continue
            checks+=1;v=cover.common(s).Volume
            if v>.1:hits.append(dict(part=n,volume_mm3=v))
        rows.append(dict(pose=label,checks=checks,hits=hits,angles_rad=q));assert not hits,rows[-1]
        print(label,checks,'cover checks; no overlaps >0.1 mm3',flush=True)
    base=ROOT/'hardware/simulation/v27/clearance-samples.json'
    prior=read(base);assert len(prior['poses'])==6
    assert all(all(h['a']=='Part__Feature' or h['b']=='Part__Feature' for h in p['hits']) for p in prior['poses'])
    result=dict(source_sha256=current['source_sha256'],scope=__doc__,unchanged_components=237,
                baseline_report='v27/clearance-samples.json',baseline_source_sha256=previous['source_sha256'],
                inherited_unchanged_pair_audit=True,poses=rows,
                conclusion='No cross-stage overlap above 0.1 mm3 in these six inherited sampled poses after cover replacement. Same-stage fitted components, entire gait and continuous ranges NOT certified.')
    (OUT/'cover-clearance-regression.json').write_text(json.dumps(result,indent=2),encoding='utf8')


if __name__=='__main__':main()
