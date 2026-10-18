"""Bounded continuous cable fitting FROM the shared-space atlas.

Optimizes one coupled cubic middle with both factory prefixes, fixed tangent
joins and whole452mm allowance. Numerical field scores are not CAD clearance.
Before exact receive, continuous cubic curvature extrema and quadrature length
are recorded. Does not save/change any source/native document.
"""
import json
import math
import time
from pathlib import Path
import numpy as np
from scipy.interpolate import BSpline
from scipy.optimize import least_squares
from scipy.ndimage import map_coordinates
from scipy.spatial.distance import cdist
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from feline_cubic_curvature import clamped_knots,extrema,exact_length
from feline_tangent_routes import samples


def main():
    tick=time.monotonic();src=OUT/'n01-joint-frame-corridor-guide.json';policy=OUT/'n01-reservation-ownership-plan.json';dest=OUT/'n01-atlas-usb-spline-fit.json';assert not dest.exists()
    g=json.loads(src.read_text());p=json.loads(policy.read_text());assert g['one_representative_per_registered_pair_retained']
    f=ROOT/p['field'];assert sha(f)==p['field_sha256'];a=np.load(f,allow_pickle=False);axes=[a[k] for k in ('x','y','z')];origin=np.array([v[0] for v in axes])
    report=dict(status='RUNNING_CONTINUOUS_USB_FIT_FROM_SHARED_FIELD',selected=False,N01_complete=False,physical_pass=False,
        source_sha256={q.relative_to(ROOT).as_posix():sha(q) for q in (src,policy,f,Path(__file__),Path(__file__).with_name('feline_cubic_curvature.py'))},
        full_project_outside_length_mm=452,catalog_factory_mm=500,manufacturer_bare_length_not_guaranteed=True,
        source_components_moved=False,full_actual_BRep_or_roots_tools_motion_accepted=False,
        seeds=[],numeric_candidate=None,solver_family='One C2cubic middle, tangent C1 joins after fixed9mm grips, constrained field/radius/whole length, not new hand-waypoint CAD variants')
    def save():
        report['worker_seconds']=round(time.monotonic()-tick,3);dest.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    save();count=12;knots=clamped_knots(count);u=np.linspace(0,1,129);basis=BSpline(knots,np.eye(count),3);M=basis(u);D1=basis(u,1);D2=basis(u,2)
    common=a['components']==p['USB_shared_component_ids'][0];common=common&~a['curve_hold']
    fields=[a['material_distance'],a['mandatory_reservation_distance'],a['motion36_distance'],a['outer_distance'],common.astype(float)];inside_field=a['inside'].astype(float)
    selected=[];seen=set()
    # Diversity first: do not spend the whole budget on the cheapest one inlet.
    for guide in g['guides']:
        si=guide['source_anchor_index']
        if si not in seen:selected.append(guide);seen.add(si)
    for guide in g['guides']:
        if guide not in selected:selected.append(guide)
        if len(selected)>=14:break
    class CostCap(Exception):pass
    for index,guide in enumerate(selected):
        if time.monotonic()-tick>210:break
        st=time.monotonic();s=g['anchors'][guide['source_anchor_index']];t=g['anchors'][guide['goal_anchor_index']]
        sp=s['prefix_parts'];tp=t['prefix_parts'];q0=np.array(sp[-1]['end']);q1=np.array(tp[-1]['end']);v0=q0-sp[-1]['start'];v0/=np.linalg.norm(v0);v1=np.array(tp[-1]['start'])-q1;v1/=np.linalg.norm(v1)
        prefix_length=s['prefix_length_mm']+t['prefix_length_mm'];target=452-prefix_length
        poly=np.vstack([q0,guide['all_grid_points_mm'],q1]);lens=np.r_[0,np.cumsum(np.linalg.norm(np.diff(poly,axis=0),axis=1))];good=np.r_[True,np.diff(lens)>1e-8];poly=poly[good];lens=lens[good]
        c=np.column_stack([np.interp(np.linspace(0,lens[-1],count),lens,poly[:,j]) for j in range(3)])
        h=max(3,min(20,target/(count-3)/3));x0=np.r_[c[2:-2].ravel(),h,h]
        lower=np.r_[np.tile([-136,-92,-42],count-4),1,1];upper=np.r_[np.tile([178,92,106],count-4),70,70];x0=np.clip(x0,lower+1e-6,upper-1e-6)
        fixed_start=np.array([q for ss in sp for q in samples(ss,2)]);fixed_end=np.array([q for ss in tp[::-1] for q in list(samples(ss,2))[::-1]])
        best=dict(cost=math.inf,x=x0.copy());calls=0
        def controls(x):return np.vstack([q0,q0+v0*x[-2],x[:-2].reshape(-1,3),q1-v1*x[-1],q1])
        def evaluate(x,return_metrics=False):
            nonlocal calls
            calls+=1
            if not return_metrics and (time.monotonic()-st>14 or time.monotonic()-tick>215):raise CostCap()
            cc=controls(x);pos=M@cc;v=D1@cc;acc=D2@cc;speed=np.linalg.norm(v,axis=1);k=np.linalg.norm(np.cross(v,acc),axis=1)/np.maximum(speed,1e-7)**3
            L=float(np.trapz(speed,u));coords=((pos-origin)/4).T
            distances=[map_coordinates(z,coords,order=1,mode='constant',cval=0,prefilter=False) for z in fields]
            # Do not mistake unsigned outer distance outside the torso for room.
            inside=map_coordinates(inside_field,coords,order=1,mode='constant',cval=0,prefilter=False)
            outer=distances[3]*(2*inside-1)
            whole=np.vstack([fixed_start,pos,fixed_end]);increments=np.linalg.norm(np.diff(whole,axis=0),axis=1);arclength=np.r_[0,np.cumsum(increments)];separation=np.abs(arclength[:,None]-arclength[None,:])
            pairdist=cdist(whole,whole);pairdist[separation<=10]=1e6;nearest=pairdist.min(1)
            residual=np.r_[3*np.maximum(0,3.9-distances[0]),3*np.maximum(0,3.9-distances[1]),3*np.maximum(0,3.9-distances[2]),
                3*np.maximum(0,5.9-outer),4*(1-distances[4]),20*np.maximum(0,30.1*k-1),
                2*np.maximum(0,5.3-nearest),[L-target],.01*(cc[2:-2]-c[2:-2]).ravel()]
            cost=float(np.dot(residual,residual))
            if cost<best['cost']:best.update(cost=cost,x=x.copy())
            if return_metrics:return dict(sampled_middle_length_mm=L,sampled_full_length_mm=L+prefix_length,
                sampled_min_radius_mm=float(1/max(k.max(),1e-12)),sampled_material_axis_gap_mm=float(distances[0].min()),
                sampled_mandatory_reservation_axis_gap_mm=float(distances[1].min()),sampled_motion_axis_gap_mm=float(distances[2].min()),
                sampled_outer_axis_gap_mm=float(outer.min()),sampled_self_axis_gap_mm=float(nearest.min()),
                sampled_connected_field_min=float(distances[4].min()),least_squares_cost=cost)
            return residual
        stopped=False;message=''
        try:
            opt=least_squares(evaluate,x0,bounds=(lower,upper),max_nfev=160,ftol=1e-5,xtol=1e-5,gtol=1e-5,diff_step=1e-4)
            message=opt.message
        except CostCap:stopped=True;message='14s per-seed cost guard; best numerical state retained'
        x=best['x'];cc=controls(x);metrics=evaluate(x,True);curvature=extrema(knots,cc);L,error=exact_length(knots,cc)
        candidate=dict(seed=index,source_anchor_index=guide['source_anchor_index'],goal_anchor_index=guide['goal_anchor_index'],
            source_prefix_parts=sp,BUS_outward_prefix_parts=tp,controls_mm=cc.tolist(),knots=knots.tolist(),degree=3,
            full_length_mm=L+prefix_length,length_quadrature_error_mm=error,continuous_curvature=curvature,
            sampled_metrics=metrics,objective_calls=calls,seed_seconds=round(time.monotonic()-st,3),cost_capped=stopped,solver_message=message,
            full_prefix_actual_neighbours_still_open=True,exact_full_BRep_distance_and_motion_still_open=True)
        radius=curvature.get('minimum_radius_mm');eligible=(curvature['regular'] and (radius is None or radius>=30-1e-6) and abs(L+prefix_length-452)<=.05
            and metrics['sampled_material_axis_gap_mm']>=3.75 and metrics['sampled_mandatory_reservation_axis_gap_mm']>=3.75
            and metrics['sampled_motion_axis_gap_mm']>=3.75 and metrics['sampled_outer_axis_gap_mm']>=5.75
            and metrics['sampled_self_axis_gap_mm']>=5.2 and metrics['sampled_connected_field_min']>=.95)
        candidate['numeric_preflight_eligible_not_CAD_PASS']=bool(eligible);report['seeds'].append(candidate)
        print('Continuous fit',index,'full',round(candidate['full_length_mm'],3),'R',round(radius or 1e9,3),'cost',round(best['cost'],2),'eligible',eligible,flush=True);save()
        if eligible:report['numeric_candidate']=candidate;break
    report['status']='NUMERIC_FULL_USB_CURVE_PENDING_EXACT_RECEIVE' if report['numeric_candidate'] else 'CONTINUOUS_FIT_BOUNDED_NO_ELIGIBLE_CURVE_NOT_INFEASIBILITY_PROOF'
    report['holds']=['Every sampled field metric is planning only; original valid source BReps and exact outer distance must receive whole cable',
        'Five provisional beams have joint relocation authority, NOT permission for missing supports',
        'All123middles/246ends/4MTA/roots/montage/tools/full36poses remain N01 requirements',
        '452outside and source mould shapes are project assumptions, not guaranteed manufacturer bare length']
    save();print(json.dumps(dict(status=report['status'],seeds=len(report['seeds']),seconds=report['worker_seconds'])),flush=True)


if __name__=='__main__':main()
