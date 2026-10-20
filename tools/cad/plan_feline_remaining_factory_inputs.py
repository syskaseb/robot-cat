"""One coupled four-input factory plan before further CAD or graph filters.

Keep current case/joint poses, selected R25.2 and full9mm grips. Long front
paths use a separate3D return layer; rear paths remain planar. Grips may use
the first/last9mm of a curve, not necessarily an invented straight9+9.
"""
import itertools,json,math,time
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from check_main_p0_placement import ROOT,sha
from plan_feline_layout import OUT
from receive_feline_existing_lower_caps import current
from feline_selected_piece_contract import load as profiles
from receive_feline_underplate_return_gallery import forward,bend
from plan_feline_factory_links import scurve
from compose_feline_n01_allocation import tangent
from feline_atomic_save import save_json


def offset(rows,p,d,v,R=25.2):
    v=np.asarray(v,float);H=np.linalg.norm(v);assert 0<H<2*R
    n=v/H;angle=math.acos(1-H/(2*R));q,h=bend(rows,p,d,n,R,angle)
    normal=d-h*float(d@h);normal/=np.linalg.norm(normal)
    return bend(rows,q,h,normal,R,angle)[0]


def samples(rows,step=.25):
    result=[];error=0.
    for p in rows:
        a,b=np.asarray(p['start']),np.asarray(p['end']);N=max(1,math.ceil(p['length_mm']/step))
        if p['kind']=='line':pts=a+(b-a)*np.linspace(0,1,N+1)[:,None]
        else:
            m=np.asarray(p['mid']);u=m-a;v=b-a;n=np.cross(u,v)
            c=a+(u@u*np.cross(v,n)+v@v*np.cross(n,u))/(2*(n@n))
            t=np.asarray(tangent(p,True));R=p['radius_mm'];angle=p['length_mm']/R
            theta=np.linspace(0,angle,N+1);pts=c+np.cos(theta)[:,None]*(a-c)+np.sin(theta)[:,None]*R*t
            assert np.linalg.norm(pts[-1]-b)<1e-5
        result.append(pts);error=max(error,p['length_mm']/(2*N))
    return np.vstack(result),error


def main():
    tick=time.monotonic();_,ends,files=current();contract,pf=profiles();byid={e['id']:e for e in ends};routes={};clouds={}
    for w in ('W041','W042','W044','W052'):
        a=byid[w+'/factory/start'];b=byid[w+'/factory/end'];p=np.array(a['point_mm']);target=np.array(b['point_mm']);d=np.array(a['departure_axis'],float)
        assert contract['portions'][w+'/factory']['minimum_project_R_mm']>=25.2
        if w in ('W041','W042'):
            rows=[];q=forward(rows,p,d,3);q=offset(rows,q,d,[0,target[1]-p[1],-6])
            q=offset(rows,q,d,[0,0,target[2]-q[2]])
            rest=float((target-q)@d);assert rest>=3 and np.linalg.norm(target-q-rest*d)<1e-6
            forward(rows,q,d,rest);kind='LONG_INPUT_3D_RETURN_LAYER'
        else:
            rows,_=scurve(p,target,d,R=25.2,land=0);kind='REAR_PLANAR_S_FULL9_INCLUDES_ARC'
        length=sum(r['length_mm'] for r in rows);clouds[w]=samples(rows)
        assert all(r.get('radius_mm',25.2)>=25.2 for r in rows)
        routes[w]=dict(parts=rows,source_end_id=a['id'],target_end_id=b['id'],radius_mm=2.1,minimum_R_mm=25.2,
            guide_mm=length,full_grip_arclength_intervals_mm=[[0,9],[length-9,length]],
            full9_straight_not_a_manufacturer_requirement=True,first_straight_mm=rows[0]['length_mm'],last_straight_mm=rows[-1]['length_mm'],
            topology=kind,termination11_min_nominal_need_mm=length+11,nominal_factory100_is_delivery_assumption=True,
            stock_rework_and_final_cut_NOT_qualified=True,old_factory_seat_fit_NOT_inherited=True)
    pairs=[]
    for a,b in itertools.combinations(routes,2):
        aa,ea=clouds[a];bb,eb=clouds[b];observed=float(cKDTree(aa).query(bb)[0].min());lower=observed-ea-eb
        pairs.append(dict(a=a,b=b,continuous_axis_distance_lower_bound_mm=lower,required_mm=4.4,ok=lower>=4.4,
            method='Arclength sample coverage<=step/2 on each exact line/circle; subtract both coverage errors'))
    result=dict(status='FOUR_FACTORY_INPUT_CONSTRUCTIVE_MATH_MUTUAL_RECEIVED_SPACE_ROOTS_OPEN' if all(p['ok'] for p in pairs) else 'FOUR_FACTORY_INPUT_MATH_MUTUAL_HOLDS',routes=routes,pairs=pairs,
        source_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in (*files,pf,Path(__file__))},
        purchased_parts_and_case_poses_changed=False,N01_complete=False,physical_pass=False,native_changed=False,
        first_factory3mm_is_project_boot_assumption_not_supplier=True,world_roots_grips_tools_and_nominal_factory_length_still_OPEN=True,
        worker_seconds=round(time.monotonic()-tick,3))
    save_json(OUT/'n01-remaining-factory-input-plan.json',result);print(result['status'],result['worker_seconds'])
    print(json.dumps(dict(lengths={w:r['guide_mm'] for w,r in routes.items()},pairs=pairs),indent=2))


if __name__=='__main__':main()
