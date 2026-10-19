"""Receive whole side-carrier CASE catalogue, not another old-row retry."""
import json
import os
import time
from pathlib import Path
import numpy as np
import FreeCAD as A
import Part
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import coo_matrix
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_case_zone_allocation import current_world
from feline_fore_power_pair import SolidQueries
from feline_solid_distance import bbox_lower_bound
from feline_flat_station_templates import box_gap
from receive_feline_global_case_candidates import placement


def main():
    tick=time.monotonic();src=OUT/'n01-side-service-carrier-plan.json';plan=json.loads(src.read_text());dest=OUT/'n01-side-service-cases.json'
    pins={p.relative_to(ROOT).as_posix():sha(p) for p in (src,Path(__file__),Path(__file__).with_name('feline_case_zone_allocation.py'),OUT/'n01-six-source-current-core.json',OUT/'n01-six-source-shared-lanes.outer.brep')}
    result=dict(status='RUNNING_SIDE_CARRIER_CASE_RECEIVER',source_sha256=pins,received={},errors=[],N01_complete=False,physical_pass=False,selected=False)
    if dest.exists():
        old=json.loads(dest.read_text());assert old['source_sha256']==pins;result=old;result.setdefault('prior_worker_seconds',[]).append(result['worker_seconds'])
    def save():
        result['worker_seconds']=round(time.monotonic()-tick,3);dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    save();world,fixed=current_world();query=SolidQueries();outer=Part.Shape();outer.read(str(OUT/'n01-six-source-shared-lanes.outer.brep'))
    if result.get('fixed_source_sha256'):assert result['fixed_source_sha256']==world.pins
    result['fixed_source_sha256']=world.pins
    try:
        for row in plan['candidates']:
            key=str(row['id'])
            if key in result['received']:continue
            if time.monotonic()-tick>240:raise TimeoutError('Atomic4min case gate; all completed source pairs retained')
            lo,hi=np.array(row['bounds_mm']);s=Part.makeBox(*(hi-lo),A.Vector(*lo));r=dict(pairs=[],failure=None)
            outside=s.cut(outer);assert outside.isNull() or outside.isValid();gap=s.distToShape(outer.Shells[0])[0]
            if outside.Volume>1e-5 or gap<3.25-1e-6:r['failure']=dict(kind='true_outer',outside_mm3=outside.Volume,gap_mm=gap)
            if not r['failure']:
                for n,t in fixed.items():
                    if bbox_lower_bound(s.BoundBox,t.BoundBox)>=1.25:continue
                    q=s
                    if n==world.bus['name']:q=s.copy();q.Placement=world.bus['inverse']*q.Placement;t=world.bus['original']
                    if not t.Solids:r['failure']=dict(kind='curve_owner_hold',source=n);break
                    gap=query.distance(q,t);p=dict(source=n,gap_mm=gap,minimum_mm=1.25);r['pairs'].append(p)
                    if gap<1.25-1e-6:
                        reservation=n.startswith('StructureReserve:') or world.meta.get(n,{}).get('kind')=='rectangular_reservation'
                        r['failure']=dict(kind='planning_reservation_hold' if reservation else 'actual_fixed_gap',**p);break
            if not r['failure']:
                for p in world.motion:
                    if bbox_lower_bound(s.BoundBox,A.BoundBox(*p['bounds'][0],*p['bounds'][1]))>=1.25:continue
                    q=s.copy();q.Placement=placement(p['r'],p['t']).inverse()*q.Placement
                    gap=query.distance(q,world.rest[p['name']]);receipt=dict(source=p['name'],pose=p['pose'],gap_mm=gap,minimum_mm=1.25);r['pairs'].append(receipt)
                    if gap<1.25-1e-6:r['failure']=dict(kind='actual_motion36_gap',**receipt);break
            result['received'][key]=r;save();print('Side case',row['id'],row['profile'],row.get('tier'),row['centre_mm'],'clear' if not r['failure'] else r['failure'],flush=True)
        good=[r for r in plan['candidates'] if not result['received'][str(r['id'])]['failure']]
        oldfile=OUT/'n01-case-zone-allocation.json';old=json.loads(oldfile.read_text());assert not old['received']['91']['failure']
        good.append(dict(id=58,profile='fixed_P_SYS',bounds_mm=[[4.55,-1.5,43.],[26.55,35.5,54.]],case_identity_unchanged=True))
        result['P_SYS_case_receipt_reused']=dict(source_file=oldfile.relative_to(ROOT).as_posix(),sha256=sha(oldfile),receipt=old['received']['91'])
        rr=[];cc=[];dd=[];low=[];high=[]
        def add(v,weights,lo,hi):
            k=len(low);rr.extend([k]*len(v));cc.extend(v);dd.extend(weights);low.append(lo);high.append(hi)
        for profile,count in {'standard':16,'large':3,'monitor':1,'fixed_P_SYS':1}.items():
            vv=[i for i,r in enumerate(good) if r['profile']==profile];add(vv,[1.]*len(vv),count,count)
        vv=[i for i,r in enumerate(good) if r['profile']=='large' and r.get('tier')=='upper'];add(vv,[1.]*len(vv),0,1)
        conflicts=0
        for i,a in enumerate(good):
            for j in range(i+1,len(good)):
                if box_gap(np.array(a['bounds_mm']),np.array(good[j]['bounds_mm']))<1.25-1e-6:add([i,j],[1.,1.],-np.inf,1.);conflicts+=1
        matrix=coo_matrix((dd,(rr,cc)),shape=(len(low),len(good))).tocsc()
        fit=milp(np.array([abs(r.get('centre_mm',[15.55])[0])/10000 for r in good]),integrality=np.ones(len(good)),bounds=Bounds(0,1),constraints=LinearConstraint(matrix,low,high),options={'time_limit':20,'mip_rel_gap':0.0})
        chosen=[] if fit.x is None else [r for i,r in enumerate(good) if fit.x[i]>.5]
        result.update(status='WHOLE21_SIDE_CASE_ASSIGNMENT_FULL_UNITS_ROOTS_SERVICE_OPEN' if len(chosen)==21 else 'BOUNDED_SIDE_CASE_CATALOGUE_NO_WHOLE21',
            solver_status=int(fit.status),solver_message=str(fit.message),chosen_cases=chosen,case_conflicts=conflicts,
            clear_case_counts={p:sum(r['profile']==p for r in good) for p in ('standard','large','monitor','fixed_P_SYS')})
    except TimeoutError as exc:result['status']='PARTIAL_SIDE_CASE_RECEIVER';result['slice_note']=str(exc)
    except Exception as exc:result['status']='SIDE_CASE_RECEIVER_ERROR_NOT_ACCEPTANCE';result['errors'].append(repr(exc))
    save();print(json.dumps({k:result.get(k) for k in ('status','worker_seconds','solver_status','clear_case_counts','errors')}),flush=True)


if __name__=='__main__':
    print('WORKER_PID',os.getpid(),flush=True);main()
