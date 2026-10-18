"""All GLOBAL case ends, compulsory first9, then full factory/sleeve/grip domains.

Numerical domains are loose source-field prefilters, NOT CAD acceptance. Both
source exits and nominal100 allowance remain explicit. No hidden extensions.
"""
import json
import math
import sys
import subprocess
import time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from scipy.interpolate import RegularGridInterpolator
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_candidate_collision_scene import Scene
from receive_feline_global_case_candidates import matrix_rotation,placement
from feline_factory_field_domains import evaluate as batch_domains


def full_profile_points(q,d,b,first,R=12.4):
    a=q+d*first;angles=np.linspace(0,math.pi/2,23)
    arc=a+np.sin(angles)[:,None]*d*R+(1-np.cos(angles))[:,None]*b*R
    end=arc[-1];tip=end+b*14
    return dict(factory=np.vstack((np.linspace(q,a,int(math.ceil(first))+1),arc,np.linspace(end,tip,15))),
        sleeve=np.linspace(tip-b*14,tip+b*6,21),custom=np.linspace(tip-b*8,tip+b*18,27)),end,tip


def main():
    tick=time.monotonic();allcells='--all-capacity-cells' in sys.argv
    src=OUT/'n01-global-case-candidates-received.json';dest=OUT/'n01-global-full-factory-domains.json'
    proof=json.loads(src.read_text());assert proof['status']=='GLOBAL_CASES_RECEIVED_FULL_FACTORY_TAILS_OPEN' and proof.get('method_repairs')
    for n,h in proof['source_sha256'].items():assert sha(ROOT/n)==h,n
    cellsfile=OUT/'n01-global-all-case-cells.json'
    if allcells:
        cells=json.loads(cellsfile.read_text());assert cells['status']=='ALL_GLOBAL_CASE_CELLS_RETAINED_END_DOMAINS_OPEN'
        for n,h in cells['source_sha256'].items():assert sha(ROOT/n)==h,n
        casepool=cells['cells']
    else:casepool=[dict(r,prior_exact_case_clear=True) for r in proof['completed_candidates'] if r['status']=='SOURCE_CASE_STATIC_AND36SAMPLED_MOTION_CLEAR_TAILS_OPEN']
    fieldfile=OUT/'n01-global-current-case-field.npz';fieldproof=OUT/'n01-global-case-capacity.json';capacity=json.loads(fieldproof.read_text())
    assert sha(fieldfile)==capacity['field_sha256'];field=np.load(fieldfile,allow_pickle=False);axes=[field[k] for k in ('x','y','z')]
    interpolators={k:RegularGridInterpolator(axes,field[k+'_distance'],bounds_error=False,fill_value=0) for k in ('material','reservation','motion36','curve_hold','outer')}
    scene=Scene();sourcefile=OUT/'n01-all-extra-interface-contract.json';sources=json.loads(sourcefile.read_text())
    local={e['endpoint']:e for sec in sources['sections'] for e in sec['ends'] if e.get('local_point_mm') is not None}
    pins=dict(scene.pins)
    for p in (src,fieldfile,fieldproof,sourcefile,Path(__file__),Path(__file__).with_name('feline_candidate_collision_scene.py')):
        pins[p.relative_to(ROOT).as_posix()]=sha(p)
    if allcells:pins[cellsfile.relative_to(ROOT).as_posix()]=sha(cellsfile)
    batchfile=Path(__file__).with_name('feline_factory_field_domains.py');pins[batchfile.relative_to(ROOT).as_posix()]=sha(batchfile)
    result=dict(status='RUNNING_GLOBAL_FULL_FACTORY_DOMAINS',selected=False,N01_complete=False,physical_pass=False,
        source_sha256=pins,first_lands=[],domains=[],errors=[],case_receipts=[],all_case_cells_before_end_pruning=allcells,
        factory_radius_mm=2,sleeve_radius_mm=2.4,custom_radius_mm=1.55,
        R_mm=12.4,first_min_mm=9,after_arc_mm=14,lap_mm=8,sleeve_mm=20,custom_grip_from_factory_tip_mm=[9,18],
        source100mm_is_delivery_assumption=True,case_identity_used_for_geometry='F_HY geometry equivalent to F_HP/F_TY instances; actual electrical side mapping remains explicit',
        numeric_material_gap_prefilter_mm=.2,numeric_reservation_motion_gap_mm=1.25,actual_material_gap_mm=1.25,actual_wire_wire_gap_mm=.2,
        source_field_screen_not_actual_geometry_acceptance=True,full_two_tail_packages_or_montage_or_stock_not_qualified=True)
    previous=json.loads(dest.read_text()) if dest.exists() else None
    if previous:
        assert previous['status']=='PARTIAL_GLOBAL_FULL_FACTORY_DOMAINS'
        if previous['source_sha256']!=pins:
            rel=Path(__file__).relative_to(ROOT).as_posix();batchrel=batchfile.relative_to(ROOT).as_posix()
            changed={n for n in set(pins)|set(previous['source_sha256']) if pins.get(n)!=previous['source_sha256'].get(n)}
            assert '--batch-receive' in sys.argv and changed=={rel,batchrel}
            oldcode=subprocess.run(['git','show','34ff0a28:'+rel],cwd=ROOT,capture_output=True,check=True).stdout
            assert __import__('hashlib').sha256(oldcode).hexdigest()==previous['source_sha256'][rel]
            previous.setdefault('implementation_receipts',[]).append(dict(prior_code_commit='34ff0a28',
                source_geometry_grid_and224profiles_unchanged=True,
                prior_first_lands_reused=len(previous['first_lands']),prior_complete_domains_reused=len(previous['domains']),
                method='Batch the identical points per category instead of3360interpolator calls per end'))
            previous['source_sha256']=pins
        result=previous;result.setdefault('prior_attempts',[]).append(dict(seconds=previous['worker_seconds'],errors=previous['errors']));result['errors']=[]
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3)
        dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    def gate():
        if time.monotonic()-tick>180:raise TimeoutError('180s all-end gate; receive remaining endpoints only')
    done={(r['case_id'],r['side']):r for r in result['first_lands']};done_domains={(r['case_id'],r['side']) for r in result['domains']}
    save()
    try:
        case_done={r['case_id']:r for r in result['case_receipts']}
        for case in casepool:
            r=matrix_rotation(case['source_axis_to_world_axis']);rot=placement(r,[0,0,0]).Rotation
            centre=A.Vector(*case['centre_mm'])
            if case['id'] not in case_done:
                if case['prior_exact_case_clear']:receipt=dict(case_id=case['id'],status='PRIOR_CASE_STATIC_MOTION_REUSED',failure=None)
                else:
                    source=scene.templates['F_HY'][1];s=source.copy()
                    s.Placement=A.Placement(centre-rot.multVec(source.BoundBox.Center),rot)*s.Placement
                    failure,queries=scene.receive(s,wire=False)
                    receipt=dict(case_id=case['id'],status='SOURCE_CASE_CLEAR' if failure is None else 'SOURCE_CASE_REJECTED',failure=failure,completed_queries=queries)
                result['case_receipts'].append(receipt);case_done[case['id']]=receipt;save()
            if case_done[case['id']]['failure'] is not None:continue
            for side in ('in','out'):
                gate();key=case['id'],side;e=local['F_HY.'+side]
                q=np.array(list(centre+rot.multVec(A.Vector(*e['local_point_mm']))));d=np.array(list(rot.multVec(A.Vector(*e['departure_axis']))))
                if key not in done:
                    land=Part.makeCylinder(2,9,A.Vector(*q),A.Vector(*d))
                    failure,queries=scene.receive(land,wire=True)
                    row=dict(case_id=case['id'],side=side,source_reference='F_HY.'+side,point_mm=q.tolist(),departure_axis=d.tolist(),
                        first_mm=9,status='COMPULSORY_FIRST9_SOURCE_CLEAR' if failure is None else 'COMPULSORY_FIRST9_BLOCKED',failure=failure,completed_queries=queries)
                    result['first_lands'].append(row);done[key]=row;save()
                if done[key]['failure'] is not None or key in done_domains:continue
                u=np.eye(3)[int(np.argmin(abs(d)))];u-=d*np.dot(u,d);u/=np.linalg.norm(u);v=np.cross(d,u)
                candidates=[];diagnostic={};eligible,tested=batch_domains(q,d,u,v,interpolators,full_profile_points,gate,diagnostic)
                for minimum,first,b,end,tip in eligible:
                    candidates.append(dict(first_mm=first,bend_unit=b.tolist(),R_mm=12.4,
                                factory_external_length_mm=first+12.4*math.pi/2+14,
                                nominal_factory_blank_with3inside_mm=3+first+12.4*math.pi/2+14,
                                source100mm_is_assumption=True,numeric_min_surface_margin_mm=minimum,
                                factory_arc_end_mm=end.tolist(),factory_tip_mm=tip.tolist(),
                                factory_grip_line_mm=[(q+d*(first-9)).tolist(),(q+d*first).tolist()],
                                custom_grip_line_mm=[(tip+b*9).tolist(),(tip+b*18).tolist()],
                                sleeve_line_mm=[(tip-b*14).tolist(),(tip+b*6).tolist()],
                                full_CAD_or_other_case_tail_or_root_not_qualified=True))
                candidates.sort(key=lambda r:(-r['numeric_min_surface_margin_mm'],r['first_mm']))
                result['domains'].append(dict(case_id=case['id'],side=side,point_mm=q.tolist(),departure_axis=d.tolist(),
                    numeric_trials=tested,numeric_eligible=len(candidates),candidates=candidates[:12],field_diagnostic=diagnostic))
                done_domains.add(key);save()
                print('Complete source end',key,'field_candidates',len(candidates),flush=True)
        result['both_first9_case_ids']=[c['id'] for c in casepool if all(done.get((c['id'],side),{}).get('failure','missing') is None for side in ('in','out'))]
        result['both_numeric_tail_case_ids']=[c for c in result['both_first9_case_ids'] if all(any(r['case_id']==c and r['side']==s and r['numeric_eligible'] for r in result['domains']) for s in ('in','out'))]
        result['status']='GLOBAL_ALL_END_DOMAINS_RECEIVED_FULL_CAD_TAILS_OPEN'
    except Exception as e:result['status']='PARTIAL_GLOBAL_FULL_FACTORY_DOMAINS';result['errors'].append(repr(e))
    save();print(json.dumps(dict(status=result['status'],first_lands=len(result['first_lands']),numeric_domains=len(result['domains']),
        both_first9=result.get('both_first9_case_ids'),both_numeric_tails=result.get('both_numeric_tail_case_ids'),errors=result['errors'],seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':main()
