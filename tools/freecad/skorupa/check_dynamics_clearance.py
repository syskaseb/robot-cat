"""Exact BRep interference growth for sampled candidate leg poses.

Existing baseline intersections are reported, not silently called acceptable.
This is discrete sampling, not continuous collision detection.
"""
from pathlib import Path
import json
import sys
import time
import FreeCAD as A
import Part
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools/simulation'))
from cad_model import OUT,R,ORIGIN_MM,REVISION
from cad_kinematics import stage_transforms,stepping_targets
from stance_search import displaced


def placement(Q,t):
    q=R.T@Q@R
    d=ORIGIN_MM-q@ORIGIN_MM+R.T@t*1000
    m=A.Matrix()
    for i in range(3):
        for j in range(3):setattr(m,'A%d%d'%(i+1,j+1),q[i,j])
    m.A14,m.A24,m.A34=d.tolist()
    return A.Placement(m)


def main():
    geometry=json.loads((OUT/'geometry.json').read_text(encoding='utf8'))
    model=json.loads((OUT/'model.json').read_text(encoding='utf8'))
    feet=json.loads((OUT/'feet.json').read_text())
    source=ROOT/('hardware/skorupa/v28/shape-cache' if REVISION=='v28' else 'hardware/skorupa/v26/shape-cache')
    shapes={};stages={}
    for row in geometry['components']:
        # Buried motor / PCB / gear internals are not external collision skins.
        # Servo housing pieces and both horn discs remain in the audit.
        if row['label'].startswith(('MOTOR-','PCB-CHAZUO_','GE_')):continue
        s=Part.Shape();s.read(str(source/(row['name']+'.brep')))
        shapes[row['name']]=s;stages[row['name']]=row['stage']
    posed,_,neutral=displaced(model,feet,-.03,-.005)
    poses=[('cad_rest',{j['name']:0. for j in model['joints']}),('candidate_stand',neutral)]
    for t in [1.5,4.5,7.5,10.5]:
        poses.append((f'lift_{t}',stepping_targets(model,feet,t,offset=[-.03,0,-.005],support_com=posed['total']['com_m'])))
    baseline={};report=[]
    for label,angles in poses:
        transforms={'Chassis':A.Placement()}
        for code in feet:
            chain=[j for j in model['joints'] if j['cad_code']==code]
            for j,(Q,t,_,_) in zip(chain,stage_transforms(chain,[angles[j['name']] for j in chain])):
                transforms[j['stage']]=placement(Q,t)
        moved={}
        for n,s in shapes.items():
            c=s.copy();c.Placement=transforms[stages[n]].multiply(c.Placement);moved[n]=c
        hits=[];checks=0;started=time.monotonic()
        for i,n in enumerate(moved):
            a=moved[n]
            for other in list(moved)[i+1:]:
                if stages[n]==stages[other]:continue
                b=moved[other]
                if not a.BoundBox.intersect(b.BoundBox):continue
                checks+=1
                if checks%10==0:print(label,'boolean',checks,n,other,flush=True)
                v=a.common(b).Volume
                key=tuple(sorted([n,other]))
                if label=='cad_rest' and v>.1:baseline[key]=v
                if v>.1:
                    prior=baseline.get(key,0)
                    hits.append(dict(a=n,b=other,volume_mm3=v,baseline_mm3=prior,
                                     growth_mm3=v-prior,new_or_growing=v>max(.2,prior*1.05)))
        row=dict(pose=label,boolean_checks=checks,seconds=time.monotonic()-started,hits=hits)
        report.append(row)
        (OUT/'clearance-samples.json').write_text(json.dumps(dict(scope=__doc__,source_sha256=model['source_sha256'],poses=report),indent=2),encoding='utf8')
        print(label,checks,'checks',len(hits),'overlaps',sum(h['new_or_growing'] for h in hits),'growing',flush=True)


if __name__=='__main__':main()
