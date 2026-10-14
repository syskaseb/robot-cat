"""One whole oblique-entry family, before new full-port spatial allocation."""
import copy
import json
import math
import time
from pathlib import Path
from plan_body_fanout_layout import OUT,ROOT,SHA
from plan_current_moving_looms import add,sub,mul,rotation
from plan_current_mta_interfaces import line
from planar_csc_flex import domain,build
from planar_round_flex import merge,intersect
from plan_continuous_joint_family import self_screen


def ends(row,angle):
    pivot=row['pivot_mm'];moving=add(pivot,rotation(sub(row['moving_anchor_rest_world_mm'],pivot),row['joint_axis'],angle))
    exit=rotation(row['moving_tangent_rest_world'],row['joint_axis'],angle)
    start=add(row['fixed_anchor_world_mm'],mul(row['fixed_tangent_world'],9))
    end=sub(moving,mul(exit,9));return start,end,exit,moving


def run():
    tick=time.monotonic();pf=OUT/'body-low-hip-rail-exit-plan.json';prior=json.loads(pf.read_text())
    df=OUT/'body-joint-port-motion-plan.json';vertical=json.loads(df.read_text())
    rows=copy.deepcopy(prior['hips']);roots={r['loom']:r['root_Z_mm'] for r in vertical['root_selection']}
    domains={};per={};common=[[0,850.]]
    for row in rows:
        loom=row['loom'];side=1 if row['fixed_anchor_world_mm'][1]>0 else -1;angle=-side*30
        row['fixed_entry_tilt_degrees']=angle;row['fixed_tangent_world']=rotation([0,0,-1],[1,0,0],angle)
        row['fixed_anchor_world_mm'][2]=roots[loom];per[loom]=[[0,850.]]
        for h in range(-15,16):
            a,b,v,m=ends(row,h)
            choices=[d for beta in range(-88,89,2) if (d:=domain(a,b,row['fixed_tangent_world'],v,beta)) is not None]
            assert choices,(loom,h)
            domains[loom,h]=choices;interval=merge([(d['minimum_mm'],d['maximum_mm']) for d in choices])
            per[loom]=intersect(per[loom],interval);common=intersect(common,interval)
    print(json.dumps(dict(common=common,per_loom=per)),flush=True)
    lengths={}
    def choose(intervals):
        for lo,hi in intervals:
            nominal=150 if lo+5<=150<=hi-5 else math.ceil((lo+5)/5)*5
            if nominal+5<=hi:return nominal
        return None
    shared=choose(common)
    for row in rows:
        loom=row['loom'];length=shared if shared is not None else choose(per[loom]);assert length is not None,(loom,per[loom])
        lengths[loom]=length;row['flex_length_mm']=length;row['flex_guide_mm']=length;row['guide_mm']=length+18;row['poses']=[]
        fixed=[beta for beta in range(-88,89,2) if all(any(d['beta_degrees']==beta and d['minimum_mm']<=length-5 and d['maximum_mm']>=length+5 for d in domains[loom,h]) for h in range(-15,16))]
        beta=min(fixed,key=abs) if fixed else None;row['common_bridge_beta_degrees']=beta
        for h in range(-15,16):
            a,b,v,m=ends(row,h);options=[d for d in domains[loom,h] if d['minimum_mm']-1e-8<=length<=d['maximum_mm']+1e-8 and (beta is None or d['beta_degrees']==beta)]
            r=min(options,key=lambda d:abs(d['beta_degrees']));middle=build(a,b,length,r);assert middle is not None
            parts=[line(row['fixed_anchor_world_mm'],a),*middle,line(b,m)]
            assert self_screen(parts) is None,(loom,h)
            row['poses'].append(dict(angle=h,parts=parts,bridge_beta_degrees=r['beta_degrees']))
        row['fixed_lands']=[dict(id=loom+'/Hip/Fixed',parts=[row['poses'][15]['parts'][0]],owner='Body')]
    result=dict(status='OBLIQUE_FIXED_ENTRY_MATH_PLANNED_FULL_PORT_SOURCE_SPACE_INVALIDATED_OPEN',hips=rows,
        common_flex_mm=shared,flex_by_loom_mm=lengths,feasible_intervals_by_loom_mm=per,
        fixed_land_count=4,additional_fixed_bands=0,project_length_allowance_mm=5,
        invalidates=['All4fixedport orientations and theircorepacking/fan reservations; previousvertical rootdomains NOTqualification',
                     'Fournewfactoryflexes/material/ground andterminalarms; other8families/11bodyroutes retained'],
        source_sha256={f.relative_to(ROOT).as_posix():SHA(f) for f in (pf,df,Path(__file__),Path(__file__).with_name('planar_csc_flex.py'))},
        worker_seconds=round(time.monotonic()-tick,3),selected=False,W5_complete=False,physical_pass=False)
    (OUT/'body-oblique-port-motion-plan.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],lengths=lengths,worker_seconds=result['worker_seconds'])),flush=True)


if __name__=='__main__':run()
