"""Exact endpoint screen for changed leg pose against retained P0 material.

Reports intersections, inherited intersections and invalid shapes separately.
No claim of continuous movement, shell fit, full wiring or hardware limits.
"""
import argparse
import itertools
import json
import time

import FreeCAD as A
import Part
from check_main_p0_placement import ROOT, SavedShapes, sha
from plan_feline_layout import BASE, OUT, MODEL, STAGES


def placement(axes, angles):
    transform=A.Placement();result={}
    for stage,a,angle in zip(STAGES,axes,angles):
        p=A.Vector(*a['pivot_mm']);rot=A.Rotation(A.Vector(*a['axis']),angle)
        transform=transform*A.Placement(p-rot.multVec(p),rot)
        result[stage]=transform
    return result


def main(sample_path=False):
    tick=time.monotonic()
    motion=json.loads((OUT/'motion-layout.json').read_text())
    layout=json.loads((OUT/'layout-checkpoint.json').read_text())
    assert all(sha(ROOT/n)==h for n,h in motion['source_sha256'].items())
    axes=json.loads((ROOT/'hardware/simulation/p0/e6-leg-compatibility.json').read_text())['axes']
    reader=SavedShapes()
    membership=motion['membership']
    stage_of={n:(code,stage) for code,g in membership.items() for stage,ns in g.items() for n in ns}
    fixed=[r['object'] for r in motion['inventory'] if r['kind']=='surface' and
           (r['label'].startswith('P0_') or r['object'].startswith('Print_P0_') or r['object'].startswith('Battery'))
           and r['object'] not in stage_of]
    names=list(stage_of)+fixed
    supplier_pairs=set()
    if sample_path:
        qualified=json.loads((OUT/'leg-body-endpoints-qualified.json').read_text())
        supplier_pairs={frozenset((r['a'],r['b'])) for r in qualified['supplier_joint_model_open']}
        assert len(supplier_pairs)==12
    report=dict(status='RUNNING_ENDPOINT_SCREEN',selected=False,physical_pass=False,
        scope='Actual108articulated P0parts vs retained fixed P0/battery and cross-stage leg members, at rest and candidate lie only.',
        fixed=fixed,poses=[],new_contacts=[],inherited_contacts=[],errors=[],pairs=0,
        continuous_sweep_verified=False,full_wiring_verified=False,mechanical_limits_verified=False)
    shapes={}
    for n in names:
        s=reader.shape(MODEL,n)
        if not s.isValid() or not s.Solids:
            report['errors'].append(dict(object=n,error='Invalid or non-solid saved current material'))
        else:shapes[n]=s
    if sample_path:
        for i in range(1,5):
            n=f'BellyPadReservation{i}'
            shapes[n]=reader.shape(OUT/'FelineLayoutEnvelope.FCStd',n)
            assert shapes[n].isValid()
            fixed.append(n)
    baseline={}
    pose_indices=range(layout['planning_pose_index']+1) if sample_path else (0,layout['planning_pose_index'])
    destination=OUT/('leg-body-path.json' if sample_path else 'leg-body-endpoints.json')
    report['supplier_pairs_excluded_from_external_scope']=[sorted(p) for p in supplier_pairs]
    report['scope']='Actual108leg parts vs fixedP0/battery and four candidate pad columns, all36sampled poses to94.79mm drop;12supplier GE/horn mating interfaces excluded and OPEN.' if sample_path else report['scope']
    for index in pose_indices:
        pose=motion['poses'][index];current={n:s for n,s in shapes.items() if n in fixed}
        for code,g in membership.items():
            a=[next(r for r in axes if r['code']==code and r['stage']==stage) for stage in STAGES]
            transforms=placement(a,pose['legs'][code]['angles_delta_degrees'])
            for stage,names in g.items():
                for n in names:
                    if n not in shapes:continue
                    s=shapes[n].copy();s.Placement=transforms[stage]*s.Placement
                    current[n]=s
        pairs=[]
        moving=[n for n in stage_of if n in current]
        for n in moving:
            for f in fixed:
                if f in current:pairs.append((n,f))
        for n,m in itertools.combinations(moving,2):
            if stage_of[n]==stage_of[m]:continue
            pairs.append((n,m))
        contacts=[];tested=0
        for n,m in pairs:
            if frozenset((n,m)) in supplier_pairs:continue
            a,b=current[n],current[m]
            if not a.BoundBox.intersect(b.BoundBox):continue
            key='|'.join(sorted((n,m)))
            tested+=1;report['pairs']+=1
            try:
                common=a.common(b)
                if not common.isNull() and not common.isValid():
                    raise ValueError('Invalid intersection result')
                volume=common.Volume
                if index==0:
                    baseline[key]=volume
                    if volume>1e-5:report['inherited_contacts'].append(dict(a=n,b=m,volume_mm3=volume))
                elif baseline.get(key,0) is None:
                    report['errors'].append(dict(a=n,b=m,pose=index,
                        error='Baseline Boolean failed; current volume cannot be classified as a NEW contact',
                        current_volume_mm3=volume))
                elif volume>max(1e-5,baseline.get(key,0)+1e-4):
                    row=dict(a=n,b=m,rest_volume_mm3=baseline.get(key,0),volume_mm3=volume,
                             pose=index,body_drop_mm=pose['body_drop_mm'])
                    contacts.append(row);report['new_contacts'].append(row)
            except Exception as error:
                if index==0:baseline[key]=None
                report['errors'].append(dict(a=n,b=m,pose=index,error=str(error)))
            if tested%100==0:
                report['worker_seconds']=round(time.monotonic()-tick,3)
                destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
                print('pose',index,'pairs',tested,'new',len(report['new_contacts']),'errors',len(report['errors']),flush=True)
        report['poses'].append(dict(index=index,body_drop_mm=pose['body_drop_mm'],pairs=tested,new_contacts=len(contacts)))
        report['worker_seconds']=round(time.monotonic()-tick,3)
        destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
        print('Completed pose',index,'new',len(report['new_contacts']),'errors',len(report['errors']),flush=True)
    report.update(status='ENDPOINT_INTERFACES_REJECTED' if report['new_contacts'] or report['errors'] else 'ENDPOINT_SCREEN_CLEAR_CONTINUOUS_PATH_OPEN',
        source_sha256={**motion['source_sha256'],**reader.hashes,Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
        worker_seconds=round(time.monotonic()-tick,3))
    if sample_path and not report['new_contacts'] and not report['errors']:
        report['status']='SAMPLED_EXTERNAL_LEG_PAD_PATH_CLEAR_SUPPLIER_JOINTS_WIRING_SHELL_OPEN'
    destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:report[k] for k in ('status','pairs','worker_seconds')}),
          'new',len(report['new_contacts']),'errors',len(report['errors']),flush=True)


if __name__=='__main__':
    from pathlib import Path
    parser=argparse.ArgumentParser()
    parser.add_argument('--sample-path',action='store_true')
    args=parser.parse_args()
    main(args.sample_path)
