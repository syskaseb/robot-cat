"""Constrained receive of saved numerical states, not another CAD layout.

The first least-squares fit traded radius/air against length. SLSQP now treats
sampled geometric constraints as hard inequalities and length as an equality.
Final continuous-span curvature/quad length still decide numeric eligibility;
only an exact source-BRep receiver can qualify the physical geometry scope.
"""
import json
import time
from pathlib import Path
import numpy as np
from scipy.interpolate import BSpline
from scipy.optimize import minimize
from scipy.ndimage import map_coordinates
from scipy.spatial.distance import cdist
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_cubic_curvature import extrema,exact_length
from feline_tangent_routes import samples


def main():
    tick=time.monotonic();src=OUT/'n01-atlas-usb-spline-fit.json';policy=OUT/'n01-reservation-ownership-plan.json';dest=OUT/'n01-atlas-usb-spline-constrained.json';assert not dest.exists()
    parent=json.loads(src.read_text());assert parent['numeric_candidate'] is None
    p=json.loads(policy.read_text());f=ROOT/p['field'];assert sha(f)==p['field_sha256'];a=np.load(f,allow_pickle=False);origin=np.array([a[k][0] for k in ('x','y','z')]);inside=a['inside'].astype(float)
    fields=[a['material_distance'],a['mandatory_reservation_distance'],a['motion36_distance'],a['outer_distance']]
    report=dict(status='RUNNING_HARD_CONSTRAINT_RECEIVE_OF_SAVED_SPLINES',selected=False,N01_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in (src,policy,f,Path(__file__),Path(__file__).with_name('feline_cubic_curvature.py'))},
        no_source_geometry_or_component_pose_changed=True,no_new_manual_waypoint_family=True,seeds=[],numeric_candidate=None)
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    save();chosen=[];seen=set()
    for s in sorted(parent['seeds'],key=lambda s:s['sampled_metrics']['least_squares_cost']):
        if s['source_anchor_index'] in seen:continue
        chosen.append(s);seen.add(s['source_anchor_index'])
        if len(chosen)>=3:break
    class Cap(Exception):pass
    for previous in chosen:
        if time.monotonic()-tick>115:break
        st=time.monotonic();cc=np.array(previous['controls_mm']);knots=np.array(previous['knots']);count=len(cc);u=np.linspace(0,1,193);basis=BSpline(knots,np.eye(count),3);M=basis(u);D1=basis(u,1);D2=basis(u,2)
        sp=previous['source_prefix_parts'];tp=previous['BUS_outward_prefix_parts'];q0=cc[0];q1=cc[-1];v0=cc[1]-q0;h0=np.linalg.norm(v0);v0/=h0;v1=q1-cc[-2];h1=np.linalg.norm(v1);v1/=h1
        prefix_length=sum(s['length'] for s in sp+tp);target=452-prefix_length
        x0=np.r_[cc[2:-2].ravel(),h0,h1];lower=np.r_[np.tile([-136,-92,-42],count-4),1,1];upper=np.r_[np.tile([178,92,106],count-4),70,70];x0=np.clip(x0,lower+1e-6,upper-1e-6)
        gauss,weight=np.polynomial.legendre.leggauss(20);gu=[];gw=[]
        for lo,hi in zip(np.unique(knots)[:-1],np.unique(knots)[1:]):gu.extend(lo+(gauss+1)*(hi-lo)/2);gw.extend(weight*(hi-lo)/2)
        GL=basis(np.array(gu),1);gw=np.array(gw)
        fixed_start=np.array([q for s in sp for q in samples(s,2)]);fixed_end=np.array([q for s in tp[::-1] for q in list(samples(s,2))[::-1]])
        best=dict(score=np.inf,x=x0.copy());cache={};calls=0
        def controls(x):return np.vstack([q0,q0+v0*x[-2],x[:-2].reshape(-1,3),q1-v1*x[-1],q1])
        def evaluate(x):
            nonlocal calls
            if time.monotonic()-st>32 or time.monotonic()-tick>115:raise Cap()
            key=x.tobytes()
            if cache.get('key')==key:return cache['value']
            calls+=1;c=controls(x);pos=M@c;v=D1@c;acc=D2@c;speed=np.linalg.norm(v,axis=1);k=np.linalg.norm(np.cross(v,acc),axis=1)/np.maximum(speed,1e-7)**3
            coords=((pos-origin)/4).T;gaps=[map_coordinates(z,coords,order=1,mode='constant',cval=0,prefilter=False) for z in fields];isin=map_coordinates(inside,coords,order=1,mode='constant',cval=0,prefilter=False);outer=gaps[3]*(2*isin-1)
            L=float(np.dot(gw,np.linalg.norm(GL@c,axis=1)))
            whole=np.vstack([fixed_start,pos,fixed_end]);arclength=np.r_[0,np.cumsum(np.linalg.norm(np.diff(whole,axis=0),axis=1))];pd=cdist(whole,whole);pd[np.abs(arclength[:,None]-arclength[None,:])<=10]=1e6;selfgap=pd.min(1)
            ineq=np.r_[gaps[0]-3.9,gaps[1]-3.9,gaps[2]-3.9,outer-5.9,1-30.15*k,selfgap-5.3];eq=L-target
            violation=float(np.sum(np.minimum(0,ineq)**2)+eq*eq)
            if violation<best['score']:best.update(score=violation,x=x.copy())
            result=(ineq,eq,float(.0002*np.sum((c[2:-2]-cc[2:-2])**2)),dict(material=float(gaps[0].min()),mandatory=float(gaps[1].min()),motion=float(gaps[2].min()),outer=float(outer.min()),self=float(selfgap.min()),sampled_R=float(1/max(k.max(),1e-12)),length=L+prefix_length))
            cache.update(key=key,value=result);return result
        capped=False;message=''
        try:
            opt=minimize(lambda x:evaluate(x)[2],x0,method='SLSQP',bounds=list(zip(lower,upper)),
                constraints=[dict(type='ineq',fun=lambda x:evaluate(x)[0]),dict(type='eq',fun=lambda x:evaluate(x)[1])],
                options=dict(maxiter=150,ftol=1e-8,eps=1e-4))
            message=str(opt.message)
        except Cap:capped=True;message='32s seed or115s total cost guard; best constraint state retained'
        x=best['x'];c=controls(x);analytic=extrema(knots,c);L,error=exact_length(knots,c)
        # Metrics at best state without spending another optimization iteration.
        st=time.monotonic();cache.clear()
        try:ineq,eq,_,metrics=evaluate(x)
        except Cap:metrics={};ineq=np.array([-1]);eq=1
        radius=analytic.get('minimum_radius_mm');eligible=bool(analytic['regular'] and (radius is None or radius>=30-1e-6) and abs(L+prefix_length-452)<=.05 and np.min(ineq)>=-1e-4)
        row=dict(source_seed=previous['seed'],source_anchor_index=previous['source_anchor_index'],goal_anchor_index=previous['goal_anchor_index'],
            controls_mm=c.tolist(),knots=knots.tolist(),degree=3,source_prefix_parts=sp,BUS_outward_prefix_parts=tp,
            full_length_mm=L+prefix_length,length_quadrature_error_mm=error,continuous_curvature=analytic,sampled_metrics=metrics,
            worst_hard_constraint=float(np.min(ineq)),constraint_violation_score=best['score'],calls=calls,cost_capped=capped,solver_message=message,
            numeric_preflight_eligible_not_CAD_PASS=eligible,full_prefix_BRep_mating_and_neighbours_open=True)
        report['seeds'].append(row);print('Constrained',previous['seed'],'full',round(row['full_length_mm'],3),'R',round(radius or 1e9,3),'violation',round(best['score'],4),'eligible',eligible,flush=True);save()
        if eligible:report['numeric_candidate']=row;break
    report['status']='HARD_CONSTRAINT_NUMERIC_USB_PENDING_EXACT_RECEIVE' if report['numeric_candidate'] else 'HARD_CONSTRAINT_RECEIVE_NO_ELIGIBLE_CURVE_NOT_INFEASIBILITY_PROOF'
    report['holds']=['Neither source dimensions nor R30 relaxed to make a test green','No source/native save or selected export',
        'Actual complete BRep/outer/all36poses,5replacement root paths and full123wires remainOPEN']
    save();print(json.dumps(dict(status=report['status'],seeds=len(report['seeds']),seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()
